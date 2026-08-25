from __future__ import annotations

from django.contrib import admin

from .models import Product, ProductVariant, StoreOrderItem


VARIANT_COMMERCE_FIELDS = [
    "size_label",
    "build_profile",
    "material",
    "quality",
    "color",
    "material_weight_grams",
    "final_weight_grams",
    "packaging_weight_grams",
    "shipping_weight_grams",
    "package_length_cm",
    "package_width_cm",
    "package_height_cm",
    "print_time_minutes",
    "cached_unit_price",
    "stock_status",
    "stock_quantity",
    "is_active",
]

ORDER_SNAPSHOT_FIELDS = [
    "size_label",
    "build_profile",
    "packaging_weight_grams",
    "package_length_cm",
    "package_width_cm",
    "package_height_cm",
]


def _extend(current, additions):
    result = list(current or [])
    for item in additions:
        if item not in result:
            result.append(item)
    return result


def install() -> None:
    variant_admin = admin.site._registry.get(ProductVariant)
    if variant_admin:
        variant_admin.list_display = _extend(
            getattr(variant_admin, "list_display", []),
            ["size_label", "build_profile", "packaging_weight_grams"],
        )
        variant_admin.list_filter = _extend(
            getattr(variant_admin, "list_filter", []),
            ["build_profile"],
        )
        variant_admin.search_fields = _extend(
            getattr(variant_admin, "search_fields", []),
            ["size_label", "code"],
        )
        variant_admin.list_per_page = 50

    product_admin = admin.site._registry.get(Product)
    if product_admin:
        for inline in getattr(product_admin, "inlines", ()):
            if getattr(inline, "model", None) is ProductVariant:
                inline.fields = VARIANT_COMMERCE_FIELDS
                inline.readonly_fields = _extend(
                    getattr(inline, "readonly_fields", []),
                    ["cached_unit_price"],
                )
                inline.extra = 0

    # StoreOrderItem is normally rendered through an inline on StoreOrder. Keep
    # the immutable commerce attributes visible when that inline is present.
    for model_admin in admin.site._registry.values():
        for inline in getattr(model_admin, "inlines", ()):
            if getattr(inline, "model", None) is StoreOrderItem:
                inline.readonly_fields = _extend(
                    getattr(inline, "readonly_fields", []),
                    ORDER_SNAPSHOT_FIELDS,
                )
