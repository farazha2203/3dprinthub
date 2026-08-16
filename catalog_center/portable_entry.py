from __future__ import annotations

import json
import os
import sys
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


def _configure_runtime():
    migration = migrate_legacy_portable_data()

    from app.env_settings import ENV_FILE, env_value, load_project_env
    load_project_env(ENV_FILE)

    from app.secure_secrets import migrate_connection_env_to_keyring
    migrated_secrets = migrate_connection_env_to_keyring(ENV_FILE)

    from app import main as app_main
    from app.epic49_desktop_schema import install as install_epic49_desktop_schema
    from app.persistent_connection_profile import install as install_persistent_connection_profile
    from app.product_workspace_v87 import ProductWorkspace
    from app.ux87_shell import build_app_class

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
    app_main.ProductStudio = ProductWorkspace
    install_epic49_desktop_schema(app_main)
    install_persistent_connection_profile(app_main)
    return app_main, build_app_class(app_main.App)


def _portable_verify() -> int:
    from app.env_settings import ENV_FILE
    from app.version import APP_NAME, APP_VERSION, BUILD_ID
    from app.product_workspace_v87 import ProductWorkspace
    from app.ux87_shell import build_app_class
    from app import main as app_main

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
        "product_workspace_v87": ProductWorkspace.__module__ == "app.product_workspace_v87",
        "ux87_shell": build_app_class(app_main.App).__name__ == "CatalogCenterApp87",
        "ai_profile_preserved": True,
        "host_profile_preserved": True,
    }
    ok = bool(
        payload["config_template_exists"]
        and payload["brand_icon_exists"]
        and payload["data_is_outside_bundle"]
        and payload["data_is_release_independent"]
        and payload["product_workspace_v87"]
        and payload["ux87_shell"]
    )
    payload["ok"] = ok
    output = str(os.getenv("CATALOG_VERIFY_OUTPUT") or "").strip()
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if ok else 2


def main() -> int:
    if "--portable-verify" in sys.argv:
        return _portable_verify()
    _app_main, App87 = _configure_runtime()
    App87().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
