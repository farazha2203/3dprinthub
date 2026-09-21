import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.db import Database
from app.page_extractor import parse_page_snapshot
from app.phase50_a2w_source_profiles import (
    extract_makerworld_print_profiles,
    refresh_product_source_profiles,
)
from qt6.kernel import build_kernel
from qt6.product_wizard import ProductWizardPage


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
        self.assertEqual(
            [x["color"] for x in by_key["source-mw-3609488"]["material_options"]],
            ["#804003", "#FECC66"],
        )

        second = self.kernel.commerce.import_source_profiles(product_id)
        profiles_again = self.kernel.commerce.profiles(product_id)
        self.assertEqual(second["added"], 0)
        self.assertEqual(second["updated"], 2)
        self.assertEqual(len(profiles_again), 3)
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
