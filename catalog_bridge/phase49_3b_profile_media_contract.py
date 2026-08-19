from __future__ import annotations

import json

from django.http import JsonResponse

from store.epic49_catalog_profile import ProductCatalogProfile
from store.phase49_3b_profile_media import PROFILE_MEDIA_FIELDS, apply_profile_media


PROFILE_API_TO_MODEL = {
    "homepage_slider_presentation_mode": "homepage_slider_presentation_mode",
    "homepage_slider_object_fit": "homepage_slider_object_fit",
    "homepage_slider_focal_position": "homepage_slider_focal_position",
    "homepage_slider_image_scale_percent": "homepage_slider_image_scale_percent",
    "homepage_slider_position_x_percent": "homepage_slider_position_x_percent",
    "homepage_slider_position_y_percent": "homepage_slider_position_y_percent",
    "homepage_slider_background_mode": "homepage_slider_background_mode",
    "homepage_slider_background_color": "homepage_slider_background_color",
    "homepage_slider_background_blur_px": "homepage_slider_background_blur_px",
    "homepage_slider_desktop_max_width_percent": "homepage_slider_desktop_max_width_percent",
    "homepage_slider_desktop_max_height_percent": "homepage_slider_desktop_max_height_percent",
    "homepage_slider_mobile_max_width_percent": "homepage_slider_mobile_max_width_percent",
    "homepage_slider_mobile_max_height_percent": "homepage_slider_mobile_max_height_percent",
}


def _desktop_style_payload(profile_data: dict) -> dict:
    return {
        key: profile_data.get(key)
        for key in PROFILE_API_TO_MODEL
        if key in profile_data
    }


def install() -> None:
    from . import unified_views

    if getattr(unified_views, "_phase49_3b_profile_media_installed", False):
        return

    original_profile_payload = unified_views._profile_payload
    original_product_sync = unified_views.product_sync_view

    def _profile_payload(profile):
        payload = original_profile_payload(profile)
        if profile is None:
            for name in PROFILE_MEDIA_FIELDS:
                payload[name] = None
            return payload
        for name in PROFILE_MEDIA_FIELDS:
            payload[name] = getattr(profile, name, None)
        return payload

    def product_sync_view(request, product_id: int):
        response = original_product_sync(request, product_id)
        if getattr(response, "status_code", 500) != 200:
            return response
        try:
            body = json.loads((request.body or b"{}").decode("utf-8"))
            profile_data = body.get("profile") if isinstance(body, dict) and isinstance(body.get("profile"), dict) else {}
        except Exception:
            profile_data = {}
        media = _desktop_style_payload(profile_data)
        if not media:
            return response
        profile = ProductCatalogProfile.objects.filter(product_id=product_id).first()
        if profile is None:
            return response
        apply_profile_media(profile, media)
        from store.models import Product
        product = Product.objects.select_related("category").filter(pk=product_id).first()
        if product is None:
            return response
        return JsonResponse({
            "status": "ok",
            "product": unified_views.serialize_product(product),
            "revision": int(profile.sync_revision or 1),
            "contract": "epic49-unified-v1",
        })

    unified_views._profile_payload = _profile_payload
    unified_views.product_sync_view = product_sync_view
    unified_views._phase49_3b_profile_media_installed = True
