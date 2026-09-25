from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtWidgets import QApplication, QMessageBox

from app.db import Database, normalize_url
from app.phase49_3i38_crawl_ledger_stage_ai import (
    reconcile_product_delete_semantics,
    reject_and_purge_product,
    remember_ledger,
    terminal_identity_state,
)
from app.phase49_3i_discovery_review import (
    candidate_preview_cache_path,
    upsert_candidate,
)
from qt6.kernel import build_kernel
from qt6.pages import ProductsPage


class Phase50A2ZO4DeleteSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data = self.root / "data"
        self.old_data_root = os.environ.get("CATALOG_DATA_ROOT")
        os.environ["CATALOG_DATA_ROOT"] = str(self.data)
        self.db = Database(self.data / "catalog.sqlite3")
        self.db.upsert_source({
            "code": "makerworld",
            "name": "MakerWorld",
            "enabled": 1,
            "methods": ["browser", "http"],
            "listing_urls": [],
            "model_url_pattern": (
                r"https?://(?:www\.)?makerworld\.com/"
                r"(?:[a-z]{2}/)?models/(?P<external_id>\d+)[^?#]*"
            ),
            "requires_login": False,
            "reference_only": False,
        })
        self.kernel = build_kernel(self.db)

    def tearDown(self):
        self.db.close()
        if self.old_data_root is None:
            os.environ.pop("CATALOG_DATA_ROOT", None)
        else:
            os.environ["CATALOG_DATA_ROOT"] = self.old_data_root
        self.temp.cleanup()

    def _product(self, external_id: str, *, blocked: bool = False) -> int:
        source_url = f"https://makerworld.com/en/models/{external_id}-o4"
        local_dir = self.data / "collected" / "makerworld" / external_id
        images_dir = local_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        image_url = (
            "https://makerworld.bblmw.com/makerworld/model/"
            f"{external_id}/design/o4.webp"
        )
        image_file = images_dir / "01.webp"
        Image.new("RGB", (420, 320), "white").save(image_file, format="WEBP")
        (local_dir / "page_extract.json").write_text(
            json.dumps({"images": [{"url": image_url, "local_file": str(image_file)}]}),
            encoding="utf-8",
        )
        self.db.upsert_product({
            "source_code": "makerworld",
            "external_id": external_id,
            "source_url": source_url,
            "normalized_url": normalize_url(source_url),
            "source_title": f"Product {external_id}",
            "title_fa": "محصول تست",
            "description_fa": "توضیح تست",
            "local_dir": str(local_dir),
            "images_json": json.dumps([image_url]),
            "selected_images_json": json.dumps([image_url]),
            "primary_image_url": image_url,
            "final_price": 850000,
            "price_is_final": 1,
            "workflow_status": "review",
            "is_blocked": int(blocked),
            "source_state": "rejected" if blocked else "active",
        })
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code='makerworld' AND external_id=?",
            (external_id,),
        ).fetchone()
        return int(row["id"])
    def _ledger(self, product_id: int, status: str) -> int:
        row = self.db.product(product_id)
        source_url = str(row["source_url"])
        remember_ledger(
            self.db,
            str(row["source_code"]),
            str(row["external_id"]),
            source_url,
            status=status,
            discovered_from="o4-test",
            force=True,
        )
        return int(
            self.db.conn.execute(
                "SELECT id FROM discovered_urls WHERE source_code=? AND external_id=?",
                (row["source_code"], row["external_id"]),
            ).fetchone()["id"]
        )

    def test_active_product_authority_overrides_stale_rejected_ledger(self):
        product_id = self._product("520101")
        self._ledger(product_id, "rejected")
        row = self.db.product(product_id)
        self.assertEqual(
            terminal_identity_state(
                self.db, row["source_code"], row["external_id"], row["source_url"]
            ),
            "collected",
        )

    def test_rejected_product_authority_overrides_stale_failed_ledger(self):
        product_id = self._product("520102")
        self._ledger(product_id, "failed")
        self.db.update_product(product_id, {
            "is_blocked": 1,
            "source_state": "rejected",
            "workflow_status": "blocked",
        })
        row = self.db.product(product_id)
        self.assertEqual(
            terminal_identity_state(
                self.db, row["source_code"], row["external_id"], row["source_url"]
            ),
            "rejected",
        )

    def test_product_reject_purges_all_same_identity_cache_and_reports_result(self):
        product_id = self._product("520103")
        row = dict(self.db.product(product_id))
        self._ledger(product_id, "collected")
        source_root = self.data / "collected" / "makerworld"
        for suffix in (
            "_refresh_latest",
            "_refetch_20260925",
            "_bulk_refetch_123",
            "_deep_repair_20260925140000",
        ):
            folder = source_root / f"520103{suffix}" / "images"
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "stale.webp").write_bytes(b"stale")
        upsert_candidate(self.db, {
            "source_code": "makerworld",
            "external_id": "520103",
            "source_url": row["source_url"],
            "normalized_url": row["normalized_url"],
            "source_title": "Candidate",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "discovered_from": "o4-test",
        })
        preview = candidate_preview_cache_path("makerworld", "520103")
        preview.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (200, 150), "white").save(preview, format="JPEG")

        result = self.kernel.products.remove_many_detailed([product_id])
        rejected = dict(self.db.product(product_id))
        self.assertEqual(result["rejected"], 1)
        self.assertEqual(result["purged_dirs"], 5)
        self.assertEqual(result["candidate_rows_deleted"], 1)
        self.assertEqual(result["preview_files_deleted"], 1)
        self.assertEqual(result["cleanup_errors"], [])
        self.assertEqual(int(rejected["is_blocked"]), 1)
        self.assertEqual(rejected["source_state"], "rejected")
        self.assertEqual(rejected["local_dir"], "")
        self.assertFalse((source_root / "520103").exists())
        self.assertFalse(preview.exists())
        candidate_count = self.db.conn.execute(
            "SELECT count(*) FROM phase49_3i_discovery_candidates "
            "WHERE source_code='makerworld' AND external_id='520103'"
        ).fetchone()[0]
        self.assertEqual(candidate_count, 0)
        ledger = self.db.conn.execute(
            "SELECT status FROM discovered_urls WHERE source_code='makerworld' AND external_id='520103'"
        ).fetchone()
        self.assertEqual(ledger["status"], "rejected")
        thumb = Path(str(rejected["rejected_thumbnail_path"] or ""))
        self.assertTrue(thumb.is_file())
    def test_restore_rejected_tombstone_stays_collected_and_requires_deep_repair(self):
        product_id = self._product("520104")
        self._ledger(product_id, "collected")
        self.assertEqual(self.kernel.products.remove_many([product_id]), 1)

        result = self.kernel.products.restore_many_detailed([product_id])
        row = dict(self.db.product(product_id))
        ledger = self.db.conn.execute(
            "SELECT status FROM discovered_urls WHERE source_code='makerworld' AND external_id='520104'"
        ).fetchone()
        self.assertEqual(result["restored"], 1)
        self.assertEqual(result["recovery_required"], [product_id])
        self.assertEqual(int(row["is_blocked"]), 0)
        self.assertEqual(row["source_state"], "active")
        self.assertEqual(row["workflow_status"], "review")
        self.assertEqual(row["images_json"], "[]")
        self.assertEqual(ledger["status"], "collected")
        self.assertFalse(
            self.db.add_discovered(
                "makerworld",
                "520104",
                row["source_url"],
                "must-not-reenter-add-products",
            )
        )
        self.assertEqual(
            terminal_identity_state(
                self.db, row["source_code"], row["external_id"], row["source_url"]
            ),
            "collected",
        )

    def test_reconcile_repairs_ledger_mismatches_and_only_rejected_cache(self):
        active_id = self._product("520105")
        rejected_id = self._product("520106")
        self._ledger(active_id, "rejected")
        self._ledger(rejected_id, "failed")
        rejected = dict(self.db.product(rejected_id))
        self.db.update_product(rejected_id, {
            "is_blocked": 1,
            "source_state": "rejected",
            "workflow_status": "blocked",
            "local_dir": "",
            "images_json": "[]",
            "selected_images_json": "[]",
            "primary_image_url": "",
        })
        stale = self.data / "collected" / "makerworld" / "520106_refresh_latest"
        (stale / "images").mkdir(parents=True, exist_ok=True)
        (stale / "images" / "stale.webp").write_bytes(b"stale")
        upsert_candidate(self.db, {
            "source_code": "makerworld",
            "external_id": "520106",
            "source_url": rejected["source_url"],
            "normalized_url": rejected["normalized_url"],
            "source_title": "Rejected Candidate",
            "thumbnail_url": "https://example.com/rejected.jpg",
            "discovered_from": "o4-test",
        })
        preview = candidate_preview_cache_path("makerworld", "520106")
        preview.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (120, 120), "white").save(preview, format="JPEG")

        plan = reconcile_product_delete_semantics(
            self.db, data_path=self.data, apply=False
        )
        mismatch_products = {
            item["product_id"] for item in plan["ledger_mismatches"]
        }
        self.assertIn(active_id, mismatch_products)
        self.assertIn(rejected_id, mismatch_products)
        self.assertTrue(stale.is_dir())
        self.assertTrue(preview.is_file())

        applied = reconcile_product_delete_semantics(
            self.db, data_path=self.data, apply=True
        )
        self.assertEqual(applied["ledger_updated"], 2)
        self.assertEqual(applied["candidate_rows_deleted"], 1)
        self.assertEqual(applied["preview_files_deleted"], 1)
        self.assertEqual(applied["local_dirs_deleted"], 2)
        self.assertEqual(applied["cleanup_errors"], [])
        statuses = {
            r["external_id"]: r["status"]
            for r in self.db.conn.execute(
                "SELECT external_id,status FROM discovered_urls "
                "WHERE external_id IN ('520105','520106')"
            )
        }
        self.assertEqual(statuses["520105"], "collected")
        self.assertEqual(statuses["520106"], "rejected")
        self.assertTrue(Path(str(self.db.product(active_id)["local_dir"])).is_dir())
        self.assertFalse(stale.exists())
        self.assertFalse(preview.exists())
    def test_reconcile_never_deletes_outside_current_catalog_data_root(self):
        product_id = self._product("520107")
        self._ledger(product_id, "failed")
        outside = self.root / "outside-keep"
        outside.mkdir(parents=True, exist_ok=True)
        sentinel = outside / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        self.db.update_product(product_id, {
            "is_blocked": 1,
            "source_state": "rejected",
            "workflow_status": "blocked",
            "local_dir": str(outside),
            "images_json": "[]",
            "selected_images_json": "[]",
        })
        result = reconcile_product_delete_semantics(
            self.db, data_path=self.data, apply=True
        )
        self.assertTrue(sentinel.is_file())
        self.assertEqual(result["ledger_updated"], 1)
        self.assertEqual(len(result["cleanup_errors"]), 1)

    def test_products_page_restore_message_explains_recovery_contract(self):
        product_id = self._product("520108")
        self._ledger(product_id, "collected")
        self.kernel.products.remove_many([product_id])
        page = ProductsPage(self.db, lambda _product_id: None, kernel=self.kernel)
        try:
            with patch.object(page, "_selected_product_ids", return_value=[product_id]),                  patch.object(QMessageBox, "information") as info:
                page._restore_selected()
            self.assertEqual(info.call_count, 1)
            message = str(info.call_args.args[2])
            self.assertIn("بازیابی عمیق از صفر", message)
            self.assertIn("Add Products", message)
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
