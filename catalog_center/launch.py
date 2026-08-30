from __future__ import annotations

import os
import sys
from pathlib import Path


EXPECTED_VERSION = "8.9.9"
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
    from app.phase49_3c_ai_recovery import install as install_ai_recovery
    from app import phase49_3c_image_pipeline as image_pipeline_module
    from app.phase49_3c_image_pipeline import install_workspace as install_image_workspace
    from app.phase49_3c_operator_recovery import install as install_operator_recovery
    from app.phase49_3c_persian_content import (
        install as install_persian_content,
        install_app as install_persian_app,
        install_readiness as install_persian_readiness,
        install_workspace as install_persian_workspace,
    )
    from app.phase49_3c_persian_translate_guard import install as install_persian_translate_guard
    from app.phase49_3d_image_signature import install as install_phase49_3d_image_signature
    from app.phase49_3d_workflow_hardening import (
        install_ai_shell as install_phase49_3d_ai_shell,
        install_workspace as install_phase49_3d_workspace,
    )
    from app.phase49_3d_ai_ui_cleanup import install as install_phase49_3d_ai_ui_cleanup
    from app import phase49_3e_ai_task_center as phase49_3e_task_center_module
    from app.phase49_3e_ai_contract import install as install_phase49_3e_contract
    from app.phase49_3e_ai_task_center import install as install_phase49_3e_task_center
    from app.phase49_3f_gemini_provider import install as install_phase49_3f_gemini_provider
    from app.phase49_3f_ai_experience import (
        prepare_provider_modules as prepare_phase49_3f_provider_modules,
        configure_runtime as configure_phase49_3f_runtime,
        install_shell as install_phase49_3f_ai_shell,
    )
    from app import phase49_3f_workspace as phase49_3f_workspace_module
    from app.phase49_3f_workspace import install as install_phase49_3f_workspace
    from app.phase49_3f_source_refresh_guard import install as install_phase49_3f_source_refresh_guard
    from app.phase49_3g_workspace_usability import install as install_phase49_3g_workspace
    from app.phase49_3g_commerce_provenance import install as install_phase49_3g_commerce_provenance
    from app import page_extractor as page_extractor_module
    from app import crawler as crawler_module
    from app.phase49_3h_image_limits import (
        install_extractor as install_phase49_3h_image_extractor,
        install_app as install_phase49_3h_image_app,
        install_workspace as install_phase49_3h_image_workspace,
    )
    from app.phase49_3h_seo_execution import (
        install_progress as install_phase49_3h_progress,
        install_workspace as install_phase49_3h_execution_workspace,
    )
    from app.phase49_3i_local_qa_hotfix import install as install_phase49_3i_local_qa_hotfix
    from app.phase49_3i_pricing_modes import install as install_phase49_3i_pricing_workspace
    from app.phase49_3i41_filament_library import (
        install_app as install_phase49_3i41_app,
        install_workspace as install_phase49_3i41_workspace,
    )
    from app import phase49_3i15_bulk_discovery_images as phase49_3i15_bulk_module
    from app.phase49_3i43_modern_acquisition_intelligence import (
        install_runtime as install_phase49_3i43_runtime,
    )
    from app.phase49_3i_discovery_review import install_app as install_phase49_3i_discovery_review
    from app.phase49_3i_product_list import install as install_phase49_3i_product_list
    from app.phase49_3i_source_safety import install as install_phase49_3i_source_safety
    from app.epic49_server_slider_manager import ServerSliderManager
    from app.phase49_3b_server_slider_media import install as install_server_slider_media
    from app import ux87_shell

    install_phase49_3f_gemini_provider()
    prepare_phase49_3f_provider_modules()
    install_phase49_3h_image_extractor(page_extractor_module, image_pipeline_module)
    install_phase49_3i_source_safety(page_extractor_module, crawler_module)

    install_ai_runtime_patch()
    install_ai_recovery()
    install_persian_content()
    install_persian_translate_guard()
    install_phase49_3d_image_signature()
    install_server_slider_media(ServerSliderManager)
    install_persian_sales_workspace(ProductWorkspace)
    install_dual_publish_workspace(ProductWorkspace)
    install_material_color_picker(ProductWorkspace)
    configure_readiness(readiness_module)
    install_readiness_workspace(ProductWorkspace)
    install_guided_workspace(ProductWorkspace)
    install_ai_product_runtime(ProductWorkspace)
    install_image_workspace(ProductWorkspace)
    install_persian_readiness(readiness_module)
    install_operator_recovery(ProductWorkspace, readiness_module)
    install_persian_workspace(ProductWorkspace, readiness_module)
    install_phase49_3d_workspace(ProductWorkspace, readiness_module)
    install_phase49_3e_contract(phase49_3e_task_center_module)
    install_phase49_3e_task_center(ProductWorkspace, readiness_module)
    install_phase49_3f_workspace(ProductWorkspace, readiness_module)
    install_phase49_3f_source_refresh_guard(ProductWorkspace)
    install_phase49_3g_workspace(ProductWorkspace, readiness_module)
    install_phase49_3g_commerce_provenance(ProductWorkspace)
    install_phase49_3h_progress(phase49_3f_workspace_module)
    install_phase49_3h_image_workspace(ProductWorkspace)
    install_phase49_3h_execution_workspace(ProductWorkspace)
    install_phase49_3i_local_qa_hotfix(ProductWorkspace, phase49_3f_workspace_module)
    install_phase49_3i_pricing_workspace(ProductWorkspace)
    install_phase49_3i41_workspace(ProductWorkspace)
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
    print("EPIC49_3C_LIVE_READINESS=ENABLED", flush=True)
    print("EPIC49_3C_STAGE_AI=ENABLED", flush=True)
    print("EPIC49_3C_IMAGE_ID_SAFE_DELETE=ENABLED", flush=True)
    print("EPIC49_3C_IMAGE_LIMIT_10=ENABLED", flush=True)
    print("EPIC49_3C_IMAGE_SEO_METADATA=ENABLED", flush=True)
    print("EPIC49_3C_AI_COMPLETENESS_RECOVERY=ENABLED", flush=True)
    print("EPIC49_3C_PERSIAN_CONTENT_GUARD=ENABLED", flush=True)
    print("EPIC49_3C_PERSIAN_TRANSLATE_GUARD=ENABLED", flush=True)
    print("EPIC49_3C_PERSIAN_SEO=ENABLED", flush=True)
    print("EPIC49_3C_HTML_SANITIZATION=ENABLED", flush=True)
    print("EPIC49_3C_WORKSPACE_CONTENT_PERSISTENCE=ENABLED", flush=True)
    print("EPIC49_3D_WORKSPACE_LAYOUT_FIX=ENABLED", flush=True)
    print("EPIC49_3D_AI_MODEL_PICKER=ENABLED", flush=True)
    print("EPIC49_3D_ACTIVE_PROVIDER_PERSISTENCE=ENABLED", flush=True)
    print("EPIC49_3D_AI_LEGACY_ACTIVATE_REMOVED=ENABLED", flush=True)
    print("EPIC49_3D_AUTO_AI_PREPARE=ENABLED", flush=True)
    print("EPIC49_3D_LOCAL_PUBLISH_PREFLIGHT=ENABLED", flush=True)
    print("EPIC49_3D_PRICE_RANGE_CONTRACT=ENABLED", flush=True)
    print("EPIC49_3D_IMAGE_LIMIT_PRESERVED=ENABLED", flush=True)
    print("EPIC49_3D_SEMANTIC_IMAGE_SIGNATURE=ENABLED", flush=True)
    print("EPIC49_3E_AI_TASK_CENTER=ENABLED", flush=True)
    print("EPIC49_3E_IMAGE_AI_SEO=ENABLED", flush=True)
    print("EPIC49_3E_OPERATOR_IMAGE_EDITOR=ENABLED", flush=True)
    print("EPIC49_3E_NON_BLOCKING_STAGE_NAV=ENABLED", flush=True)
    print("EPIC49_3E_LOCAL_PREFLIGHT_ALWAYS_ACCESSIBLE=ENABLED", flush=True)
    print("EPIC49_3F_SELECTED_IMAGE_TEXT_ONLY_AI=ENABLED", flush=True)
    print("EPIC49_3F_UNSELECTED_IMAGE_METADATA_PRESERVED=ENABLED", flush=True)
    print("EPIC49_3F_AI_PROGRESS_TIMEOUT=ENABLED", flush=True)
    print("EPIC49_3F_SCROLLABLE_AI_CENTER=ENABLED", flush=True)
    print("EPIC49_3F_GOOGLE_GEMINI_DIRECT=ENABLED", flush=True)
    print("EPIC49_3F_RUNTIME_TRACE=ENABLED", flush=True)
    print("EPIC49_3F_SOURCE_GROUNDED_TECHNICAL_AI=ENABLED", flush=True)
    print("EPIC49_3F_DYNAMIC_PRICING=ENABLED", flush=True)
    print("EPIC49_3G_WORKSPACE_VERTICAL_SCROLL=ENABLED", flush=True)
    print("EPIC49_3G_GALLERY_HORIZONTAL_SCROLL=ENABLED", flush=True)
    print("EPIC49_3G_COMPACT_COMMERCE=ENABLED", flush=True)
    print("EPIC49_3G_AI_AUTOFILL_PROVENANCE=ENABLED", flush=True)
    print("EPIC49_3G_MANUAL_OVERRIDE_GUARD=ENABLED", flush=True)
    print("EPIC49_3G_AI_DISABLE_PER_GROUP=ENABLED", flush=True)
    print("EPIC49_3G_COMMERCE_PROVENANCE=ENABLED", flush=True)
    print("EPIC49_3H_SEO_EXECUTION_CONSOLE=ENABLED", flush=True)
    print("EPIC49_3H_RESULT_ERROR_DRAWER=ENABLED", flush=True)
    print("EPIC49_3H_AI_COST_LEDGER=ENABLED", flush=True)
    print("EPIC49_3H_PUBLISH_COST_RECEIPT=ENABLED", flush=True)
    print("EPIC49_3H_IMAGE_LIMIT_DEFAULT_10=ENABLED", flush=True)
    print("EPIC49_3H_IMAGE_LIMIT_HARD_MAX_20=ENABLED", flush=True)
    print("EPIC49_3H_PERSISTED_IMAGE_CAP=ENABLED", flush=True)
    print("EPIC49_3I_EXACT_SEARCH_URL=ENABLED", flush=True)
    print("EPIC49_3I_DISCOVERY_REVIEW_QUEUE=ENABLED", flush=True)
    print("EPIC49_3I_PREVIEW_ONE_IMAGE=ENABLED", flush=True)
    print("EPIC49_3I_APPROVAL_BEFORE_FULL_FETCH=ENABLED", flush=True)
    print("EPIC49_3I_ARCHIVE_BLOCK_DEDUPE=ENABLED", flush=True)
    print("EPIC49_3I_SOURCE_TEXT_LATIN_SAFE=ENABLED", flush=True)
    print("EPIC49_3I_LIGHTWEIGHT_PRODUCT_LIST=ENABLED", flush=True)
    print("EPIC49_3I_PRODUCT_GALLERY_CARDS=ENABLED", flush=True)
    print("EPIC49_3I_PRODUCT_LIST_ONLY_IMAGE_NAME_EDIT=ENABLED", flush=True)
    print("EPIC49_3I_AI_PROGRESS_FIRST_PAINT=ENABLED", flush=True)
    print("EPIC49_3I_PRICING_FIXED_RANGE_FORMULA=ENABLED", flush=True)
    print("EPIC49_3I29_PRODUCTS_PAGE_PAGED_48=ENABLED", flush=True)
    print("EPIC49_3I29_DEFERRED_GLOBAL_REFRESH=ENABLED", flush=True)
    print("EPIC49_3I31_SMART_LINK_AI=ENABLED", flush=True)
    print("EPIC49_3I31_BATCH_SELECTED_PRODUCTS_AI=ENABLED", flush=True)
    print("EPIC49_3I31_AI_TITLE_TEXT_ONLY=ENABLED", flush=True)
    print("EPIC49_3I31_AI_SELECTED_IMAGE_SEO=ENABLED", flush=True)
    print("EPIC49_3I33_CONSOLIDATED_PRODUCT_AI=ENABLED", flush=True)
    print("EPIC49_3I33_LIVE_LINK_AI=ENABLED", flush=True)
    print("EPIC49_3I33_SAVED_DATA_AI=ENABLED", flush=True)
    print("EPIC49_3I33_SCREENSHOT_VISION_AI=ENABLED", flush=True)
    print("EPIC49_3I33_REPAIR_AI=ENABLED", flush=True)
    print("EPIC49_3I33_OPERATOR_MATERIAL_COLOR_ONLY=ENABLED", flush=True)
    print("EPIC49_3I33_EXPLICIT_PRODUCTS_REFRESH=ENABLED", flush=True)
    print("EPIC49_3I33_SINGLE_CARD_UPDATE=ENABLED", flush=True)
    print("EPIC49_3I33_IMAGE_FILE_METADATA=ENABLED", flush=True)
    print("EPIC49_3I33_RUNTIME_TELEMETRY=ENABLED", flush=True)
    print("EPIC49_3I34_PROFILE_MATRIX=ENABLED", flush=True)
    print("EPIC49_3I34_PROFILE_CLONE=ENABLED", flush=True)
    print("EPIC49_3I34_SIZE_WEIGHT_DEPENDENCY=ENABLED", flush=True)
    print("EPIC49_3I34_PROFILE_PRICE_AUTHORITY=ENABLED", flush=True)
    print("EPIC49_3I34_DESKTOP_STORE_SYNC=ENABLED", flush=True)
    print("EPIC49_3I35_OPERATOR_LEDGER=ENABLED", flush=True)
    print("EPIC49_3I35_BRAND_AWARE_FILAMENT_OFFERS=ENABLED", flush=True)
    print("EPIC49_3I35_RESILIENT_AI_RETRY_FAILOVER=ENABLED", flush=True)
    print("EPIC49_3I35_MANUAL_SEO_SOURCE_REVIEW=ENABLED", flush=True)
    print("EPIC49_3I35_LOCAL_PROFILE_SNAPSHOT_AUTHORITY=ENABLED", flush=True)
    print("EPIC49_3I36_SEVEN_STAGE_FINALIZATION=ENABLED", flush=True)
    print("EPIC49_3I36_AI_UNLOCKED_STAGE_ONLY=ENABLED", flush=True)
    print("EPIC49_3I36_LOCKED_PROFILE_COMMERCE_GUARD=ENABLED", flush=True)
    print("EPIC49_3I36_AI_STATE_NO_NETWORK_HYDRATION=ENABLED", flush=True)
    print("EPIC49_3I36_SEMANTIC_TITLE_GUARD=ENABLED", flush=True)
    print("EPIC49_3I37_SEVEN_STAGE_AI_ORCHESTRATOR=ENABLED", flush=True)
    print("EPIC49_3I37_PERSISTED_SOURCE_MODE=ENABLED", flush=True)
    print("EPIC49_3I37_SCREENSHOT_SELECTED_FOR_SITE=ENABLED", flush=True)
    print("EPIC49_3I37_STAGE_BY_STAGE_APPLY=ENABLED", flush=True)
    print("EPIC49_3I37_SEO_LANGUAGE_GUARD=ENABLED", flush=True)
    print("EPIC49_3I38_PERMANENT_CRAWL_LEDGER=ENABLED", flush=True)
    print("EPIC49_3I38_REJECT_PURGE_TOMBSTONE=ENABLED", flush=True)
    print("EPIC49_3I38_CONTINUATION_CURSOR=ENABLED", flush=True)
    print("EPIC49_3I38_DIRECT_LINK_PRE_ACQUISITION_GUARD=ENABLED", flush=True)
    print("EPIC49_3I38_STAGE_SCOPED_AI=ENABLED", flush=True)
    print("EPIC49_3I38_BULK_STAGE4_SAME_ENGINE=ENABLED", flush=True)
    print("EPIC49_3I39_PROFESSIONAL_STAGE2=ENABLED", flush=True)
    print("EPIC49_3I39_OFFER_MANUFACTURER_MATERIAL_COLOR=ENABLED", flush=True)
    print("EPIC49_3I39_OFFER_PREHEAT_PRICING=ENABLED", flush=True)
    print("EPIC49_3I39_PROFILE_IDENTITY_DIMENSIONS_ONLY=ENABLED", flush=True)
    print("EPIC49_3I39_READINESS_REPAIR_LOOP=ENABLED", flush=True)
    print("EPIC49_3I39_AI_DIALOG_BEFORE_AFTER=ENABLED", flush=True)
    print("EPIC49_3I39_TOP_VIEWPORT_SCREENSHOT=ENABLED", flush=True)
    print("EPIC49_3I40_MULTI_BRAND_FILTER_SELECTION=ENABLED", flush=True)
    print("EPIC49_3I40_PRODUCT_OFFER_FIXED_PRICE=ENABLED", flush=True)
    print("EPIC49_3I40_COLOR_PREVIEW=ENABLED", flush=True)
    print("EPIC49_3I40_READINESS_DATA_VS_FINALIZATION=ENABLED", flush=True)
    print("EPIC49_3I40_AI_PROGRESS_TRUTH=ENABLED", flush=True)
    print("EPIC49_3I41_FILAMENT_LIBRARY=ENABLED", flush=True)
    print("EPIC49_3I41_GROUPED_FILAMENT_CHECKLIST=ENABLED", flush=True)
    print("EPIC49_3I41_FILAMENT_SITE_SYNC=ENABLED", flush=True)
    print("EPIC49_3I43_MODERN_ACQUISITION_INTELLIGENCE=ENABLED", flush=True)
    print("EPIC49_3I43_CONDITIONAL_HTTP_CACHE=ENABLED", flush=True)
    print("EPIC49_3I43_ROBOTS_RETRY_AFTER_GUARD=ENABLED", flush=True)
    print("EPIC49_3I43_PUBLIC_JSON_ENDPOINT_PROVENANCE=ENABLED", flush=True)
    print("EPIC49_3I44_ADAPTIVE_HOST_THROTTLE=ENABLED", flush=True)
    print("EPIC49_3I44_BOUNDED_TRANSIENT_RETRY=ENABLED", flush=True)
    print("EPIC49_3I44_STALE_CACHE_TRANSIENT_FALLBACK=ENABLED", flush=True)
    print("EPIC49_3I44_CONDITION_DRIVEN_BROWSER_READINESS=ENABLED", flush=True)
    print("EPIC49_3I44_ENDPOINT_SCHEMA_ONLY=ENABLED", flush=True)
    print("EPIC49_3I44_GZIP_SITEMAP_DISCOVERY=ENABLED", flush=True)
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
    from app.phase49_3c_image_pipeline import install_base_app as install_image_base

    configure_phase49_3f_runtime(app_module.DATA)
    install_diagnostic_database(Database)
    install_ai_base(app_module.App)
    install_image_base(app_module)
    install_epic49_desktop_schema(app_module)
    install_persistent_connection_profile(app_module)
    install_readiness_app(app_module.App)
    install_persian_app(app_module.App)
    install_diagnostic_ui(app_module.App, app_module.DATA)
    install_diagnostic_identity_ui(app_module.App)
    app_module.ProductStudio = ProductWorkspace
    App87 = ux87_shell.build_app_class(app_module.App)
    install_phase49_3i41_app(App87)
    install_ai_shell(App87)
    install_phase49_3d_ai_shell(App87)
    install_phase49_3d_ai_ui_cleanup(App87)
    install_phase49_3f_ai_shell(App87, app_module.DATA)
    install_phase49_3h_image_app(App87)
    install_phase49_3i_discovery_review(App87)
    install_phase49_3i_product_list(App87)
    app = App87()
    install_phase49_3i43_runtime(
        app,
        bulk_module=phase49_3i15_bulk_module,
        app_module=app_module,
    )
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
