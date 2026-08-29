from __future__ import annotations

import threading
import unittest
from pathlib import Path

from app.phase49_3i40_commerce_precision import (
    _CompletionProgressProxy,
    apply_product_fixed_prices,
    color_preview_hex,
    filament_rate_calculation,
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


class _Dialog:
    def __init__(self):
        self.cancelled = threading.Event()
        self.progress = []
        self.events = []

    def set_progress(self, value, message=""):
        self.progress.append((float(value), message))

    def event(self, *args, **kwargs):
        self.events.append((args, kwargs))


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

    def test_filament_rate_calculation_shows_final_roll_basis_and_per_gram_rate(self):
        result = filament_rate_calculation({
            "roll_weight_grams": 1000,
            "sale_price_per_roll": 3_000_000,
            "usd_price_per_roll": 40,
            "usd_fx_rate_toman": 100_000,
        })
        self.assertEqual(result["final_roll_toman"], 4_000_000)
        self.assertEqual(result["rate_per_gram"], 4_000)
        self.assertEqual(result["basis"], "دلار × نرخ ثبت‌شده")

        no_fx = filament_rate_calculation({
            "roll_weight_grams": 1000,
            "sale_price_per_roll": 3_000_000,
            "usd_price_per_roll": 40,
            "usd_fx_rate_toman": 0,
        })
        self.assertEqual(no_fx["final_roll_toman"], 3_000_000)
        self.assertEqual(no_fx["rate_per_gram"], 3_000)
        self.assertEqual(no_fx["basis"], "قیمت فروش هر رول")

    def test_global_editor_exposes_final_rate_calculation_and_filament_labels(self):
        root = Path(__file__).resolve().parents[1]
        source = (root / "app" / "phase49_3i40_commerce_precision.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("محاسبه نرخ نهایی Filament", source)
        self.assertIn("مبلغ نهایی مبنای هر رول", source)
        self.assertIn("نرخ نهایی مصرف", source)
        self.assertIn("ذخیره Filament جهانی", source)
        self.assertNotIn('text="ذخیره Offer جهانی"', source)

    def test_color_preview_uses_hex_then_name_fallback(self):
        self.assertEqual(color_preview_hex({"color": "صورتی", "hex": "#ABCDEF"}), "#ABCDEF")
        self.assertEqual(color_preview_hex({"color": "صورتی"}), "#EC407A")
        self.assertEqual(color_preview_hex({"color": "آبی آسمانی"}), "#1E88E5")
        self.assertEqual(color_preview_hex({"color": "رنگ ناشناخته"}), "#D9D9D9")

    def test_readiness_display_does_not_count_finalize_only_as_data_error(self):
        state = {
            "stages": {
                "quick": {"data_ready": True, "missing_data": []},
                "commerce": {"data_ready": False, "missing_data": ["حداقل یک Filament برند/متریال/رنگ ثبت‌شده"]},
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
                "۲. سفارش، قیمت و گزینه‌ها: حداقل یک Filament برند/متریال/رنگ ثبت‌شده",
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

    def test_visual_tick_is_reserved_for_confirmed_stage(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "app" / "phase49_3i40_commerce_precision.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'icon = "✅" if locked and data_ready else ("◌" if data_ready else "❌")',
            source,
        )
        self.assertIn("منتظر ثبت و تأیید", source)

    def test_completion_truth_uses_scope_remaining_when_stage_ai_is_targeted(self):
        root = Path(__file__).resolve().parents[1]
        source = (root / "app" / "phase49_3i40_commerce_precision.py").read_text(encoding="utf-8")
        self.assertIn('result.get("scoped_ai_fixable_count"', source)
        self.assertIn("بازبینی Scope انجام شد", source)

    def test_progress_proxy_suppresses_internal_100_percent(self):
        dialog = _Dialog()
        proxy = _CompletionProgressProxy(dialog)
        proxy.set_progress(75, "pass")
        proxy.set_progress(100, "old cosmetic terminal")
        self.assertEqual(dialog.progress, [(75.0, "pass")])
        self.assertEqual(proxy.held_terminal, (100.0, "old cosmetic terminal"))


if __name__ == "__main__":
    unittest.main()
