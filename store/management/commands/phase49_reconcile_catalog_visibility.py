from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from store.models import ImportedPrintAsset
from store.phase49_catalog_visibility import publish_catalog_product_to_store


class Command(BaseCommand):
    help = "Reconcile store visibility from approved Catalog Intelligence v8.5 pending batches."

    def add_arguments(self, parser):
        parser.add_argument("--batch", action="append", default=[])
        parser.add_argument("--all-pending", action="store_true")
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        pending_root = Path(
            getattr(settings, "CATALOG_BRIDGE_PENDING_ROOT", None)
            or (Path(settings.BASE_DIR) / "imports" / "desktop_catalog" / "pending")
        ).resolve()
        requested = [str(x).strip() for x in options["batch"] if str(x).strip()]
        if options["all_pending"]:
            requested.extend(sorted(p.name for p in pending_root.glob("desktop_catalog_v85_*") if p.is_dir()))
        requested = list(dict.fromkeys(requested))
        if not requested:
            raise CommandError("Use --batch NAME or --all-pending.")

        scanned = eligible = changed = missing = failed = 0
        for batch_name in requested:
            root = (pending_root / batch_name).resolve()
            try:
                root.relative_to(pending_root)
            except ValueError as exc:
                raise CommandError("Batch path escapes pending root.") from exc
            manifest_path = root / "batch_manifest.json"
            if not manifest_path.is_file():
                self.stderr.write(f"MISSING_BATCH={batch_name}")
                missing += 1
                continue
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for item in manifest.get("models", []):
                scanned += 1
                editorial = (root / item.get("editorial", "")).resolve()
                try:
                    editorial.relative_to(root)
                except ValueError:
                    failed += 1
                    continue
                if not editorial.is_file():
                    failed += 1
                    continue
                data = json.loads(editorial.read_text(encoding="utf-8"))
                if not (data.get("publish_as_product") and data.get("approved_for_sale")):
                    continue
                source_code = str(data.get("source_code") or "")
                external_id = str(data.get("external_id") or "")
                asset = ImportedPrintAsset.objects.filter(
                    source__code=source_code,
                    external_id=external_id,
                    product__isnull=False,
                ).select_related("product", "product__category").order_by("pk").first()
                if asset is None:
                    missing += 1
                    self.stderr.write(f"ASSET_OR_PRODUCT_MISSING={source_code}:{external_id}")
                    continue
                eligible += 1
                product = asset.product
                before = bool(product.is_active)
                try:
                    if options["apply"]:
                        with transaction.atomic():
                            decision = publish_catalog_product_to_store(product, asset, data)
                    else:
                        from store.phase49_catalog_visibility import evaluate_catalog_product_visibility
                        decision = evaluate_catalog_product_visibility(product, asset, data)
                    self.stdout.write(
                        f"PRODUCT={product.pk} SOURCE={source_code}:{external_id} "
                        f"BEFORE_ACTIVE={int(before)} READY={int(decision.visible)} URL={decision.product_url or '-'}"
                    )
                    if options["apply"] and decision.visible and not before:
                        changed += 1
                except Exception as exc:
                    failed += 1
                    self.stderr.write(f"FAILED={source_code}:{external_id} {type(exc).__name__}: {exc}")

        self.stdout.write(f"SCANNED={scanned}")
        self.stdout.write(f"ELIGIBLE={eligible}")
        self.stdout.write(f"ACTIVATED={changed}")
        self.stdout.write(f"MISSING={missing}")
        self.stdout.write(f"FAILED={failed}")
        self.stdout.write(f"MODE={'APPLY' if options['apply'] else 'DRY_RUN'}")
        if failed:
            raise CommandError(f"Visibility reconciliation has {failed} failure(s).")
        self.stdout.write("PHASE49_CATALOG_VISIBILITY_RECONCILE=OK")
