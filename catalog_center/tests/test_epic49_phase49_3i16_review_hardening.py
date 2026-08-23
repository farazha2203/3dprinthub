from __future__ import annotations

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app import phase49_3i16_resilient_acquisition as recovery
from app import phase49_3i16_review_hardening as hardening


class _FakeDb:
    pass


class Phase493I16ReviewHardeningTests(unittest.TestCase):
    def setUp(self):
        recovery._TRACE.clear()
        hardening._ACTIVE_DB = None

    def test_discovery_order_avoids_leak_prone_classic_fallback(self):
        source = __import__(
            "pathlib"
        ).Path(hardening.__file__).read_text(encoding="utf-8")
        self.assertNotIn("discover_classic(", source)
        self.assertNotIn("evaluate_all(", source)
        self.assertIn("cached-candidate-db", source)
        self.assertIn("attached-chrome-listing", source)

    def test_cached_candidates_are_used_after_live_methods_fail(self):
        listing = "https://makerworld.com/en/search/models?keyword=cake+stand"
        row = {
            "source_code": "makerworld",
            "external_id": "400767",
            "source_url": "https://makerworld.com/en/models/400767-test",
            "source_title": "3 Tier Cake Stand",
            "thumbnail_url": "https://cdn.example/thumb.jpg",
            "discovered_from": listing,
        }
        hardening._ACTIVE_DB = _FakeDb()
        with patch.object(
            hardening,
            "candidate_rows",
            return_value=[row],
        ), patch.object(
            recovery,
            "discover_locator_safe",
            new=AsyncMock(side_effect=RuntimeError("locator failed")),
        ), patch.object(
            recovery,
            "discover_http_html_fallback",
            new=AsyncMock(side_effect=RuntimeError("http failed")),
        ), patch.object(
            hardening,
            "discover_attached_locator_safe",
            new=AsyncMock(side_effect=RuntimeError("cdp unavailable")),
        ):
            result = asyncio.run(
                hardening.discover_preview_candidates_hardened(
                    listing,
                    source_code="makerworld",
                    model_pattern=r"https://makerworld\.com/en/models/(?P<external_id>\d+)[^\s\"']*",
                    requested=10,
                    scroll_rounds=8,
                    headed=False,
                )
            )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["external_id"], "400767")
        trace = recovery.trace_for(listing)
        self.assertEqual(trace[-1]["method"], "cached-candidate-db")
        self.assertTrue(trace[-1]["ok"])

    def test_app_start_registers_db_before_worker_starts(self):
        calls = []

        class FakeApp:
            def start_bulk_page_discovery(self, *args, **kwargs):
                calls.append((self.db, args, kwargs))
                return "started"

        hardening.install(FakeApp)
        app = FakeApp()
        app.db = _FakeDb()
        result = app.start_bulk_page_discovery(1, test=True)
        self.assertEqual(result, "started")
        self.assertIs(hardening._ACTIVE_DB, app.db)
        self.assertEqual(len(calls), 1)
        self.assertEqual(
            recovery.DISCOVERY_METHODS,
            (
                "locator-safe",
                "http-html-links",
                "attached-chrome-listing",
                "cached-candidate-db",
            ),
        )


if __name__ == "__main__":
    unittest.main()
