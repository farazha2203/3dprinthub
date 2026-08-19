from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .epic49_catalog_profile import ProductCatalogProfile


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

PROFILE_MEDIA_FIELDS = (
    "homepage_slider_presentation_mode",
    "homepage_slider_object_fit",
    "homepage_slider_focal_position",
    "homepage_slider_image_scale_percent",
    "homepage_slider_position_x_percent",
    "homepage_slider_position_y_percent",
    "homepage_slider_background_mode",
    "homepage_slider_background_color",
    "homepage_slider_background_blur_px",
    "homepage_slider_desktop_max_width_percent",
    "homepage_slider_desktop_max_height_percent",
    "homepage_slider_mobile_max_width_percent",
    "homepage_slider_mobile_max_height_percent",
)


def _has(name: str) -> bool:
    try:
        ProductCatalogProfile._meta.get_field(name)
        return True
    except Exception:
        return False


def install_model_contract() -> None:
    if not _has("homepage_slider_presentation_mode"):
        models.CharField(
            max_length=20,
            choices=PRESENTATION_CHOICES,
            default="product_fit",
            verbose_name="حالت ارائه تصویر اسلایدر",
        ).contribute_to_class(ProductCatalogProfile, "homepage_slider_presentation_mode")
    if not _has("homepage_slider_object_fit"):
        models.CharField(
            max_length=12,
            choices=[("contain", "نمایش کامل"), ("cover", "پر کردن کامل")],
            default="contain",
            verbose_name="Object Fit اسلایدر",
        ).contribute_to_class(ProductCatalogProfile, "homepage_slider_object_fit")
    if not _has("homepage_slider_focal_position"):
        models.CharField(
            max_length=12,
            choices=[
                ("center", "وسط"), ("top", "بالا"), ("bottom", "پایین"),
                ("left", "چپ"), ("right", "راست"),
            ],
            default="center",
            verbose_name="نقطه تمرکز اسلایدر",
        ).contribute_to_class(ProductCatalogProfile, "homepage_slider_focal_position")
    if not _has("homepage_slider_image_scale_percent"):
        models.PositiveSmallIntegerField(
            default=100,
            validators=[MinValueValidator(60), MaxValueValidator(140)],
            verbose_name="مقیاس تصویر اسلایدر درصد",
        ).contribute_to_class(ProductCatalogProfile, "homepage_slider_image_scale_percent")
    for name, default, label in (
        ("homepage_slider_position_x_percent", 50, "موقعیت افقی تصویر اسلایدر درصد"),
        ("homepage_slider_position_y_percent", 50, "موقعیت عمودی تصویر اسلایدر درصد"),
    ):
        if not _has(name):
            models.PositiveSmallIntegerField(
                default=default,
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                verbose_name=label,
            ).contribute_to_class(ProductCatalogProfile, name)
    if not _has("homepage_slider_background_mode"):
        models.CharField(
            max_length=20,
            choices=BACKGROUND_CHOICES,
            default="blur",
            verbose_name="حالت پس‌زمینه اسلایدر",
        ).contribute_to_class(ProductCatalogProfile, "homepage_slider_background_mode")
    if not _has("homepage_slider_background_color"):
        models.CharField(
            max_length=24,
            default="#071827",
            verbose_name="رنگ پس‌زمینه اسلایدر",
        ).contribute_to_class(ProductCatalogProfile, "homepage_slider_background_color")
    if not _has("homepage_slider_background_blur_px"):
        models.PositiveSmallIntegerField(
            default=18,
            validators=[MinValueValidator(0), MaxValueValidator(60)],
            verbose_name="Blur پس‌زمینه اسلایدر",
        ).contribute_to_class(ProductCatalogProfile, "homepage_slider_background_blur_px")
    for name, default, label in (
        ("homepage_slider_desktop_max_width_percent", 78, "حداکثر عرض تصویر دسکتاپ درصد"),
        ("homepage_slider_desktop_max_height_percent", 88, "حداکثر ارتفاع تصویر دسکتاپ درصد"),
        ("homepage_slider_mobile_max_width_percent", 92, "حداکثر عرض تصویر موبایل درصد"),
        ("homepage_slider_mobile_max_height_percent", 72, "حداکثر ارتفاع تصویر موبایل درصد"),
    ):
        if not _has(name):
            models.PositiveSmallIntegerField(
                default=default,
                validators=[MinValueValidator(30), MaxValueValidator(100)],
                verbose_name=label,
            ).contribute_to_class(ProductCatalogProfile, name)


def _bounded(value, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(float(str(value if value not in (None, "") else default).replace(",", "")))
    except Exception:
        parsed = default
    return min(maximum, max(minimum, parsed))


def normalized_profile_media(data: dict) -> dict:
    presentation = str(data.get("homepage_slider_presentation_mode") or "product_fit").strip().lower()
    if presentation not in {"product_fit", "full_bleed", "framed", "cinematic"}:
        presentation = "product_fit"
    fit = str(data.get("homepage_slider_object_fit") or "").strip().lower()
    if fit not in {"contain", "cover"}:
        fit = "cover" if presentation == "full_bleed" else "contain"
    focal = str(data.get("homepage_slider_focal_position") or "center").strip().lower()
    if focal not in {"center", "top", "bottom", "left", "right"}:
        focal = "center"
    background = str(data.get("homepage_slider_background_mode") or "blur").strip().lower()
    if background not in {"solid", "blur", "gradient", "image"}:
        background = "blur"
    return {
        "homepage_slider_presentation_mode": presentation,
        "homepage_slider_object_fit": fit,
        "homepage_slider_focal_position": focal,
        "homepage_slider_image_scale_percent": _bounded(data.get("homepage_slider_image_scale_percent"), 100, 60, 140),
        "homepage_slider_position_x_percent": _bounded(data.get("homepage_slider_position_x_percent"), 50, 0, 100),
        "homepage_slider_position_y_percent": _bounded(data.get("homepage_slider_position_y_percent"), 50, 0, 100),
        "homepage_slider_background_mode": background,
        "homepage_slider_background_color": str(data.get("homepage_slider_background_color") or "#071827").strip()[:24] or "#071827",
        "homepage_slider_background_blur_px": _bounded(data.get("homepage_slider_background_blur_px"), 18, 0, 60),
        "homepage_slider_desktop_max_width_percent": _bounded(data.get("homepage_slider_desktop_max_width_percent"), 78, 30, 100),
        "homepage_slider_desktop_max_height_percent": _bounded(data.get("homepage_slider_desktop_max_height_percent"), 88, 30, 100),
        "homepage_slider_mobile_max_width_percent": _bounded(data.get("homepage_slider_mobile_max_width_percent"), 92, 30, 100),
        "homepage_slider_mobile_max_height_percent": _bounded(data.get("homepage_slider_mobile_max_height_percent"), 72, 30, 100),
    }


def apply_profile_media(profile: ProductCatalogProfile, data: dict, *, save: bool = True) -> list[str]:
    values = normalized_profile_media(data)
    changed = []
    for name, value in values.items():
        if getattr(profile, name, None) != value:
            setattr(profile, name, value)
            changed.append(name)
    if save and changed and profile.pk:
        profile.save(update_fields=[*changed, "updated_at"])
    return changed


def _patch_publish() -> None:
    from . import epic49_publish_options

    if getattr(epic49_publish_options, "_phase49_3b_profile_media_installed", False):
        return
    original = epic49_publish_options.apply_homepage_slider

    def apply_homepage_slider(product, asset, data: dict):
        profile = ProductCatalogProfile.objects.filter(product=product).first()
        if profile is not None:
            apply_profile_media(profile, data)
        return original(product, asset, data)

    epic49_publish_options.apply_homepage_slider = apply_homepage_slider
    epic49_publish_options._phase49_3b_profile_media_installed = True


def _patch_profile_admin() -> None:
    from . import epic49_catalog_admin

    if getattr(epic49_catalog_admin, "_phase49_3b_profile_media_installed", False):
        return
    original = epic49_catalog_admin._mirror_profile_to_hero

    def _mirror_profile_to_hero(profile: ProductCatalogProfile, actor: str) -> None:
        original(profile, actor)
        asset = epic49_catalog_admin._asset_for_product(profile.product)
        if asset is None:
            return
        from website.models import HomepageHeroSlide

        slide = HomepageHeroSlide.objects.filter(asset=asset).order_by("id").first()
        if slide is None:
            return
        mapping = {
            "presentation_mode": profile.homepage_slider_presentation_mode,
            "object_fit": profile.homepage_slider_object_fit,
            "focal_position": profile.homepage_slider_focal_position,
            "image_scale_percent": profile.homepage_slider_image_scale_percent,
            "image_position_x_percent": profile.homepage_slider_position_x_percent,
            "image_position_y_percent": profile.homepage_slider_position_y_percent,
            "background_mode": profile.homepage_slider_background_mode,
            "background_color": profile.homepage_slider_background_color,
            "background_blur_px": profile.homepage_slider_background_blur_px,
            "desktop_max_width_percent": profile.homepage_slider_desktop_max_width_percent,
            "desktop_max_height_percent": profile.homepage_slider_desktop_max_height_percent,
            "mobile_max_width_percent": profile.homepage_slider_mobile_max_width_percent,
            "mobile_max_height_percent": profile.homepage_slider_mobile_max_height_percent,
        }
        changed = []
        for name, value in mapping.items():
            if getattr(slide, name, None) != value:
                setattr(slide, name, value)
                changed.append(name)
        if changed:
            slide.save(update_fields=[*changed, "updated_at"])

    epic49_catalog_admin._mirror_profile_to_hero = _mirror_profile_to_hero

    model_admin = epic49_catalog_admin.ProductCatalogProfileAdmin
    fieldsets = list(model_admin.fieldsets or [])
    if not any(str(title).startswith("اسلایدر صفحه اول — قاب‌بندی") for title, _opts in fieldsets):
        insert_at = next((i + 1 for i, (title, _opts) in enumerate(fieldsets) if str(title).startswith("اسلایدر صفحه اول — افکت")), len(fieldsets))
        fieldsets.insert(insert_at, (
            "اسلایدر صفحه اول — قاب‌بندی تصویر",
            {"fields": list(PROFILE_MEDIA_FIELDS)},
        ))
        model_admin.fieldsets = fieldsets
    epic49_catalog_admin._phase49_3b_profile_media_installed = True


def install() -> None:
    install_model_contract()
    _patch_publish()
    _patch_profile_admin()


install_model_contract()
