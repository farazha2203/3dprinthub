from __future__ import annotations

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import ProductVariant


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
        price = getattr(variant, "price_breakdown", {}) or {}
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
            "material_weight_grams": str(getattr(variant, "material_weight_grams", 0) or 0),
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
