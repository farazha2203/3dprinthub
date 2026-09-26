from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.db import Database


class Phase50A2ZO5CSocialFilterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Database(Path(self.temp.name) / "catalog.sqlite3")
        self.addCleanup(self.db.close)
        self.db.upsert_source(
            {
                "code": "makerworld",
                "name": "MakerWorld",
                "enabled": 1,
                "methods": ["http"],
                "listing_urls": [],
                "model_url_pattern": "",
                "requires_login": False,
                "reference_only": False,
            }
        )
        self.db.upsert_product(
            {
                "source_code": "makerworld",
                "external_id": "o5c-7001",
                "source_url": "https://makerworld.com/en/models/7001-o5c",
                "source_title": "O5C Product",
                "source_description": "Social revision filter test",
                "images_json": "[]",
                "selected_images_json": "[]",
            }
        )
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("makerworld", "o5c-7001"),
        ).fetchone()
        self.product_id = int(row["id"])
        self.current_fp = json.dumps(
            {
                "product_url": "/store/product/o5c-7001/",
                "revision": 11,
            },
            separators=(",", ":"),
        )
        self.db.conn.execute(
            "UPDATE products SET server_ack_json=? WHERE id=?",
            (self.current_fp, self.product_id),
        )
        self.db.conn.commit()

    def _ids(self, filter_name: str) -> set[int]:
        return {
            int(row["id"])
            for row in self.db.products(filter_name=filter_name)
        }

    def test_stale_published_receipts_do_not_satisfy_current_revision_filters(self):
        old_fp = json.dumps(
            {
                "product_url": "/store/product/o5c-7001/",
                "revision": 10,
            },
            separators=(",", ":"),
        )
        self.db.record_sync_receipt(
            self.product_id,
            "instagram:buffer:old-feed",
            "instagram_published",
            server_id="old-feed",
            payload={
                "provider_post_id": "old-feed",
                "site_ack_fingerprint": old_fp,
            },
        )
        self.db.record_sync_receipt(
            self.product_id,
            "instagram:buffer:old-story",
            "instagram_story_published",
            server_id="old-story",
            payload={
                "provider_post_id": "old-story",
                "site_ack_fingerprint": old_fp,
            },
        )

        self.assertNotIn(self.product_id, self._ids("instagram_posted"))
        self.assertNotIn(self.product_id, self._ids("instagram_story"))

    def test_feed_and_story_filters_require_their_own_current_receipt(self):
        self.db.record_sync_receipt(
            self.product_id,
            "instagram:buffer:feed-current",
            "instagram_published",
            server_id="feed-current",
            payload={
                "provider_post_id": "feed-current",
                "site_ack_fingerprint": self.current_fp,
            },
        )

        self.assertIn(self.product_id, self._ids("instagram_posted"))
        self.assertNotIn(self.product_id, self._ids("instagram_story"))

        self.db.record_sync_receipt(
            self.product_id,
            "instagram:buffer:story-current",
            "instagram_story_published",
            server_id="story-current",
            payload={
                "provider_post_id": "story-current",
                "site_ack_fingerprint": self.current_fp,
            },
        )

        self.assertIn(self.product_id, self._ids("instagram_posted"))
        self.assertIn(self.product_id, self._ids("instagram_story"))

    def test_empty_site_ack_never_counts_as_current_social_publication(self):
        self.db.conn.execute(
            "UPDATE products SET server_ack_json='{}' WHERE id=?",
            (self.product_id,),
        )
        self.db.conn.commit()
        self.db.record_sync_receipt(
            self.product_id,
            "instagram:buffer:empty-ack-feed",
            "instagram_published",
            server_id="empty-ack-feed",
            payload={
                "provider_post_id": "empty-ack-feed",
                "site_ack_fingerprint": "{}",
            },
        )

        self.assertNotIn(self.product_id, self._ids("instagram_posted"))


if __name__ == "__main__":
    unittest.main()
