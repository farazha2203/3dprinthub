from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.db import Database
from app.epic49_desktop_schema import (
    add_available_material_color,
    ensure_epic49_desktop_schema,
)
from qt6.main_window import MainWindow
from qt6.models import FilamentFilterProxyModel, FilamentTableModel, ProductTableModel
from qt6.theme import apply_theme
from qt6.workers import Worker


class Phase493I42Qt6FoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temporary.name) / "catalog.sqlite3")
        ensure_epic49_desktop_schema(self.db)

        self.db.upsert_product({
            "source_code": "makerworld",
            "external_id": "QT6-P1",
            "source_url": "https://example.com/models/qt6-p1",
            "source_title": "Qt6 Product One",
            "title_fa": "محصول تست Qt 6",
            "workflow_status": "review",
        })
        self.db.upsert_product({
            "source_code": "printables",
            "external_id": "QT6-P2",
            "source_url": "https://example.com/models/qt6-p2",
            "source_title": "Qt6 Product Two",
            "title_fa": "محصول دوم",
            "workflow_status": "uploaded",
            "server_id": "82",
        })

        add_available_material_color(
            self.db,
            "PLA",
            "سفید",
            "#FFFFFF",
            brand_name="Bambu Lab",
            manufacturer_name="Bambu Lab",
            roll_weight_grams=1000,
            stock_roll_count=2.5,
            sale_price_per_roll=4_000_000,
        )
        add_available_material_color(
            self.db,
            "PETG",
            "شفاف",
            "#EEEEEE",
            brand_name="eSUN",
            manufacturer_name="eSUN",
            roll_weight_grams=1000,
            stock_roll_count=1,
            sale_price_per_roll=4_500_000,
        )

    def tearDown(self):
        self.db.close()
        self.temporary.cleanup()

    def test_main_window_has_stable_routes_actions_and_seven_stage_wizard(self):
        window = MainWindow(self.db)
        try:
            contract = window.structural_contract()
            self.assertEqual(
                contract["routes"],
                ("dashboard", "products", "wizard", "filaments", "operations", "settings"),
            )
            self.assertEqual(contract["nav_count"], 6)
            self.assertEqual(contract["stack_count"], 6)
            self.assertEqual(contract["wizard_stages"], 7)
            self.assertGreaterEqual(contract["action_count"], 10)
            self.assertGreaterEqual(contract["threadpool_max"], 1)

            window.navigate("filaments")
            self.assertEqual(window.current_route(), "filaments")
            window.navigate("wizard")
            self.assertEqual(window.current_route(), "wizard")
        finally:
            window.close()

    def test_action_registry_reuses_same_qaction_in_menu_and_toolbar(self):
        window = MainWindow(self.db)
        try:
            refresh = window.actions.action("refresh")
            self.assertIn(refresh, window.toolbar.actions())
            file_actions = window.menuBar().actions()[0].menu().actions()
            self.assertIn(refresh, file_actions)
            self.assertEqual(refresh.shortcut().toString(), "F5")
        finally:
            window.close()

    def test_product_model_and_wizard_open_exact_product(self):
        model = ProductTableModel(self.db)
        self.assertEqual(model.rowCount(), 2)
        product_id = model.product_id_at(0)
        self.assertIsNotNone(product_id)

        window = MainWindow(self.db)
        try:
            window.open_product(product_id)
            self.assertEqual(window.current_route(), "wizard")
            self.assertEqual(window.wizard_page.product_id, product_id)
            self.assertIn(f"#{product_id}", window.wizard_page.product_label.text())
            window.wizard_page.stepper.set_stage(6)
            self.assertEqual(window.wizard_page.stack.currentIndex(), 6)
        finally:
            window.close()

    def test_filament_model_uses_model_view_and_material_filter(self):
        model = FilamentTableModel(self.db)
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.materials(), ["PETG", "PLA"])

        proxy = FilamentFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.set_material("PLA")
        self.assertEqual(proxy.rowCount(), 1)
        proxy.set_query("Bambu سفید")
        self.assertEqual(proxy.rowCount(), 1)
        proxy.set_query("eSUN")
        self.assertEqual(proxy.rowCount(), 0)

    def test_worker_reports_progress_result_and_finished_without_touching_gui(self):
        events = []
        worker = Worker(
            lambda progress: (progress(40, "مرحله اول"), progress(100, "تمام"), 42)[-1]
        )
        worker.signals.progress.connect(lambda value, message: events.append(("progress", value, message)))
        worker.signals.result.connect(lambda result: events.append(("result", result)))
        worker.signals.error.connect(lambda detail: events.append(("error", detail)))
        worker.signals.finished.connect(lambda: events.append(("finished",)))
        worker.run()

        self.assertIn(("progress", 40, "مرحله اول"), events)
        self.assertIn(("progress", 100, "تمام"), events)
        self.assertIn(("result", 42), events)
        self.assertIn(("finished",), events)
        self.assertFalse(any(event[0] == "error" for event in events))

    def test_theme_switch_and_qt_package_do_not_import_tkinter(self):
        self.assertEqual(apply_theme(self.app, "light"), "light")
        self.assertEqual(apply_theme(self.app, "dark"), "dark")

        qt_root = Path(__file__).resolve().parents[1] / "qt6"
        for source in qt_root.glob("*.py"):
            text = source.read_text(encoding="utf-8")
            self.assertNotIn("import tkinter", text, source.name)
            self.assertNotIn("from tkinter", text, source.name)


if __name__ == "__main__":
    unittest.main()
