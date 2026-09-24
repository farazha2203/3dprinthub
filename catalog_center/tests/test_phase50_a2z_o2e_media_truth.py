import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from app.db import Database
from app.instagram_publish import canonical_site_payload
from app.phase50_a2w_media_sync import media_truth_snapshot
from qt6.kernel import build_kernel


class Phase50A2ZO2EMediaTruthTests(unittest.TestCase):
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

    def _product(self, *, stale_sha=False, selected_only_first=True):
        local_dir = self.root / "collected" / "makerworld" / "9001"
        image_dir = local_dir / "images"
        seo_dir = local_dir / "seo_images"
        image_dir.mkdir(parents=True)
        seo_dir.mkdir(parents=True)

        source_1 = image_dir / "01.jpg"
        source_2 = image_dir / "02.jpg"
        final_1 = seo_dir / "lamp-selected-01.webp"
        final_2 = seo_dir / "lamp-other-02.webp"
        Image.new("RGB", (320, 240), "#aa5522").save(source_1, "JPEG")
        Image.new("RGB", (320, 240), "#2255aa").save(source_2, "JPEG")
        Image.new("RGB", (320, 240), "#aa5522").save(final_1, "WEBP")
        Image.new("RGB", (320, 240), "#2255aa").save(final_2, "WEBP")

        historical = (
            self.root
            / "collected"
            / "makerworld"
            / "9001_refetch_20260924"
            / "images"
        )
        historical.mkdir(parents=True)
        Image.new("RGB", (320, 240), "#00aa44").save(
            historical / "01.jpg",
            "JPEG",
        )

        url1 = "https://makerworld.com/media/lamp-1.jpg"
        url2 = "https://makerworld.com/media/lamp-2.jpg"
        sha1 = hashlib.sha256(final_1.read_bytes()).hexdigest()
        sha2 = hashlib.sha256(final_2.read_bytes()).hexdigest()
        if stale_sha:
            sha1 = "0" * 64

        (local_dir / "page_extract.json").write_text(
            json.dumps({
                "images": [
                    {"url": url1, "local_file": str(source_1)},
                    {"url": url2, "local_file": str(source_2)},
                ]
            }),
            encoding="utf-8",
        )
        selected = [url1] if selected_only_first else [url1, url2]
        self.db.upsert_product({
            "source_code": "makerworld",
            "external_id": "9001",
            "source_url": "https://makerworld.com/en/models/9001-lamp",
            "source_title": "Lamp",
            "title_fa": "چراغ",
            "local_dir": str(local_dir),
            "images_json": json.dumps([url1, url2]),
            "selected_images_json": json.dumps(selected),
            "primary_image_url": url1,
            "image_metadata_json": json.dumps([
                {
                    "source_url": url1,
                    "seo_filename": final_1.name,
                    "final_local_file": str(final_1),
                    "final_sha256": sha1,
                },
                {
                    "source_url": url2,
                    "seo_filename": final_2.name,
                    "final_local_file": str(final_2),
                    "final_sha256": sha2,
                },
            ]),
        })
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("makerworld", "9001"),
        ).fetchone()
        return int(row["id"]), url1, url2, final_1, final_2

    def test_current_gallery_excludes_historical_refetch_and_uses_selected_final_file(self):
        product_id, url1, url2, final1, _final2 = self._product()
        items = self.kernel.images.current_local_items(product_id)

        self.assertEqual([item["url"] for item in items], [url1, url2])
        self.assertEqual(Path(items[0]["path"]).resolve(), final1.resolve())
        self.assertTrue(items[0]["selected"])
        self.assertFalse(
            any("refetch_20260924" in str(item["path"]) for item in items)
        )

    def test_social_payload_keeps_only_public_media_matching_selected_local_authority(self):
        product_id, _url1, _url2, final1, final2 = self._product()
        row = dict(self.db.product(product_id))
        sha1 = hashlib.sha256(final1.read_bytes()).hexdigest()
        sha2 = hashlib.sha256(final2.read_bytes()).hexdigest()
        selected_public = (
            f"https://3dprinthub.ir/media/p/9001/{sha1[:12]}/"
            "lamp-selected-01.webp"
        )
        stale_public = (
            f"https://3dprinthub.ir/media/p/9001/{sha2[:12]}/"
            "lamp-other-02.webp"
        )
        row["server_ack_json"] = json.dumps({
            "product_url": "/store/product/lamp/",
            "public_http_ok": True,
            "public_main_image_url": stale_public,
            "public_images": [
                {"url": stale_public, "ok": True},
                {"url": selected_public, "ok": True},
            ],
        })

        payload = canonical_site_payload(
            row,
            site_url="https://3dprinthub.ir",
        )
        self.assertEqual(payload["media_urls"], [selected_public])

        row["server_ack_json"] = json.dumps({
            "product_url": "/store/product/lamp/",
            "public_http_ok": True,
            "public_main_image_url": stale_public,
            "public_images": [{"url": stale_public, "ok": True}],
        })
        with self.assertRaisesRegex(
            RuntimeError,
            "Public/Social media parity failed",
        ):
            canonical_site_payload(
                row,
                site_url="https://3dprinthub.ir",
            )

    def test_truth_snapshot_reports_selected_sha_drift(self):
        product_id, _url1, _url2, _final1, _final2 = self._product(
            stale_sha=True
        )
        result = media_truth_snapshot(
            self.db,
            self.kernel.images,
            product_id,
        )
        self.assertTrue(result["selected_media_error"])
        self.assertTrue(
            any(
                "Selected media truth" in item
                for item in result["mismatches"]
            )
        )

    def test_product_wizard_refresh_is_local_truth_only(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "qt6"
            / "product_wizard.py"
        ).read_text(encoding="utf-8")
        marker = "recover_site_media=False"
        self.assertIn(marker, source)
        self.assertIn("current_local_items", source)


if __name__ == "__main__":
    unittest.main()
