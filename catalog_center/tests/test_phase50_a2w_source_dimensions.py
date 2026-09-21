from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from app.phase49_3i35_operator_ledger import normalize_ledger_profile
from app.phase50_a2w_source_profiles import (
    enrich_source_profiles_with_description_dimensions,
    extract_ordered_dimension_evidence,
    ledger_candidates,
    patch_source_ledger_dimensions,
)
from qt6.parity_dialogs import ProfileEditorDialog


HYDRA_DESCRIPTION = """
<p>Important - Please Read Before Printing<br>
1. Two Print Sizes Included<br>
Small Version: Height = 120 mm<br>
Large Version: Height = 180 mm</p>
"""


def hydra_profiles():
    return [
        {
            "instance_id": 3595936,
            "name": "0.2mm layer, 2 walls, 15% infill",
            "print_seconds": 30646,
            "weight_grams": 113,
            "filaments": [{
                "material": "PLA",
                "color_hex": "#E5B03D",
            }],
        },
        {
            "instance_id": 3596024,
            "name": "0.2mm layer, 2 walls, 15% infill",
            "print_seconds": 59485,
            "weight_grams": 312,
            "filaments": [{
                "material": "PLA",
                "color_hex": "#E5B03D",
            }],
        },
    ]


def local_offer():
    return {
        "material": "PLA",
        "brand": "Bambulab",
        "manufacturer": "Bambulab",
        "color": "White",
        "hex": "#FFFFFF",
        "roll_weight_grams": 1000,
        "stock_roll_count": 1,
        "purchase_price_per_roll": 3_500_000,
        "sale_price_per_roll": 4_500_000,
        "print_hourly_rate": 150_000,
        "supervision_hourly_rate": 50_000,
    }

class Phase50A2WSourceDimensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_hydra_ordered_description_binds_first_small_second_large(self):
        evidence = extract_ordered_dimension_evidence(HYDRA_DESCRIPTION)
        self.assertEqual(len(evidence), 2)
        self.assertEqual(evidence[0]["label"], "Small Version")
        self.assertEqual(evidence[0]["dimensions_cm"], {"height": 12.0})
        self.assertEqual(evidence[1]["label"], "Large Version")
        self.assertEqual(evidence[1]["dimensions_cm"], {"height": 18.0})

        profiles = enrich_source_profiles_with_description_dimensions(
            hydra_profiles(),
            HYDRA_DESCRIPTION,
        )
        self.assertEqual(profiles[0]["instance_id"], 3595936)
        self.assertEqual(profiles[0]["dimensions_cm"], {"height": 12.0})
        self.assertEqual(profiles[1]["instance_id"], 3596024)
        self.assertEqual(profiles[1]["dimensions_cm"], {"height": 18.0})
        self.assertEqual(
            profiles[0]["dimension_binding"],
            "ordered_description_to_profile",
        )

    def test_compact_makerworld_meta_keeps_next_numbered_section_separate(self):
        compact = (
            "1. Two Print Sizes Included• "
            "Small Version: Height = 120 mm• "
            "Large Version: Height = 180 mm2. Support Removal Tips• "
            "Use side cutters."
        )
        evidence = extract_ordered_dimension_evidence(compact)
        self.assertEqual(
            [(x["label"], x["dimensions_cm"]) for x in evidence],
            [
                ("Small Version", {"height": 12.0}),
                ("Large Version", {"height": 18.0}),
            ],
        )

    def test_mismatched_count_fails_closed_without_dimension_binding(self):
        profiles = enrich_source_profiles_with_description_dimensions(
            hydra_profiles()[:1],
            HYDRA_DESCRIPTION,
        )
        self.assertNotIn("dimensions_cm", profiles[0])

    def test_full_dimensions_convert_to_cm(self):
        evidence = extract_ordered_dimension_evidence(
            "Dimensions: 40 x 50 x 60 mm"
        )
        self.assertEqual(len(evidence), 1)
        self.assertEqual(
            evidence[0]["dimensions_cm"],
            {"length": 4.0, "width": 5.0, "height": 6.0},
        )
        inches = extract_ordered_dimension_evidence(
            "Size 1: 2 x 3 x 4 inch"
        )
        self.assertEqual(
            inches[0]["dimensions_cm"],
            {"length": 5.08, "width": 7.62, "height": 10.16},
        )

    def test_ledger_candidates_expand_single_source_dimension_to_all_axes(self):
        profiles = enrich_source_profiles_with_description_dimensions(
            hydra_profiles(),
            HYDRA_DESCRIPTION,
        )
        candidates = ledger_candidates(profiles)
        self.assertEqual(
            (
                candidates[0]["part_length_cm"],
                candidates[0]["part_width_cm"],
                candidates[0]["part_height_cm"],
            ),
            (12.0, 12.0, 12.0),
        )
        self.assertEqual(
            (
                candidates[1]["part_length_cm"],
                candidates[1]["part_width_cm"],
                candidates[1]["part_height_cm"],
            ),
            (18.0, 18.0, 18.0),
        )
        self.assertEqual(candidates[0]["size_label"], "Small 12 x 12 x 12 cm")
        self.assertEqual(candidates[1]["size_label"], "Large 18 x 18 x 18 cm")
        self.assertEqual(
            candidates[0]["dimension_axis_sources"],
            {
                "length": "owner_equal_dimension_rule",
                "width": "owner_equal_dimension_rule",
                "height": "source_description",
            },
        )
        self.assertEqual(
            candidates[0]["dimension_factual_axes"],
            ["height"],
        )
        self.assertTrue(candidates[0]["dimension_is_estimated"])

    def test_dimension_patch_preserves_local_commerce_and_applies_exact_height(self):
        source = enrich_source_profiles_with_description_dimensions(
            hydra_profiles(),
            HYDRA_DESCRIPTION,
        )
        current = ledger_candidates(hydra_profiles())
        current[0]["material_options"] = [local_offer()]
        current[0]["price_min"] = 321000
        current[0]["part_length_cm"] = 7
        current[0]["part_width_cm"] = 8
        before_offer = dict(current[0]["material_options"][0])

        patched, report = patch_source_ledger_dimensions(current, source)

        self.assertEqual(report["changed_keys"], ["source-mw-3595936", "source-mw-3596024"])
        first = patched[0]
        self.assertEqual(first["part_length_cm"], 7)
        self.assertEqual(first["part_width_cm"], 8)
        self.assertEqual(first["part_height_cm"], 12)
        self.assertEqual(first["material_options"][0], before_offer)
        self.assertEqual(first["price_min"], 321000)
        self.assertFalse(first["dimension_is_estimated"])
        self.assertEqual(
            first["dimension_axis_sources"]["height"],
            "source_description",
        )

    def test_625_style_owner_fallback_fills_only_zero_axes(self):
        source = [
            {"instance_id": 3609481, "name": "Single"},
            {"instance_id": 3609488, "name": "Multi"},
        ]
        current = [
            {
                **ledger_candidates(source)[0],
                "part_length_cm": 5,
                "part_width_cm": 5,
                "part_height_cm": 5,
                "material_options": [local_offer()],
            },
            ledger_candidates(source)[1],
        ]
        patched, report = patch_source_ledger_dimensions(
            current,
            source,
            owner_fallback_by_key={"source-mw-3609488": 4.0},
        )
        first, second = patched
        self.assertEqual(
            (first["part_length_cm"], first["part_width_cm"], first["part_height_cm"]),
            (5, 5, 5),
        )
        self.assertEqual(first["material_options"], [local_offer()])
        self.assertEqual(
            (second["part_length_cm"], second["part_width_cm"], second["part_height_cm"]),
            (4.0, 4.0, 4.0),
        )
        self.assertTrue(second["dimension_is_estimated"])
        self.assertEqual(second["dimension_source"], "owner_estimated")
        self.assertEqual(report["estimated_keys"], ["source-mw-3609488"])

    def test_normalizer_preserves_dimension_metadata(self):
        profile = normalize_ledger_profile({
            "key": "source-mw-1",
            "name": "Source Profile",
            "size_label": "Small H=12 cm",
            "part_height_cm": 12,
            "production_rows": [{
                "weight_grams": 10,
                "support_weight_grams": 0,
                "print_time_minutes": 20,
            }],
            "material_options": [local_offer()],
            "dimension_source": "source_description",
            "dimension_is_estimated": False,
            "dimension_label": "Small Version",
            "dimension_evidence": "Small Version: Height = 120 mm",
            "dimension_known_axes": ["length", "width", "height"],
            "dimension_factual_axes": ["height"],
            "dimension_binding": "ordered_description_to_profile",
            "dimension_axis_sources": {
                "length": "owner_equal_dimension_rule",
                "width": "owner_equal_dimension_rule",
                "height": "source_description",
            },
        })
        self.assertEqual(profile["dimension_source"], "source_description")
        self.assertEqual(
            profile["dimension_known_axes"],
            ["length", "width", "height"],
        )
        self.assertEqual(profile["dimension_factual_axes"], ["height"])
        self.assertEqual(
            profile["dimension_axis_sources"],
            {
                "length": "owner_equal_dimension_rule",
                "width": "owner_equal_dimension_rule",
                "height": "source_description",
            },
        )

    def test_source_single_dimension_profile_shows_all_three_equal_and_can_save(self):
        source = enrich_source_profiles_with_description_dimensions(
            hydra_profiles(),
            HYDRA_DESCRIPTION,
        )
        profile = ledger_candidates(source)[0]
        profile["material_options"] = [local_offer()]
        dialog = ProfileEditorDialog([local_offer()], profile)
        warnings = []
        original_warning = QMessageBox.warning
        try:
            self.assertEqual(dialog.length.value(), 12)
            self.assertEqual(dialog.width.value(), 12)
            self.assertEqual(dialog.height.value(), 12)
            self.assertIn("تکمیل", dialog.dimension_hint.text())
            self.assertIn("ارتفاع", dialog.dimension_hint.text())
            QMessageBox.warning = lambda *args, **kwargs: warnings.append(args)
            dialog._accept()
            self.assertEqual(warnings, [])
            self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
        finally:
            QMessageBox.warning = original_warning
            dialog.close()

    def test_manual_profile_still_rejects_zero_dimensions(self):
        profile = {
            "key": "manual-one",
            "name": "Manual One",
            "size_label": "Manual",
            "part_length_cm": 0,
            "part_width_cm": 0,
            "part_height_cm": 0,
            "production_rows": [{
                "weight_grams": 50,
                "support_weight_grams": 0,
                "print_time_minutes": 60,
            }],
            "material_options": [local_offer()],
        }
        dialog = ProfileEditorDialog([local_offer()], profile)
        warnings = []
        original_warning = QMessageBox.warning
        try:
            QMessageBox.warning = lambda *args, **kwargs: warnings.append(args)
            dialog._accept()
            self.assertTrue(warnings)
            self.assertNotEqual(dialog.result(), QDialog.DialogCode.Accepted)
        finally:
            QMessageBox.warning = original_warning
            dialog.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
