from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.phase49_3i15_bulk_discovery_images import (
    build_product_payload,
    candidate_manifest_path,
    manifest_image_text,
    normalize_product_limit,
    read_candidate_manifest,
    write_candidate_manifest,
)


class Phase493I15BulkDiscoveryTests(unittest.TestCase):
    def test_product_limit_is_bounded_to_one_hundred(self):
        self.assertEqual(normalize_product_limit(30), 30)
        self.assertEqual(normalize_product_limit(50), 50)
        self.assertEqual(normalize_product_limit(100), 100)
        self.assertEqual(normalize_product_limit(999), 100)
        self.assertEqual(normalize_product_limit(0), 1)
        self.assertEqual(normalize_product_limit("bad"), 30)

    def test_candidate_manifest_round_trip_does_not_require_schema_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = {
                "source_code": "makerworld",
                "external_id": "2834255",
                "source_url": "https://makerworld.com/en/models/2834255-cake-stand",
                "source_title": "Cake stand",
                "thumbnail_url": "https://img.example/thumb.jpg",
            }
            path = write_candidate_manifest(
                tmp,
                candidate,
                requested_images=10,
                image_urls=[f"https://img.example/{i}.jpg" for i in range(12)],
                downloaded_images=[f"C:/catalog/{i}.jpg" for i in range(10)],
                final_url=candidate["source_url"],
                http_status=200,
            )
            self.assertEqual(path, candidate_manifest_path(tmp, "makerworld", "2834255"))
            payload = read_candidate_manifest(tmp, "makerworld", "2834255")
            self.assertEqual(payload["requested_images"], 10)
            self.assertEqual(payload["image_count"], 10)
            self.assertEqual(payload["downloaded_count"], 10)
            self.assertEqual(len(payload["image_urls"]), 10)
            self.assertIn("10/10", manifest_image_text(payload))

    def test_build_product_payload_uses_staged_images_without_direct_fetch(self):
        candidate = {
            "source_code": "makerworld",
            "external_id": "2834255",
            "source_url": "https://makerworld.com/en/models/2834255-cake-stand",
            "source_title": "Cake stand",
            "thumbnail_url": "https://img.example/thumb.jpg",
        }
        manifest = {
            "requested_images": 10,
            "final_url": candidate["source_url"],
            "image_urls": [f"https://img.example/{i}.jpg" for i in range(10)],
            "local_dir": "C:/catalog/2834255",
        }
        payload = build_product_payload(candidate, manifest, {"reference_only": False}, "MakerWorld")
        self.assertEqual(payload["source_name"], "MakerWorld")
        self.assertEqual(payload["download_image_limit"], 10)
        self.assertEqual(len(json.loads(payload["images_json"])), 10)
        self.assertEqual(json.loads(payload["selected_images_json"]), json.loads(payload["images_json"]))
        self.assertEqual(payload["primary_image_url"], "https://img.example/0.jpg")
        self.assertEqual(payload["workflow_status"], "review")
        self.assertEqual(payload["upload_ready"], 0)

    def test_source_contract_has_no_rich_direct_dependency(self):
        source = Path(__file__).parents[1] / "app" / "phase49_3i15_bulk_discovery_images.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("extract_direct_link(", text)
        self.assertIn("_dom_image_urls", text)
        self.assertIn("_download_context_images", text)
        self.assertIn("اضافه کردن انتخاب‌شده‌ها به محصولات", text)
        self.assertIn("values=(10, 20, 30, 50, 100)", text)
        self.assertIn("values=(5, 10, 15, 20)", text)


if __name__ == "__main__":
    unittest.main()
