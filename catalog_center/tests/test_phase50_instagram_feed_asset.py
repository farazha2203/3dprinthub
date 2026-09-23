from __future__ import annotations

import hashlib
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
    def test_github_raw_preparation_uses_exact_local_final_bytes_and_skips_site_http(
        self, urlopen, connect_ftp, ensure_remote_dir, verify_public
    ):
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
            root = Path(local_appdata)
            source1 = root / "demo-01.webp"
            source2 = root / "demo-02.webp"
            source1.write_bytes(self._webp_bytes())
            source2.write_bytes(self._webp_bytes((800, 1000)))
            sha1 = hashlib.sha256(source1.read_bytes()).hexdigest()
            sha2 = hashlib.sha256(source2.read_bytes()).hexdigest()
            payload = {
                "media_urls": [
                    f"https://3dprinthub.ir/media/p/7/{sha1[:12]}/demo-01.webp",
                    f"https://3dprinthub.ir/media/p/7/{sha2[:12]}/demo-02.webp",
                ]
            }
            db = _DB()
            db.row["image_metadata_json"] = json.dumps(
                [
                    {
                        "seo_filename": source1.name,
                        "final_local_file": str(source1),
                        "final_sha256": sha1,
                    },
                    {
                        "seo_filename": source2.name,
                        "final_local_file": str(source2),
                        "final_sha256": sha2,
                    },
                ]
            )
            with patch.dict("os.environ", {"LOCALAPPDATA": local_appdata}):
                result = prepare_product_feed_assets(
                    db,
                    7,
                    settings,
                    payload,
                    publish_to_site=False,
                )
                self.assertEqual(len(result["local_paths"]), 2)
                self.assertTrue(
                    all(Path(value).is_file() for value in result["local_paths"])
                )

        self.assertEqual(result["urls"], [])
        self.assertFalse(result["published_to_site"])
        self.assertEqual(result["source_urls"], payload["media_urls"])
        urlopen.assert_not_called()
        connect_ftp.assert_not_called()
        ensure_remote_dir.assert_not_called()
        verify_public.assert_not_called()

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
