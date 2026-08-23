from __future__ import annotations

import json
import unittest

from app.phase49_3i18_operator_editing import (
    _template,
    authoritative_updates,
    ai_updates,
)


class Phase493I18OperatorEditingTests(unittest.TestCase):
    def test_bulk_template_supports_title_and_numbering(self):
        self.assertEqual(
            _template("{title} - تصویر {n2} از {total}", "استند کیک", 3, 12),
            "استند کیک - تصویر 03 از 12",
        )

    def test_authoritative_title_replaces_editable_text_not_source_identity(self):
        row = {
            "title_fa": "عنوان اشتباه",
            "short_description_fa": "خرید عنوان اشتباه برای میز پذیرایی",
            "description_fa": "<p>عنوان اشتباه مناسب دکور است.</p>",
            "seo_title_fa": "عنوان اشتباه | چاپ سه بعدی",
            "seo_description_fa": "سفارش عنوان اشتباه",
            "tags_fa_json": json.dumps(["عنوان اشتباه", "دکور"], ensure_ascii=False),
            "image_alt_texts_json": json.dumps(["نمای عنوان اشتباه"], ensure_ascii=False),
            "content_pack_json": json.dumps({"title_fa": "عنوان اشتباه", "sales_bullets": ["عنوان اشتباه زیبا"]}, ensure_ascii=False),
            "image_metadata_json": json.dumps([{
                "source_url": "https://example.test/source.webp",
                "alt_text": "نمای عنوان اشتباه",
                "title": "عنوان اشتباه",
                "caption": "عنوان اشتباه",
                "creator": "Original Creator",
            }], ensure_ascii=False),
        }
        updates = authoritative_updates(row, "استند کیک")
        self.assertEqual(updates["title_fa"], "استند کیک")
        self.assertIn("استند کیک", updates["short_description_fa"])
        self.assertIn("استند کیک", updates["seo_title_fa"])
        self.assertNotIn("عنوان اشتباه", updates["seo_description_fa"])
        metadata = json.loads(updates["image_metadata_json"])
        self.assertEqual(metadata[0]["source_url"], "https://example.test/source.webp")
        self.assertEqual(metadata[0]["creator"], "Original Creator")
        self.assertEqual(metadata[0]["title"], "استند کیک")
        self.assertFalse(metadata[0]["metadata_ready"])

    def test_ai_rebuild_forces_operator_title_across_generated_pack(self):
        row = {"title_fa": "عنوان اشتباه", "homepage_slider_enabled": 1}
        pack = {
            "title_fa": "نام حدسی AI",
            "short_description_fa": "نام حدسی AI برای پذیرایی",
            "description_fa": "<p>نام حدسی AI برای میز.</p>",
            "use_description_fa": "کاربرد نام حدسی AI",
            "categories_fa": ["دکور"],
            "specs_fa": [],
            "tags_fa": ["نام حدسی AI"],
            "hashtags_fa": ["#نام_حدسی_AI"],
            "target_keywords_fa": ["خرید نام حدسی AI"],
            "sales_bullets": ["نام حدسی AI"],
            "image_alt_texts": ["نمای نام حدسی AI"],
            "seo_title_fa": "نام حدسی AI | خرید",
            "seo_description_fa": "خرید نام حدسی AI",
            "social_caption_fa": "نام حدسی AI",
            "homepage_slider_seo": {
                "title_fa": "نام حدسی AI",
                "description_fa": "نام حدسی AI برای پذیرایی",
                "image_alt_fa": "نمای نام حدسی AI",
                "button_text_fa": "مشاهده محصول",
                "focus_keyword_fa": "خرید نام حدسی AI",
            },
        }
        updates = ai_updates(row, pack, "استند کیک")
        self.assertEqual(updates["title_fa"], "استند کیک")
        self.assertIn("استند کیک", updates["seo_title_fa"])
        self.assertNotIn("نام حدسی AI", updates["seo_description_fa"])
        self.assertIn("استند کیک", updates["homepage_slider_title_fa"])
        self.assertIn("استند کیک", json.loads(updates["image_alt_texts_json"])[0])


if __name__ == "__main__":
    unittest.main()
