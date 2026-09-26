import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.db import Database
from app.phase49_3i36_stage_finalization import ensure_schema as ensure_stage_schema
from qt6.kernel import InstagramCore


STAGES = (
    "quick",
    "commerce",
    "images",
    "content",
    "specs",
    "slider",
    "publish",
)


def locks_json(count: int) -> str:
    return json.dumps(
        {
            stage: {"locked": True, "locked_at": "2026-09-24T00:00:00Z"}
            for stage in STAGES[:count]
        },
        ensure_ascii=False,
    )
class ProductFilterContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Database(Path(self.temp.name) / "catalog.sqlite3")
        ensure_stage_schema(self.db)
        self.addCleanup(self.db.close)

    def add_product(
        self,
        external_id: str,
        *,
        locks: int,
        ai: int = 0,
        workflow: str = "review",
        server_id: str = "",
        needs_update: int = 0,
        upload_ready: int = 0,
    ) -> int:
        self.db.upsert_product({
            "source_code": "makerworld",
            "external_id": external_id,
            "source_url": f"https://example.com/models/{external_id}",
            "source_title": f"Product {external_id}",
            "title_fa": f"محصول {external_id}",
            "description_fa": "توضیح کامل",
            "images_json": json.dumps(["https://example.com/a.webp"]),
            "operator_stage_locks_json": locks_json(locks),
            "ai_completed_once": ai,
            "workflow_status": workflow,
            "server_id": server_id,
            "needs_update": needs_update,
            "upload_ready": upload_ready,
        })
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("makerworld", external_id),
        ).fetchone()
        return int(row["id"])

    def ids(self, filter_name: str) -> set[int]:
        return {
            int(row["id"])
            for row in self.db.products(filter_name=filter_name)
        }

    def test_operational_filters_use_stage_truth_and_final_social_receipts(self):
        ready = self.add_product("ready7", locks=7, ai=1)
        ai_six = self.add_product("ai6", locks=6, ai=1)
        self.add_product("six-no-ai", locks=6, ai=0)
        published = self.add_product(
            "site",
            locks=7,
            ai=1,
            workflow="uploaded",
            server_id="asset-site",
        )
        posted = self.add_product(
            "post",
            locks=7,
            ai=1,
            workflow="uploaded",
            server_id="asset-post",
        )
        story = self.add_product(
            "story",
            locks=7,
            ai=1,
            workflow="uploaded",
            server_id="asset-story",
        )
        submitted = self.add_product(
            "submitted",
            locks=7,
            ai=1,
            workflow="uploaded",
            server_id="asset-submitted",
        )
        social_acks = {
            posted: json.dumps(
                {"product_url": "/store/product/post/", "revision": 1},
                separators=(",", ":"),
            ),
            story: json.dumps(
                {"product_url": "/store/product/story/", "revision": 1},
                separators=(",", ":"),
            ),
            submitted: json.dumps(
                {"product_url": "/store/product/submitted/", "revision": 1},
                separators=(",", ":"),
            ),
        }
        for product_id, fingerprint in social_acks.items():
            self.db.conn.execute(
                "UPDATE products SET server_ack_json=? WHERE id=?",
                (fingerprint, product_id),
            )
        self.db.conn.commit()

        self.db.record_sync_receipt(
            posted,
            "instagram:buffer:post",
            "instagram_published",
            "post-1",
            {
                "buffer_status": "sent",
                "site_ack_fingerprint": social_acks[posted],
            },
        )
        self.db.record_sync_receipt(
            story,
            "instagram:buffer:story",
            "instagram_story_published",
            "story-1",
            {
                "buffer_status": "sent",
                "site_ack_fingerprint": social_acks[story],
            },
        )
        self.db.record_sync_receipt(
            submitted,
            "instagram:buffer:submitted",
            "instagram_submitted",
            "post-pending",
            {
                "buffer_status": "sending",
                "site_ack_fingerprint": social_acks[submitted],
            },
        )

        self.assertEqual(self.ids("ready_7"), {ready})
        self.assertEqual(self.ids("ai_6"), {ai_six})
        self.assertEqual(
            self.ids("published"),
            {published, posted, story, submitted},
        )
        self.assertEqual(self.ids("instagram_posted"), {posted})
        self.assertEqual(self.ids("instagram_story"), {story})


class _SocialDB:
    def __init__(self, *, story_mode="bio_shop_grid"):
        self.values = {
            "instagram_publish_provider": "buffer",
            "buffer_instagram_channel_id": "chan-1",
            "instagram_companion_story_enabled": "1",
            "instagram_story_link_mode": story_mode,
            "buffer_media_host": "site",
        }
        self.row = {
            "id": 7,
            "server_ack_json": json.dumps({
                "product_url": "/store/product/demo/",
                "public_http_ok": True,
                "public_images": [{
                    "url": "https://3dprinthub.ir/media/demo.webp",
                    "ok": True,
                }],
            }),
            "title_fa": "محصول تست",
            "description_fa": "توضیح",
            "image_alt_texts_json": json.dumps(["تصویر"]),
        }

    def setting(self, key, default=""):
        return self.values.get(key, default)

    def product(self, product_id):
        return self.row if int(product_id) == 7 else None


class _Connection:
    def settings(self, require_bridge=False):
        return SimpleNamespace(
            site_url="https://3dprinthub.ir",
            timeout=25,
        )


class _PublishCore:
    def publish_many(self, product_ids, *, progress=None):
        raise AssertionError("Site publish should not run for public test product")


class InstagramSplitContractTests(unittest.TestCase):
    def core(self, *, story_mode="bio_shop_grid"):
        return InstagramCore(
            _SocialDB(story_mode=story_mode),
            _Connection(),
            _PublishCore(),
        )

    @patch("app.buffer_publish.test_connection")
    def test_feed_readiness_is_not_blocked_by_native_story_mobile_requirement(
        self, test_connection
    ):
        test_connection.return_value = {
            "id": "chan-1",
            "name": "demo",
            "has_active_member_device": False,
        }
        core = self.core(story_mode="native_sticker_notification")
        feed = core.delivery_readiness(scope="feed")
        story = core.delivery_readiness(scope="story")
        self.assertTrue(feed["ready"])
        self.assertFalse(feed["requires_mobile_handoff"])
        self.assertFalse(story["ready"])
        self.assertTrue(story["requires_mobile_handoff"])

    @patch("app.buffer_publish.publish_product")
    @patch("app.buffer_media_host.rehost_buffer_assets")
    @patch("app.instagram_feed_asset.prepare_all_current_product_feed_assets")
    @patch("app.buffer_publish.test_connection")
    def test_feed_only_never_requests_companion_story(
        self,
        test_connection,
        prepare_feed,
        rehost,
        publish_feed,
    ):
        test_connection.return_value = {
            "id": "chan-1",
            "name": "demo",
            "has_active_member_device": False,
        }
        prepare_feed.return_value = {
            "urls": ["https://3dprinthub.ir/media/feed.png"],
            "local_paths": [],
            "source_urls": ["https://3dprinthub.ir/media/demo.webp"],
            "revision": "feedrev",
        }
        rehost.return_value = {
            "host": "site",
            "feed_urls": ["https://3dprinthub.ir/media/feed.png"],
            "story_url": "",
            "commit_sha": "",
        }
        publish_feed.return_value = {
            "provider_post_id": "post-1",
            "buffer_status": "sent",
        }
        core = self.core()
        core.preview = lambda product_id: {"product_url": "https://3dprinthub.ir/p/7"}
        result = core.publish_feed_many([7])

        self.assertEqual(result["scope"], "feed")
        self.assertEqual(result["published"], 1)
        kwargs = publish_feed.call_args.kwargs
        self.assertFalse(kwargs["companion_story"])
        self.assertNotIn("story_asset_url", kwargs)

    @patch("app.buffer_publish.publish_story_for_product")
    @patch("app.buffer_media_host.rehost_buffer_assets")
    @patch("app.instagram_story_asset.prepare_product_story_asset")
    @patch("app.buffer_publish.test_connection")
    def test_story_only_never_calls_feed_publisher(
        self,
        test_connection,
        prepare_story,
        rehost,
        publish_story,
    ):
        test_connection.return_value = {
            "id": "chan-1",
            "name": "demo",
            "has_active_member_device": True,
        }
        prepare_story.return_value = {
            "url": "https://3dprinthub.ir/media/story.png",
            "local_path": "",
            "revision": "storyrev",
        }
        rehost.return_value = {
            "host": "site",
            "feed_urls": [],
            "story_url": "https://3dprinthub.ir/media/story.png",
            "commit_sha": "",
        }
        publish_story.return_value = {
            "provider_post_id": "story-1",
            "buffer_status": "sent",
            "instagram_live_confirmed": True,
            "link_sticker_required": False,
        }
        core = self.core()
        core.preview = lambda product_id: {"product_url": "https://3dprinthub.ir/p/7"}
        result = core.publish_story_many([7])

        self.assertEqual(result["scope"], "story")
        self.assertEqual(result["published"], 1)
        feed_meta = rehost.call_args.args[2]
        self.assertEqual(feed_meta["local_paths"], [])
        self.assertEqual(feed_meta["source_urls"], [])
        publish_story.assert_called_once()


class ProductPageSourceContractTests(unittest.TestCase):
    def test_products_page_exposes_requested_filters_and_split_social_buttons(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "qt6"
            / "pages.py"
        ).read_text(encoding="utf-8")
        for marker in (
            '"آماده انتشار — ۷/۷ تیک", "ready_7"',
            '"تکمیل هوش مصنوعی — ۶/۷ تیک", "ai_6"',
            '"ارسال پست Instagram", "instagram_posted"',
            '"ارسال استوری Instagram", "instagram_story"',
            'self.instagram_post_btn = QPushButton("📸 ارسال پست Instagram")',
            'self.instagram_story_btn = QPushButton("📱 ارسال استوری Instagram")',
            "publish_site_then_feed",
            "publish_site_then_story",
        ):
            self.assertIn(marker, source)
        self.assertNotIn("instagram_publish_btn", source)


if __name__ == "__main__":
    unittest.main()
