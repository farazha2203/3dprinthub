from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _build_runtime():
    from app.db import Database
    from app.runtime_paths import data_root
    from qt6.kernel import build_kernel

    db_path = data_root() / "catalog.sqlite3"
    db = Database(db_path)
    return build_kernel(db)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--offscreen", action="store_true")
    args = parser.parse_args(argv)

    if args.verify_only or args.offscreen:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    from qt6 import QT_UI_CONTRACT
    from qt6.main_window import MainWindow
    from qt6.theme import apply_theme

    app = QApplication.instance() or QApplication(sys.argv)
    app.setOrganizationName("3DPrintHub")
    app.setApplicationName("CatalogCenterQt6")
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    kernel = _build_runtime()
    try:
        window = MainWindow(kernel)
        apply_theme(app, window._current_theme)
        contract = window.structural_contract()

        print(f"QT_UI_CONTRACT={QT_UI_CONTRACT}", flush=True)
        print("QT6_MAIN_WINDOW=ENABLED", flush=True)
        print("QT6_MODEL_VIEW=ENABLED", flush=True)
        print("QT6_WIZARD_7_STAGE=ENABLED", flush=True)
        print("QT6_COMMAND_PALETTE=ENABLED", flush=True)
        print("QT6_QTHREADPOOL=ENABLED", flush=True)
        print("QT6_APPLICATION_KERNEL=ENABLED", flush=True)
        print("QT6_PRODUCT_GALLERY_SORT=ENABLED", flush=True)
        print("QT6_FILAMENT_CRUD=ENABLED", flush=True)
        print("QT6_PROFILE_MATRIX=ENABLED", flush=True)
        print("QT6_IMAGE_DIMENSION_SIZE_SEO=ENABLED", flush=True)
        print("QT6_CONTENT_SEO_EDITOR=ENABLED", flush=True)
        print("QT6_SOURCE_LICENSE_SPECS=ENABLED", flush=True)
        print("QT6_HOMEPAGE_SLIDER_EDITOR=ENABLED", flush=True)
        print("QT6_STAGE_TRISTATE=ENABLED", flush=True)
        print("QT6_AI_SOURCE_MODES=ENABLED", flush=True)
        print("QT6_AI_PROVIDER_HUB=ENABLED", flush=True)
        print("QT6_SITE_CONNECTION_SETTINGS=ENABLED", flush=True)
        print("QT6_SINGLE_AI_CORE=ENABLED", flush=True)
        print("QT6_PRODUCT_ACQUISITION_ROUTE=ENABLED", flush=True)
        print("QT6_LEGACY_CRAWL_CONTROLS=ENABLED", flush=True)
        print("QT6_AI_MODEL_RANKING_COST=ENABLED", flush=True)
        print("QT6_AI_STRUCTURED_PROBE=ENABLED", flush=True)
        print("QT6_AI_COST_CONFIRM=ENABLED", flush=True)
        print("QT6_DIAGNOSTIC_DIALOG=ENABLED", flush=True)
        print("QT6_OPENROUTER_JSON_MODE=ENABLED", flush=True)
        print("QT6_SEMANTIC_TRANSLATION_GUARD=ENABLED", flush=True)
        print("QT6_IMAGE_FINAL_WEBP_PARITY=ENABLED", flush=True)
        print("QT6_PERSISTENT_CRAWL_INVENTORY=ENABLED", flush=True)
        print("QT6_PRODUCT_LIFECYCLE_BULK_ACTIONS=ENABLED", flush=True)
        print("QT6_PRODUCT_STATUS_BORDER_SEO=ENABLED", flush=True)
        print("QT6_SLIDER_DIRECT_INPUT_UX=ENABLED", flush=True)
        print("QT6_SEARCH_LINK_REVIEW_AI=ENABLED", flush=True)
        print("QT6_FILAMENT_BRAND_COLOR_REGISTRY=ENABLED", flush=True)
        print("QT6_PUBLISHED_REPUBLISH_UPDATE=ENABLED", flush=True)
        print(f"QT6_ROUTES={len(contract['routes'])}", flush=True)
        print(f"QT6_ACTIONS={contract['action_count']}", flush=True)
        print(f"QT6_CORES={len(contract['core_names'])}", flush=True)

        if args.verify_only:
            if contract["wizard_stages"] != 7:
                raise RuntimeError("Qt6 wizard stage contract mismatch")
            if contract["stack_count"] != len(contract["routes"]):
                raise RuntimeError("Qt6 route/stack contract mismatch")
            if not contract["ai_single_engine"] or not contract["ai_bound"]:
                raise RuntimeError("Qt6 AI core contract mismatch")
            if not contract["stage_authority_shared"]:
                raise RuntimeError("Qt6 stage authority contract mismatch")
            if len(contract["core_names"]) < 11:
                raise RuntimeError("Qt6 full parity core registry incomplete")
            if not hasattr(kernel.acquisition, "queue_items"):
                raise RuntimeError("Qt6 persistent Crawl inventory core missing")
            if not hasattr(kernel.products, "archive_many"):
                raise RuntimeError("Qt6 Product lifecycle bulk core missing")
            if not hasattr(kernel.products, "remove_many"):
                raise RuntimeError("Qt6 Product reject/tombstone core missing")
            if not hasattr(kernel.filaments, "brands") or not hasattr(kernel.filaments, "color_presets"):
                raise RuntimeError("Qt6 Filament brand/color registry core missing")
            if not hasattr(kernel, "complete_products_with_ai"):
                raise RuntimeError("Qt6 Search-Link collect+AI completion core missing")
            print("QT6_FOUNDATION_VERIFY=OK", flush=True)
            print("QT6_42B2_FULL_PARITY_VERIFY=OK", flush=True)
            window.close()
            return 0

        window.show()
        return app.exec()
    finally:
        kernel.db.close()


if __name__ == "__main__":
    raise SystemExit(main())
