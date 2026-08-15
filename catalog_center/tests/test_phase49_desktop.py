from __future__ import annotations

import unittest
from pathlib import Path

from app.v8_features import ack_item_confirms_publish
from app.phase49_ui import (
    first_site_images,
    gallery_page,
    keep_only_gallery_urls,
    remove_gallery_urls,
)


ROOT = Path(__file__).resolve().parents[1]


class Phase49GalleryTests(unittest.TestCase):
    def test_gallery_is_paged_for_thousands_of_images(self):
        page = gallery_page(2000, 49, 40)
        self.assertEqual(page.total_pages, 50)
        self.assertEqual((page.start, page.end), (1960, 2000))

    def test_first_five_keeps_primary_first(self):
        urls = [f"u{i}" for i in range(10)]
        self.assertEqual(first_site_images(urls, 5, "u7"), ["u7", "u0", "u1", "u2", "u3"])

    def test_bulk_remove_preserves_valid_primary(self):
        urls, selected, primary = remove_gallery_urls(
            ["a", "b", "c", "d"], ["a", "b", "c"], "a", {"a", "d"}
        )
        self.assertEqual(urls, ["b", "c"])
        self.assertEqual(primary, "b")
        self.assertEqual(selected, ["b", "c"])

    def test_keep_only_bulk(self):
        urls, selected, primary = keep_only_gallery_urls(
            ["a", "b", "c", "d"], ["a", "b"], "a", {"c", "d"}
        )
        self.assertEqual(urls, ["c", "d"])
        self.assertEqual(primary, "c")
        self.assertEqual(selected, ["c"])


class Phase49DesktopContractTests(unittest.TestCase):
    def test_product_studio_has_group_image_and_direct_publish_controls(self):
        source = (ROOT / "app" / "product_studio.py").read_text(encoding="utf-8")
        for marker in [
            "ارسال همین محصول",
            "حذف گروهی از محصول",
            "فقط انتخاب‌شده‌های گروهی بماند",
            "۵ عکس اول برای سایت",
            "فقط ۵ عکس اول بماند",
            "def keep_first_five_only",
            "def open_sync_log",
            "def publish_now",
        ]:
            self.assertIn(marker, source)


    def test_product_ack_preserves_legacy_and_phase49_strict_contracts(self):
        row = {"publish_as_product": 1, "publish_as_portfolio": 0}
        base = {"status": "created", "server_id": "9", "product_id": 12}

        # v8.4 compatibility: old ACKs did not expose store visibility.
        self.assertTrue(ack_item_confirms_publish(dict(base), row))

        # Phase49 real publish paths opt in to the stronger contract.
        self.assertFalse(ack_item_confirms_publish(dict(base), row, require_store_visibility=True))
        self.assertFalse(
            ack_item_confirms_publish(
                {**base, "visible_on_store": False}, row, require_store_visibility=True
            )
        )
        self.assertTrue(
            ack_item_confirms_publish(
                {**base, "visible_on_store": True}, row, require_store_visibility=True
            )
        )

    def test_main_direct_publish_builds_single_product_batch(self):
        source = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
        self.assertIn("def build_batch(self, product_ids=None, quiet=False)", source)
        self.assertIn("def publish_product_now(self, product_id=None, parent=None)", source)
        self.assertIn("desktop_ftp_uploaded", source)
        self.assertIn("visible_on_store", source)
        self.assertIn("require_store_visibility=True", source)
        self.assertIn("items[:24]", source)
        self.assertIn("studio.nb.select(studio.images_tab)", source)
        self.assertIn("get_batch_diagnostic", source)


if __name__ == "__main__":
    unittest.main()
