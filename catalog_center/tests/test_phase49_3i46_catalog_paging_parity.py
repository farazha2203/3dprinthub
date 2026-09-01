from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.db import Database
from app.epic49_desktop_schema import ensure_epic49_desktop_schema
from qt6.kernel import build_kernel
from qt6.models import ProductTableModel
from qt6.pages import OperationsPage
from qt6.product_explorer import ProductGalleryModel


class Phase493I46CatalogPagingParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp.name) / "catalog.sqlite3")
        ensure_epic49_desktop_schema(self.db)
        self.db.upsert_source(
            {
                "code": "makerworld",
                "name": "MakerWorld",
                "enabled": 1,
                "methods": ["browser", "http", "sitemap"],
                "listing_urls": [
                    "https://makerworld.com/en/search/models?keyword={query}"
                ],
                "model_url_pattern": (
                    r"https?://(?:www\\.)?makerworld\\.com/"
                    r"(?:[a-z]{2}/)?models/(?P<external_id>\\d+)"
                ),
                "requires_login": False,
                "reference_only": False,
            }
        )
        for number in range(1, 74):
            self.db.upsert_product(
                {
                    "source_code": "makerworld",
                    "external_id": f"PAGING-{number:03d}",
                    "source_url": f"https://example.com/models/paging-{number:03d}",
                    "source_title": f"Paged Product {number:03d}",
                    "title_fa": f"محصول صفحه {number:03d}",
                    "workflow_status": "review",
                }
            )
        for number in range(1, 126):
            self.db.add_discovered(
                "makerworld",
                f"QUEUE-{number:03d}",
                f"https://makerworld.com/en/models/{100000 + number}-queue",
                "paging-test",
            )
        self.kernel = build_kernel(self.db)

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_product_page_is_bounded_and_omits_heavy_payload_columns(self):
        self.assertEqual(self.db.product_count(), 73)
        page = [dict(row) for row in self.db.product_page(limit=20, offset=0)]
        self.assertEqual(len(page), 20)
        self.assertNotIn("source_snapshot_json", page[0])
        self.assertNotIn("content_pack_json", page[0])
        self.assertIn("selected_images_json", page[0])

    def test_table_loads_20_then_fetches_next_20(self):
        model = ProductTableModel(self.db)
        self.assertEqual(model.total_count, 73)
        self.assertEqual(model.rowCount(), 20)
        self.assertTrue(model.canFetchMore())
        model.fetchMore()
        self.assertEqual(model.rowCount(), 40)
        while model.canFetchMore():
            model.fetchMore()
        self.assertEqual(model.rowCount(), 73)
        self.assertFalse(model.canFetchMore())

    def test_gallery_loads_50_then_fetches_remaining_page(self):
        model = ProductGalleryModel(
            self.kernel.products,
            self.kernel.images,
        )
        self.assertEqual(model.total_count, 73)
        self.assertEqual(model.rowCount(), 50)
        self.assertTrue(model.canFetchMore())
        model.fetchMore()
        self.assertEqual(model.rowCount(), 73)
        self.assertFalse(model.canFetchMore())

    def test_crawl_inventory_uses_count_and_100_row_pages(self):
        self.assertEqual(self.kernel.acquisition.queue_count("", "all"), 125)
        first = self.kernel.acquisition.queue_page("", "all", limit=100, offset=0)
        second = self.kernel.acquisition.queue_page("", "all", limit=100, offset=100)
        self.assertEqual(len(first), 100)
        self.assertEqual(len(second), 25)
        first_ids = {int(row["id"]) for row in first}
        second_ids = {int(row["id"]) for row in second}
        self.assertFalse(first_ids & second_ids)

    def test_operations_page_initially_renders_only_first_100_queue_rows(self):
        page = OperationsPage(self.db, kernel=self.kernel)
        try:
            page.refresh()
            self.assertEqual(page._queue_total, 125)
            self.assertEqual(page._queue_offset, 100)
            self.assertEqual(page.queue_table.rowCount(), 100)
            page._populate_queue(reset=False)
            self.assertEqual(page._queue_offset, 125)
            self.assertEqual(page.queue_table.rowCount(), 125)
            self.assertIn("125", page.queue_loaded_label.text())
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
