from __future__ import annotations

from types import MethodType

from django.contrib import admin
from django.core.exceptions import ValidationError

from . import epic49_publish_options as publish
from .epic49_catalog_profile import (
    ProductCatalogProfile,
    SLIDER_EFFECT_CODES,
    _unique_public_slug,
)
from .models import Product


_ORIGINAL_SYNC = publish.sync_epic49_publish_options
_INSTALLED = False


def _int(value, default=0) -> int:
    try:
        return int(float(str(value if value not in (None, "") else default).replace(",", "").strip()))
    except Exception:
        return int(default)


def _bounded(value, default: int, minimum: int, maximum: int) -> int:
    return min(maximum, max(minimum, _int(value, default)))


def _actor(data: dict) -> str:
    return str(data.get("operator_name") or data.get("operator_id") or "desktop")[:120]


def _assert_revision(*, entity: str, current_revision: int, expected_revision: int, last_source: str) -> None:
    current_revision = max(0, int(current_revision or 0))
    expected_revision = max(0, int(expected_revision or 0))
    if expected_revision:
        if current_revision != expected_revision:
            raise ValidationError(
                f"EPIC49_SYNC_CONFLICT entity={entity} expected={expected_revision} current={current_revision}"
            )
        return
    # Legacy/no-revision desktop batches are still accepted unless a human Admin
    # has edited this record. In that case forcing a refresh is safer than a silent
    # overwrite of the manager's newer site-side changes.
    if current_revision > 1 and str(last_source or "") == "admin":
        raise ValidationError(
            f"EPIC49_SYNC_CONFLICT entity={entity} expected=refresh current={current_revision} source=admin"
        )


def _check_product_revision(product, data: dict) -> None:
    profile = ProductCatalogProfile.objects.filter(product=product).first()
    if profile is None:
        return
    _assert_revision(
        entity=f"product:{product.pk}",
        current_revision=profile.sync_revision,
        expected_revision=_int(data.get("server_product_revision"), 0),
        last_source=profile.last_modified_source,
    )


def _existing_slide(asset):
    from website.models import HomepageHeroSlide

    return HomepageHeroSlide.objects.filter(asset=asset).order_by("id").first()


def _check_slider_revision(asset, data: dict) -> None:
    slide = _existing_slide(asset)
    if slide is None:
        return
    _assert_revision(
        entity=f"hero:{slide.pk}",
        current_revision=getattr(slide, "sync_revision", 1),
        expected_revision=_int(data.get("server_slider_revision"), 0),
        last_source=getattr(slide, "last_modified_source", ""),
    )


def _selected_image(asset, requested: str):
    requested = str(requested or "").strip()
    if not requested:
        return None
    row = asset.images.filter(remote_url=requested).order_by("sort_order", "id").first()
    if row is not None:
        return row
    # A newer desktop may send the already-synced server media URL. Match it to
    # the imported image filename when possible instead of storing a loose URL.
    for candidate in asset.images.exclude(image="").order_by("sort_order", "id")[:80]:
        try:
            local_url = str(candidate.image.url or "").strip()
        except Exception:
            local_url = ""
        if local_url and (requested == local_url or requested.endswith(local_url)):
            return candidate
    return None


def apply_homepage_slider(product, asset, data: dict) -> dict:
    from website.models import HomepageHeroSlide

    enabled = bool(data.get("homepage_slider_enabled"))
    existing = HomepageHeroSlide.objects.filter(asset=asset).order_by("id")
    slide = existing.first()
    actor = _actor(data)

    if not enabled:
        if slide is not None:
            changed = bool(slide.is_active)
            slide.is_active = False
            slide.last_modified_source = "desktop"
            slide.last_modified_by = actor
            if changed:
                slide.sync_revision = max(1, int(getattr(slide, "sync_revision", 1) or 1)) + 1
            slide.save()
        existing.exclude(pk=getattr(slide, "pk", None)).update(is_active=False)
        return {
            "enabled": False,
            "slide_id": getattr(slide, "pk", None),
            "slider_revision": int(getattr(slide, "sync_revision", 0) or 0),
        }

    requested = str(data.get("homepage_slider_image_url") or "").strip()
    selected = _selected_image(asset, requested)
    image_url = ""
    if selected is not None and selected.image:
        image_url = publish._absolute_internal_media_url(selected.image.url)
    elif requested.startswith(("http://", "https://")):
        image_url = requested
    elif asset.preview_image:
        image_url = publish._absolute_internal_media_url(asset.preview_image.url)

    slider_seo = publish._homepage_slider_seo(data, product)
    effect = str(data.get("homepage_slider_transition_effect") or "cinematic_fade").strip()
    if effect not in SLIDER_EFFECT_CODES:
        effect = "cinematic_fade"

    defaults = {
        "selected_asset_image": selected,
        "image_url": image_url,
        "image_alt_text": slider_seo["image_alt_fa"],
        "title_override": slider_seo["title_fa"],
        "group_title": getattr(product.category, "name", "")[:160],
        "description": slider_seo["description_fa"],
        "button_text": slider_seo["button_text_fa"],
        "sort_order": max(0, publish._positive_int(data.get("homepage_slider_sort_order"), 100)),
        "transition_effect": effect,
        "transition_duration_ms": _bounded(data.get("homepage_slider_transition_duration_ms"), 1400, 300, 4000),
        "display_duration_ms": _bounded(data.get("homepage_slider_display_duration_ms"), 7000, 2000, 30000),
        "is_active": True,
        "last_modified_source": "desktop",
        "last_modified_by": actor,
    }

    if slide is None:
        defaults["sync_revision"] = 1
        slide = HomepageHeroSlide.objects.create(asset=asset, **defaults)
    else:
        for key, value in defaults.items():
            setattr(slide, key, value)
        slide.sync_revision = max(1, int(getattr(slide, "sync_revision", 1) or 1)) + 1
        slide.save()
    existing.exclude(pk=slide.pk).update(is_active=False)
    return {
        "enabled": True,
        "slide_id": slide.pk,
        "slider_revision": int(slide.sync_revision or 1),
        "image_url": image_url,
        "selected_image_id": getattr(selected, "pk", None),
        "title": slider_seo["title_fa"],
        "description": slider_seo["description_fa"],
        "image_alt": slider_seo["image_alt_fa"],
        "button_text": slider_seo["button_text_fa"],
        "focus_keyword": slider_seo["focus_keyword_fa"],
        "transition_effect": effect,
        "transition_duration_ms": slide.transition_duration_ms,
        "display_duration_ms": slide.display_duration_ms,
    }


def sync_epic49_publish_options(asset) -> dict:
    if not getattr(asset, "product_id", None):
        return {}
    data = publish._desktop_data(asset)
    if not data:
        return {}

    product = asset.product
    _check_product_revision(product, data)
    _check_slider_revision(asset, data)

    result = _ORIGINAL_SYNC(asset)
    profile = ProductCatalogProfile.objects.filter(product=product).first()
    actor = _actor(data)
    if profile is not None:
        # sync_catalog_profile already increments exactly once; this update only
        # records who initiated the desktop operation.
        ProductCatalogProfile.objects.filter(pk=profile.pk).update(
            last_modified_source="desktop",
            last_modified_by=actor,
        )
        profile.refresh_from_db()
        result["product_revision"] = int(profile.sync_revision or 1)
    else:
        result["product_revision"] = 0

    slide = _existing_slide(asset)
    result["slider_id"] = getattr(slide, "pk", None)
    result["slider_revision"] = int(getattr(slide, "sync_revision", 0) or 0)
    result["server_product_id"] = product.pk
    return result


def _admin_actor(request) -> str:
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return ""
    return str(
        getattr(user, "username", "")
        or getattr(user, "email", "")
        or getattr(user, "pk", "")
        or ""
    )[:120]


def _ensure_profile_for_admin(product: Product) -> ProductCatalogProfile:
    profile = ProductCatalogProfile.objects.filter(product=product).first()
    if profile is not None:
        return profile
    return ProductCatalogProfile.objects.create(
        product=product,
        public_slug=_unique_public_slug(product, getattr(product, "title_en", "")),
        legacy_slug=str(getattr(product, "slug", "") or ""),
        sync_revision=1,
        last_modified_source="admin",
    )


def _install_product_admin_revision() -> None:
    model_admin = admin.site._registry.get(Product)
    if model_admin is None or getattr(model_admin, "_phase49_unified_revision_installed", False):
        return
    original_save_model = model_admin.save_model

    def save_model(this, request, obj, form, change):
        result = original_save_model(request, obj, form, change)
        profile = _ensure_profile_for_admin(obj)
        if change:
            profile.sync_revision = max(1, int(profile.sync_revision or 1)) + 1
        else:
            profile.sync_revision = max(1, int(profile.sync_revision or 1))
        profile.last_modified_source = "admin"
        profile.last_modified_by = _admin_actor(request)
        profile.save(update_fields=[
            "sync_revision",
            "last_modified_source",
            "last_modified_by",
            "updated_at",
        ])
        return result

    model_admin.save_model = MethodType(save_model, model_admin)
    model_admin._phase49_unified_revision_installed = True


def install() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    publish.apply_homepage_slider = apply_homepage_slider
    publish.sync_epic49_publish_options = sync_epic49_publish_options

    # epic49_publish_signals imported the callable into its module namespace.
    # Rebind it too so post_save uses the same optimistic-concurrency contract.
    try:
        from . import epic49_publish_signals

        epic49_publish_signals.sync_epic49_publish_options = sync_epic49_publish_options
    except Exception:
        pass

    _install_product_admin_revision()
    _INSTALLED = True
