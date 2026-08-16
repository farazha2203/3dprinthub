from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from store.epic49_catalog_profile import ProductCatalogProfile, safe_public_slug
from store.epic49_publish_options import _desktop_data, sync_epic49_publish_options
from store.models import ImportedPrintAsset


class Command(BaseCommand):
    help = "Audit or apply Epic49 structured catalog profile/SEO/variant/slider sync for existing imported products."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Write changes. Default is dry-run.")
        parser.add_argument("--product-id", type=int, default=0, help="Limit to one Store Product ID.")

    def handle(self, *args, **options):
        apply = bool(options["apply"])
        product_id = int(options.get("product_id") or 0)
        queryset = (
            ImportedPrintAsset.objects.exclude(product_id=None)
            .select_related("product", "source", "product__category")
            .order_by("product_id")
        )
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        checked = eligible = changed = failed = 0
        for asset in queryset.iterator():
            checked += 1
            data = _desktop_data(asset)
            if not data:
                self.stdout.write(f"SKIP PRODUCT={asset.product_id} ASSET={asset.pk} REASON=no_desktop_payload")
                continue
            eligible += 1
            product = asset.product
            existing = ProductCatalogProfile.objects.filter(product=product).first()
            current_slug = str(getattr(product, "slug", "") or "")
            proposed_slug = str(getattr(existing, "public_slug", "") or safe_public_slug(product))
            self.stdout.write(
                f"{'APPLY' if apply else 'PLAN'} PRODUCT={product.pk} ASSET={asset.pk} "
                f"SLUG={current_slug!r} -> {proposed_slug!r} "
                f"PRICE_MIN={data.get('price_min') or 0} PRICE_MAX={data.get('price_max') or 0} "
                f"SLIDER={int(bool(data.get('homepage_slider_enabled')))}"
            )
            if not apply:
                continue
            try:
                with transaction.atomic():
                    result = sync_epic49_publish_options(asset)
                changed += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"OK PRODUCT={product.pk} PROFILE={result.get('profile_id') or '-'} "
                        f"PUBLIC_SLUG={result.get('public_slug') or '-'} "
                        f"VARIANTS={len(result.get('material_color_variants') or [])}"
                    )
                )
            except Exception as exc:
                failed += 1
                self.stderr.write(
                    self.style.ERROR(f"FAILED PRODUCT={product.pk} ASSET={asset.pk} {type(exc).__name__}: {exc}")
                )

        self.stdout.write(f"CHECKED={checked}")
        self.stdout.write(f"ELIGIBLE={eligible}")
        self.stdout.write(f"CHANGED={changed}")
        self.stdout.write(f"FAILED={failed}")
        self.stdout.write(f"MODE={'APPLY' if apply else 'DRY_RUN'}")
        if failed:
            raise CommandError(f"Epic49 server catalog backfill has {failed} failure(s).")
        self.stdout.write("EPIC49_SERVER_CATALOG_BACKFILL=OK")
