from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.db import Database
from app.epic49_desktop_schema import (
    add_available_material_color,
    ensure_epic49_desktop_schema,
    list_available_material_colors,
    normalize_material_color_options,
)


ROOT = Path(__file__).resolve().parents[1]


class Epic49OperatorDatabaseTests(unittest.TestCase):
    def test_additive_schema_and_material_color_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            db = Database(Path(temporary) / "catalog.sqlite3")
            try:
                ensure_epic49_desktop_schema(db)
                columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
                for name in {
                    "download_image_limit",
                    "price_min",
                    "price_max",
                    "material_color_options_json",
                    "homepage_slider_enabled",
                    "homepage_slider_image_url",
                    "homepage_slider_sort_order",
                }:
                    self.assertIn(name, columns)
                pink = add_available_material_color(db, "PLA", "صورتی", "#ff69b4")
                green = add_available_material_color(db, "PLA", "سبز", "#00aa55")
                rows = list_available_material_colors(db)
                self.assertEqual({row["color_name"] for row in rows}, {"صورتی", "سبز"})
                self.assertEqual(pink["material_name"], "PLA")
                self.assertEqual(green["material_name"], "PLA")
            finally:
                db.close()

    def test_material_color_selection_is_normalized_and_deduplicated(self):
        raw = json.dumps([
            {"material": "PLA", "color": "صورتی", "hex": "#ff69b4"},
            {"material": "pla", "color": "صورتی", "hex": ""},
            {"material": "PETG", "color": "مشکی"},
        ], ensure_ascii=False)
        result = normalize_material_color_options(raw)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["material"], "PLA")
        self.assertEqual(result[0]["color"], "صورتی")
        self.assertEqual(result[1]["material"], "PETG")


class Epic49OperatorUIContractTests(unittest.TestCase):
    def test_final_studio_exposes_requested_operator_controls(self):
        source = (ROOT / "app" / "epic49_product_studio_final.py").read_text(encoding="utf-8")
        for marker in [
            "حداکثر تعداد عکس در هر بازیابی",
            "افزودن عکس از کامپیوتر",
            "حداقل قیمت (تومان)",
            "حداکثر قیمت (تومان)",
            "افزودن متریال/رنگ",
            "نمایش این محصول در اسلایدر صفحه اصلی",
            "عکس اسلایدر",
            "download_image_limit",
            "material_color_options_json",
        ]:
            self.assertIn(marker, source)

    def test_manual_images_are_copied_and_use_local_scheme(self):
        source = (ROOT / "app" / "product_studio.py").read_text(encoding="utf-8")
        self.assertIn("def add_local_images", source)
        self.assertIn("local://", source)
        self.assertIn("shutil.copy2", source)

    def test_86_release_and_resilient_staged_exe_build_are_enabled(self):
        from app.version import APP_VERSION
        self.assertEqual(APP_VERSION, "8.6.0")
        builder = (ROOT / "build_portable_exe.py").read_text(encoding="utf-8")
        self.assertIn("staging_dir", builder)
        self.assertIn("except PermissionError", builder)
        self.assertIn("stable_exe_updated", builder)
        self.assertIn("--portable-verify", builder)


if __name__ == "__main__":
    unittest.main()
