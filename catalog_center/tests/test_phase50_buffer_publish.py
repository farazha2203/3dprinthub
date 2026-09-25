from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlparse
from unittest.mock import patch

from PIL import Image

from app.buffer_publish import (
    BufferConfig,
    publish_product,
    reconcile_product_receipts,
    require_clickable_story_device,
    test_connection,
)
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
            "source_url": "https://makerworld.com/en/models/7001-demo",
            "description_fa": "توضیح محصول",
            "image_alt_texts_json": json.dumps(["تصویر محصول"]),
        }
        self._temp = tempfile.TemporaryDirectory()
        self._media_root = Path(self._temp.name) / "product"
        self.configure_media([
            "https://3dprinthub.ir/media/demo.webp",
        ])

    def configure_media(self, public_urls):
        image_dir = self._media_root / "images"
        seo_dir = self._media_root / "seo_images"
        image_dir.mkdir(parents=True, exist_ok=True)
        seo_dir.mkdir(parents=True, exist_ok=True)
        selected = []
        metadata = []
        for index, public_url in enumerate(public_urls, 1):
            name = Path(urlparse(public_url).path).name or f"image-{index}.webp"
            source_url = f"local://{name}"
            source = image_dir / name
            final = seo_dir / name
            Image.new(
                "RGB",
                (320 + index, 240 + index),
                (40 + index, 80, 120),
            ).save(source, "WEBP")
            Image.open(source).save(final, "WEBP")
            digest = hashlib.sha256(final.read_bytes()).hexdigest()
            selected.append(source_url)
            metadata.append({
                "source_url": source_url,
                "seo_filename": name,
                "final_local_file": str(final),
                "final_sha256": digest,
            })
        self.row["local_dir"] = str(self._media_root)
        self.row["images_json"] = json.dumps(selected)
        self.row["selected_images_json"] = json.dumps(selected)
        self.row["primary_image_url"] = selected[0] if selected else ""
        self.row["image_metadata_json"] = json.dumps(metadata)

    def product(self, product_id):
        return self.row if int(product_id) == 7 else None

    def sync_receipts(self, product_id, limit=80):
        return self.receipts

    def record_sync_receipt(self, product_id, key, status, *, server_id, payload):
        self.receipts.append({
            "id": len(self.receipts) + 1,
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
            "hasActiveMemberDevice": True,
            "externalLink": "https://instagram.com/demo",
        }}
        result = test_connection(BufferConfig(channel_id="chan-1"))
        self.assertEqual(result["service"], "instagram")
        self.assertEqual(result["id"], "chan-1")
        self.assertTrue(result["has_active_member_device"])

    @patch("app.buffer_publish.get_secret", return_value="secret")
    @patch("app.buffer_publish._request_graphql")
    def test_clickable_story_requires_active_buffer_mobile_device(
        self, request, _secret
    ):
        request.return_value = {"channel": {
            "id": "chan-1", "displayName": "3DPrintHub", "service": "instagram",
            "isDisconnected": False, "isLocked": False,
            "hasActiveMemberDevice": False,
            "externalLink": "https://instagram.com/demo",
        }}
        with self.assertRaisesRegex(RuntimeError, "mobile device"):
            require_clickable_story_device(BufferConfig(channel_id="chan-1"))

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
        self.assertTrue(create_input["aiAssisted"])
        self.assertTrue(create_input["metadata"]["instagram"]["isAiGenerated"])
        self.assertEqual(
            create_input["metadata"]["instagram"]["link"],
            result["tracking_url"],
        )
        self.assertIn("utm_source=instagram", result["tracking_url"])
        self.assertTrue(
            create_input["assets"][0]["image"]["url"].startswith("https://3dprinthub.ir/")
        )
        self.assertEqual(result["provider_post_id"], "post-1")
        self.assertTrue(result["ai_disclosure"])
        self.assertEqual(
            result["product_details"]["source_url"],
            "https://makerworld.com/en/models/7001-demo",
        )
        self.assertEqual(
            result["product_details"]["order_url"],
            result["tracking_url"],
        )
        self.assertIn("instagram_published", [item["status"] for item in db.receipts])

    @patch("app.buffer_publish.get_secret", return_value="secret")
    @patch("app.buffer_publish._request_graphql")
    def test_buffer_feed_can_use_static_compatibility_media_without_losing_source_audit(self, request, _secret):
        request.return_value = {"createPost": {"post": {
            "id": "post-compat", "status": "sent",
            "externalLink": "https://instagram.com/p/compat",
        }}}
        db = _DB()
        source_url = "https://3dprinthub.ir/media/demo.webp"
        compat_url = "https://3dprinthub.ir/media/instagram/feed/products/7/rev/01.png"
        result = publish_product(
            db, 7, BufferConfig(channel_id="chan-1"),
            site_url="https://3dprinthub.ir",
            feed_asset_urls=[compat_url],
            media_host_meta={
                "host": "github_raw",
                "branch": "social-assets-buffer",
                "commit_sha": "abc123",
            },
        )
        create_input = self._feed_input(request)
        self.assertEqual(create_input["assets"][0]["image"]["url"], compat_url)
        self.assertEqual(result["media_urls"], [compat_url])
        self.assertEqual(result["source_media_urls"], [source_url])
        self.assertEqual(result["media_host"], "github_raw")
        self.assertEqual(result["media_host_branch"], "social-assets-buffer")
        self.assertEqual(result["media_host_commit_sha"], "abc123")

    @patch("app.buffer_publish.get_secret", return_value="secret")
    @patch("app.buffer_publish._request_graphql")
    def test_feed_override_can_publish_all_current_media_not_only_selected_payload(
        self, request, _secret
    ):
        request.return_value = {"createPost": {"post": {
            "id": "post-all-current", "status": "sent",
            "externalLink": "https://instagram.com/p/all-current",
        }}}
        db = _DB()
        provider_urls = [
            f"https://raw.githubusercontent.com/demo/feed-{index:02d}.png"
            for index in range(1, 4)
        ]
        source_urls = [
            f"https://makerworld.com/media/source-{index}.jpg"
            for index in range(1, 4)
        ]
        alt_texts = [f"Product image {index}" for index in range(1, 4)]
        result = publish_product(
            db, 7, BufferConfig(channel_id="chan-1"),
            site_url="https://3dprinthub.ir",
            companion_story=False,
            feed_asset_urls=provider_urls,
            feed_alt_texts=alt_texts,
            feed_source_urls=source_urls,
        )
        create_input = self._feed_input(request)
        self.assertEqual(len(create_input["assets"]), 3)
        self.assertEqual(result["media_urls"], provider_urls)
        self.assertEqual(result["source_media_urls"], source_urls)
        self.assertEqual(result["alt_texts"], alt_texts)

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
        ack["public_main_image_url"] = "https://3dprinthub.ir/media/demo-4.webp"
        db.row["server_ack_json"] = json.dumps(ack)
        db.configure_media([
            "https://3dprinthub.ir/media/demo-4.webp",
            "https://3dprinthub.ir/media/demo-1.webp",
            "https://3dprinthub.ir/media/demo-2.webp",
            "https://3dprinthub.ir/media/demo-3.webp",
            "https://3dprinthub.ir/media/demo-5.webp",
        ])
        result = publish_product(
            db, 7, BufferConfig(channel_id="chan-1"),
            site_url="https://3dprinthub.ir",
        )
        create_input = self._feed_input(request)
        self.assertEqual(len(create_input["assets"]), 5)
        self.assertEqual(len(result["media_urls"]), 5)
        self.assertEqual(
            create_input["assets"][0]["image"]["url"],
            "https://3dprinthub.ir/media/demo-4.webp",
        )
        self.assertEqual(
            result["media_urls"][0],
            "https://3dprinthub.ir/media/demo-4.webp",
        )
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
        db.configure_media([
            f"https://3dprinthub.ir/media/seo-{index}.webp"
            for index in range(1, 7)
        ])
        payload = canonical_site_payload(db.row, site_url="https://3dprinthub.ir")
        self.assertEqual(len(payload["media_urls"]), 6)
        self.assertTrue(payload["tracking_url"].startswith("https://3dprinthub.ir/"))
        self.assertIn("utm_source=instagram", payload["tracking_url"])
        self.assertEqual(
            payload["product_details"]["source_url"],
            "https://makerworld.com/en/models/7001-demo",
        )
        self.assertEqual(payload["product_details"]["order_url"], payload["tracking_url"])
        self.assertNotIn(payload["tracking_url"], payload["caption"])
        self.assertIn("لینک بیو", payload["caption"])


    @patch("app.buffer_publish.get_secret", return_value="secret")
    @patch("app.buffer_publish._reconcile_recent_asset")
    def test_reconcile_submitted_feed_appends_published_receipt_without_repost(
        self, reconcile, _secret
    ):
        db = _DB()
        fingerprint = db.row["server_ack_json"]
        db.record_sync_receipt(
            7,
            "instagram:buffer:post-submitted",
            "instagram_submitted",
            server_id="post-submitted",
            payload={
                "provider_post_id": "post-submitted",
                "site_ack_fingerprint": fingerprint,
                "media_urls": ["https://raw.githubusercontent.com/demo/feed.png"],
                "buffer_status": "sending",
                "external_link": "",
            },
        )
        reconcile.return_value = {
            "id": "post-submitted",
            "status": "sent",
            "externalLink": "https://instagram.com/p/final",
        }

        result = reconcile_product_receipts(
            db,
            7,
            BufferConfig(channel_id="chan-1"),
        )

        self.assertEqual(len(result["reconciled"]), 1)
        self.assertEqual(result["reconciled"][0]["status"], "instagram_published")
        final = json.loads(db.receipts[-1]["payload_json"])
        self.assertTrue(final["reconciled_without_repost"])
        self.assertEqual(final["external_link"], "https://instagram.com/p/final")
        self.assertEqual(db.receipts[-1]["status"], "instagram_published")

    @patch("app.buffer_publish.get_secret", return_value="")
    def test_missing_key_fails_closed(self, _secret):
        with self.assertRaisesRegex(RuntimeError, "Buffer API Key"):
            test_connection(BufferConfig(channel_id="chan-1"))


if __name__ == "__main__":
    unittest.main()
