from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.instagram_story_asset import _render_html, _render_story, prepare_product_story_asset
from app.site_connection import SiteConnection


class _DB:
    def __init__(self):
        self.row = {
            "id": 7,
            "server_ack_json": '{"revision": 2}',
            "title_fa": "آباژور موج‌دار",
            "short_description_fa": "نور دکوراتیو مدرن",
            "sales_bullets_json": '["طراحی دقیق","قابل سفارش"]',
        }

    def product(self, product_id):
        return self.row if int(product_id) == 7 else None

    def setting(self, key, default=""):
        if key == "instagram_story_remote_root":
            return "/public_html/media/instagram/stories/products"
        return default


class InstagramStoryAssetTests(unittest.TestCase):
    @patch("app.instagram_story_asset._font_uri", return_value="file:///font.ttf")
    @patch("app.instagram_story_asset._logo_uri", return_value="file:///logo.png")
    def test_story_cta_uses_product_link_copy_not_raw_product_url(
        self, _logo, _font
    ):
        rendered = _render_html(
            image_url="https://cdn.example.com/product.webp",
            product_url="https://3dprinthub.ir/store/product/demo-product/",
            copy={
                "title": "محصول تست",
                "subtitle": "توضیح تست",
                "bullets": ["ویژگی یک"],
            },
        )
        self.assertIn("مشاهده و سفارش محصول", rendered)
        self.assertIn("3DPrintHub.ir", rendered)
        self.assertIn("لینک همین محصول", rendered)
        self.assertNotIn("store/product/demo-product", rendered)

    @patch("app.instagram_story_asset.subprocess.run")
    @patch("app.instagram_story_asset._render_html", return_value="<html><body>story</body></html>")
    def test_render_uses_isolated_headless_profile(self, _render_html, run):
        with tempfile.TemporaryDirectory() as local_appdata:
            def fake_run(command, **_kwargs):
                direct = next(
                    (item for item in command if item.startswith("--screenshot=")),
                    "",
                )
                if direct:
                    screenshot = direct.split("=", 1)[1]
                else:
                    script = str(command[-1])
                    marker = "'--screenshot="
                    screenshot = script.split(marker, 1)[1].split("'", 1)[0]
                Path(screenshot).write_bytes(b"x" * 60000)

            run.side_effect = fake_run
            with patch.dict("os.environ", {"LOCALAPPDATA": local_appdata}):
                path = _render_story(
                    {
                        "id": 7,
                        "server_ack_json": '{"revision": 3}',
                        "title_fa": "آباژور",
                        "short_description_fa": "دکور",
                        "sales_bullets_json": "[]",
                    },
                    {
                        "media_urls": ["https://3dprinthub.ir/media/p/7/demo.webp"],
                        "product_url": "https://3dprinthub.ir/store/product/demo/",
                    },
                )

            command = run.call_args.args[0]
            rendered_command = " ".join(str(arg) for arg in command)
            self.assertTrue(path.is_file())
            self.assertIn("--user-data-dir=", rendered_command)
            self.assertIn("--no-first-run", rendered_command)
            self.assertIn("--no-default-browser-check", rendered_command)
            self.assertIn("--run-all-compositor-stages-before-draw", rendered_command)
            self.assertIn("--virtual-time-budget=4000", rendered_command)
            if os.name == "nt":
                self.assertIn("Start-Process", rendered_command)
                self.assertIn("-Wait", rendered_command)

    @patch("app.instagram_story_asset._verify_public_image")
    @patch("app.instagram_story_asset._ensure_remote_dir")
    @patch("app.instagram_story_asset.connect_ftp")
    @patch("app.instagram_story_asset._render_story")
    def test_prepare_uploads_to_public_story_path(
        self, render_story, connect_ftp, ensure_remote_dir, verify_public
    ):
        with tempfile.TemporaryDirectory() as tmp:
            rendered = Path(tmp) / "story.png"
            rendered.write_bytes(b"png" * 20000)
            render_story.return_value = rendered
            ftp = MagicMock()
            connect_ftp.return_value = ftp
            settings = SiteConnection(
                ftp_host="ftp.3dprinthub.ir",
                ftp_port=21,
                ftp_user="demo",
                ftp_password="secret",
                remote_root="/3dprinthub",
                site_url="https://3dprinthub.ir",
                bridge_token="",
            )
            payload = {
                "media_urls": ["https://3dprinthub.ir/media/product.webp"],
                "product_url": "https://3dprinthub.ir/store/product/demo/",
            }

            result = prepare_product_story_asset(_DB(), 7, settings, payload)

            self.assertEqual(result["style_id"], "3dprinthub_instagram_gold_navy_v4_iransans_product_link")
            self.assertEqual(result["font_family"], "IRANSansWeb(FaNum)")
            self.assertEqual(result["width"], 1080)
            self.assertEqual(result["height"], 1920)
            self.assertTrue(
                result["url"].startswith(
                    "https://3dprinthub.ir/media/instagram/stories/products/7/"
                )
            )
            ensure_remote_dir.assert_called_once()
            remote_dir = ensure_remote_dir.call_args.args[1]
            self.assertEqual(
                remote_dir,
                "/public_html/media/instagram/stories/products/7",
            )
            command = ftp.storbinary.call_args.args[0]
            self.assertTrue(command.startswith("STOR /public_html/media/instagram/stories/products/7/"))
            verify_public.assert_called_once_with(
                result["url"],
                timeout=30,
            )

    @patch("app.instagram_story_asset._verify_public_image")
    @patch("app.instagram_story_asset._ensure_remote_dir")
    @patch("app.instagram_story_asset.connect_ftp")
    @patch("app.instagram_story_asset.resolve_local_product_media")
    @patch("app.instagram_story_asset._render_story")
    def test_github_raw_preparation_renders_from_local_product_media_without_site_ftp(
        self,
        render_story,
        resolve_local,
        connect_ftp,
        ensure_remote_dir,
        verify_public,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            rendered = Path(tmp) / "story.png"
            rendered.write_bytes(b"png" * 20000)
            render_story.return_value = rendered
            source = Path(tmp) / "product.webp"
            source.write_bytes(b"local-product-bytes")
            resolve_local.return_value = source
            settings = SiteConnection(
                ftp_host="ftp.3dprinthub.ir",
                ftp_port=21,
                ftp_user="demo",
                ftp_password="secret",
                remote_root="/3dprinthub",
                site_url="https://3dprinthub.ir",
                bridge_token="",
            )
            payload = {
                "media_urls": ["https://3dprinthub.ir/media/product.webp"],
                "product_url": "https://3dprinthub.ir/store/product/demo/",
            }

            result = prepare_product_story_asset(
                _DB(),
                7,
                settings,
                payload,
                publish_to_site=False,
            )

            self.assertEqual(result["url"], "")
            self.assertEqual(result["local_path"], str(rendered))
            self.assertFalse(result["published_to_site"])
            self.assertEqual(
                result["style_id"],
                "3dprinthub_instagram_gold_navy_v4_iransans_product_link",
            )
            resolve_local.assert_called_once()
            rendered_payload = render_story.call_args.args[1]
            self.assertEqual(
                rendered_payload["media_urls"][0],
                source.resolve().as_uri(),
            )
            connect_ftp.assert_not_called()
            ensure_remote_dir.assert_not_called()
            verify_public.assert_not_called()


if __name__ == "__main__":
    unittest.main()
