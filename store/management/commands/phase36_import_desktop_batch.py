from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from store.management.commands.phase34c_import_makerworld_export import import_manifest
from store.models import Category, Product


def unique_slug(title: str, external_id: str) -> str:
    base = slugify(title, allow_unicode=True) or f"makerworld-{external_id}"
    candidate = base
    index = 2
    while Product.objects.filter(slug=candidate).exists():
        candidate = f"{base}-{index}"
        index += 1
    return candidate


def unique_sku(external_id: str) -> str:
    base = f"MW-{external_id}"[:80]
    candidate = base
    index = 2
    while Product.objects.filter(sku=candidate).exists():
        candidate = f"{base}-{index}"[:80]
        index += 1
    return candidate


class Command(BaseCommand):
    help = "Import a batch created by 3DPrintHub Desktop Manager."

    def add_arguments(self, parser):
        parser.add_argument("batch_path")
        parser.add_argument("--continue-on-error", action="store_true")

    def handle(self, *args, **options):
        batch_path = Path(options["batch_path"]).resolve()
        manifest_path = batch_path / "batch_manifest.json"
        if not manifest_path.is_file():
            raise CommandError(f"Batch manifest was not found: {manifest_path}")

        batch = json.loads(manifest_path.read_text(encoding="utf-8"))
        imported = 0
        failed = 0

        for row in batch.get("models") or []:
            external_id = str(row.get("model_id") or "")
            try:
                with transaction.atomic():
                    asset = import_manifest(batch_path / row["manifest"])
                    editorial = json.loads((batch_path / row["editorial"]).read_text(encoding="utf-8"))

                    asset.source_title = editorial.get("source_title") or asset.source_title
                    asset.source_description = editorial.get("source_description") or asset.source_description
                    asset.persian_title = editorial.get("title_fa") or asset.persian_title
                    asset.persian_short_description = (editorial.get("description_fa") or "")[:500]
                    asset.persian_description = editorial.get("description_fa") or asset.persian_description
                    selected_price = int(
                        editorial.get("final_price")
                        if editorial.get("price_is_final")
                        else editorial.get("suggested_price") or 500_000
                    )
                    asset.fixed_print_price = max(500_000, selected_price)
                    asset.editorial_status = "ready" if editorial.get("approved") else "review"
                    asset.save()

                    product = None
                    if editorial.get("as_product") and editorial.get("approved"):
                        category, _ = Category.objects.get_or_create(
                            slug=editorial.get("category_slug") or "external-other",
                            defaults={
                                "name": "مدل‌های آماده چاپ",
                                "section": "general",
                                "is_active": True,
                            },
                        )
                        if asset.product_id:
                            product = asset.product
                            product.title = asset.persian_title or asset.source_title or asset.title
                            product.short_description = asset.persian_short_description or "محصول آماده سفارش چاپ سه‌بعدی"
                            product.description = asset.persian_description or asset.source_description or asset.description
                            product.fixed_price = asset.fixed_print_price
                            product.save()
                        else:
                            product = Product.objects.create(
                                category=category,
                                title=asset.persian_title or asset.source_title or asset.title,
                                slug=unique_slug(
                                    asset.persian_title or asset.source_title or asset.title,
                                    external_id,
                                ),
                                sku=unique_sku(external_id),
                                short_description=asset.persian_short_description or "محصول آماده سفارش چاپ سه‌بعدی",
                                description=asset.persian_description or asset.source_description or asset.description or "",
                                main_image=asset.primary_image,
                                order_mode="fixed",
                                fixed_price=asset.fixed_print_price,
                                fixed_delivery_days=3,
                                consultation_required=False,
                                is_active=False,
                            )
                            asset.product = product
                            asset.save(update_fields=["product", "updated_at"])

                imported += 1
                self.stdout.write(
                    f"OK MODEL_ID={external_id} ASSET_ID={asset.pk} "
                    f"PRODUCT_ID={product.pk if product else '-'}"
                )
            except Exception as error:
                failed += 1
                self.stderr.write(
                    f"FAILED MODEL_ID={external_id} {type(error).__name__}: {error}"
                )
                if not options["continue_on_error"]:
                    break

        self.stdout.write(f"IMPORTED_COUNT={imported}")
        self.stdout.write(f"FAILED_COUNT={failed}")
        if failed:
            raise CommandError(f"Desktop batch import has {failed} failure(s).")
        self.stdout.write("PHASE36_DESKTOP_BATCH_IMPORT=OK")
