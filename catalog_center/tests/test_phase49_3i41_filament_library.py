from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.db import Database
from app.epic49_desktop_schema import add_available_material_color, ensure_epic49_desktop_schema
from app.phase49_3i41_filament_library import (
    _active_inventory,
    _choice_lists,
    _material_groups,
    _sync_payload,
)


ROOT = Path(__file__).resolve().parents[1]


class Phase493I41FilamentLibraryTests(unittest.TestCase):
    def test_library_groups_filaments_by_material_and_reuses_company_material_choices(self):
        with tempfile.TemporaryDirectory() as temporary:
            db = Database(Path(temporary) / "catalog.sqlite3")
            try:
                ensure_epic49_desktop_schema(db)
                for color in ("سفید", "مشکی", "صورتی", "آبی", "قرمز"):
                    add_available_material_color(
                        db,
                        "PLA",
                        color,
                        brand_name="Bambu Lab",
                        manufacturer_name="Bambu Lab",
                        sale_price_per_roll=4_000_000,
                    )
                for color in ("شفاف", "دودی", "سبز"):
                    add_available_material_color(
                        db,
                        "PETG",
                        color,
                        brand_name="eSUN",
                        manufacturer_name="eSUN",
                        sale_price_per_roll=4_500_000,
                    )

                inventory = _active_inventory(db)
                groups = _material_groups(inventory)
                self.assertEqual(len(groups["PLA"]), 5)
                self.assertEqual(len(groups["PETG"]), 3)

                choices = _choice_lists(db)
                self.assertEqual(choices["materials"], ["PETG", "PLA"])
                self.assertEqual(set(choices["brands"]), {"Bambu Lab", "eSUN"})
                self.assertEqual(set(choices["manufacturers"]), {"Bambu Lab", "eSUN"})
            finally:
                db.close()

    def test_site_sync_payload_keeps_weight_stock_brand_rates_and_preheat(self):
        payload = _sync_payload({
            "material": "PLA",
            "brand": "Bambu Lab",
            "manufacturer": "Bambu Lab",
            "color": "صورتی",
            "roll_weight_grams": 1000,
            "stock_roll_count": 2.5,
            "sale_price_per_roll": 4_200_000,
            "print_hourly_rate": 160_000,
            "supervision_hourly_rate": 50_000,
            "preheat_hours": 8,
            "preheat_temperature_c": 45,
            "preheat_hourly_rate": 30_000,
        })
        self.assertEqual(payload["material"], "PLA")
        self.assertEqual(payload["brand"], "Bambu Lab")
        self.assertEqual(payload["stock_roll_count"], 2.5)
        self.assertEqual(payload["sale_price_per_roll"], 4_200_000)
        self.assertEqual(payload["print_hourly_rate"], 160_000)
        self.assertEqual(payload["preheat_hourly_rate"], 30_000)

    def test_main_navigation_and_product_stage_expose_clear_filament_library_contract(self):
        shell = (ROOT / "app" / "ux87_shell.py").read_text(encoding="utf-8")
        phase = (ROOT / "app" / "phase49_3i41_filament_library.py").read_text(encoding="utf-8")
        pricing = (ROOT / "app" / "phase49_3i39_professional_commerce.py").read_text(encoding="utf-8")
        launch = (ROOT / "launch.py").read_text(encoding="utf-8")

        self.assertIn('("filaments", "فیلامنت‌ها", "products")', shell)
        self.assertIn("کتابخانه مرکزی Filament", phase)
        self.assertIn("Filamentهای موجود — تفکیک بر اساس نوع", phase)
        self.assertIn("انتخاب‌های این محصول", phase)
        self.assertIn("☑", phase)
        self.assertIn("☐", phase)
        self.assertIn("مدیریت / تعریف Filament در کتابخانه اصلی", phase)
        self.assertIn("state=\"normal\"", phase)
        self.assertNotIn("fixed_product", phase)
        self.assertIn("_phase49_3i41_selected_draft_offers", pricing)
        self.assertIn("EPIC49_3I41_FILAMENT_LIBRARY=ENABLED", launch)

    def test_central_editor_preserves_multicolor_fields_and_deactivation_sync_contract(self):
        phase = (ROOT / "app" / "phase49_3i41_filament_library.py").read_text(encoding="utf-8")
        self.assertIn('("color_type", "نوع رنگ")', phase)
        self.assertIn('("secondary_hex", "HEX دوم")', phase)
        self.assertIn('("tertiary_hex", "HEX سوم")', phase)
        self.assertIn('color_type=vars_["color_type"].get()', phase)
        self.assertIn('disabled["_is_active"] = False', phase)
        self.assertIn("_async_site_sync(self, disabled)", phase)

    def test_product_checklist_has_explicit_save_and_no_ctrl_shift_contract(self):
        phase = (ROOT / "app" / "phase49_3i41_filament_library.py").read_text(encoding="utf-8")
        self.assertIn("✓ ثبت انتخاب‌ها روی این محصول", phase)
        self.assertIn("روی نام گروه PLA/PETG کلیک کن", phase)
        self.assertNotIn("Ctrl/Shift", phase)


if __name__ == "__main__":
    unittest.main()
