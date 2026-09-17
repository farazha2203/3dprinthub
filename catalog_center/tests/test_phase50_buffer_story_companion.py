from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from app.buffer_publish import BufferConfig, publish_product


class _DB:
    def __init__(self):
        self.receipts = []
        self.row = {
            "id": 11,
            "server_ack_json": json.dumps({
                "product_url": "/store/product/story-demo/",
                "public_http_ok": True,
                "public_images": [{
                    "url": "https://3dprinthub.ir/media/story-demo.webp",
                    "ok": True,
                }],
                "instagram_story_url": "https://3dprinthub.ir/media/story-card.webp",
            }),
            "title_fa": "Story demo",
            "image_alt_texts_json": json.dumps(["3D printed product"]),
            "instagram_highlight": "آباژور",
        }

    def product(self, product_id):
        return self.row if int(product_id) == 11 else None

    def setting(self, key, default=""):
        if key == "instagram_companion_story_enabled":
            return "1"
        return default

    def sync_receipts(self, product_id, limit=120):
        return self.receipts

    def record_sync_receipt(self, product_id, key, status, *, server_id, payload):
        self.receipts.append({
            "status": status,
            "payload_json": json.dumps(payload, ensure_ascii=False),
            "server_id": server_id,
        })


class BufferStoryCompanionTests(unittest.TestCase):
    @patch("app.buffer_publish.get_secret", return_value="secret")
    @patch("app.buffer_publish._request_graphql")
    def test_feed_publish_creates_companion_story(self, request, _secret):
        request.side_effect = [
            {"createPost": {"post": {"id": "feed-1", "status": "sent", "externalLink": "feed-link"}}},
            {"createPost": {"post": {"id": "story-1", "status": "sent", "externalLink": "story-link"}}},
        ]
        db = _DB()
        result = publish_product(
            db, 11, BufferConfig(channel_id="chan-1"),
            site_url="https://3dprinthub.ir",
        )
        self.assertEqual(request.call_count, 2)
        self.assertEqual(result["provider_post_id"], "feed-1")
        self.assertEqual(result["companion_story"]["provider_post_id"], "story-1")
        story_input = request.call_args_list[1].kwargs["variables"]["input"]
        self.assertEqual(story_input["metadata"]["instagram"]["type"], "story")
        self.assertFalse(story_input["metadata"]["instagram"]["shouldShareToFeed"])
        self.assertIn("/store/product/story-demo/", story_input["metadata"]["instagram"]["link"])
        self.assertEqual(
            story_input["assets"][0]["image"]["url"],
            "https://3dprinthub.ir/media/story-card.webp",
        )
        statuses = [row["status"] for row in db.receipts]
        self.assertIn("instagram_published", statuses)
        self.assertIn("instagram_story_published", statuses)
        story_receipt = json.loads(db.receipts[-1]["payload_json"])
        self.assertEqual(story_receipt["highlight_target"], "آباژور")
        self.assertEqual(story_receipt["highlight_status"], "operator_required")


if __name__ == "__main__":
    unittest.main()
