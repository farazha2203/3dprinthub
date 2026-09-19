from __future__ import annotations

import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from app.instagram_feed_asset import prepare_product_feed_assets
from app.site_connection import SiteConnection


class _DB:
    def __init__(self):
        self.row = {
            "id": 7,
            "server_ack_json": json.dumps({"revision": 3}),
        }

    def product(self, product_id):
        return self.row if int(product_id) == 7 else None

    def setting(self, key, default=""):
        if key == "instagram_feed_remote_root":
            return "/public_html/media/instagram/feed/products"
        return default


class _Response:
    def __init__(self, data: bytes):
        self._data = data

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit=-1):
        return self._data


class InstagramFeedAssetTests(unittest.TestCase):
    @staticmethod
    def _webp_bytes(size=(1000, 750)) -> bytes:
        buffer = BytesIO()
        Image.new("RGB", size, "#a67c52").save(buffer, format="WEBP")
        return buffer.getvalue()

    @patch("app.instagram_feed_asset._verify_public_image")
    @patch("app.instagram_feed_asset._ensure_remote_dir")
    @patch("app.instagram_feed_asset.connect_ftp")
    @patch("app.instagram_feed_asset.urllib_request.urlopen")
    def test_webp_sources_are_rehosted_as_static_png_for_buffer(
        self, urlopen, connect_ftp, ensure_remote_dir, verify_public
    ):
        urlopen.side_effect = [
            _Response(self._webp_bytes()),
            _Response(self._webp_bytes((800, 1000))),
        ]
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
            "media_urls": [
                "https://3dprinthub.ir/media/p/7/a/demo-01.webp",
                "https://3dprinthub.ir/media/p/7/b/demo-02.webp",
            ]
        }

        with tempfile.TemporaryDirectory() as local_appdata:
            with patch.dict("os.environ", {"LOCALAPPDATA": local_appdata}):
                result = prepare_product_feed_assets(_DB(), 7, settings, payload)

        self.assertEqual(result["format"], "png")
        self.assertEqual(len(result["urls"]), 2)
        self.assertEqual(result["source_urls"], payload["media_urls"])
        self.assertTrue(all(url.endswith(".png") for url in result["urls"]))
        self.assertTrue(all("/media/instagram/feed/products/7/" in url for url in result["urls"]))
        ensure_remote_dir.assert_called_once()
        self.assertEqual(
            ensure_remote_dir.call_args.args[1].split("/")[:6],
            ["", "public_html", "media", "instagram", "feed", "products"],
        )
        self.assertEqual(ftp.storbinary.call_count, 2)
        self.assertEqual(verify_public.call_count, 2)

    @patch("app.instagram_feed_asset._verify_public_image")
    @patch("app.instagram_feed_asset._ensure_remote_dir")
    @patch("app.instagram_feed_asset.connect_ftp")
    @patch("app.instagram_feed_asset.urllib_request.urlopen")
    def test_extreme_aspect_ratio_is_letterboxed_into_instagram_range(
        self, urlopen, connect_ftp, _ensure_remote_dir, _verify_public
    ):
        urlopen.return_value = _Response(self._webp_bytes((300, 1200)))
        connect_ftp.return_value = MagicMock()
        settings = SiteConnection(
            ftp_host="ftp.3dprinthub.ir",
            ftp_port=21,
            ftp_user="demo",
            ftp_password="secret",
            remote_root="/3dprinthub",
            site_url="https://3dprinthub.ir",
            bridge_token="",
        )
        with tempfile.TemporaryDirectory() as local_appdata:
            with patch.dict("os.environ", {"LOCALAPPDATA": local_appdata}):
                result = prepare_product_feed_assets(
                    _DB(),
                    7,
                    settings,
                    {"media_urls": ["https://3dprinthub.ir/media/p/7/a/tall.webp"]},
                )

        dims = result["dimensions"][0]
        ratio = dims["width"] / dims["height"]
        self.assertGreaterEqual(ratio, 0.75)
        self.assertLessEqual(ratio, 1.91)


if __name__ == "__main__":
    unittest.main()
