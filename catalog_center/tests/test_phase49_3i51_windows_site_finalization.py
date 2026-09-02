from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.db import Database
from qt6.image_gallery import ProductImageGrid
from qt6.kernel import build_kernel
from qt6.pages import FilamentsPage, OperationsPage
from qt6.parity_dialogs import FilamentEditorDialog
from qt6.product_wizard import ProductWizardPage


class Phase493I51WindowsSiteFinalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = Database(self.root / "catalog.sqlite3")
        self.db.upsert_source(
            {
                "code": "makerworld",
                "name": "MakerWorld",
                "enabled": 1,
                "methods": ["browser", "http", "sitemap"],
                "listing_urls": [
                    "https://makerworld.com/en/search/models?keyword={query}"
                ],
                "model_url_pattern": (
                    r"https?://(?:www\\.)?makerworld\\.com/"
                    r"(?:[a-z]{2}/)?models/(?P<external_id>\\d+)"
                ),
                "requires_login": False,
                "reference_only": False,
            }
        )
        self.db.upsert_source(
            {
                "code": "grabcad",
                "name": "GrabCAD Library",
                "enabled": 1,
                "methods": ["browser", "http"],
                "listing_urls": ["https://grabcad.com/library"],
                "model_url_pattern": r"https?://grabcad\\.com/library/.+",
                "requires_login": False,
                "reference_only": False,
            }
        )
        self.kernel = build_kernel(self.db)

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def _make_product(self, external_id: str = "3510001") -> int:
        self.db.upsert_product(
            {
                "source_code": "makerworld",
                "external_id": external_id,
                "source_url": f"https://makerworld.com/en/models/{external_id}-test",
                "source_title": "Source Product",
                "source_description": "",
                "title_fa": "محصول تست نهایی",
                "short_description_fa": "توضیح تست",
                "description_fa": "توضیح تست",
                "workflow_status": "review",
                "images_json": "[]",
                "selected_images_json": "[]",
            }
        )
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("makerworld", external_id),
        ).fetchone()
        return int(row["id"])

    def _save_filament(self, material: str, brand: str, color: str) -> None:
        self.kernel.filaments.save(
            {
                "material": material,
                "brand": brand,
                "color": color,
                "color_type": "solid",
                "color_finish": "matte",
                "palette_hexes": ["#445566"],
                "roll_weight_grams": 1000,
                "sale_price_per_roll": 2_000_000,
            }
        )

    def test_missing_source_profile_creates_explicit_default_with_all_pla_petg_family_filaments(self):
        for material, color in (
            ("PLA", "PLA Base"),
            ("PLA-CF", "PLA CF"),
            ("PLA Silk", "PLA Silk"),
            ("PETG", "PETG Base"),
            ("PETG-HF", "PETG HF"),
            ("ABS", "ABS"),
        ):
            self._save_filament(material, "Owner Brand", color)

        product_id = self._make_product()
        result = self.kernel.commerce.bootstrap_from_source(
            product_id,
            self.kernel.filaments.list(),
        )
        profiles = self.kernel.commerce.profiles(product_id)

        self.assertTrue(result["changed"])
        self.assertTrue(result["fallback_used"])
        self.assertEqual(len(profiles), 1)
        profile = profiles[0]
        self.assertEqual(profile["name"], "پیش‌فرض")
        self.assertEqual(profile["size_label"], "پیش‌فرض")
        row = profile["production_rows"][0]
        self.assertEqual(float(row["weight_grams"]), 100.0)
        self.assertEqual(float(row["support_weight_grams"]), 50.0)
        self.assertEqual(int(row["print_time_minutes"]), 60)
        materials = {
            str(item.get("material") or "")
            for item in profile["material_options"]
        }
        self.assertTrue({"PLA", "PLA-CF", "PLA Silk", "PETG", "PETG-HF"}.issubset(materials))
        self.assertNotIn("ABS", materials)

    def test_filament_editor_uses_managed_brand_material_color_and_optional_description(self):
        self.kernel.filaments.save_brand("Bambu Lab", "برند تست")
        self.kernel.filaments.save_material("PLA", "متریال تست", 1_500_000)
        self.kernel.filaments.save_color_preset(
            {
                "name": "صورتی پاستلی",
                "color_type": "solid",
                "color_finish": "matte",
                "palette_hexes": ["#F5D4ED"],
            }
        )
        dialog = FilamentEditorDialog(
            parent=None,
            filament_core=self.kernel.filaments,
        )
        try:
            dialog.brand_library.setCurrentIndex(
                dialog.brand_library.findData("Bambu Lab")
            )
            dialog.material_library.setCurrentIndex(
                dialog.material_library.findData("PLA")
            )
            for index in range(dialog.color_library.count()):
                preset = dialog.color_library.itemData(index)
                if isinstance(preset, dict) and preset.get("name") == "صورتی پاستلی":
                    dialog.color_library.setCurrentIndex(index)
                    break
            dialog.filament_description.setPlainText("توضیح اختیاری فیلامنت")
            values = dialog.values()
            self.assertEqual(values["brand"], "Bambu Lab")
            self.assertEqual(values["material"], "PLA")
            self.assertEqual(values["color"], "صورتی پاستلی")
            self.assertEqual(values["description"], "توضیح اختیاری فیلامنت")
            self.assertFalse(hasattr(dialog, "brand"))
            self.assertFalse(hasattr(dialog, "material"))
        finally:
            dialog.close()

    def test_filament_workspace_has_material_brand_and_color_registries(self):
        self.kernel.filaments.save_material("PLA", "توضیح PLA", 1_250_000)
        self.kernel.filaments.save_brand("Polymaker", "توضیح برند")
        page = FilamentsPage(self.db, kernel=self.kernel)
        try:
            labels = [
                page.workspace_tabs.tabText(index)
                for index in range(page.workspace_tabs.count())
            ]
            self.assertEqual(
                labels,
                ["فیلامنت‌ها", "متریال‌ها", "برندها", "رنگ‌ها"],
            )
            self.assertGreaterEqual(page.material_table.rowCount(), 1)
            self.assertGreaterEqual(page.brand_table.rowCount(), 1)
            self.assertIn("1,250,000", page.material_table.item(0, 1).text())
        finally:
            page.close()

    def test_filament_table_model_preserves_optional_description_for_edit_and_site_sync(self):
        self.kernel.filaments.save_material("PLA")
        self.kernel.filaments.save_brand("Description Brand")
        self.kernel.filaments.save_color_preset(
            {
                "name": "Description Color",
                "color_type": "solid",
                "color_finish": "matte",
                "palette_hexes": ["#123456"],
            }
        )
        self.kernel.filaments.save(
            {
                "material": "PLA",
                "brand": "Description Brand",
                "color": "Description Color",
                "description": "توضیحی که نباید هنگام Edit از بین برود",
                "color_type": "solid",
                "color_finish": "matte",
                "palette_hexes": ["#123456"],
                "roll_weight_grams": 1000,
                "sale_price_per_roll": 2_000_000,
            }
        )
        page = FilamentsPage(self.db, kernel=self.kernel)
        try:
            self.assertEqual(len(page.model.rows), 1)
            self.assertEqual(
                page.model.rows[0]["description"],
                "توضیحی که نباید هنگام Edit از بین برود",
            )
            dialog = FilamentEditorDialog(
                page.model.rows[0],
                parent=None,
                filament_core=self.kernel.filaments,
            )
            try:
                self.assertEqual(
                    dialog.filament_description.toPlainText(),
                    "توضیحی که نباید هنگام Edit از بین برود",
                )
            finally:
                dialog.close()
        finally:
            page.close()

    def test_registry_renames_propagate_to_assigned_filaments_without_stale_identity(self):
        self.kernel.filaments.save_material("PLA", "ماده اولیه", 1_200_000)
        self.kernel.filaments.save_brand("Old Brand", "برند قدیمی")
        self.kernel.filaments.save_color_preset(
            {
                "name": "Old Color",
                "color_type": "solid",
                "color_finish": "matte",
                "palette_hexes": ["#112233"],
            }
        )
        self.kernel.filaments.save(
            {
                "material": "PLA",
                "brand": "Old Brand",
                "color": "Old Color",
                "color_type": "solid",
                "color_finish": "matte",
                "palette_hexes": ["#112233"],
                "roll_weight_grams": 1000,
                "sale_price_per_roll": 2_000_000,
            }
        )

        self.kernel.filaments.save_brand(
            "New Brand",
            "برند جدید",
            previous_name="Old Brand",
        )
        self.kernel.filaments.save_material(
            "PLA Plus",
            "متریال جدید",
            1_350_000,
            previous_name="PLA",
        )
        self.kernel.filaments.save_color_preset(
            {
                "name": "New Color",
                "color_type": "dual",
                "color_finish": "glossy",
                "palette_hexes": ["#334455", "#778899"],
            },
            previous_name="Old Color",
        )

        rows = self.kernel.filaments.list()
        self.assertEqual(len(rows), 1)
        item = rows[0]
        self.assertEqual(item["brand_name"], "New Brand")
        self.assertEqual(item["manufacturer_name"], "New Brand")
        self.assertEqual(item["material_name"], "PLA Plus")
        self.assertEqual(item["color_name"], "New Color")
        self.assertEqual(item["color_type"], "dual")
        self.assertEqual(item["color_finish"], "glossy")
        self.assertEqual(
            json.loads(item["palette_hex_json"]),
            ["#334455", "#778899"],
        )
        self.assertNotIn("Old Brand", self.kernel.filaments.brands())
        self.assertNotIn("PLA", self.kernel.filaments.materials())

    def test_registry_rename_refuses_identity_collision_before_mutation(self):
        self.kernel.filaments.save_brand("Brand A")
        self.kernel.filaments.save_brand("Brand B")
        self.kernel.filaments.save_material("PLA")
        self.kernel.filaments.save_color_preset(
            {
                "name": "Black",
                "color_type": "solid",
                "color_finish": "matte",
                "palette_hexes": ["#111111"],
            }
        )
        for brand in ("Brand A", "Brand B"):
            self.kernel.filaments.save(
                {
                    "material": "PLA",
                    "brand": brand,
                    "color": "Black",
                    "color_type": "solid",
                    "color_finish": "matte",
                    "palette_hexes": ["#111111"],
                    "roll_weight_grams": 1000,
                    "sale_price_per_roll": 2_000_000,
                }
            )

        with self.assertRaises(ValueError):
            self.kernel.filaments.save_brand(
                "Brand B",
                previous_name="Brand A",
            )

        rows = self.kernel.filaments.list()
        self.assertEqual(
            {row["brand_name"] for row in rows},
            {"Brand A", "Brand B"},
        )

    def test_filament_site_payload_carries_registry_metadata_without_ftp_dependency(self):
        self.kernel.filaments.save_material(
            "PLA",
            "توضیح متریال سایت",
            1_450_000,
        )
        self.kernel.filaments.save_brand(
            "Bambu Lab",
            "توضیح برند سایت",
        )
        self.kernel.filaments.save_color_preset(
            {
                "name": "Ocean",
                "color_type": "dual",
                "color_finish": "glossy",
                "palette_hexes": ["#112233", "#445566"],
            }
        )
        saved = self.kernel.filaments.save(
            {
                "material": "PLA",
                "brand": "Bambu Lab",
                "color": "Ocean",
                "description": "توضیح خود Filament",
                "color_type": "dual",
                "color_finish": "glossy",
                "palette_hexes": ["#112233", "#445566"],
                "roll_weight_grams": 1000,
                "stock_roll_count": 2,
                "sale_price_per_roll": 2_000_000,
            }
        )
        row = next(
            item
            for item in self.kernel.filaments.list()
            if int(item["id"]) == int(saved["id"])
        )
        payload = self.kernel.filaments.site_payload(row)
        self.assertEqual(payload["material"], "PLA")
        self.assertEqual(payload["material_description"], "توضیح متریال سایت")
        self.assertEqual(payload["material_price_per_kg"], 1_450_000)
        self.assertEqual(payload["brand_description"], "توضیح برند سایت")
        self.assertEqual(payload["description"], "توضیح خود Filament")
        self.assertEqual(payload["palette_hexes"], ["#112233", "#445566"])

        disabled = self.kernel.filaments.site_payload(row, is_active=False)
        self.assertFalse(disabled["is_active"])

    def test_kernel_filament_sync_reuses_existing_bridge_and_reports_partial_failure(self):
        self.kernel.filaments.save_material("PLA")
        self.kernel.filaments.save_brand("Brand One")
        self.kernel.filaments.save_brand("Brand Two")
        self._save_filament("PLA", "Brand One", "Black")
        self._save_filament("PLA", "Brand Two", "White")
        rows = self.kernel.filaments.list()

        self.kernel.connection.bridge_settings = lambda: object()
        calls = []

        def fake_sync(_settings, payload, *, operator):
            calls.append((dict(payload), operator))
            if payload["brand"] == "Brand Two":
                raise RuntimeError("simulated site failure")
            return {"status": "ok"}

        with patch("app.epic49_site_sync.sync_filament", side_effect=fake_sync):
            result = self.kernel.sync_filaments_with_site(rows)

        self.assertEqual(result["requested"], 2)
        self.assertEqual(result["synced"], 1)
        self.assertEqual(result["failed"], 1)
        self.assertEqual(len(calls), 2)
        self.assertTrue(
            all(operator == "catalog-center-qt6" for _payload, operator in calls)
        )

    def test_filament_page_exposes_selected_and_all_site_sync_controls(self):
        page = FilamentsPage(self.db, kernel=self.kernel)
        try:
            self.assertEqual(page.site_sync_selected_btn.text(), "Sync انتخابی با سایت")
            self.assertEqual(page.site_sync_all_btn.text(), "Sync همه با سایت")
            self.assertIsNotNone(page.site_sync_status)
        finally:
            page.close()

    def test_product_image_stage_is_larger_two_row_capable_and_source_link_is_fixed(self):
        product_id = self._make_product("3510002")
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            self.assertTrue(page.product_source_btn.isEnabled())
            self.assertEqual(page.image_grid.columns, 3)
            self.assertGreaterEqual(page.image_grid.minimumHeight(), 540)
            button_texts = {
                button.text()
                for button in page.findChildren(type(page.product_source_btn))
            }
            self.assertIn("دریافت مجدد تصاویر از لینک محصول", button_texts)
            self.assertIn("حذف انتخاب‌شده‌ها", button_texts)
        finally:
            page.close()

    def test_image_grid_multi_selection_is_observable_and_bulk_addressable(self):
        grid = ProductImageGrid(columns=3)
        try:
            grid.set_items(
                [
                    {"url": "https://img.example/1.jpg", "selected": False},
                    {"url": "https://img.example/2.jpg", "selected": False},
                    {"url": "https://img.example/3.jpg", "selected": False},
                ]
            )
            grid.set_all_selected(True)
            self.assertEqual(len(grid.selected_urls()), 3)
            self.assertIn("3 انتخاب‌شده", grid.summary.text())
            grid.set_all_selected(False)
            self.assertEqual(grid.selected_urls(), [])
            self.assertIn("0 انتخاب‌شده", grid.summary.text())
        finally:
            grid.close()

    def test_makerworld_url_auto_switches_source_away_from_grabcad_and_live_results_exist(self):
        page = OperationsPage(self.db, kernel=self.kernel)
        try:
            grabcad_index = page.source.findData("grabcad")
            self.assertGreaterEqual(grabcad_index, 0)
            page.source.setCurrentIndex(grabcad_index)
            page.url.setText(
                "https://makerworld.com/en/search/models?keyword=Minimalistic+Japandi+Decor"
            )
            page._sync_source_from_url()
            self.assertEqual(page.source.currentData(), "makerworld")
            self.assertIsNotNone(page.live_results)
            self.assertGreaterEqual(page.live_results.minimumHeight(), 210)
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
