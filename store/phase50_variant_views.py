from __future__ import annotations

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import ProductVariant


def _filament_image_url(color_option) -> str:
    if color_option is None:
        return ""
    try:
        image = getattr(color_option, "filament_image", None)
        if image:
            return str(image.url or "")
    except Exception:
        pass
    return str(getattr(color_option, "filament_image_url", "") or "")


@require_GET
def variant_commerce_options_view(request):
    raw_ids = str(request.GET.get("ids") or "")
    ids = []
    for token in raw_ids.split(","):
        token = token.strip()
        if token.isdigit():
            ids.append(int(token))
    ids = ids[:100]

    variants = (
        ProductVariant.objects.filter(
            pk__in=ids,
            is_active=True,
            product__is_active=True,
        )
        .select_related("product", "material", "quality", "color")
        .order_by("product_id", "sales_profile_sort_order", "pk")
    )
    payload = {}
    products = {}
    for variant in variants:
        product = variant.product
        products[str(product.pk)] = {
            "selection_mode": str(getattr(product, "sales_profile_selection_mode", "size_build") or "size_build"),
            "selector_label": str(getattr(product, "sales_profile_selector_label", "") or ""),
        }
        price_contract = getattr(variant, "price_breakdown", {})
        price = price_contract() if callable(price_contract) else (price_contract or {})
        color_option = getattr(variant, "color", None)
        inventory_ok = (
            not bool(getattr(variant, "track_inventory", False))
            or bool(getattr(variant, "allow_backorder", False))
            or max(
                0,
                int(getattr(variant, "stock_quantity", 0) or 0)
                - int(getattr(variant, "reserved_quantity", 0) or 0),
            ) > 0
        )
        color_stock_ok = bool(getattr(variant, "color_stock_sufficient", True))
        orderable = (
            str(getattr(variant, "stock_status", "") or "") != "out_of_stock"
            and inventory_ok
            and color_stock_ok
        )
        payload[str(variant.pk)] = {
            "product_id": product.pk,
            "profile_name": str(getattr(variant, "sales_profile_name", "") or ""),
            "profile_key": str(getattr(variant, "sales_profile_key", "") or ""),
            "profile_label": str(getattr(variant, "sales_profile_display_label", "") or ""),
            "selection_value": str(getattr(variant, "sales_profile_selection_value", "") or ""),
            "profile_is_default": bool(getattr(variant, "sales_profile_is_default", False)),
            "profile_sort_order": int(getattr(variant, "sales_profile_sort_order", 0) or 0),
            "profile_description": str(getattr(variant, "sales_profile_description", "") or ""),
            "size_label": str(getattr(variant, "size_label", "") or ""),
            "build_profile": str(getattr(variant, "build_profile", "standard") or "standard"),
            "build_profile_label": str(variant.get_build_profile_display()) if hasattr(variant, "get_build_profile_display") else "",
            "commerce_label": str(getattr(variant, "commerce_display_label", "") or ""),
            "material": str(getattr(variant, "material", "") or ""),
            "color": str(getattr(variant, "color", "") or ""),
            "filament_brand_name": str(getattr(color_option, "brand_name", "") or ""),
            # Brand is the public identity authority. Keep the manufacturer key
            # as a compatibility alias for older selector clients.
            "filament_manufacturer_name": str(getattr(color_option, "brand_name", "") or ""),
            "color_hex": str(getattr(color_option, "hex_code", "") or ""),
            "color_secondary_hex": str(getattr(color_option, "secondary_hex", "") or ""),
            "color_tertiary_hex": str(getattr(color_option, "tertiary_hex", "") or ""),
            "color_type": str(getattr(color_option, "color_type", "solid") or "solid"),
            "color_type_label": (
                str(color_option.get_color_type_display())
                if color_option is not None and hasattr(color_option, "get_color_type_display")
                else ""
            ),
            "color_finish": str(getattr(color_option, "color_finish", "matte") or "matte"),
            "color_finish_label": (
                str(color_option.get_color_finish_display())
                if color_option is not None and hasattr(color_option, "get_color_finish_display")
                else ""
            ),
            "color_palette_hexes": list(getattr(color_option, "palette_hexes", None) or [])[:7],
            "filament_image_url": _filament_image_url(color_option),
            "filament_roll_weight_grams": str(getattr(color_option, "roll_weight_grams", 0) or 0),
            "filament_sale_price_per_roll": int(getattr(color_option, "sale_price_per_roll", 0) or 0),
            "filament_sale_price_per_gram": str(getattr(color_option, "effective_sale_price_per_gram", 0) or 0),
            "current_stock_grams": str(getattr(color_option, "current_stock_grams", 0) or 0),
            "offer_print_hourly_rate": int(getattr(color_option, "print_hourly_rate", 0) or 0),
            "offer_supervision_hourly_rate": int(getattr(color_option, "supervision_hourly_rate", 0) or 0),
            "preheat_hours": str(getattr(color_option, "preheat_hours", 0) or 0),
            "preheat_temperature_c": str(getattr(color_option, "preheat_temperature_c", 0) or 0),
            "preheat_hourly_rate": int(getattr(color_option, "preheat_hourly_rate", 0) or 0),
            "color_stock_sufficient": color_stock_ok,
            "orderable": orderable,
            "material_weight_grams": str(getattr(variant, "material_weight_grams", 0) or 0),
            "support_weight_grams": str(getattr(variant, "support_weight_grams", 0) or 0),
            "final_weight_grams": str(getattr(variant, "final_weight_grams", 0) or 0),
            "print_time_minutes": int(getattr(variant, "print_time_minutes", 0) or 0),
            "unit_price": int(price.get("unit_price") or getattr(variant, "cached_unit_price", 0) or 0),
            "fixed_price_override": int(getattr(variant, "fixed_price_override", 0) or 0),
            "part_length_cm": str(getattr(variant, "part_length_cm", 0) or 0),
            "part_width_cm": str(getattr(variant, "part_width_cm", 0) or 0),
            "part_height_cm": str(getattr(variant, "part_height_cm", 0) or 0),
            "part_dimensions_label": str(getattr(variant, "part_dimensions_label", "") or ""),
            "packaging_weight_grams": str(getattr(variant, "packaging_weight_grams", 0) or 0),
            "effective_shipping_weight_grams": str(getattr(variant, "effective_shipping_weight_grams", 0) or 0),
            "package_length_cm": str(getattr(variant, "package_length_cm", 0) or 0),
            "package_width_cm": str(getattr(variant, "package_width_cm", 0) or 0),
            "package_height_cm": str(getattr(variant, "package_height_cm", 0) or 0),
        }
    return JsonResponse({"products": products, "variants": payload})
