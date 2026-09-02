from __future__ import annotations

import os
from pathlib import Path

from django.conf import settings
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

from store.models import PrintQuality
from website.models import Material

from .views import _configured_token, _pending_root


REQUIRED_MIGRATIONS = (
    ("store", "0036_phase50_checkout_snapshot"),
    ("store", "0037_phase50_professional_commerce_policy"),
    ("store", "0038_phase50_profile_matrix"),
    ("store", "0039_phase50_filament_offer_pricing"),
    ("store", "0040_phase50_filament_offer_operations"),
    ("store", "0041_phase50_filament_visual_identity"),
    ("website", "0024_phase49_3i51_material_catalog_description"),
    ("store", "0042_phase49_3i51_filament_registry_descriptions"),
)

REQUIRED_SCHEMA = {
    "store_materialcoloroption": {
        "brand_name",
        "sale_price_per_roll",
        "print_hourly_rate",
        "color_finish",
        "description",
    },
    "store_productvariant": {
        "sales_profile_description",
        "part_length_cm",
        "support_weight_grams",
    },
    "website_material": {"catalog_description"},
    "store_filamentbrand": {"id", "name", "description", "is_active"},
}


def _storage_ready(path: Path) -> dict:
    path = Path(path)
    if path.is_dir():
        return {
            "exists": True,
            "readable": os.access(path, os.R_OK | os.X_OK),
            "writable": os.access(path, os.W_OK | os.X_OK),
            "parent_ready": True,
        }
    parent = path.parent
    return {
        "exists": False,
        "readable": False,
        "writable": False,
        "parent_ready": bool(
            parent.is_dir()
            and os.access(parent, os.R_OK | os.W_OK | os.X_OK)
        ),
    }


def _schema_state() -> tuple[dict, list[str]]:
    state = {}
    blockers: list[str] = []
    with connection.cursor() as cursor:
        table_names = set(connection.introspection.table_names(cursor))
        for table, required_columns in REQUIRED_SCHEMA.items():
            if table not in table_names:
                state[table] = {
                    "exists": False,
                    "missing_columns": sorted(required_columns),
                }
                blockers.append(f"schema:{table}:missing")
                continue
            description = connection.introspection.get_table_description(
                cursor,
                table,
            )
            columns = {str(column.name) for column in description}
            missing = sorted(required_columns - columns)
            state[table] = {
                "exists": True,
                "missing_columns": missing,
            }
            for column in missing:
                blockers.append(f"schema:{table}.{column}:missing")
    return state, blockers


def publish_readiness() -> dict:
    blockers: list[str] = []

    token_ready = len(_configured_token()) >= 24
    if not token_ready:
        blockers.append("bridge_token:not_configured")

    pending = _storage_ready(_pending_root())
    if not (pending["exists"] and pending["readable"]):
        if not pending["parent_ready"]:
            blockers.append("pending_root:not_accessible")

    media_root = Path(getattr(settings, "MEDIA_ROOT", "") or "")
    media = _storage_ready(media_root) if str(media_root) not in {"", "."} else {
        "exists": False,
        "readable": False,
        "writable": False,
        "parent_ready": False,
    }
    if not (
        (media["exists"] and media["readable"] and media["writable"])
        or media["parent_ready"]
    ):
        blockers.append("media_root:not_writable")

    applied = set(
        MigrationRecorder.Migration.objects.filter(
            app__in={app for app, _name in REQUIRED_MIGRATIONS}
        ).values_list("app", "name")
    )
    migration_state = []
    for app, name in REQUIRED_MIGRATIONS:
        ok = (app, name) in applied
        migration_state.append({
            "app": app,
            "name": name,
            "applied": ok,
        })
        if not ok:
            blockers.append(f"migration:{app}.{name}:missing")

    try:
        schema_state, schema_blockers = _schema_state()
    except Exception as exc:
        schema_state = {}
        schema_blockers = [f"schema_introspection:{type(exc).__name__}"]
    blockers.extend(schema_blockers)

    prerequisites = {
        "active_materials": 0,
        "active_print_qualities": 0,
    }
    try:
        prerequisites["active_materials"] = Material.objects.filter(
            is_active=True
        ).count()
    except Exception as exc:
        blockers.append(f"active_materials:{type(exc).__name__}")
    try:
        prerequisites["active_print_qualities"] = PrintQuality.objects.filter(
            is_active=True
        ).count()
    except Exception as exc:
        blockers.append(f"active_print_qualities:{type(exc).__name__}")

    if prerequisites["active_materials"] <= 0:
        blockers.append("active_materials:none")
    if prerequisites["active_print_qualities"] <= 0:
        blockers.append("active_print_qualities:none")

    blockers = list(dict.fromkeys(blockers))
    return {
        "status": "ready" if not blockers else "blocked",
        "ready": not blockers,
        "contract": "epic49-site-publish-readiness-v1",
        "database_vendor": str(connection.vendor or ""),
        "bridge_token_ready": token_ready,
        "pending_storage": pending,
        "media_storage": media,
        "migrations": migration_state,
        "schema": schema_state,
        "prerequisites": prerequisites,
        "blockers": blockers,
    }


from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def publish_readiness_view(request):
    from .views import _authorized, _unauthorized
    if not _authorized(request):
        return _unauthorized()
    return JsonResponse(publish_readiness())
