from __future__ import annotations

import json
import unittest

from app import phase49_3i31_smart_link_bulk_ai as phase31


class Phase49I31SmartLinkBulkAITests(unittest.TestCase):
    def test_structured_source_description_keeps_safe_product_facts_as_one_text_field(self):
        parsed = {
            "source_description": "Cake stand for cupcakes and small cakes",
            "source_category": "Home > Kitchen",
            "source_specs": {"diameter": "180 mm", "height": "90 mm"},
            "source_tags": ["cake", "stand"],
            "author_name": "Designer A",
            "license_name": "Standard Digital File License",
            "source_price": 3.5,
            "source_currency": "USD",
            "custom_safe_fact": "three printable parts",
            "headers": {"Authorization": "secret"},
            "raw_html": "<html>huge</html>",
        }
        facts = {
            "source_description": parsed["source_description"],
            "source_category": parsed["source_category"],
            "source_specs": parsed["source_specs"],
            "source_tags": parsed["source_tags"],
            "author_name": parsed["author_name"],
            "license_name": parsed["license_name"],
            "source_price": parsed["source_price"],
            "source_currency": parsed["source_currency"],
        }
        text = phase31.structured_source_description(parsed, facts, "https://example.com/model/42")
        self.assertIn("## توضیحات منبع", text)
        self.assertIn("Cake stand for cupcakes", text)
        self.assertIn("## مشخصات و ویژگی‌ها", text)
        self.assertIn("diameter: 180 mm", text)
        self.assertIn("## مجوز", text)
        self.assertIn("custom_safe_fact: three printable parts", text)
        self.assertNotIn("Authorization", text)
        self.assertNotIn("<html>huge</html>", text)
        self.assertLessEqual(len(text), phase31.MAX_AI_SOURCE_TEXT)

    def test_build_product_updates_changes_editorial_fields_not_business_state(self):
        row = {
            "title_fa": "عنوان قدیمی",
            "source_title": "Cake Stand",
            "source_description": "old source",
            "selected_images_json": json.dumps(["https://img.example/1.jpg"]),
            "image_metadata_json": "[]",
            "homepage_slider_enabled": 0,
            "final_price": 900000,
            "stock_quantity": 7,
            "availability_status": "in_stock",
        }
        pack = {
            "title_fa": "استند کیک رومیزی",
            "short_description_fa": "توضیح کوتاه",
            "description_fa": "توضیح کامل و فارسی",
            "use_description_fa": "مناسب سرو کیک",
            "categories_fa": ["خانه و آشپزخانه"],
            "specs_fa": [{"key": "قطر", "value": "۱۸۰ میلی‌متر"}],
            "tags_fa": ["استند کیک"],
            "hashtags_fa": ["#استند_کیک"],
            "target_keywords_fa": ["خرید استند کیک"],
            "sales_bullets": ["چاپ سه‌بعدی سفارشی"],
            "image_alt_texts": ["استند کیک رومیزی - نمای اول"],
            "seo_title_fa": "خرید استند کیک رومیزی",
            "seo_description_fa": "استند کیک رومیزی برای سرو کیک و کاپ‌کیک",
            "social_caption_fa": "استند کیک رومیزی",
            "homepage_slider_seo": {},
        }
        extracted = {
            "source_title": "Cake Stand Small Table",
            "raw_source_description": "Source page description",
            "facts": {"estimated_weight_grams": 123.0, "estimated_print_minutes": 240.0},
        }
        updates, title = phase31.build_product_updates(row, pack, extracted)
        self.assertEqual(title, "استند کیک رومیزی")
        self.assertEqual(updates["source_title"], "Cake Stand Small Table")
        self.assertEqual(updates["estimated_weight_grams"], 123.0)
        self.assertEqual(updates["estimated_print_minutes"], 240.0)
        self.assertEqual(json.loads(updates["image_alt_texts_json"])[0], "استند کیک رومیزی - نمای اول")
        self.assertNotIn("final_price", updates)
        self.assertNotIn("stock_quantity", updates)
        self.assertNotIn("availability_status", updates)

    def test_selected_image_urls_is_bounded_and_falls_back_to_gallery(self):
        row = {
            "selected_images_json": "[]",
            "images_json": json.dumps([
                "https://img.example/1.jpg",
                "https://img.example/2.jpg",
                "local://3.jpg",
                "https://img.example/4.jpg",
                "https://img.example/5.jpg",
                "https://img.example/6.jpg",
            ]),
        }
        urls = phase31.selected_image_urls(row, limit=4)
        self.assertEqual(len(urls), 4)
        self.assertTrue(all(url.startswith("https://") for url in urls))

    def test_batch_and_single_ai_share_same_grounded_execution_function(self):
        source = open(phase31.__file__, "r", encoding="utf-8").read()
        self.assertIn("result = run_product_ai(self.app, self.product_id, provider, key, model)", source)
        self.assertIn("result = run_product_ai(self, product_id, provider, key, model)", source)
        self.assertIn("workspace_class._phase49_3e_run_all_ai = smart_ai", source)
        self.assertIn("workspace_class._phase49_3c_stage_ai = smart_ai", source)
        self.assertIn("workspace_class._phase49_3i21_link_refresh = smart_ai", source)


if __name__ == "__main__":
    unittest.main()
