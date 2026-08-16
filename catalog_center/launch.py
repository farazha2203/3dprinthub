from __future__ import annotations

import os
import sys
from pathlib import Path


EXPECTED_VERSION = "8.6.0"
ROOT = Path(__file__).resolve().parent


def main() -> int:
    # The absolute launcher location must win over the caller's current folder.
    root_text = str(ROOT)
    sys.path[:] = [root_text, *[item for item in sys.path if item != root_text]]

    from app.env_settings import ENV_FILE, load_project_env
    load_project_env(ENV_FILE)

    from app.version import APP_VERSION, BUILD_ID, SOURCE_ROOT
    from app.epic49_product_studio_final import ProductStudio as Epic49ProductStudio

    if APP_VERSION != EXPECTED_VERSION:
        raise RuntimeError(
            f"Launcher expected {EXPECTED_VERSION}, but imported {APP_VERSION} from {SOURCE_ROOT}"
        )
    expected_root = ROOT.resolve()
    if SOURCE_ROOT.resolve() != expected_root:
        raise RuntimeError(
            f"Wrong source imported. Expected {expected_root}; received {SOURCE_ROOT.resolve()}"
        )

    print(f"ACTIVE_VERSION={APP_VERSION}", flush=True)
    print(f"ACTIVE_BUILD={BUILD_ID}", flush=True)
    print(f"ACTIVE_SOURCE={SOURCE_ROOT}", flush=True)
    print("PRODUCT_STUDIO_EPIC49=ENABLED", flush=True)
    print("EPIC49_OPERATOR_CONTROLS=ENABLED", flush=True)

    if "--verify-only" in sys.argv:
        print("ACTIVE_RELEASE_VERIFIED=OK", flush=True)
        return 0
    if "--debug" in sys.argv:
        os.environ["CATALOG_DEBUG"] = "1"

    from app import main as app_module
    from app.epic49_desktop_schema import install as install_epic49_desktop_schema
    from app.persistent_connection_profile import install as install_persistent_connection_profile

    app_module.ProductStudio = Epic49ProductStudio
    install_epic49_desktop_schema(app_module)
    install_persistent_connection_profile(app_module)
    app_module.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
