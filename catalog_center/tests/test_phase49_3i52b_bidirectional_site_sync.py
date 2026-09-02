from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.db import Database
from app.epic49_site_sync import apply_server_product_to_local
from app.phase49_3i49_site_publish import guard_site_revisions
from qt6.kernel import build_kernel
from qt6.pages import ProductsPage


def server_product(
    *,
    product_id=501,
    revision=3,
    title="عنوان سایت",
    active=True,
    desktop_product_id=0,
):
    return {
        "id": product_id,
        "title": title,
        "title_en": "Site Product",
        "short_description": "توضیح کوتاه سایت",
        "description": "توضیح کامل سایت",
        "category_slug": "home-decor",
        "source_name": "",
        "source_code": "",
        "source_external_id": "",
        "source_url": "",
        "is_active": active,
        "main_image": "/media/site-product.webp",
        "meta_title": "SEO سایت",
        "meta_description": "SEO Description سایت",
        "hero_slide_id": 0,
        "hero_revision": 0,
        "updated_at": "2026-09-02T10:00:00+00:00",
        "profile": {
            "desktop_product_id": desktop_product_id,
            "sync_revision": revision,
            "product_type": "ready_product",
            "use_description": "کاربرد سایت",
            "availability_status": "made_to_order",
            "stock_quantity": 4,
            "lead_time_min_days": 2,
            "lead_time_max_days": 5,
            "has_3d_file": False,
            "license_name": "Commercial",
            "license_url": "https://example.com/license",
            "technical_features": {"کاربرد": "دکور"},
            "keywords": ["چاپ سه بعدی", "دکور"],
            "price_min": 720000,
            "price_max": 720000,
            "price_mode": "fixed",
            "pricing_strategy": "fixed",
            "pricing_inputs": {"part_weight_grams": 100},
            "technical_summary_fa": "خلاصه فنی سایت",
            "homepage_slider_enabled": False,
        },
    }


class Phase493I52BBidirectionalSiteSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp.name) / "catalog.sqlite3")
        self.kernel = build_kernel(self.db)

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def _local_product(self, *, server_id=501, revision=1, dirty=False):
        self.db.upsert_product({
            "source_code": "makerworld",
            "external_id": "phase52b-1",
            "source_url": "https://makerworld.com/en/models/phase52b-1",
            "source_title": "Original",
            "title_fa": "عنوان Local",
            "workflow_status": "uploaded",
            "server_id": "asset-501",
            "server_status": "updated",
            "server_product_id": server_id,
            "server_product_revision": revision,
            "needs_update": int(bool(dirty)),
            "upload_ready": 0,
        })
        row = self.db.conn.execute(
            "SELECT * FROM products WHERE source_code='makerworld' AND external_id='phase52b-1'"
        ).fetchone()
        return int(row["id"])

    def test_apply_server_product_maps_canonical_profile_and_pricing(self):
        local_id = self._local_product()
        apply_server_product_to_local(
            self.db,
            local_id,
            server_product(revision=4),
        )
        row = dict(self.db.product(local_id))
        self.assertEqual(row["server_product_revision"], 4)
        self.assertEqual(row["title_fa"], "عنوان سایت")
        self.assertEqual(row["pricing_strategy"], "fixed")
        self.assertEqual(json.loads(row["pricing_inputs_json"])["part_weight_grams"], 100)
        self.assertEqual(row["technical_summary_fa"], "خلاصه فنی سایت")
        self.assertEqual(row["price_min"], 720000)
        self.assertEqual(row["price_max"], 720000)
        self.assertEqual(row["final_price"], 720000)
        self.assertEqual(row["price_is_final"], 1)
        self.assertEqual(row["stock_quantity"], 4)
        self.assertEqual(row["lead_time_max_days"], 5)
        self.assertEqual(json.loads(row["technical_features_json"])["کاربرد"], "دکور")

    def test_pull_creates_non_publishable_site_origin_mirror(self):
        payload = server_product(product_id=777, revision=2, active=True)
        with patch.object(
            self.kernel.connection,
            "bridge_settings",
            return_value=SimpleNamespace(site_url="https://site.test"),
        ), patch(
            "app.epic49_site_sync.list_all_products",
            return_value=[payload],
        ):
            result = self.kernel.pull_site_products()

        self.assertEqual(result["created"], 1)
        row = self.db.conn.execute(
            "SELECT * FROM products WHERE server_product_id=777"
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["source_code"], "site-admin")
        self.assertEqual(row["reference_only"], 1)
        self.assertEqual(row["workflow_status"], "uploaded")
        self.assertEqual(row["server_product_revision"], 2)
        self.assertEqual(row["title_fa"], "عنوان سایت")
        self.assertEqual(row["needs_update"], 0)

    def test_newer_site_revision_never_overwrites_dirty_local_product(self):
        local_id = self._local_product(revision=2, dirty=True)
        payload = server_product(
            product_id=501,
            revision=3,
            title="نباید overwrite شود",
        )
        with patch.object(
            self.kernel.connection,
            "bridge_settings",
            return_value=SimpleNamespace(site_url="https://site.test"),
        ), patch(
            "app.epic49_site_sync.list_all_products",
            return_value=[payload],
        ):
            result = self.kernel.pull_site_products()

        row = dict(self.db.product(local_id))
        self.assertEqual(result["conflict_count"], 1)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(row["title_fa"], "عنوان Local")
        self.assertEqual(row["needs_update"], 1)
        self.assertIn("Site revision 3", row["last_sync_conflict"])

    def test_clean_local_product_accepts_newer_site_revision(self):
        local_id = self._local_product(revision=2, dirty=False)
        payload = server_product(product_id=501, revision=3)
        with patch.object(
            self.kernel.connection,
            "bridge_settings",
            return_value=SimpleNamespace(site_url="https://site.test"),
        ), patch(
            "app.epic49_site_sync.list_all_products",
            return_value=[payload],
        ):
            result = self.kernel.pull_site_products()
        row = dict(self.db.product(local_id))
        self.assertEqual(result["updated"], 1)
        self.assertEqual(row["server_product_revision"], 3)
        self.assertEqual(row["title_fa"], "عنوان سایت")
        self.assertEqual(row["needs_update"], 0)

    def test_publish_guard_stops_stale_local_revision(self):
        local_id = self._local_product(revision=2, dirty=True)
        result = guard_site_revisions(
            self.db,
            object(),
            [local_id],
            server_getter=lambda _settings, _server_id: server_product(
                product_id=501,
                revision=3,
            ),
        )
        self.assertEqual(result["safe_ids"], [])
        self.assertEqual(len(result["conflicts"]), 1)
        self.assertIn(
            "Pull Site changes",
            self.db.product(local_id)["last_sync_conflict"],
        )

    def test_publish_guard_allows_exact_accepted_revision(self):
        local_id = self._local_product(revision=3, dirty=True)
        result = guard_site_revisions(
            self.db,
            object(),
            [local_id],
            server_getter=lambda _settings, _server_id: server_product(
                product_id=501,
                revision=3,
            ),
        )
        self.assertEqual(result["safe_ids"], [local_id])
        self.assertEqual(result["conflicts"], [])

    def test_products_page_exposes_site_pull_action(self):
        page = ProductsPage(
            self.db,
            open_product=lambda _product_id: None,
            kernel=self.kernel,
        )
        try:
            self.assertIn("دریافت تغییرات سایت", page.pull_site_btn.text())
            self.assertIsNotNone(page.site_sync_pool)
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
