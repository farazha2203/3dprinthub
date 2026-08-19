from __future__ import annotations

import json
import unittest

from app import phase49_3e_ai_task_center as task_center
from app.phase49_3e_ai_contract import install as install_contract


install_contract(task_center)


class Phase493EAITaskCenterTests(unittest.TestCase):
    def base_row(self):
        return {
            "id": 77,
            "title_fa": "خرس همبستگی آگاهی از سرطان پستان",
            "short_description_fa": "مدل سه‌بعدی تزئینی برای چاپ و استفاده دکوری.",
            "description_fa": "<p>این مدل سه‌بعدی برای چاپ و استفاده دکوری آماده شده است.</p>",
            "use_description": "مناسب برای دکور، هدیه و نمایش موضوعی.",
            "seo_title_fa": "خرید مدل سه‌بعدی خرس همبستگی",
            "seo_description_fa": "خرید و سفارش مدل سه‌بعدی خرس همبستگی با امکان انتخاب گزینه‌های چاپ.",
            "keywords_json": json.dumps(["خرید مدل سه‌بعدی خرس", "سفارش خرس چاپ سه‌بعدی", "قیمت مدل خرس سه‌بعدی"], ensure_ascii=False),
            "tags_fa_json": json.dumps(["چاپ سه‌بعدی", "خرس سه‌بعدی"], ensure_ascii=False),
            "hashtags_fa_json": json.dumps(["#چاپ_سه_بعدی", "#خرس_سه_بعدی"], ensure_ascii=False),
            "selected_images_json": json.dumps(["https://example.com/a.jpg"], ensure_ascii=False),
            "image_alt_texts_json": "[]",
            "image_metadata_json": "[]",
            "material_recommendations_json": "[]",
            "homepage_slider_enabled": 0,
            "homepage_slider_title_fa": "",
            "homepage_slider_description_fa": "",
            "homepage_slider_alt_text": "",
            "homepage_slider_focus_keyword": "",
            "homepage_slider_image_url": "",
            "source_title": "Solidarity Bear",
            "source_url": "https://example.com/product",
            "source_name": "makerworld",
            "source_code": "makerworld",
            "author_name": "Designer",
            "license_name": "review",
            "license_url": "",
            "commercial_status": "review",
            "specs_fa_json": "[]",
        }

    def test_image_task_is_red_until_alt_and_metadata_are_complete(self):
        row = self.base_row()
        tasks = {item["key"]: item for item in task_center.evaluate_ai_tasks(row)}
        self.assertEqual(tasks["image_seo"]["status"], "missing")
        self.assertIn("Alt فارسی همه تصاویر", tasks["image_seo"]["missing"])
        self.assertTrue(any("نام SEO تصویر 1" == item for item in tasks["image_seo"]["missing"]))

    def test_slider_task_is_skipped_when_slider_is_disabled(self):
        row = self.base_row()
        tasks = {item["key"]: item for item in task_center.evaluate_ai_tasks(row)}
        self.assertEqual(tasks["slider_seo"]["status"], "skipped")
        self.assertEqual(tasks["slider_seo"]["missing"], [])

    def test_slider_task_becomes_required_when_enabled(self):
        row = self.base_row()
        row["homepage_slider_enabled"] = 1
        tasks = {item["key"]: item for item in task_center.evaluate_ai_tasks(row)}
        self.assertEqual(tasks["slider_seo"]["status"], "missing")
        self.assertIn("عنوان اسلایدر", tasks["slider_seo"]["missing"])
        self.assertIn("عکس اسلایدر", tasks["slider_seo"]["missing"])

    def test_ai_updates_never_overwrite_existing_manual_seo(self):
        row = self.base_row()
        pack = {
            "title_fa": "عنوان جدید",
            "short_description_fa": "توضیح جدید",
            "description_fa": "<p>متن جدید</p>",
            "use_description_fa": "کاربرد جدید",
            "seo_title_fa": "سئو جدید",
            "seo_description_fa": "توضیح سئو جدید",
            "target_keywords_fa": ["کلمه یک", "کلمه دو", "کلمه سه"],
            "tags_fa": ["تگ جدید"],
            "hashtags_fa": ["#هشتگ_جدید"],
            "image_alt_texts": ["نمای فارسی محصول"],
            "categories_fa": ["دکور"],
            "specs_fa": [{"key": "نوع", "value": "تزئینی"}],
            "sales_bullets": ["قابل سفارش"],
            "social_caption_fa": "کپشن فارسی",
            "material_recommendations": [{"material": "PLA", "score": 80, "recommended": True, "reason_fa": "برای قطعه تزئینی مناسب است."}],
            "homepage_slider_seo": {},
        }
        updates = task_center.build_ai_updates(row, pack, scope="all")
        self.assertNotIn("title_fa", updates)
        self.assertNotIn("seo_title_fa", updates)
        self.assertNotIn("seo_description_fa", updates)
        self.assertIn("image_alt_texts_json", updates)
        self.assertEqual(json.loads(updates["image_alt_texts_json"]), ["نمای فارسی محصول"])

    def test_structured_specs_and_material_recommendations_remain_objects(self):
        row = self.base_row()
        pack = {
            "specs_fa": [{"key": "نوع", "value": "تزئینی"}],
            "material_recommendations": [{"material": "PLA", "score": 82, "recommended": True, "reason_fa": "برای استفاده تزئینی انتخاب مناسبی است."}],
            "homepage_slider_seo": {},
        }
        updates = task_center.build_ai_updates(row, pack, scope="all")
        specs = json.loads(updates["specs_fa_json"])
        recs = json.loads(updates["material_recommendations_json"])
        self.assertIsInstance(specs[0], dict)
        self.assertEqual(specs[0]["key"], "نوع")
        self.assertIsInstance(recs[0], dict)
        self.assertEqual(recs[0]["material"], "PLA")

    def test_material_task_does_not_turn_green_for_stringified_fake_objects(self):
        row = self.base_row()
        row["material_recommendations_json"] = json.dumps(["{'material': 'PLA'}"])
        tasks = {item["key"]: item for item in task_center.evaluate_ai_tasks(row)}
        self.assertEqual(tasks["materials"]["status"], "missing")

    def test_operator_override_merge_preserves_only_declared_fields(self):
        base = {
            "seo_filename": "base.webp",
            "alt_text": "Alt پایه",
            "creator": "Original Creator",
            "copyright_holder": "Original Creator",
        }
        existing = {
            "seo_filename": "custom-name.webp",
            "alt_text": "Alt دستی",
            "creator": "Corrected Creator",
            "copyright_holder": "DO NOT OVERRIDE",
            "operator_override_fields": ["seo_filename", "alt_text", "creator"],
        }
        merged = task_center.merge_operator_overrides(base, existing)
        self.assertEqual(merged["seo_filename"], "custom-name.webp")
        self.assertEqual(merged["alt_text"], "Alt دستی")
        self.assertEqual(merged["creator"], "Corrected Creator")
        self.assertEqual(merged["copyright_holder"], "Original Creator")

    def test_safe_seo_filename_never_returns_arbitrary_path(self):
        value = task_center._safe_seo_filename("../My Product IMAGE!!.JPG", "fallback.webp")
        self.assertEqual(value, "my-product-image-jpg.webp")
        self.assertNotIn("/", value)
        self.assertNotIn("\\", value)


if __name__ == "__main__":
    unittest.main()
