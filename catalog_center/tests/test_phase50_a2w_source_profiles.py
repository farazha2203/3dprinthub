import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtWidgets import QApplication

from app.db import Database
from app.epic49_desktop_schema import add_available_material_color
from app.page_extractor import parse_page_snapshot
from app.phase50_a2w_source_profiles import (
    extract_makerworld_print_profiles,
    refresh_product_source_profiles,
)
from qt6.kernel import build_kernel
from qt6.product_wizard import ProductWizardPage
from qt6.parity_dialogs import ProfileEditorDialog


def makerworld_next_data():
    return {
        "props": {
            "pageProps": {
                "design": {
                    "id": 3190563,
                    "instances": [
                        {
                            "id": 3609481,
                            "profileId": 943581967,
                            "title": "Single Color Print Profile",
                            "status": 1,
                            "extention": {"modelInfo": {
                                "compatibility": {
                                    "devModelName": "N2S",
                                    "devProductName": "A1",
                                    "nozzleDiameter": 0.4,
                                },
                                "hasFilamentMixed": False,
                                "projectSettings": {
                                    "layerHeight": "0.16",
                                    "wallLoops": "2",
                                    "sparseInfillDensity": "5%",
                                },
                                "plates": [{
                                    "index": 1,
                                    "prediction": 4814,
                                    "weight": 13,
                                    "filaments": [{
                                        "id": "3",
                                        "type": "PLA",
                                        "color": "#FECC66",
                                        "usedM": "4.27",
                                        "usedG": "13",
                                    }],
                                }],
                            }},
                        },
                        {
                            "id": 3609488,
                            "profileId": 943610448,
                            "title": "Multicolor Print Profile",
                            "status": 1,
                            "extention": {"modelInfo": {
                                "compatibility": {
                                    "devModelName": "N2S",
                                    "devProductName": "A1",
                                    "nozzleDiameter": 0.4,
                                },
                                "hasFilamentMixed": False,
                                "projectSettings": {
                                    "layerHeight": "0.16",
                                    "wallLoops": "2",
                                    "sparseInfillDensity": "5%",
                                },
                                "plates": [{
                                    "index": 1,
                                    "prediction": 15748,
                                    "weight": 50,
                                    "filaments": [
                                        {
                                            "id": "1", "type": "PLA",
                                            "color": "#804003", "usedM": "3.55", "usedG": "11",
                                        },
                                        {
                                            "id": "2", "type": "PLA",
                                            "color": "#FECC66", "usedM": "12.69", "usedG": "39",
                                        },
                                    ],
                                }],
                            }},
                        },
                    ],
                }
            }
        }
    }


class Phase50A2WSourceProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = Database(self.root / "catalog.sqlite3")
        self.db.upsert_source({
            "code": "makerworld",
            "name": "MakerWorld",
            "enabled": 1,
            "methods": ["http"],
            "listing_urls": [],
            "model_url_pattern": "",
            "requires_login": False,
            "reference_only": False,
        })
        self.kernel = build_kernel(self.db)

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def _html(self):
        return (
            "<html><head><script id=\"__NEXT_DATA__\" type=\"application/json\">"
            + json.dumps(makerworld_next_data())
            + "</script></head><body>Print Profile (2)</body></html>"
        )

    def _product(self):
        local_dir = self.root / "product-3190563"
        local_dir.mkdir(parents=True)
        (local_dir / "model_3190563_test.html").write_text(
            self._html(), encoding="utf-8"
        )
        self.db.upsert_product({
            "source_code": "makerworld",
            "external_id": "3190563",
            "source_url": "https://makerworld.com/en/models/3190563-test#profileId-3609481",
            "source_title": "Mini Articulated Skeletal Spinosaurus",
            "title_fa": "اسپینوزور",
            "local_dir": str(local_dir),
            "source_print_profiles_json": "[]",
            "workflow_status": "review",
        })
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("makerworld", "3190563"),
        ).fetchone()
        return int(row["id"])

    def _seed_local_filaments(self):
        add_available_material_color(
            self.db,
            "PLA",
            "White",
            "#FFFFFF",
            brand_name="Bambulab",
            manufacturer_name="Bambulab",
            stock_roll_count=1,
            purchase_price_per_roll=3_500_000,
            sale_price_per_roll=4_500_000,
            print_hourly_rate=150_000,
            supervision_hourly_rate=50_000,
        )
        add_available_material_color(
            self.db,
            "PLA",
            "Black",
            "#111111",
            brand_name="E-Sun",
            manufacturer_name="E-Sun",
            stock_roll_count=2,
            purchase_price_per_roll=3_500_000,
            sale_price_per_roll=4_500_000,
            print_hourly_rate=150_000,
            supervision_hourly_rate=50_000,
        )
        add_available_material_color(
            self.db,
            "PETG",
            "Clear",
            "#DDDDDD",
            brand_name="E-Sun",
            manufacturer_name="E-Sun",
            stock_roll_count=1,
            purchase_price_per_roll=4_500_000,
            sale_price_per_roll=5_500_000,
            print_hourly_rate=150_000,
            supervision_hourly_rate=50_000,
        )

    def test_exact_next_data_profiles_do_not_collapse(self):
        profiles = extract_makerworld_print_profiles(
            makerworld_next_data(),
            source_url="https://makerworld.com/en/models/3190563-test",
        )
        self.assertEqual(len(profiles), 2)
        single, multi = profiles
        self.assertEqual(single["instance_id"], 3609481)
        self.assertEqual(single["profile_id"], 943581967)
        self.assertEqual(single["print_seconds"], 4814)
        self.assertEqual(single["weight_grams"], 13)
        self.assertAlmostEqual(single["print_minutes"], 4814 / 60, places=3)
        self.assertEqual(single["material_families"], ["PLA"])
        self.assertEqual(single["filaments"][0]["color_hex"], "#FECC66")
        self.assertEqual(single["nozzle_diameter_mm"], 0.4)
        self.assertEqual(single["layer_height_mm"], 0.16)

        self.assertEqual(multi["instance_id"], 3609488)
        self.assertEqual(multi["profile_id"], 943610448)
        self.assertEqual(multi["print_seconds"], 15748)
        self.assertEqual(multi["weight_grams"], 50)
        self.assertAlmostEqual(multi["print_minutes"], 15748 / 60, places=3)
        self.assertEqual(
            [(x["color_hex"], x["used_grams"]) for x in multi["filaments"]],
            [("#804003", 11.0), ("#FECC66", 39.0)],
        )
    def test_page_extractor_carries_source_profiles(self):
        next_data = makerworld_next_data()
        page = parse_page_snapshot({
            "source_url": "https://makerworld.com/en/models/3190563-test",
            "final_url": "https://makerworld.com/en/models/3190563-test",
            "title": "Mini Articulated Skeletal Spinosaurus",
            "metas": {},
            "json_ld": [],
            "embedded_json": [json.dumps(next_data)],
            "network_json": [],
            "breadcrumbs": [],
            "spec_rows": [],
            "labeled_sections": [],
            "dom_images": [],
            "picture_sources": [],
            "links": [],
            "body_text": "Print Profile (2)",
        })
        self.assertEqual(len(page.source_print_profiles), 2)
        self.assertEqual(
            [item["instance_id"] for item in page.source_print_profiles],
            [3609481, 3609488],
        )

    def test_cached_refresh_persists_facts_without_touching_sales_ledger(self):
        product_id = self._product()
        self.kernel.commerce.save_profiles(product_id, [{
            "key": "manual-standard",
            "name": "Standard",
            "size_label": "Manual",
            "production_rows": [{
                "weight_grams": 60,
                "print_time_minutes": 180,
                "support_weight_grams": 50,
            }],
            "material_options": [],
        }])
        before = dict(self.db.product(product_id))
        result = refresh_product_source_profiles(
            self.db, product_id, fresh_capture=False
        )
        after = dict(self.db.product(product_id))
        self.assertEqual(result["profile_count"], 2)
        self.assertEqual(
            before["sales_profile_ledger_json"],
            after["sales_profile_ledger_json"],
        )
        self.assertEqual(
            len(json.loads(after["source_print_profiles_json"])),
            2,
        )
    def test_import_preserves_manual_profile_and_is_idempotent(self):
        product_id = self._product()
        self._seed_local_filaments()
        self.kernel.commerce.save_profiles(product_id, [{
            "key": "manual-standard",
            "name": "Standard",
            "size_label": "Manual",
            "production_rows": [{
                "weight_grams": 60,
                "print_time_minutes": 180,
                "support_weight_grams": 50,
            }],
            "material_options": [],
        }])
        refresh_product_source_profiles(self.db, product_id, fresh_capture=False)

        first = self.kernel.commerce.import_source_profiles(product_id)
        profiles = self.kernel.commerce.profiles(product_id)
        self.assertEqual(first["added"], 2)
        self.assertEqual(len(profiles), 3)
        self.assertEqual(profiles[0]["key"], "manual-standard")
        by_key = {item["key"]: item for item in profiles}
        self.assertEqual(
            by_key["source-mw-3609481"]["production_rows"][0]["weight_grams"],
            13,
        )
        self.assertEqual(
            by_key["source-mw-3609481"]["production_rows"][0]["print_time_minutes"],
            80,
        )
        self.assertEqual(
            by_key["source-mw-3609488"]["production_rows"][0]["weight_grams"],
            50,
        )
        self.assertEqual(
            by_key["source-mw-3609488"]["production_rows"][0]["print_time_minutes"],
            262,
        )
        single_options = by_key["source-mw-3609481"]["material_options"]
        multi_options = by_key["source-mw-3609488"]["material_options"]
        self.assertEqual(len(single_options), 2)
        self.assertEqual(len(multi_options), 2)
        self.assertEqual(
            {x["material"] for x in single_options},
            {"PLA"},
        )
        self.assertEqual(
            {x["brand"] for x in single_options},
            {"Bambulab", "E-Sun"},
        )
        self.assertNotIn("PETG", {x["material"] for x in single_options})
        self.assertEqual(first["local_filament_count"], 4)

        dialog = ProfileEditorDialog(
            self.kernel.filaments.list(),
            by_key["source-mw-3609481"],
            filament_core=self.kernel.filaments,
        )
        try:
            self.assertEqual(len(dialog._selected_filaments()), 2)
        finally:
            dialog.close()

        second = self.kernel.commerce.import_source_profiles(product_id)
        profiles_again = self.kernel.commerce.profiles(product_id)
        self.assertEqual(second["added"], 0)
        self.assertEqual(second["updated"], 2)
        self.assertEqual(len(profiles_again), 3)
    def test_full_completion_reuses_source_profiles_filaments_slider_category_and_physical_seo(self):
        product_id = self._product()
        self._seed_local_filaments()
        row = dict(self.db.product(product_id))
        local_dir = Path(row["local_dir"])
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        source_image = image_dir / "01.jpg"
        Image.new("RGB", (640, 640), "orange").save(
            source_image,
            "JPEG",
        )
        image_url = "https://cdn.example.com/spinosaurus-main.jpg"
        (local_dir / "page_extract.json").write_text(
            json.dumps(
                {
                    "images": [
                        {
                            "url": image_url,
                            "local_file": str(source_image),
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        valid_category = next(
            item
            for item in self.kernel.categories.list()
            if item["slug"] != "external-other"
        )
        self.db.update_product(
            product_id,
            {
                "source_category": valid_category["name"],
                "local_category_slug": "external-other",
                "images_json": json.dumps([image_url]),
                "selected_images_json": json.dumps([image_url]),
                "primary_image_url": image_url,
                "image_alt_texts_json": "[]",
                "content_pack_json": json.dumps(
                    {
                        "homepage_slider_seo": {
                            "title_fa": "اسپینوزور مفصلی چاپ سه‌بعدی",
                            "description_fa": "مدل مفصلی دکوراتیو با امکان سفارش رنگ.",
                            "image_alt_fa": "اسپینوزور مفصلی چاپ سه‌بعدی",
                            "button_text_fa": "مشاهده محصول",
                            "focus_keyword_fa": "اسپینوزور چاپ سه‌بعدی",
                        }
                    },
                    ensure_ascii=False,
                ),
                "homepage_slider_enabled": 0,
                "homepage_slider_image_url": "",
                "homepage_slider_title_fa": "",
                "homepage_slider_description_fa": "",
                "homepage_slider_alt_text": "",
                "homepage_slider_button_text": "",
                "homepage_slider_focus_keyword": "",
                "operator_stage_locks_json": json.dumps(
                    {
                        "quick": {"locked": True},
                        "commerce": {"locked": True},
                        "content": {"locked": True},
                        "specs": {"locked": True},
                        "slider": {"locked": True},
                        "publish": {"locked": True},
                    },
                    ensure_ascii=False,
                ),
            },
        )

        self.kernel.stages.prepare_full_product_completion(product_id)
        self.kernel.acquisition.refresh_source_profiles = (
            lambda product_id, fresh_capture=True, progress=None:
            refresh_product_source_profiles(
                self.db,
                product_id,
                fresh_capture=False,
            )
        )
        self.kernel.providers.active = lambda: {
            "provider": "test-provider",
            "model": "test-model",
        }

        result = self.kernel.postprocess_full_product_ai(
            product_id,
            {"requested_source_mode": "link"},
            extended_bulk=True,
        )
        after = dict(self.db.product(product_id))
        profiles = {
            item["key"]: item
            for item in self.kernel.commerce.profiles(product_id)
        }

        self.assertEqual(
            set(profiles),
            {"source-mw-3609481", "source-mw-3609488"},
        )
        for profile in profiles.values():
            options = profile["material_options"]
            self.assertEqual(len(options), 2)
            self.assertEqual(
                {item["material"] for item in options},
                {"PLA"},
            )
            self.assertEqual(
                {item["brand"] for item in options},
                {"Bambulab", "E-Sun"},
            )

        self.assertEqual(
            after["local_category_slug"],
            valid_category["slug"],
        )
        self.assertEqual(int(after["homepage_slider_enabled"] or 0), 0)
        for field in (
            "homepage_slider_image_url",
            "homepage_slider_title_fa",
            "homepage_slider_description_fa",
            "homepage_slider_alt_text",
            "homepage_slider_button_text",
            "homepage_slider_focus_keyword",
        ):
            self.assertTrue(str(after[field] or "").strip(), field)

        physical = dict(result["physical_image_rename"])
        self.assertEqual(physical["selected"], 1)
        self.assertEqual(len(physical["filenames"]), 1)
        physical_name = physical["filenames"][0]
        self.assertTrue(physical_name.endswith("-01.webp"))
        self.assertTrue((image_dir / physical_name).is_file())
        self.assertTrue((local_dir / "source_originals" / "01.jpg").is_file())
        self.assertTrue(result["slider_backfill"]["complete"])
        self.assertFalse(result["slider_backfill"]["membership"])
        self.assertEqual(result["source_profile_import"]["added"], 2)

        locks = json.loads(after["operator_stage_locks_json"])
        self.assertIn("publish", locks)

        standard_result = self.kernel.postprocess_full_product_ai(
            product_id,
            {"requested_source_mode": "link"},
        )
        self.assertNotIn("source_profile_refresh", standard_result)
        self.assertNotIn("source_profile_import", standard_result)
        self.assertNotIn("slider_backfill", standard_result)

    def test_stage2_exposes_source_profile_action(self):
        product_id = self._product()
        refresh_product_source_profiles(self.db, product_id, fresh_capture=False)
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            self.assertEqual(
                page.source_profile_btn.text(),
                "دریافت پروفایل از محصول",
            )
            self.assertIn("Source Profile: 2", page.source_profile_status.text())
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
