from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from store.management.commands.phase37_import_catalog_center import import_videos


class _Asset:
    pk = 48

    def __init__(self):
        self.technical_specs = {}
        self.source_payload = {}
        self.saved = False

    def save(self, **kwargs):
        self.saved = True


class _Storage:
    def __init__(self):
        self.files = {}

    def exists(self, name):
        return name in self.files

    def save(self, name, handle):
        self.files[name] = handle.read()
        return name

    def url(self, name):
        return "/media/" + name


class Phase50A2RSiteVideoTests(SimpleTestCase):
    def test_receiver_persists_public_video_metadata_without_schema_change(self):
        with tempfile.TemporaryDirectory() as td:
            model_dir = Path(td)
            video_dir = model_dir / "videos"
            video_dir.mkdir()
            video = video_dir / "product-video-01.gif"
            video.write_bytes(b"G" * 4096)
            asset = _Asset()
            storage = _Storage()
            data = {"local_video_files_json": '["product-video-01.gif"]'}

            with patch(
                "store.management.commands.phase37_import_catalog_center.default_storage",
                storage,
            ):
                result = import_videos(asset, model_dir, data)

            self.assertTrue(asset.saved)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["kind"], "animated_image")
            self.assertTrue(result[0]["url"].startswith("/media/store/products/videos/48/"))
            self.assertEqual(asset.technical_specs["desktop_catalog_public_videos"], result)
            self.assertEqual(asset.source_payload["public_videos"], result)

    def test_product_detail_renders_motion_media_from_imported_asset(self):
        template = (
            Path(__file__).resolve().parents[1]
            / "templates"
            / "store"
            / "product_detail.html"
        ).read_text(encoding="utf-8")
        self.assertIn("desktop_catalog_public_videos", template)
        self.assertIn("data-product-motion-media", template)
        self.assertIn("<video src=", template)
        self.assertIn('media.kind == "animated_image"', template)
