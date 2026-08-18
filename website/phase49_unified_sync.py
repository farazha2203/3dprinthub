from __future__ import annotations

from types import MethodType

from django.contrib import admin
from django.db import models

from .models import HomepageHeroSlide


def _has_field(name: str) -> bool:
    try:
        HomepageHeroSlide._meta.get_field(name)
        return True
    except Exception:
        return False


def install_model_contract() -> None:
    if not _has_field("sync_revision"):
        models.PositiveBigIntegerField(
            default=1,
            db_index=True,
            verbose_name="نسخه همگام‌سازی",
        ).contribute_to_class(HomepageHeroSlide, "sync_revision")
    if not _has_field("last_modified_source"):
        models.CharField(
            max_length=20,
            default="desktop",
            db_index=True,
            verbose_name="منبع آخرین تغییر",
        ).contribute_to_class(HomepageHeroSlide, "last_modified_source")
    if not _has_field("last_modified_by"):
        models.CharField(
            max_length=120,
            blank=True,
            verbose_name="عامل آخرین تغییر",
        ).contribute_to_class(HomepageHeroSlide, "last_modified_by")


def _actor(request) -> str:
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return ""
    return str(
        getattr(user, "username", "")
        or getattr(user, "email", "")
        or getattr(user, "pk", "")
        or ""
    )[:120]


def _mirror_hero_to_profile(slide: HomepageHeroSlide, actor: str) -> None:
    asset = getattr(slide, "asset", None)
    product = getattr(asset, "product", None) if asset is not None else None
    if product is None:
        return
    from store.epic49_catalog_profile import ProductCatalogProfile, _unique_public_slug

    profile = ProductCatalogProfile.objects.filter(product=product).first()
    if profile is None:
        profile = ProductCatalogProfile.objects.create(
            product=product,
            public_slug=_unique_public_slug(product, getattr(product, "title_en", "")),
            legacy_slug=str(getattr(product, "slug", "") or ""),
            sync_revision=1,
            last_modified_source="admin",
            last_modified_by=actor,
        )
    else:
        profile.sync_revision = max(1, int(profile.sync_revision or 1)) + 1

    selected = getattr(slide, "selected_asset_image", None)
    selected_url = ""
    if selected is not None:
        selected_url = str(getattr(selected, "remote_url", "") or "").strip()
        if not selected_url:
            try:
                selected_url = str(selected.image.url or "").strip()
            except Exception:
                selected_url = ""

    profile.homepage_slider_enabled = bool(slide.is_active)
    profile.homepage_slider_image_url = selected_url or str(slide.image_url or "")[:2000]
    profile.homepage_slider_sort_order = max(0, int(slide.sort_order or 0))
    profile.homepage_slider_title_fa = str(slide.title_override or "")[:220]
    profile.homepage_slider_description_fa = str(slide.description or "")
    profile.homepage_slider_alt_text = str(slide.image_alt_text or "")[:240]
    profile.homepage_slider_button_text = str(slide.button_text or "مشاهده محصول")[:80]
    profile.homepage_slider_transition_effect = str(slide.transition_effect or "cinematic_fade")[:32]
    profile.homepage_slider_transition_duration_ms = int(slide.transition_duration_ms or 1400)
    profile.homepage_slider_display_duration_ms = int(slide.display_duration_ms or 7000)
    profile.last_modified_source = "admin"
    profile.last_modified_by = actor
    profile.save()


def install_admin_contract() -> None:
    model_admin = admin.site._registry.get(HomepageHeroSlide)
    if model_admin is None or getattr(model_admin, "_phase49_unified_sync_installed", False):
        return

    original_save_model = model_admin.save_model
    original_readonly = tuple(getattr(model_admin, "readonly_fields", ()) or ())
    original_fieldsets = tuple(getattr(model_admin, "fieldsets", ()) or ())

    audit_fields = ("sync_revision", "last_modified_source", "last_modified_by")
    model_admin.readonly_fields = tuple(dict.fromkeys([*original_readonly, *audit_fields]))

    if original_fieldsets:
        patched = []
        audit_injected = False
        for title, options in original_fieldsets:
            copied = dict(options)
            fields = tuple(copied.get("fields") or ())
            if str(title).strip().startswith("۵."):
                copied["fields"] = tuple(dict.fromkeys([*fields, *audit_fields]))
                audit_injected = True
            patched.append((title, copied))
        if not audit_injected:
            patched.append(("همگام‌سازی Desktop / Server", {"fields": audit_fields}))
        model_admin.fieldsets = tuple(patched)

    def save_model(this, request, obj, form, change):
        obj.sync_revision = max(1, int(getattr(obj, "sync_revision", 1) or 1)) + (1 if change else 0)
        obj.last_modified_source = "admin"
        actor = _actor(request)
        obj.last_modified_by = actor
        result = original_save_model(request, obj, form, change)
        _mirror_hero_to_profile(obj, actor)
        return result

    model_admin.save_model = MethodType(save_model, model_admin)
    model_admin._phase49_unified_sync_installed = True


def install() -> None:
    install_model_contract()
    install_admin_contract()


install()
