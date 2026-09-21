from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QAbstractItemView

from app.db import Database
from app.phase50_a2w_material_mapping import (
    build_source_filament_mapping_preview,
)
from qt6.kernel import build_kernel
from qt6.parity_dialogs import SourceFilamentMappingDialog
from qt6.product_wizard import ProductWizardPage


def source_profiles():
    return [
        {
            "instance_id": 3609481,
            "profile_id": 943581967,
            "name": "Single Color Print Profile",
            "print_seconds": 4814,
            "print_minutes": 80.233,
            "weight_grams": 13,
            "material_families": ["PLA"],
            "filaments": [
                {
                    "material": "PLA",
                    "color_hex": "#FECC66",
                    "used_grams": 13,
                    "used_meters": 4.27,
                }
            ],
        },
        {
            "instance_id": 3609488,
            "profile_id": 943610448,
            "name": "Multicolor Print Profile",
            "print_seconds": 15748,
            "print_minutes": 262.467,
            "weight_grams": 50,
            "material_families": ["PLA"],
            "filaments": [
                {
                    "material": "PLA",
                    "color_hex": "#804003",
                    "used_grams": 11,
                    "used_meters": 3.55,
                },
                {
                    "material": "PLA",
                    "color_hex": "#FECC66",
                    "used_grams": 39,
                    "used_meters": 12.69,
                },
            ],
        },
    ]


def local_offers():
    base = {
        "material_name": "PLA",
        "manufacturer_name": "",
        "roll_weight_grams": 1000,
        "stock_roll_count": 1,
        "purchase_price_per_roll": 3_500_000,
        "sale_price_per_roll": 4_500_000,
        "print_hourly_rate": 150_000,
        "supervision_hourly_rate": 50_000,
        "preheat_hours": 0,
        "preheat_temperature_c": 0,
        "preheat_hourly_rate": 0,
        "is_active": 1,
        "color_type": "solid",
        "color_finish": "matte",
        "secondary_hex": "",
        "tertiary_hex": "",
        "palette_hex_json": "[]",
    }
    return [
        {
            **base,
            "id": 1,
            "brand_name": "Bambulab",
            "manufacturer_name": "Bambulab",
            "color_name": "زرد منبع",
            "hex_code": "",
        },
        {
            **base,
            "id": 2,
            "brand_name": "E-Sun",
            "manufacturer_name": "E-Sun",
            "color_name": "سفید",
            "hex_code": "#FAF8F6",
            "palette_hex_json": '["#FAF8F6"]',
            "preheat_hours": 4,
            "preheat_temperature_c": 45,
            "preheat_hourly_rate": 30_000,
        },
        {
            **base,
            "id": 3,
            "brand_name": "ExactCo",
            "manufacturer_name": "ExactCo",
            "color_name": "رنگ ثبت‌شده",
            "hex_code": "#FECC66",
            "palette_hex_json": '["#FECC66"]',
        },
        {
            **base,
            "id": 4,
            "material_name": "PETG",
            "brand_name": "Other",
            "manufacturer_name": "Other",
            "color_name": "رنگ ثبت‌شده",
            "hex_code": "#FECC66",
            "palette_hex_json": '["#FECC66"]',
        },
    ]


def ledger_profiles():
    return [
        {
            "key": "manual-standard",
            "name": "Standard",
            "size_label": "Standard",
            "part_length_cm": 10,
            "part_width_cm": 10,
            "part_height_cm": 10,
            "production_rows": [
                {
                    "weight_grams": 60,
                    "support_weight_grams": 0,
                    "print_time_minutes": 180,
                }
            ],
            "material_options": [],
        },
        {
            "key": "source-mw-3609481",
            "name": "Single Color Print Profile",
            "size_label": "Source 3609481",
            "production_rows": [
                {
                    "weight_grams": 13,
                    "support_weight_grams": 0,
                    "print_time_minutes": 80,
                }
            ],
            "material_options": [],
            "pricing_strategy": "dynamic",
        },
        {
            "key": "source-mw-3609488",
            "name": "Multicolor Print Profile",
            "size_label": "Source 3609488",
            "production_rows": [
                {
                    "weight_grams": 50,
                    "support_weight_grams": 0,
                    "print_time_minutes": 262,
                }
            ],
            "material_options": [],
            "pricing_strategy": "dynamic",
        },
    ]

class Phase50A2WMaterialMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_material_match_and_explicit_hex_ranking_never_guess_names(self):
        preview = build_source_filament_mapping_preview(
            source_profiles(),
            ledger_profiles(),
            local_offers(),
        )
        self.assertEqual(preview["profile_count"], 2)
        self.assertEqual(preview["slot_count"], 3)
        self.assertEqual(preview["candidate_count"], 9)

        single = preview["profiles"][0]
        slot = single["slots"][0]
        self.assertEqual(slot["candidate_count"], 3)
        self.assertEqual(slot["exact_match_count"], 1)
        self.assertEqual(
            slot["candidates"][0]["offer"]["brand"],
            "ExactCo",
        )
        self.assertEqual(
            slot["candidates"][0]["color_match"],
            "exact_hex",
        )
        bambu = next(
            item
            for item in slot["candidates"]
            if item["offer"]["brand"] == "Bambulab"
        )
        self.assertEqual(bambu["color_match"], "no_local_hex")
        self.assertEqual(bambu["offer"]["explicit_palette_hexes"], [])
        self.assertFalse(
            any(
                item["offer"]["material"] == "PETG"
                for item in slot["candidates"]
            )
        )

    def test_single_slot_uses_mature_local_pricing(self):
        preview = build_source_filament_mapping_preview(
            source_profiles(),
            ledger_profiles(),
            local_offers(),
        )
        slot = preview["profiles"][0]["slots"][0]
        exact = next(
            item
            for item in slot["candidates"]
            if item["offer"]["brand"] == "ExactCo"
        )
        self.assertEqual(exact["rate_per_gram"], 4500.0)
        self.assertEqual(exact["slot_material_cost"], 58_500)
        self.assertEqual(exact["single_slot_profile_total"], 325_167)

        esun = next(
            item
            for item in slot["candidates"]
            if item["offer"]["brand"] == "E-Sun"
        )
        self.assertEqual(esun["slot_material_cost"], 58_500)
        self.assertEqual(esun["single_slot_profile_total"], 445_167)

    def test_multicolor_slots_remain_separate_and_have_no_fake_combined_total(self):
        preview = build_source_filament_mapping_preview(
            source_profiles(),
            ledger_profiles(),
            local_offers(),
        )
        multi = preview["profiles"][1]
        self.assertFalse(multi["single_slot"])
        self.assertEqual(multi["slot_count"], 2)
        self.assertEqual(
            [(item["source_hex"], item["used_grams"]) for item in multi["slots"]],
            [("#804003", 11.0), ("#FECC66", 39.0)],
        )
        for slot in multi["slots"]:
            self.assertEqual(slot["candidate_count"], 3)
            for candidate in slot["candidates"]:
                self.assertIsNone(candidate["single_slot_profile_total"])

    def test_commerce_preview_does_not_mutate_product_ledger_or_locks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            db = Database(root / "catalog.sqlite3")
            try:
                db.upsert_source({
                    "code": "makerworld",
                    "name": "MakerWorld",
                    "enabled": 1,
                    "methods": ["http"],
                    "listing_urls": [],
                    "model_url_pattern": "",
                    "requires_login": False,
                    "reference_only": False,
                })
                db.upsert_product({
                    "source_code": "makerworld",
                    "external_id": "w4-test",
                    "source_url": "https://makerworld.com/en/models/1-test",
                    "source_title": "W4 Test",
                    "title_fa": "تست",
                    "local_dir": str(root),
                    "source_print_profiles_json": json.dumps(
                        source_profiles(),
                        ensure_ascii=False,
                    ),
                    "workflow_status": "review",
                })
                product_id = int(
                    db.conn.execute(
                        "SELECT id FROM products WHERE external_id='w4-test'"
                    ).fetchone()["id"]
                )
                kernel = build_kernel(db)
                kernel.commerce.save_profiles(product_id, ledger_profiles())
                db.update_product(
                    product_id,
                    {
                        "operator_stage_locks_json": json.dumps(
                            {"quick": {"locked": True, "locked_at": "x"}},
                            ensure_ascii=False,
                        )
                    },
                )
                before = dict(db.product(product_id))
                history_before = int(
                    db.conn.execute(
                        "SELECT COUNT(*) AS n FROM product_history WHERE product_id=?",
                        (product_id,),
                    ).fetchone()["n"]
                )

                preview = kernel.commerce.preview_source_filament_mapping(
                    product_id,
                    local_offers(),
                )

                after = dict(db.product(product_id))
                history_after = int(
                    db.conn.execute(
                        "SELECT COUNT(*) AS n FROM product_history WHERE product_id=?",
                        (product_id,),
                    ).fetchone()["n"]
                )
                self.assertEqual(preview["candidate_count"], 9)
                self.assertEqual(
                    before["sales_profile_ledger_json"],
                    after["sales_profile_ledger_json"],
                )
                self.assertEqual(
                    before["source_print_profiles_json"],
                    after["source_print_profiles_json"],
                )
                self.assertEqual(
                    before["operator_stage_locks_json"],
                    after["operator_stage_locks_json"],
                )
                self.assertEqual(history_before, history_after)
                self.assertFalse(preview["mutates_ledger"])
                self.assertTrue(preview["requires_operator_review"])
            finally:
                db.close()

    def test_review_dialog_and_stage2_action_are_read_only_ui_contract(self):
        preview = build_source_filament_mapping_preview(
            source_profiles(),
            ledger_profiles(),
            local_offers(),
        )
        dialog = SourceFilamentMappingDialog(preview)
        try:
            self.assertEqual(dialog.table.rowCount(), 9)
            self.assertEqual(
                dialog.table.editTriggers(),
                QAbstractItemView.EditTrigger.NoEditTriggers,
            )
        finally:
            dialog.close()

        with tempfile.TemporaryDirectory() as temp:
            db = Database(Path(temp) / "catalog.sqlite3")
            try:
                kernel = build_kernel(db)
                page = ProductWizardPage(db, kernel=kernel)
                try:
                    self.assertEqual(
                        page.source_filament_map_btn.text(),
                        "W4 تطبیق Filament محلی",
                    )
                    self.assertTrue(
                        callable(getattr(page, "_review_source_filament_mapping"))
                    )
                finally:
                    page.close()
            finally:
                db.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
