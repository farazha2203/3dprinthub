import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from PySide6.QtWidgets import QApplication, QMessageBox

from app.db import Database
from app.phase49_3i_discovery_review import (
    CANDIDATE_TABLE,
    candidate_preview_cache_path,
    upsert_candidate,
)
from qt6.kernel import build_kernel
from qt6.pages import OperationsPage


class Phase50A2ZO4RFullReacquireTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.old_data_root = os.environ.get("CATALOG_DATA_ROOT")
        os.environ["CATALOG_DATA_ROOT"] = str(self.root)
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
    def url(external_id: str) -> str:
        return f"https://makerworld.com/en/models/{external_id}-o4r-test"

    def add_identity(self, external_id: str) -> dict:
        url = self.url(external_id)
        self.assertTrue(
            self.db.add_discovered(
                "makerworld",
                external_id,
                url,
                "o4r-test-listing",
            )
        )
        row = self.db.conn.execute(
            "SELECT id FROM discovered_urls WHERE source_code=? AND external_id=?",
            ("makerworld", external_id),
        ).fetchone()
        self.assertIsNotNone(row)
        queue_id = int(row["id"])
        self.db.conn.execute(
            "UPDATE discovered_urls SET status='failed', attempts=3, last_error='HTTP 403' WHERE id=?",
            (queue_id,),
        )
        self.db.conn.commit()
        upsert_candidate(
            self.db,
            {
                "source_code": "makerworld",
                "external_id": external_id,
                "source_url": url,
                "source_title": f"Candidate {external_id}",
                "thumbnail_url": f"https://example.com/{external_id}.jpg",
                "discovered_from": "o4r-test-listing",
            },
        )
        preview = candidate_preview_cache_path("makerworld", external_id)
        Image.new("RGB", (64, 64), "white").save(preview, format="JPEG")

        source_root = self.root / "collected" / "makerworld"
        folders = []
        for suffix in (
            "",
            "_refresh_latest",
            "_refetch_20260925",
            "_bulk_refetch_20260925",
            "_deep_repair_20260925",
        ):
            folder = source_root / f"{external_id}{suffix}" / "images"
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "stale.txt").write_text("stale", encoding="utf-8")
            folders.append(folder.parent)
        return {
            "queue_id": queue_id,
            "url": url,
            "preview": preview,
            "folders": folders,
        }

    def add_product(self, external_id: str) -> int:
        self.db.upsert_product(
            {
                "source_code": "makerworld",
                "external_id": external_id,
                "source_url": self.url(external_id),
                "source_title": f"Product {external_id}",
                "source_description": "Existing Product authority",
                "images_json": "[]",
                "selected_images_json": "[]",
            }
        )
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("makerworld", external_id),
        ).fetchone()
        self.assertIsNotNone(row)
        return int(row["id"])

    def test_full_reacquire_quarantines_only_exact_identity_and_keeps_source_row(self):
        target = self.add_identity("910001")
        unrelated = (
            self.root
            / "collected"
            / "makerworld"
            / "910099"
            / "images"
            / "keep.txt"
        )
        unrelated.parent.mkdir(parents=True, exist_ok=True)
        unrelated.write_text("keep", encoding="utf-8")

        result = self.kernel.acquisition.prepare_queue_full_reacquire(
            [target["queue_id"]]
        )

        self.assertEqual(result["prepared"], 1)
        self.assertEqual(result["product_backed"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["files_quarantined"], 6)
        self.assertFalse(target["preview"].exists())
        self.assertTrue(unrelated.is_file())
        for folder in target["folders"]:
            self.assertFalse(folder.exists())

        row = self.db.conn.execute(
            "SELECT status,attempts,last_error,url FROM discovered_urls WHERE id=?",
            (target["queue_id"],),
        ).fetchone()
        self.assertEqual(row["status"], "new")
        self.assertEqual(int(row["attempts"]), 0)
        self.assertEqual(row["last_error"], "")
        self.assertEqual(row["url"], target["url"])
        candidate = self.db.conn.execute(
            f"SELECT status FROM {CANDIDATE_TABLE} WHERE source_code=? AND external_id=?",
            ("makerworld", "910001"),
        ).fetchone()
        self.assertEqual(candidate["status"], "review")

        rollback = Path(result["rollback_roots"][0])
        self.assertTrue(rollback.is_dir())
        self.assertTrue((rollback / "preview" / target["preview"].name).is_file())
        quarantined_names = {
            item.name for item in (rollback / "old_local").iterdir()
        }
        self.assertEqual(
            quarantined_names,
            {
                "910001",
                "910001_refresh_latest",
                "910001_refetch_20260925",
                "910001_bulk_refetch_20260925",
                "910001_deep_repair_20260925",
            },
        )

    def test_product_backed_identity_is_not_deleted_and_is_hidden_from_add_products(self):
        target = self.add_identity("910002")
        product_id = self.add_product("910002")

        result = self.kernel.acquisition.prepare_queue_full_reacquire(
            [target["queue_id"]]
        )

        self.assertEqual(result["prepared"], 0)
        self.assertEqual(result["product_backed"], 1)
        self.assertEqual(result["product_rows"][0]["product_id"], product_id)
        self.assertTrue(target["preview"].is_file())
        for folder in target["folders"]:
            self.assertTrue(folder.is_dir())

        row = self.db.conn.execute(
            "SELECT status,last_error FROM discovered_urls WHERE id=?",
            (target["queue_id"],),
        ).fetchone()
        self.assertEqual(row["status"], "collected")
        self.assertEqual(row["last_error"], "")
        candidate = self.db.conn.execute(
            f"SELECT status FROM {CANDIDATE_TABLE} WHERE source_code=? AND external_id=?",
            ("makerworld", "910002"),
        ).fetchone()
        self.assertEqual(candidate["status"], "imported")

        queue_ids = {
            int(item["id"])
            for item in self.kernel.acquisition.queue_page(
                "",
                "all",
                limit=100,
                offset=0,
            )
        }
        self.assertNotIn(target["queue_id"], queue_ids)
        live = self.kernel.acquisition.current_review_items(
            "makerworld",
            "o4r-test-listing",
            limit=100,
        )
        self.assertFalse(
            any(str(item.get("external_id") or "") == "910002" for item in live)
        )

    def test_operations_ui_exposes_distinct_full_reacquire_action(self):
        app = QApplication.instance() or QApplication([])
        page = OperationsPage(self.db, kernel=self.kernel)
        try:
            self.assertIn("بازیابی کامل از صفر", page.queue_full_reacquire_btn.text())
            tooltip = page.queue_full_reacquire_btn.toolTip()
            self.assertIn("Print Profile", tooltip)
            self.assertIn("Screenshot", tooltip)
            self.assertNotEqual(
                page.queue_full_reacquire_btn.text(),
                page.queue_recover_btn.text(),
            )
        finally:
            page.close()
            if QApplication.instance() is app:
                app.processEvents()

    def test_full_reacquire_worker_requests_full_source_profiles_and_screenshot(self):
        target = self.add_identity("910003")
        app = QApplication.instance() or QApplication([])
        page = OperationsPage(self.db, kernel=self.kernel)
        captured = []

        def fake_run_single(**kwargs):
            self.assertTrue(kwargs["adaptive_fallback"])
            self.assertTrue(kwargs["download_images"])
            self.assertTrue(kwargs["download_files"])
            self.assertFalse(kwargs["force_recover"])
            self.db.upsert_product(
                {
                    "source_code": "makerworld",
                    "external_id": "910003",
                    "source_url": target["url"],
                    "source_title": "Recovered Product",
                    "source_description": "Recovered full source data",
                    "images_json": json.dumps(
                        ["https://example.com/910003-01.webp"]
                    ),
                    "selected_images_json": json.dumps(
                        ["https://example.com/910003-01.webp"]
                    ),
                    "source_print_profiles_json": json.dumps(
                        [
                            {
                                "name": "0.20mm PLA",
                                "weight_grams": 20,
                                "print_minutes": 75,
                                "materials": ["PLA"],
                            }
                        ]
                    ),
                }
            )
            row = self.db.conn.execute(
                "SELECT id FROM products WHERE source_code=? AND external_id=?",
                ("makerworld", "910003"),
            ).fetchone()
            return {
                "product_id": int(row["id"]),
                "selected_method": "network_capture",
            }

        try:
            page._selected_queue_ids = lambda: [target["queue_id"]]
            page.pool.start = lambda worker: captured.append(worker) or worker
            with patch.object(
                QMessageBox,
                "question",
                return_value=QMessageBox.StandardButton.Yes,
            ), patch.object(
                self.kernel.acquisition,
                "run_single",
                side_effect=fake_run_single,
            ) as run_single, patch.object(
                self.kernel.acquisition,
                "refresh_source_profiles",
                return_value={
                    "product_id": 1,
                    "profile_count": 1,
                    "profiles": [{"name": "0.20mm PLA"}],
                },
            ) as refresh_profiles, patch.object(
                self.kernel.acquisition,
                "capture_product_source_screenshot",
                return_value=str(self.root / "source-page.png"),
            ) as screenshot, patch.object(
                self.kernel.commerce,
                "import_source_profiles",
                return_value={
                    "source_profile_count": 1,
                    "imported_profile_count": 3,
                },
            ) as import_profiles:
                page._full_reacquire_selected_queue()
                self.assertEqual(len(captured), 1)
                result = captured[0].fn(progress=lambda *_args: None)

            self.assertEqual(result["recovered"], 1)
            self.assertEqual(result["failed"], 0)
            self.assertEqual(result["screenshots"], 1)
            self.assertEqual(result["profiles_refreshed"], 1)
            self.assertEqual(result["profiles_imported"], 3)
            self.assertEqual(result["preferred_method"], "network_capture")
            run_single.assert_called_once()
            refresh_profiles.assert_called_once()
            screenshot.assert_called_once()
            import_profiles.assert_called_once()
            row = self.db.conn.execute(
                "SELECT status FROM discovered_urls WHERE id=?",
                (target["queue_id"],),
            ).fetchone()
            self.assertEqual(row["status"], "collected")
        finally:
            page.close()
            if QApplication.instance() is app:
                app.processEvents()

    def test_full_reacquire_worker_stops_after_first_acquisition_failure(self):
        first = self.add_identity("910004")
        second = self.add_identity("910005")
        app = QApplication.instance() or QApplication([])
        page = OperationsPage(self.db, kernel=self.kernel)
        captured = []
        try:
            page._selected_queue_ids = lambda: [
                first["queue_id"],
                second["queue_id"],
            ]
            page.pool.start = lambda worker: captured.append(worker) or worker
            with patch.object(
                QMessageBox,
                "question",
                return_value=QMessageBox.StandardButton.Yes,
            ), patch.object(
                self.kernel.acquisition,
                "run_single",
                side_effect=RuntimeError("provider access blocked"),
            ) as run_single:
                page._full_reacquire_selected_queue()
                self.assertEqual(len(captured), 1)
                result = captured[0].fn(progress=lambda *_args: None)

            self.assertEqual(result["recovered"], 0)
            self.assertEqual(result["failed"], 1)
            self.assertEqual(result["unattempted"], 1)
            run_single.assert_called_once()
            first_row = self.db.conn.execute(
                "SELECT status FROM discovered_urls WHERE id=?",
                (first["queue_id"],),
            ).fetchone()
            second_row = self.db.conn.execute(
                "SELECT status FROM discovered_urls WHERE id=?",
                (second["queue_id"],),
            ).fetchone()
            self.assertEqual(first_row["status"], "failed")
            self.assertEqual(second_row["status"], "failed")
            self.assertTrue(second["preview"].is_file())
            for folder in second["folders"]:
                self.assertTrue(folder.is_dir())
        finally:
            page.close()
            if QApplication.instance() is app:
                app.processEvents()


if __name__ == "__main__":
    unittest.main()
