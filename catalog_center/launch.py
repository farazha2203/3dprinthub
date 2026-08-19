from __future__ import annotations

import os
import sys
from pathlib import Path


EXPECTED_VERSION = "8.7.1"
ROOT = Path(__file__).resolve().parent


def main() -> int:
    root_text = str(ROOT)
    sys.path[:] = [root_text, *[item for item in sys.path if item != root_text]]

    from app.env_settings import ENV_FILE, load_project_env
    load_project_env(ENV_FILE)

    from app.version import APP_VERSION, BUILD_ID, SOURCE_ROOT
    from app.product_workspace_epic49 import ProductWorkspace
    from app.phase49_persian_sales_desktop import install as install_persian_sales_workspace
    from app.phase49_dual_publish_desktop import install as install_dual_publish_workspace
    from app.phase49_material_color_picker import install as install_material_color_picker
    from app import phase49_readiness_wizard as readiness_module
    from app.phase49_readiness_wizard import install as install_readiness_workspace
    from app.phase49_3b_guided_wizard import configure_readiness, install as install_guided_workspace
    from app.phase49_3b_ai_product_runtime import install as install_ai_product_runtime
    from app.phase49_3b_ai_runtime_patch import install as install_ai_runtime_patch
    from app.epic49_server_slider_manager import ServerSliderManager
    from app.phase49_3b_server_slider_media import install as install_server_slider_media
    from app import ux87_shell

    install_ai_runtime_patch()
    install_server_slider_media(ServerSliderManager)
    install_persian_sales_workspace(ProductWorkspace)
    install_dual_publish_workspace(ProductWorkspace)
    install_material_color_picker(ProductWorkspace)
    configure_readiness(readiness_module)
    install_readiness_workspace(ProductWorkspace)
    install_guided_workspace(ProductWorkspace)
    install_ai_product_runtime(ProductWorkspace)
    ux87_shell.ProductWorkspace = ProductWorkspace
    ux87_shell.NAV_ITEMS[:] = [
        (key, "لاگ برنامه" if key == "logs" else label, icon)
        for key, label, icon in ux87_shell.NAV_ITEMS
    ]

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
    print("UX87_SHELL=ENABLED", flush=True)
    print("UX87_EPIC49_WORKSPACE_ROUTING=ENABLED", flush=True)
    print("PRODUCT_WORKSPACE_V87=ENABLED", flush=True)
    print("PRODUCT_WORKSPACE_V871=ENABLED", flush=True)
    print("HOMEPAGE_SLIDER_SEO_V871=ENABLED", flush=True)
    print("EPIC49_UNIFIED_SYNC=ENABLED", flush=True)
    print("EPIC49_SERVER_SLIDER_MANAGER=ENABLED", flush=True)
    print("EPIC49_SERVER_SLIDER_MEDIA=ENABLED", flush=True)
    print("EPIC49_PERSIAN_SALES_HERO=ENABLED", flush=True)
    print("EPIC49_DUAL_PUBLISH_TARGETS=ENABLED", flush=True)
    print("EPIC49_LOCAL_PUBLISH_SQLITE_GUARD=ENABLED", flush=True)
    print("EPIC49_MATERIAL_COLOR_PICKER=ENABLED", flush=True)
    print("EPIC49_READINESS_WIZARD=ENABLED", flush=True)
    print("EPIC49_SEO_REFERENCE_SYNC=ENABLED", flush=True)
    print("EPIC49_GUIDED_WIZARD_7_STAGE=ENABLED", flush=True)
    print("EPIC49_HERO_MEDIA_STUDIO=ENABLED", flush=True)
    print("EPIC49_AI_PROVIDER_HUB=ENABLED", flush=True)
    print("EPIC49_AI_PRODUCT_CONTEXT=ENABLED", flush=True)
    print("EPIC49_AI_COST_TOMAN=ENABLED", flush=True)
    print("EPIC49_OPENROUTER=ENABLED", flush=True)
    print("EPIC49_PERSISTENT_DIAGNOSTICS=ENABLED", flush=True)
    print("EPIC49_DIAGNOSTIC_LOG_UI=ENABLED", flush=True)
    print("EPIC49_AUDIT_IDENTITY=ENABLED", flush=True)
    print("EPIC49_AI_COST_PERSISTENCE=ENABLED", flush=True)
    print("AI_PROFILE_MIGRATION=PRESERVED", flush=True)
    print("HOST_PROFILE_MIGRATION=PRESERVED", flush=True)

    if "--verify-only" in sys.argv:
        print("ACTIVE_RELEASE_VERIFIED=OK", flush=True)
        return 0
    if "--debug" in sys.argv:
        os.environ["CATALOG_DEBUG"] = "1"

    from app import main as app_module
    from app.db import Database
    from app.epic49_desktop_schema import install as install_epic49_desktop_schema
    from app.persistent_connection_profile import install as install_persistent_connection_profile
    from app.phase49_readiness_wizard import install_app as install_readiness_app
    from app.phase49_ai_provider_hub import install_base_app as install_ai_base, install_shell as install_ai_shell
    from app.phase49_diagnostics import configure as configure_diagnostics, audit_event
    from app.phase49_diagnostics_ui import install_database as install_diagnostic_database, install_base_app as install_diagnostic_ui
    from app.phase49_diagnostics_identity import install as install_diagnostic_identity
    from app.phase49_diagnostics_identity_ui import install as install_diagnostic_identity_ui

    install_diagnostic_database(Database)
    install_ai_base(app_module.App)
    install_epic49_desktop_schema(app_module)
    install_persistent_connection_profile(app_module)
    install_readiness_app(app_module.App)
    install_diagnostic_ui(app_module.App, app_module.DATA)
    install_diagnostic_identity_ui(app_module.App)
    app_module.ProductStudio = ProductWorkspace
    App87 = ux87_shell.build_app_class(app_module.App)
    install_ai_shell(App87)
    app = App87()
    configure_diagnostics(app.db, getattr(app, "logger", None))
    install_diagnostic_identity(app.db)
    audit_event(
        "runtime",
        "app_start",
        source_file=str(Path(__file__).resolve()),
        message=f"Catalog Center {APP_VERSION} build={BUILD_ID}",
        detail={"source": str(SOURCE_ROOT)},
    )
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
