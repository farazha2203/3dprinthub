from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from app.buffer_publish import BufferConfig, publish_product, test_connection
from app.instagram_publish import canonical_site_payload


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
    @staticmethod
    def _feed_input(mock_request):
        for call in mock_request.call_args_list:
            variables = call.kwargs.get("variables") or {}
            value = variables.get("input") or {}
            if ((value.get("metadata") or {}).get("instagram") or {}).get("type") == "post":
                return value
        raise AssertionError("Buffer feed createPost input was not observed")

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
        create_input = self._feed_input(request)
        self.assertEqual(create_input["mode"], "shareNow")
        self.assertEqual(create_input["schedulingType"], "automatic")
        self.assertEqual(create_input["channelId"], "chan-1")
        self.assertEqual(
            create_input["metadata"]["instagram"]["link"],
            result["tracking_url"],
        )
        self.assertIn("utm_source=instagram", result["tracking_url"])
        self.assertTrue(
            create_input["assets"][0]["image"]["url"].startswith("https://3dprinthub.ir/")
        )
        self.assertEqual(result["provider_post_id"], "post-1")
        self.assertIn("instagram_published", [item["status"] for item in db.receipts])

    @patch("app.buffer_publish.get_secret", return_value="secret")
    @patch("app.buffer_publish._request_graphql")
    def test_five_public_images_remain_five_buffer_assets(self, request, _secret):
        request.return_value = {"createPost": {"post": {
            "id": "post-5", "status": "sent",
            "externalLink": "https://instagram.com/p/five",
        }}}
        db = _DB()
        ack = json.loads(db.row["server_ack_json"])
        ack["public_images"] = [
            {"url": f"https://3dprinthub.ir/media/demo-{index}.webp", "ok": True}
            for index in range(1, 6)
        ]
        db.row["server_ack_json"] = json.dumps(ack)
        result = publish_product(
            db, 7, BufferConfig(channel_id="chan-1"),
            site_url="https://3dprinthub.ir",
        )
        create_input = self._feed_input(request)
        self.assertEqual(len(create_input["assets"]), 5)
        self.assertEqual(len(result["media_urls"]), 5)
        self.assertIn("utm_source=instagram", result["tracking_url"])
        self.assertIn("utm_campaign=product_catalog", result["tracking_url"])

    def test_canonical_payload_keeps_up_to_ten_images_and_tracking_url(self):
        db = _DB()
        ack = json.loads(db.row["server_ack_json"])
        ack["public_images"] = [
            {"url": f"https://3dprinthub.ir/media/seo-{index}.webp", "ok": True}
            for index in range(1, 7)
        ]
        db.row["server_ack_json"] = json.dumps(ack)
        payload = canonical_site_payload(db.row, site_url="https://3dprinthub.ir")
        self.assertEqual(len(payload["media_urls"]), 6)
        self.assertTrue(payload["tracking_url"].startswith("https://3dprinthub.ir/"))
        self.assertIn(payload["tracking_url"], payload["caption"])

    @patch("app.buffer_publish.get_secret", return_value="")
    def test_missing_key_fails_closed(self, _secret):
        with self.assertRaisesRegex(RuntimeError, "Buffer API Key"):
            test_connection(BufferConfig(channel_id="chan-1"))


if __name__ == "__main__":
    unittest.main()
