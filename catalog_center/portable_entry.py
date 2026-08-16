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
    runtime_summary,
)


def _configure_main_runtime():
    from app.env_settings import env_value
    from app import main as app_main
    from app.epic49_product_studio import ProductStudio as Epic49ProductStudio

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
    app_main.ProductStudio = Epic49ProductStudio
    return app_main


def _portable_verify() -> int:
    from app.env_settings import ENV_FILE
    from app.version import APP_NAME, APP_VERSION, BUILD_ID
    from app.epic49_product_studio import ProductStudio as Epic49ProductStudio

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
        "product_studio_epic49": Epic49ProductStudio.__module__ == "app.epic49_product_studio",
    }
    ok = bool(
        payload["config_template_exists"]
        and payload["brand_icon_exists"]
        and payload["data_is_outside_bundle"]
        and payload["product_studio_epic49"]
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
    app_main = _configure_main_runtime()
    app_main.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
