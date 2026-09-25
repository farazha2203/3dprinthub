import os
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from PySide6.QtWidgets import QApplication

from app.db import Database
from app.phase49_3i_discovery_review import (
    CANDIDATE_TABLE,
    candidate_preview_cache_path,
    upsert_candidate,
)
from qt6.kernel import build_kernel
from qt6.pages import OperationsPage


class Phase50A2ZO2HHardDeleteTests(unittest.TestCase):
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
        return f"https://makerworld.com/en/models/{external_id}-o2h-test"
    def add_crawl_identity(self, external_id: str) -> dict:
        url = self.url(external_id)
        self.assertTrue(
            self.db.add_discovered(
                "makerworld",
                external_id,
                url,
                "o2h-test",
            )
        )
        upsert_candidate(
            self.db,
            {
                "source_code": "makerworld",
                "external_id": external_id,
                "source_url": url,
                "source_title": f"Candidate {external_id}",
                "thumbnail_url": f"https://example.com/{external_id}.jpg",
                "discovered_from": "o2h-test",
            },
        )
        queue_row = self.db.conn.execute(
            "SELECT * FROM discovered_urls WHERE source_code=? AND external_id=?",
            ("makerworld", external_id),
        ).fetchone()
        self.assertIsNotNone(queue_row)

        preview = candidate_preview_cache_path("makerworld", external_id)
        Image.new("RGB", (64, 64), "white").save(preview, format="JPEG")
        collected = self.root / "collected" / "makerworld"
        primary = collected / external_id / "images"
        primary.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (64, 64), "white").save(
            primary / "01.jpg",
            format="JPEG",
        )
        refetch = collected / f"{external_id}_refetch_20260925" / "images"
        refetch.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (64, 64), "white").save(
            refetch / "02.jpg",
            format="JPEG",
        )
        return {
            "queue_id": int(queue_row["id"]),
            "url": url,
            "preview": preview,
            "primary_root": primary.parent,
            "refetch_root": refetch.parent,
        }

    def add_product(self, external_id: str) -> int:
        self.db.upsert_product(
            {
                "source_code": "makerworld",
                "external_id": external_id,
                "source_url": self.url(external_id),
                "source_title": f"Product {external_id}",
                "source_description": "Product authority",
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

    def test_hard_delete_removes_only_unconsumed_identity_data(self):
        target = self.add_crawl_identity("810001")
        unrelated = (
            self.root
            / "collected"
            / "makerworld"
            / "KEEP-810099"
            / "images"
            / "keep.txt"
        )
        unrelated.parent.mkdir(parents=True, exist_ok=True)
        unrelated.write_text("keep", encoding="utf-8")

        result = self.kernel.acquisition.hard_delete_queue_items(
            [target["queue_id"]]
        )
        self.assertEqual(result["deleted"], 1)
        self.assertEqual(result["blocked"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertFalse(target["preview"].exists())
        self.assertFalse(target["primary_root"].exists())
        self.assertFalse(target["refetch_root"].exists())
        self.assertTrue(unrelated.is_file())
        self.assertEqual(
            self.db.conn.execute(
                "SELECT COUNT(*) FROM discovered_urls WHERE id=?",
                (target["queue_id"],),
            ).fetchone()[0],
            0,
        )
        self.assertEqual(
            self.db.conn.execute(
                f"SELECT COUNT(*) FROM {CANDIDATE_TABLE} "
                "WHERE source_code='makerworld' AND external_id='810001'"
            ).fetchone()[0],
            0,
        )

    def test_product_backed_identity_fails_closed(self):
        target = self.add_crawl_identity("810002")
        product_id = self.add_product("810002")
        result = self.kernel.acquisition.hard_delete_queue_items(
            [target["queue_id"]]
        )
        self.assertEqual(result["deleted"], 0)
        self.assertEqual(result["blocked"], 1)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(
            result["blocked_rows"][0]["product_id"],
            product_id,
        )
        self.assertTrue(target["preview"].is_file())
        self.assertTrue(target["primary_root"].is_dir())
        self.assertTrue(target["refetch_root"].is_dir())
        self.assertEqual(
            self.db.conn.execute(
                "SELECT COUNT(*) FROM discovered_urls WHERE id=?",
                (target["queue_id"],),
            ).fetchone()[0],
            1,
        )
        self.assertEqual(
            self.db.conn.execute(
                f"SELECT COUNT(*) FROM {CANDIDATE_TABLE} "
                "WHERE source_code='makerworld' AND external_id='810002'"
            ).fetchone()[0],
            1,
        )

    def test_normalized_url_product_authority_also_fails_closed(self):
        target = self.add_crawl_identity("810004")
        self.db.upsert_product(
            {
                "source_code": "makerworld",
                "external_id": "DIFFERENT-810004",
                "source_url": target["url"],
                "source_title": "Same URL Product Authority",
                "source_description": "Normalized URL must protect this Crawl identity.",
                "images_json": "[]",
                "selected_images_json": "[]",
            }
        )
        product = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND normalized_url=?",
            ("makerworld", self.db.conn.execute(
                "SELECT normalized_url FROM discovered_urls WHERE id=?",
                (target["queue_id"],),
            ).fetchone()["normalized_url"]),
        ).fetchone()
        self.assertIsNotNone(product)

        result = self.kernel.acquisition.hard_delete_queue_items(
            [target["queue_id"]]
        )
        self.assertEqual(result["deleted"], 0)
        self.assertEqual(result["blocked"], 1)
        self.assertTrue(target["preview"].is_file())
        self.assertTrue(target["primary_root"].is_dir())

    def test_reject_remains_reversible_and_non_destructive(self):
        target = self.add_crawl_identity("810003")
        self.assertEqual(
            self.kernel.acquisition.reject_queue_items([target["queue_id"]]),
            1,
        )
        row = self.db.conn.execute(
            "SELECT status FROM discovered_urls WHERE id=?",
            (target["queue_id"],),
        ).fetchone()
        self.assertEqual(row["status"], "rejected")
        self.assertTrue(target["preview"].is_file())
        self.assertTrue(target["primary_root"].is_dir())
        self.assertEqual(
            self.db.conn.execute(
                f"SELECT COUNT(*) FROM {CANDIDATE_TABLE} "
                "WHERE source_code='makerworld' AND external_id='810003'"
            ).fetchone()[0],
            1,
        )
        self.assertEqual(
            self.kernel.acquisition.restore_queue_items([target["queue_id"]]),
            1,
        )
        row = self.db.conn.execute(
            "SELECT status FROM discovered_urls WHERE id=?",
            (target["queue_id"],),
        ).fetchone()
        self.assertEqual(row["status"], "new")
    def test_operations_ui_separates_reject_from_hard_delete(self):
        app = QApplication.instance() or QApplication([])
        page = OperationsPage(self.db, kernel=self.kernel)
        try:
            self.assertEqual(page.queue_reject_btn.text(), "رد")
            self.assertIn("حذف واقعی", page.queue_delete_btn.text())
            self.assertEqual(page.live_reject_btn.text(), "رد انتخابی")
            self.assertIn("حذف واقعی", page.live_delete_btn.text())
            self.assertNotEqual(
                page.queue_reject_btn.toolTip(),
                page.queue_delete_btn.toolTip(),
            )
        finally:
            page.close()
            if QApplication.instance() is app:
                app.processEvents()


if __name__ == "__main__":
    unittest.main()
