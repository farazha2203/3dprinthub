from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from app.buffer_publish import BufferConfig, publish_product, test_connection


class _DB:
    def __init__(self):
        self.receipts = []
        self.row = {
            "id": 7,
            "server_ack_json": json.dumps({
                "product_url": "/store/product/demo/",
                "public_http_ok": True,
                "public_images": [
                    {"url": "https://3dprinthub.ir/media/demo.webp", "ok": True}
                ],
            }),
            "title_fa": "محصول آزمایشی",
            "description_fa": "توضیح محصول",
            "image_alt_texts_json": json.dumps(["تصویر محصول"]),
        }

    def product(self, product_id):
        return self.row if int(product_id) == 7 else None

    def sync_receipts(self, product_id, limit=80):
        return self.receipts

    def record_sync_receipt(self, product_id, key, status, *, server_id, payload):
        self.receipts.append({
            "status": status,
            "payload_json": json.dumps(payload),
            "server_id": server_id,
        })


class BufferPublishTests(unittest.TestCase):
    @patch("app.buffer_publish.get_secret", return_value="secret")
    @patch("app.buffer_publish._request_graphql")
    def test_connection_accepts_healthy_instagram_channel(self, request, _secret):
        request.return_value = {"channel": {
            "id": "chan-1", "displayName": "3DPrintHub", "service": "instagram",
            "isDisconnected": False, "isLocked": False,
            "externalLink": "https://instagram.com/demo",
        }}
        result = test_connection(BufferConfig(channel_id="chan-1"))
        self.assertEqual(result["service"], "instagram")
        self.assertEqual(result["id"], "chan-1")

    @patch("app.buffer_publish.get_secret", return_value="secret")
    @patch("app.buffer_publish._request_graphql")
    def test_publish_uses_share_now_and_public_site_media(self, request, _secret):
        request.return_value = {"createPost": {"post": {
            "id": "post-1", "status": "sent",
            "externalLink": "https://instagram.com/p/demo",
        }}}
        db = _DB()
        result = publish_product(
            db, 7, BufferConfig(channel_id="chan-1"),
            site_url="https://3dprinthub.ir",
        )
        create_input = request.call_args.kwargs["variables"]["input"]
        self.assertEqual(create_input["mode"], "shareNow")
        self.assertEqual(create_input["schedulingType"], "automatic")
        self.assertEqual(create_input["channelId"], "chan-1")
        self.assertTrue(
            create_input["assets"][0]["image"]["url"].startswith("https://3dprinthub.ir/")
        )
        self.assertEqual(result["provider_post_id"], "post-1")
        self.assertEqual(db.receipts[-1]["status"], "instagram_published")

    @patch("app.buffer_publish.get_secret", return_value="")
    def test_missing_key_fails_closed(self, _secret):
        with self.assertRaisesRegex(RuntimeError, "Buffer API Key"):
            test_connection(BufferConfig(channel_id="chan-1"))


if __name__ == "__main__":
    unittest.main()
