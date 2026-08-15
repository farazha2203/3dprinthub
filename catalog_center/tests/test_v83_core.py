from __future__ import annotations

import inspect
import json
import tempfile
import unittest
from pathlib import Path

from app.db import Database
from app.openai_content import OpenAIContentService


class V83Contracts(unittest.TestCase):
    def test_openai_content_supports_translate_and_commerce_modes(self):
        sig = inspect.signature(OpenAIContentService.enrich_product)
        self.assertIn("mode", sig.parameters)
        text = Path(__file__).resolve().parents[1].joinpath("app", "openai_content.py").read_text(encoding="utf-8")
        self.assertIn('mode == "translate"', text)
        self.assertIn("precise Persian technical translator", text)
        self.assertIn("Persian ecommerce content editor", text)

    def test_product_studio_has_fast_publish_and_gallery_contract(self):
        text = Path(__file__).resolve().parents[1].joinpath("app", "product_studio.py").read_text(encoding="utf-8")
        for required in [
            "class ProductStudio", "def refresh_gallery", "def set_primary", "def toggle_selected",
            "def remove_image", "def add_local_images", "def add_url_image", "def generate_ai",
            "def preview_ai_pack", "def add_category", "def queue_for_publish", "لینک منبع",
            "ترجمه دقیق EN → FA", "تولید محتوای فروشگاهی",
        ]:
            self.assertIn(required, text)

    def test_custom_categories_can_live_in_db_settings_without_schema_change(self):
        with tempfile.TemporaryDirectory() as td:
            db = Database(Path(td) / "catalog.sqlite3")
            db.set_setting("custom_categories_json", json.dumps([{"slug": "car-interior", "name": "خودرو - قطعات داخلی"}], ensure_ascii=False))
            value = json.loads(db.setting("custom_categories_json"))
            self.assertEqual(value[0]["slug"], "car-interior")
            db.close()

    def test_v83_server_ack_marker(self):
        text = Path(__file__).resolve().parents[1].joinpath("server", "store", "management", "commands", "phase37_import_catalog_center.py").read_text(encoding="utf-8")
        self.assertIn('"schema_version": "8.3"', text)
        self.assertIn("CATALOG_INTELLIGENCE_V8_3_IMPORT=OK", text)
        self.assertIn("local_category_name", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
