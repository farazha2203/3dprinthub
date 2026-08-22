from __future__ import annotations

import json
import sqlite3
import unittest
from pathlib import Path

from app.phase49_3g_workspace_usability import (
    GROUP_FIELDS,
    ai_group_locked,
    disabled_groups,
    ensure_schema,
    filter_updates_for_ai_ownership,
    group_changed_fields,
    group_snapshot,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app" / "phase49_3g_workspace_usability.py"
SELECTED_IMAGE_AI = ROOT / "app" / "phase49_3f_selected_image_ai.py"
SOURCE_GUARD = ROOT / "app" / "phase49_3f_source_refresh_guard.py"
LAUNCHER = ROOT / "launch.py"


class _Db:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("CREATE TABLE products (id INTEGER PRIMARY KEY)")
        self.conn.execute("INSERT INTO products(id) VALUES(1)")
        self.conn.commit()


class Phase493GProvenanceTests(unittest.TestCase):
    def test_schema_is_additive_and_local_only(self):
        db = _Db()
        try:
            ensure_schema(db)
            columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
            self.assertIn("ai_provenance_json", columns)
            self.assertIn("ai_disabled_groups_json", columns)
            self.assertEqual(db.conn.execute("SELECT ai_provenance_json FROM products WHERE id=1").fetchone()[0], "{}")
            self.assertEqual(db.conn.execute("SELECT ai_disabled_groups_json FROM products WHERE id=1").fetchone()[0], "[]")
        finally:
            db.conn.close()

    def test_disabled_group_blocks_only_that_groups_ai_updates(self):
        row = {
            "ai_disabled_groups_json": json.dumps(["product_seo"], ensure_ascii=False),
            "ai_provenance_json": "{}",
        }
        updates = {
            "title_fa": "عنوان فارسی",
            "seo_title_fa": "سئوی فارسی",
            "seo_description_fa": "توضیح سئو",
            "material_recommendations_json": "[]",
        }
        filtered = filter_updates_for_ai_ownership(row, updates)
        self.assertEqual(filtered["title_fa"], "عنوان فارسی")
        self.assertNotIn("seo_title_fa", filtered)
        self.assertNotIn("seo_description_fa", filtered)
        self.assertIn("material_recommendations_json", filtered)
        self.assertEqual(disabled_groups(row), {"product_seo"})

    def test_manual_override_locks_group_until_operator_releases_it(self):
        row = {
            "ai_disabled_groups_json": "[]",
            "ai_provenance_json": json.dumps({
                "persian_content": {"source": "manual", "manual_override": True}
            }, ensure_ascii=False),
        }
        self.assertTrue(ai_group_locked(row, "persian_content"))
        filtered = filter_updates_for_ai_ownership(row, {
            "title_fa": "AI title",
            "short_description_fa": "AI short",
            "seo_title_fa": "SEO can still change",
        })
        self.assertNotIn("title_fa", filtered)
        self.assertNotIn("short_description_fa", filtered)
        self.assertEqual(filtered["seo_title_fa"], "SEO can still change")

    def test_snapshot_is_semantic_for_json_and_detects_real_manual_change(self):
        before = {
            "seo_title_fa": "عنوان",
            "seo_description_fa": "توضیح",
            "keywords_json": '["الف", "ب"]',
            "tags_fa_json": '["تگ"]',
            "hashtags_fa_json": '["هشتگ"]',
        }
        same = dict(before)
        same["keywords_json"] = '[ "الف", "ب" ]'
        changed = dict(before)
        changed["seo_title_fa"] = "عنوان دستی جدید"
        self.assertEqual(group_snapshot(before, "product_seo"), group_snapshot(same, "product_seo"))
        self.assertNotEqual(group_snapshot(before, "product_seo"), group_snapshot(changed, "product_seo"))
        self.assertEqual(group_changed_fields(before, changed, "product_seo"), ["seo_title_fa"])

    def test_group_contract_covers_requested_ai_task_ownership(self):
        self.assertEqual(set(GROUP_FIELDS), {"persian_content", "product_seo", "image_seo", "materials", "slider_seo"})
        self.assertIn("image_metadata_json", GROUP_FIELDS["image_seo"])
        self.assertIn("homepage_slider_focus_keyword", GROUP_FIELDS["slider_seo"])


class Phase493GSourceContractTests(unittest.TestCase):
    def test_workspace_has_vertical_scroll_and_horizontal_gallery_contract(self):
        source = MODULE.read_text(encoding="utf-8")
        self.assertIn("_phase49_3g_enable_workspace_scroll", source)
        self.assertIn("orient=\"vertical\"", source)
        self.assertIn("_phase49_3g_scroll_command", source)
        self.assertIn("_phase49_3g_enable_gallery_scroll", source)
        self.assertIn("orient=\"horizontal\"", source)
        self.assertIn("card.grid(row=0, column=index", source)
        self.assertIn("canvas.configure(xscrollcommand=hbar.set", source)

    def test_compact_commerce_and_autofill_controls_are_present(self):
        source = MODULE.read_text(encoding="utf-8")
        self.assertIn("_phase49_3g_compact_commerce", source)
        self.assertIn("use_description_text\", 3", source)
        self.assertIn("material_rate_tree", source)
        self.assertIn("✨ تکمیل هوشمند محصول با AI", source)
        self.assertIn("AI فقط فیلدهای خالی و مجاز را تکمیل می‌کند", source)

    def test_provenance_ui_exposes_disable_and_manual_rewrite_controls(self):
        source = MODULE.read_text(encoding="utf-8")
        self.assertIn("مالکیت و وضعیت هوش مصنوعی", source)
        self.assertIn("خاموش/روشن AI", source)
        self.assertIn("اجازه بازنویسی AI", source)
        self.assertIn("manual_override", source)
        self.assertIn("snapshot_hash", source)

    def test_selected_image_ai_remains_text_only(self):
        source = SELECTED_IMAGE_AI.read_text(encoding="utf-8")
        self.assertIn("input_text", source)
        self.assertNotIn('"input_image"', source)
        self.assertNotIn("image_url", source)

    def test_3g_installs_only_at_real_launcher_boundary_after_3f_guard(self):
        launcher = LAUNCHER.read_text(encoding="utf-8")
        guard = SOURCE_GUARD.read_text(encoding="utf-8")
        self.assertIn("install_phase49_3g_workspace(ProductWorkspace, readiness_module)", launcher)
        self.assertLess(
            launcher.index("install_phase49_3f_source_refresh_guard(ProductWorkspace)"),
            launcher.index("install_phase49_3g_workspace(ProductWorkspace, readiness_module)"),
        )
        self.assertNotIn("phase49_3g_workspace_usability", guard)
        self.assertNotIn("install_phase49_3g_workspace", guard)


if __name__ == "__main__":
    unittest.main()
