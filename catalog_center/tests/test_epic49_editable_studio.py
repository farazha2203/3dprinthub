from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from app.epic49_product_studio import (
    LICENSE_CODE_TO_LABEL,
    LICENSE_LABEL_TO_CODE,
    ProductStudio,
    parse_json_list,
    unique_lines,
)
from app.v8_features import commercial_license_allows_publish


ROOT = Path(__file__).resolve().parents[1]


class Epic49EditableContentTests(unittest.TestCase):
    def test_unique_lines_supports_add_edit_delete_semantics(self):
        self.assertEqual(
            unique_lines("PLA\nPETG\n\nPLA\nASA  \n"),
            ["PLA", "PETG", "ASA"],
        )

    def test_material_recommendations_require_json_array(self):
        self.assertEqual(parse_json_list('[{"material":"ASA"}]', field_name="مواد"), [{"material": "ASA"}])
        with self.assertRaises(ValueError):
            parse_json_list('{"material":"ASA"}', field_name="مواد")

    def test_content_ui_exposes_real_editors_and_list_actions(self):
        source = inspect.getsource(ProductStudio._content_ui)
        for token in (
            "content_categories_fa",
            "content_tags_fa",
            "content_hashtags_fa",
            "content_keywords",
            "content_materials",
            "content_colors",
            "content_sales_bullets",
            "content_image_alts",
            "content_seo_title",
            "content_seo_desc",
            "content_social_caption",
            "content_material_recommendations",
        ):
            self.assertIn(token, source)
        helper = inspect.getsource(ProductStudio._list_editor)
        self.assertIn("+ افزودن مورد", helper)
        self.assertIn("− حذف خط جاری", helper)
        self.assertIn("پاک‌کردن همه", helper)

    def test_extended_save_persists_ai_content_fields(self):
        source = inspect.getsource(ProductStudio.save)
        for field in (
            "categories_fa_json",
            "tags_fa_json",
            "hashtags_fa_json",
            "keywords_json",
            "materials_json",
            "colors_json",
            "seo_title_fa",
            "seo_description_fa",
            "social_caption_fa",
            "sales_bullets_json",
            "image_alt_texts_json",
            "material_recommendations_json",
            "content_pack_json",
        ):
            self.assertIn(field, inspect.getsource(ProductStudio._extended_content_values) + source)


class Epic49EditablePublishTests(unittest.TestCase):
    def test_license_labels_map_to_stable_server_codes(self):
        self.assertEqual(LICENSE_LABEL_TO_CODE["مجاز برای فروش"], "allowed")
        self.assertEqual(LICENSE_LABEL_TO_CODE["متعلق به 3DPrintHub"], "owned")
        self.assertEqual(LICENSE_LABEL_TO_CODE["مالکیت عمومی"], "public_domain")
        self.assertEqual(LICENSE_CODE_TO_LABEL["review"], "نیازمند بررسی")

    def test_commercial_gate_stays_fail_closed(self):
        self.assertFalse(commercial_license_allows_publish("review"))
        self.assertFalse(commercial_license_allows_publish("blocked"))
        self.assertTrue(commercial_license_allows_publish("allowed"))
        self.assertTrue(commercial_license_allows_publish("owned"))
        self.assertTrue(commercial_license_allows_publish("public_domain"))

    def test_publish_tab_has_editable_approval_destination_and_license(self):
        source = inspect.getsource(ProductStudio._publish_ui)
        self.assertIn("approved_var", source)
        self.assertIn("publish_product_var", source)
        self.assertIn("publish_portfolio_var", source)
        self.assertIn("publish_license_label_var", source)
        self.assertIn("ذخیره تنظیمات انتشار", source)
        self.assertIn("ارسال همین محصول به سایت", source)

    def test_publish_flow_saves_visible_controls_before_validation(self):
        source = inspect.getsource(ProductStudio.queue_for_publish)
        self.assertIn("self.save(silent=True)", source)
        self.assertIn("publish_as_product", source)
        self.assertIn("publish_as_portfolio", source)
        self.assertIn("commercial_license_allows_publish", source)
        self.assertIn("approved_for_sale", source)


class Epic49StudioActivationTests(unittest.TestCase):
    def test_normal_launcher_activates_enhanced_studio(self):
        source = (ROOT / "launch.py").read_text(encoding="utf-8")
        self.assertIn("app.epic49_product_studio", source)
        self.assertIn("app_module.ProductStudio = Epic49ProductStudio", source)
        self.assertIn("PRODUCT_STUDIO_EPIC49=ENABLED", source)

    def test_portable_exe_activates_and_verifies_enhanced_studio(self):
        source = (ROOT / "portable_entry.py").read_text(encoding="utf-8")
        self.assertIn("app_main.ProductStudio = Epic49ProductStudio", source)
        self.assertIn('"product_studio_epic49"', source)


if __name__ == "__main__":
    unittest.main()
