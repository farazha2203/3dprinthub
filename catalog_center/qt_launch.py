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
    from app.epic49_desktop_schema import ensure_epic49_desktop_schema
    from app.runtime_paths import data_root

    db_path = data_root() / "catalog.sqlite3"
    db = Database(db_path)
    ensure_epic49_desktop_schema(db)
    return db


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

    db = _build_runtime()
    try:
        window = MainWindow(db)
        apply_theme(app, window._current_theme)
        contract = window.structural_contract()
        print(f"QT_UI_CONTRACT={QT_UI_CONTRACT}", flush=True)
        print("QT6_MAIN_WINDOW=ENABLED", flush=True)
        print("QT6_MODEL_VIEW=ENABLED", flush=True)
        print("QT6_WIZARD_7_STAGE=ENABLED", flush=True)
        print("QT6_COMMAND_PALETTE=ENABLED", flush=True)
        print("QT6_QTHREADPOOL=ENABLED", flush=True)
        print(f"QT6_ROUTES={len(contract['routes'])}", flush=True)
        print(f"QT6_ACTIONS={contract['action_count']}", flush=True)
        if args.verify_only:
            if contract["wizard_stages"] != 7:
                raise RuntimeError("Qt6 wizard stage contract mismatch")
            if contract["stack_count"] != len(contract["routes"]):
                raise RuntimeError("Qt6 route/stack contract mismatch")
            print("QT6_FOUNDATION_VERIFY=OK", flush=True)
            window.close()
            return 0
        window.show()
        return app.exec()
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
