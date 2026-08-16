from django.contrib import admin

from .epic49_catalog_profile import ProductCatalogProfile


@admin.register(ProductCatalogProfile)
class ProductCatalogProfileAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "public_slug",
        "product_type",
        "availability_status",
        "price_mode",
        "price_min",
        "price_max",
        "stock_quantity",
        "homepage_slider_enabled",
        "last_synced_at",
    ]
    list_filter = [
        "product_type",
        "availability_status",
        "price_mode",
        "commercial_license_status",
        "homepage_slider_enabled",
        "has_3d_file",
    ]
    search_fields = [
        "product__title",
        "product__sku",
        "public_slug",
        "legacy_slug",
        "desktop_product_id",
        "batch_uuid",
        "source_hash",
    ]
    readonly_fields = ["legacy_slug", "created_at", "updated_at", "last_synced_at"]
    raw_id_fields = ["product"]
    fieldsets = [
        ("اتصال محصول", {"fields": ["product", "public_slug", "legacy_slug", "desktop_product_id", "batch_uuid", "source_hash"]}),
        ("فروش و سفارش", {"fields": ["product_type", "use_description", "availability_status", "stock_quantity", "lead_time_min_days", "lead_time_max_days", "has_3d_file"]}),
        ("قیمت", {"fields": ["price_mode", "price_min", "price_max"]}),
        ("مجوز", {"fields": ["commercial_license_status", "license_name", "license_url"]}),
        ("اطلاعات فنی و SEO", {"fields": ["technical_features", "keywords", "download_image_limit"]}),
        ("اسلایدر صفحه اول", {"fields": ["homepage_slider_enabled", "homepage_slider_image_url", "homepage_slider_sort_order"]}),
        ("همگام‌سازی", {"fields": ["last_synced_at", "created_at", "updated_at"]}),
    ]
