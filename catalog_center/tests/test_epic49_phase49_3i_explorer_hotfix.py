from __future__ import annotations

import unittest
from pathlib import Path

from app.phase49_3i_explorer_hotfix import (
    DEFAULT_VIEW_MODE,
    VIEW_MODES,
    matches_source_product_url,
    normalize_view_mode,
)


ROOT = Path(__file__).resolve().parents[1]
MAKERWORLD_PATTERN = r"https?://(?:www\.)?makerworld\.com/(?:[a-z]{2}/)?models/(?P<external_id>\d+)[^\s\"'<>]*"
PRODUCT_URL = "https://makerworld.com/en/models/2834255-cake-stand-small-table-great-for-cakes-cupcakes?from=search#profileId-3158565"
GROUP_URL = "https://makerworld.com/en/3d-models/household"
SEARCH_URL = "https://makerworld.com/en/search/models?keyword=cake+stand"


class Phase493IExplorerHotfixTests(unittest.TestCase):
    def test_view_modes_match_windows_explorer_operator_contract(self):
        self.assertEqual(DEFAULT_VIEW_MODE, "large")
        self.assertEqual(
            [VIEW_MODES[key]["label"] for key in VIEW_MODES],
            ["آیکن خیلی بزرگ", "آیکن بزرگ", "آیکن متوسط", "آیکن کوچک", "لیست"],
        )
        self.assertEqual(normalize_view_mode("unknown"), "large")
        self.assertEqual(normalize_view_mode("list"), "list")

    def test_product_url_is_distinguished_from_group_or_search_url_by_source_pattern(self):
        self.assertTrue(matches_source_product_url(PRODUCT_URL, MAKERWORLD_PATTERN))
        self.assertFalse(matches_source_product_url(GROUP_URL, MAKERWORLD_PATTERN))
        self.assertFalse(matches_source_product_url(SEARCH_URL, MAKERWORLD_PATTERN))

    def test_invalid_or_empty_pattern_fails_closed_as_not_product(self):
        self.assertFalse(matches_source_product_url(PRODUCT_URL, ""))
        self.assertFalse(matches_source_product_url("not-a-url", MAKERWORLD_PATTERN))
        self.assertFalse(matches_source_product_url(PRODUCT_URL, "[invalid"))

    def test_thumbnail_uses_pixel_holder_not_text_unit_image_label_dimensions(self):
        source = (ROOT / "app" / "phase49_3i_explorer_hotfix.py").read_text(encoding="utf-8")
        self.assertIn("image_holder = tk.Frame(card, width=thumb_w, height=thumb_h", source)
        self.assertIn("image_holder.pack_propagate(False)", source)
        self.assertIn("image_label = tk.Label(\n                image_holder,", source)
        image_label_block = source.split("image_label = tk.Label(", 1)[1].split(")\n            image_label.pack", 1)[0]
        self.assertNotIn("width=", image_label_block)
        self.assertNotIn("height=", image_label_block)

    def test_multiselect_context_menu_and_safe_queue_removal_contract_exist(self):
        source = (ROOT / "app" / "phase49_3i_explorer_hotfix.py").read_text(encoding="utf-8")
        self.assertIn("state & 0x0004", source)
        self.assertIn("state & 0x0001", source)
        self.assertIn('"<Button-3>"', source)
        self.assertIn('label=f"حذف از صف انتشار ({len(selected)})"', source)
        self.assertIn('{"upload_ready": 0, "workflow_status": "review"}', source)
        self.assertNotIn("delete_product", source)
        self.assertNotIn("block_product", source)

    def test_view_mode_persists_in_existing_catalog_settings(self):
        source = (ROOT / "app" / "phase49_3i_explorer_hotfix.py").read_text(encoding="utf-8")
        self.assertIn('VIEW_SETTING_KEY = "phase49_3i_product_view_mode"', source)
        self.assertIn("self.db.setting(VIEW_SETTING_KEY", source)
        self.assertIn("self.db.set_setting(VIEW_SETTING_KEY, key)", source)

    def test_direct_link_router_uses_source_model_pattern_before_full_fetch(self):
        source = (ROOT / "app" / "phase49_3i_explorer_hotfix.py").read_text(encoding="utf-8")
        self.assertIn('source["model_url_pattern"]', source)
        self.assertIn("matches_source_product_url(url, pattern)", source)
        self.assertIn("return self.start_candidate_discovery()", source)
        self.assertIn("return original_direct_link(self)", source)
        self.assertIn("PHASE49_3I_URL_ROUTE=direct_product", source)
        self.assertIn("PHASE49_3I_URL_ROUTE=preview_listing", source)

    def test_explorer_hotfix_is_composed_after_original_product_gallery(self):
        source = (ROOT / "app" / "phase49_3i_product_list.py").read_text(encoding="utf-8")
        installed = source.index("app_class._phase49_3i_product_list_installed = True")
        imported = source.index("from .phase49_3i_explorer_hotfix import install as install_explorer_hotfix")
        invoked = source.index("install_explorer_hotfix(app_class)")
        self.assertLess(installed, imported)
        self.assertLess(imported, invoked)


if __name__ == "__main__":
    unittest.main()
