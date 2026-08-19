from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.epic49_desktop_schema import PRODUCT_COLUMNS, ensure_epic49_desktop_schema
from app.epic49_site_sync import BridgeConflictError
from app.product_workspace_epic49 import ProductWorkspace
from app.product_workspace_v871 import ProductWorkspace as ProductWorkspace871


class _DB:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("CREATE TABLE products(id INTEGER PRIMARY KEY)")
        self.conn.commit()

    def close(self):
        self.conn.close()


class Epic49UnifiedDesktopTests(unittest.TestCase):
    def test_desktop_schema_is_additive_and_contains_unified_slider_revision_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = _DB(Path(tmp) / "catalog.sqlite3")
            try:
                ensure_epic49_desktop_schema(db)
                columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
                expected = {
                    "homepage_slider_title_fa",
                    "homepage_slider_description_fa",
                    "homepage_slider_alt_text",
                    "homepage_slider_button_text",
                    "homepage_slider_focus_keyword",
                    "homepage_slider_transition_effect",
                    "homepage_slider_transition_duration_ms",
                    "homepage_slider_display_duration_ms",
                    "server_product_id",
                    "server_product_revision",
                    "server_slider_id",
                    "server_slider_revision",
                    "server_updated_at",
                    "last_sync_conflict",
                }
                self.assertTrue(expected.issubset(columns))
                self.assertTrue(expected.issubset(PRODUCT_COLUMNS))
                # Running the additive installer twice must be safe for employee PCs.
                ensure_epic49_desktop_schema(db)
                columns2 = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
                self.assertEqual(columns, columns2)
            finally:
                db.close()

    def test_unified_workspace_extends_v871_instead_of_replacing_existing_product_studio(self):
        self.assertTrue(issubclass(ProductWorkspace, ProductWorkspace871))
        for method in (
            "preview_slider_effect",
            "refresh_current_from_server",
            "open_all_server_sliders",
            "save",
            "reload",
        ):
            self.assertTrue(hasattr(ProductWorkspace, method), method)

    def test_windows_sources_expose_slider_seo_effect_timing_and_same_bridge(self):
        root = Path(__file__).resolve().parents[1]
        workspace = (root / "app" / "product_workspace_epic49.py").read_text(encoding="utf-8")
        v871 = (root / "app" / "product_workspace_v871.py").read_text(encoding="utf-8")
        client = (root / "app" / "epic49_site_sync.py").read_text(encoding="utf-8")
        main = (root / "app" / "main.py").read_text(encoding="utf-8")
        launch = (root / "launch.py").read_text(encoding="utf-8")

        for marker in (
            "homepage_slider_title_fa",
            "homepage_slider_description_fa",
            "homepage_slider_alt_text",
            "homepage_slider_button_text",
            "homepage_slider_focus_keyword",
            "انتخاب برای اسلایدر",
        ):
            self.assertIn(marker, v871)
        for marker in (
            "homepage_slider_transition_effect",
            "homepage_slider_transition_duration_ms",
            "homepage_slider_display_duration_ms",
            "پیش‌نمایش افکت",
            "دریافت نسخه فعلی این کالا از سایت",
            "مدیریت همه اسلایدرهای سایت",
        ):
            self.assertIn(marker, workspace)
        self.assertIn('/api/catalog-bridge/v1/', client)
        self.assertIn('hero-slides/', client)
        self.assertIn('products/', client)
        self.assertIn('editorial={k:r[k] for k in r.keys()', main)
        self.assertIn('product_workspace_epic49', launch)
        self.assertIn('EPIC49_UNIFIED_SYNC=ENABLED', launch)

    def test_conflict_error_is_structured_for_employee_ui(self):
        error = BridgeConflictError({
            "entity": "hero:9",
            "expected_revision": 3,
            "current_revision": 4,
        })
        text = str(error)
        self.assertIn("نسخه سایت جدیدتر است", text)
        self.assertIn("hero:9", text)
        self.assertIn("local=3", text)
        self.assertIn("server=4", text)

    def test_ai_schema_keeps_slider_seo_separate_from_product_seo(self):
        source = (Path(__file__).resolve().parents[1] / "app" / "openai_content.py").read_text(encoding="utf-8")
        self.assertIn('"homepage_slider_seo"', source)
        for marker in ('"title_fa"', '"description_fa"', '"image_alt_fa"', '"button_text_fa"', '"focus_keyword_fa"'):
            self.assertIn(marker, source)


if __name__ == "__main__":
    unittest.main()
