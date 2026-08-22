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
    def _result(self, prefix: str, count: int = 100):
        urls = [f"https://example.test/{prefix}/image-{i:03d}.jpg" for i in range(1, count + 1)]
        return {
            "images_json": json.dumps(urls),
            "selected_images_json": json.dumps(urls),
            "downloaded_image_files": [f"C:/tmp/{prefix}-{i:03d}.jpg" for i in range(1, count + 1)],
            "primary_image_url": urls[0],
        }

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
        result = cap_direct_result(self._result("first"), 10)
        images = json.loads(result["images_json"])
        selected = json.loads(result["selected_images_json"])
        self.assertEqual(len(images), 10)
        self.assertEqual(len(selected), 10)
        self.assertEqual(len(result["downloaded_image_files"]), 10)
        self.assertIn(result["primary_image_url"], images)

    def test_direct_result_caps_at_20_even_when_legacy_value_is_100(self):
        result = cap_direct_result(self._result("legacy"), 100)
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

    def test_limit_is_per_product_and_does_not_stop_next_product(self):
        # There is deliberately no shared/global consumed-image counter. Each
        # product gets the operator-selected cap, then the surrounding intake
        # loop can continue with the next product.
        first = cap_direct_result(self._result("product-a"), 10)
        second = cap_direct_result(self._result("product-b"), 10)
        self.assertEqual(len(json.loads(first["images_json"])), 10)
        self.assertEqual(len(json.loads(second["images_json"])), 10)
        self.assertNotEqual(json.loads(first["images_json"])[0], json.loads(second["images_json"])[0])


if __name__ == "__main__":
    unittest.main()
