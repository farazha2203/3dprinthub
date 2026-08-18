from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from store.models import ImportedPrintAsset
from store.phase49_persian_sales_copy import (
    build_product_sales_seo,
    build_slider_sales_copy,
    clean_public_text,
    safe_persian_text,
)
from website.models import HomepageHeroSlide
from website.phase49_persian_sales_hero import hero_suggestions


COOKIE_TEXT = (
    'When you visit our website, if you give your consent, we will use cookies and other '
    'tracking technologies to improve your browsing experience. <br>Select an option or '
    'go to <a href="#">Cookie Settings</a> to manage your preferences.'
)


class Phase49PersianSalesHeroTests(SimpleTestCase):
    def _asset(self):
        return ImportedPrintAsset(
            title="Vesper – Sculptural Bedside Lamp",
            persian_title="چراغ رومیزی دکوراتیو وسپر",
            persian_short_description="چراغ دکوراتیو مناسب میز کنار تخت با طراحی مدرن و قابل سفارش با چاپ سه‌بعدی.",
            description=COOKIE_TEXT,
            source_payload={
                "desktop_catalog_v85": {
                    "source_title": "Vesper – Sculptural Bedside Lamp",
                    "source_description": COOKIE_TEXT,
                    "title_fa": "چراغ رومیزی دکوراتیو وسپر",
                    "short_description_fa": "چراغ دکوراتیو مدرن برای میز کنار تخت و دکور منزل.",
                    "seo_title_fa": "خرید چراغ رومیزی دکوراتیو وسپر",
                    "seo_description_fa": "خرید و سفارش چراغ رومیزی دکوراتیو وسپر با چاپ سه‌بعدی و متریال قابل انتخاب.",
                    "tags_fa_json": ["چراغ دکوراتیو", "دکور منزل"],
                    "keywords_json": ["خرید چراغ دکوراتیو"],
                    "homepage_slider_title_fa": "چراغ رومیزی دکوراتیو وسپر",
                    "homepage_slider_description_fa": "چراغی مدرن برای دکور منزل؛ مشخصات، متریال و قیمت را در صفحه محصول ببینید.",
                    "homepage_slider_alt_text": "چراغ رومیزی دکوراتیو وسپر برای خرید و سفارش چاپ سه‌بعدی",
                    "homepage_slider_focus_keyword": "خرید چراغ رومیزی دکوراتیو",
                    "homepage_slider_button_text": "مشاهده محصول",
                }
            },
        )

    def test_source_cookie_and_html_are_rejected(self):
        self.assertIn("Cookie Settings", clean_public_text(COOKIE_TEXT))
        self.assertEqual(safe_persian_text(COOKIE_TEXT), "")
        resolved = build_slider_sales_copy(
            {"homepage_slider_description_fa": COOKIE_TEXT, "source_description": COOKIE_TEXT}
        )
        self.assertNotIn("cookie", resolved["description_fa"].casefold())
        self.assertNotIn("<", resolved["description_fa"])
        self.assertTrue(safe_persian_text(resolved["description_fa"]))

    def test_windows_dedicated_persian_slider_seo_is_authoritative(self):
        asset = self._asset()
        suggested = hero_suggestions(asset)
        self.assertEqual(suggested["title"], "چراغ رومیزی دکوراتیو وسپر")
        self.assertIn("متریال", suggested["description"])
        self.assertIn("خرید", suggested["image_alt_text"])
        self.assertEqual(suggested["focus_keyword"], "خرید چراغ رومیزی دکوراتیو")
        self.assertNotIn("Vesper – Sculptural Bedside Lamp", suggested["title"])
        self.assertNotIn("Cookie Settings", suggested["description"])

    def test_legacy_english_slide_override_cannot_beat_persian_windows_copy(self):
        asset = self._asset()
        slide = HomepageHeroSlide(
            asset=asset,
            title_override="Vesper – Sculptural Bedside Lamp",
            group_title="MakerWorld",
            description=COOKIE_TEXT,
            image_alt_text="Vesper sculptural lamp",
            button_text="Buy now",
        )
        self.assertEqual(slide.effective_title, "چراغ رومیزی دکوراتیو وسپر")
        self.assertEqual(slide.effective_group_title, "محصول منتخب")
        self.assertIn("متریال", slide.effective_description)
        self.assertNotIn("cookie", slide.effective_description.casefold())
        self.assertIn("خرید", slide.effective_alt_text)
        self.assertEqual(slide.effective_button_text, "مشاهده محصول")

    def test_product_meta_fallback_has_sales_intent_and_is_persian(self):
        resolved = build_product_sales_seo(
            {
                "title_fa": "چراغ رومیزی دکوراتیو",
                "short_description_fa": "چراغ مناسب دکور منزل با امکان انتخاب متریال.",
                "tags_fa_json": ["چراغ دکوراتیو"],
            }
        )
        self.assertTrue(resolved["meta_title"].startswith("خرید "))
        self.assertIn("خرید", resolved["focus_keyword"])
        self.assertTrue(safe_persian_text(resolved["meta_description"]))

    def test_template_keeps_full_text_but_css_clamps_to_two_lines(self):
        root = Path(settings.BASE_DIR)
        template = (root / "templates/website/partials/hero.html").read_text(encoding="utf-8")
        css = (root / "static/css/phase49_2c-hero-effects.css").read_text(encoding="utf-8")
        js = (root / "static/js/phase49_2c-home-hero.js").read_text(encoding="utf-8")
        self.assertIn("data-p49c-description", template)
        self.assertIn("slide.effective_description", template)
        self.assertIn("-webkit-line-clamp:2", css)
        self.assertIn("text-overflow:ellipsis", css)
        self.assertIn("is-expanded", css)
        self.assertIn("بستن توضیحات", js)
        self.assertIn("aria-expanded", js)
