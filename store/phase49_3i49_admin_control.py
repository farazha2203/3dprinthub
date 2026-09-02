from __future__ import annotations

from django.contrib import admin

from .epic49_catalog_profile import ProductCatalogProfile
from .phase49_3b_profile_media import PROFILE_MEDIA_FIELDS


def install() -> None:
    model_admin = admin.site._registry.get(ProductCatalogProfile)
    if model_admin is None or getattr(
        model_admin,
        "_phase49_3i49_admin_control_installed",
        False,
    ):
        return

    model_admin.fieldsets = (
        (
            "۱. اتصال و هویت Product",
            {
                "fields": (
                    "product",
                    "public_slug",
                    "legacy_slug",
                    "desktop_product_id",
                    "batch_uuid",
                    "source_hash",
                ),
            },
        ),
        (
            "۲. فروش، سفارش و موجودی",
            {
                "fields": (
                    "product_type",
                    "use_description",
                    "availability_status",
                    "stock_quantity",
                    "lead_time_min_days",
                    "lead_time_max_days",
                    "has_3d_file",
                ),
            },
        ),
        (
            "۳. قیمت",
            {
                "fields": ("price_mode", "price_min", "price_max"),
                "description": (
                    "قیمت اینجا همان قرارداد Product/Variant سایت است؛ "
                    "نرخ Filament از کتابخانه مرکزی Filament می‌آید."
                ),
            },
        ),
        (
            "۴. منبع، مجوز و اطلاعات فنی",
            {
                "fields": (
                    "commercial_license_status",
                    "license_name",
                    "license_url",
                    "technical_features",
                    "keywords",
                    "download_image_limit",
                ),
            },
        ),
        (
            "۵. اسلایدر — محتوا و انتشار",
            {
                "fields": (
                    "homepage_slider_enabled",
                    "homepage_slider_image_url",
                    "homepage_slider_sort_order",
                    "homepage_slider_title_fa",
                    "homepage_slider_description_fa",
                    "homepage_slider_alt_text",
                    "homepage_slider_button_text",
                    "homepage_slider_focus_keyword",
                ),
            },
        ),
        (
            "۶. اسلایدر — قاب‌بندی و Responsive",
            {
                "fields": tuple(PROFILE_MEDIA_FIELDS),
                "description": (
                    "این کنترل‌ها با Hero Studio و Windows Catalog Center یک قرارداد مشترک دارند."
                ),
            },
        ),
        (
            "۷. اسلایدر — Motion و Timing",
            {
                "fields": (
                    "homepage_slider_transition_effect",
                    "homepage_slider_transition_duration_ms",
                    "homepage_slider_display_duration_ms",
                ),
            },
        ),
        (
            "۸. همگام‌سازی Desktop / Server",
            {
                "fields": (
                    "sync_revision",
                    "last_modified_source",
                    "last_modified_by",
                    "last_synced_at",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
    model_admin._phase49_3i49_admin_control_installed = True


install()
