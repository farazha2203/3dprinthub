from __future__ import annotations

import logging
from typing import Any

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models

from django_smartbase_admin.admin.admin_base import (
    SBAdmin,
    SBAdminStackedInline,
    SBAdminTableInline,
)
from django_smartbase_admin.admin.site import sb_admin_site
from django_smartbase_admin.engine.field import SBAdminField

from .utils import (
    concrete_field_names,
    editable_field_names,
    safe_fieldsets,
    safe_list_display,
    safe_list_filters,
    safe_ordering,
    safe_search_fields,
)


logger = logging.getLogger(__name__)

SKIP_APP_LABELS = {
    "django_smartbase_admin",
    "sb_admin_audit",
    "sb_admin_messaging",
    "smartbase_admin_bridge",
}


def _safe_readonly_fields(
    model: type[models.Model],
    legacy_admin: admin.ModelAdmin,
) -> tuple[str, ...]:
    concrete = concrete_field_names(model)
    return tuple(
        name
        for name in getattr(legacy_admin, "readonly_fields", ()) or ()
        if isinstance(name, str) and name in concrete
    )


def _convert_inline(
    inline_class: type[admin.options.InlineModelAdmin],
    parent_model: type[models.Model],
    index: int,
):
    inline_model = getattr(inline_class, "model", None)
    if inline_model is None:
        return None

    base = (
        SBAdminStackedInline
        if issubclass(inline_class, admin.StackedInline)
        else SBAdminTableInline
    )

    attrs: dict[str, Any] = {
        "__module__": __name__,
        "model": inline_model,
        "extra": getattr(inline_class, "extra", 0),
        "can_delete": getattr(inline_class, "can_delete", True),
        "show_change_link": getattr(inline_class, "show_change_link", True),
    }

    for name in (
        "fk_name",
        "max_num",
        "min_num",
        "verbose_name",
        "verbose_name_plural",
        "classes",
        "autocomplete_fields",
        "raw_id_fields",
        "filter_horizontal",
        "filter_vertical",
    ):
        value = getattr(inline_class, name, None)
        if value not in (None, (), [], ""):
            attrs[name] = value

    concrete = concrete_field_names(inline_model)
    readonly = tuple(
        item
        for item in getattr(inline_class, "readonly_fields", ()) or ()
        if isinstance(item, str) and item in concrete
    )
    if readonly:
        attrs["readonly_fields"] = readonly

    declared_fields = getattr(inline_class, "fields", None)
    if declared_fields:
        safe_fields = tuple(
            item
            for item in declared_fields
            if isinstance(item, str) and item in concrete
        )
        if safe_fields:
            attrs["fields"] = safe_fields

    name = (
        f"{parent_model.__name__}{inline_model.__name__}"
        f"SmartBaseInline{index}"
    )
    return type(name, (base,), attrs)


def _build_admin_class(
    model: type[models.Model],
    legacy_admin: admin.ModelAdmin,
) -> type[SBAdmin]:
    readonly_fields = _safe_readonly_fields(model, legacy_admin)
    fieldsets = safe_fieldsets(model, legacy_admin)

    # Never expose the encoded password hash as a normal editable field.
    if model is get_user_model():
        cleaned_fieldsets = []
        for title, options in fieldsets:
            fields = tuple(
                name
                for name in options.get("fields", ())
                if name != "password"
            )
            cleaned_fieldsets.append((title, {**options, "fields": fields}))
        fieldsets = tuple(cleaned_fieldsets)

    ordering = safe_ordering(model, legacy_admin)
    list_display: list[Any] = list(safe_list_display(model, legacy_admin))
    visible_names = {item for item in list_display if isinstance(item, str)}
    for ordering_item in ordering:
        ordering_name = ordering_item.lstrip("-").split("__", 1)[0]
        if ordering_name in visible_names:
            continue
        try:
            model_field = model._meta.get_field(ordering_name)
            title = str(model_field.verbose_name)
        except Exception:
            title = ordering_name.replace("_", " ").title()
        list_display.append(
            SBAdminField(
                name=ordering_name,
                title=title,
                list_visible=False,
                filter_disabled=True,
            )
        )
        visible_names.add(ordering_name)

    converted_inlines = []
    for index, inline in enumerate(getattr(legacy_admin, "inlines", ()) or ()):
        try:
            converted = _convert_inline(inline, model, index)
        except Exception:
            logger.exception(
                "Could not convert inline %r for %s",
                inline,
                model._meta.label,
            )
            converted = None
        if converted is not None:
            converted_inlines.append(converted)

    attrs: dict[str, Any] = {
        "__module__": __name__,
        "model": model,
        "menu_label": str(model._meta.verbose_name_plural),
        "sbadmin_list_display": tuple(list_display),
        "sbadmin_list_filter": safe_list_filters(model, legacy_admin),
        "search_fields": safe_search_fields(model, legacy_admin),
        "ordering": ordering,
        "sbadmin_fieldsets": fieldsets,
        "readonly_fields": readonly_fields,
        "list_per_page": min(
            int(getattr(legacy_admin, "list_per_page", 50) or 50),
            200,
        ),
        "inlines": converted_inlines,
    }

    for name in (
        "date_hierarchy",
        "list_select_related",
        "save_as",
        "save_on_top",
        "view_on_site",
        "autocomplete_fields",
        "raw_id_fields",
        "filter_horizontal",
        "filter_vertical",
        "prepopulated_fields",
        "exclude",
    ):
        value = getattr(legacy_admin, name, None)
        if value not in (None, (), [], {}, "", False):
            attrs[name] = value

    class_name = f"{model.__name__}SmartBaseAdmin"
    return type(class_name, (SBAdmin,), attrs)


def register_legacy_admin_models() -> int:
    registered = 0
    for model, legacy_admin in list(admin.site._registry.items()):
        if model._meta.app_label in SKIP_APP_LABELS:
            continue
        if sb_admin_site.is_registered(model):
            continue

        try:
            admin_class = _build_admin_class(model, legacy_admin)
            sb_admin_site.register(model, admin_class)
            registered += 1
        except Exception:
            logger.exception(
                "Failed to register %s in SmartBase Admin",
                model._meta.label,
            )

    return registered


REGISTERED_MODEL_COUNT = register_legacy_admin_models()
