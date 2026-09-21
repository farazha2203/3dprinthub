import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

from app.db import Database
from qt6.kernel import build_kernel


class Phase50A2WProductMediaSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = Database(self.root / "catalog.sqlite3")
        self.db.upsert_source({
            "code": "makerworld",
            "name": "MakerWorld",
            "enabled": 1,
            "methods": ["http"],
            "listing_urls": [],
            "model_url_pattern": "",
            "requires_login": False,
            "reference_only": False,
        })
        self.kernel = build_kernel(self.db)
    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def _product(self) -> int:
        local_dir = self.root / "product-625"
        image_dir = local_dir / "images"
        seo_dir = local_dir / "seo_images"
        image_dir.mkdir(parents=True)
        seo_dir.mkdir(parents=True)
        source = image_dir / "04.jpg"
        final = seo_dir / "product-01.webp"
        Image.new("RGB", (320, 240), (210, 170, 120)).save(source, "JPEG")
        Image.new("RGB", (320, 240), (210, 170, 120)).save(final, "WEBP")
        url = "local://04.jpg"
        self.db.upsert_product({
            "source_code": "makerworld",
            "external_id": "3190563",
            "source_url": "https://makerworld.com/en/models/3190563-test",
            "source_title": "Mini Articulated Skeletal Spinosaurus",
            "title_fa": "اسکلتی مینی متحرک اسپینوزور",
            "local_dir": str(local_dir),
            "images_json": json.dumps([url]),
            "selected_images_json": json.dumps([url]),
            "primary_image_url": url,
            "server_product_id": 39,
            "server_product_revision": 11,
            "workflow_status": "uploaded",
            "image_metadata_json": json.dumps([{
                "source_url": url,
                "seo_filename": final.name,
                "final_local_file": str(final),
                "metadata_ready": True,
            }]),
        })
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("makerworld", "3190563"),
        ).fetchone()
        return int(row["id"])

    @staticmethod
    def _server_payload():
        return {
            "id": 39,
            "main_image": "/media/p/625/aaa/product-01.webp",
            "images": [
                {"url": "/media/p/625/aaa/product-01.webp", "alt": "first", "is_primary": True},
                {"url": "/media/p/625/bbb/product-02.webp", "alt": "second", "is_primary": False},
            ],
            "profile": {"desktop_product_id": 625, "sync_revision": 11},
        }
    def test_slider_membership_edit_marks_server_product_id_linked_product_for_republish(self):
        product_id = self._product()
        before = dict(self.db.product(product_id))
        self.assertEqual(str(before.get("server_id") or ""), "")
        self.assertEqual(int(before["server_product_id"]), 39)

        self.kernel.stages.update(
            product_id,
            "slider",
            {"homepage_slider_enabled": 1},
        )

        after = dict(self.db.product(product_id))
        self.assertEqual(int(after["server_product_id"]), 39)
        self.assertEqual(int(after["server_product_revision"]), 11)
        self.assertEqual(int(after["homepage_slider_enabled"]), 1)
        self.assertEqual(int(after["needs_update"]), 1)
        self.assertEqual(int(after["upload_ready"]), 0)

    def test_refresh_recovers_missing_site_media_without_changing_site_selection(self):
        product_id = self._product()
        server = self._server_payload()

        def fake_download(url, target, **_kwargs):
            Image.new("RGB", (400, 300), (30, 100, 180)).save(target, "WEBP")
            return Path(target)

        with patch.object(
            self.kernel.connection,
            "bridge_settings",
            return_value=SimpleNamespace(site_url="https://3dprinthub.ir"),
        ), patch("app.epic49_site_sync.get_product", return_value=server), patch(
            "app.phase50_a2w_media_sync.download_public_file",
            side_effect=fake_download,
        ):
            first = self.kernel.refresh_product_media_truth(product_id)
            second = self.kernel.refresh_product_media_truth(product_id)

        self.assertEqual(first["site_media_count"], 2)
        self.assertEqual(first["selected_count"], 1)
        self.assertEqual(len(first["recovered"]), 1)
        self.assertTrue(any("تعداد Site=2" in item for item in first["mismatches"]))
        row = dict(self.db.product(product_id))
        selected = json.loads(row["selected_images_json"])
        canonical = json.loads(row["images_json"])
        self.assertEqual(selected, ["local://04.jpg"])
        self.assertEqual(len(canonical), 2)
        recovered_urls = [value for value in canonical if value.startswith("local://site-")]
        self.assertEqual(len(recovered_urls), 1)
        recovered_path = Path(row["local_dir"]) / "images" / recovered_urls[0].split("local://", 1)[1]
        self.assertTrue(recovered_path.is_file())
        self.assertEqual(second["recovered"], [])
        self.assertEqual(len(json.loads(self.db.product(product_id)["images_json"])), 2)

    def test_site_read_failure_preserves_local_media_truth(self):
        product_id = self._product()
        before = dict(self.db.product(product_id))
        with patch.object(
            self.kernel.connection,
            "bridge_settings",
            return_value=SimpleNamespace(site_url="https://3dprinthub.ir"),
        ), patch(
            "app.epic49_site_sync.get_product",
            side_effect=RuntimeError("bridge unavailable"),
        ):
            result = self.kernel.refresh_product_media_truth(product_id)
        after = dict(self.db.product(product_id))
        self.assertIn("bridge unavailable", result["site_error"])
        self.assertEqual(result["selected_count"], 1)
        self.assertEqual(after["selected_images_json"], before["selected_images_json"])
        self.assertEqual(after["images_json"], before["images_json"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
