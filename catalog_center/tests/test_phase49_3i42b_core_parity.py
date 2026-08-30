from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.db import Database
from app.epic49_desktop_schema import ensure_epic49_desktop_schema
from app.phase49_3i36_stage_finalization import LOCK_COLUMN
from qt6.kernel import AICore, build_kernel
from qt6.main_window import MainWindow
from qt6.product_explorer import ProductGalleryModel


class Phase493I42BCoreParityTests(unittest.TestCase):
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
            "external_id": "QT42B-1",
            "source_url": "https://example.com/models/qt42b-1",
            "source_title": "Source Product",
            "title_fa": "محصول اولیه",
            "local_category_slug": "home-decor",
            "workflow_status": "review",
            "images_json": json.dumps([]),
            "selected_images_json": json.dumps([]),
        })
        self.kernel = build_kernel(self.db)

    def tearDown(self):
        self.db.close()
        self.temporary.cleanup()

    def _product_id(self) -> int:
        return int(self.kernel.products.list()[0]["id"])

    def test_kernel_has_one_long_lived_core_per_capability(self):
        self.assertEqual(
            self.kernel.registry.names(),
            (
                "products",
                "images",
                "filaments",
                "acquisition",
                "publish",
                "ai",
            ),
        )
        self.assertIs(self.kernel.ai, self.kernel.ai)
        self.assertIs(self.kernel.products, self.kernel.products)
        self.assertTrue(self.kernel.contract()["ai_single_engine"])
        self.assertTrue(self.kernel.contract()["database_shared"])

    def test_ai_core_is_single_execution_boundary(self):
        core = AICore()
        calls = []
        core.bind_executor(lambda value: calls.append(value) or value)
        self.assertEqual(core.execute(7), 7)
        self.assertEqual(calls, [7])

    def test_gallery_model_reads_products_from_same_database(self):
        model = ProductGalleryModel(
            self.kernel.products,
            self.kernel.images,
        )
        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(model.product_id_at(0), self._product_id())

    def test_stage1_editor_persists_via_product_core_and_history(self):
        product_id = self._product_id()
        window = MainWindow(self.kernel)
        try:
            window.open_product(product_id)
            window.wizard_page.title_edit.setText("عنوان جدید")
            window.wizard_page.category_edit.setText("decor")
            self.assertTrue(window.wizard_page._save_stage1(notify=False))

            row = self.kernel.products.get(product_id)
            self.assertEqual(row["title_fa"], "عنوان جدید")
            self.assertEqual(row["local_category_slug"], "decor")

            history = self.db.history(product_id)
            self.assertTrue(
                any(
                    item["event_type"] == "qt_operator_edit"
                    for item in history
                )
            )
        finally:
            window.close()

    def test_stage1_lock_blocks_write_until_explicit_unlock(self):
        product_id = self._product_id()
        self.db.update_product(
            product_id,
            {
                LOCK_COLUMN: json.dumps(
                    {"quick": {"locked": True, "locked_at": "2026-08-30"}},
                    ensure_ascii=False,
                )
            },
        )
        self.assertTrue(
            self.kernel.products.is_stage_locked(product_id, "quick")
        )

        with self.assertRaisesRegex(RuntimeError, "ثبت نهایی"):
            self.kernel.products.update_operator_fields(
                product_id,
                {"title_fa": "نباید ذخیره شود"},
            )

        self.kernel.products.unlock_stage_for_edit(product_id, "quick")
        self.assertFalse(
            self.kernel.products.is_stage_locked(product_id, "quick")
        )

        row = self.kernel.products.update_operator_fields(
            product_id,
            {"title_fa": "پس از اصلاح"},
        )
        self.assertEqual(row["title_fa"], "پس از اصلاح")

    def test_main_window_reports_kernel_gallery_and_image_stage(self):
        window = MainWindow(self.kernel)
        try:
            contract = window.structural_contract()
            self.assertIn("ai", contract["core_names"])
            self.assertTrue(contract["ai_single_engine"])
            self.assertEqual(window.products_page.tabs.count(), 2)
            self.assertEqual(
                window.products_page.gallery_model.rowCount(),
                1,
            )

            window.open_product(self._product_id())
            self.assertEqual(window.wizard_page.stack.count(), 7)
            self.assertIsNotNone(window.wizard_page.image_list)
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
