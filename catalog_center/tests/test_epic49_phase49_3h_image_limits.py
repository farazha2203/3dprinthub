from __future__ import annotations

import json
import unittest

from app.phase49_3h_image_limits import (
    DEFAULT_IMAGE_LIMIT,
    HARD_MAX_IMAGE_LIMIT,
    cap_direct_result,
    normalize_image_limit,
)


class Phase493HImageLimitTests(unittest.TestCase):
    def test_canonical_default_and_hard_max(self):
        self.assertEqual(DEFAULT_IMAGE_LIMIT, 10)
        self.assertEqual(HARD_MAX_IMAGE_LIMIT, 20)
        self.assertEqual(normalize_image_limit(None), 10)
        self.assertEqual(normalize_image_limit("bad"), 10)
        self.assertEqual(normalize_image_limit(0), 1)
        self.assertEqual(normalize_image_limit(10), 10)
        self.assertEqual(normalize_image_limit(20), 20)
        self.assertEqual(normalize_image_limit(60), 20)
        self.assertEqual(normalize_image_limit(100), 20)

    def test_direct_result_caps_persisted_selected_and_downloaded_at_10(self):
        urls = [f"https://example.test/image-{i:03d}.jpg" for i in range(1, 101)]
        result = cap_direct_result(
            {
                "images_json": json.dumps(urls),
                "selected_images_json": json.dumps(urls),
                "downloaded_image_files": [f"C:/tmp/{i:03d}.jpg" for i in range(1, 101)],
                "primary_image_url": urls[50],
            },
            10,
        )
        images = json.loads(result["images_json"])
        selected = json.loads(result["selected_images_json"])
        self.assertEqual(len(images), 10)
        self.assertEqual(len(selected), 10)
        self.assertEqual(len(result["downloaded_image_files"]), 10)
        self.assertIn(result["primary_image_url"], images)

    def test_direct_result_caps_at_20_even_when_legacy_value_is_100(self):
        urls = [f"https://example.test/image-{i:03d}.jpg" for i in range(1, 101)]
        result = cap_direct_result(
            {
                "images_json": json.dumps(urls),
                "selected_images_json": json.dumps(urls),
                "downloaded_image_files": [f"C:/tmp/{i:03d}.jpg" for i in range(1, 101)],
                "primary_image_url": urls[0],
            },
            100,
        )
        self.assertEqual(len(json.loads(result["images_json"])), 20)
        self.assertEqual(len(json.loads(result["selected_images_json"])), 20)
        self.assertEqual(len(result["downloaded_image_files"]), 20)

    def test_selected_urls_must_be_subset_of_capped_images(self):
        all_urls = [f"https://example.test/{i}.jpg" for i in range(30)]
        selected = all_urls[5:25] + ["https://example.test/not-in-images.jpg"]
        result = cap_direct_result(
            {
                "images_json": json.dumps(all_urls),
                "selected_images_json": json.dumps(selected),
                "downloaded_image_files": [],
                "primary_image_url": all_urls[0],
            },
            10,
        )
        images = set(json.loads(result["images_json"]))
        self.assertLessEqual(len(images), 10)
        self.assertTrue(set(json.loads(result["selected_images_json"])).issubset(images))


if __name__ == "__main__":
    unittest.main()
