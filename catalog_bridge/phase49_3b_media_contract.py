from __future__ import annotations

import json

from django.http import JsonResponse


MEDIA_FIELDS = {
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
}


def _bounded(value, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(float(str(value if value not in (None, "") else default).replace(",", "")))
    except Exception:
        parsed = default
    return min(maximum, max(minimum, parsed))


def _apply(slide, data: dict) -> list[str]:
    changed = []
    presentation = str(data.get("presentation_mode") or getattr(slide, "presentation_mode", "product_fit") or "product_fit").strip().lower()
    if presentation not in {"product_fit", "full_bleed", "framed", "cinematic"}:
        presentation = "product_fit"
    fit = str(data.get("object_fit") or getattr(slide, "object_fit", "contain") or "contain").strip().lower()
    if fit not in {"contain", "cover"}:
        fit = "cover" if presentation == "full_bleed" else "contain"
    focal = str(data.get("focal_position") or getattr(slide, "focal_position", "center") or "center").strip().lower()
    if focal not in {"center", "top", "bottom", "left", "right"}:
        focal = "center"
    background = str(data.get("background_mode") or getattr(slide, "background_mode", "blur") or "blur").strip().lower()
    if background not in {"solid", "blur", "gradient", "image"}:
        background = "blur"
    values = {
        "presentation_mode": presentation,
        "object_fit": fit,
        "focal_position": focal,
        "image_scale_percent": _bounded(data.get("image_scale_percent"), getattr(slide, "image_scale_percent", 100), 60, 140),
        "image_position_x_percent": _bounded(data.get("image_position_x_percent"), getattr(slide, "image_position_x_percent", 50), 0, 100),
        "image_position_y_percent": _bounded(data.get("image_position_y_percent"), getattr(slide, "image_position_y_percent", 50), 0, 100),
        "background_mode": background,
        "background_color": str(data.get("background_color") or getattr(slide, "background_color", "#071827") or "#071827")[:24],
        "background_blur_px": _bounded(data.get("background_blur_px"), getattr(slide, "background_blur_px", 18), 0, 60),
        "desktop_max_width_percent": _bounded(data.get("desktop_max_width_percent"), getattr(slide, "desktop_max_width_percent", 78), 30, 100),
        "desktop_max_height_percent": _bounded(data.get("desktop_max_height_percent"), getattr(slide, "desktop_max_height_percent", 88), 30, 100),
        "mobile_max_width_percent": _bounded(data.get("mobile_max_width_percent"), getattr(slide, "mobile_max_width_percent", 92), 30, 100),
        "mobile_max_height_percent": _bounded(data.get("mobile_max_height_percent"), getattr(slide, "mobile_max_height_percent", 72), 30, 100),
    }
    for name, value in values.items():
        if getattr(slide, name, None) != value:
            setattr(slide, name, value)
            changed.append(name)
    if changed:
        slide.save(update_fields=[*changed, "updated_at"])
    return changed


def install() -> None:
    # Ensure runtime fields exist even if app ordering changes.
    from website import phase49_3b_hero_media  # noqa: F401
    from website.models import HomepageHeroSlide
    from catalog_bridge import unified_views

    if getattr(unified_views, "_phase49_3b_media_installed", False):
        return
    original_serialize = unified_views.serialize_slide
    original_sync = unified_views.hero_slide_sync_view

    def serialize_slide(slide):
        payload = original_serialize(slide)
        for name in MEDIA_FIELDS:
            payload[name] = getattr(slide, name, None)
        return payload

    def hero_slide_sync_view(request, slide_id: int):
        response = original_sync(request, slide_id)
        if getattr(response, "status_code", 500) != 200:
            return response
        try:
            body = json.loads((request.body or b"{}").decode("utf-8"))
            data = body.get("slide") if isinstance(body, dict) and isinstance(body.get("slide"), dict) else {}
        except Exception:
            data = {}
        if not any(name in data for name in MEDIA_FIELDS):
            return response
        slide = HomepageHeroSlide.objects.filter(pk=slide_id).first()
        if slide is None:
            return response
        _apply(slide, data)
        return JsonResponse({"status": "ok", "slide": serialize_slide(slide), "revision": int(getattr(slide, "sync_revision", 1) or 1)})

    unified_views.serialize_slide = serialize_slide
    unified_views.hero_slide_sync_view = hero_slide_sync_view
    unified_views._phase49_3b_media_installed = True
