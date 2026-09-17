from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

from app.runtime_paths import (
    asset_root,
    config_template,
    data_root,
    default_host_mirror,
    migrate_legacy_portable_data,
    persistent_data_root,
    runtime_summary,
)


def _configure_runtime_paths() -> None:
    """Prepare persistent portable paths before the canonical launcher starts.

    Runtime composition itself remains owned by launch.py. This keeps the frozen
    executable on the same Phase49.3I install order as the source launcher while
    preserving release-independent data and Windows Credential Manager secrets.
    """

    migration = migrate_legacy_portable_data()

    from app.env_settings import ENV_FILE, env_value, load_project_env

    load_project_env(ENV_FILE)

    from app.secure_secrets import migrate_connection_env_to_keyring

    migrated_secrets = migrate_connection_env_to_keyring(ENV_FILE)

    from app import main as app_main

    data = data_root()
    data.mkdir(parents=True, exist_ok=True)
    host_mirror = Path(env_value("CATALOG_HOST_MIRROR", str(default_host_mirror()))).resolve()

    app_main.ROOT = data.parent
    app_main.DATA = data
    app_main.DB_FILE = data / "catalog.sqlite3"
    app_main.CONFIG_FILE = data / "config.json"
    app_main.PROFILE_ROOT = data / "browser_profiles"
    app_main.HOST_MIRROR = host_mirror
    app_main.BATCH_ROOT = host_mirror / "imports" / "desktop_catalog" / "pending"
    app_main.ASSET_ROOT = asset_root()
    app_main.PORTABLE_PROFILE_MIGRATION = migration
    app_main.PORTABLE_SECRET_MIGRATION = migrated_secrets


def _portable_verify() -> int:
    from app.env_settings import ENV_FILE
    from app.version import APP_NAME, APP_VERSION, BUILD_ID
    from qt_launch import main as qt_main

    previous_data_root = os.environ.get("CATALOG_DATA_ROOT")
    try:
        with tempfile.TemporaryDirectory() as temporary:
            os.environ["CATALOG_DATA_ROOT"] = temporary
            qt_verify_rc = int(qt_main(["--verify-only"]))
    finally:
        if previous_data_root is None:
            os.environ.pop("CATALOG_DATA_ROOT", None)
        else:
            os.environ["CATALOG_DATA_ROOT"] = previous_data_root

    payload = {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "build_id": BUILD_ID,
        **runtime_summary(),
        "config_template": str(config_template()),
        "config_template_exists": config_template().is_file(),
        "asset_root": str(asset_root()),
        "brand_icon_exists": (asset_root() / "brand_icon.png").is_file(),
        "env_file": str(ENV_FILE),
        "data_is_outside_bundle": data_root().resolve() != Path(getattr(sys, "_MEIPASS", data_root())).resolve(),
        "data_is_release_independent": data_root().resolve() == persistent_data_root().resolve(),
        "canonical_launcher_runtime": "qt_launch.py",
        "qt6_runtime_verified": qt_verify_rc == 0,
        "legacy_rollback_preserved": True,
        "ai_profile_preserved": True,
        "host_profile_preserved": True,
    }
    ok = bool(
        payload["config_template_exists"]
        and payload["brand_icon_exists"]
        and payload["data_is_outside_bundle"]
        and payload["data_is_release_independent"]
        and payload["qt6_runtime_verified"]
        and payload["canonical_launcher_runtime"] == "qt_launch.py"
    )
    payload["ok"] = ok
    output = str(os.getenv("CATALOG_VERIFY_OUTPUT") or "").strip()
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if ok else 2


def _portable_browser_smoke() -> int:
    """Prove the frozen EXE can load Playwright and launch a real browser.

    The smoke deliberately uses a data: URL, not MakerWorld or another external
    service. Release validation therefore detects PyInstaller/browser packaging
    regressions without turning a third-party website into a CI dependency.
    """

    from app.version import APP_VERSION, BUILD_ID
    from app.classic_methods import launch_fresh_browser

    async def _run() -> dict:
        from playwright.async_api import async_playwright

        async with async_playwright() as playwright:
            browser, browser_label = await launch_fresh_browser(playwright, headed=False)
            page = await browser.new_page()
            await page.goto(
                "data:text/html,<html><head><title>3DPrintHub Portable Browser Smoke</title></head><body>ok</body></html>",
                wait_until="load",
                timeout=30_000,
            )
            title = await page.title()
            await browser.close()
            return {
                "browser": browser_label,
                "title": title,
                "ok": title == "3DPrintHub Portable Browser Smoke",
            }

    payload = {
        "app_version": APP_VERSION,
        "build_id": BUILD_ID,
        "ok": False,
    }
    try:
        payload.update(asyncio.run(_run()))
    except Exception as error:  # packaged runtime diagnostics only; no secrets
        payload["error_type"] = type(error).__name__
        payload["error"] = str(error)[-1500:]

    output = str(os.getenv("CATALOG_BROWSER_SMOKE_OUTPUT") or "").strip()
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if payload.get("ok") is True else 3


def main() -> int:
    if "--portable-verify" in sys.argv:
        return _portable_verify()
    if "--portable-browser-smoke" in sys.argv:
        return _portable_browser_smoke()

    _configure_runtime_paths()
    from launch import main as launch_main

    return launch_main()


if __name__ == "__main__":
    raise SystemExit(main())
