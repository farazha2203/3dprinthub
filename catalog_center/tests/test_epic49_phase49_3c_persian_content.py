from __future__ import annotations

import json
import unittest

from app.openai_content import CONTENT_SCHEMA
from app.phase49_3c_persian_content import (
    _generic_persian_pack,
    ensure_html_fragment,
    has_persian_editorial_text,
    sanitize_fa_html,
)


class Phase493CPersianContentTests(unittest.TestCase):
    def test_english_editorial_text_is_rejected(self):
        self.assertFalse(has_persian_editorial_text("Fanart Solidarity Bear"))
        self.assertTrue(has_persian_editorial_text("خرس همبستگی"))
        self.assertFalse(has_persian_editorial_text("خرید Fanart"))

    def test_fallback_never_uses_english_source_as_persian_content(self):
        result = _generic_persian_pack(
            {
                "title_fa": "Fanart Solidarity Bear",
                "short_description_fa": "A decorative model",
                "description_fa": "A decorative model",
                "seo_title_fa": "Fanart Solidarity Bear",
                "seo_description_fa": "Buy Fanart",
                "tags_fa": ["Fanart"],
                "hashtags_fa": ["#Fanart"],
                "target_keywords_fa": ["buy Fanart"],
                "sales_bullets": ["A decorative model"],
                "social_caption_fa": "Buy Fanart",
                "image_alt_texts": ["Fanart image"],
                "homepage_slider_seo": {
                    "title_fa": "Fanart",
                    "description_fa": "Buy Fanart",
                    "image_alt_fa": "Fanart image",
                    "button_text_fa": "View product",
                    "focus_keyword_fa": "Fanart",
                },
            },
            2,
        )
        for key in (
            "title_fa", "short_description_fa", "description_fa", "use_description_fa",
            "seo_title_fa", "seo_description_fa", "social_caption_fa",
        ):
            self.assertTrue(has_persian_editorial_text(result[key]), key)
        for key in ("tags_fa", "hashtags_fa", "target_keywords_fa", "sales_bullets", "image_alt_texts"):
            self.assertTrue(result[key], key)
            self.assertTrue(all(has_persian_editorial_text(item) for item in result[key]), key)
        self.assertEqual(len(result["image_alt_texts"]), 2)
        self.assertTrue(result["_phase49_3c_persian_fallback"])

    def test_description_is_html_fragment_and_scripts_are_removed(self):
        raw = "<p>سلام</p><script>alert(1)</script><strong>چاپ سه‌بعدی</strong>"
        sanitized = sanitize_fa_html(raw)
        self.assertIn("<p>سلام</p>", sanitized)
        self.assertIn("<strong>چاپ سه‌بعدی</strong>", sanitized)
        self.assertNotIn("script", sanitized.lower())
        wrapped = ensure_html_fragment("سلام\nتوضیح دوم")
        self.assertIn("<p>سلام</p>", wrapped)
        self.assertIn("<p>توضیح دوم</p>", wrapped)

    def test_schema_requires_use_description_fa_after_install(self):
        from app.phase49_3c_persian_content import install
        install()
        self.assertIn("use_description_fa", CONTENT_SCHEMA["properties"])
        self.assertIn("use_description_fa", CONTENT_SCHEMA["required"])

    def test_seo_fallback_is_persian_only(self):
        result = _generic_persian_pack({}, 1)
        for key in ("seo_title_fa", "seo_description_fa", "tags_fa", "hashtags_fa", "target_keywords_fa"):
            value = result[key]
            values = value if isinstance(value, list) else [value]
            self.assertTrue(all(has_persian_editorial_text(item) for item in values), key)
        self.assertTrue(result["use_description_fa"])
        self.assertTrue(result["description_fa"].startswith("<p>"))


if __name__ == "__main__":
    unittest.main()
