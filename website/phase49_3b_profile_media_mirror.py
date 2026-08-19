from __future__ import annotations

from types import MethodType

from django.contrib import admin

from .models import HomepageHeroSlide


SLIDE_TO_PROFILE = {
    "presentation_mode": "homepage_slider_presentation_mode",
    "object_fit": "homepage_slider_object_fit",
    "focal_position": "homepage_slider_focal_position",
    "image_scale_percent": "homepage_slider_image_scale_percent",
    "image_position_x_percent": "homepage_slider_position_x_percent",
    "image_position_y_percent": "homepage_slider_position_y_percent",
    "background_mode": "homepage_slider_background_mode",
    "background_color": "homepage_slider_background_color",
    "background_blur_px": "homepage_slider_background_blur_px",
    "desktop_max_width_percent": "homepage_slider_desktop_max_width_percent",
    "desktop_max_height_percent": "homepage_slider_desktop_max_height_percent",
    "mobile_max_width_percent": "homepage_slider_mobile_max_width_percent",
    "mobile_max_height_percent": "homepage_slider_mobile_max_height_percent",
}


def install() -> None:
    model_admin = admin.site._registry.get(HomepageHeroSlide)
    if model_admin is None or getattr(model_admin, "_phase49_3b_profile_media_mirror_installed", False):
        return
    original_save_model = model_admin.save_model

    def save_model(this, request, obj, form, change):
        result = original_save_model(request, obj, form, change)
        asset = getattr(obj, "asset", None)
        product = getattr(asset, "product", None) if asset is not None else None
        if product is None:
            return result
        from store.epic49_catalog_profile import ProductCatalogProfile

        profile = ProductCatalogProfile.objects.filter(product=product).first()
        if profile is None:
            return result
        changed = []
        for slide_name, profile_name in SLIDE_TO_PROFILE.items():
            value = getattr(obj, slide_name, None)
            if getattr(profile, profile_name, None) != value:
                setattr(profile, profile_name, value)
                changed.append(profile_name)
        if changed:
            profile.save(update_fields=[*changed, "updated_at"])
        return result

    model_admin.save_model = MethodType(save_model, model_admin)
    model_admin._phase49_3b_profile_media_mirror_installed = True


install()
