from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.db import Database
from app.phase49_3b_guided_wizard import HERO_COLUMNS, STAGE_ORDER, STAGE_LABELS, ensure_schema


class Phase493BGuidedWizardTests(unittest.TestCase):
    def test_wizard_is_seven_stage_and_slider_is_separate(self):
        self.assertEqual(STAGE_ORDER, ("quick", "commerce", "images", "content", "specs", "slider", "publish"))
        self.assertEqual(STAGE_LABELS["slider"], "۶. اسلایدر صفحه اصلی")
        self.assertEqual(STAGE_LABELS["publish"], "۷. بررسی و انتشار")

    def test_hero_media_columns_upgrade_existing_windows_sqlite_additively(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Database(Path(tmp) / "catalog.sqlite3")
            try:
                before = db.conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()["c"]
                ensure_schema(db)
                columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
                for name in HERO_COLUMNS:
                    self.assertIn(name, columns)
                after = db.conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()["c"]
                self.assertEqual(before, after)
            finally:
                db.close()

    def test_guided_ui_contract_has_previous_next_required_stars_and_title_only_ai(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "app" / "phase49_3b_guided_wizard.py").read_text(encoding="utf-8")
        for token in (
            "← مرحله قبل",
            "مرحله بعد برای انتشار →",
            "★ الزامی برای ادامه",
            "✨ ترجمه فقط عنوان فارسی",
            "استودیوی اسلایدر صفحه اصلی",
            "پیش‌نمایش Desktop/Mobile",
            "homepage_slider_presentation_mode",
            "homepage_slider_position_x_percent",
            "homepage_slider_background_blur_px",
        ):
            self.assertIn(token, text)

    def test_launcher_verifies_phase49_3b_runtime_markers(self):
        root = Path(__file__).resolve().parents[1]
        launch = (root / "launch.py").read_text(encoding="utf-8")
        for marker in (
            "EPIC49_GUIDED_WIZARD_7_STAGE=ENABLED",
            "EPIC49_HERO_MEDIA_STUDIO=ENABLED",
            "EPIC49_AI_PROVIDER_HUB=ENABLED",
            "EPIC49_OPENROUTER=ENABLED",
            "EPIC49_PERSISTENT_DIAGNOSTICS=ENABLED",
            "EPIC49_DIAGNOSTIC_LOG_UI=ENABLED",
        ):
            self.assertIn(marker, launch)


if __name__ == "__main__":
    unittest.main()
