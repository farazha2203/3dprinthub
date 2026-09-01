from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QDoubleSpinBox, QSpinBox
from PIL import Image

from app import ai_providers
from app.ai_providers import AIProviderClient
from app.db import Database
from app.phase49_3i36_stage_finalization import LOCK_COLUMN
from qt6.kernel import AICore, build_kernel
from qt6.main_window import MainWindow
from qt6.parity_dialogs import FIXED_PRICE_COLUMN, ProfileEditorDialog
from qt6.product_explorer import ProductGalleryModel


class Phase493I42BCoreParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temporary.name) / "catalog.sqlite3")
        self.db.upsert_product({
            "source_code": "makerworld",
            "external_id": "QT42B-1",
            "source_url": "https://example.com/models/qt42b-1",
            "source_title": "Cake Stand",
            "source_short_description": "A decorative cake stand.",
            "source_description": "A decorative cake stand with two levels.",
            "title_fa": "استند کیک",
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

    def _add_filaments(self):
        pla = self.kernel.filaments.save({
            "manufacturer": "Bambu Lab",
            "brand": "Bambu Lab",
            "material": "PLA",
            "color": "سفید",
            "hex": "#FFFFFF",
            "roll_weight_grams": 1000,
            "stock_roll_count": 2,
            "sale_price_per_roll": 4_000_000,
            "print_hourly_rate": 35_000,
            "supervision_hourly_rate": 15_000,
            "preheat_hours": 2,
            "preheat_temperature_c": 55,
            "preheat_hourly_rate": 9_000,
        })
        petg = self.kernel.filaments.save({
            "manufacturer": "eSUN",
            "brand": "eSUN",
            "material": "PETG",
            "color": "مشکی",
            "hex": "#111111",
            "roll_weight_grams": 1000,
            "stock_roll_count": 3,
            "sale_price_per_roll": 4_500_000,
            "print_hourly_rate": 40_000,
            "supervision_hourly_rate": 15_000,
        })
        return pla, petg

    def test_kernel_has_one_long_lived_core_per_capability(self):
        self.assertEqual(
            self.kernel.registry.names(),
            (
                "products",
                "images",
                "filaments",
                "categories",
                "stages",
                "commerce",
                "providers",
                "connection",
                "acquisition",
                "publish",
                "ai",
            ),
        )
        self.assertIs(self.kernel.ai, self.kernel.ai)
        self.assertIs(self.kernel.products, self.kernel.products)
        self.assertTrue(self.kernel.contract()["ai_single_engine"])
        self.assertTrue(self.kernel.contract()["ai_bound"])
        self.assertTrue(self.kernel.contract()["database_shared"])
        self.assertTrue(self.kernel.contract()["stage_authority_shared"])

    def test_ai_core_is_single_execution_boundary(self):
        core = AICore()
        calls = []
        core.bind_executor(lambda value: calls.append(value) or value)
        self.assertEqual(core.execute(7), 7)
        self.assertEqual(calls, [7])

    def test_gallery_model_reads_same_db_and_supports_sort_contract(self):
        model = ProductGalleryModel(
            self.kernel.products,
            self.kernel.images,
        )
        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(model.product_id_at(0), self._product_id())
        model.refresh(sort_key="title_fa")
        self.assertEqual(model.rowCount(), 1)

    def test_stage1_has_source_and_persian_titles_plus_site_category_combo(self):
        product_id = self._product_id()
        window = MainWindow(self.kernel)
        try:
            window.open_product(product_id)
            wizard = window.wizard_page
            self.assertEqual(wizard.source_title.text(), "Cake Stand")
            self.assertEqual(wizard.title_fa.text(), "استند کیک")
            self.assertIsInstance(wizard.category, QComboBox)
            self.assertGreater(wizard.category.count(), 0)

            wizard.title_fa.setText("استند کیک دو طبقه")
            index = wizard.category.findData("home-decor")
            if index >= 0:
                wizard.category.setCurrentIndex(index)
            wizard._save_stage1()

            row = self.kernel.products.get(product_id)
            self.assertEqual(row["title_fa"], "استند کیک دو طبقه")
        finally:
            window.close()

    def test_stage_lock_blocks_write_until_explicit_unlock(self):
        product_id = self._product_id()
        self.db.update_product(
            product_id,
            {
                LOCK_COLUMN: json.dumps(
                    {"quick": {"locked": True, "locked_at": "2026-08-31"}},
                    ensure_ascii=False,
                )
            },
        )

        with self.assertRaisesRegex(RuntimeError, "ثبت نهایی"):
            self.kernel.stages.update(
                product_id,
                "quick",
                {"title_fa": "نباید ذخیره شود"},
            )

        self.kernel.stages.unlock(product_id, "quick")
        row = self.kernel.stages.update(
            product_id,
            "quick",
            {"title_fa": "پس از اصلاح"},
        )
        self.assertEqual(row["title_fa"], "پس از اصلاح")

    def test_filament_core_supports_add_edit_and_soft_deactivate(self):
        saved, _ = self._add_filaments()
        self.assertEqual(len(self.kernel.filaments.list()), 2)

        edited = self.kernel.filaments.save(
            {
                "manufacturer": "Bambu Lab",
                "brand": "Bambu Lab",
                "material": "PLA",
                "color": "سفید",
                "hex": "#FAFAFA",
                "roll_weight_grams": 1000,
                "stock_roll_count": 4,
                "sale_price_per_roll": 4_200_000,
            },
            previous_row_id=int(saved["id"]),
        )
        self.assertEqual(int(edited["id"]), int(saved["id"]))
        self.assertEqual(float(edited["stock_roll_count"]), 4.0)
        self.assertEqual(int(edited["sale_price_per_roll"]), 4_200_000)
        self.assertEqual(int(edited["print_hourly_rate"]), 35_000)
        self.assertEqual(int(edited["supervision_hourly_rate"]), 15_000)
        self.assertEqual(float(edited["preheat_hours"]), 2.0)
        self.assertEqual(int(edited["preheat_hourly_rate"]), 9_000)

        self.kernel.filaments.deactivate(int(edited["id"]))
        active_ids = {int(item["id"]) for item in self.kernel.filaments.list()}
        self.assertNotIn(int(edited["id"]), active_ids)

    def test_profile_matrix_persists_size_times_production_rows_times_filaments(self):
        pla, petg = self._add_filaments()
        product_id = self._product_id()

        profile = self.kernel.commerce.upsert_profile(
            product_id,
            {
                "name": "سایز 20",
                "size_label": "20 cm",
                "part_length_cm": 20,
                "part_width_cm": 15,
                "part_height_cm": 8,
                "pricing_strategy": "dynamic",
                "production_rows": [
                    {
                        "weight_grams": 80,
                        "support_weight_grams": 5,
                        "print_time_minutes": 120,
                    },
                    {
                        "weight_grams": 95,
                        "support_weight_grams": 10,
                        "print_time_minutes": 150,
                    },
                    {
                        "weight_grams": 110,
                        "support_weight_grams": 15,
                        "print_time_minutes": 180,
                    },
                ],
                "material_options": [pla, petg],
            },
        )

        self.assertEqual(len(profile["production_rows"]), 3)
        self.assertEqual(len(profile["material_options"]), 2)

        row = self.kernel.products.get(product_id)
        ledger = json.loads(row["sales_profile_ledger_json"])
        flattened = json.loads(row["sales_profiles_json"])
        self.assertEqual(len(ledger), 1)
        self.assertEqual(len(flattened), 6)
        self.assertEqual(
            {
                (item["weight_grams"], item["material"], item["color"])
                for item in flattened
            },
            {
                (80, "PLA", "سفید"),
                (80, "PETG", "مشکی"),
                (95, "PLA", "سفید"),
                (95, "PETG", "مشکی"),
                (110, "PLA", "سفید"),
                (110, "PETG", "مشکی"),
            },
        )
        self.assertGreater(int(row["price_max"] or 0), 0)

    def test_product_page_has_description_and_real_sorting(self):
        window = MainWindow(self.kernel)
        try:
            headers = tuple(window.products_page.model.headers)
            self.assertIn("عنوان فارسی", headers)
            self.assertIn("عنوان اصلی / انگلیسی", headers)
            self.assertIn("توضیح", headers)
            self.assertTrue(window.products_page.table.isSortingEnabled())
            self.assertGreaterEqual(window.products_page.sort_combo.count(), 5)
        finally:
            window.close()

    def test_image_stage_uses_four_column_cards_with_size_and_seo_facts(self):
        product_id = self._product_id()
        local_dir = Path(self.temporary.name) / "product-images"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        image_path = image_dir / "source.jpg"
        Image.new("RGB", (640, 480), "white").save(image_path, format="JPEG")

        image_url = "https://example.com/media/product-1.jpg"
        (local_dir / "page_extract.json").write_text(
            json.dumps(
                {
                    "images": [
                        {
                            "url": image_url,
                            "local_file": str(image_path),
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        self.db.update_product(
            product_id,
            {
                "local_dir": str(local_dir),
                "images_json": json.dumps([image_url]),
                "selected_images_json": json.dumps([image_url]),
                "primary_image_url": image_url,
                "image_alt_texts_json": json.dumps(["استند کیک سه‌بعدی"]),
            },
        )

        window = MainWindow(self.kernel)
        try:
            window.open_product(product_id)
            wizard = window.wizard_page
            grid = wizard.image_grid
            self.assertEqual(grid.columns, 4)
            self.assertEqual(len(grid.cards), 1)

            item = grid.cards[0].item
            self.assertEqual(item["width"], 640)
            self.assertEqual(item["height"], 480)
            self.assertGreater(item["bytes"], 0)
            self.assertEqual(item["alt_text"], "استند کیک سه‌بعدی")
            self.assertIn("640×480 px", grid.cards[0].facts.text())
            self.assertTrue(wizard.image_slider_enabled.isEnabled())
        finally:
            window.close()

    def test_product_ai_exposes_only_link_and_saved_data_modes(self):
        window = MainWindow(self.kernel)
        try:
            modes = [
                str(window.wizard_page.ai_source.itemData(index))
                for index in range(window.wizard_page.ai_source.count())
            ]
            self.assertEqual(modes, ["link", "data"])
        finally:
            window.close()

    def test_content_source_slider_and_publish_editors_are_present(self):
        window = MainWindow(self.kernel)
        try:
            window.open_product(self._product_id())
            wizard = window.wizard_page
            self.assertTrue(wizard.seo_title_fa.isEnabled())
            self.assertTrue(wizard.description_fa.isEnabled())
            self.assertTrue(wizard.author_name.isEnabled())
            self.assertTrue(wizard.license_name.isEnabled())
            self.assertTrue(wizard.technical_summary.isEnabled())
            self.assertTrue(wizard.slider_enabled.isEnabled())
            self.assertTrue(wizard.slider_title.isEnabled())
            self.assertTrue(wizard.slider_sort.isEnabled())
            self.assertTrue(wizard.publish_product.isEnabled())
            self.assertEqual(wizard.stack.count(), 7)
        finally:
            window.close()

    def test_stage_stepper_uses_red_pending_green_state_contract(self):
        statuses = self.kernel.stages.statuses(self._product_id())
        self.assertEqual(len(statuses), 7)
        self.assertTrue(all(item["icon"] in {"❌", "◌", "✅"} for item in statuses))

        window = MainWindow(self.kernel)
        try:
            window.open_product(self._product_id())
            self.assertEqual(window.wizard_page.stepper.list.count(), 7)
            text = window.wizard_page.stepper.list.item(0).text()
            self.assertTrue(text.startswith(("❌", "◌", "✅")))
        finally:
            window.close()

    def test_provider_hub_and_site_connection_are_restored_in_settings(self):
        window = MainWindow(self.kernel)
        try:
            settings = window.settings_page
            providers = {
                str(settings.provider.itemData(index))
                for index in range(settings.provider.count())
            }
            self.assertTrue({"avalai", "openrouter", "google", "openai"}.issubset(providers))
            self.assertTrue(settings.model.isEditable())
            self.assertIn("تست", settings.test_ai_btn.text())
            self.assertIn("مدل", settings.load_models_btn.text())
            self.assertIn("FTP", settings.test_ftp_btn.text())
            self.assertIn("Bridge", settings.test_bridge_btn.text())
            self.assertEqual(settings.site_url.text(), "https://3dprinthub.ir")
            self.assertEqual(settings.ftp_host.text(), "ftp.3dprinthub.ir")
        finally:
            window.close()

    def test_openrouter_selected_model_test_is_one_fast_request(self):
        calls = []

        def fake_request(url, key, **kwargs):
            calls.append((url, kwargs))
            return {
                "id": "generation-test",
                "model": kwargs.get("model"),
                "choices": [{"message": {"content": "آماده"}}],
            }

        with patch.object(ai_providers, "_json_request", side_effect=fake_request):
            client = AIProviderClient(
                "openrouter",
                "dummy-openrouter-key",
                "openai/gpt-5-mini",
            )
            result = client.test_connection()

        self.assertEqual(result["model"], "openai/gpt-5-mini")
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0][0].endswith("/chat/completions"))
        payload = calls[0][1]["payload"]
        self.assertEqual(payload["provider"]["sort"], "latency")
        self.assertTrue(payload["provider"]["allow_fallbacks"])

    def test_openrouter_structured_content_routes_for_latency_without_model_catalog(self):
        calls = []

        def fake_request(url, key, **kwargs):
            calls.append((url, kwargs))
            return {
                "id": "generation-content",
                "model": kwargs.get("model"),
                "choices": [{"message": {"content": "{}"}}],
            }

        with patch.object(ai_providers, "_json_request", side_effect=fake_request):
            client = AIProviderClient(
                "openrouter",
                "dummy-openrouter-key",
                "openai/gpt-5-mini",
            )
            selected = client.choose_model("openai/gpt-5-mini")
            client._chat(
                selected,
                [{"role": "user", "content": "test"}],
                operation="structured_content",
            )

        self.assertEqual(len(calls), 1)
        payload = calls[0][1]["payload"]
        self.assertEqual(payload["model"], "openai/gpt-5-mini")
    def test_openrouter_structured_content_routes_for_latency_without_model_catalog(self):
        calls = []

        def fake_request(url, key, **kwargs):
            calls.append((url, kwargs))
            return {
                "id": "generation-content",
                "model": kwargs.get("model"),
                "choices": [{"message": {"content": "{}"}}],
            }

        with patch.object(ai_providers, "_json_request", side_effect=fake_request):
            client = AIProviderClient(
                "openrouter",
                "dummy-openrouter-key",
                "openai/gpt-5-mini",
            )
            selected = client.choose_model("openai/gpt-5-mini")
            client._chat(
                selected,
                [{"role": "user", "content": "test"}],
                operation="structured_content",
            )

        self.assertEqual(len(calls), 1)
        payload = calls[0][1]["payload"]
        self.assertEqual(payload["model"], "openai/gpt-5-mini")

    def test_profile_editor_numeric_widgets_are_ltr_and_costs_visible(self):
        self._add_filaments()
        dialog = ProfileEditorDialog(
            self.kernel.filaments.list(),
            filament_core=self.kernel.filaments,
        )
        try:
            self.assertEqual(
                dialog.length.layoutDirection(),
                Qt.LayoutDirection.LeftToRight,
            )
            self.assertGreaterEqual(dialog.length.minimumWidth(), 150)
            self.assertIsInstance(
                dialog.production.cellWidget(0, 0),
                QDoubleSpinBox,
            )
            self.assertIsInstance(
                dialog.production.cellWidget(0, 2),
                QSpinBox,
            )
            headers = [
                dialog.filament_table.horizontalHeaderItem(i).text()
                for i in range(dialog.filament_table.columnCount())
            ]
            for expected in (
                "فروش رول",
                "چاپ/ساعت",
                "نظارت/ساعت",
                "پیش‌گرم h",
                "پیش‌گرم/ساعت",
                "قیمت قطعی محصول",
            ):
                self.assertIn(expected, headers)
            self.assertEqual(FIXED_PRICE_COLUMN, 12)
            self.assertTrue(dialog.edit_filament_btn.isEnabled())
        finally:
            dialog.close()

    def test_main_window_reports_full_parity_contract(self):
        window = MainWindow(self.kernel)
        try:
            contract = window.structural_contract()
            self.assertIn("commerce", contract["core_names"])
            self.assertIn("providers", contract["core_names"])
            self.assertIn("connection", contract["core_names"])
            self.assertTrue(contract["ai_single_engine"])
            self.assertTrue(contract["ai_bound"])
            self.assertTrue(contract["stage_authority_shared"])
            self.assertEqual(window.products_page.tabs.count(), 2)
            self.assertEqual(window.wizard_page.stack.count(), 7)
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
