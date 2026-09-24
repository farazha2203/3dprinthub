import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from PIL import Image

from app.db import Database
from app.phase49_3i_discovery_review import upsert_candidate
from app.phase49_3i38_crawl_ledger_stage_ai import terminal_identity_state
from qt6 import acquisition_runtime
from qt6.acquisition_runtime import run_single_async
from qt6.kernel import build_kernel
from qt6.models import ProductTableModel


class Phase50A2ZO2DIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.old_data_root = os.environ.get("CATALOG_DATA_ROOT")
        os.environ["CATALOG_DATA_ROOT"] = str(self.root / "data")
        self.addCleanup(self._restore_env)
        self.db = Database(self.root / "catalog.sqlite3")
        self.addCleanup(self.db.close)
        self.db.upsert_source(
            {
                "code": "makerworld",
                "name": "MakerWorld",
                "enabled": 1,
                "methods": ["browser", "http"],
                "listing_urls": [
                    "https://makerworld.com/en/search/models?keyword={query}"
                ],
                "model_url_pattern": (
                    r"https?://(?:www\.)?makerworld\.com/"
                    r"(?:[a-z]{2}/)?models/(?P<external_id>\d+)[^?#]*"
                ),
                "requires_login": False,
                "reference_only": False,
            }
        )
        self.kernel = build_kernel(self.db)

    def _restore_env(self):
        if self.old_data_root is None:
            os.environ.pop("CATALOG_DATA_ROOT", None)
        else:
            os.environ["CATALOG_DATA_ROOT"] = self.old_data_root

    @staticmethod
    def url(external_id):
        return (
            f"https://makerworld.com/en/models/"
            f"{external_id}-identity-test?from=search"
        )

    def add_product(self, external_id, *, title="Existing Product"):
        url = self.url(external_id)
        self.db.upsert_product(
            {
                "source_code": "makerworld",
                "external_id": str(external_id),
                "source_url": url,
                "source_title": title,
                "source_description": "Existing source description",
                "images_json": "[]",
                "selected_images_json": "[]",
            }
        )
        return int(
            self.db.conn.execute(
                "SELECT id FROM products "
                "WHERE source_code='makerworld' AND external_id=?",
                (str(external_id),),
            ).fetchone()["id"]
        )

    def add_candidate(self, external_id, *, title, local_image):
        url = self.url(external_id)
        self.assertTrue(
            self.db.add_discovered(
                "makerworld",
                str(external_id),
                url,
                "o2d-test",
            )
        )
        upsert_candidate(
            self.db,
            {
                "source_code": "makerworld",
                "external_id": str(external_id),
                "source_url": url,
                "source_title": title,
                "thumbnail_url": (
                    f"https://example.com/{external_id}.jpg"
                    if title
                    else ""
                ),
                "discovered_from": "o2d-test",
            },
        )
        if local_image:
            image_dir = (
                Path(self.db.path).resolve().parent
                / "collected"
                / "makerworld"
                / str(external_id)
                / "images"
            )
            image_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (320, 240), "white").save(
                image_dir / "01.jpg",
                format="JPEG",
            )

    def test_existing_product_identity_cannot_be_discovered_again(self):
        product_id = self.add_product("700001")
        self.assertFalse(
            self.db.add_discovered(
                "makerworld",
                "700001",
                self.url("700001"),
                "repeat-search",
            )
        )
        self.assertEqual(
            self.db.conn.execute(
                "SELECT count(*) FROM discovered_urls "
                "WHERE source_code='makerworld' AND external_id='700001'"
            ).fetchone()[0],
            0,
        )
        self.assertEqual(
            terminal_identity_state(
                self.db,
                "makerworld",
                "700001",
                self.url("700001"),
            ),
            "collected",
        )
        self.assertEqual(product_id, self.add_product("700001"))

    def test_existing_product_is_hidden_from_pending_and_add_products_queue(self):
        self.assertTrue(
            self.db.add_discovered(
                "makerworld",
                "700002",
                self.url("700002"),
                "before-product",
            )
        )
        self.add_product("700002")
        self.assertEqual(
            [
                row["external_id"]
                for row in self.db.pending_urls(
                    "makerworld",
                    50,
                    include_failed=True,
                )
            ],
            [],
        )
        self.assertEqual(
            self.kernel.acquisition.queue_count("", "all"),
            0,
        )
        self.assertEqual(
            self.kernel.acquisition.queue_page(
                "",
                "all",
                limit=50,
                offset=0,
            ),
            [],
        )
        # The ledger remains as identity memory, so discovery cannot re-add it.
        self.assertEqual(
            self.db.conn.execute(
                "SELECT count(*) FROM discovered_urls "
                "WHERE source_code='makerworld' AND external_id='700002'"
            ).fetchone()[0],
            1,
        )

    def test_existing_product_run_single_skips_network_without_force_recover(self):
        product_id = self.add_product("700003")
        with patch(
            "qt6.acquisition_runtime._collect_one",
            new=AsyncMock(side_effect=AssertionError("network should not run")),
        ):
            result = asyncio.run(
                run_single_async(
                    self.db,
                    source_code="makerworld",
                    product_url=self.url("700003"),
                    image_limit=5,
                    collection_method="rich",
                    force_recover=False,
                )
            )
        self.assertEqual(result["product_id"], product_id)
        self.assertTrue(result["already_collected"])

    def test_unconsumed_complete_incomplete_partition_uses_candidate_title_and_local_preview(self):
        self.add_candidate(
            "700010",
            title="Ready Candidate",
            local_image=True,
        )
        self.add_candidate(
            "700011",
            title="",
            local_image=False,
        )
        # A mapped Product must disappear from the Add Products inventory.
        self.assertTrue(
            self.db.add_discovered(
                "makerworld",
                "700012",
                self.url("700012"),
                "before-product",
            )
        )
        self.add_product("700012")

        all_count = self.kernel.acquisition.queue_count("", "all")
        complete_count = self.kernel.acquisition.queue_count("", "complete")
        incomplete_count = self.kernel.acquisition.queue_count("", "incomplete")

        self.assertEqual(all_count, 2)
        self.assertEqual(complete_count, 1)
        self.assertEqual(incomplete_count, 1)
        self.assertEqual(complete_count + incomplete_count, all_count)

        complete = self.kernel.acquisition.queue_page(
            "",
            "complete",
            limit=10,
            offset=0,
        )
        incomplete = self.kernel.acquisition.queue_page(
            "",
            "incomplete",
            limit=10,
            offset=0,
        )
        self.assertEqual(
            [row["external_id"] for row in complete],
            ["700010"],
        )
        self.assertEqual(
            [row["external_id"] for row in incomplete],
            ["700011"],
        )
        reasons = self.kernel.acquisition.queue_completeness_reasons(
            incomplete[0]
        )
        self.assertIn("عنوان Candidate ندارد", reasons)
        self.assertIn("Preview/عکس محلی ندارد", reasons)

    def test_queue_summary_excludes_consumed_product_identities(self):
        self.add_candidate(
            "700020",
            title="Unconsumed Candidate",
            local_image=True,
        )
        self.assertTrue(
            self.db.add_discovered(
                "makerworld",
                "700021",
                self.url("700021"),
                "before-product",
            )
        )
        self.add_product("700021")
        counts = self.kernel.acquisition.queue_counts("")
        self.assertEqual(sum(counts.values()), 1)
        self.assertEqual(counts.get("new"), 1)

    def test_products_table_displays_canonical_source_identity_code(self):
        self.add_product("700030", title="Visible Identity")
        model = ProductTableModel(self.db)
        self.assertEqual(model.rowCount(), 1)
        source_text = model.data(model.index(0, 4))
        self.assertIn("makerworld", source_text)
        self.assertIn("makerworld:700030", source_text)

    def test_batch_pending_listing_excludes_existing_product_ledger(self):
        listing = "https://makerworld.com/en/search/models?keyword=o2d"
        self.assertTrue(
            self.db.add_discovered(
                "makerworld",
                "700040",
                self.url("700040"),
                listing,
            )
        )
        self.add_product("700040")
        rows = acquisition_runtime._pending_for_listing(
            self.db,
            "makerworld",
            listing,
            20,
            include_failed=True,
        )
        self.assertEqual(rows, [])

    def test_preview_existing_product_skips_candidate_and_thumbnail_work(self):
        self.add_product("700041")
        listing = "https://makerworld.com/en/search/models?keyword=o2d-preview"
        candidate = {
            "source_code": "makerworld",
            "external_id": "700041",
            "source_url": self.url("700041"),
            "source_title": "Existing Preview Product",
            "thumbnail_url": "https://example.com/700041.jpg",
        }
        source_cfg = dict(self.db.source("makerworld"))
        with patch(
            "qt6.acquisition_runtime._browser_robots_gate",
            new=AsyncMock(return_value=0.0),
        ), patch(
            "qt6.acquisition_runtime.discover_preview_candidates_safe",
            new=AsyncMock(return_value=[candidate]),
        ), patch(
            "qt6.acquisition_runtime._cache_candidate_thumbnail",
            side_effect=AssertionError("existing Product thumbnail must not recrawl"),
        ):
            result = asyncio.run(
                acquisition_runtime._preview_listing_candidates(
                    self.db,
                    source_cfg,
                    listing,
                    10,
                )
            )
        self.assertEqual(result["previewed"], 0)
        self.assertEqual(result["new"], 0)
        self.assertEqual(result["duplicates"], 1)
        self.assertEqual(result["thumbs"], 0)


if __name__ == "__main__":
    unittest.main()
