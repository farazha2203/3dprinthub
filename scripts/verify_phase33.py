#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def setup_django(root: Path) -> None:
    sys.path.insert(0, str(root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)
    print(f"FAIL {message}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--require-font", action="store_true")
    parser.add_argument("--require-migration", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    setup_django(root)

    from django.apps import apps
    from django.contrib.staticfiles import finders
    from django.db import connection
    from django.db.migrations.recorder import MigrationRecorder
    from django.urls import reverse

    from store.automation_watchdog import expire_stale_automation

    failures: list[str] = []
    CatalogSyncRun = apps.get_model("store", "CatalogSyncRun")
    ExternalSourceFetchLog = apps.get_model("store", "ExternalSourceFetchLog")

    expected_fields = {"deadline_at", "heartbeat_at", "cancelled_at"}
    for model in (CatalogSyncRun, ExternalSourceFetchLog):
        names = {field.name for field in model._meta.fields}
        missing = sorted(expected_fields - names)
        if missing:
            fail(f"missing_fields model={model._meta.label} fields={','.join(missing)}", failures)

    catalog_statuses = {value for value, _ in CatalogSyncRun._meta.get_field("status").choices}
    source_statuses = {value for value, _ in ExternalSourceFetchLog._meta.get_field("status").choices}
    if "cancelled" not in catalog_statuses:
        fail("catalog_cancelled_status_missing", failures)
    if "cancelled" not in source_statuses:
        fail("source_cancelled_status_missing", failures)

    url_names = [
        "admin:store_catalogautomationdashboard_stop_stale",
        "admin:store_catalogautomationdashboard_stop_source_log",
        "admin:store_catalogautomationdashboard_stop_catalog_run",
    ]
    for name in url_names:
        try:
            if name.endswith("stop_source_log") or name.endswith("stop_catalog_run"):
                reverse(name, args=[1])
            else:
                reverse(name)
        except Exception as exc:
            fail(f"admin_url name={name} error={type(exc).__name__}", failures)

    css_checks = {
        "admin/master-django.css": [
            'font-family:"IRANSans"',
            ".app-menu .navbar-nav .nav-link",
            "font-family:remixicon",
        ],
        "smartbase_admin_bridge/css/rtl.css": [
            '@font-face',
            '#main-navigation',
            'font-family:"IRANSans"',
        ],
    }
    for static_name, markers in css_checks.items():
        path = finders.find(static_name)
        if not path:
            fail(f"static_missing path={static_name}", failures)
            continue
        content = Path(path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in content:
                fail(f"static_marker_missing path={static_name} marker={marker}", failures)

    font_candidates = [
        "fonts/iransans/IRANSansWeb_FaNum.woff",
        "fonts/iransans/IRANSansWeb.woff",
    ]
    found_fonts = [name for name in font_candidates if finders.find(name)]
    print(f"IRANSANS_FONT_FOUND={bool(found_fonts)}")
    if found_fonts:
        print(f"IRANSANS_FONT_PATH={found_fonts[0]}")
    if args.require_font and not found_fonts:
        fail("iransans_font_source_missing", failures)

    migration_applied = MigrationRecorder(connection).migration_qs.filter(
        app="store",
        name="0023_phase33_automation_deadlines",
    ).exists()
    print(f"PHASE33_MIGRATION_APPLIED={migration_applied}")
    if args.require_migration and not migration_applied:
        fail("phase33_migration_not_applied", failures)

    watchdog = expire_stale_automation(dry_run=True)
    for key in sorted(watchdog):
        print(f"WATCHDOG_{key.upper()}={watchdog[key]}")

    print(f"DATABASE_VENDOR={connection.vendor}")
    print(f"PHASE33_VERIFY_FAILURE_COUNT={len(failures)}")
    if failures:
        print("PHASE33_RUNTIME_VERIFY=FAILED")
        return 1
    print("PHASE33_RUNTIME_VERIFY=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
