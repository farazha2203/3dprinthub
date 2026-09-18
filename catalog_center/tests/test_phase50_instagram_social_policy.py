from __future__ import annotations

import json
import unittest

from app.social_content_policy import (
    MAX_HASHTAGS,
    POLICY_VERSION,
    build_alt_texts,
    build_caption,
    build_hashtags,
    build_story_copy,
)


def row():
    return {
        "id": 91,
        "seo_title_fa": "چراغ رومیزی موج‌دار سه‌بعدی",
        "seo_description_fa": "چراغ دکوراتیو مدرن با فرم پارامتریک و نور گرم.",
        "sales_bullets_json": json.dumps(
            ["طراحی پارامتریک", "قابل سفارش", "چاپ دقیق", "مناسب دکور مدرن"],
            ensure_ascii=False,
        ),
        "hashtags_fa_json": json.dumps(
            ["چراغ", "دکور", "چاپ سه بعدی", "چراغ", "خانه", "نورپردازی", "مدرن", "هدیه", "پارامتریک"],
            ensure_ascii=False,
        ),
        "tags_fa_json": json.dumps(["آباژور", "دکور"], ensure_ascii=False),
        "categories_fa_json": json.dumps(["دکوراسیون"], ensure_ascii=False),
        "image_alt_texts_json": json.dumps(["نمای اصلی چراغ"], ensure_ascii=False),
        "materials_json": json.dumps(["PLA"], ensure_ascii=False),
    }


class InstagramSocialPolicyTests(unittest.TestCase):
    def test_hashtags_are_relevant_deduplicated_and_bounded(self):
        tags = build_hashtags(row())
        self.assertLessEqual(len(tags), MAX_HASHTAGS)
        self.assertEqual(len(tags), len(set(tags)))
        self.assertIn("#چاپ_سه_بعدی", tags)
        self.assertIn("#3DPrintHub", tags)

    def test_alt_text_is_present_for_every_media_asset(self):
        urls = ["https://x/a.webp", "https://x/b.webp", "https://x/c.webp"]
        alt = build_alt_texts(row(), urls)
        self.assertEqual(len(alt), len(urls))
        self.assertEqual(alt[0], "نمای اصلی چراغ")
        self.assertTrue(all(str(item).strip() for item in alt))
        self.assertIn("نمای 2 از 3", alt[1])

    def test_caption_contains_product_copy_cta_and_bounded_hashtags(self):
        caption, tags = build_caption(
            row(),
            "https://3dprinthub.ir/store/product/demo/?utm_source=instagram",
        )
        self.assertIn("چراغ رومیزی موج‌دار سه‌بعدی", caption)
        self.assertIn("مشاهده محصول و انتخاب مشخصات", caption)
        self.assertIn("utm_source=instagram", caption)
        self.assertLessEqual(len(tags), MAX_HASHTAGS)
        self.assertTrue(all(tag in caption for tag in tags))

    def test_story_copy_is_generic_and_brand_consistent(self):
        copy = build_story_copy(row())
        self.assertEqual(copy["style_id"], "3dprinthub_instagram_gold_navy_v2")
        self.assertEqual(copy["font_family"], "IRANSansWeb(FaNum)")
        self.assertEqual(len(copy["bullets"]), 4)
        self.assertTrue(copy["title"])
        self.assertTrue(copy["subtitle"])

    def test_policy_version_is_stable_for_receipts(self):
        self.assertEqual(POLICY_VERSION, "instagram-product-v2-20260918")


if __name__ == "__main__":
    unittest.main()
