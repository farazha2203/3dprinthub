from __future__ import annotations

import unittest
from pathlib import Path

from app.phase49_3i_explorer_hotfix import (
    DEFAULT_VIEW_MODE,
    FILTER_OPTIONS,
    SORT_OPTIONS,
    VIEW_MODES,
    install,
    matches_source_product_url,
    normalize_view_mode,
    product_card_metadata,
)


ROOT = Path(__file__).resolve().parents[1]
MAKERWORLD_PATTERN = r"https?://(?:www\.)?makerworld\.com/(?:[a-z]{2}/)?models/(?P<external_id>\d+)[^\s\"'<>]*"
PRODUCT_URL = "https://makerworld.com/en/models/2834255-cake-stand-small-table-great-for-cakes-cupcakes?from=search#profileId-3158565"
GROUP_URL = "https://makerworld.com/en/3d-models/household"
SEARCH_URL = "https://makerworld.com/en/search/models?keyword=cake+stand"


class _FakeStatus:
    def __init__(self):
        self.value = ""

    def set(self, value):
        self.value = str(value)


class _FeedbackTree:
    """Simulate Tk <<TreeviewSelect>> callback immediately from selection_set."""

    def __init__(self):
        self._selection = ()
        self.callback = None
        self.selection_set_calls = 0
        self.focus_value = ""

    def exists(self, iid):
        return bool(iid)

    def selection(self):
        return self._selection

    def selection_set(self, iid):
        self.selection_set_calls += 1
        if self.selection_set_calls > 3:
            raise RuntimeError("selection feedback loop")
        self._selection = (str(iid),)
        if self.callback:
            self.callback()

    def focus(self, iid):
        self.focus_value = str(iid)


class _InstallStub:
    def _modernize_products_page(self):
        return None

    def start_direct_link_import(self):
        return None

    def refresh_products(self):
        return None


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

    def test_selection_sync_is_one_way_and_cannot_feedback_loop(self):
        class Stub(_InstallStub):
            pass

        install(Stub)
        app = Stub()
        app.current_product = None
        app.status = _FakeStatus()
        app.product_tree = _FeedbackTree()
        app._phase49_3i_syncing_tree_selection = False
        app.product_tree.callback = lambda: app.load_product()

        app._phase49_3i_select_product(42)

        self.assertEqual(app.current_product, 42)
        self.assertEqual(app.product_tree.selection(), ("42",))
        self.assertEqual(app.product_tree.selection_set_calls, 1)
        self.assertFalse(app._phase49_3i_syncing_tree_selection)

        app.load_product()
        self.assertEqual(app.current_product, 42)
        self.assertEqual(app.product_tree.selection_set_calls, 1)

    def test_filter_and_sort_controls_restore_operator_friendly_options(self):
        self.assertIn(("ready", "آماده انتشار"), FILTER_OPTIONS)
        self.assertIn(("upload_queue", "صف انتشار"), FILTER_OPTIONS)
        self.assertIn(("published", "منتشرشده"), FILTER_OPTIONS)
        self.assertIn(("newest", "جدیدترین"), SORT_OPTIONS)
        self.assertIn(("oldest", "قدیمی‌ترین"), SORT_OPTIONS)
        self.assertIn(("updated", "آخرین بروزرسانی"), SORT_OPTIONS)

    def test_product_cards_include_compact_operational_metadata(self):
        row = {
            "id": 77,
            "source_code": "makerworld",
            "images_json": '["a.jpg", "b.jpg"]',
            "is_blocked": 0,
            "server_status": "",
            "product_sync_error": "",
            "needs_update": 0,
            "server_id": "",
            "workflow_status": "review",
            "upload_ready": 1,
            "title_fa": "محصول تست",
            "description_fa": "شرح",
            "content_status": "ready",
            "approved_for_sale": 1,
            "publish_as_product": 1,
            "created_at": "2026-08-22T12:30:00Z",
        }
        line_one, line_two = product_card_metadata(row)
        self.assertIn("#77", line_one)
        self.assertIn("در صف ارسال", line_one)
        self.assertIn("makerworld", line_one)
        self.assertIn("2 عکس", line_one)
        self.assertIn("2026-08-22", line_two)
        self.assertIn("در صف انتشار", line_two)

    def test_open_product_has_repeat_click_guard_and_tk_yield(self):
        source = (ROOT / "app" / "phase49_3i_explorer_hotfix.py").read_text(encoding="utf-8")
        self.assertIn('_phase49_3i_opening_product', source)
        self.assertIn('self.update_idletasks()', source)
        self.assertIn('self.after(20, open_now)', source)
        self.assertIn('app_class.load_product = load_product', source)
        self.assertIn('app_class._phase49_3i_select_product = _phase49_3i_select_product', source)


if __name__ == "__main__":
    unittest.main()
