#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import tempfile
import traceback
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.db import transaction
from django.test import override_settings

from store.management.commands.phase37_import_catalog_center import (
    apply_phase39_product_intelligence,
    apply_phase43_product_details,
    category_for,
    import_images,
    import_videos,
    source_for,
    upsert_asset,
)
from store.phase34b_publishing import convert_to_fixed_product, convert_to_portfolio
from store.phase49_3i52_site_identity import reconcile_asset_product_identity
from store.phase49_catalog_visibility import (
    catalog_license_allows_publish,
    publish_catalog_product_to_store,
)
from store.phase50_republish_contract import verify_product_republish_contract


def run_stage(name, fn):
    print(f"TRACE_STAGE_BEGIN={name}", flush=True)
    result = fn()
    print(f"TRACE_STAGE_PASS={name}", flush=True)
    return result


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: phase50_a2z_trace_import.py <batch_root> <desktop_product_id>", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).resolve()
    expected_desktop_id = int(sys.argv[2])
    manifest = json.loads((root / "batch_manifest.json").read_text(encoding="utf-8"))
    models = [
        item
        for item in manifest.get("models", [])
        if int(item.get("desktop_product_id") or 0) == expected_desktop_id
    ]
    if len(models) != 1:
        raise SystemExit(f"TRACE_FAIL=model_count:{len(models)}")

    item = models[0]
    editorial_path = (root / str(item["editorial"])).resolve()
    editorial_path.relative_to(root)
    data = json.loads(editorial_path.read_text(encoding="utf-8"))
    desktop_product_id = int(data.get("desktop_product_id") or item.get("desktop_product_id") or 0)
    if desktop_product_id != expected_desktop_id:
        raise SystemExit("TRACE_FAIL=desktop_product_id_mismatch")

    print("TRACE_BATCH=" + root.name, flush=True)
    print("TRACE_SOURCE=" + str(data.get("source_code") or "") + ":" + str(data.get("external_id") or ""), flush=True)

    with tempfile.TemporaryDirectory(prefix="a2z-import-trace-media-") as media_root:
        try:
            with override_settings(MEDIA_ROOT=media_root):
                with transaction.atomic():
                    category = run_stage("category_for", lambda: category_for(data))
                    source = run_stage("source_for", lambda: source_for(data, category))
                    asset, created = run_stage("upsert_asset", lambda: upsert_asset(source, data))
                    print(f"TRACE_ASSET_ID={asset.pk}", flush=True)
                    print(f"TRACE_ASSET_CREATED={created}", flush=True)

                    run_stage(
                        "reconcile_identity",
                        lambda: reconcile_asset_product_identity(
                            asset,
                            data,
                            desktop_product_id=desktop_product_id,
                        ),
                    )
                    image_count = run_stage(
                        "import_images",
                        lambda: import_images(asset, editorial_path.parent, data),
                    )
                    print(f"TRACE_IMAGE_COUNT={image_count}", flush=True)
                    run_stage(
                        "import_videos",
                        lambda: import_videos(asset, editorial_path.parent, data),
                    )

                    license_ok = catalog_license_allows_publish(
                        asset.commercial_license_status,
                        data,
                    )
                    print(f"TRACE_LICENSE_OK={license_ok}", flush=True)

                    product = None
                    if (
                        data.get("publish_as_product")
                        and data.get("approved_for_sale")
                        and license_ok
                    ):
                        product = run_stage(
                            "convert_product",
                            lambda: convert_to_fixed_product(asset),
                        )
                        print(f"TRACE_PRODUCT_ID={product.pk}", flush=True)
                        run_stage(
                            "phase39_product_intelligence",
                            lambda: apply_phase39_product_intelligence(product, data),
                        )
                        run_stage(
                            "phase43_product_details",
                            lambda: apply_phase43_product_details(product, data),
                        )
                        visibility = run_stage(
                            "publish_visibility",
                            lambda: publish_catalog_product_to_store(product, asset, data),
                        )
                        print(f"TRACE_VISIBLE={visibility.visible}", flush=True)
                        if visibility.visible:
                            parity = run_stage(
                                "republish_parity",
                                lambda: verify_product_republish_contract(product, asset, data),
                            )
                            print("TRACE_PARITY=" + json.dumps(parity, ensure_ascii=False), flush=True)

                    if data.get("publish_as_portfolio") and license_ok:
                        portfolio = run_stage(
                            "convert_portfolio",
                            lambda: convert_to_portfolio(asset),
                        )
                        print(f"TRACE_PORTFOLIO_ID={portfolio.pk}", flush=True)

                    transaction.set_rollback(True)
                    print("TRACE_DB_ROLLBACK=YES", flush=True)
        except Exception:
            print("TRACE_EXCEPTION_BEGIN", flush=True)
            traceback.print_exc()
            print("TRACE_EXCEPTION_END", flush=True)
            return 1

    print("TRACE_MEDIA_TEMP_CLEANED=YES", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
