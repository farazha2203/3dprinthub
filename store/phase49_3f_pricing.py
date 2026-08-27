from __future__ import annotations

import hashlib
import json
import math
from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.utils.text import slugify

from .epic49_catalog_profile import ProductCatalogProfile

PRICING_STRATEGY_CHOICES = [
    ("legacy", "رفتار قبلی"),
    ("fixed", "قیمت قطعی"),
    ("dynamic", "قیمت محاسباتی"),
]
PRODUCT_TYPE_LABELS = {
    "ready_product": "محصول آماده سفارش",
    "printable_model": "مدل قابل چاپ",
    "custom_product": "محصول سفارشی",
    "portfolio": "نمونه‌کار",
}
AVAILABILITY_LABELS = {
    "made_to_order": "تولید پس از سفارش",
    "in_stock": "آماده ارسال",
    "preorder": "پیش‌سفارش",
    "out_of_stock": "ناموجود",
    "quote_required": "نیازمند استعلام",
}


def _field_exists(model, name: str) -> bool:
    try:
        model._meta.get_field(name)
        return True
    except Exception:
        return False


def install_model_contract() -> None:
    from store.models import ProductVariant
    from website.models import Material

    if not _field_exists(ProductCatalogProfile, "pricing_strategy"):
        models.CharField(
            max_length=20,
            choices=PRICING_STRATEGY_CHOICES,
            default="legacy",
            db_index=True,
            verbose_name="روش قیمت‌گذاری Catalog Center",
        ).contribute_to_class(ProductCatalogProfile, "pricing_strategy")
    if not _field_exists(ProductCatalogProfile, "pricing_inputs"):
        models.JSONField(
            default=dict,
            blank=True,
            verbose_name="ورودی‌های محاسبه قیمت Catalog Center",
        ).contribute_to_class(ProductCatalogProfile, "pricing_inputs")
    if not _field_exists(ProductCatalogProfile, "technical_summary_fa"):
        models.TextField(
            blank=True,
            verbose_name="خلاصه فنی فارسی قابل فهم برای مشتری",
        ).contribute_to_class(ProductCatalogProfile, "technical_summary_fa")

    if not _field_exists(Material, "print_hourly_rate_toman"):
        models.PositiveBigIntegerField(
            default=0,
            verbose_name="نرخ ساعتی چاپ این متریال (تومان)",
        ).contribute_to_class(Material, "print_hourly_rate_toman")
    if not _field_exists(Material, "supervision_hourly_rate_toman"):
        models.PositiveBigIntegerField(
            default=0,
            verbose_name="نرخ ساعتی نظارت اپراتور برای این متریال (تومان)",
        ).contribute_to_class(Material, "supervision_hourly_rate_toman")

    if not _field_exists(ProductVariant, "part_weight_grams"):
        models.DecimalField(
            max_digits=10,
            decimal_places=2,
            default=0,
            verbose_name="وزن خود قطعه (گرم)",
        ).contribute_to_class(ProductVariant, "part_weight_grams")
    if not _field_exists(ProductVariant, "support_weight_grams"):
        models.DecimalField(
            max_digits=10,
            decimal_places=2,
            default=0,
            verbose_name="وزن ساپورت مصرفی",
        ).contribute_to_class(ProductVariant, "support_weight_grams")
    if not _field_exists(ProductVariant, "support_cost_multiplier"):
        models.DecimalField(
            max_digits=6,
            decimal_places=2,
            default=Decimal("1.00"),
            verbose_name="ضریب هزینه ساپورت",
        ).contribute_to_class(ProductVariant, "support_cost_multiplier")
    if not _field_exists(ProductVariant, "supervision_hourly_rate_override"):
        models.PositiveIntegerField(
            null=True,
            blank=True,
            verbose_name="نرخ ساعتی نظارت اختصاصی",
        ).contribute_to_class(ProductVariant, "supervision_hourly_rate_override")


def _safe_dict(value) -> dict:
    if isinstance(value, dict):
        return dict(value)
    try:
        parsed = json.loads(value or "{}")
    except Exception:
        return {}
    return dict(parsed) if isinstance(parsed, dict) else {}


def _positive_int(value, default=0) -> int:
    try:
        return max(0, int(float(str(value if value not in (None, "") else default).replace(",", "").strip() or 0)))
    except Exception:
        return max(0, int(default or 0))


def _decimal(value, default="0") -> Decimal:
    try:
        parsed = Decimal(str(value if value not in (None, "") else default).replace(",", "").strip() or default)
    except Exception:
        parsed = Decimal(str(default))
    return max(Decimal("0"), parsed)


def normalize_strategy(value) -> str:
    value = str(value or "legacy").strip().lower()
    return value if value in {"legacy", "fixed", "dynamic"} else "legacy"


def pricing_inputs_from_data(data: dict) -> dict:
    return _safe_dict(data.get("pricing_inputs_json") or data.get("pricing_inputs") or {})


def _round_money(value: Decimal) -> int:
    return int(Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _billable_minutes(actual: int, pricing) -> int:
    actual = max(1, int(actual or 1))
    minimum = max(1, int(getattr(pricing, "minimum_billable_minutes", 1) or 1))
    increment = max(1, int(getattr(pricing, "billing_increment_minutes", 1) or 1))
    value = max(actual, minimum)
    return int(math.ceil(value / increment) * increment)


def _profile_for_variant(variant):
    try:
        return variant.product.catalog_profile
    except Exception:
        return None


def _fixed_breakdown(variant, original_breakdown: dict, profile) -> dict:
    fixed = int(getattr(variant.product, "fixed_price", 0) or getattr(profile, "price_min", 0) or original_breakdown.get("unit_price") or 0)
    before_discount = fixed
    unit_price = fixed
    promotion = None
    try:
        promotion = next(
            (item for item in variant.product.promotions.filter(is_active=True).order_by("-created_at") if item.is_current),
            None,
        )
    except Exception:
        promotion = None
    if promotion:
        unit_price = int(promotion.apply(before_discount))
    estimated = int(original_breakdown.get("estimated_cost") or 0)
    output = dict(original_breakdown)
    output.update({
        "pricing_strategy": "fixed",
        "unit_price_before_discount": before_discount,
        "unit_price": unit_price,
        "gross_profit": int(unit_price) - estimated,
        "supervision_cost": 0,
        "billable_print_minutes": int(getattr(variant, "print_time_minutes", 0) or 0),
        "part_weight_grams": str(getattr(variant, "part_weight_grams", 0) or 0),
        "support_weight_grams": str(getattr(variant, "support_weight_grams", 0) or 0),
        "support_cost_multiplier": str(getattr(variant, "support_cost_multiplier", 1) or 1),
    })
    return output


def _dynamic_breakdown(variant, profile) -> dict:
    from store.models import PricingSetting

    pricing = PricingSetting.load()
    part = _decimal(getattr(variant, "part_weight_grams", 0))
    support = _decimal(getattr(variant, "support_weight_grams", 0))
    multiplier = _decimal(getattr(variant, "support_cost_multiplier", 1), "1")
    if multiplier <= 0:
        multiplier = Decimal("1")
    explicit_weights = part > 0 or support > 0
    actual_material_grams = (part + support) if explicit_weights else _decimal(getattr(variant, "material_weight_grams", 0))
    chargeable_grams = (part + (support * multiplier)) if explicit_weights else actual_material_grams

    color_sale = getattr(variant.color, "effective_sale_price_per_gram", None) if getattr(variant, "color_id", None) else None
    material_sale_per_gram = Decimal(
        getattr(variant, "material_price_per_gram_override", None)
        or color_sale
        or getattr(variant.material, "effective_sale_price_per_gram", 0)
        or getattr(variant.material, "sale_price_per_gram", 0)
        or getattr(variant.material, "price_per_gram", 0)
        or 0
    )
    material_cost = _round_money(material_sale_per_gram * chargeable_grams)

    actual_minutes = max(1, int(getattr(variant, "print_time_minutes", 1) or 1))
    billable_minutes = _billable_minutes(actual_minutes, pricing)
    print_hourly = int(
        getattr(variant, "hourly_rate_override", 0)
        or getattr(variant.material, "print_hourly_rate_toman", 0)
        or getattr(pricing, "default_hourly_rate", 0)
        or 0
    )
    machine_cost = _round_money(Decimal(print_hourly) * Decimal(billable_minutes) / Decimal("60"))

    supervision_override = getattr(variant, "supervision_hourly_rate_override", None)
    supervision_hourly = int(
        supervision_override
        if supervision_override is not None
        else (getattr(variant.material, "supervision_hourly_rate_toman", 0) or 0)
    )
    supervision_cost = _round_money(Decimal(supervision_hourly) * Decimal(billable_minutes) / Decimal("60"))

    bom_items = list(
        variant.product.bom_items.filter(is_active=True, is_required=True).select_related("component")
    ) if getattr(variant, "product_id", None) else []
    accessory_sale = sum(item.sale_total for item in bom_items)
    accessory_cost = sum(item.cost_total for item in bom_items)
    assembly_minutes = sum(int(item.assembly_minutes or 0) for item in bom_items)
    if getattr(variant, "assembly_fee_override", None) is not None:
        assembly_cost = int(variant.assembly_fee_override)
    else:
        assembly_cost = _round_money(
            Decimal(getattr(pricing, "assembly_hourly_rate", 0) or 0)
            * Decimal(assembly_minutes)
            / Decimal("60")
        )

    post_processing = int(getattr(variant, "post_processing_fee", 0) or 0)
    fixed_fee = int(getattr(variant, "fixed_fee", 0) or 0)
    color_adjustment = int(getattr(variant, "color_price_adjustment", 0) or 0)
    subtotal = (
        material_cost + machine_cost + supervision_cost + post_processing + fixed_fee
        + color_adjustment + accessory_sale + assembly_cost
    )
    before_discount = max(subtotal, int(getattr(pricing, "minimum_order_amount", 0) or 0))
    unit_price = before_discount
    promotion = None
    try:
        promotion = next(
            (item for item in variant.product.promotions.filter(is_active=True).order_by("-created_at") if item.is_current),
            None,
        )
    except Exception:
        promotion = None
    if promotion:
        unit_price = int(promotion.apply(before_discount))

    purchase_per_gram = Decimal(getattr(variant.material, "purchase_cost_per_gram", 0) or 0)
    direct_material_cost = _round_money(purchase_per_gram * actual_material_grams)
    estimated_cost = (
        direct_material_cost + machine_cost + supervision_cost + accessory_cost
        + assembly_cost + post_processing + fixed_fee
    )
    return {
        "pricing_strategy": "dynamic",
        "material_cost": material_cost,
        "machine_cost": machine_cost,
        "labor_cost": supervision_cost,
        "supervision_cost": supervision_cost,
        "post_processing_fee": post_processing,
        "fixed_fee": fixed_fee,
        "unit_price": int(unit_price),
        "unit_price_before_discount": int(before_discount),
        "accessory_sale": int(accessory_sale),
        "accessory_cost": int(accessory_cost),
        "assembly_cost": int(assembly_cost),
        "color_price_adjustment": color_adjustment,
        "estimated_cost": int(estimated_cost),
        "gross_profit": int(unit_price) - int(estimated_cost),
        "hourly_rate": print_hourly,
        "supervision_hourly_rate": supervision_hourly,
        "labor_percent": "0",
        "actual_print_minutes": actual_minutes,
        "billable_print_minutes": billable_minutes,
        "part_weight_grams": str(part),
        "support_weight_grams": str(support),
        "support_cost_multiplier": str(multiplier),
        "actual_material_grams": str(actual_material_grams),
        "chargeable_material_grams": str(chargeable_grams),
        "material_price_per_gram": str(material_sale_per_gram),
    }


def _install_variant_engine() -> None:
    from store.models import ProductVariant

    if getattr(ProductVariant, "_phase49_3f_pricing_installed", False):
        return
    original = ProductVariant.price_breakdown

    def price_breakdown(self):
        profile = _profile_for_variant(self)
        strategy = normalize_strategy(getattr(profile, "pricing_strategy", "legacy") if profile else "legacy")
        if strategy == "legacy":
            return original(self)
        if strategy == "fixed":
            return _fixed_breakdown(self, original(self), profile)
        return _dynamic_breakdown(self, profile)

    ProductVariant.price_breakdown = price_breakdown
    ProductVariant._phase49_3f_pricing_installed = True


def _material_rate_map(inputs: dict) -> dict[str, dict]:
    output = {}
    for item in inputs.get("material_rates") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("material") or "").strip()
        if name:
            output[name.casefold()] = item
    return output


def _quality_profiles(inputs: dict, fallback_minutes: int) -> list[dict]:
    output = []
    seen = set()
    for item in inputs.get("quality_profiles") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("quality") or "").strip()
        minutes = _positive_int(item.get("print_minutes"), 0)
        if not name or not minutes or name.casefold() in seen:
            continue
        seen.add(name.casefold())
        output.append({"name": name[:100], "print_minutes": minutes})
    if not output:
        output.append({"name": "استاندارد", "print_minutes": max(1, int(fallback_minutes or 60))})
    return output


def _quality_code(name: str) -> str:
    base = slugify(name, allow_unicode=False).strip("-")
    if not base:
        base = "q-" + hashlib.sha1(name.encode("utf-8")).hexdigest()[:10]
    return ("ep49-" + base)[:50]


def _install_publish_contract() -> None:
    from . import epic49_catalog_profile, epic49_publish_options

    if getattr(epic49_publish_options, "_phase49_3f_pricing_installed", False):
        return

    original_range = epic49_publish_options.apply_price_range
    original_variants = epic49_publish_options.apply_material_color_variants
    original_profile_sync = epic49_catalog_profile.sync_catalog_profile

    def apply_price_range(product, asset, data: dict):
        strategy = normalize_strategy(data.get("pricing_strategy"))
        if strategy == "legacy":
            return original_range(product, asset, data)
        minimum, maximum = original_range(product, asset, data)
        from store.models import Product

        if strategy == "fixed":
            fixed = minimum or _positive_int(data.get("final_price"), getattr(product, "fixed_price", 0))
            maximum = fixed
            Product.objects.filter(pk=product.pk).update(
                fixed_price=fixed,
                price_is_final=True,
                consultation_required=False,
                price_note="قیمت قطعی برای متریال، رنگ و کیفیت انتخاب‌شده توسط اپراتور.",
            )
            product.fixed_price = fixed
            product.price_is_final = True
            product.consultation_required = False
        else:
            Product.objects.filter(pk=product.pk).update(
                price_is_final=False,
                consultation_required=False,
                price_note="قیمت نهایی پس از انتخاب متریال، رنگ و کیفیت چاپ با فرمول شفاف محاسبه می‌شود؛ هزینه ارسال در تسویه جدا است.",
            )
            product.price_is_final = False
            product.consultation_required = False
        return minimum, maximum

    def apply_material_color_variants(product, asset, data: dict, *, minimum_price: int):
        base_output = original_variants(product, asset, data, minimum_price=minimum_price)
        strategy = normalize_strategy(data.get("pricing_strategy"))
        if strategy == "legacy" or not base_output:
            return base_output

        from website.models import Material
        from store.models import PrintQuality, Product, ProductVariant
        from store.phase39_models import MaterialColorOption

        inputs = pricing_inputs_from_data(data)
        rates = _material_rate_map(inputs)
        part_weight = _decimal(inputs.get("part_weight_grams"), "0")
        support_weight = _decimal(inputs.get("support_weight_grams"), "0")
        support_multiplier = _decimal(inputs.get("support_cost_multiplier"), "1") or Decimal("1")
        assembly_fee = _positive_int(inputs.get("assembly_fee"), 0)
        fallback_minutes = _positive_int((getattr(asset, "technical_specs", None) or {}).get("estimated_print_minutes"), 60)
        profiles = _quality_profiles(inputs, fallback_minutes)
        fixed_material = str(data.get("fixed_price_material_name") or inputs.get("fixed_material") or "").strip()
        fixed_color = str(data.get("fixed_price_color_name") or inputs.get("fixed_color") or "").strip()

        pairs = list(base_output)
        if strategy == "fixed":
            chosen = next(
                (
                    item for item in pairs
                    if (not fixed_material or str(item.get("material") or "").casefold() == fixed_material.casefold())
                    and (not fixed_color or str(item.get("color") or "").casefold() == fixed_color.casefold())
                ),
                pairs[0],
            )
            pairs = [chosen]
            profiles = profiles[:1]

        active_codes = []
        output = []
        for pair in pairs:
            material = Material.objects.filter(name__iexact=str(pair.get("material") or "")).order_by("id").first()
            if material is None:
                continue
            color = MaterialColorOption.objects.filter(material=material, name__iexact=str(pair.get("color") or "")).order_by("id").first()
            if color is None:
                continue
            rate = rates.get(material.name.casefold(), {})
            price_per_kg = _positive_int(rate.get("price_per_kg"), 0)
            print_hourly = _positive_int(rate.get("print_hourly_rate"), 0)
            supervision_hourly = _positive_int(rate.get("supervision_hourly_rate"), 0)
            material_updates = {}
            if price_per_kg:
                material_updates["price_per_kg"] = price_per_kg
                material_updates["sale_price_per_gram"] = max(1, round(price_per_kg / 1000))
            if print_hourly:
                material_updates["print_hourly_rate_toman"] = print_hourly
            if supervision_hourly or "supervision_hourly_rate" in rate:
                material_updates["supervision_hourly_rate_toman"] = supervision_hourly
            if material_updates:
                Material.objects.filter(pk=material.pk).update(**material_updates)
                for key, value in material_updates.items():
                    setattr(material, key, value)

            for order, profile_item in enumerate(profiles):
                quality = PrintQuality.objects.filter(name__iexact=profile_item["name"]).order_by("id").first()
                if quality is None:
                    code = _quality_code(profile_item["name"])
                    candidate = code
                    counter = 1
                    while PrintQuality.objects.filter(code=candidate).exists():
                        counter += 1
                        candidate = f"{code[:43]}-{counter}"
                    quality = PrintQuality.objects.create(
                        code=candidate,
                        name=profile_item["name"],
                        description="کیفیت تعریف‌شده از Catalog Center",
                        sort_order=100 + order,
                        is_active=True,
                    )
                code = f"EP49-3F-{product.pk}-M{material.pk}-C{color.pk}-Q{quality.pk}"[:100]
                active_codes.append(code)
                actual_material = part_weight + support_weight
                defaults = {
                    "product": product,
                    "material": material,
                    "quality": quality,
                    "color": color,
                    "material_weight_grams": actual_material if actual_material > 0 else Decimal("1"),
                    "final_weight_grams": part_weight if part_weight > 0 else (actual_material if actual_material > 0 else Decimal("1")),
                    "shipping_weight_grams": part_weight if part_weight > 0 else (actual_material if actual_material > 0 else Decimal("1")),
                    "print_time_minutes": int(profile_item["print_minutes"]),
                    "hourly_rate_override": print_hourly or None,
                    "assembly_fee_override": assembly_fee,
                    "fixed_fee": 0,
                    "lead_time_min_days": max(1, _positive_int(data.get("lead_time_min_days"), 1)),
                    "lead_time_max_days": max(1, _positive_int(data.get("lead_time_max_days"), 1)),
                    "stock_status": "made_to_order",
                    "is_active": True,
                    "part_weight_grams": part_weight,
                    "support_weight_grams": support_weight,
                    "support_cost_multiplier": support_multiplier,
                    "supervision_hourly_rate_override": supervision_hourly,
                }
                variant = ProductVariant.objects.filter(code=code).first()
                if variant is None:
                    variant = ProductVariant.objects.create(code=code, **defaults)
                else:
                    for key, value in defaults.items():
                        setattr(variant, key, value)
                    variant.save()
                variant.recalculate_price(save=True)
                output.append({
                    "material": material.name,
                    "color": color.name,
                    "quality": quality.name,
                    "variant_id": variant.pk,
                    "unit_price": variant.cached_unit_price,
                })

        ProductVariant.objects.filter(product=product, code__startswith=f"EP49-{product.pk}-").update(is_active=False)
        ProductVariant.objects.filter(product=product, code__startswith=f"EP49-3F-{product.pk}-").exclude(code__in=active_codes).update(is_active=False)
        Product.objects.filter(pk=product.pk).update(order_mode="variant")
        product.order_mode = "variant"
        return output or base_output

    def sync_catalog_profile(product, asset, data: dict, **kwargs):
        profile = original_profile_sync(product, asset, data, **kwargs)
        strategy = normalize_strategy(data.get("pricing_strategy"))
        values = {
            "pricing_strategy": strategy,
            "pricing_inputs": pricing_inputs_from_data(data),
            "technical_summary_fa": str(data.get("technical_summary_fa") or "").strip(),
        }
        changed = []
        for key, value in values.items():
            if getattr(profile, key, None) != value:
                setattr(profile, key, value)
                changed.append(key)
        if strategy == "fixed" and profile.price_min:
            if profile.price_max != profile.price_min:
                profile.price_max = profile.price_min
                changed.append("price_max")
            if profile.price_mode != "fixed":
                profile.price_mode = "fixed"
                changed.append("price_mode")
        elif strategy == "dynamic" and profile.price_mode not in {"range", "variant"}:
            profile.price_mode = "variant"
            changed.append("price_mode")
        if changed:
            profile.save(update_fields=[*dict.fromkeys(changed), "updated_at"])
        return profile

    epic49_publish_options.apply_price_range = apply_price_range
    epic49_publish_options.apply_material_color_variants = apply_material_color_variants
    epic49_catalog_profile.sync_catalog_profile = sync_catalog_profile
    epic49_publish_options._phase49_3f_pricing_installed = True


def _install_labels() -> None:
    if not hasattr(ProductCatalogProfile, "product_type_label"):
        ProductCatalogProfile.product_type_label = property(
            lambda self: PRODUCT_TYPE_LABELS.get(str(self.product_type or ""), str(self.product_type or "—"))
        )
    if not hasattr(ProductCatalogProfile, "availability_status_label"):
        ProductCatalogProfile.availability_status_label = property(
            lambda self: AVAILABILITY_LABELS.get(str(self.availability_status or ""), str(self.availability_status or "—"))
        )


def install() -> None:
    install_model_contract()
    _install_labels()
    _install_variant_engine()
    _install_publish_contract()


install_model_contract()
_install_labels()
