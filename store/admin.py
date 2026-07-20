from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Category,
    PricingSetting,
    PrintQuality,
    Product,
    ProductComment,
    ProductCompatibility,
    ProductImage,
    ProductLike,
    ProductRequest,
    ProductRequestImage,
    ProductReview,
    ProductVariant,
    ServicePage,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductCompatibilityInline(admin.TabularInline):
    model = ProductCompatibility
    extra = 0


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = [
        "code",
        "material",
        "quality",
        "material_weight_grams",
        "final_weight_grams",
        "print_time_minutes",
        "hourly_rate_override",
        "labor_percent_override",
        "post_processing_fee",
        "fixed_fee",
        "cached_unit_price",
        "stock_status",
        "is_active",
    ]
    readonly_fields = ["cached_unit_price"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "section", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    list_filter = ["section", "is_active"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(PrintQuality)
class PrintQualityAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "layer_height_mm", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]


@admin.register(PricingSetting)
class PricingSettingAdmin(admin.ModelAdmin):
    list_display = [
        "default_hourly_rate",
        "default_labor_percent",
        "minimum_order_amount",
        "packaging_fee",
        "tax_percent",
        "updated_at",
    ]

    def has_add_permission(self, request):
        return not PricingSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "sku", "category", "minimum_price", "is_featured", "is_active", "published_at"]
    list_editable = ["is_featured", "is_active"]
    list_filter = ["category__section", "category", "is_featured", "is_active"]
    search_fields = ["title", "sku", "short_description", "description"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["view_count", "created_at", "updated_at"]
    inlines = [ProductImageInline, ProductCompatibilityInline, ProductVariantInline]

    @admin.display(description="کمترین قیمت")
    def minimum_price(self, obj):
        price = obj.variants.filter(is_active=True).order_by("cached_unit_price").values_list("cached_unit_price", flat=True).first()
        return f"{price:,} تومان" if price else "بدون قیمت"


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "short_body", "is_approved", "created_at"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["product__title", "user__username", "body"]
    actions = ["approve_selected"]

    @admin.display(description="متن")
    def short_body(self, obj):
        return obj.body[:80]

    @admin.action(description="تأیید دیدگاه‌های انتخاب‌شده")
    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "rating", "is_verified_purchase", "is_approved", "created_at"]
    list_filter = ["rating", "is_verified_purchase", "is_approved", "created_at"]
    search_fields = ["product__title", "user__username", "title", "body"]
    actions = ["approve_selected"]

    @admin.action(description="تأیید نظرهای انتخاب‌شده")
    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)


@admin.register(ProductLike)
class ProductLikeAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "created_at"]
    search_fields = ["product__title", "user__username"]
    readonly_fields = ["product", "user", "created_at"]


@admin.register(ServicePage)
class ServicePageAdmin(admin.ModelAdmin):
    list_display = ["title", "service_type", "sort_order", "is_active", "updated_at"]
    list_editable = ["sort_order", "is_active"]
    list_filter = ["service_type", "is_active"]
    search_fields = ["title", "short_description", "content"]
    prepopulated_fields = {"slug": ("title",)}


class ProductRequestImageInline(admin.TabularInline):
    model = ProductRequestImage
    extra = 0


@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = ["title", "request_type", "full_name", "phone", "brand", "model", "status", "created_at"]
    list_editable = ["status"]
    list_filter = ["request_type", "status", "created_at"]
    search_fields = ["title", "full_name", "phone", "brand", "model", "description"]
    inlines = [ProductRequestImageInline]
