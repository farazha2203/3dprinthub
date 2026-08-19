from __future__ import annotations

import unittest
from pathlib import Path

from app.phase49_3d_workflow_hardening import (
    clean_model_id,
    model_matches,
    needs_auto_prepare,
    normalize_price_range,
)
from app.phase49_3c_image_pipeline import MAX_SOURCE_IMAGES, cap_unique_urls


class Phase493DWorkflowPureTests(unittest.TestCase):
    def test_decorated_model_label_is_never_persisted_as_model_id(self):
        self.assertEqual(
            clean_model_id("openai/gpt-5.4 • $1.000/$2.000 per 1M"),
            "openai/gpt-5.4",
        )
        self.assertEqual(clean_model_id("openrouter/free • رایگان"), "openrouter/free")

    def test_chatgpt_search_alias_finds_gpt_models(self):
        gpt = {"id": "openai/gpt-5.4", "name": "GPT-5.4", "free": False}
        claude = {"id": "anthropic/claude-sonnet", "name": "Claude Sonnet", "free": False}
        self.assertTrue(model_matches("CHATGPT", gpt))
        self.assertTrue(model_matches("gpt", gpt))
        self.assertFalse(model_matches("CHATGPT", claude))

    def test_price_range_normalization_is_operator_friendly(self):
        self.assertEqual(normalize_price_range("450000", "650000", 0), (450000, 650000))
        self.assertEqual(normalize_price_range("650000", "450000", 0), (450000, 650000))
        self.assertEqual(normalize_price_range("450000", "", 0), (450000, 450000))
        self.assertEqual(normalize_price_range("", "", 500000), (500000, 500000))

    def test_auto_prepare_only_when_editorial_content_is_incomplete(self):
        complete = {
            "title_fa": "استند نمایش سه‌بعدی",
            "translation_status": "reviewed",
            "content_status": "ready",
            "short_description_fa": "استند کاربردی برای نمایش محصول و استفاده روی میز.",
            "description_fa": "<p>این استند برای نمایش منظم محصول و استفاده دکوراتیو طراحی شده است.</p>",
            "use_description": "مناسب برای نمایش محصول روی میز، ویترین و محیط فروشگاهی.",
            "seo_title_fa": "خرید استند نمایش سه‌بعدی",
            "seo_description_fa": "مشخصات و گزینه‌های سفارش استند نمایش سه‌بعدی را بررسی کنید.",
            "keywords_json": '["خرید استند سه‌بعدی","سفارش استند نمایش","قیمت استند سه‌بعدی"]',
            "tags_fa_json": '["استند نمایش","چاپ سه‌بعدی"]',
            "hashtags_fa_json": '["#چاپ_سه_بعدی","#استند_نمایش"]',
        }
        self.assertFalse(needs_auto_prepare(complete))
        incomplete = dict(complete)
        incomplete["seo_title_fa"] = ""
        self.assertTrue(needs_auto_prepare(incomplete))
        generic = dict(complete)
        generic["title_fa"] = "محصول چاپ سه‌بعدی"
        self.assertTrue(needs_auto_prepare(generic))

    def test_user_image_limit_is_respected_below_hard_cap(self):
        urls = [f"https://cdn.example.test/{i}.jpg" for i in range(30)]
        self.assertEqual(len(cap_unique_urls(urls, limit=5)), 5)
        self.assertEqual(len(cap_unique_urls(urls, limit=100)), MAX_SOURCE_IMAGES)
        self.assertEqual(MAX_SOURCE_IMAGES, 10)


class Phase493DSourceContractTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]

    def test_workspace_layout_fix_uses_grid_for_quick_tab_parent(self):
        text = (self.root / "app" / "phase49_3d_workflow_hardening.py").read_text(encoding="utf-8")
        start = text.index("def _phase49_3b_add_title_ai")
        end = text.index("workspace_class._phase49_3b_add_title_ai", start)
        block = text[start:end]
        self.assertIn("holder.grid(", block)
        self.assertNotIn("holder.pack(", block)

    def test_ai_picker_provider_and_publish_preflight_contracts_are_present(self):
        text = (self.root / "app" / "phase49_3d_workflow_hardening.py").read_text(encoding="utf-8")
        for token in (
            "جستجو و انتخاب مدل",
            "CHATGPT",
            "ttk.Radiobutton",
            "ذخیره Provider و مدل فعال",
            "تست اتصال Provider/Model فعال",
            "ai_auto_prepare_on_open",
            "similar_editorial_keywords",
            "finalize_selected_images",
            "preflight_blocked",
            "هیچ Batch/FTP/Import اجرا نشد",
        ):
            self.assertIn(token, text)

    def test_price_range_is_present_in_desktop_server_and_public_templates(self):
        desktop = (self.root / "app" / "epic49_desktop_schema.py").read_text(encoding="utf-8")
        project = self.root.parent
        profile = (project / "store" / "epic49_catalog_profile.py").read_text(encoding="utf-8")
        detail = (project / "templates" / "store" / "product_detail.html").read_text(encoding="utf-8")
        listing = (project / "templates" / "store" / "product_list.html").read_text(encoding="utf-8")
        for text in (desktop, profile):
            self.assertIn("price_min", text)
            self.assertIn("price_max", text)
        self.assertIn("بازه قیمت", detail)
        self.assertIn("product.catalog_profile.price_max", listing)

    def test_launcher_exposes_phase49_3d_markers(self):
        text = (self.root / "launch.py").read_text(encoding="utf-8")
        for marker in (
            "EPIC49_3D_WORKSPACE_LAYOUT_FIX=ENABLED",
            "EPIC49_3D_AI_MODEL_PICKER=ENABLED",
            "EPIC49_3D_ACTIVE_PROVIDER_PERSISTENCE=ENABLED",
            "EPIC49_3D_AUTO_AI_PREPARE=ENABLED",
            "EPIC49_3D_LOCAL_PUBLISH_PREFLIGHT=ENABLED",
            "EPIC49_3D_PRICE_RANGE_CONTRACT=ENABLED",
            "EPIC49_3D_IMAGE_LIMIT_PRESERVED=ENABLED",
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
