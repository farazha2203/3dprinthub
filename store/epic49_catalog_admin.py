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
        "homepage_slider_transition_effect",
        "sync_revision",
        "last_modified_source",
        "last_synced_at",
    ]
    list_filter = [
        "product_type",
        "availability_status",
        "price_mode",
        "commercial_license_status",
        "homepage_slider_enabled",
        "homepage_slider_transition_effect",
        "last_modified_source",
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
        "homepage_slider_title_fa",
        "homepage_slider_alt_text",
        "homepage_slider_focus_keyword",
        "last_modified_by",
    ]
    readonly_fields = [
        "legacy_slug",
        "sync_revision",
        "last_modified_source",
        "last_modified_by",
        "created_at",
        "updated_at",
        "last_synced_at",
    ]
    raw_id_fields = ["product"]
    fieldsets = [
        ("اتصال محصول", {"fields": ["product", "public_slug", "legacy_slug", "desktop_product_id", "batch_uuid", "source_hash"]}),
        ("فروش و سفارش", {"fields": ["product_type", "use_description", "availability_status", "stock_quantity", "lead_time_min_days", "lead_time_max_days", "has_3d_file"]}),
        ("قیمت", {"fields": ["price_mode", "price_min", "price_max"]}),
        ("مجوز", {"fields": ["commercial_license_status", "license_name", "license_url"]}),
        ("اطلاعات فنی و SEO", {"fields": ["technical_features", "keywords", "download_image_limit"]}),
        (
            "اسلایدر صفحه اول — انتشار و تصویر",
            {"fields": ["homepage_slider_enabled", "homepage_slider_image_url", "homepage_slider_sort_order"]},
        ),
        (
            "اسلایدر صفحه اول — SEO اختصاصی",
            {"fields": [
                "homepage_slider_title_fa",
                "homepage_slider_description_fa",
                "homepage_slider_alt_text",
                "homepage_slider_button_text",
                "homepage_slider_focus_keyword",
            ]},
        ),
        (
            "اسلایدر صفحه اول — افکت سینمایی",
            {"fields": [
                "homepage_slider_transition_effect",
                "homepage_slider_transition_duration_ms",
                "homepage_slider_display_duration_ms",
            ]},
        ),
        (
            "همگام‌سازی Desktop / Server",
            {"fields": ["sync_revision", "last_modified_source", "last_modified_by", "last_synced_at", "created_at", "updated_at"]},
        ),
    ]

    def save_model(self, request, obj, form, change):
        if change:
            obj.sync_revision = max(1, int(obj.sync_revision or 1)) + 1
        else:
            obj.sync_revision = max(1, int(obj.sync_revision or 1))
        obj.last_modified_source = "admin"
        user = getattr(request, "user", None)
        actor = ""
        if user is not None and getattr(user, "is_authenticated", False):
            actor = str(getattr(user, "username", "") or getattr(user, "email", "") or getattr(user, "pk", ""))
        obj.last_modified_by = actor[:120]
        super().save_model(request, obj, form, change)
