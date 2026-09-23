from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from app.instagram_publish import InstagramConfig, canonical_site_payload, publish_product
from qt6.kernel import InstagramCore


class FakeDB:
    def __init__(self, row):
        self.row = dict(row)
        self.receipts = []
        self.settings = {
            "instagram_publish_provider": "buffer",
            "buffer_instagram_channel_id": "chan-1",
            "instagram_companion_story_enabled": "1",
            "instagram_story_link_mode": "bio_shop_grid",
            "instagram_story_clickable_link_enabled": "1",
            "buffer_media_host": "github_raw",
        }

    def setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings[key] = value

    def product(self, product_id):
        return self.row if int(product_id) == int(self.row["id"]) else None

    def sync_receipts(self, product_id, limit=40):
        return list(reversed(self.receipts))[:limit]

    def record_sync_receipt(self, product_id, batch_uuid, status, server_id="", payload=None):
        self.receipts.append({
            "product_id": product_id,
            "batch_uuid": batch_uuid,
            "status": status,
            "server_id": server_id,
            "payload_json": json.dumps(payload or {}, ensure_ascii=False),
        })


def product_row():
    ack = {
        "visible_on_store": True,
        "public_http_ok": True,
        "product_url": "/store/product/test-product/",
        "public_main_image_url": "https://3dprinthub.ir/media/store/products/test-main.webp",
        "images": [
            {"url": "https://3dprinthub.ir/media/store/products/test-main.webp", "ok": True},
            {"url": "https://3dprinthub.ir/media/store/products/test-02.webp", "ok": True},
        ],
    }
    return {
        "id": 42,
        "title_fa": "محصول سه‌بعدی تست",
        "seo_title_fa": "خرید محصول سه‌بعدی تست",
        "seo_description_fa": "انتخاب رنگ، متریال و کیفیت چاپ در صفحه محصول.",
        "social_caption_fa": "یک محصول چاپ سه‌بعدی با انتخاب‌های واقعی سفارش.",
        "hashtags_fa_json": json.dumps(["#چاپ_سه_بعدی", "خرید_سه_بعدی"], ensure_ascii=False),
        "tags_fa_json": json.dumps(["دکور"], ensure_ascii=False),
        "image_alt_texts_json": json.dumps(["نمای اصلی محصول", "نمای دوم محصول"], ensure_ascii=False),
        "server_ack_json": json.dumps(ack, ensure_ascii=False),
    }


class Phase50InstagramPublishTests(unittest.TestCase):
    def test_payload_uses_canonical_site_link_and_product_seo(self):
        payload = canonical_site_payload(product_row(), site_url="https://3dprinthub.ir")
        self.assertEqual(payload["product_url"], "https://3dprinthub.ir/store/product/test-product/")
        self.assertIn("خرید این محصول: لینک بیو", payload["caption"])
        self.assertNotIn("utm_source=instagram", payload["caption"])
        self.assertIn("utm_source=instagram", payload["tracking_url"])
        self.assertIn("#چاپ_سه_بعدی", payload["caption"])
        self.assertLessEqual(len(payload["hashtags"]), 8)
        self.assertEqual(payload["social_policy_version"], "instagram-product-v5-20260923")
        self.assertIn("سفارش این محصول از 3DPrintHub.ir", payload["caption"])
        self.assertIn("ارسال سفارش به سراسر ایران", payload["caption"])
        self.assertIn("#ارسال_سراسری", payload["hashtags"])
        self.assertEqual(len(payload["media_urls"]), 2)
        self.assertEqual(len(payload["alt_texts"]), len(payload["media_urls"]))
        self.assertEqual(payload["alt_texts"][0], "نمای اصلی محصول")

    def test_real_site_ack_count_uses_verified_product_owned_http_images(self):
        row = product_row()
        ack = json.loads(row["server_ack_json"])
        main = ack["public_main_image_url"]
        ack["images"] = 4
        ack["public_http_checks"] = {
            "ok": True,
            "main_image_url": main,
            "images": [
                {"ok": True, "url": main},
                {"ok": True, "url": "https://3dprinthub.ir/media/store/products/gallery/test-product-02.webp"},
                {"ok": True, "url": "https://3dprinthub.ir/media/store/products/unrelated-product.webp"},
            ],
        }
        row["server_ack_json"] = json.dumps(ack, ensure_ascii=False)

        payload = canonical_site_payload(row, site_url="https://3dprinthub.ir")

        self.assertEqual(
            payload["media_urls"],
            [
                main,
                "https://3dprinthub.ir/media/store/products/gallery/test-product-02.webp",
            ],
        )

    def test_primary_public_image_is_always_first_instagram_media(self):
        row = product_row()
        ack = json.loads(row["server_ack_json"])
        main = ack["public_main_image_url"]
        ack["images"] = [
            {"url": "https://3dprinthub.ir/media/store/products/test-02.webp", "ok": True},
            {"url": main, "ok": True},
            {"url": "https://3dprinthub.ir/media/store/products/test-03.webp", "ok": True},
        ]
        row["server_ack_json"] = json.dumps(ack, ensure_ascii=False)

        payload = canonical_site_payload(row, site_url="https://3dprinthub.ir")

        self.assertEqual(payload["media_urls"][0], main)
        self.assertEqual(len(payload["media_urls"]), 3)
        self.assertEqual(payload["media_urls"].count(main), 1)

    @patch("app.instagram_publish.get_secret", return_value="token")
    @patch("app.instagram_publish._wait_container")
    @patch("app.instagram_publish._request_json")
    def test_carousel_publish_records_receipt_and_never_uses_source_url(self, request_json, _wait, _secret):
        request_json.side_effect = [
            {"id": "child-1"},
            {"id": "child-2"},
            {"id": "carousel-1"},
            {"id": "media-1"},
        ]
        db = FakeDB(product_row())
        cfg = InstagramConfig(account_id="ig-123", api_version="v26.0", login_mode="instagram")
        result = publish_product(db, 42, cfg, site_url="https://3dprinthub.ir")
        self.assertEqual(result["media_id"], "media-1")
        self.assertEqual(result["site_product_url"], "https://3dprinthub.ir/store/product/test-product/")
        self.assertEqual(result["social_policy_version"], "instagram-product-v5-20260923")
        self.assertEqual(result["alt_texts"], ["نمای اصلی محصول", "نمای دوم محصول"])
        self.assertEqual(db.receipts[-1]["status"], "instagram_published")
        calls = [call.args[0] for call in request_json.call_args_list]
        self.assertTrue(all("makerworld" not in value.lower() for value in calls))
        parent_payload = request_json.call_args_list[2].kwargs["payload"]
        self.assertEqual(parent_payload["media_type"], "CAROUSEL")
        self.assertIn("لینک بیو", parent_payload["caption"])
        self.assertNotIn("utm_source=instagram", parent_payload["caption"])

    @patch("app.instagram_publish.get_secret", return_value="token")
    def test_same_site_ack_cannot_be_published_twice(self, _secret):
        row = product_row()
        db = FakeDB(row)
        db.record_sync_receipt(
            42,
            "instagram:old",
            "instagram_published",
            server_id="media-old",
            payload={"site_ack_fingerprint": row["server_ack_json"]},
        )
        with self.assertRaisesRegex(RuntimeError, "قبلاً"):
            publish_product(
                db,
                42,
                InstagramConfig(account_id="ig-123"),
                site_url="https://3dprinthub.ir",
            )

    def test_social_seo_v4_removes_false_free_claims_and_prefers_product_keyword(self):
        row = product_row()
        row["seo_title_fa"] = "چاپ سه بعدی رایگان اسکلتی اسپینوزور"
        row["seo_description_fa"] = "دانلود رایگان مدل و سفارش محصول"
        row["social_caption_fa"] = "چاپ سه‌بعدی رایگان برای همه"
        row["seo_focus_keyword"] = "اسکلتی اسپینوزور"
        row["keywords_json"] = json.dumps(
            ["اسکلتی اسپینوزور", "دایناسور متحرک"],
            ensure_ascii=False,
        )
        row["hashtags_fa_json"] = json.dumps(
            ["#دانلود_رایگان", "#اسکلتی_اسپینوزور"],
            ensure_ascii=False,
        )
        row["image_alt_texts_json"] = json.dumps(
            ["چاپ سه بعدی رایگان اسکلتی اسپینوزور", "نمای دوم محصول"],
            ensure_ascii=False,
        )

        payload = canonical_site_payload(row, site_url="https://3dprinthub.ir")

        combined = " ".join(
            [
                payload["caption"],
                *payload["hashtags"],
                *payload["alt_texts"],
            ]
        )
        self.assertNotIn("رایگان", combined)
        self.assertIn("#اسکلتی_اسپینوزور", payload["hashtags"])
        self.assertIn("3DPrintHub.ir", payload["caption"])
        self.assertIn("utm_source=instagram", payload["tracking_url"])
        self.assertLessEqual(len(payload["hashtags"]), 8)

    def test_non_public_product_fails_closed(self):
        row = product_row()
        ack = json.loads(row["server_ack_json"])
        ack["public_http_ok"] = False
        row["server_ack_json"] = json.dumps(ack, ensure_ascii=False)
        with self.assertRaisesRegex(RuntimeError, "تأیید عمومی"):
            canonical_site_payload(row, site_url="https://3dprinthub.ir")


if __name__ == "__main__":
    unittest.main()


class _ConnectionStub:
    def settings(self, require_bridge=False):
        return type("Settings", (), {"site_url": "https://3dprinthub.ir"})()


class _PublishStub:
    def __init__(self, db, *, make_public=True):
        self.db = db
        self.make_public = make_public
        self.calls = []

    def publish_many(self, product_ids, *, progress=None):
        self.calls.append(list(product_ids))
        if self.make_public:
            ack = json.loads(product_row()["server_ack_json"])
            self.db.row["server_ack_json"] = json.dumps(ack, ensure_ascii=False)
            return {"published": len(product_ids), "failed": 0, "items": []}
        return {"published": 0, "failed": len(product_ids), "items": []}


class Phase50InstagramDeliveryReadinessTests(unittest.TestCase):
    def _core(self):
        db = FakeDB(product_row())
        return InstagramCore(db, _ConnectionStub(), _PublishStub(db))

    @patch("app.buffer_publish.test_connection")
    def test_default_shop_grid_story_is_ready_without_mobile(self, connection):
        connection.return_value = {
            "id": "chan-1",
            "name": "3dprinthub_ir",
            "service": "instagram",
            "external_link": "https://instagram.com/3dprinthub_ir",
            "has_active_member_device": False,
        }
        core = self._core()
        state = core.delivery_readiness()
        self.assertTrue(state["ready"])
        self.assertFalse(state["requires_mobile_handoff"])
        self.assertEqual(state["story_link_mode"], "bio_shop_grid")
        self.assertEqual(state["feed_link_mode"], "buffer_shop_grid")
        self.assertFalse(state["has_active_member_device"])

    @patch("app.buffer_publish.test_connection")
    def test_native_sticker_mode_blocks_before_any_work_without_mobile(
        self, connection
    ):
        connection.return_value = {
            "id": "chan-1",
            "name": "3dprinthub_ir",
            "service": "instagram",
            "external_link": "https://instagram.com/3dprinthub_ir",
            "has_active_member_device": False,
        }
        core = self._core()
        core.db.set_setting(
            "instagram_story_link_mode", "native_sticker_notification"
        )

        state = core.delivery_readiness()
        self.assertFalse(state["ready"])
        self.assertTrue(state["requires_mobile_handoff"])
        self.assertFalse(state["has_active_member_device"])
        self.assertTrue(any("Buffer mobile" in value for value in state["blockers"]))

        with self.assertRaisesRegex(RuntimeError, "Buffer mobile"):
            core.publish_site_then_instagram([42])
        self.assertEqual(core.publish_core.calls, [])

    @patch("app.buffer_publish.test_connection")
    def test_mobile_ready_allows_optional_native_sticker_workflow(self, connection):
        connection.return_value = {
            "id": "chan-1",
            "name": "3dprinthub_ir",
            "service": "instagram",
            "external_link": "https://instagram.com/3dprinthub_ir",
            "has_active_member_device": True,
        }
        core = self._core()
        core.db.set_setting(
            "instagram_story_link_mode", "native_sticker_notification"
        )
        state = core.delivery_readiness()
        self.assertTrue(state["ready"])
        self.assertTrue(state["requires_mobile_handoff"])
        self.assertTrue(state["has_active_member_device"])


class Phase50SiteThenInstagramOrderTests(unittest.TestCase):
    def _core(self, *, public=False, site_success=True):
        row = product_row()
        if not public:
            row["server_ack_json"] = "{}"
        db = FakeDB(row)
        site = _PublishStub(db, make_public=site_success)
        core = InstagramCore(db, _ConnectionStub(), site)
        events = []
        original_site = site.publish_many

        def site_publish(ids, *, progress=None):
            events.append("site")
            return original_site(ids, progress=progress)

        site.publish_many = site_publish
        original_preview = core.preview
        core.preview = lambda pid: original_preview(pid)

        def instagram_publish(ids, *, progress=None):
            events.append("instagram")
            return {"requested": len(ids), "published": len(ids), "failed": 0, "results": [], "failures": []}

        core.publish_many = instagram_publish
        core.require_delivery_readiness = lambda: {
            "ready": True,
            "provider": "buffer",
            "has_active_member_device": True,
        }
        return core, site, events
    def test_site_publish_runs_before_instagram_for_unpublished_product(self):
        core, site, events = self._core(public=False, site_success=True)
        result = core.publish_site_then_instagram([42])
        self.assertEqual(events, ["site", "instagram"])
        self.assertEqual(site.calls, [[42]])
        self.assertEqual(result["instagram"]["published"], 1)

    def test_already_public_product_skips_site_publish(self):
        core, site, events = self._core(public=True, site_success=True)
        result = core.publish_site_then_instagram([42])
        self.assertEqual(events, ["instagram"])
        self.assertEqual(site.calls, [])
        self.assertEqual(result["instagram"]["published"], 1)

    def test_site_failure_never_reaches_instagram(self):
        core, site, events = self._core(public=False, site_success=False)
        result = core.publish_site_then_instagram([42])
        self.assertEqual(events, ["site"])
        self.assertEqual(result["instagram"]["published"], 0)
        self.assertEqual(len(result["site_blocked"]), 1)
