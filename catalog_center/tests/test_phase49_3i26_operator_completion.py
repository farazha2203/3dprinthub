from __future__ import annotations

import json
import unittest
from pathlib import Path

from app import phase49_3i26_operator_completion as phase


class Phase493I26OperatorCompletionTests(unittest.TestCase):
    def test_canonical_stage_order_is_restored(self):
        self.assertEqual(
            phase.CANONICAL_STAGE_ORDER,
            ("quick", "commerce", "images", "content", "specs", "slider", "publish"),
        )
        self.assertEqual(phase.WORKSPACE_SECTIONS[0][0], "quick")
        self.assertEqual(phase.WORKSPACE_SECTIONS[3][0], "content")

    def test_exact_link_timeout_is_two_minutes(self):
        self.assertEqual(phase.AI_TIMEOUT_SECONDS, 120)
        self.assertEqual(phase.PROGRESS["queued"], 3)
        self.assertEqual(phase.PROGRESS["completed"], 100)

    def test_acquisition_default_is_five_images(self):
        self.assertEqual(phase.DEFAULT_IMAGE_LIMIT, 5)
        limits = Path(phase.__file__).with_name("phase49_3h_image_limits.py").read_text(encoding="utf-8")
        self.assertIn("DEFAULT_IMAGE_LIMIT = 5", limits)
        self.assertIn("HARD_MAX_IMAGE_LIMIT = 20", limits)

    def test_unified_ai_does_not_send_image_urls(self):
        source = Path(phase.__file__).read_text(encoding="utf-8")
        start = source.index("def _run_unified_link_refresh")
        end = source.index("def install_workspace")
        implementation = source[start:end]
        self.assertIn("image_urls=[]", implementation)
        self.assertIn('"images_sent_to_ai": 0', implementation)
        self.assertNotIn("workspace._phase49_3i18_apply_ai", implementation)

    def test_unified_path_builds_image_text_metadata(self):
        source = Path(phase.__file__).read_text(encoding="utf-8")
        self.assertIn("_build_local_image_metadata", source)
        self.assertIn('item["alt_text"]', source)
        self.assertIn('item["seo_filename"]', source)
        self.assertIn('item["caption"]', source)
        self.assertIn('item["keywords"]', source)
        self.assertIn("strict_source_local_image", source)
        self.assertIn("no network image download attempted by AI completion", source)

    def test_gallery_final_override_is_vertical_five_columns(self):
        source = Path(phase.__file__).read_text(encoding="utf-8")
        self.assertIn("index // 5", source)
        self.assertIn("index % 5", source)
        self.assertIn("canvas.yview_scroll", source)
        self.assertIn("_phase49_3g_layout_gallery_cards = vertical_3g_layout", source)

    def test_product_archive_and_block_are_distinct(self):
        source = Path(phase.__file__).read_text(encoding="utf-8")
        self.assertIn('"workflow_status": "archived"', source)
        self.assertIn("self.db.block_product(product_id", source)
        self.assertIn("source identity retained to prevent re-import", source)

    def test_source_screenshot_is_extra_local_gallery_item(self):
        source = Path(phase.__file__).read_text(encoding="utf-8")
        self.assertIn('local_url = "local://source-page-screenshot.png"', source)
        self.assertIn("collect_classic_exact", source)
        self.assertIn("result[\"images_json\"]", source)

    def test_progress_has_recheck_path_after_timeout(self):
        source = Path(phase.__file__).read_text(encoding="utf-8")
        self.assertIn('"source_recheck"', source)
        self.assertIn("crawler.public_http(source_url, 20)", source)
        self.assertIn("لینک منبع سالم است", source)


if __name__ == "__main__":
    unittest.main()
