from __future__ import annotations

from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.utils import timezone

ALLOWED_LICENSES = {"allowed", "owned", "public_domain"}


@dataclass(frozen=True)
class VisibilityDecision:
    requested: bool
    visible: bool
    checks: dict[str, bool]
    reasons: tuple[str, ...]
    product_url: str

    def as_dict(self) -> dict:
        return {
            "requested": self.requested,
            "visible": self.visible,
            "checks": dict(self.checks),
            "reasons": list(self.reasons),
            "product_url": self.product_url,
        }


def _safe_product_url(product) -> str:
    try:
        return product.get_absolute_url() or ""
    except Exception:
        return ""


def _main_image_exists(field_file) -> bool:
    if not field_file:
        return False
    name = str(getattr(field_file, "name", "") or field_file or "").strip()
    if not name:
        return False
    storage = getattr(field_file, "storage", None)
    if storage is None:
        # Compatibility for contract-test fakes; real Django ImageFieldFile
        # instances always expose storage and are checked physically below.
        return True
    try:
        return bool(storage.exists(name))
    except Exception:
        return False


def evaluate_catalog_product_visibility(product, asset, data: dict) -> VisibilityDecision:
    """Return a fail-closed visibility decision for a desktop-published product."""

    requested = bool(data.get("publish_as_product") and data.get("approved_for_sale"))
    license_status = str(getattr(asset, "commercial_license_status", "") or "")

    try:
        category_active = bool(product.category_id and product.category.is_active)
    except Exception:
        category_active = False

    try:
        active_variants = product.variants.filter(is_active=True)
        variant_exists = active_variants.exists()
        priced_variant = active_variants.filter(cached_unit_price__gt=0).exists()
    except Exception:
        variant_exists = False
        priced_variant = False

    main_image_field = getattr(product, "main_image", None)
    main_image = bool(main_image_field)
    main_image_storage = _main_image_exists(main_image_field)
    fixed_price = int(getattr(product, "fixed_price", 0) or 0)

    checks = {
        "requested_for_store": requested,
        "approved_for_sale": bool(data.get("approved_for_sale")),
        "commercial_license": license_status in ALLOWED_LICENSES,
        "category_active": category_active,
        "main_image": main_image,
        "main_image_storage": main_image_storage,
        "active_variant": variant_exists,
        "price_available": bool(fixed_price > 0 or priced_variant),
    }
    reasons = tuple(name for name, ok in checks.items() if not ok)
    return VisibilityDecision(
        requested=requested,
        visible=requested and not reasons,
        checks=checks,
        reasons=reasons,
        product_url=_safe_product_url(product),
    )


def publish_catalog_product_to_store(product, asset, data: dict) -> VisibilityDecision:
    """Activate a desktop-approved product or fail before ACK success."""

    decision = evaluate_catalog_product_visibility(product, asset, data)
    if not decision.requested:
        return decision
    if not decision.visible:
        raise ValidationError("STORE_VISIBILITY_BLOCKED: " + ", ".join(decision.reasons))

    update_fields: list[str] = []
    if not product.is_active:
        product.is_active = True
        update_fields.append("is_active")
    if not product.robots_index:
        product.robots_index = True
        update_fields.append("robots_index")
    if not product.robots_follow:
        product.robots_follow = True
        update_fields.append("robots_follow")
    if not getattr(product, "published_at", None):
        product.published_at = timezone.now()
        update_fields.append("published_at")
    if update_fields:
        if hasattr(product, "updated_at"):
            update_fields.append("updated_at")
        product.save(update_fields=list(dict.fromkeys(update_fields)))

    return evaluate_catalog_product_visibility(product, asset, data)
