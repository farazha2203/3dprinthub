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
from qt6.parity_dialogs import (
    FilamentBulkRatesDialog,
    FilamentEditorDialog,
    ProfileEditorDialog,
)
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

    def test_missing_source_profile_uses_safe_general_material_recommendations(self):
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
        self.assertEqual(materials, {"PLA", "PETG"})
        self.assertEqual(set(result["recommended_materials"]), {"PLA", "PETG"})
        self.assertNotIn("PLA-CF", materials)
        self.assertNotIn("PETG-HF", materials)
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
            "\u0646\u0645\u0648\u0646\u0647\u200c\u0633\u0627\u0632\u06cc \u0648 \u0642\u0637\u0639\u0627\u062a \u0639\u0645\u0648\u0645\u06cc",
            "\u0645\u0627\u06a9\u062a\u060c \u0627\u0633\u062a\u0646\u062f \u0648 \u0646\u0638\u0645\u200c\u062f\u0647\u0646\u062f\u0647",
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
        self.assertTrue(payload["material_main_usage"])
        self.assertTrue(payload["material_sample_parts"])
        self.assertEqual(payload["brand_description"], "توضیح برند سایت")
        self.assertEqual(payload["description"], "توضیح خود Filament")
        self.assertEqual(payload["palette_hexes"], ["#112233", "#445566"])

        disabled = self.kernel.filaments.site_payload(row, is_active=False)
        self.assertFalse(disabled["is_active"])

    def test_bridge_only_settings_and_test_do_not_require_ftp_credentials(self):
        self.db.set_setting("site_url", "https://3dprinthub.ir")
        with patch("qt6.parity_core.get_secret", return_value="bridge-token"):
            cfg = self.kernel.connection.bridge_settings()
            self.assertEqual(cfg.site_url, "https://3dprinthub.ir")
            self.assertEqual(cfg.bridge_token, "bridge-token")
            self.assertEqual(cfg.ftp_host, "")
            self.assertEqual(cfg.ftp_user, "")
            with patch(
                "qt6.parity_core.test_bridge",
                return_value={"ok": True, "status": "ok"},
            ) as probe, patch(
                "qt6.parity_core.test_publish_readiness",
                return_value={
                    "ready": True,
                    "status": "ready",
                    "blockers": [],
                },
            ) as readiness_probe:
                result = self.kernel.connection.test_bridge()
            self.assertTrue(result["ok"])
            self.assertTrue(result["publish_readiness"]["ready"])
            self.assertEqual(probe.call_args.args[0].ftp_host, "")
            self.assertEqual(readiness_probe.call_args.args[0].ftp_host, "")

    def test_bridge_health_survives_missing_publish_readiness_endpoint(self):
        self.db.set_setting("site_url", "https://3dprinthub.ir")
        with patch("qt6.parity_core.get_secret", return_value="bridge-token"), patch(
            "qt6.parity_core.test_bridge",
            return_value={"ok": True, "status": "ok"},
        ), patch(
            "qt6.parity_core.test_publish_readiness",
            side_effect=RuntimeError("Bridge HTTP 404"),
        ):
            result = self.kernel.connection.test_bridge()

        self.assertTrue(result["ok"])
        readiness = result["publish_readiness"]
        self.assertFalse(readiness["ready"])
        self.assertEqual(readiness["status"], "blocked")
        self.assertIn(
            "publish_readiness_unavailable:RuntimeError",
            readiness["blockers"],
        )

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

    def test_full_site_reconciliation_includes_locally_inactive_filaments(self):
        self.kernel.filaments.save_material("PLA")
        self.kernel.filaments.save_brand("Inactive Brand")
        self.kernel.filaments.save_color_preset(
            {
                "name": "Inactive Color",
                "color_type": "solid",
                "color_finish": "matte",
                "palette_hexes": ["#222222"],
            }
        )
        saved = self.kernel.filaments.save(
            {
                "material": "PLA",
                "brand": "Inactive Brand",
                "color": "Inactive Color",
                "color_type": "solid",
                "color_finish": "matte",
                "palette_hexes": ["#222222"],
                "roll_weight_grams": 1000,
                "sale_price_per_roll": 2_000_000,
            }
        )
        self.kernel.filaments.deactivate(int(saved["id"]))
        self.assertEqual(self.kernel.filaments.list(), [])
        all_rows = self.kernel.filaments.list(include_inactive=True)
        self.assertEqual(len(all_rows), 1)
        self.assertFalse(bool(all_rows[0]["is_active"]))

        self.kernel.connection.bridge_settings = lambda: object()
        sent = []

        def fake_sync(_settings, payload, *, operator):
            sent.append(dict(payload))
            return {"status": "ok"}

        with patch("app.epic49_site_sync.sync_filament", side_effect=fake_sync):
            result = self.kernel.sync_filaments_with_site()

        self.assertEqual(result["requested"], 1)
        self.assertEqual(result["synced"], 1)
        self.assertFalse(sent[0]["is_active"])

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
            self.assertEqual(page.image_grid.columns, 2)
            self.assertTrue(page.image_grid.large_cards)
            self.assertEqual(
                page.image_grid.scroll.verticalScrollBarPolicy(),
                Qt.ScrollBarPolicy.ScrollBarAlwaysOn,
            )
            self.assertGreaterEqual(page.image_grid.minimumHeight(), 560)
            self.assertGreaterEqual(page.image_grid.scroll.verticalScrollBar().singleStep(), 72)
            self.assertGreaterEqual(page.image_grid.scroll.verticalScrollBar().pageStep(), 420)
            button_texts = {
                button.text()
                for button in page.findChildren(type(page.product_source_btn))
            }
            self.assertIn("دریافت داده و عکس بیشتر از لینک محصول", button_texts)
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

    def test_image_grid_five_large_cards_keep_three_scroll_rows_reachable(self):
        grid = ProductImageGrid(columns=2, large_cards=True)
        try:
            grid.set_items([
                {"url": f"https://img.example/{index}.jpg", "selected": True}
                for index in range(1, 6)
            ])
            self.assertEqual(len(grid.cards), 5)
            self.assertGreaterEqual(grid.host.minimumHeight(), 3 * 492)
            self.assertEqual(
                grid.scroll.verticalScrollBarPolicy(),
                Qt.ScrollBarPolicy.ScrollBarAlwaysOn,
            )
            self.assertEqual(len(grid.selected_urls()), 5)
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


    def test_material_default_guide_is_case_insensitive_and_has_usage(self):
        self.kernel.filaments.save_material("pla")
        self.kernel.filaments.save_material("petg")
        records = {str(row["name"]).casefold(): row for row in self.kernel.filaments.material_records()}
        for key in ("pla", "petg"):
            self.assertTrue(str(records[key].get("description") or "").strip())
            self.assertTrue(str(records[key].get("main_usage") or "").strip())
            self.assertTrue(str(records[key].get("sample_parts") or "").strip())

    def test_profile_editor_supports_select_all_clear_all_and_registered_brand_edit_context(self):
        self.kernel.filaments.save_material("PLA")
        self.kernel.filaments.save_brand("Brand Alpha")
        self.kernel.filaments.save_brand("Brand Beta")
        self._save_filament("PLA", "Brand Alpha", "Black")
        self._save_filament("PLA", "Brand Beta", "White")
        dialog = ProfileEditorDialog(
            self.kernel.filaments.list(),
            filament_core=self.kernel.filaments,
        )
        try:
            dialog._set_all_filaments_checked(True)
            self.assertEqual(len(dialog._selected_filaments()), 2)
            dialog._set_all_filaments_checked(False)
            self.assertEqual(dialog._selected_filaments(), [])
            editor = FilamentEditorDialog(
                self.kernel.filaments.list()[0],
                parent=dialog,
                filament_core=dialog.filament_core,
            )
            try:
                self.assertGreaterEqual(editor.brand_library.findData("Brand Alpha"), 0)
                self.assertGreaterEqual(editor.brand_library.findData("Brand Beta"), 0)
                self.assertGreaterEqual(editor.material_library.findData("PLA"), 0)
            finally:
                editor.close()
        finally:
            dialog.close()

    def test_material_registry_exposes_usage_and_sample_columns(self):
        self.kernel.filaments.save_material("PLA")
        page = FilamentsPage(self.db, kernel=self.kernel)
        try:
            headers = [
                page.material_table.horizontalHeaderItem(i).text()
                for i in range(page.material_table.columnCount())
            ]
            self.assertEqual(page.material_table.columnCount(), 5)
            self.assertIn("\u06a9\u0627\u0631\u0628\u0631\u062f\u0647\u0627", headers)
            self.assertIn("\u0646\u0645\u0648\u0646\u0647 \u0642\u0637\u0639\u0627\u062a", headers)
            self.assertTrue(page.material_table.item(0, 3).text().strip())
            self.assertTrue(page.material_table.item(0, 4).text().strip())
        finally:
            page.close()


    def test_full_site_sync_skips_legacy_blank_brand_without_aborting_valid_rows(self):
        self.kernel.filaments.save_material("PLA")
        self.kernel.filaments.save_brand("Managed Brand")
        self._save_filament("PLA", "Managed Brand", "Black")
        legacy = self.kernel.filaments.save({
            "material": "PLA",
            "brand": "",
            "color": "Legacy Color",
            "color_type": "solid",
            "palette_hexes": ["#445566"],
            "roll_weight_grams": 1000,
            "sale_price_per_roll": 2_000_000,
        })
        rows = self.kernel.filaments.list(include_inactive=True)
        self.assertEqual(len(rows), 2)
        self.kernel.connection.bridge_settings = lambda: object()
        sent = []

        def fake_sync(_settings, payload, *, operator):
            sent.append(dict(payload))
            return {"status": "ok"}

        with patch("app.epic49_site_sync.sync_filament", side_effect=fake_sync):
            result = self.kernel.sync_filaments_with_site(rows)

        self.assertEqual(result["requested"], 2)
        self.assertEqual(result["synced"], 1)
        self.assertEqual(result["failed"], 1)
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0]["brand"], "Managed Brand")
        self.assertEqual(result["failures"][0]["row_id"], int(legacy["id"]))
        self.assertIn("ValueError", result["failures"][0]["error"])

    def test_bulk_rates_dialog_changes_only_explicitly_enabled_fields(self):
        dialog = FilamentBulkRatesDialog(4)
        try:
            enabled, widget = dialog._fields["print_hourly_rate"]
            enabled.setChecked(True)
            widget.setValue(175_000)
            enabled, widget = dialog._fields["preheat_temperature_c"]
            enabled.setChecked(True)
            widget.setValue(70)
            values = dialog.values()
            self.assertEqual(values["print_hourly_rate"], 175_000)
            self.assertEqual(values["preheat_temperature_c"], 70)
            self.assertNotIn("supervision_hourly_rate", values)
            self.assertNotIn("preheat_hours", values)
        finally:
            dialog.close()

    def test_decorative_product_recommends_pla_petg_not_engineering_cf(self):
        product_id = self._make_product("3510003")
        self.db.update_product(product_id, {
            "source_title": "Decorative dragon sculpture art display",
            "source_description": "Desktop ornament and display sculpture",
        })
        result = self.kernel.commerce.recommend_materials(product_id, [
            {"material": "PLA"},
            {"material": "PETG"},
            {"material": "PA12-CF10"},
            {"material": "PLA-CF"},
        ])
        self.assertEqual(set(result["materials"]), {"PLA", "PETG"})
        self.assertFalse(result["source_declared"])

    def test_page_extract_mapping_preserves_five_distinct_source_images(self):
        from qt6.acquisition_runtime import _page_extract_image_urls

        local_dir = self.root / "capture"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True)
        entries = []
        for index in range(1, 6):
            local_file = image_dir / f"{index:02d}.webp"
            local_file.write_bytes(b"fixture")
            entries.append({
                "url": f"https://cdn.example.test/product/image-{index}.jpg?width=1000",
                "local_file": str(local_file),
            })
        entries.append({
            "url": "https://cdn.example.test/product/image-1.jpg?width=400",
            "local_file": str(image_dir / "01.webp"),
        })
        (local_dir / "page_extract.json").write_text(
            json.dumps({"images": entries}),
            encoding="utf-8",
        )
        urls = _page_extract_image_urls(local_dir, 20)
        self.assertEqual(len(urls), 5)
        self.assertTrue(all(url.startswith("https://") for url in urls))


    def test_makerworld_product_media_filter_rejects_store_and_avatar_assets(self):
        from qt6.acquisition_runtime import _is_product_media_url

        self.assertTrue(_is_product_media_url(
            "makerworld",
            "https://makerworld.bblmw.com/makerworld/model/USabc/design/hero.jpg?width=1000",
        ))
        self.assertTrue(_is_product_media_url(
            "makerworld",
            "https://makerworld.bblmw.com/makerworld/model/USabc/123/instance/plate_1.png",
        ))
        self.assertFalse(_is_product_media_url(
            "makerworld",
            "https://store.bblcdn.eu/s8/default/material/PLA_Silk.jpg",
        ))
        self.assertFalse(_is_product_media_url(
            "makerworld",
            "https://public-cdn.bblmw.com/avatar/123/avatar.png",
        ))

    def test_ai_production_estimate_is_preview_only_and_carries_images(self):
        product_id = self._make_product("3510004")
        self.db.update_product(product_id, {
            "source_title": "Decorative vase",
            "source_description": "A decorative display vase",
            "images_json": json.dumps([
                "https://cdn.example.test/a.webp",
                "https://cdn.example.test/b.webp",
            ]),
            "selected_images_json": json.dumps([
                "https://cdn.example.test/a.webp",
            ]),
            "estimated_weight_grams": 0,
            "estimated_print_minutes": 0,
        })
        before = dict(self.db.product(product_id))
        captured = {}

        class FakeClient:
            def __init__(self, provider, key, model, product_id=None):
                captured["init"] = (provider, key, model, product_id)

            def structured_response(self, **kwargs):
                captured.update(kwargs)
                return ({
                    "length_cm": 18.0,
                    "width_cm": 12.0,
                    "height_cm": 24.0,
                    "weight_grams": 210.0,
                    "print_minutes": 315,
                    "confidence": "medium",
                    "evidence_summary": "estimated from product identity and imagery",
                    "assumptions": ["standard decorative scale"],
                    "recommended_materials": ["PLA", "PETG"],
                }, "vision-model")

        with patch("qt6.parity_core.active_ai_config", return_value=("openai", "test-key", "vision-model")), patch(
            "qt6.parity_core.resolve_source",
            return_value={
                "source_url": before["source_url"],
                "source_title": before["source_title"],
                "source_description": before["source_description"],
                "_effective_mode": "link",
            },
        ), patch("qt6.parity_core.AIProviderClient", FakeClient):
            result = self.kernel.providers.estimate_product_production(product_id, "link")

        after = dict(self.db.product(product_id))
        self.assertEqual(before["estimated_weight_grams"], after["estimated_weight_grams"])
        self.assertEqual(before["estimated_print_minutes"], after["estimated_print_minutes"])
        self.assertTrue(result["preview_only"])
        self.assertEqual(result["weight_grams"], 210.0)
        self.assertEqual(result["print_minutes"], 315)
        self.assertEqual(result["image_count"], 2)
        image_inputs = [item for item in captured["input_content"] if item.get("type") == "input_image"]
        self.assertEqual(len(image_inputs), 2)

    def test_ai_production_apply_preserves_operator_values_and_uses_safe_material_rule(self):
        for material in ("PLA", "PETG", "PA12-CF10"):
            self.kernel.filaments.save_material(material)
            self.kernel.filaments.save_brand("Owner Brand")
            self._save_filament(material, "Owner Brand", material + " Black")
        product_id = self._make_product("3510005")
        self.db.update_product(product_id, {
            "source_title": "Decorative dragon sculpture",
            "source_description": "Art display ornament",
        })
        self.kernel.commerce.save_profiles(product_id, [{
            "name": "اپراتور",
            "size_label": "بزرگ",
            "part_length_cm": 30,
            "part_width_cm": 20,
            "part_height_cm": 40,
            "production_rows": [{
                "weight_grams": 450,
                "support_weight_grams": 20,
                "print_time_minutes": 600,
            }],
            "material_options": [],
            "pricing_strategy": "dynamic",
        }])
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            changed = page._apply_production_estimate({
                "length_cm": 10,
                "width_cm": 11,
                "height_cm": 12,
                "weight_grams": 100,
                "print_minutes": 120,
            })
            profile = self.kernel.commerce.profiles(product_id)[0]
            self.assertEqual(float(profile["part_length_cm"]), 30.0)
            self.assertEqual(float(profile["part_width_cm"]), 20.0)
            self.assertEqual(float(profile["part_height_cm"]), 40.0)
            production = profile["production_rows"][0]
            self.assertEqual(float(production["weight_grams"]), 450.0)
            self.assertEqual(int(production["print_time_minutes"]), 600)
            materials = {str(item.get("material") or "") for item in profile["material_options"]}
            self.assertEqual(materials, {"PLA", "PETG"})
            self.assertNotIn("PA12-CF10", materials)
            self.assertEqual(changed, 1)
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
