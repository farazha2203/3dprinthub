from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.db import Database
from app.phase49_3i34_profile_matrix import (
    SELECTION_MODES,
    duplicate_profile,
    ensure_schema,
    normalize_profile,
    profile_price_range,
    seed_profile_from_row,
)


ROOT = Path(__file__).resolve().parents[1]


class Phase49I34ProfileMatrixTests(unittest.TestCase):
    def test_normalize_profile_keeps_independent_size_weight_price_dimensions(self):
        profile = normalize_profile(
            {
                "key": "cake-30-200",
                "name": "۳۰ سانتی - ۲۰۰ گرم",
                "size_label": "30 سانتی‌متر",
                "weight_grams": "200",
                "material_weight_grams": "190",
                "print_time_minutes": "180",
                "fixed_price": "850,000",
                "part_length_cm": "30",
                "part_width_cm": "30",
                "part_height_cm": "10",
                "build_profile": "reinforced",
                "material": "PETG",
                "color": "سفید",
                "quality": "استاندارد",
            },
            1,
        )
        self.assertEqual(profile["key"], "cake-30-200")
        self.assertEqual(profile["size_label"], "30 سانتی‌متر")
        self.assertEqual(profile["weight_grams"], 200)
        self.assertEqual(profile["material_weight_grams"], 190)
        self.assertEqual(profile["print_time_minutes"], 180)
        self.assertEqual(profile["fixed_price"], 850000)
        self.assertEqual(profile["part_length_cm"], 30)
        self.assertEqual(profile["build_profile"], "reinforced")

    def test_clone_is_profile1_copy_with_new_identity(self):
        source = normalize_profile(
            {
                "key": "profile-one",
                "name": "پروفایل ۱",
                "size_label": "20 سانتی‌متر",
                "weight_grams": 100,
                "fixed_price": 350000,
                "part_length_cm": 20,
                "part_width_cm": 20,
                "part_height_cm": 8,
                "is_default": True,
            },
            1,
        )
        clone = duplicate_profile(source, 2)
        self.assertNotEqual(clone["key"], source["key"])
        self.assertEqual(clone["size_label"], source["size_label"])
        self.assertEqual(clone["weight_grams"], source["weight_grams"])
        self.assertEqual(clone["fixed_price"], source["fixed_price"])
        self.assertEqual(clone["part_length_cm"], source["part_length_cm"])
        self.assertFalse(clone["is_default"])
        self.assertIn("کپی", clone["name"])

    def test_price_range_comes_only_from_profile_fixed_prices(self):
        profiles = [
            {"fixed_price": 650000},
            {"fixed_price": 350000},
            {"fixed_price": 850000},
            {"fixed_price": 0},
        ]
        self.assertEqual(profile_price_range(profiles), (350000, 850000))

    def test_desktop_schema_is_additive_and_persistent(self):
        with tempfile.TemporaryDirectory() as temporary:
            db = Database(Path(temporary) / "catalog.sqlite3")
            try:
                ensure_schema(db)
                columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
                for name in (
                    "sales_profiles_json",
                    "sales_profile_selection_mode",
                    "sales_profile_selector_label",
                ):
                    self.assertIn(name, columns)
                ensure_schema(db)
                self.assertEqual(
                    db.conn.execute(
                        "SELECT COUNT(*) FROM pragma_table_info('products') WHERE name='sales_profiles_json'"
                    ).fetchone()[0],
                    1,
                )
            finally:
                db.close()

    def test_seed_profile_uses_existing_weight_time_price_without_losing_product(self):
        row = {
            "estimated_weight_grams": 150,
            "estimated_print_minutes": 120,
            "final_price": 450000,
            "price_min": 450000,
        }
        profile = seed_profile_from_row(row)
        self.assertEqual(profile["weight_grams"], 150)
        self.assertEqual(profile["print_time_minutes"], 120)
        self.assertEqual(profile["fixed_price"], 450000)
        self.assertTrue(profile["is_default"])

    def test_size_weight_modes_cover_requested_customer_flow(self):
        for mode in (
            "size_weight",
            "weight_size",
            "size_weight_build",
            "size_build_weight",
        ):
            self.assertIn(mode, SELECTION_MODES)

    def test_selected_profile_loader_uses_installed_namespaced_lookup(self):
        from app.phase49_3i34_profile_matrix import install_workspace

        class Base:
            def __init__(self, *_args, **_kwargs):
                pass

            def reload(self):
                return True

            def save(self, silent=False):
                return True

        class Tree:
            def selection(self):
                return ("profile-1",)

        class Value:
            def __init__(self):
                self.value = None

            def set(self, value):
                self.value = value

        install_workspace(Base)
        workspace = object.__new__(Base)
        workspace._phase49_3i34_tree = Tree()
        workspace._phase49_3i34_profiles = [{
            "key": "profile-1",
            "is_default": True,
            "is_active": True,
            "track_inventory": False,
        }]
        workspace._phase49_3i34_vars = {}
        workspace._phase49_3i34_default_var = Value()
        workspace._phase49_3i34_active_var = Value()
        workspace._phase49_3i34_track_var = Value()
        workspace._phase49_3i34_selected_key = ""

        workspace._phase49_3i34_load_selected()

        self.assertEqual(workspace._phase49_3i34_selected_key, "profile-1")
        self.assertEqual(workspace._phase49_3i34_default_var.value, 1)
        self.assertEqual(workspace._phase49_3i34_active_var.value, 1)
        self.assertEqual(workspace._phase49_3i34_track_var.value, 0)

    def test_final_composition_and_batch_transport_are_present(self):
        pricing = (ROOT / "app" / "phase49_3i_pricing_modes.py").read_text(encoding="utf-8")
        matrix = (ROOT / "app" / "phase49_3i34_profile_matrix.py").read_text(encoding="utf-8")
        main = (ROOT / "app" / "main.py").read_text(encoding="utf-8")

        self.assertIn("_install_phase49_3i34_workspace(workspace_class)", pricing)
        self.assertIn("کپی پروفایل انتخابی", matrix)
        self.assertIn("sales_profiles_json", matrix)
        self.assertIn("سایز ← وزن", matrix)
        self.assertIn('editorial={k:r[k] for k in r.keys()', main)
        self.assertIn('editorial["desktop_product_id"]', main)


if __name__ == "__main__":
    unittest.main()
