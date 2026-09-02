from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QApplication, QListWidget

from app.db import Database, normalize_url
from app.phase49_3i_discovery_review import (
    candidate_by_identity,
    candidate_preview_cache_path,
    set_candidate_status,
    upsert_candidate,
)
from qt6 import acquisition_runtime
from qt6.kernel import build_kernel
from qt6.pages import OperationsPage
from qt6.product_wizard import ProductWizardPage


class Phase493I52CCrawlReviewRecoveryTests(unittest.TestCase):
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
                "methods": ["browser", "http", "sitemap"],
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

    @staticmethod
    def _candidate(external_id: str, listing: str, *, title: str = "") -> dict:
        url = f"https://makerworld.com/en/models/{external_id}-preview-test"
        return {
            "source_code": "makerworld",
            "external_id": external_id,
            "source_url": url,
            "normalized_url": normalize_url(url),
            "source_title": title or f"Preview Product {external_id}",
            "thumbnail_url": f"https://cdn.example.com/{external_id}.jpg",
            "discovered_from": listing,
        }

    def _create_product(
        self,
        external_id: str,
        *,
        title_fa: str = "عنوان اپراتور",
        status: str = "review",
    ) -> int:
        url = f"https://makerworld.com/en/models/{external_id}-preview-test"
        self.db.upsert_product(
            {
                "source_code": "makerworld",
                "external_id": external_id,
                "source_url": url,
                "source_title": "Old Source Title",
                "source_description": "Old source description",
                "title_fa": title_fa,
                "short_description_fa": "توضیح اپراتور",
                "description_fa": "متن اپراتور که باید حفظ شود",
                "workflow_status": status,
                "final_price": 910000,
                "price_is_final": 1,
                "approved_for_sale": 1,
                "publish_as_product": 1,
                "images_json": "[]",
                "selected_images_json": "[]",
            }
        )
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("makerworld", external_id),
        ).fetchone()
        return int(row["id"])

    def test_persistent_inventory_reuses_legacy_preview_title_thumbnail_and_easy_multiselect(self):
        listing = "https://makerworld.com/en/search/models?keyword=lamp"
        candidate = self._candidate("520001", listing, title="Modern Lamp Preview")
        upsert_candidate(self.db, candidate)
        self.db.add_discovered(
            "makerworld",
            candidate["external_id"],
            candidate["source_url"],
            listing,
        )
        preview = candidate_preview_cache_path("makerworld", "520001")
        Image.new("RGB", (480, 320), "white").save(preview, format="JPEG")

        page = OperationsPage(self.db, kernel=self.kernel)
        try:
            page._populate_queue(reset=True)
            self.assertEqual(
                page.queue_gallery.selectionMode(),
                QAbstractItemView.SelectionMode.MultiSelection,
            )
            self.assertEqual(
                page.queue_table.selectionMode(),
                QAbstractItemView.SelectionMode.MultiSelection,
            )
            self.assertEqual(page.queue_gallery.count(), 1)
            card = page.queue_gallery.item(0)
            self.assertIn("Modern Lamp Preview", card.text())
            self.assertIn("Preview: 1 عکس", card.text())
            self.assertFalse(card.icon().isNull())

            page.queue_select_all_btn.click()
            self.assertEqual(len(page._selected_queue_ids()), 1)
            self.assertIn("1 انتخاب‌شده", page.queue_selected_label.text())
            page.queue_clear_selection_btn.click()
            self.assertEqual(page._selected_queue_ids(), [])
        finally:
            page.close()

    def test_current_search_gallery_is_visual_scoped_and_click_toggle_multiselect(self):
        listing = "https://makerworld.com/en/search/models?keyword=japandi"
        for external_id in ("520010", "520011"):
            candidate = self._candidate(external_id, listing)
            upsert_candidate(self.db, candidate)
            self.db.add_discovered(
                "makerworld",
                external_id,
                candidate["source_url"],
                listing,
            )
            preview = candidate_preview_cache_path("makerworld", external_id)
            Image.new("RGB", (420, 300), "white").save(preview, format="JPEG")

        other = self._candidate(
            "520099",
            "https://makerworld.com/en/search/models?keyword=unrelated",
        )
        upsert_candidate(self.db, other)

        page = OperationsPage(self.db, kernel=self.kernel)
        try:
            page._active_source_code = "makerworld"
            page._active_listing_url = listing
            page._active_run_started_at = ""
            page._refresh_live_discovery()
            self.assertEqual(
                page.live_results.viewMode(),
                QListWidget.ViewMode.IconMode,
            )
            self.assertEqual(
                page.live_results.selectionMode(),
                QAbstractItemView.SelectionMode.MultiSelection,
            )
            self.assertEqual(page.live_results.count(), 2)
            text = "\n".join(
                page.live_results.item(index).text()
                for index in range(page.live_results.count())
            )
            self.assertIn("Preview: 1 عکس", text)
            self.assertNotIn("520099", text)
            page.live_select_all_btn.click()
            self.assertEqual(len(page.live_results.selectedItems()), 2)
            self.assertIn("2 انتخاب‌شده", page.live_selected_label.text())
        finally:
            page.close()

    def test_selected_collected_live_product_shows_real_image_strip_and_count(self):
        listing = "https://makerworld.com/en/search/models?keyword=review-images"
        external_id = "520015"
        product_id = self._create_product(external_id)
        local_dir = self.root / "collected" / "makerworld" / external_id
        images_dir = local_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        for name in ("one.jpg", "two.jpg"):
            Image.new("RGB", (420, 300), "white").save(
                images_dir / name,
                format="JPEG",
            )
        urls = ["local://one.jpg", "local://two.jpg"]
        self.db.update_product(
            product_id,
            {
                "local_dir": str(local_dir),
                "images_json": json.dumps(urls),
                "selected_images_json": json.dumps(urls),
                "primary_image_url": urls[0],
            },
        )
        candidate = self._candidate(external_id, listing)
        candidate_id = upsert_candidate(self.db, candidate)
        self.db.add_discovered(
            "makerworld",
            external_id,
            candidate["source_url"],
            listing,
        )
        queue = self.db.conn.execute(
            "SELECT id FROM discovered_urls WHERE source_code=? AND external_id=?",
            ("makerworld", external_id),
        ).fetchone()
        self.db.mark_url(int(queue["id"]), "collected")
        set_candidate_status(
            self.db,
            candidate_id,
            "imported",
            product_id=product_id,
        )

        page = OperationsPage(self.db, kernel=self.kernel)
        try:
            page._active_source_code = "makerworld"
            page._active_listing_url = listing
            page._active_run_started_at = ""
            page._refresh_live_discovery()
            self.assertEqual(page.live_results.count(), 1)
            page.live_results.item(0).setSelected(True)
            self.app.processEvents()
            self.assertEqual(page.live_detail_images.count(), 2)
            self.assertIn("2 عکس دارد", page.live_detail_meta.text())
            self.assertIn(
                "2 فایل محلی قابل نمایش",
                page.live_detail_meta.text(),
            )
            self.assertTrue(page.live_detail_open_btn.isEnabled())
        finally:
            page.close()

    def test_receive_action_labels_are_compact_but_keep_full_tooltips(self):
        page = OperationsPage(self.db, kernel=self.kernel)
        try:
            self.assertEqual(page.start_btn.text(), "شروع دریافت")
            self.assertEqual(page.queue_btn.text(), "موجودی Crawl")
            self.assertEqual(page.default_url_btn.text(), "لینک پیش‌فرض")
            self.assertEqual(page.direct_btn.text(), "دریافت Product")
            self.assertEqual(page.live_add_btn.text(), "افزودن انتخابی")
            self.assertEqual(page.live_reject_btn.text(), "حذف انتخابی")
            for button in (
                page.start_btn,
                page.queue_btn,
                page.default_url_btn,
                page.direct_btn,
                page.live_add_btn,
                page.live_reject_btn,
            ):
                self.assertTrue(button.toolTip().strip())
        finally:
            page.close()

    def test_batch_preview_appears_before_full_fetch_and_reports_per_image_progress(self):
        listing = "https://makerworld.com/en/search/models?keyword=hooks"
        candidates = [
            self._candidate("520020", listing),
            self._candidate("520021", listing),
        ]
        progress = []

        async def fake_collect(_db, _source_cfg, **kwargs):
            callback = kwargs["image_progress"]
            for index in range(1, 6):
                callback(index, 5, f"https://cdn.example.com/{index}.jpg")
            external_id = str(kwargs["external_id"])
            return {
                "product_id": 9000 + int(external_id[-1]),
                "source_title": f"Collected {external_id}",
                "images_found": 5,
                "images_saved": 5,
                "files_saved": 0,
            }

        with patch(
            "qt6.acquisition_runtime._browser_robots_gate",
            new=AsyncMock(return_value=0),
        ), patch(
            "qt6.acquisition_runtime.discover_preview_candidates_safe",
            new=AsyncMock(return_value=candidates),
        ), patch(
            "qt6.acquisition_runtime._cache_candidate_thumbnail",
            return_value="",
        ), patch(
            "qt6.acquisition_runtime._discover_listing",
            new=AsyncMock(),
        ) as deeper, patch(
            "qt6.acquisition_runtime._collect_one",
            new=AsyncMock(side_effect=fake_collect),
        ):
            result = acquisition_runtime.run_batch(
                self.db,
                source_code="makerworld",
                listing_url=listing,
                requested=2,
                image_limit=5,
                progress=lambda value, message: progress.append((value, message)),
            )

        self.assertEqual(result["collected"], 2)
        deeper.assert_not_awaited()
        self.assertTrue(
            any("پیش‌نمایش" in message for _value, message in progress)
        )
        self.assertTrue(
            any("عکس 3/5" in message for _value, message in progress)
        )
        candidate = candidate_by_identity(self.db, "makerworld", "520020")
        self.assertEqual(candidate["status"], "imported")

    def test_new_search_clears_previous_live_cards_before_worker_starts(self):
        page = OperationsPage(self.db, kernel=self.kernel)
        captured = []
        try:
            page.live_results.addItem("stale item")
            page.url.setText(
                "https://makerworld.com/en/search/models?keyword=new-search"
            )
            page.requested.setValue(5)
            page.image_limit.setValue(5)
            page.pool.start = lambda worker: captured.append(worker)
            page._start()
            self.assertEqual(page.live_results.count(), 0)
            self.assertEqual(
                page._active_listing_url,
                "https://makerworld.com/en/search/models?keyword=new-search",
            )
            self.assertEqual(len(captured), 1)
        finally:
            page.close()

    def test_existing_collected_selection_is_preserved_and_routes_to_products(self):
        external_id = "520030"
        product_id = self._create_product(external_id, status="uploaded")
        url = f"https://makerworld.com/en/models/{external_id}-preview-test"
        self.db.add_discovered(
            "makerworld",
            external_id,
            url,
            "phase49-3i52c-test",
        )
        queue = self.db.conn.execute(
            "SELECT id FROM discovered_urls WHERE source_code=? AND external_id=?",
            ("makerworld", external_id),
        ).fetchone()
        queue_id = int(queue["id"])
        self.db.mark_url(queue_id, "collected")

        routes = []
        page = OperationsPage(
            self.db,
            kernel=self.kernel,
            navigate=routes.append,
        )
        captured = []
        try:
            page.pool.start = lambda worker: captured.append(worker)
            page._collect_queue_ids([queue_id])
            self.assertEqual(len(captured), 1)
            result = captured[0].fn(lambda _value, _message: None)
            self.assertEqual(result["already_collected_count"], 1)
            self.assertIn(product_id, result["product_ids"])
            page._done(result)
            self.app.processEvents()
            self.assertIn("products", routes)
        finally:
            page.close()

    def test_safe_source_recovery_updates_source_data_and_images_without_clobbering_operator_fields(self):
        product_id = self._create_product("520040")
        old = dict(self.db.product(product_id))
        self.assertEqual(old["final_price"], 910000)

        async_result = {
            "source_code": "makerworld",
            "external_id": "520040",
            "source_url": "https://makerworld.com/en/models/520040-preview-test",
            "source_title": "Fresh Source Title",
            "source_short_description": "Fresh short",
            "source_description": "Fresh source description",
            "source_category": "Decor",
            "source_categories_json": json.dumps(["Decor"]),
            "tags_json": json.dumps(["lamp", "decor"]),
            "images_json": json.dumps([
                "https://cdn.example.com/new-1.jpg",
                "https://cdn.example.com/new-2.jpg",
            ]),
            "selected_images_json": json.dumps([
                "https://cdn.example.com/new-1.jpg",
                "https://cdn.example.com/new-2.jpg",
            ]),
            "primary_image_url": "https://cdn.example.com/new-1.jpg",
            "file_links_json": "[]",
            "selected_file_links_json": "[]",
            "source_specs_json": json.dumps({"height": "20 cm"}),
            "source_snapshot_json": "{}",
            "source_price": None,
            "source_currency": "",
            "estimated_weight_grams": 120,
            "estimated_print_minutes": 150,
            "source_rating": 4.8,
            "source_rating_count": 10,
            "source_like_count": 20,
            "source_download_count": 30,
            "source_view_count": 40,
            "source_published_at": "",
            "source_updated_at": "",
            "downloaded_image_files": ["a.jpg", "b.jpg"],
        }

        with patch(
            "qt6.acquisition_runtime._browser_robots_gate",
            new=AsyncMock(return_value=0),
        ), patch(
            "qt6.acquisition_runtime.extract_direct_link",
            new=AsyncMock(return_value=async_result),
        ):
            result = self.kernel.acquisition.recover_product_images(
                product_id,
                image_limit=5,
            )

        row = dict(self.db.product(product_id))
        self.assertTrue(result["changed"])
        self.assertEqual(row["source_title"], "Fresh Source Title")
        self.assertEqual(row["estimated_weight_grams"], 120)
        self.assertEqual(row["estimated_print_minutes"], 150)
        self.assertEqual(row["title_fa"], "عنوان اپراتور")
        self.assertEqual(row["description_fa"], "متن اپراتور که باید حفظ شود")
        self.assertEqual(row["final_price"], 910000)
        self.assertEqual(row["price_is_final"], 1)
        self.assertEqual(row["approved_for_sale"], 1)
        self.assertEqual(row["publish_as_product"], 1)
        self.assertIn("new-1.jpg", row["images_json"])

    def test_stage3_exposes_explicit_safe_data_and_more_images_action(self):
        product_id = self._create_product("520050")
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            labels = {
                button.text()
                for button in page.findChildren(type(page.product_source_btn))
            }
            self.assertIn(
                "دریافت داده و عکس بیشتر از لینک محصول",
                labels,
            )
            self.assertNotIn(
                "دریافت مجدد تصاویر از لینک محصول",
                labels,
            )
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
