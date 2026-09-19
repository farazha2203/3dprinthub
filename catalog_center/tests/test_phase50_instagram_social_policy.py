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
    highlight_target_for_product,
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
        self.assertIn("#ارسال_سراسری", tags)
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
        self.assertIn("ارسال سفارش به سراسر ایران", caption)
        self.assertIn("مشاهده محصول، انتخاب مشخصات و ثبت سفارش", caption)
        self.assertIn("utm_source=instagram", caption)
        self.assertLessEqual(len(tags), MAX_HASHTAGS)
        self.assertTrue(all(tag in caption for tag in tags))

    def test_story_copy_is_generic_and_brand_consistent(self):
        copy = build_story_copy(row())
        self.assertEqual(copy["style_id"], "3dprinthub_instagram_gold_navy_v2_iransans")
        self.assertEqual(copy["font_family"], "IRANSansWeb(FaNum)")
        self.assertEqual(len(copy["bullets"]), 4)
        self.assertIn("ارسال سفارش به سراسر ایران", copy["bullets"])
        self.assertTrue(copy["title"])
        self.assertTrue(copy["subtitle"])

    def test_highlight_target_uses_product_category_before_keyword_guessing(self):
        spino = row()
        spino.update({
            "local_category_slug": "toys-games",
            "title_fa": "اسکلتی مینی متحرک اسپینوزور",
            "tags_fa_json": json.dumps(["دیناسور", "متحرک"], ensure_ascii=False),
        })
        self.assertEqual(highlight_target_for_product(spino), "اسباب بازی")

        automotive = row()
        automotive["local_category_slug"] = "automotive-clips"
        self.assertEqual(highlight_target_for_product(automotive), "قطعات خودرو")

        cake = row()
        cake["local_category_slug"] = "home-decor"
        cake["title_fa"] = "پایه کیک سه طبقه"
        self.assertEqual(highlight_target_for_product(cake), "پایه کیک")

    def test_false_free_claims_are_removed_across_social_surfaces(self):
        dirty = row()
        dirty.update({
            "seo_title_fa": "چاپ 3 بعدی مجانی دایناسور متحرک",
            "seo_description_fa": "free download model ، قابل سفارش از سایت",
            "sales_bullets_json": json.dumps(
                ["چاپ رایگان", "قابل سفارش", "ارسال سراسری"],
                ensure_ascii=False,
            ),
            "hashtags_fa_json": json.dumps(
                ["#free_download", "#دانلود_رایگان", "دایناسور"],
                ensure_ascii=False,
            ),
            "image_alt_texts_json": json.dumps(
                ["free 3d print dinosaur", "دانلود مجانی مدل"],
                ensure_ascii=False,
            ),
            "local_category_slug": "toys-games",
        })

        caption, tags = build_caption(
            dirty,
            "https://3dprinthub.ir/store/product/dino/?utm_source=instagram",
        )
        alts = build_alt_texts(dirty, ["https://x/1.webp", "https://x/2.webp"])
        story = build_story_copy(dirty)
        combined = " ".join(
            [caption, *tags, *alts, story["title"], story["subtitle"], *story["bullets"]]
        ).casefold()

        for forbidden in (
            "رایگان",
            "مجانی",
            "free_download",
            "free download",
            "free 3d print",
            "3d print for free",
        ):
            self.assertNotIn(forbidden, combined)
        self.assertFalse(any("دانلود" in tag for tag in tags))
        self.assertNotIn(r"\1", combined)
        self.assertIn("قابل سفارش", combined)
        self.assertIn("دایناسور", combined)
        self.assertEqual(highlight_target_for_product(dirty), "اسباب بازی")

    def test_free_sanitizer_does_not_damage_unrelated_freestyle_word(self):
        clean = row()
        clean["seo_description_fa"] = "Freestyle geometric decor ، قابل سفارش"
        caption, _tags = build_caption(
            clean,
            "https://3dprinthub.ir/store/product/freestyle/?utm_source=instagram",
        )
        self.assertIn("Freestyle", caption)
        self.assertNotIn(r"\1", caption)


    def test_policy_version_is_stable_for_receipts(self):
        self.assertEqual(POLICY_VERSION, "instagram-product-v4-20260920")


if __name__ == "__main__":
    unittest.main()
