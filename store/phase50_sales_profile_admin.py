from __future__ import annotations

from uuid import uuid4

from django.contrib import admin, messages

from .models import Product, ProductVariant


PROFILE_INLINE_FIELDS = [
    "sales_profile_name",
    "sales_profile_key",
    "sales_profile_is_default",
    "sales_profile_sort_order",
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


def _extend(current, additions):
    result = list(current or [])
    for item in additions:
        if item not in result:
            result.append(item)
    return result


def _clone_variant(source: ProductVariant) -> ProductVariant:
    data = {}
    excluded = {
        "id",
        "code",
        "cached_unit_price",
        "cached_cost_price",
        "reserved_quantity",
        "sales_profile_key",
        "sales_profile_is_default",
    }
    for field in source._meta.concrete_fields:
        if field.name in excluded or field.primary_key:
            continue
        data[field.attname] = getattr(source, field.attname)

    suffix = uuid4().hex[:8]
    base_code = str(source.code or f"variant-{source.pk}")
    data["code"] = f"{base_code[:88]}-p-{suffix}"
    data["sales_profile_key"] = f"profile-{source.pk}-{suffix}"
    data["sales_profile_name"] = (
        f"{source.sales_profile_display_label} - کپی"
        if getattr(source, "sales_profile_display_label", "")
        else f"پروفایل کپی {source.pk}"
    )[:120]
    data["sales_profile_is_default"] = False
    data["sales_profile_sort_order"] = int(getattr(source, "sales_profile_sort_order", 0) or 0) + 10
    clone = ProductVariant(**data)
    clone.save()
    return clone


def install() -> None:
    variant_admin = admin.site._registry.get(ProductVariant)
    if variant_admin is not None and not getattr(variant_admin, "_phase50_sales_profile_admin", False):
        variant_admin.list_display = _extend(
            getattr(variant_admin, "list_display", []),
            [
                "sales_profile_name",
                "sales_profile_selection_value",
                "sales_profile_is_default",
                "sales_profile_sort_order",
            ],
        )
        variant_admin.list_filter = _extend(
            getattr(variant_admin, "list_filter", []),
            ["sales_profile_is_default", "product__sales_profile_selection_mode"],
        )
        variant_admin.search_fields = _extend(
            getattr(variant_admin, "search_fields", []),
            ["sales_profile_name", "sales_profile_key"],
        )
        variant_admin.list_editable = _extend(
            getattr(variant_admin, "list_editable", []),
            ["sales_profile_is_default", "sales_profile_sort_order"],
        )

        @admin.action(description="کپی پروفایل‌های فروش انتخاب‌شده")
        def duplicate_sales_profiles(modeladmin, request, queryset):
            created = 0
            for source in queryset.select_related("product", "material", "quality", "color"):
                _clone_variant(source)
                created += 1
            modeladmin.message_user(
                request,
                f"{created} پروفایل فروش کپی شد. وزن، زمان چاپ، قیمت و سایر مشخصات نسخه‌های جدید را ویرایش کنید.",
                level=messages.SUCCESS,
            )

        variant_admin.duplicate_sales_profiles = duplicate_sales_profiles
        variant_admin.actions = _extend(getattr(variant_admin, "actions", []), ["duplicate_sales_profiles"])
        variant_admin._phase50_sales_profile_admin = True

    product_admin = admin.site._registry.get(Product)
    if product_admin is None or getattr(product_admin, "_phase50_sales_profile_admin", False):
        return

    product_admin.list_display = _extend(
        getattr(product_admin, "list_display", []),
        ["sales_profile_selection_mode"],
    )
    product_admin.list_filter = _extend(
        getattr(product_admin, "list_filter", []),
        ["sales_profile_selection_mode"],
    )

    fieldsets = list(getattr(product_admin, "fieldsets", ()) or ())
    if fieldsets and not any(title == "پروفایل‌های فروش و روش انتخاب" for title, _opts in fieldsets):
        fieldsets.append((
            "پروفایل‌های فروش و روش انتخاب",
            {
                "fields": ("sales_profile_selection_mode", "sales_profile_selector_label"),
                "description": "معیار نمایش و انتخاب پروفایل‌ها برای مشتری را مشخص کنید؛ مثال: سایز، وزن، مدل ساخت یا انتخاب دو مرحله‌ای.",
            },
        ))
        product_admin.fieldsets = tuple(fieldsets)

    for inline in getattr(product_admin, "inlines", ()):
        if getattr(inline, "model", None) is ProductVariant:
            inline.fields = PROFILE_INLINE_FIELDS
            inline.readonly_fields = _extend(
                getattr(inline, "readonly_fields", []),
                ["cached_unit_price"],
            )
            inline.extra = 0

    product_admin._phase50_sales_profile_admin = True
