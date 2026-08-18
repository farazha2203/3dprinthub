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
        # Admin is an authoritative editor. Every human save creates a new
        # optimistic-concurrency revision so a stale Windows client receives 409
        # instead of silently overwriting a newer site edit.
        obj.sync_revision = max(1, int(getattr(obj, "sync_revision", 1) or 1)) + (1 if change else 0)
        obj.last_modified_source = "admin"
        user = getattr(request, "user", None)
        actor = ""
        if user is not None and getattr(user, "is_authenticated", False):
            actor = str(getattr(user, "username", "") or getattr(user, "email", "") or getattr(user, "pk", ""))
        obj.last_modified_by = actor[:120]
        return original_save_model(request, obj, form, change)

    model_admin.save_model = MethodType(save_model, model_admin)
    model_admin._phase49_unified_sync_installed = True


def install() -> None:
    install_model_contract()
    install_admin_contract()


install()
