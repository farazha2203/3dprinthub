from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.db.models.deletion import Collector, ProtectedError, RestrictedError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from store.models import (
    ImportedPrintAsset,
    InventoryMovement,
    PrintQuality,
    Product,
    ProductImage,
    ProductVariant,
    StoreOrder,
    StoreOrderItem,
)
from store.phase39_models import FilamentBrand, MaterialColorOption
from website.models import HomepageHeroSlide, Material, PortfolioItem

from .views import _authorized, _unauthorized

CONFIRMATION = "RESET_IMPORTED_STORE_PRODUCTS"
BACKUP_SUFFIX = "-store-product-reset"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _allowed_backup_root() -> Path:
    configured = str(getattr(settings, "PHASE50_STORE_RESET_BACKUP_ROOT", "") or "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path(settings.BASE_DIR).resolve().parent / "3dprinthub-deploy-backups").resolve()


def _field_name(field_file) -> str:
    try:
        return str(field_file.name or "").strip()
    except Exception:
        return ""


def _live_product_media_names() -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for product in Product.objects.order_by("id"):
        for field in (product.main_image, product.og_image, product.model_file):
            name = _field_name(field)
            if name and name not in seen:
                seen.add(name)
                names.append(name)
    for row in ProductImage.objects.order_by("id"):
        name = _field_name(row.image)
        if name and name not in seen:
            seen.add(name)
            names.append(name)
    return names


def _current_counts() -> dict[str, int]:
    return {
        "products": Product.objects.count(),
        "variants": ProductVariant.objects.count(),
        "images": ProductImage.objects.count(),
        "orders": StoreOrder.objects.count(),
        "order_items": StoreOrderItem.objects.count(),
        "inventory_movements": InventoryMovement.objects.count(),
        "linked_assets": ImportedPrintAsset.objects.exclude(product=None).count(),
        "hero_slides": HomepageHeroSlide.objects.count(),
    }


def _master_counts() -> dict[str, int]:
    return {
        "assets": ImportedPrintAsset.objects.count(),
        "portfolio": PortfolioItem.objects.count(),
        "materials": Material.objects.count(),
        "qualities": PrintQuality.objects.count(),
        "colors": MaterialColorOption.objects.count(),
        "filament_brands": FilamentBrand.objects.count(),
    }


def _deletion_blockers() -> list[str]:
    blockers: list[str] = []
    if InventoryMovement.objects.exists():
        blockers.append("inventory_movements_present")
    try:
        collector = Collector(using=Product.objects.db)
        collector.collect(Product.objects.all())
    except (ProtectedError, RestrictedError) as exc:
        protected = sorted({obj._meta.label for obj in getattr(exc, "protected_objects", [])})
        blockers.append("protected_relations:" + (",".join(protected) or type(exc).__name__))
    return blockers


def _preflight_payload() -> dict:
    counts = _current_counts()
    blockers = _deletion_blockers()
    if counts["products"] <= 0:
        blockers.append("store_already_empty")
    if counts["linked_assets"] != counts["products"]:
        blockers.append("non_catalog_products_present")
    return {
        "status": "ready" if not blockers else "blocked",
        "contract": "phase50-store-reset-v2",
        "eligible": not blockers,
        "counts": counts,
        "master": _master_counts(),
        "blockers": blockers,
        "preserves": {
            "source_assets": True,
            "master_data": True,
            "portfolio": True,
            "hero_slides": True,
            "orders_and_snapshots": True,
        },
    }


def _load_verified_backup(raw_root: str, counts: dict[str, int]) -> tuple[Path, dict, list[dict]]:
    allowed = _allowed_backup_root()
    root = Path(str(raw_root or "")).expanduser().resolve()
    if root.parent != allowed or not root.name.endswith(BACKUP_SUFFIX):
        raise ValueError("backup_root is outside the approved store-reset backup directory")

    db_dump = root / "database-before-3i53.sql.gz"
    manifest_path = root / "store-reset-manifest.json"
    if not db_dump.is_file() or db_dump.stat().st_size < 1024:
        raise ValueError("verified MySQL backup is missing")
    try:
        with gzip.open(db_dump, "rb") as handle:
            prefix = handle.read(4096)
    except Exception as exc:
        raise ValueError("MySQL backup gzip is invalid") from exc
    if b"MySQL dump" not in prefix and b"MariaDB dump" not in prefix:
        raise ValueError("MySQL backup payload is invalid")
    if not manifest_path.is_file():
        raise ValueError("store reset manifest is missing")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError("store reset manifest is invalid") from exc
    if not isinstance(manifest, dict):
        raise ValueError("store reset manifest must be an object")

    expected = {
        "products": len(manifest.get("products") or []),
        "variants": int(manifest.get("variants") or 0),
        "images": int(manifest.get("images") or 0),
        "orders": int(manifest.get("orders") or 0),
        "order_items": int(manifest.get("order_items") or 0),
        "inventory_movements": int(manifest.get("inventory_movements") or 0),
        "linked_assets": len(manifest.get("linked_assets") or []),
        "hero_slides": len(manifest.get("hero_slides") or []),
    }
    if expected != counts:
        raise ValueError("backup manifest no longer matches the live Store state")

    hero_ids = [int(item.get("id") or 0) for item in (manifest.get("hero_slides") or [])]
    live_hero_ids = list(HomepageHeroSlide.objects.order_by("id").values_list("id", flat=True))
    if hero_ids != live_hero_ids:
        raise ValueError("backup Hero-slide set no longer matches the live Store state")

    media_root = Path(settings.MEDIA_ROOT).resolve()
    live_names = set(_live_product_media_names())
    verified_media: list[dict] = []
    manifest_names: set[str] = set()
    for item in manifest.get("media") or []:
        if not isinstance(item, dict) or not item.get("exists"):
            continue
        name = str(item.get("name") or "").strip().replace("\\", "/")
        expected_hash = str(item.get("sha256") or "").strip().lower()
        if not name or len(expected_hash) != 64 or name in manifest_names:
            raise ValueError("backup media manifest contains an invalid row")
        manifest_names.add(name)
        live = (media_root / name).resolve()
        backup = (root / "media" / name).resolve()
        if media_root != live and media_root not in live.parents:
            raise ValueError("live media path escapes MEDIA_ROOT")
        if root != backup and root not in backup.parents:
            raise ValueError("backup media path escapes backup_root")
        if not live.is_file() or not backup.is_file():
            raise ValueError("live or backup Product media is missing")
        if _sha256(live) != expected_hash or _sha256(backup) != expected_hash:
            raise ValueError("Product media hash no longer matches the verified backup")
        verified_media.append({"name": name, "live": live, "backup": backup, "sha256": expected_hash})
    if live_names != manifest_names:
        raise ValueError("backup media set no longer matches Product-owned live media")
    return root, manifest, verified_media


@csrf_exempt
@require_http_methods(["GET", "POST"])
def store_reset_view(request):
    if not _authorized(request):
        return _unauthorized()
    if request.method == "GET":
        return JsonResponse(_preflight_payload())
    try:
        payload = json.loads((request.body or b"{}").decode("utf-8"))
    except Exception:
        return JsonResponse({"status": "invalid_request", "detail": "A valid JSON object is required."}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"status": "invalid_request", "detail": "A JSON object is required."}, status=400)
    if str(payload.get("confirmation") or "") != CONFIRMATION:
        return JsonResponse({"status": "invalid_request", "detail": "Explicit reset confirmation is required."}, status=400)
    if not all(bool(payload.get(name)) for name in ("preserve_source_assets", "preserve_master_data", "preserve_portfolio")):
        return JsonResponse({"status": "invalid_request", "detail": "Preservation contract is required."}, status=400)

    counts = _current_counts()
    requested = {
        "products": int(payload["expected_products"]) if "expected_products" in payload else -1,
        "variants": int(payload["expected_variants"]) if "expected_variants" in payload else -1,
        "images": int(payload["expected_images"]) if "expected_images" in payload else -1,
        "hero_slides": int(payload["expected_hero_slides"]) if "expected_hero_slides" in payload else -1,
    }
    for key, value in requested.items():
        if value != counts[key]:
            return JsonResponse({"status": "conflict", "detail": f"Live {key} count changed.", "counts": counts}, status=409)
    if counts["products"] <= 0:
        return JsonResponse({"status": "conflict", "detail": "Store is already empty.", "counts": counts}, status=409)
    blockers = _deletion_blockers()
    if blockers:
        return JsonResponse({"status": "conflict", "detail": "Protected commerce history blocks Product deletion.", "counts": counts, "blockers": blockers}, status=409)
    if counts["linked_assets"] != counts["products"]:
        return JsonResponse({"status": "conflict", "detail": "Only fully imported Catalog Products may be reset.", "counts": counts}, status=409)

    try:
        backup_root, manifest, verified_media = _load_verified_backup(str(payload.get("backup_root") or ""), counts)
    except ValueError as exc:
        return JsonResponse({"status": "conflict", "detail": str(exc), "counts": counts}, status=409)

    master_before = _master_counts()
    hero_ids = [int(item.get("id") or 0) for item in manifest.get("hero_slides") or []]
    hero_before = list(HomepageHeroSlide.objects.order_by("id").values_list("id", flat=True))
    with transaction.atomic():
        product_result = Product.objects.all().delete()

    after = _current_counts()
    if any(after[key] for key in ("products", "variants", "images", "linked_assets")):
        return JsonResponse({"status": "failed", "detail": "Database reset did not reach an empty Product Store.", "counts": after}, status=500)
    hero_after = list(HomepageHeroSlide.objects.order_by("id").values_list("id", flat=True))
    if hero_before != hero_ids or hero_after != hero_ids:
        return JsonResponse({"status": "failed", "detail": "Homepage Hero slides changed unexpectedly.", "before": hero_before, "after": hero_after}, status=500)
    master_after = _master_counts()
    if master_before != master_after:
        return JsonResponse({"status": "failed", "detail": "Master/source data changed unexpectedly.", "before": master_before, "after": master_after}, status=500)

    deleted_media: list[str] = []
    media_errors: list[str] = []
    for item in verified_media:
        live = item["live"]
        try:
            if live.is_file():
                if _sha256(live) != item["sha256"]:
                    raise RuntimeError("hash changed after database reset")
                live.unlink()
                deleted_media.append(item["name"])
        except Exception as exc:
            media_errors.append(f"{item['name']}:{type(exc).__name__}")

    result = {
        "status": "ok" if not media_errors else "partial",
        "contract": "phase50-store-reset-v2",
        "backup_root": str(backup_root),
        "before": counts,
        "after": _current_counts(),
        "product_delete": list(product_result),
        "hero_slides_preserved": hero_after,
        "orders_preserved": after["orders"],
        "order_items_preserved": after["order_items"],
        "deleted_media_count": len(deleted_media),
        "media_errors": media_errors,
        "preserved": master_after,
    }
    status_code = 200 if not media_errors else 500
    return JsonResponse(result, status=status_code)
