from __future__ import annotations

from django.contrib import admin

from .models import Product, ProductVariant, ShippingMethod
from .phase50_commerce_policy import StorePaymentSettings


def _extend(sequence, additions):
    result = list(sequence or [])
    for item in additions:
        if item not in result:
            result.append(item)
    return result


def _extend_product_fieldsets(product_admin) -> None:
    updated = []
    for title, options in tuple(getattr(product_admin, "fieldsets", ()) or ()):
        options = dict(options)
        fields = list(options.get("fields", ()) or ())
        if title == "اطلاعات کالا":
            for field in ("sales_notice",):
                if field not in fields:
                    fields.append(field)
        elif title == "فروش و موجودی":
            for field in ("enforce_color_stock",):
                if field not in fields:
                    fields.append(field)
        elif title == "قیمت‌گذاری":
            if "pricing_policy" not in fields:
                fields.insert(0, "pricing_policy")
            options["description"] = (
                "سیاست قیمت تعیین می‌کند مبلغ کل محصول، هر پروفایل/سایز، متریال یا ترکیب متریال+رنگ ثابت باشد؛ "
                "در حالت فرمولی موتور محاسباتی قبلی بدون تغییر استفاده می‌شود."
            )
        options["fields"] = tuple(fields)
        updated.append((title, options))
    product_admin.fieldsets = tuple(updated)


def _extend_variant_inlines(product_admin) -> None:
    for inline in getattr(product_admin, "inlines", ()):
        if getattr(inline, "model", None) is not ProductVariant:
            continue
        inline.fields = _extend(
            getattr(inline, "fields", ()),
            [
                "fixed_price_override",
                "track_inventory",
                "allow_backorder",
                "low_stock_threshold",
            ],
        )
        inline.readonly_fields = _extend(
            getattr(inline, "readonly_fields", ()),
            ["reserved_quantity"],
        )


def _extend_variant_admin() -> None:
    variant_admin = admin.site._registry.get(ProductVariant)
    if variant_admin is None:
        return
    variant_admin.list_display = _extend(
        getattr(variant_admin, "list_display", ()),
        [
            "fixed_price_override",
            "stock_status",
            "track_inventory",
            "stock_quantity",
            "reserved_quantity",
            "allow_backorder",
        ],
    )
    variant_admin.list_filter = _extend(
        getattr(variant_admin, "list_filter", ()),
        ["stock_status", "track_inventory", "allow_backorder"],
    )


def _extend_shipping_admin() -> None:
    shipping_admin = admin.site._registry.get(ShippingMethod)
    if shipping_admin is None:
        return
    shipping_admin.list_display = _extend(
        getattr(shipping_admin, "list_display", ()),
        ["service_type", "delivery_scope", "fee_mode", "is_active"],
    )
    shipping_admin.list_filter = _extend(
        getattr(shipping_admin, "list_filter", ()),
        ["service_type", "delivery_scope", "fee_mode", "is_active"],
    )
    if getattr(shipping_admin, "fields", None):
        shipping_admin.fields = _extend(
            shipping_admin.fields,
            [
                "service_type",
                "delivery_scope",
                "fee_mode",
                "requires_address",
                "requires_postal_code",
                "customer_notice",
            ],
        )


@admin.register(StorePaymentSettings)
class StorePaymentSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "حساب مقصد کارت به کارت",
            {
                "fields": (
                    "title",
                    "bank_name",
                    "account_holder",
                    "card_number",
                    "sheba_number",
                    "account_number",
                )
            },
        ),
        (
            "نمایش به مشتری",
            {
                "fields": ("transfer_instructions", "is_active"),
                "description": "این اطلاعات در صفحه پرداخت دستی سفارش نمایش داده می‌شود. شماره کارت/شبا اطلاعات پرداخت عمومی‌اند؛ هیچ PIN/CVV/رمز پویا اینجا وارد نکنید.",
            },
        ),
        ("وضعیت", {"fields": ("updated_at",), "classes": ("collapse",)}),
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        if StorePaymentSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


def install() -> None:
    product_admin = admin.site._registry.get(Product)
    if product_admin is not None:
        _extend_product_fieldsets(product_admin)
        _extend_variant_inlines(product_admin)
    _extend_variant_admin()
    _extend_shipping_admin()
