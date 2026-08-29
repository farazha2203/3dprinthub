from __future__ import annotations

import unittest

from app.epic49_desktop_schema import normalize_material_color_options
from app.phase49_3i33_ai_core import source_screenshot_viewport_height
from app.phase49_3i35_operator_ledger import flatten_ledger_profiles
from app.phase49_3i39_professional_commerce import (
    formula_price_breakdown,
    offer_display,
    validate_profile_identity,
)


class Phase493I39ProfessionalCommerceTests(unittest.TestCase):
    def test_offer_normalization_keeps_brand_color_rates_preheat_image_and_fixed_product_price(self):
        offers = normalize_material_color_options([{
            "material": "PLA",
            "brand": "Bambu Lab",
            "manufacturer": "Bambu Lab",
            "color": "سفید",
            "hex": "#F5F5F5",
            "roll_weight_grams": 1000,
            "stock_roll_count": 3,
            "sale_price_per_roll": 3_600_000,
            "print_hourly_rate": 150_000,
            "supervision_hourly_rate": 50_000,
            "preheat_hours": 24,
            "preheat_temperature_c": 70,
            "preheat_hourly_rate": 30_000,
            "filament_image_url": "https://example.com/bambu-pla-white.webp",
            "fixed_product_price": 950_000,
        }])
        self.assertEqual(len(offers), 1)
        offer = offers[0]
        self.assertEqual(offer["brand"], "Bambu Lab")
        self.assertEqual(offer["manufacturer"], "Bambu Lab")
        self.assertEqual(offer["color"], "سفید")
        self.assertEqual(offer["stock_roll_count"], 3)
        self.assertEqual(offer["print_hourly_rate"], 150000)
        self.assertEqual(offer["supervision_hourly_rate"], 50000)
        self.assertEqual(offer["preheat_hours"], 24)
        self.assertEqual(offer["preheat_temperature_c"], 70)
        self.assertEqual(offer["preheat_hourly_rate"], 30000)
        self.assertEqual(offer["fixed_product_price"], 950000)
        self.assertIn("Bambu Lab-PLA-سفید", offer_display(offer))

    def test_formula_price_is_exact_offer_specific_and_includes_preheat(self):
        row = {
            "weight_grams": 100,
            "support_weight_grams": 10,
            "print_time_minutes": 60,
        }
        bambu = {
            "roll_weight_grams": 1000,
            "sale_price_per_roll": 3_600_000,
            "print_hourly_rate": 150_000,
            "supervision_hourly_rate": 50_000,
            "preheat_hours": 0,
            "preheat_hourly_rate": 0,
        }
        esun_cf = {
            "roll_weight_grams": 1000,
            "sale_price_per_roll": 4_000_000,
            "print_hourly_rate": 170_000,
            "supervision_hourly_rate": 60_000,
            "preheat_hours": 24,
            "preheat_temperature_c": 70,
            "preheat_hourly_rate": 30_000,
        }
        first = formula_price_breakdown(bambu, row, support_multiplier=2, assembly_fee=10_000)
        second = formula_price_breakdown(esun_cf, row, support_multiplier=2, assembly_fee=10_000)
        self.assertEqual(first["material_cost"], 432000)
        self.assertEqual(first["print_cost"], 150000)
        self.assertEqual(first["supervision_cost"], 50000)
        self.assertEqual(first["preheat_cost"], 0)
        self.assertEqual(first["total"], 642000)
        self.assertEqual(second["preheat_cost"], 720000)
        self.assertGreater(second["total"], first["total"])

    def test_profile_identity_rejects_duplicate_name_size_and_dimensions(self):
        ledger = [{
            "key": "p20",
            "name": "سایز 20",
            "size_label": "20",
            "part_length_cm": 20,
            "part_width_cm": 20,
            "part_height_cm": 13,
            "production_rows": [{"weight_grams": 100, "print_time_minutes": 60}],
        }]
        with self.assertRaisesRegex(ValueError, "نام"):
            validate_profile_identity(
                ledger,
                name="سایز 20",
                size_label="30",
                length_cm=30,
                width_cm=30,
                height_cm=15,
            )
        with self.assertRaisesRegex(ValueError, "سایز"):
            validate_profile_identity(
                ledger,
                name="پروفایل جدید",
                size_label="20",
                length_cm=30,
                width_cm=30,
                height_cm=15,
            )
        with self.assertRaisesRegex(ValueError, "ابعاد"):
            validate_profile_identity(
                ledger,
                name="پروفایل جدید",
                size_label="30",
                length_cm=20,
                width_cm=20,
                height_cm=13,
            )
        validate_profile_identity(
            ledger,
            name="سایز 30",
            size_label="30",
            length_cm=30,
            width_cm=30,
            height_cm=15,
        )

    def test_flat_profile_snapshots_dimensions_but_fixed_price_belongs_to_each_offer(self):
        ledger = [{
            "key": "cake-20",
            "name": "پایه کیک 20",
            "size_label": "20",
            "part_length_cm": 20,
            "part_width_cm": 20,
            "part_height_cm": 13,
            "pricing_strategy": "fixed",
            "production_rows": [{
                "weight_grams": 300,
                "print_time_minutes": 200,
                "support_weight_grams": 20,
            }],
            "material_options": [
                {
                    "material": "PLA",
                    "brand": "Bambu Lab",
                    "manufacturer": "Bambu Lab",
                    "color": "White",
                    "fixed_product_price": 900000,
                },
                {
                    "material": "PLA",
                    "brand": "eSUN",
                    "manufacturer": "eSUN",
                    "color": "White",
                    "fixed_product_price": 1050000,
                },
            ],
        }]
        flat = flatten_ledger_profiles(ledger)
        self.assertEqual(len(flat), 2)
        self.assertEqual({item["fixed_price"] for item in flat}, {900000, 1050000})
        self.assertEqual({item["part_length_cm"] for item in flat}, {20})
        self.assertEqual({item["part_width_cm"] for item in flat}, {20})
        self.assertEqual({item["part_height_cm"] for item in flat}, {13})
        self.assertEqual({item["brand"] for item in flat}, {"Bambu Lab", "eSUN"})

    def test_product_screenshot_is_top_viewport_not_full_page(self):
        self.assertEqual(source_screenshot_viewport_height(1658, 4000), 961)
        self.assertEqual(source_screenshot_viewport_height(1200, 800), 800)
        self.assertLess(source_screenshot_viewport_height(1920, 5000), 5000)


if __name__ == "__main__":
    unittest.main()
