from __future__ import annotations

import asyncio
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, patch

from app import phase49_3i16_resilient_acquisition as recovery


class Phase493I16ResilientAcquisitionTests(unittest.TestCase):
    def setUp(self):
        recovery._TRACE.clear()
        if hasattr(recovery.collect_candidate_images_resilient, "_original_collect"):
            delattr(recovery.collect_candidate_images_resilient, "_original_collect")

    def test_contract_records_ordered_fallback_methods(self):
        self.assertEqual(
            recovery.DISCOVERY_METHODS,
            ("locator-safe", "classic-links", "http-html-links"),
        )
        self.assertEqual(
            recovery.IMAGE_METHODS,
            (
                "locator-safe-fresh",
                "http-html-parse",
                "mature-classic-dom",
                "attached-chrome-locator",
                "listing-thumbnail",
            ),
        )
        source = Path(recovery.__file__).read_text(encoding="utf-8")
        self.assertNotIn("extract_direct_link(", source)
        self.assertNotIn("evaluate_all(", source)
        self.assertIn("All discovery methods failed", source)
        self.assertIn("All image acquisition methods failed", source)

    def test_discovery_falls_back_after_locator_error(self):
        expected = [
            {
                "source_code": "makerworld",
                "external_id": "400767",
                "source_url": "https://makerworld.com/en/models/400767-test",
                "source_title": "Test",
                "thumbnail_url": "",
                "discovered_from": "https://makerworld.com/en/search/models?keyword=cake+stand",
            }
        ]
        with patch.object(
            recovery,
            "discover_locator_safe",
            new=AsyncMock(side_effect=RuntimeError("Locator.evaluate_all SyntaxError")),
        ), patch.object(
            recovery,
            "discover_classic_links_fallback",
            new=AsyncMock(return_value=expected),
        ), patch.object(
            recovery,
            "discover_http_html_fallback",
            new=AsyncMock(side_effect=AssertionError("third method should not run")),
        ):
            result = asyncio.run(
                recovery.discover_preview_candidates_resilient(
                    "https://makerworld.com/en/search/models?keyword=cake+stand",
                    source_code="makerworld",
                    model_pattern=r"https://makerworld\.com/en/models/(?P<external_id>\d+)[^\s\"']*",
                    requested=10,
                    scroll_rounds=8,
                    headed=False,
                )
            )
        self.assertEqual(result, expected)
        trace = recovery.trace_for("https://makerworld.com/en/search/models?keyword=cake+stand")
        self.assertEqual([row["method"] for row in trace], ["locator-safe", "classic-links"])
        self.assertFalse(trace[0]["ok"])
        self.assertTrue(trace[1]["ok"])

    def test_image_acquisition_tries_next_method_until_local_stage_succeeds(self):
        success = {
            "browser": "attached",
            "http_status": 200,
            "final_url": "https://makerworld.com/en/models/400767-test",
            "image_urls": ["https://cdn.example/a.jpg", "https://cdn.example/b.jpg"],
            "downloaded_images": ["C:/tmp/a.jpg", "C:/tmp/b.jpg"],
        }
        with TemporaryDirectory() as tmp, patch.object(
            recovery,
            "collect_locator_safe_fresh",
            new=AsyncMock(side_effect=RuntimeError("HTTP 403")),
        ), patch.object(
            recovery,
            "collect_http_html_parse",
            new=AsyncMock(
                return_value={
                    "image_urls": ["https://cdn.example/a.jpg"],
                    "downloaded_images": [],
                    "final_url": "https://makerworld.com/en/models/400767-test",
                }
            ),
        ), patch.object(
            recovery,
            "collect_attached_locator",
            new=AsyncMock(return_value=success),
        ), patch.object(
            recovery,
            "collect_listing_thumbnail",
            new=AsyncMock(side_effect=AssertionError("listing fallback should not run")),
        ):
            result = asyncio.run(
                recovery.collect_candidate_images_resilient(
                    "https://makerworld.com/en/models/400767-test",
                    Path(tmp),
                    image_limit=10,
                    referer="https://makerworld.com/en/search/models?keyword=cake+stand",
                    headed=False,
                )
            )
        self.assertEqual(result["acquisition_method"], "attached-chrome-locator")
        self.assertEqual(len(result["downloaded_images"]), 2)
        trace = recovery.trace_for("https://makerworld.com/en/models/400767-test")
        self.assertEqual(
            [row["method"] for row in trace],
            ["locator-safe-fresh", "http-html-parse", "attached-chrome-locator"],
        )
        self.assertTrue(trace[-1]["ok"])

    def test_original_mature_collector_is_kept_as_bounded_fallback(self):
        mature = AsyncMock(
            return_value={
                "image_urls": ["https://cdn.example/a.jpg"],
                "downloaded_images": ["C:/tmp/a.jpg"],
                "final_url": "https://makerworld.com/en/models/400767-test",
            }
        )
        recovery.collect_candidate_images_resilient._original_collect = mature
        with TemporaryDirectory() as tmp, patch.object(
            recovery,
            "collect_locator_safe_fresh",
            new=AsyncMock(side_effect=RuntimeError("fresh failed")),
        ), patch.object(
            recovery,
            "collect_http_html_parse",
            new=AsyncMock(side_effect=RuntimeError("http failed")),
        ):
            result = asyncio.run(
                recovery.collect_candidate_images_resilient(
                    "https://makerworld.com/en/models/400767-test",
                    Path(tmp),
                    image_limit=10,
                    referer="https://makerworld.com/en/search/models?keyword=cake+stand",
                )
            )
        self.assertEqual(result["acquisition_method"], "mature-classic-dom")
        mature.assert_awaited_once()

    def test_trace_is_bounded_and_contains_operator_diagnostics(self):
        for index in range(40):
            recovery._trace("u", "images", f"m{index}", False, f"error-{index}")
        rows = recovery.trace_for("u")
        self.assertEqual(len(rows), 30)
        self.assertEqual(rows[-1]["detail"], "error-39")


if __name__ == "__main__":
    unittest.main()
