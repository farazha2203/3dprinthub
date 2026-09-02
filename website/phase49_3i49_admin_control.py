from __future__ import annotations

from django.contrib import admin

from .models import HomepageHeroSlide


HERO_COMPOSITION_FIELDS = (
    "presentation_mode",
    "object_fit",
    "focal_position",
    "image_scale_percent",
    "image_position_x_percent",
    "image_position_y_percent",
    "background_mode",
    "background_color",
    "background_blur_px",
    "desktop_max_width_percent",
    "desktop_max_height_percent",
    "mobile_max_width_percent",
    "mobile_max_height_percent",
)


def install() -> None:
    model_admin = admin.site._registry.get(HomepageHeroSlide)
    if model_admin is None or getattr(
        model_admin,
        "_phase49_3i49_admin_control_installed",
        False,
    ):
        return

    readonly = list(getattr(model_admin, "readonly_fields", ()) or ())
    for name in (
        "selected_image_preview",
        "sync_revision",
        "last_modified_source",
        "last_modified_by",
        "created_at",
        "updated_at",
    ):
        if name not in readonly:
            readonly.append(name)
    model_admin.readonly_fields = tuple(readonly)

    # Practical UI / Lean UX / Don't Make Me Think:
    # organize by the operator's task order and keep sync diagnostics last.
    model_admin.fieldsets = (
        (
            "۱. محصول و تصویر",
            {
                "fields": (
                    "asset",
                    "selected_asset_image",
                    "image_url",
                    "selected_image_preview",
                ),
                "description": (
                    "ابتدا محصول و تصویر واقعی را انتخاب کنید. URL دستی مسیر جایگزین است؛ "
                    "تصویر عمومی Product بر فایل موقت کاتالوگ اولویت دارد."
                ),
            },
        ),
        (
            "۲. محتوا و SEO اسلاید",
            {
                "fields": (
                    "group_title",
                    "title_override",
                    "description",
                    "image_alt_text",
                    "button_text",
                ),
                "description": (
                    "متن کوتاه، خوانا و هم‌راستا با محتوای واقعی Product نگه داشته شود."
                ),
            },
        ),
        (
            "۳. قاب‌بندی و Responsive",
            {
                "fields": HERO_COMPOSITION_FIELDS,
                "description": (
                    "Fit، نقطه تمرکز، Scale، Position، Background و محدودیت‌های "
                    "Desktop/Mobile همان قرارداد Windows Catalog Center هستند."
                ),
            },
        ),
        (
            "۴. Motion و Timing",
            {
                "fields": (
                    "transition_effect",
                    "transition_duration_ms",
                    "display_duration_ms",
                ),
                "description": (
                    "حرکت باید هدفمند و آرام باشد؛ زمان نمایش باید فرصت خواندن متن را بدهد."
                ),
            },
        ),
        (
            "۵. انتشار",
            {
                "fields": ("sort_order", "is_active"),
                "description": (
                    "فعال‌سازی اقدام نهایی این فرم است. ترتیب نمایش مستقل از محتوا مدیریت می‌شود."
                ),
            },
        ),
        (
            "۶. همگام‌سازی Desktop / Server",
            {
                "fields": (
                    "sync_revision",
                    "last_modified_source",
                    "last_modified_by",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
                "description": (
                    "اطلاعات تشخیصی برای Conflict و Audit؛ در ویرایش روزمره تغییر نمی‌کنند."
                ),
            },
        ),
    )

    desired = (
        "slide_preview",
        "effective_title_display",
        "presentation_mode",
        "transition_effect",
        "timing_display",
        "sort_order",
        "is_active",
        "last_modified_source",
        "sync_revision",
        "edit_slide_link",
    )
    available_names = set(dir(model_admin)) | {
        field.name for field in HomepageHeroSlide._meta.get_fields()
    }
    model_admin.list_display = tuple(
        name for name in desired if name in available_names
    )
    model_admin.list_editable = tuple(
        name
        for name in ("transition_effect", "sort_order", "is_active")
        if name in model_admin.list_display
    )
    model_admin._phase49_3i49_admin_control_installed = True


install()
