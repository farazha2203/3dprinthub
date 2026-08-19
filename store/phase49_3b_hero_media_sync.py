from __future__ import annotations


def _bounded(value, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(float(str(value if value is not None else default).replace(",", "")))
    except Exception:
        parsed = default
    return min(maximum, max(minimum, parsed))


def install() -> None:
    from store import epic49_publish_options as publish_options

    if getattr(publish_options, "_phase49_3b_hero_media_installed", False):
        return
    original = publish_options.apply_homepage_slider

    def apply_homepage_slider(product, asset, data: dict) -> dict:
        result = original(product, asset, data)
        if not result.get("enabled") or not result.get("slide_id"):
            return result

        from website.models import HomepageHeroSlide

        slide = HomepageHeroSlide.objects.filter(pk=result["slide_id"]).first()
        if slide is None:
            return result

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
        color = str(data.get("homepage_slider_background_color") or "#071827").strip()[:24] or "#071827"

        values = {
            "presentation_mode": presentation,
            "object_fit": fit,
            "focal_position": focal,
            "image_scale_percent": _bounded(data.get("homepage_slider_image_scale_percent"), 100, 60, 140),
            "image_position_x_percent": _bounded(data.get("homepage_slider_position_x_percent"), 50, 0, 100),
            "image_position_y_percent": _bounded(data.get("homepage_slider_position_y_percent"), 50, 0, 100),
            "background_mode": background,
            "background_color": color,
            "background_blur_px": _bounded(data.get("homepage_slider_background_blur_px"), 18, 0, 60),
            "desktop_max_width_percent": _bounded(data.get("homepage_slider_desktop_max_width_percent"), 78, 30, 100),
            "desktop_max_height_percent": _bounded(data.get("homepage_slider_desktop_max_height_percent"), 88, 30, 100),
            "mobile_max_width_percent": _bounded(data.get("homepage_slider_mobile_max_width_percent"), 92, 30, 100),
            "mobile_max_height_percent": _bounded(data.get("homepage_slider_mobile_max_height_percent"), 72, 30, 100),
        }
        HomepageHeroSlide.objects.filter(pk=slide.pk).update(**values)
        for key, value in values.items():
            setattr(slide, key, value)
        result["media_presentation"] = values
        return result

    publish_options.apply_homepage_slider = apply_homepage_slider
    publish_options._phase49_3b_hero_media_installed = True
