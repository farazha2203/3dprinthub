from __future__ import annotations

import inspect
import sqlite3
import unittest
from pathlib import Path

from app.epic49_desktop_schema import ensure_epic49_desktop_schema
from app.openai_content import CONTENT_SCHEMA
from app.product_workspace_v871 import ProductWorkspace


ROOT = Path(__file__).resolve().parents[1]


class _DB:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("CREATE TABLE products(id INTEGER PRIMARY KEY)")


class V871SliderSeoTests(unittest.TestCase):
    def test_desktop_schema_adds_dedicated_slider_seo_fields_non_destructively(self):
        db = _DB()
        ensure_epic49_desktop_schema(db)
        names = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
        for name in {
            "homepage_slider_enabled",
            "homepage_slider_image_url",
            "homepage_slider_title_fa",
            "homepage_slider_description_fa",
            "homepage_slider_alt_text",
            "homepage_slider_button_text",
            "homepage_slider_focus_keyword",
        }:
            self.assertIn(name, names)

    def test_ai_schema_requires_independent_homepage_slider_seo_pack(self):
        slider = CONTENT_SCHEMA["properties"]["homepage_slider_seo"]
        self.assertIn("homepage_slider_seo", CONTENT_SCHEMA["required"])
        self.assertFalse(slider["additionalProperties"])
        self.assertEqual(
            set(slider["required"]),
            {"title_fa", "description_fa", "image_alt_fa", "button_text_fa", "focus_keyword_fa"},
        )
        source = (ROOT / "app" / "openai_content.py").read_text(encoding="utf-8")
        self.assertIn("separate homepage hero content pack", source)
        self.assertIn("without keyword stuffing", source)

    def test_workspace_exposes_direct_gallery_slider_selection_and_editable_copy(self):
        source = inspect.getsource(ProductWorkspace)
        for marker in [
            "set_slider_image_from_gallery",
            "انتخاب برای اسلایدر",
            "homepage_slider_title_fa",
            "homepage_slider_description_fa",
            "homepage_slider_alt_text",
            "homepage_slider_button_text",
            "homepage_slider_focus_keyword",
            "تولید/بازسازی با هوش مصنوعی",
        ]:
            self.assertIn(marker, source)

    def test_launchers_and_portable_verify_preserve_v871_through_final_epic49_workspace(self):
        launch = (ROOT / "launch.py").read_text(encoding="utf-8")
        portable = (ROOT / "portable_entry.py").read_text(encoding="utf-8")
        epic49 = (ROOT / "app" / "product_workspace_epic49.py").read_text(encoding="utf-8")

        self.assertIn("from app.product_workspace_epic49 import ProductWorkspace", launch)
        self.assertIn("from app.product_workspace_epic49 import ProductWorkspace", portable)
        self.assertIn("from .product_workspace_v871 import ProductWorkspace as ProductWorkspace871", epic49)
        self.assertIn("class ProductWorkspace(ProductWorkspace871):", epic49)
        self.assertIn("PRODUCT_WORKSPACE_V871=ENABLED", launch)
        self.assertIn("HOMEPAGE_SLIDER_SEO_V871=ENABLED", launch)
        self.assertIn('"homepage_slider_seo_v871"', portable)

    def test_server_sync_reads_operator_fields_and_ai_pack_fallback(self):
        source = (ROOT.parent / "store" / "epic49_publish_options.py").read_text(encoding="utf-8")
        for marker in [
            "def _homepage_slider_seo",
            'content_pack.get("homepage_slider_seo")',
            'data.get("homepage_slider_title_fa")',
            'data.get("homepage_slider_description_fa")',
            'data.get("homepage_slider_alt_text")',
            'data.get("homepage_slider_button_text")',
            '"title_override": slider_seo["title_fa"]',
            '"image_alt_text": slider_seo["image_alt_fa"]',
            '"button_text": slider_seo["button_text_fa"]',
        ]:
            self.assertIn(marker, source)


if __name__ == "__main__":
    unittest.main()
