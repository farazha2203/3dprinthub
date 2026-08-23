from __future__ import annotations

import asyncio
import unittest

from app import phase49_3i15_bulk_discovery_images as bulk
from app.phase49_3i15_staging_guard import install_guard


class Phase493I15StagingGuardTests(unittest.TestCase):
    def test_guard_clears_remote_urls_when_no_image_was_staged(self):
        original = bulk.collect_candidate_images

        async def fake_collect(*_args, **_kwargs):
            return {
                "http_status": 200,
                "final_url": "https://example.test/product",
                "image_urls": ["https://img.example.test/1.jpg"],
                "downloaded_images": [],
            }

        try:
            bulk.collect_candidate_images = fake_collect
            if hasattr(bulk, "_phase49_3i15_local_staging_guard_installed"):
                delattr(bulk, "_phase49_3i15_local_staging_guard_installed")
            install_guard()
            result = asyncio.run(
                bulk.collect_candidate_images(
                    "https://example.test/product",
                    __import__("pathlib").Path("."),
                    image_limit=10,
                )
            )
            self.assertEqual(result["image_urls"], [])
            self.assertEqual(result["downloaded_images"], [])
        finally:
            bulk.collect_candidate_images = original
            if hasattr(bulk, "_phase49_3i15_local_staging_guard_installed"):
                delattr(bulk, "_phase49_3i15_local_staging_guard_installed")

    def test_guard_preserves_urls_when_local_image_exists(self):
        original = bulk.collect_candidate_images

        async def fake_collect(*_args, **_kwargs):
            return {
                "http_status": 200,
                "final_url": "https://example.test/product",
                "image_urls": ["https://img.example.test/1.jpg"],
                "downloaded_images": ["C:/staged/01.jpg"],
            }

        try:
            bulk.collect_candidate_images = fake_collect
            if hasattr(bulk, "_phase49_3i15_local_staging_guard_installed"):
                delattr(bulk, "_phase49_3i15_local_staging_guard_installed")
            install_guard()
            result = asyncio.run(
                bulk.collect_candidate_images(
                    "https://example.test/product",
                    __import__("pathlib").Path("."),
                    image_limit=10,
                )
            )
            self.assertEqual(result["image_urls"], ["https://img.example.test/1.jpg"])
            self.assertEqual(result["downloaded_images"], ["C:/staged/01.jpg"])
        finally:
            bulk.collect_candidate_images = original
            if hasattr(bulk, "_phase49_3i15_local_staging_guard_installed"):
                delattr(bulk, "_phase49_3i15_local_staging_guard_installed")


if __name__ == "__main__":
    unittest.main()
