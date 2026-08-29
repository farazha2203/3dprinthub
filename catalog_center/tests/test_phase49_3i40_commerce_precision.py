from __future__ import annotations

import unittest

from app.phase49_3i40_commerce_precision import (
    apply_product_fixed_prices,
    color_preview_hex,
    merge_offer_scope,
    readiness_display,
)


def offer(brand, material, color, **extra):
    return {
        "manufacturer": brand,
        "brand": brand,
        "material": material,
        "color": color,
        "roll_weight_grams": 1000,
        "stock_roll_count": 3,
        "sale_price_per_roll": 3_000_000,
        **extra,
    }


class Phase493I40CommercePrecisionTests(unittest.TestCase):
    def test_commit_current_filter_preserves_other_manufacturer_offers(self):
        bambu_white = offer("Bambu Lab", "PLA", "White", fixed_product_price=900_000)
        bambu_black = offer("Bambu Lab", "PLA", "Black", fixed_product_price=910_000)
        esun_white = offer("eSUN", "PLA", "White", fixed_product_price=1_050_000)

        existing = [bambu_white, esun_white]
        visible = [bambu_white, bambu_black]
        selected = [bambu_black]
        merged = merge_offer_scope(existing, visible, selected)

        keys = {(item["brand"], item["material"], item["color"]) for item in merged}
        self.assertEqual(keys, {("Bambu Lab", "PLA", "Black"), ("eSUN", "PLA", "White")})
        by_key = {(item["brand"], item["color"]): item for item in merged}
        self.assertEqual(by_key[("eSUN", "White")]["fixed_product_price"], 1_050_000)
        self.assertEqual(by_key[("Bambu Lab", "Black")]["fixed_product_price"], 0)

    def test_deselect_all_current_scope_clears_only_that_scope(self):
        bambu = offer("Bambu Lab", "PLA", "White")
        esun = offer("eSUN", "PLA", "Multicolor")
        merged = merge_offer_scope([bambu, esun], [bambu], [])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["brand"], "eSUN")

    def test_product_fixed_price_changes_only_selected_product_offer_snapshot(self):
        global_offer = offer("Bambu Lab", "PLA", "White", sale_price_per_roll=3_600_000)
        product_offer = dict(global_offer)
        updated = apply_product_fixed_prices([product_offer], {
            ("bambu lab", "pla", "white"): 950_000,
        })
        self.assertEqual(updated[0]["fixed_product_price"], 950_000)
        self.assertEqual(updated[0]["sale_price_per_roll"], 3_600_000)
        self.assertNotIn("fixed_product_price", global_offer)

    def test_color_preview_uses_hex_then_name_fallback(self):
        self.assertEqual(color_preview_hex({"color": "صورتی", "hex": "#ABCDEF"}), "#ABCDEF")
        self.assertEqual(color_preview_hex({"color": "صورتی"}), "#EC407A")
        self.assertEqual(color_preview_hex({"color": "آبی آسمانی"}), "#1E88E5")
        self.assertEqual(color_preview_hex({"color": "رنگ ناشناخته"}), "#D9D9D9")

    def test_readiness_display_does_not_count_finalize_only_as_data_error(self):
        state = {
            "stages": {
                "quick": {"data_ready": True, "missing_data": []},
                "commerce": {"data_ready": False, "missing_data": ["حداقل یک Offer برند/فیلامنت/رنگ ثبت‌شده"]},
                "images": {"data_ready": True, "missing_data": []},
                "content": {"data_ready": True, "missing_data": []},
                "specs": {"data_ready": False, "missing_data": ["مجوز تجاری مجاز"]},
                "slider": {"data_ready": True, "missing_data": []},
                "publish": {"data_ready": True, "missing_data": []},
            }
        }
        row = {"operator_stage_locks_json": "{}"}
        result = readiness_display(state, row)
        self.assertEqual(result["data_defect_count"], 2)
        self.assertEqual(
            result["data_defects"],
            [
                "۲. سفارش، قیمت و گزینه‌ها: حداقل یک Offer برند/فیلامنت/رنگ ثبت‌شده",
                "۵. منبع و مجوز: مجوز تجاری مجاز",
            ],
        )
        self.assertEqual(set(result["pending_finalization"]), {"quick", "images", "content", "slider", "publish"})

    def test_locked_complete_stage_is_not_pending_finalization(self):
        state = {
            "stages": {
                key: {"data_ready": True, "missing_data": []}
                for key in ("quick", "commerce", "images", "content", "specs", "slider", "publish")
            }
        }
        row = {"operator_stage_locks_json": '{"content":{"locked":true},"commerce":{"locked":true}}'}
        result = readiness_display(state, row)
        self.assertEqual(result["data_defect_count"], 0)
        self.assertNotIn("content", result["pending_finalization"])
        self.assertNotIn("commerce", result["pending_finalization"])
        self.assertIn("quick", result["pending_finalization"])


if __name__ == "__main__":
    unittest.main()
