from __future__ import annotations

from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html

from .models import PricingSetting, Product, ProductReview, ProductVariant
from .phase39_models import (
    AccessoryComponent, MaterialColorOption, ProductBOMItem, ProductMaterialRecommendation,
    ProductPromotion, ProductReviewImage, ShippingRateRule,
)


class ProductMaterialRecommendationInline(admin.TabularInline):
    model = ProductMaterialRecommendation
    extra = 0


class ProductBOMItemInline(admin.TabularInline):
    model = ProductBOMItem
    extra = 0


class ProductPromotionInline(admin.TabularInline):
    model = ProductPromotion
    extra = 0


class ProductReviewImageInline(admin.TabularInline):
    model = ProductReviewImage
    extra = 0


def _augment_registered(model, inline_classes=(), list_methods=()):
    current = admin.site._registry.get(model)
    if not current:
        return
    cls = current.__class__
    cls.inlines = list(getattr(cls, "inlines", [])) + [x for x in inline_classes if x not in getattr(cls, "inlines", [])]
    display = list(getattr(cls, "list_display", []))
    for name in list_methods:
        if name not in display:
            display.append(name)
    cls.list_display = display


def sold_quantity_admin(self, obj):
    return obj.store_order_items.filter(order__payment_status="paid").aggregate(v=Sum("quantity"))["v"] or 0
sold_quantity_admin.short_description = "فروش موفق"


def estimated_profit_admin(self, obj):
    total = obj.store_order_items.filter(order__payment_status="paid").aggregate(v=Sum("gross_profit"))["v"] or 0
    # Django 6 format_html() escapes every argument before interpolation, so a
    # numeric format specifier such as {:,.0f} is applied to SafeString and
    # raises ValueError. Format the numeric value first, then pass plain text
    # through format_html() for safe markup output.
    formatted_total = f"{total:,.0f}"
    return format_html('<strong style="color:#059669">{} تومان</strong>', formatted_total)
estimated_profit_admin.short_description = "سود ثبت‌شده"

product_admin = admin.site._registry.get(Product)
if product_admin:
    setattr(product_admin.__class__, "sold_quantity_admin", sold_quantity_admin)
    setattr(product_admin.__class__, "estimated_profit_admin", estimated_profit_admin)
_augment_registered(Product, [ProductMaterialRecommendationInline, ProductBOMItemInline, ProductPromotionInline], ["sold_quantity_admin", "estimated_profit_admin"])
_augment_registered(ProductReview, [ProductReviewImageInline], [])

# Extend the existing ProductVariant inline instead of replacing the project's current admin.
if product_admin:
    for inline in getattr(product_admin.__class__, "inlines", []):
        if getattr(inline, "model", None) is ProductVariant:
            fields = list(getattr(inline, "fields", []) or [])
            for name in ["color", "material_price_per_gram_override", "color_price_adjustment", "assembly_fee_override", "cached_cost_price"]:
                if name not in fields:
                    fields.append(name)
            inline.fields = fields
            readonly = list(getattr(inline, "readonly_fields", []) or [])
            if "cached_cost_price" not in readonly:
                readonly.append("cached_cost_price")
            inline.readonly_fields = readonly

pricing_admin = admin.site._registry.get(PricingSetting)
if pricing_admin:
    display = list(getattr(pricing_admin.__class__, "list_display", []) or [])
    for name in ["vat_enabled", "tax_percent", "assembly_hourly_rate", "default_margin_percent"]:
        if name not in display:
            display.append(name)
    pricing_admin.__class__.list_display = display


@admin.register(MaterialColorOption)
class MaterialColorOptionAdmin(admin.ModelAdmin):
    list_display = [
        "material", "color_chip", "name", "color_type", "effective_price",
        "current_stock", "current_roll_count", "is_active",
    ]
    list_filter = ["material", "color_type", "is_active"]
    search_fields = ["name", "code", "material__name"]
    list_editable = ["is_active"]
    fieldsets = (
        ("متریال و رنگ", {
            "fields": ("material", "name", "code", "color_type", "is_active", "sort_order")
        }),
        ("نمایش رنگ", {
            "fields": ("hex_code", "secondary_hex", "tertiary_hex"),
            "description": "برای رنگ ساده فقط HEX اصلی کافی است. برای دو‌رنگ/چندرنگ/گرادیانی HEX دوم و سوم را هم وارد کنید.",
        }),
        ("قیمت و موجودی", {
            "fields": ("sale_price_per_gram_override", "low_stock_threshold_grams")
        }),
    )

    @admin.display(description="رنگ")
    def color_chip(self, obj):
        colors = [x for x in [obj.hex_code, obj.secondary_hex, obj.tertiary_hex] if x]
        if not colors:
            colors = ["#e5e7eb"]
        if len(colors) == 1:
            background = colors[0]
        else:
            step = 100 / len(colors)
            pieces = []
            for index, color in enumerate(colors):
                start = int(index * step)
                end = 100 if index == len(colors) - 1 else int((index + 1) * step)
                pieces.append(f"{color} {start}% {end}%")
            background = "linear-gradient(135deg," + ",".join(pieces) + ")"
        return format_html(
            '<span title="{}" style="display:inline-block;width:38px;height:24px;border-radius:8px;background:{};border:1px solid #999"></span>',
            obj.get_color_type_display(),
            background,
        )

    @admin.display(description="قیمت هر گرم")
    def effective_price(self, obj):
        return obj.effective_sale_price_per_gram

    @admin.display(description="موجودی گرم")
    def current_stock(self, obj):
        return obj.current_stock_grams


@admin.register(AccessoryComponent)
class AccessoryComponentAdmin(admin.ModelAdmin):
    list_display = ["name", "sku", "unit_cost", "default_sale_price", "stock_quantity", "low_stock_threshold", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "sku"]


@admin.register(ProductPromotion)
class ProductPromotionAdmin(admin.ModelAdmin):
    list_display = ["product", "kind", "title", "discount_percent", "discount_amount", "stock_limit", "starts_at", "ends_at", "is_active"]
    list_filter = ["kind", "is_active"]
    search_fields = ["product__title", "title"]


@admin.register(ShippingRateRule)
class ShippingRateRuleAdmin(admin.ModelAdmin):
    list_display = ["shipping_method", "title", "min_weight_grams", "max_weight_grams", "base_fee", "per_kg_fee", "is_active"]
    list_filter = ["shipping_method", "is_active"]
