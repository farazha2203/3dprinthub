#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROJECT = Path("/home/sfkilvrs/3dprinthub")
sys.path.insert(0, str(PROJECT))
os.chdir(PROJECT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings
from store.models import ImportedPrintAsset, Product

SITE = "https://3dprinthub.ir"


def post_json(url: str, token: str, payload: dict) -> tuple[int, dict]:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=raw,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(body or "{}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body or "{}")
        except Exception:
            parsed = {"detail": body[:3000]}
        return exc.code, parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--batch", default="")
    args = parser.parse_args()

    token = str(getattr(settings, "CATALOG_BRIDGE_TOKEN", "") or "").strip()
    if len(token) < 24:
        raise RuntimeError("CATALOG_BRIDGE_TOKEN is missing or too short.")

    pending = Path(settings.CATALOG_BRIDGE_PENDING_ROOT).resolve()
    if not pending.is_dir():
        raise RuntimeError(f"Pending directory not found: {pending}")

    if args.batch:
        candidates = [pending / args.batch]
    else:
        candidates = sorted(
            p for p in pending.iterdir()
            if p.is_dir() and p.name.startswith("desktop_catalog_v85_")
        )
        if not args.all:
            candidates = candidates[:1]

    if not candidates:
        print("PENDING_BATCHES=0")
        print("PHASE48_PENDING_IMPORT=NOTHING_TO_DO")
        return 0

    before_assets = ImportedPrintAsset.objects.count()
    before_products = Product.objects.count()
    print(f"ASSETS_BEFORE={before_assets}")
    print(f"PRODUCTS_BEFORE={before_products}")
    print(f"BATCHES_SELECTED={len(candidates)}")

    failures = 0
    for batch in candidates:
        manifest_path = batch / "batch_manifest.json"
        if not manifest_path.is_file():
            print(f"BATCH={batch.name} STATUS=SKIPPED_NO_MANIFEST")
            failures += 1
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        schema = str(manifest.get("schema_version") or "")
        batch_uuid = str(manifest.get("batch_uuid") or "").strip()
        if schema != "8.5" or not batch_uuid:
            print(f"BATCH={batch.name} STATUS=INVALID_MANIFEST SCHEMA={schema}")
            failures += 1
            continue

        status, ack = post_json(
            SITE + "/api/catalog-bridge/v1/import/",
            token,
            {
                "batch_name": batch.name,
                "batch_uuid": batch_uuid,
                "schema_version": "8.5",
            },
        )
        print(f"BATCH={batch.name} HTTP_STATUS={status}")
        print(
            "ACK="
            + json.dumps(
                ack,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )

        if status != 200 or int(ack.get("failed_count") or 0) != 0:
            failures += 1

    after_assets = ImportedPrintAsset.objects.count()
    after_products = Product.objects.count()
    print(f"ASSETS_AFTER={after_assets}")
    print(f"PRODUCTS_AFTER={after_products}")
    print(f"ASSETS_DELTA={after_assets - before_assets}")
    print(f"PRODUCTS_DELTA={after_products - before_products}")
    print(f"FAILED_BATCHES={failures}")

    if failures:
        return 30

    print("PHASE48_PENDING_IMPORT=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
