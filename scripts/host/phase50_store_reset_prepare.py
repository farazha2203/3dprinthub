#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

BACKUP_SUFFIX = "-store-product-reset"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def project_root() -> Path:
    raw = str(os.environ.get("PHASE50_PROJECT_ROOT") or "").strip()
    if not raw:
        raise SystemExit("STORE_RESET_PREPARE_FAIL=project_root_missing")
    root = Path(raw).expanduser().resolve()
    if not (root / "manage.py").is_file() or not (root / "config" / "__init__.py").is_file():
        raise SystemExit("STORE_RESET_PREPARE_FAIL=project_root_invalid")
    sys.path.insert(0, str(root))
    return root

def field_name(field_file) -> str:
    try:
        return str(field_file.name or "").strip().replace("\\", "/")
    except Exception:
        return ""


def main() -> int:
    root = project_root()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()

    from django.conf import settings
    from django.db import connection
    from store.models import ImportedPrintAsset, InventoryMovement, Product, ProductImage, ProductVariant, StoreOrder, StoreOrderItem
    from website.models import HomepageHeroSlide

    if connection.vendor != "mysql":
        raise SystemExit("STORE_RESET_PREPARE_FAIL=database_not_mysql")
    expected_db = str(os.environ.get("PHASE50_EXPECTED_DB") or "").strip()
    actual_db = str(connection.settings_dict.get("NAME") or "")
    if not expected_db or actual_db != expected_db:
        raise SystemExit("STORE_RESET_PREPARE_FAIL=database_identity_mismatch")

    backup_root = Path(str(os.environ.get("PHASE50_BACKUP_ROOT") or "")).expanduser().resolve()
    allowed_root = Path(str(os.environ.get("PHASE50_ALLOWED_BACKUP_ROOT") or "")).expanduser().resolve()
    if not str(allowed_root) or backup_root.parent != allowed_root or not backup_root.name.endswith(BACKUP_SUFFIX):
        raise SystemExit("STORE_RESET_PREPARE_FAIL=backup_root_invalid")

    if InventoryMovement.objects.exists():
        raise SystemExit("STORE_RESET_PREPARE_FAIL=inventory_movements_present")
    products = list(Product.objects.order_by("id"))
    linked_assets = list(ImportedPrintAsset.objects.exclude(product=None).order_by("id"))
    if not products:
        raise SystemExit("STORE_RESET_PREPARE_FAIL=store_already_empty")
    if len(linked_assets) != len(products):
        raise SystemExit("STORE_RESET_PREPARE_FAIL=non_catalog_products_present")
    backup_root.mkdir(parents=True, exist_ok=False)

    media_names: list[str] = []
    seen: set[str] = set()
    for product in products:
        for field in (product.main_image, product.og_image, product.model_file):
            name = field_name(field)
            if name and name not in seen:
                seen.add(name); media_names.append(name)
    for row in ProductImage.objects.order_by("id"):
        name = field_name(row.image)
        if name and name not in seen:
            seen.add(name); media_names.append(name)

    media_root = Path(settings.MEDIA_ROOT).resolve()
    media_rows: list[dict] = []
    for name in media_names:
        live = (media_root / name).resolve()
        if media_root != live and media_root not in live.parents:
            raise SystemExit("STORE_RESET_PREPARE_FAIL=media_path_escape")
        if not live.is_file():
            raise SystemExit("STORE_RESET_PREPARE_FAIL=product_media_missing:" + name)
        target = (backup_root / "media" / name).resolve()
        if backup_root != target and backup_root not in target.parents:
            raise SystemExit("STORE_RESET_PREPARE_FAIL=backup_media_path_escape")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live, target)
        live_hash = sha256(live)
        if sha256(target) != live_hash:
            raise SystemExit("STORE_RESET_PREPARE_FAIL=media_hash_mismatch:" + name)
        media_rows.append({"name": name, "exists": True, "size": live.stat().st_size, "sha256": live_hash})

    hero = list(HomepageHeroSlide.objects.order_by("id").values("id", "asset_id"))
    manifest = {
        "products": list(Product.objects.order_by("id").values("id", "slug", "sku")),
        "variants": ProductVariant.objects.count(),
        "images": ProductImage.objects.count(),
        "orders": StoreOrder.objects.count(),
        "order_items": StoreOrderItem.objects.count(),
        "inventory_movements": InventoryMovement.objects.count(),
        "linked_assets": list(ImportedPrintAsset.objects.exclude(product=None).order_by("id").values("id", "product_id")),
        "hero_slides": hero,
        "media": media_rows,
    }

    manifest_path = backup_root / "store-reset-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=True, sort_keys=True, indent=2), encoding="utf-8")
    manifest_hash = sha256(manifest_path)
    print("PROJECT_ROOT=" + str(root))
    print("DATABASE=" + actual_db)
    print("BACKUP_ROOT=" + str(backup_root))
    print("PRODUCTS=" + str(len(manifest["products"])))
    print("VARIANTS=" + str(manifest["variants"]))
    print("IMAGES=" + str(manifest["images"]))
    print("ORDERS=" + str(manifest["orders"]))
    print("HERO_SLIDES=" + str(len(hero)))
    print("MEDIA_FILES=" + str(len(media_rows)))
    print("MANIFEST_SHA256=" + manifest_hash)
    print("STORE_RESET_PREPARE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
