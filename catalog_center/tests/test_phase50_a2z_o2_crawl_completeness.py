import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.db import Database
from qt6.kernel import build_kernel
from qt6.pages import OperationsPage


class Phase50A2ZO2CrawlCompletenessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.old_data_root = os.environ.get("CATALOG_DATA_ROOT")
        os.environ["CATALOG_DATA_ROOT"] = str(self.root / "data")
        self.db = Database(self.root / "catalog.sqlite3")
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

    def tearDown(self):
        self.db.close()
        if self.old_data_root is None:
            os.environ.pop("CATALOG_DATA_ROOT", None)
        else:
            os.environ["CATALOG_DATA_ROOT"] = self.old_data_root
        self.temp.cleanup()

    def add_discovered(self, external_id: str) -> None:
        url = f"https://makerworld.com/en/models/{external_id}-o2-test"
        self.assertTrue(
            self.db.add_discovered(
                "makerworld",
                external_id,
                url,
                "phase50-o2-test",
            )
        )

    def add_product(
        self,
        external_id: str,
        *,
        title: str,
        description: str,
        with_local_image: bool,
    ) -> int:
        url = f"https://makerworld.com/en/models/{external_id}-o2-test"
        self.db.upsert_product(
            {
                "source_code": "makerworld",
                "external_id": external_id,
                "source_url": url,
                "source_title": title,
                "source_description": description,
                "title_fa": "",
                "short_description_fa": "",
                "description_fa": "",
                "images_json": "[]",
                "selected_images_json": "[]",
            }
        )
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("makerworld", external_id),
        ).fetchone()
        product_id = int(row["id"])
        if with_local_image:
            image_dir = (
                Path(self.db.path).resolve().parent
                / "collected"
                / "makerworld"
                / external_id
                / "images"
            )
            image_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (320, 240), "white").save(
                image_dir / "01.jpg",
                format="JPEG",
            )
        return product_id

    def seed_contract_rows(self):
        self.add_discovered("610001")
        complete_id = self.add_product(
            "610001",
            title="Complete source title",
            description="Complete source description",
            with_local_image=True,
        )

        self.add_discovered("610002")
        incomplete_id = self.add_product(
            "610002",
            title="",
            description="",
            with_local_image=False,
        )

        self.add_discovered("610003")
        return complete_id, incomplete_id

    def test_shared_contract_marks_complete_and_reports_exact_missing_reasons(self):
        self.seed_contract_rows()
        rows = {
            row["external_id"]: row
            for row in self.kernel.acquisition.queue_page(
                "",
                "all",
                limit=20,
                offset=0,
            )
        }

        complete = rows["610001"]
        self.assertTrue(self.kernel.acquisition.queue_is_complete(complete))
        self.assertEqual(
            self.kernel.acquisition.queue_completeness_reasons(complete),
            [],
        )

        incomplete = rows["610002"]
        reasons = self.kernel.acquisition.queue_completeness_reasons(incomplete)
        self.assertFalse(self.kernel.acquisition.queue_is_complete(incomplete))
        self.assertIn("عنوان ندارد", reasons)
        self.assertIn("توضیح ندارد", reasons)
        self.assertIn("فایل عکس محلی قابل نمایش ندارد", reasons)

        unmapped = rows["610003"]
        reasons = self.kernel.acquisition.queue_completeness_reasons(unmapped)
        self.assertFalse(self.kernel.acquisition.queue_is_complete(unmapped))
        self.assertIn("Product mapping ندارد / هنوز دریافت نشده", reasons)

    def test_complete_and_incomplete_filters_cover_inventory_with_filtered_paging(self):
        self.seed_contract_rows()
        all_count = self.kernel.acquisition.queue_count("", "all")
        complete_count = self.kernel.acquisition.queue_count("", "complete")
        incomplete_count = self.kernel.acquisition.queue_count("", "incomplete")

        self.assertEqual(all_count, 3)
        self.assertEqual(complete_count, 1)
        self.assertEqual(incomplete_count, 2)
        self.assertEqual(complete_count + incomplete_count, all_count)

        complete = self.kernel.acquisition.queue_page(
            "",
            "complete",
            limit=10,
            offset=0,
        )
        self.assertEqual([row["external_id"] for row in complete], ["610001"])

        first = self.kernel.acquisition.queue_page(
            "",
            "incomplete",
            limit=1,
            offset=0,
        )
        second = self.kernel.acquisition.queue_page(
            "",
            "incomplete",
            limit=1,
            offset=1,
        )
        self.assertEqual([row["external_id"] for row in first], ["610003"])
        self.assertEqual([row["external_id"] for row in second], ["610002"])

    def test_operations_page_filters_and_card_status_share_core_truth(self):
        self.seed_contract_rows()
        page = OperationsPage(self.db, kernel=self.kernel)
        try:
            complete_index = page.queue_filter.findData("complete")
            incomplete_index = page.queue_filter.findData("incomplete")
            self.assertGreaterEqual(complete_index, 0)
            self.assertGreaterEqual(incomplete_index, 0)

            page.queue_filter.setCurrentIndex(complete_index)
            page._populate_queue(reset=True)
            self.assertEqual(page.queue_gallery.count(), 1)
            complete_text = page.queue_gallery.item(0).text()
            self.assertIn("Complete source title", complete_text)
            self.assertIn("✅ کامل:", complete_text)

            page.queue_filter.setCurrentIndex(incomplete_index)
            page._populate_queue(reset=True)
            self.assertEqual(page.queue_gallery.count(), 2)
            texts = [
                page.queue_gallery.item(index).text()
                for index in range(page.queue_gallery.count())
            ]
            self.assertTrue(all("⚠ ناقص:" in value for value in texts))
            self.assertTrue(
                any("Product mapping ندارد" in value for value in texts)
            )
            self.assertTrue(
                any("عنوان ندارد" in value for value in texts)
            )
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
