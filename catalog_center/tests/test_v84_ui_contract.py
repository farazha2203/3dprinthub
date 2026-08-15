from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class V84UIContractTests(unittest.TestCase):
    def test_provider_controls_and_live_test_exist(self):
        text = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
        for token in [
            "self.ai_provider", "values=[\"auto\",\"avalai\",\"openai\"]",
            "command=self.load_ai_models", "command=self.test_openai_api",
            "command=self.migrate_ai_key_file", "دریافت مدل‌ها", "تست زنده AI",
        ]:
            self.assertIn(token, text)

    def test_content_studio_surfaces_hashtags_and_material_recommendations(self):
        text = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
        self.assertIn("hashtags_fa_json", text)
        self.assertIn("material_recommendations_json", text)
        self.assertIn("هشتگ‌های پیشنهادی", text)
        self.assertIn("پیشنهاد متریال", text)

    def test_local_skills_are_packaged(self):
        self.assertTrue((ROOT / "skills" / "avalai-provider" / "SKILL.md").is_file())
        self.assertTrue((ROOT / "skills" / "extract-web-data-python" / "SKILL.md").is_file())
    def test_product_studio_uses_selected_ai_provider(self):
        text = (ROOT / "app" / "product_studio.py").read_text(encoding="utf-8")
        self.assertIn("provider = self.app._selected_ai_provider()", text)
        self.assertIn("OpenAIContentService(key, model, provider)", text)

    def test_legacy_translate_path_is_provider_aware(self):
        text = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
        block = text.split("    def translate_product(self):", 1)[1].split("    def _selected_batch_images", 1)[0]
        self.assertIn("provider=self._selected_ai_provider()", block)
        self.assertIn("AIContentService(key,self.ai_model.get().strip(),provider)", block)
        self.assertNotIn("openai_translate(", block)

