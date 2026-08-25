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
                    "homepage_slider_title_fa",
                    "homepage_slider_description_fa",
                    "homepage_slider_alt_text",
                    "homepage_slider_button_text",
                    "homepage_slider_focus_keyword",
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
    def test_v87_workspace_exposes_requested_operator_controls(self):
        source = (ROOT / "app" / "product_workspace_v87.py").read_text(encoding="utf-8")
        final_source = (ROOT / "app" / "epic49_product_studio_final.py").read_text(encoding="utf-8")
        v871_source = (ROOT / "app" / "product_workspace_v871.py").read_text(encoding="utf-8")
        combined = source + "\n" + final_source + "\n" + v871_source
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
            "محتوای اختصاصی اسلایدر صفحه اول",
            "انتخاب برای اسلایدر",
        ]:
            self.assertIn(marker, combined)

    def test_manual_images_are_copied_and_use_local_scheme(self):
        source = (ROOT / "app" / "product_studio.py").read_text(encoding="utf-8")
        self.assertIn("def add_local_images", source)
        self.assertIn("local://", source)
        self.assertIn("shutil.copy2", source)

    def test_current_release_and_resilient_staged_exe_build_are_enabled(self):
        from app.version import APP_VERSION
        self.assertEqual(APP_VERSION, "8.8.1")
        builder = (ROOT / "build_portable_exe.py").read_text(encoding="utf-8")
        self.assertIn("staging_dir", builder)
        self.assertIn("except PermissionError", builder)
        self.assertIn("stable_exe_updated", builder)
        self.assertIn("--portable-verify", builder)
        self.assertIn("--portable-browser-smoke", builder)

    def test_workspace_avoids_pack_grid_collision_in_commerce_page(self):
        source = (ROOT / "app" / "product_workspace_v87.py").read_text(encoding="utf-8")
        start = source.index("def _commerce_ui")
        end = source.index("def select_section", start)
        method = source[start:end]
        self.assertIn("panel.grid", method)
        self.assertNotIn("panel.pack", method)
        self.assertIn("super(Epic49ProductStudio, self)._commerce_ui()", method)


if __name__ == "__main__":
    unittest.main()
