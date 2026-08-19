from __future__ import annotations

from django.contrib import admin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .models import HomepageHeroSlide


PRESENTATION_CHOICES = [
    ("product_fit", "نمایش کامل محصول"),
    ("full_bleed", "پر کردن کامل اسلایدر"),
    ("framed", "کادر محصول"),
    ("cinematic", "سینمایی با پس‌زمینه"),
]
BACKGROUND_CHOICES = [
    ("solid", "رنگ ثابت"),
    ("blur", "پس‌زمینه Blur از تصویر"),
    ("gradient", "گرادیان"),
    ("image", "خود تصویر"),
]


def _has(name: str) -> bool:
    try:
        HomepageHeroSlide._meta.get_field(name)
        return True
    except Exception:
        return False


def _install_fields() -> None:
    if not _has("presentation_mode"):
        models.CharField(
            max_length=20,
            choices=PRESENTATION_CHOICES,
            default="product_fit",
            verbose_name="حالت ارائه تصویر",
        ).contribute_to_class(HomepageHeroSlide, "presentation_mode")
    if not _has("image_scale_percent"):
        models.PositiveSmallIntegerField(
            default=100,
            validators=[MinValueValidator(60), MaxValueValidator(140)],
            verbose_name="مقیاس تصویر درصد",
        ).contribute_to_class(HomepageHeroSlide, "image_scale_percent")
    for name, default, label in (
        ("image_position_x_percent", 50, "موقعیت افقی تصویر درصد"),
        ("image_position_y_percent", 50, "موقعیت عمودی تصویر درصد"),
    ):
        if not _has(name):
            models.PositiveSmallIntegerField(
                default=default,
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                verbose_name=label,
            ).contribute_to_class(HomepageHeroSlide, name)
    if not _has("background_mode"):
        models.CharField(
            max_length=20,
            choices=BACKGROUND_CHOICES,
            default="blur",
            verbose_name="حالت پس‌زمینه Hero",
        ).contribute_to_class(HomepageHeroSlide, "background_mode")
    if not _has("background_color"):
        models.CharField(default="#071827", max_length=24, verbose_name="رنگ پس‌زمینه Hero").contribute_to_class(
            HomepageHeroSlide, "background_color"
        )
    if not _has("background_blur_px"):
        models.PositiveSmallIntegerField(
            default=18,
            validators=[MinValueValidator(0), MaxValueValidator(60)],
            verbose_name="Blur پس‌زمینه پیکسل",
        ).contribute_to_class(HomepageHeroSlide, "background_blur_px")
    for name, default, label in (
        ("desktop_max_width_percent", 78, "حداکثر عرض تصویر دسکتاپ درصد"),
        ("desktop_max_height_percent", 88, "حداکثر ارتفاع تصویر دسکتاپ درصد"),
        ("mobile_max_width_percent", 92, "حداکثر عرض تصویر موبایل درصد"),
        ("mobile_max_height_percent", 72, "حداکثر ارتفاع تصویر موبایل درصد"),
    ):
        if not _has(name):
            models.PositiveSmallIntegerField(
                default=default,
                validators=[MinValueValidator(30), MaxValueValidator(100)],
                verbose_name=label,
            ).contribute_to_class(HomepageHeroSlide, name)


_install_fields()


def _install_admin() -> None:
    model_admin = admin.site._registry.get(HomepageHeroSlide)
    if model_admin is None or getattr(model_admin, "_phase49_3b_media_installed", False):
        return
    fieldsets = list(model_admin.fieldsets or [])
    output = []
    for title, options in fieldsets:
        options = dict(options)
        fields = list(options.get("fields") or [])
        if title == "۲. تصویر Hero":
            for name in (
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
            ):
                if name not in fields:
                    fields.append(name)
            # De-duplicate because object_fit/focal_position were already in 49.2C.
            options["fields"] = tuple(dict.fromkeys(fields))
            options["description"] = (
                "برای کالاها حالت «نمایش کامل محصول» پیشنهاد می‌شود تا Crop نشود. Scale، Position دقیق، پس‌زمینه، Blur و سقف اندازه "
                "Desktop/Mobile هم از Windows Catalog Center و هم از این فرم قابل مدیریت‌اند."
            )
        output.append((title, options))
    model_admin.fieldsets = tuple(output)
    filters = list(model_admin.list_filter or [])
    for name in ("object_fit", "focal_position", "presentation_mode", "background_mode"):
        if name not in filters:
            filters.append(name)
    model_admin.list_filter = tuple(filters)
    model_admin._phase49_3b_media_installed = True


_install_admin()
