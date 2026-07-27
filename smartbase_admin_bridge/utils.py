from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from django.apps import apps
from django.contrib import admin
from django.db import models


ORDER_TOKENS = (
    "order",
    "quote",
    "invoice",
    "job",
    "project",
    "سفارش",
    "پیش فاکتور",
    "پیش‌فاکتور",
    "فاکتور",
    "پروژه",
)

STATUS_FIELD_CANDIDATES = (
    "status",
    "order_status",
    "state",
    "workflow_status",
)

DATE_FIELD_CANDIDATES = (
    "created_at",
    "created",
    "submitted_at",
    "date_created",
    "created_on",
    "updated_at",
)

APP_LABELS_FA = {
    "store": "فروشگاه، سفارش‌ها و کاتالوگ",
    "website": "وب‌سایت و محتوا",
    "auth": "کاربران و دسترسی‌ها",
    "sb_admin_audit": "گزارش فعالیت‌ها",
    "sb_admin_messaging": "پیام‌ها و اعلان‌ها",
    "filer": "مدیریت فایل‌ها",
    "smartbase_admin_bridge": "میز کار مدیریت",
}

APP_ICONS = {
    "store": "Ad-product",
    "website": "Application",
    "auth": "Id-card-h",
    "sb_admin_audit": "History",
    "sb_admin_messaging": "Accept-email",
    "filer": "Folder",
    "smartbase_admin_bridge": "All-application",
}


def model_haystack(model: type[models.Model]) -> str:
    return " ".join(
        (
            model.__name__,
            model._meta.model_name,
            str(model._meta.verbose_name),
            str(model._meta.verbose_name_plural),
        )
    ).lower()


def is_order_model(model: type[models.Model]) -> bool:
    haystack = model_haystack(model)
    return any(token.lower() in haystack for token in ORDER_TOKENS)


def get_order_models() -> list[type[models.Model]]:
    result: list[type[models.Model]] = []
    for model in apps.get_models():
        if model._meta.abstract or model._meta.proxy:
            continue
        if model._meta.app_label in {
            "admin",
            "contenttypes",
            "sessions",
            "django_smartbase_admin",
            "sb_admin_audit",
            "sb_admin_messaging",
        }:
            continue
        if is_order_model(model):
            result.append(model)
    return result


def concrete_field_names(model: type[models.Model]) -> set[str]:
    return {
        field.name
        for field in model._meta.get_fields()
        if getattr(field, "concrete", False)
    }


def editable_field_names(model: type[models.Model]) -> list[str]:
    result: list[str] = []
    for field in model._meta.get_fields():
        if getattr(field, "auto_created", False):
            continue
        if not getattr(field, "editable", False):
            continue
        if field.name == "password" and model._meta.app_label == "auth":
            continue
        if not getattr(field, "concrete", False) and not getattr(
            field, "many_to_many", False
        ):
            continue
        result.append(field.name)
    return result


def safe_list_display(
    model: type[models.Model],
    legacy_admin: admin.ModelAdmin | None = None,
    *,
    max_fields: int = 8,
) -> tuple[str, ...]:
    field_map = {
        field.name: field
        for field in model._meta.get_fields()
        if getattr(field, "concrete", False)
    }
    selected: list[str] = []

    if legacy_admin is not None:
        for item in getattr(legacy_admin, "list_display", ()) or ():
            if not isinstance(item, str):
                continue
            if item in field_map and item not in selected:
                selected.append(item)

    preferred = (
        model._meta.pk.name,
        "status",
        "order_status",
        "title",
        "name",
        "email",
        "customer",
        "user",
        "created_at",
        "updated_at",
        "is_active",
    )
    for name in preferred:
        if name in field_map and name not in selected:
            selected.append(name)

    if len(selected) < max_fields:
        for name, field in field_map.items():
            if name in selected:
                continue
            if isinstance(
                field,
                (
                    models.BinaryField,
                    models.JSONField,
                    models.TextField,
                ),
            ):
                continue
            selected.append(name)
            if len(selected) >= max_fields:
                break

    if not selected:
        selected.append(model._meta.pk.name)

    return tuple(selected[:max_fields])


def safe_search_fields(
    model: type[models.Model],
    legacy_admin: admin.ModelAdmin | None = None,
) -> tuple[str, ...]:
    valid_root_fields = concrete_field_names(model)
    selected: list[str] = []

    if legacy_admin is not None:
        for item in getattr(legacy_admin, "search_fields", ()) or ():
            if not isinstance(item, str):
                continue
            raw = item.lstrip("^=@")
            root = raw.split("__", 1)[0]
            if root in valid_root_fields and item not in selected:
                selected.append(item)

    if selected:
        return tuple(selected)

    for field in model._meta.get_fields():
        if not getattr(field, "concrete", False):
            continue
        if isinstance(
            field,
            (
                models.CharField,
                models.TextField,
                models.EmailField,
                models.SlugField,
            ),
        ):
            selected.append(field.name)
        if len(selected) >= 6:
            break
    return tuple(selected)


def safe_list_filters(
    model: type[models.Model],
    legacy_admin: admin.ModelAdmin | None = None,
) -> tuple[str, ...]:
    valid = concrete_field_names(model)
    selected: list[str] = []

    if legacy_admin is not None:
        for item in getattr(legacy_admin, "list_filter", ()) or ():
            if isinstance(item, str) and item.split("__", 1)[0] in valid:
                if item not in selected:
                    selected.append(item)

    for field in model._meta.get_fields():
        if not getattr(field, "concrete", False):
            continue
        if field.name in selected:
            continue
        if getattr(field, "choices", None) or isinstance(
            field,
            (
                models.BooleanField,
                models.DateField,
                models.DateTimeField,
                models.ForeignKey,
            ),
        ):
            selected.append(field.name)
        if len(selected) >= 6:
            break

    return tuple(selected[:6])


def safe_ordering(
    model: type[models.Model],
    legacy_admin: admin.ModelAdmin | None = None,
) -> tuple[str, ...]:
    valid = concrete_field_names(model)
    if legacy_admin is not None:
        ordering = getattr(legacy_admin, "ordering", None)
        if ordering:
            safe = [
                item
                for item in ordering
                if isinstance(item, str)
                and item.lstrip("-").split("__", 1)[0] in valid
            ]
            if safe:
                return tuple(safe)

    for name in DATE_FIELD_CANDIDATES:
        if name in valid:
            return (f"-{name}",)
    return (f"-{model._meta.pk.name}",)


def safe_fieldsets(
    model: type[models.Model],
    legacy_admin: admin.ModelAdmin | None = None,
) -> tuple[tuple[str | None, dict[str, Any]], ...]:
    editable = editable_field_names(model)
    if not editable:
        editable = [model._meta.pk.name]
    return ((None, {"fields": tuple(editable)}),)


def get_status_field_name(model: type[models.Model]) -> str | None:
    fields = concrete_field_names(model)
    return next((name for name in STATUS_FIELD_CANDIDATES if name in fields), None)


def get_date_field_name(model: type[models.Model]) -> str | None:
    fields = concrete_field_names(model)
    return next((name for name in DATE_FIELD_CANDIDATES if name in fields), None)


def app_group_label(app_label: str, fallback: str) -> str:
    return APP_LABELS_FA.get(app_label, fallback)


def app_group_icon(app_label: str) -> str:
    return APP_ICONS.get(app_label, "Folder")
