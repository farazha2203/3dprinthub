from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from .models import Product, ProductVariant, StoreOrderItem

PROFILE_SELECTION_CHOICES = [
    ("list", "فهرست کامل پروفایل‌ها"),
    ("size", "انتخاب بر اساس سایز"),
    ("weight", "انتخاب بر اساس وزن"),
    ("build", "انتخاب بر اساس مدل ساخت"),
    ("size_build", "سایز ← مدل ساخت"),
    ("build_size", "مدل ساخت ← سایز"),
    ("size_weight", "سایز ← وزن"),
    ("weight_size", "وزن ← سایز"),
    ("size_weight_build", "سایز ← وزن ← مدل ساخت"),
    ("size_build_weight", "سایز ← مدل ساخت ← وزن"),
]

PROFILE_BUILD_VALUES = {"standard", "hollow", "reinforced", "solid", "custom"}
PROFILE_STOCK_VALUES = {"made_to_order", "in_stock", "preorder", "out_of_stock"}


def _has_field(model, name: str) -> bool:
    return any(field.name == name for field in model._meta.get_fields())


def _contribute(model, name: str, field: models.Field) -> None:
    if not _has_field(model, name):
        field.contribute_to_class(model, name)


def _decimal(value) -> Decimal:
    try:
        return Decimal(str(value or 0))
    except Exception:
        return Decimal("0")


def _part_dimensions_label(self) -> str:
    values = [
        _decimal(getattr(self, "part_length_cm", 0)),
        _decimal(getattr(self, "part_width_cm", 0)),
        _decimal(getattr(self, "part_height_cm", 0)),
    ]
    if not any(values):
        return ""
    return " × ".join(format(value.normalize(), "f") if value else "0" for value in values) + " سانتی‌متر"


def install_model_fields() -> None:
    try:
        field = Product._meta.get_field("sales_profile_selection_mode")
        field.choices = PROFILE_SELECTION_CHOICES
    except Exception:
        pass

    _contribute(
        ProductVariant,
        "sales_profile_description",
        models.CharField(
            max_length=300,
            blank=True,
            default="",
            verbose_name="توضیح کوتاه پروفایل",
            help_text="مثال: سبک‌تر و اقتصادی، یا سنگین‌تر و مقاوم‌تر.",
        ),
    )
    for name, label in (
        ("part_length_cm", "طول خود قطعه به سانتی‌متر"),
        ("part_width_cm", "عرض خود قطعه به سانتی‌متر"),
        ("part_height_cm", "ارتفاع خود قطعه به سانتی‌متر"),
    ):
        _contribute(
            ProductVariant,
            name,
            models.DecimalField(
                max_digits=8,
                decimal_places=2,
                default=0,
                validators=[MinValueValidator(0)],
                verbose_name=label,
            ),
        )

    for name, label in (
        ("part_length_cm", "طول قطعه هنگام سفارش"),
        ("part_width_cm", "عرض قطعه هنگام سفارش"),
        ("part_height_cm", "ارتفاع قطعه هنگام سفارش"),
    ):
        _contribute(
            StoreOrderItem,
            name,
            models.DecimalField(
                max_digits=8,
                decimal_places=2,
                default=0,
                verbose_name=label,
            ),
        )

    if not hasattr(ProductVariant, "part_dimensions_label"):
        ProductVariant.part_dimensions_label = property(_part_dimensions_label)


def _desktop_payload(asset) -> dict[str, Any]:
    payload = getattr(asset, "source_payload", None) or {}
    value = payload.get("desktop_catalog_v85") if isinstance(payload, dict) else {}
    return value if isinstance(value, dict) else {}


def _json_list(value) -> list:
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return parsed if isinstance(parsed, list) else []


def _slug_token(value: str) -> str:
    token = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(value or "").strip()).strip("-").lower()
    return token[:48] or "profile"


def _profile_rows(asset) -> list[dict[str, Any]]:
    raw = _desktop_payload(asset).get("sales_profiles_json")
    rows = []
    for index, item in enumerate(_json_list(raw), 1):
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or item.get("profile_key") or f"profile-{index}").strip()[:80]
        rows.append({**item, "key": key})
    return rows


def _resolve_material(product, name: str):
    from website.models import Material
    name = str(name or "").strip()
    if name:
        obj = Material.objects.filter(name__iexact=name).order_by("pk").first()
        if obj is None:
            obj = Material.objects.create(
                name=name[:100],
                main_usage="تعریف‌شده توسط Catalog Center",
                sample_parts="پروفایل‌های فروش 3DPrintHub",
                is_active=True,
            )
        elif not obj.is_active:
            Material.objects.filter(pk=obj.pk).update(is_active=True)
            obj.is_active = True
        return obj
    current = product.variants.filter(is_active=True).select_related("material").order_by("pk").first()
    if current is not None:
        return current.material
    obj = Material.objects.filter(is_active=True).order_by("sort_order", "pk").first()
    if obj is None:
        raise ValidationError("حداقل یک متریال فعال روی سایت لازم است.")
    return obj


def _resolve_quality(product, name: str):
    from .models import PrintQuality
    name = str(name or "").strip()
    if name:
        obj = PrintQuality.objects.filter(name__iexact=name, is_active=True).first()
        if obj is None:
            raise ValidationError(f"کیفیت چاپ پروفایل «{name}» روی سایت تعریف نشده است.")
        return obj
    current = product.variants.filter(is_active=True).select_related("quality").order_by("pk").first()
    if current is not None:
        return current.quality
    obj = PrintQuality.objects.filter(is_active=True).order_by("sort_order", "pk").first()
    if obj is None:
        raise ValidationError("حداقل یک کیفیت چاپ فعال روی سایت لازم است.")
    return obj


def _resolve_color(material, item: dict):
    from .models import MaterialColorOption
    name = str(item.get("color") or "").strip()
    if not name:
        return None
    brand = str(item.get("brand") or item.get("brand_name") or "").strip()[:120]
    manufacturer = str(item.get("manufacturer") or item.get("manufacturer_name") or "").strip()[:160]
    obj = MaterialColorOption.objects.filter(
        material=material,
        name__iexact=name,
        brand_name__iexact=brand,
    ).order_by("pk").first()

    defaults = {
        "brand_name": brand,
        "manufacturer_name": manufacturer,
        "roll_weight_grams": _number(item, "roll_weight_grams", 1000),
        "stock_roll_count_snapshot": _number(item, "stock_roll_count", 0),
        "purchase_price_per_roll": _integer(item, "purchase_price_per_roll", 0),
        "sale_price_per_roll": _integer(item, "sale_price_per_roll", 0),
        "usd_price_per_roll": _number(item, "usd_price_per_roll", 0),
        "usd_fx_rate_toman": _number(item, "usd_fx_rate_toman", 0),
        "is_active": True,
    }
    if obj is None:
        base = re.sub(r"[^a-z0-9]+", "-", f"{brand}-{name}".lower()).strip("-") or "color"
        code = base[:100]
        suffix = 1
        candidate = code
        while MaterialColorOption.objects.filter(material=material, code=candidate).exists():
            suffix += 1
            candidate = f"{code[:108]}-{suffix}"
        obj = MaterialColorOption.objects.create(
            material=material,
            name=name[:100],
            code=candidate,
            **defaults,
        )
    else:
        changed = {}
        for field, value in defaults.items():
            if getattr(obj, field) != value:
                changed[field] = value
        if changed:
            MaterialColorOption.objects.filter(pk=obj.pk).update(**changed)
            for field, value in changed.items():
                setattr(obj, field, value)
    return obj

def _number(item: dict, key: str, default=0):
    value = item.get(key, default)
    try:
        return Decimal(str(value or default))
    except Exception:
        return Decimal(str(default))


def _integer(item: dict, key: str, default=0) -> int:
    try:
        return max(0, int(float(str(item.get(key, default) or default).replace(",", ""))))
    except Exception:
        return max(0, int(default))


def sync_desktop_profile_matrix(product: Product, asset) -> int:
    """Upsert only Desktop-managed ProductVariant rows.

    Manual server-side variants are preserved. Missing Desktop profiles deactivate
    only rows with this product's CC-P<id>- prefix.
    """
    rows = _profile_rows(asset)
    if not rows:
        return 0

    desktop = _desktop_payload(asset)
    mode = str(desktop.get("sales_profile_selection_mode") or "size_weight").strip()
    allowed_modes = {code for code, _label in PROFILE_SELECTION_CHOICES}
    if mode not in allowed_modes:
        mode = "size_weight"
    selector_label = str(desktop.get("sales_profile_selector_label") or "").strip()[:120]

    product.order_mode = "variant"
    product.sales_profile_selection_mode = mode
    product.sales_profile_selector_label = selector_label
    if any(_integer(row, "fixed_price", 0) > 0 for row in rows):
        product.pricing_policy = "profile_fixed"
        product.fixed_price = 0
        product.price_is_final = all(_integer(row, "fixed_price", 0) > 0 for row in rows)
    else:
        product.pricing_policy = "formula"
        product.fixed_price = 0
        product.price_is_final = False
    product.save(
        update_fields=[
            "order_mode",
            "sales_profile_selection_mode",
            "sales_profile_selector_label",
            "pricing_policy",
            "fixed_price",
            "price_is_final",
            "updated_at",
        ]
    )

    prefix = f"CC-P{product.pk}-"
    active_codes = set()
    seen_profile_keys = set()
    default_seen = False
    created_or_updated = 0

    for index, item in enumerate(rows, 1):
        key = str(item["key"])[:80]
        if key in seen_profile_keys:
            raise ValidationError(f"کلید پروفایل تکراری است: {key}")
        seen_profile_keys.add(key)
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:10]
        code = f"{prefix}{_slug_token(key)[:32]}-{digest}"[:100]
        active_codes.add(code)
        material = _resolve_material(product, str(item.get("material") or ""))
        quality = _resolve_quality(product, str(item.get("quality") or ""))
        color = _resolve_color(material, item)

        weight = _number(item, "weight_grams", item.get("final_weight_grams") or 0)
        material_weight = _number(item, "material_weight_grams", weight)
        build_profile = str(item.get("build_profile") or "standard")
        if build_profile not in PROFILE_BUILD_VALUES:
            build_profile = "standard"
        fixed_price = _integer(item, "fixed_price", 0)
        is_default = bool(item.get("is_default")) and not default_seen
        if is_default:
            default_seen = True

        stock_status = str(item.get("stock_status") or "made_to_order")
        if stock_status not in PROFILE_STOCK_VALUES:
            raise ValidationError(
                f"وضعیت موجودی پروفایل «{stock_status}» معتبر نیست."
            )

        defaults = {
            "product": product,
            "material": material,
            "quality": quality,
            "color": color,
            "sales_profile_name": str(item.get("name") or f"پروفایل {index}")[:120],
            "sales_profile_key": key,
            "sales_profile_description": str(item.get("description") or "")[:300],
            "sales_profile_sort_order": _integer(item, "sort_order", index * 10),
            "sales_profile_is_default": is_default,
            "size_label": str(item.get("size_label") or "")[:80],
            "build_profile": build_profile,
            "material_weight_grams": material_weight,
            "final_weight_grams": weight,
            "support_weight_grams": _number(item, "support_weight_grams", 0),
            "shipping_weight_grams": _number(item, "shipping_weight_grams", 0),
            "packaging_weight_grams": _number(item, "packaging_weight_grams", 0),
            "part_length_cm": _number(item, "part_length_cm", 0),
            "part_width_cm": _number(item, "part_width_cm", 0),
            "part_height_cm": _number(item, "part_height_cm", 0),
            "package_length_cm": _number(item, "package_length_cm", 0),
            "package_width_cm": _number(item, "package_width_cm", 0),
            "package_height_cm": _number(item, "package_height_cm", 0),
            "print_time_minutes": max(1, _integer(item, "print_time_minutes", 60)),
            "fixed_price_override": fixed_price,
            "cached_unit_price": fixed_price,
            "stock_status": stock_status,
            "stock_quantity": _integer(item, "stock_quantity", 0),
            "track_inventory": bool(item.get("track_inventory", False)),
            "is_active": bool(item.get("is_active", True)),
        }
        variant = ProductVariant.objects.filter(product=product, sales_profile_key=key).order_by("pk").first()
        if variant is None:
            variant = ProductVariant(code=code, **defaults)
        else:
            variant.code = code
            for field, value in defaults.items():
                setattr(variant, field, value)
        variant.save()
        created_or_updated += 1

    managed = ProductVariant.objects.filter(product=product, code__startswith=prefix)
    managed.exclude(code__in=active_codes).update(is_active=False, sales_profile_is_default=False)
    ProductVariant.objects.filter(product=product, code__startswith="MW-FIX-", sales_profile_key="").update(is_active=False)

    if not default_seen:
        first = ProductVariant.objects.filter(product=product, code__in=active_codes, is_active=True).order_by("sales_profile_sort_order", "pk").first()
        if first is not None:
            first.sales_profile_is_default = True
            first.save(update_fields=["sales_profile_is_default"])

    return created_or_updated
