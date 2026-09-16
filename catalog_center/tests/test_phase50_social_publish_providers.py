from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from app.buffer_publish import BufferConfig, publish_product as publish_buffer_product
from app.instagram_publish import canonical_site_payload, tracking_product_url


class FakeDB:
    def __init__(self, row):
        self.row = dict(row)
        self.receipts = []

    def product(self, product_id):
        return self.row if int(product_id) == int(self.row["id"]) else None

    def sync_receipts(self, product_id, limit=60):
        return list(reversed(self.receipts))[:limit]

    def record_sync_receipt(self, product_id, batch_uuid, status, server_id="", payload=None):
        self.receipts.append(
            {
                "product_id": int(product_id),
                "batch_uuid": batch_uuid,
                "status": status,
                "server_id": server_id,
                "payload_json": json.dumps(payload or {}, ensure_ascii=False),
            }
        )


def row():
    ack = {
        "visible_on_store": True,
        "public_http_ok": True,
        "product_url": "/store/product/desk-lamp/",
        "public_main_image_url": "https://3dprinthub.ir/media/store/products/lamp-01.webp",
        "images": [
            {"url": "https://3dprinthub.ir/media/store/products/lamp-01.webp", "ok": True},
            {"url": "https://3dprinthub.ir/media/store/products/lamp-02.webp", "ok": True},
        ],
    }
    return {
        "id": 628,
        "title_fa": "چراغ رومیزی چاپ سه بعدی",
        "seo_title_fa": "خرید چراغ رومیزی چاپ سه بعدی",
        "social_caption_fa": "چراغ دکوراتیو با انتخاب رنگ و متریال.",
        "hashtags_fa_json": json.dumps(["چاپ_سه_بعدی", "چراغ_رومیزی"], ensure_ascii=False),
        "tags_fa_json": "[]",
        "image_alt_texts_json": json.dumps(["نمای اصلی چراغ", "نمای دوم چراغ"], ensure_ascii=False),
        "server_ack_json": json.dumps(ack, ensure_ascii=False),
    }


class Phase50SocialProviderTests(unittest.TestCase):
    def test_tracking_url_is_deterministic_and_preserves_product_path(self):
        url = tracking_product_url(
            "https://3dprinthub.ir/store/product/desk-lamp/",
            product_id=628,
        )
        self.assertTrue(url.startswith("https://3dprinthub.ir/store/product/desk-lamp/?"))
        self.assertIn("utm_source=instagram", url)
        self.assertIn("utm_medium=social", url)
        self.assertIn("utm_campaign=product", url)
        self.assertIn("utm_content=product-628", url)

    def test_site_payload_caption_uses_utm_but_keeps_canonical_url(self):
        payload = canonical_site_payload(row(), site_url="https://3dprinthub.ir")
        self.assertEqual(payload["product_url"], "https://3dprinthub.ir/store/product/desk-lamp/")
        self.assertIn("utm_source=instagram", payload["tracking_url"])
        self.assertIn(payload["tracking_url"], payload["caption"])
        self.assertIn("#چراغ_رومیزی", payload["caption"])

    @patch("app.buffer_publish.get_secret", return_value="buffer-key")
    @patch("app.buffer_publish._graphql")
    def test_buffer_carousel_uses_site_media_alt_utm_and_records_provider_post_id(self, graphql, _secret):
        graphql.side_effect = [
            {
                "channel": {
                    "id": "buffer-ig-1",
                    "name": "3DPrintHub",
                    "displayName": "3DPrintHub",
                    "service": "instagram",
                    "externalLink": "https://instagram.com/3dprinthub",
                    "isLocked": False,
                    "isDisconnected": False,
                }
            },
            {
                "createPost": {
                    "post": {
                        "id": "buffer-post-99",
                        "text": "ok",
                        "externalLink": "https://instagram.com/p/example/",
                    }
                }
            },
        ]
        db = FakeDB(row())
        result = publish_buffer_product(
            db,
            628,
            BufferConfig(channel_id="buffer-ig-1"),
            site_url="https://3dprinthub.ir",
        )
        self.assertEqual(result["provider"], "buffer")
        self.assertEqual(result["provider_post_id"], "buffer-post-99")
        self.assertEqual(db.receipts[-1]["status"], "buffer_instagram_published")
        variables = graphql.call_args_list[-1].args[2]
        post_input = variables["input"]
        self.assertEqual(post_input["channelId"], "buffer-ig-1")
        self.assertEqual(post_input["mode"], "shareNow")
        self.assertEqual(post_input["metadata"]["instagram"]["type"], "carousel")
        self.assertEqual(post_input["assets"][0]["image"]["metadata"]["altText"], "نمای اصلی چراغ")
        self.assertIn("utm_source=instagram", post_input["metadata"]["instagram"]["link"])
        self.assertIn("utm_content=product-628", post_input["text"])

    @patch("app.buffer_publish.get_secret", return_value="buffer-key")
    def test_buffer_duplicate_same_public_revision_fails_closed(self, _secret):
        source = row()
        db = FakeDB(source)
        db.record_sync_receipt(
            628,
            "buffer-instagram:old",
            "buffer_instagram_published",
            server_id="old",
            payload={"site_ack_fingerprint": source["server_ack_json"]},
        )
        with self.assertRaisesRegex(RuntimeError, "already published"):
            publish_buffer_product(
                db,
                628,
                BufferConfig(channel_id="buffer-ig-1"),
                site_url="https://3dprinthub.ir",
            )


if __name__ == "__main__":
    unittest.main()
