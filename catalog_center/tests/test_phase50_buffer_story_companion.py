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
            "local_category_slug": "toys-games",
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
    def setUp(self):
        self.device_patcher = patch(
            "app.buffer_publish.require_clickable_story_device",
            return_value={"has_active_member_device": True},
        )
        self.device_patcher.start()

    def tearDown(self):
        self.device_patcher.stop()

    @patch("app.buffer_publish.get_secret", return_value="secret")
    @patch("app.buffer_publish._request_graphql")
    def test_missing_mobile_device_blocks_before_new_feed(self, request, _secret):
        db = _DB()
        with patch(
            "app.buffer_publish.require_clickable_story_device",
            side_effect=RuntimeError("No mobile reminder device"),
        ):
            with self.assertRaisesRegex(RuntimeError, "هیچ Feed جدیدی ساخته نشد"):
                publish_product(
                    db,
                    11,
                    BufferConfig(channel_id="chan-1"),
                    site_url="https://3dprinthub.ir",
                )
        request.assert_not_called()
        self.assertEqual(db.receipts, [])

    @patch("app.buffer_publish.get_secret", return_value="secret")
    @patch("app.buffer_publish._request_graphql")
    def test_missing_mobile_device_keeps_existing_feed_and_blocks_story_only(
        self, request, _secret
    ):
        db = _DB()
        fingerprint = db.row["server_ack_json"]
        db.receipts.append(
            {
                "status": "instagram_published",
                "payload_json": json.dumps(
                    {
                        "site_ack_fingerprint": fingerprint,
                        "provider_post_id": "feed-live",
                        "external_link": "https://instagram.com/p/live",
                    }
                ),
                "server_id": "feed-live",
            }
        )
        with patch(
            "app.buffer_publish.require_clickable_story_device",
            side_effect=RuntimeError("No mobile reminder device"),
        ):
            with self.assertRaisesRegex(RuntimeError, "قبلاً ثبت شده"):
                publish_product(
                    db,
                    11,
                    BufferConfig(channel_id="chan-1"),
                    site_url="https://3dprinthub.ir",
                )
        request.assert_not_called()
        self.assertEqual(
            len([r for r in db.receipts if r["status"] == "instagram_published"]),
            1,
        )

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
        self.assertEqual(story_input["schedulingType"], "notification")
        self.assertIn("/store/product/story-demo/", story_input["metadata"]["instagram"]["link"])
        sticker = story_input["metadata"]["instagram"]["stickerFields"]
        self.assertEqual(sticker["text"], "لینک محصول")
        self.assertIn("utm_source=instagram", sticker["other"])
        self.assertEqual(
            story_input["assets"][0]["image"]["url"],
            "https://3dprinthub.ir/media/story-card.webp",
        )
        statuses = [row["status"] for row in db.receipts]
        self.assertIn("instagram_published", statuses)
        self.assertIn("instagram_story_notification_ready", statuses)
        self.assertNotIn("instagram_story_published", statuses)
        story_receipt = json.loads(db.receipts[-1]["payload_json"])
        self.assertEqual(story_receipt["highlight_target"], "اسباب بازی")
        self.assertEqual(story_receipt["highlight_status"], "operator_required")
        self.assertEqual(story_receipt["story_publish_mode"], "notification")
        self.assertTrue(story_receipt["link_sticker_required"])
        self.assertEqual(story_receipt["link_sticker_label"], "لینک محصول")
        self.assertFalse(story_receipt["instagram_live_confirmed"])

    @patch("app.buffer_publish.get_secret", return_value="secret")
    @patch("app.buffer_publish._request_graphql")
    def test_story_can_remain_fully_automatic_without_clickable_sticker(
        self, request, _secret
    ):
        request.side_effect = [
            {
                "createPost": {
                    "post": {
                        "id": "feed-auto",
                        "status": "sent",
                        "externalLink": "feed-link",
                    }
                }
            },
            {
                "createPost": {
                    "post": {
                        "id": "story-auto",
                        "status": "sent",
                        "externalLink": "story-link",
                    }
                }
            },
        ]
        db = _DB()
        result = publish_product(
            db,
            11,
            BufferConfig(channel_id="chan-1"),
            site_url="https://3dprinthub.ir",
            story_link_notification=False,
        )
        story_input = request.call_args_list[1].kwargs["variables"]["input"]
        self.assertEqual(story_input["schedulingType"], "automatic")
        self.assertNotIn("stickerFields", story_input["metadata"]["instagram"])
        self.assertEqual(
            result["companion_story"]["story_publish_mode"],
            "automatic",
        )
        self.assertFalse(result["companion_story"]["link_sticker_required"])
        self.assertTrue(result["companion_story"]["instagram_live_confirmed"])

    @patch("app.buffer_publish.get_secret", return_value="secret")
    @patch("app.buffer_publish._request_graphql")
    def test_provider_error_story_is_failure_and_retry_does_not_duplicate_feed(
        self, request, _secret
    ):
        db = _DB()
        request.side_effect = [
            {"createPost": {"post": {"id": "feed-err", "status": "sent", "externalLink": "feed-link"}}},
            {"createPost": {"post": {"id": "story-err", "status": "error", "externalLink": ""}}},
            {
                "post": {
                    "id": "story-err",
                    "status": "error",
                    "externalLink": None,
                    "notificationStatus": None,
                    "error": {
                        "message": "No mobile reminder device is linked.",
                        "rawError": "No devices found.",
                        "supportUrl": "",
                    },
                }
            },
        ]
        with self.assertRaisesRegex(RuntimeError, "No mobile reminder device"):
            publish_product(
                db,
                11,
                BufferConfig(channel_id="chan-1"),
                site_url="https://3dprinthub.ir",
            )
        statuses = [row["status"] for row in db.receipts]
        self.assertIn("instagram_published", statuses)
        self.assertIn("instagram_story_failed", statuses)
        self.assertNotIn("instagram_story_notification_ready", statuses)

        # A historical false-ready/error receipt must not block a corrected retry.
        fingerprint = db.row["server_ack_json"]
        db.receipts.append(
            {
                "status": "instagram_story_notification_ready",
                "payload_json": json.dumps(
                    {
                        "site_ack_fingerprint": fingerprint,
                        "buffer_status": "error",
                    }
                ),
                "server_id": "story-old-error",
            }
        )
        request.reset_mock()
        request.side_effect = None
        request.return_value = {
            "createPost": {
                "post": {
                    "id": "story-after-device",
                    "status": "sent",
                    "externalLink": "",
                }
            }
        }
        result = publish_product(
            db,
            11,
            BufferConfig(channel_id="chan-1"),
            site_url="https://3dprinthub.ir",
        )
        self.assertEqual(request.call_count, 1)
        self.assertEqual(result["provider_post_id"], "feed-err")
        self.assertEqual(
            result["companion_story"]["provider_post_id"],
            "story-after-device",
        )

    @patch("app.buffer_publish.get_secret", return_value="secret")
    @patch("app.buffer_publish._request_graphql")
    def test_retry_after_story_failure_does_not_duplicate_feed(self, request, _secret):
        db = _DB()
        request.side_effect = [
            {"createPost": {"post": {"id": "feed-1", "status": "sent", "externalLink": "feed-link"}}},
            RuntimeError("temporary story failure"),
        ]
        with self.assertRaisesRegex(RuntimeError, "Retry فقط Story"):
            publish_product(
                db, 11, BufferConfig(channel_id="chan-1"),
                site_url="https://3dprinthub.ir",
            )
        feed_receipts = [
            item for item in db.receipts if item["status"] == "instagram_published"
        ]
        self.assertEqual(len(feed_receipts), 1)

        request.reset_mock()
        request.side_effect = None
        request.return_value = {
            "createPost": {"post": {
                "id": "story-retry", "status": "sent", "externalLink": "story-link"
            }}
        }
        result = publish_product(
            db, 11, BufferConfig(channel_id="chan-1"),
            site_url="https://3dprinthub.ir",
        )
        self.assertEqual(request.call_count, 1)
        self.assertEqual(result["provider_post_id"], "feed-1")
        self.assertEqual(result["companion_story"]["provider_post_id"], "story-retry")


if __name__ == "__main__":
    unittest.main()
