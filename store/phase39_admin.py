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
    return format_html('<strong style="color:#059669">{:,.0f} تومان</strong>', total)
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
    list_display = ["material", "color_chip", "name", "effective_price", "current_stock", "current_roll_count", "is_active"]
    list_filter = ["material", "is_active"]
    search_fields = ["name", "code", "material__name"]
    list_editable = ["is_active"]

    @admin.display(description="رنگ")
    def color_chip(self, obj):
        color = obj.hex_code or "#e5e7eb"
        return format_html('<span style="display:inline-block;width:24px;height:24px;border-radius:50%;background:{};border:1px solid #999"></span>', color)

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
