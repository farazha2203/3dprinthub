from __future__ import annotations

import unittest
from pathlib import Path

from app.phase49_3i_pricing_modes import normalize_range


ROOT = Path(__file__).resolve().parents[1]


class Phase493IPricingModeTests(unittest.TestCase):
    def test_range_normalization_sorts_values(self):
        self.assertEqual(normalize_range("200000", "500000"), (200000, 500000))
        self.assertEqual(normalize_range("500000", "200000"), (200000, 500000))
        self.assertEqual(normalize_range("0", "500000"), (0, 500000))

    def test_workspace_exposes_exactly_three_business_pricing_modes(self):
        source = (ROOT / "app" / "phase49_3i_pricing_modes.py").read_text(encoding="utf-8")
        self.assertIn('value="fixed"', source)
        self.assertIn('value="range"', source)
        self.assertIn('value="dynamic"', source)
        self.assertIn("● قیمت قطعی", source)
        self.assertIn("● بازه قیمت", source)
        self.assertIn("● قیمت فرمولی", source)
        self.assertNotIn('value="quote"', source)

    def test_range_save_does_not_mark_price_final_or_formula(self):
        source = (ROOT / "app" / "phase49_3i_pricing_modes.py").read_text(encoding="utf-8")
        self.assertIn('"pricing_strategy": "range"', source)
        self.assertIn('"price_is_final": 0', source)
        self.assertIn('"final_price": 0', source)
        self.assertIn("maximum <= minimum", source)


if __name__ == "__main__":
    unittest.main()
