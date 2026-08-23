from __future__ import annotations

import unittest
from pathlib import Path

from PIL import Image

from app.phase49_3i12_discovery_image_recovery import (
    CARD_BACKGROUND,
    CARD_VIEWPORT,
    classify_manual_url,
    fit_image_to_card,
)


MAKERWORLD_PATTERN = r"https?://(?:www\.)?makerworld\.com/(?:[a-z]{2}/)?models/(?P<external_id>\d+)[^\s\"'<>]*"
SEARCH_URL = "https://makerworld.com/en/search/models?keyword=cake+stand"
PRODUCT_URL = "https://makerworld.com/en/models/3132472-halloween-samhain-pumpkin-led-goth-tealight-holder#profileId-3535417"


class Phase493I12DiscoveryImageRecoveryTests(unittest.TestCase):
    def test_manual_url_classification_keeps_page_and_product_paths_explicit(self):
        self.assertEqual(classify_manual_url(SEARCH_URL, MAKERWORLD_PATTERN), "page")
        self.assertEqual(classify_manual_url(PRODUCT_URL, MAKERWORLD_PATTERN), "product")
        self.assertEqual(classify_manual_url("cake stand", MAKERWORLD_PATTERN), "invalid")

    def test_invalid_source_regex_fails_closed(self):
        self.assertEqual(classify_manual_url(SEARCH_URL, "(["), "invalid_pattern")

    def test_landscape_image_is_contained_without_crop_in_fixed_viewport(self):
        source = Image.new("RGB", (800, 200), (220, 20, 20))
        fitted = fit_image_to_card(source)
        self.assertEqual(fitted.size, CARD_VIEWPORT)
        # Very wide input must have top/bottom letterbox rather than being cropped.
        self.assertEqual(fitted.getpixel((0, 0)), CARD_BACKGROUND)
        self.assertEqual(fitted.getpixel((CARD_VIEWPORT[0] // 2, CARD_VIEWPORT[1] // 2)), (220, 20, 20))

    def test_portrait_image_is_contained_without_crop_in_fixed_viewport(self):
        source = Image.new("RGB", (200, 800), (20, 80, 220))
        fitted = fit_image_to_card(source)
        self.assertEqual(fitted.size, CARD_VIEWPORT)
        self.assertEqual(fitted.getpixel((0, 0)), CARD_BACKGROUND)
        self.assertEqual(fitted.getpixel((CARD_VIEWPORT[0] // 2, CARD_VIEWPORT[1] // 2)), (20, 80, 220))

    def test_runtime_module_targets_real_ux87_boundary_and_reuses_mature_discovery(self):
        source = (Path(__file__).resolve().parents[1] / "app" / "phase49_3i12_discovery_image_recovery.py").read_text(encoding="utf-8")
        self.assertIn("original_ui = app_class._ui", source)
        self.assertIn("result = original_ui(self)", source)
        self.assertIn("original_start_candidate", source)
        self.assertIn("original_direct", source)
        self.assertNotIn("async_playwright", source)
        self.assertNotIn("extract_direct_link", source)
        self.assertNotIn("collect_classic_exact", source)
        self.assertIn("کشف لینک‌های همین صفحه", source)
        self.assertIn("دریافت محصول تکی", source)
        self.assertIn("در حال کشف لینک‌های صفحه", source)
        self.assertIn("درخواست توقف ثبت شد", source)

    def test_workspace_image_fit_uses_pixel_photo_contract_not_text_unit_label_size(self):
        source = (Path(__file__).resolve().parents[1] / "app" / "phase49_3i12_discovery_image_recovery.py").read_text(encoding="utf-8")
        self.assertIn("ImageOps.contain", source)
        self.assertIn("CARD_VIEWPORT = (228, 171)", source)
        self.assertNotIn("label.configure(width=", source)
        self.assertNotIn("label.configure(height=", source)


if __name__ == "__main__":
    unittest.main()
