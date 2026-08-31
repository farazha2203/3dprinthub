from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app.db import Database
from app.phase49_3i43_modern_acquisition_intelligence import (
    ensure_schema as ensure_modern_schema,
)
from app.phase49_3i45_incremental_discovery_intelligence import (
    ensure_schema as ensure_incremental_schema,
)
from qt6 import acquisition_runtime


class _FakeModernClient:
    def __init__(self, db, source_code: str = "") -> None:
        self.db = db
        self.source_code = source_code

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class Phase493I42CAcquisitionRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temporary.name) / "catalog.sqlite3")
        self.db.upsert_source(
            {
                "code": "makerworld",
                "name": "MakerWorld",
                "enabled": 1,
                "methods": ["browser", "http", "sitemap"],
                "listing_urls": [],
                "model_url_pattern": (
                    r"https?://(?:www\\.)?makerworld\\.com/"
                    r"(?:[a-z]{2}/)?models/(?P<external_id>\\d+)"
                    r"[^\\s\\\"'<>]*"
                ),
                "requires_login": False,
                "reference_only": False,
            }
        )
        ensure_modern_schema(self.db)
        ensure_incremental_schema(self.db)

    def tearDown(self):
        self.db.close()
        self.temporary.cleanup()

    def _source(self) -> dict:
        return dict(self.db.source("makerworld"))

    @staticmethod
    def _model(number: int) -> tuple[str, str]:
        return (
            str(number),
            f"https://makerworld.com/en/models/{number}-test-model",
        )

    def test_classic_mode_skips_modern_http_and_advances_same_search_link(self):
        listing = "https://makerworld.com/en/search/models?keyword=cake+stand"
        calls: list[int] = []

        async def fake_classic(_url, *, model_pattern, scroll_rounds, headed):
            calls.append(int(scroll_rounds))
            if len(calls) == 1:
                links = [self._model(1001), self._model(1002)]
            else:
                links = [
                    self._model(1001),
                    self._model(1002),
                    self._model(1003),
                    self._model(1004),
                ]
            return {"links": links}

        with (
            patch.object(
                acquisition_runtime,
                "discover_classic",
                side_effect=fake_classic,
            ),
            patch.object(
                acquisition_runtime,
                "discover_conditional_http",
                new=AsyncMock(
                    side_effect=AssertionError(
                        "classic strategy must not call modern discovery"
                    )
                ),
            ),
        ):
            first = asyncio.run(
                acquisition_runtime._discover_listing(
                    self.db,
                    self._source(),
                    listing,
                    2,
                    strategy="classic",
                )
            )
            first_pending = self.db.pending_urls("makerworld", 10)
            self.assertEqual(
                [str(row["external_id"]) for row in first_pending],
                ["1001", "1002"],
            )
            self.assertEqual(first["new"], 2)

            for row in first_pending:
                self.db.mark_url(int(row["id"]), "collected")

            second = asyncio.run(
                acquisition_runtime._discover_listing(
                    self.db,
                    self._source(),
                    listing,
                    2,
                    strategy="classic",
                )
            )
            second_pending = self.db.pending_urls("makerworld", 10)

        self.assertEqual(calls, [8, 16])
        self.assertEqual(
            [str(row["external_id"]) for row in second_pending],
            ["1003", "1004"],
        )
        self.assertEqual(second["new"], 2)

    def test_hybrid_mode_prefers_modern_candidates_without_browser_when_enough(self):
        listing = "https://makerworld.com/en/search/models?keyword=lamp"
        candidates = [
            {
                "source_code": "makerworld",
                "external_id": "2001",
                "source_url": self._model(2001)[1],
                "discovered_from": listing,
            },
            {
                "source_code": "makerworld",
                "external_id": "2002",
                "source_url": self._model(2002)[1],
                "discovered_from": listing,
            },
        ]

        with (
            patch.object(
                acquisition_runtime,
                "ModernHttpClient",
                _FakeModernClient,
            ),
            patch.object(
                acquisition_runtime,
                "discover_conditional_http",
                new=AsyncMock(return_value=candidates),
            ) as modern,
            patch.object(
                acquisition_runtime,
                "discover_classic",
                new=AsyncMock(
                    side_effect=AssertionError(
                        "browser fallback should not run when modern discovery is enough"
                    )
                ),
            ),
        ):
            result = asyncio.run(
                acquisition_runtime._discover_listing(
                    self.db,
                    self._source(),
                    listing,
                    2,
                    strategy="hybrid",
                )
            )

        self.assertEqual(result["new"], 2)
        self.assertEqual(modern.await_count, 1)
        pending = self.db.pending_urls("makerworld", 10)
        self.assertEqual(
            [str(row["external_id"]) for row in pending],
            ["2001", "2002"],
        )

    def test_rich_product_collection_persists_source_facts_and_caps_product_images(self):
        local_dir = Path(self.temporary.name) / "rich-product"
        local_dir.mkdir(parents=True, exist_ok=True)

        urls = [
            f"https://cdn.example.com/product-{index}.jpg"
            for index in range(1, 7)
        ]
        snapshot = {
            "source": "makerworld",
            "json_ld_count": 1,
            "embedded_json_count": 2,
            "specs": {"layer_height": "0.20 mm"},
        }
        rich = {
            "source_code": "makerworld",
            "external_id": "3001",
            "source_url": self._model(3001)[1],
            "normalized_url": self._model(3001)[1],
            "source_title": "Organic Desk Lamp",
            "source_short_description": "Decorative lamp.",
            "source_description": "Decorative organic table lamp.",
            "author_name": "Example Designer",
            "license_name": "Standard Digital File License",
            "license_url": "https://example.com/license",
            "source_category": "Home decor",
            "source_categories_json": json.dumps(
                ["Home decor", "Lighting"],
                ensure_ascii=False,
            ),
            "tags_json": json.dumps(
                ["lamp", "desk", "decor"],
                ensure_ascii=False,
            ),
            "images_json": json.dumps(urls, ensure_ascii=False),
            "selected_images_json": json.dumps(urls, ensure_ascii=False),
            "primary_image_url": urls[0],
            "file_links_json": "[]",
            "selected_file_links_json": "[]",
            "source_specs_json": json.dumps(
                {"layer_height": "0.20 mm"},
                ensure_ascii=False,
            ),
            "source_snapshot_json": json.dumps(
                snapshot,
                ensure_ascii=False,
            ),
            "source_price": 0,
            "source_currency": "",
            "estimated_weight_grams": 82.5,
            "estimated_print_minutes": 155,
            "source_rating": 4.9,
            "source_rating_count": 23,
            "source_like_count": 180,
            "source_download_count": 77,
            "source_view_count": 1400,
            "source_published_at": "2026-08-01",
            "source_updated_at": "2026-08-29",
            "local_dir": str(local_dir),
            "downloaded_image_files": [
                str(local_dir / f"{index:03d}.jpg")
                for index in range(1, 7)
            ],
        }

        with patch.object(
            acquisition_runtime,
            "extract_direct_link",
            new=AsyncMock(return_value=rich),
        ):
            result = asyncio.run(
                acquisition_runtime._collect_one(
                    self.db,
                    self._source(),
                    external_id="3001",
                    url=self._model(3001)[1],
                    image_limit=3,
                    local_dir=local_dir,
                )
            )

        row = dict(self.db.product(int(result["product_id"])))
        self.assertEqual(row["source_title"], "Organic Desk Lamp")
        self.assertEqual(row["author_name"], "Example Designer")
        self.assertEqual(row["source_category"], "Home decor")
        self.assertEqual(
            json.loads(row["tags_json"]),
            ["lamp", "desk", "decor"],
        )
        self.assertEqual(
            json.loads(row["source_specs_json"]),
            {"layer_height": "0.20 mm"},
        )
        self.assertEqual(json.loads(row["source_snapshot_json"]), snapshot)
        self.assertEqual(json.loads(row["images_json"]), urls[:3])
        self.assertEqual(
            json.loads(row["selected_images_json"]),
            urls[:3],
        )
        self.assertEqual(row["primary_image_url"], urls[0])
        self.assertEqual(result["images_found"], 3)
        self.assertEqual(result["images_saved"], 3)
        self.assertEqual(
            row["acquisition_method"],
            "qt42c-rich-page-extractor",
        )

    def test_invalid_discovery_strategy_is_rejected_before_crawl(self):
        with self.assertRaisesRegex(ValueError, "strategy"):
            asyncio.run(
                acquisition_runtime._discover_listing(
                    self.db,
                    self._source(),
                    "https://makerworld.com/en/search/models?keyword=test",
                    2,
                    strategy="unknown",
                )
            )


if __name__ == "__main__":
    unittest.main()
