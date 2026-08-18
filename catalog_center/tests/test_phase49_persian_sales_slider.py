from __future__ import annotations

import unittest
from pathlib import Path

from app.phase49_persian_sales_desktop import _fa, _fallbacks


class Phase49PersianSalesSliderDesktopTests(unittest.TestCase):
    def test_raw_english_cookie_copy_is_never_a_slider_fallback(self):
        row = {
            "seo_title_fa": "",
            "title_fa": "",
            "short_description_fa": "",
            "seo_description_fa": "",
            "description_fa": "",
            "source_title": "Vesper – Sculptural Bedside Lamp",
            "source_description": "We use cookies and tracking technologies. Cookie Settings",
            "image_alt_texts_json": "[]",
            "keywords_json": "[]",
            "tags_fa_json": "[]",
        }
        title, description, alt, focus = _fallbacks(row)
        self.assertEqual(title, "محصول منتخب چاپ سه‌بعدی")
        self.assertNotIn("Vesper", title)
        self.assertNotIn("cookie", description.casefold())
        self.assertIn("خرید", focus)
        self.assertIn("خرید", alt)

    def test_existing_persian_product_seo_drives_slider_copy(self):
        row = {
            "seo_title_fa": "خرید چراغ رومیزی دکوراتیو وسپر",
            "title_fa": "چراغ رومیزی دکوراتیو وسپر",
            "short_description_fa": "چراغ مدرن برای دکور منزل و میز کنار تخت.",
            "seo_description_fa": "خرید و سفارش چراغ رومیزی وسپر با چاپ سه‌بعدی.",
            "description_fa": "توضیح کامل فارسی",
            "image_alt_texts_json": '["چراغ رومیزی وسپر برای دکور منزل"]',
            "keywords_json": '["خرید چراغ دکوراتیو"]',
            "tags_fa_json": '["چراغ دکوراتیو"]',
        }
        title, description, alt, focus = _fallbacks(row)
        self.assertEqual(title, row["seo_title_fa"])
        self.assertEqual(description, row["short_description_fa"])
        self.assertIn("چراغ", alt)
        self.assertEqual(focus, "خرید چراغ دکوراتیو")

    def test_cookie_boilerplate_is_rejected_even_if_html_is_present(self):
        self.assertEqual(
            _fa('<p>Cookie Settings</p><br>We use cookies and tracking technologies.'),
            "",
        )

    def test_active_launcher_installs_persian_sales_workspace_marker(self):
        launch = (Path(__file__).resolve().parents[1] / "launch.py").read_text(encoding="utf-8")
        self.assertIn("install_persian_sales_workspace(ProductWorkspace)", launch)
        self.assertIn("EPIC49_PERSIAN_SALES_HERO=ENABLED", launch)


if __name__ == "__main__":
    unittest.main()
