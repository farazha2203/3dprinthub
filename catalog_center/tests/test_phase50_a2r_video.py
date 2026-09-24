from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.db import Database
from app.page_extractor import ExtractedPage, ExtractedImage, parse_page_snapshot
from app.phase49_3i49_site_publish import _copy_publish_videos
from app.site_connection import SiteConnection, verify_publish_item
from qt6 import acquisition_runtime


class Phase50A2RVideoTests(unittest.TestCase):
    def test_database_adds_video_columns_without_changing_queue_contract(self):
        with tempfile.TemporaryDirectory() as td:
            db = Database(Path(td) / "catalog.sqlite3")
            columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
            self.assertTrue({"video_links_json", "selected_video_links_json", "local_video_files_json"}.issubset(columns))
            db.close()

    def test_extracted_page_serializes_video_links(self):
        page = ExtractedPage(
            source_url="https://example.com/p/1", final_url="https://example.com/p/1",
            source_title="Demo", source_description="", author_name="", license_name="", license_url="",
            source_category="", source_categories=[], tags=[], source_price=None, source_currency="",
            estimated_weight_grams=None, estimated_print_minutes=None, source_rating=None,
            source_rating_count=0, source_like_count=0, source_download_count=0, source_view_count=0,
            source_published_at="", source_updated_at="", images=[], file_links=[],
            video_links=["https://example.com/video.mp4"], specs={}, body_text="",
        )
        self.assertEqual(page.as_dict()["video_links"], ["https://example.com/video.mp4"])

    def test_makerworld_animated_picture_is_discovered_as_video(self):
        snapshot = {
            "source_url": "https://makerworld.com/en/models/1-demo",
            "final_url": "https://makerworld.com/en/models/1-demo",
            "title": "Demo",
            "embedded_json": [json.dumps({
                "props": {"pageProps": {"design": {"designExtension": {
                    "design_pictures": [{
                        "name": "GIF_20260818221845673.gif",
                        "url": "https://cdn.example.test/design/demo.gif",
                    }],
                    "design_video": [],
                }}}}
            })],
            "video_links": [],
            "links": [], "dom_images": [], "picture_sources": [],
            "network_json": [], "json_ld": [], "metas": {},
            "body_text": "", "breadcrumbs": [], "spec_rows": [],
            "labeled_sections": [],
        }
        page = parse_page_snapshot(snapshot)
        self.assertEqual(page.video_links, ["https://cdn.example.test/design/demo.gif"])

    def test_video_download_is_same_domain_bounded_and_recordable(self):
        payload = {
            "source_url": "https://example.com/p/1",
            "selected_video_links_json": json.dumps([
                "https://example.com/a.mp4", "https://cdn.other.test/b.mp4"
            ]),
        }
        with tempfile.TemporaryDirectory() as td, patch(
            "qt6.acquisition_runtime.download_public_file",
            side_effect=lambda url, target, **kwargs: (Path(target).parent.mkdir(parents=True, exist_ok=True), Path(target).write_bytes(b"video"), target)[2],
        ) as mocked:
            saved = acquisition_runtime._download_public_videos(
                payload, Path(td), referer=payload["source_url"], same_domain_only=True
            )
        self.assertEqual(len(saved), 1)
        self.assertEqual(mocked.call_count, 1)
        self.assertTrue(saved[0].replace("\\", "/").endswith("/videos/product-video-01.mp4"))

    def test_crawl_keeps_unlinked_rows_useful_with_identity_media_fallback(self):
        pages = (Path(__file__).resolve().parents[1] / "qt6" / "pages.py").read_text(encoding="utf-8")
        kernel = (Path(__file__).resolve().parents[1] / "qt6" / "kernel.py").read_text(encoding="utf-8")
        self.assertIn("def _queue_local_identity_items", pages)
        self.assertIn("self.kernel.acquisition.queue_image_count", pages)
        self.assertIn("identity_local_items", kernel)
        self.assertIn("کاندیدای کشف‌شده؛ هنوز دریافت نشده", pages)
        self.assertIn("def _queue_is_incomplete", pages)
        self.assertIn("queue_completeness_reasons", kernel)

    def test_crawl_explicit_recovery_uses_mature_adaptive_path(self):
        source = (Path(__file__).resolve().parents[1] / "qt6" / "pages.py").read_text(encoding="utf-8")
        start = source.index("def _recover_selected_queue")
        block = source[start:start + 12000]
        self.assertIn("force_recover=True", block)
        self.assertIn("adaptive_fallback=True", block)
        self.assertIn("has_title", block)
        self.assertIn("has_description", block)
        self.assertIn("local_count >= image_limit", block)
        self.assertIn("Queue item has no valid public Product URL/source.", block)

    def test_site_batch_copies_only_product_owned_video_with_checksum(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            video = source / "videos" / "received.gif"
            video.parent.mkdir(parents=True)
            video.write_bytes(b"G" * 2048)
            model_dir = root / "batch-model"
            model_dir.mkdir()
            names = _copy_publish_videos(
                {"local_video_files_json": json.dumps([str(video)])},
                source,
                model_dir,
            )
            self.assertEqual(names, ["product-video-01.gif"])
            self.assertEqual((model_dir / "videos" / names[0]).read_bytes(), video.read_bytes())

    def test_public_verifier_separates_product_video_from_image_checks(self):
        cfg = SiteConnection("ftp", 21, "u", "p", "/", "https://3dprinthub.ir", "token")
        page_html = (
            b'<img src="/media/p/536/abc/main.webp">'
            b'<img src="/media/store/products/videos/48/hash.gif">'
        )

        def fake_get(_cfg, value, *, expect_image=False, expect_video=False, attempts=3):
            if not expect_image and not expect_video:
                return {"ok": True, "url": "https://3dprinthub.ir/store/product/demo/", "http_status": 200,
                        "content_type": "text/html", "error": "", "body": page_html}
            url = "https://3dprinthub.ir" + str(value)
            return {"ok": True, "url": url, "http_status": 200,
                    "content_type": "image/gif" if expect_video else "image/webp",
                    "error": "", "body": b"x"}

        item = {
            "product_url": "/store/product/demo/",
            "public_videos": [{"url": "/media/store/products/videos/48/hash.gif"}],
        }
        with patch("app.site_connection._public_get", side_effect=fake_get):
            result = verify_publish_item(cfg, item)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["images"]), 1)
        self.assertEqual(len(result["videos"]), 1)
        self.assertEqual(result["videos"][0]["content_type"], "image/gif")


if __name__ == "__main__":
    unittest.main()
