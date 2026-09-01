from __future__ import annotations

import re

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
        "material", "brand_name", "color_chip", "name", "color_type",
        "color_finish", "sale_price_per_roll", "effective_price",
        "current_stock", "current_roll_count", "is_active",
    ]
    list_filter = ["material", "color_type", "color_finish", "is_active"]
    search_fields = ["name", "code", "material__name", "brand_name"]
    list_editable = ["is_active"]
    readonly_fields = ["effective_price", "current_stock", "filament_preview"]
    fieldsets = (
        (
            "هویت Filament",
            {
                "fields": (
                    "material",
                    "brand_name",
                    "name",
                    "code",
                    "is_active",
                    "sort_order",
                ),
                "description": (
                    "Brand مرجع هویت Filament است. Manufacturer قدیمی فقط برای "
                    "سازگاری Snapshotهای قبلی در دیتابیس باقی می‌ماند."
                ),
            },
        ),
        (
            "رنگ، Finish و تصویر",
            {
                "fields": (
                    "color_type",
                    "color_finish",
                    "palette_hexes",
                    "hex_code",
                    "secondary_hex",
                    "tertiary_hex",
                    "filament_image",
                    "filament_image_url",
                    "filament_preview",
                ),
                "description": (
                    "رفتار رنگ (تک/دو/چند/گرادیانی/تغییررنگ) مستقل از Finish "
                    "(مات/براق/متالیک/شفاف/Silk) است. palette_hexes مرجع جدید "
                    "نمایش سایت است و سه HEX قدیمی فقط سازگاری را حفظ می‌کنند."
                ),
            },
        ),
        (
            "موجودی و قیمت رول",
            {
                "fields": (
                    "roll_weight_grams",
                    "stock_roll_count_snapshot",
                    "purchase_price_per_roll",
                    "sale_price_per_roll",
                    "effective_price",
                    "current_stock",
                    "low_stock_threshold_grams",
                ),
                "description": (
                    "قیمت هر گرم فقط به‌صورت خودکار از «قیمت فروش رول ÷ وزن رول» "
                    "محاسبه می‌شود. Override قدیمی قیمت هر گرم دیگر مرجع فروش نیست."
                ),
            },
        ),
        (
            "هزینه‌های تولید و پیش‌گرم",
            {
                "fields": (
                    "print_hourly_rate",
                    "supervision_hourly_rate",
                    "preheat_hours",
                    "preheat_temperature_c",
                    "preheat_hourly_rate",
                ),
            },
        ),
    )

    class Media:
        css = {"all": ("admin/phase49-admin-tabs.css",)}
        js = ("admin/phase49-admin-tabs.js",)

    @admin.display(description="رنگ")
    def color_chip(self, obj):
        palette = list(getattr(obj, "palette_hexes", None) or [])
        colors = [
            str(value).strip().upper()
            for value in [*palette, obj.hex_code, obj.secondary_hex, obj.tertiary_hex]
            if re.fullmatch(r"#[0-9A-Fa-f]{6}", str(value or "").strip())
        ]
        colors = list(dict.fromkeys(colors))[:7]
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

    @admin.display(description="قیمت خودکار هر گرم")
    def effective_price(self, obj):
        return obj.effective_sale_price_per_gram

    @admin.display(description="موجودی گرم")
    def current_stock(self, obj):
        return obj.current_stock_grams

    @admin.display(description="پیش‌نمایش Filament")
    def filament_preview(self, obj):
        url = ""
        try:
            if getattr(obj, "filament_image", None):
                url = str(obj.filament_image.url or "")
        except Exception:
            url = ""
        if not url:
            url = str(getattr(obj, "filament_image_url", "") or "")
        if not url:
            return "تصویری ثبت نشده"
        return format_html(
            '<img src="{}" alt="{}" style="max-width:220px;max-height:180px;'
            'object-fit:contain;border:1px solid #d1d5db;border-radius:12px;padding:6px;background:#fff">',
            url,
            obj.name,
        )


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
