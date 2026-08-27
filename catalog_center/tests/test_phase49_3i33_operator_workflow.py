from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.db import Database
from app.phase49_3i33_ai_core import (
    AI_MODES,
    ensure_schema,
    makerworld_evidence_from_html,
    sanitize_product_facts,
    structured_ai_text,
)
from app.phase49_3i33_operator_workflow import fixed_price_from_row, image_file_info


ROOT = Path(__file__).resolve().parents[1]


class Phase49I33CoreTests(unittest.TestCase):
    def test_material_color_are_removed_but_weight_time_remain(self):
        clean = sanitize_product_facts(
            {
                "source_title": "Flexi Gecko",
                "material": "PLA",
                "color": "black",
                "estimated_weight_grams": 19,
                "estimated_print_minutes": 84,
                "source_specs": {
                    "layer_height": "0.2 mm",
                    "filament": "PETG",
                    "nested": {"colour_name": "green", "walls": 2},
                },
            }
        )
        self.assertNotIn("material", clean)
        self.assertNotIn("color", clean)
        self.assertNotIn("filament", clean["source_specs"])
        self.assertNotIn("colour_name", clean["source_specs"]["nested"])
        self.assertEqual(clean["estimated_weight_grams"], 19)
        self.assertEqual(clean["estimated_print_minutes"], 84)
        self.assertEqual(clean["source_specs"]["nested"]["walls"], 2)

    def test_makerworld_metrics_and_exact_profile_are_parsed(self):
        next_data = {
            "props": {
                "pageProps": {
                    "model": {
                        "likeCount": 1309,
                        "collectCount": 5529,
                        "downloadCount": 1200,
                        "printCount": 879,
                        "boostCount": 24,
                        "profiles": [
                            {
                                "id": 2179910,
                                "profileName": "0.2mm layer, 2 walls, 5% infill",
                                "predictionSeconds": 5040,
                                "plateCount": 1,
                                "layerHeight": 0.2,
                                "wallCount": 2,
                                "infillPercent": 5,
                                "rating": 4.9,
                            },
                            {
                                "id": 2179911,
                                "profileName": "Optimized Parameters Version",
                                "predictionSeconds": 4680,
                                "plateCount": 1,
                                "rating": 5.0,
                            },
                        ],
                    }
                }
            }
        }
        html = (
            '<script id="__NEXT_DATA__" type="application/json">'
            + json.dumps(next_data)
            + "</script>"
        )
        evidence = makerworld_evidence_from_html(
            html,
            "https://makerworld.com/en/models/2022402-tealight-christmas-tree#profileId-2179910",
        )
        self.assertEqual(evidence["like_count"], 1309)
        self.assertEqual(evidence["save_count"], 5529)
        self.assertEqual(evidence["download_count"], 1200)
        self.assertEqual(evidence["print_count"], 879)
        self.assertEqual(evidence["boost_count"], 24)
        self.assertEqual(evidence["print_profiles"][0]["id"], "2179910")
        self.assertEqual(evidence["print_profiles"][0]["layer_height_mm"], 0.2)
        self.assertEqual(evidence["estimated_print_minutes"], 84.0)

    def test_structured_ai_text_never_contains_operator_material_color(self):
        text = structured_ai_text(
            "https://example.com/model",
            {
                "source_description": "A useful object",
                "material": "PLA",
                "color": "red",
                "estimated_weight_grams": 22,
            },
            {"like_count": 10},
        )
        self.assertIn("22", text)
        self.assertIn("10", text)
        self.assertNotIn("PLA", text)
        self.assertNotIn("red", text)
        self.assertIn("متریال و رنگ عمداً حذف شده‌اند", text)

    def test_exact_operator_ai_surface_has_four_modes(self):
        self.assertEqual(list(AI_MODES), ["link", "data", "screenshot", "repair"])
        self.assertIn("لینک", AI_MODES["link"])
        self.assertIn("دیتای", AI_MODES["data"])
        self.assertIn("اسکرین", AI_MODES["screenshot"])
        self.assertIn("رفع نقص", AI_MODES["repair"])

    def test_desktop_schema_is_additive(self):
        with tempfile.TemporaryDirectory() as temporary:
            db = Database(Path(temporary) / "catalog.sqlite3")
            try:
                ensure_schema(db)
                columns = {
                    row["name"]
                    for row in db.conn.execute("PRAGMA table_info(products)")
                }
                for field in (
                    "source_save_count",
                    "source_boost_count",
                    "source_print_count",
                    "source_print_profiles_json",
                    "source_page_screenshot_path",
                    "ai_last_mode",
                    "ai_last_completed_at",
                ):
                    self.assertIn(field, columns)
            finally:
                db.close()


class Phase49I33UIContractTests(unittest.TestCase):
    def test_quick_price_only_represents_fixed_policy(self):
        self.assertEqual(
            fixed_price_from_row(
                {
                    "pricing_strategy": "fixed",
                    "price_min": 500000,
                    "price_max": 500000,
                    "final_price": 500000,
                    "price_is_final": 1,
                }
            ),
            "500000",
        )
        self.assertEqual(
            fixed_price_from_row(
                {
                    "pricing_strategy": "dynamic",
                    "price_min": 300000,
                    "price_max": 600000,
                    "final_price": 500000,
                    "price_is_final": 0,
                }
            ),
            "",
        )

    def test_image_info_reports_dimensions_ratio_size(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "sample.png"
            Image.new("RGB", (1200, 800), "white").save(path)
            text = image_file_info(str(path))
            self.assertIn("1200×800px", text)
            self.assertIn("3:2", text)
            self.assertIn("PNG", text)

    def test_source_contract_contains_explicit_refresh_and_four_ai_paths(self):
        source = (ROOT / "app" / "phase49_3i33_operator_workflow.py").read_text(encoding="utf-8")
        core = (ROOT / "app" / "phase49_3i33_ai_core.py").read_text(encoding="utf-8")
        self.assertIn("suppress_global_products_refresh", source)
        self.assertIn("app_class._phase49_3i29_flush_products_refresh = no_auto_flush", source)
        self.assertIn("ثبت نهایی محصول و بروزرسانی همان کارت", source)
        self.assertIn("قیمت قطعی فروش (تومان)", source)
        self.assertIn("دریافت اسکرین‌شات از صفحه محصول", source)
        self.assertIn("آوانویسی", core)
        self.assertIn('result["material_recommendations"] = []', core)


if __name__ == "__main__":
    unittest.main()
