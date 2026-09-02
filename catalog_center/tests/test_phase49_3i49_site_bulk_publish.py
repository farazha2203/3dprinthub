from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.db import Database
from app.phase49_3i49_site_publish import mark_ready_many, publish_many
from qt6.kernel import build_kernel
from qt6.pages import OperationsPage, ProductsPage


class FakeStages:
    def __init__(self, blocked: set[int] | None = None) -> None:
        self.blocked = set(blocked or set())

    def statuses(self, product_id: int):
        if int(product_id) in self.blocked:
            return [
                {
                    "stage": "content",
                    "label": "۴. محتوا و SEO",
                    "data_ready": False,
                    "missing": ["SEO Description فارسی"],
                }
            ]
        return [
            {
                "stage": name,
                "label": label,
                "data_ready": True,
                "missing": [],
            }
            for name, label in (
                ("quick", "۱. اطلاعات پایه"),
                ("commerce", "۲. سفارش، قیمت و گزینه‌ها"),
                ("images", "۳. تصاویر"),
                ("content", "۴. محتوا و SEO"),
                ("specs", "۵. منبع و مجوز"),
                ("slider", "۶. اسلایدر صفحه اول"),
                ("publish", "۷. بررسی و انتشار"),
            )
        ]


class Phase493I49SiteBulkPublishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = Database(self.root / "catalog.sqlite3")
        self.db.upsert_source({
            "code": "makerworld",
            "name": "MakerWorld",
            "enabled": 1,
            "methods": ["http"],
            "listing_urls": [],
            "model_url_pattern": "",
            "requires_login": False,
            "reference_only": False,
        })
        self.kernel = build_kernel(self.db)

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def _product(self, external_id: str) -> int:
        local_dir = self.root / f"product-{external_id}"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        image_path = image_dir / "source.jpg"
        Image.new("RGB", (720, 540), (120, 40, 180)).save(
            image_path,
            "JPEG",
            quality=90,
        )
        url = f"https://cdn.example.com/{external_id}.jpg"
        (local_dir / "page_extract.json").write_text(
            json.dumps({
                "images": [{"url": url, "local_file": str(image_path)}],
            }),
            encoding="utf-8",
        )
        self.db.upsert_product({
            "source_code": "makerworld",
            "external_id": external_id,
            "source_url": f"https://makerworld.com/en/models/{external_id}",
            "source_title": f"Owner Product {external_id}",
            "title_fa": f"محصول {external_id}",
            "short_description_fa": "توضیح فارسی محصول آماده",
            "description_fa": "توضیح کامل فارسی محصول آماده برای انتشار",
            "local_category_slug": "home-decor",
            "product_type": "ready_product",
            "local_dir": str(local_dir),
            "images_json": json.dumps([url]),
            "selected_images_json": json.dumps([url]),
            "primary_image_url": url,
            "image_alt_texts_json": json.dumps([f"محصول {external_id}"]),
            "materials_json": json.dumps(["PLA"]),
            "colors_json": json.dumps(["مشکی"]),
            "keywords_json": json.dumps(["چاپ سه بعدی", "محصول سه بعدی", "دکور"]),
            "seo_title_fa": f"خرید محصول {external_id}",
            "seo_description_fa": "توضیح سئو کامل برای محصول سه بعدی و سفارش چاپ حرفه ای.",
            "suggested_price": 850000,
            "final_price": 900000,
            "price_is_final": 1,
            "approved_for_sale": 1,
            "publish_as_product": 0,
            "workflow_status": "review",
        })
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("makerworld", external_id),
        ).fetchone()
        return int(row["id"])

    def test_two_ready_products_publish_and_move_to_published_filter(self):
        first = self._product("3491001")
        second = self._product("3491002")
        stages = FakeStages()

        ready = mark_ready_many(self.db, stages, [first, second])
        self.assertEqual(ready["marked"], 2)
        self.assertEqual(int(self.db.product(first)["upload_ready"]), 1)
        self.assertEqual(int(self.db.product(second)["upload_ready"]), 1)
        self.assertEqual(int(self.db.product(first)["publish_as_product"]), 1)

        uploaded = []

        def fake_upload(_settings, batch, callback=None):
            uploaded.append(Path(batch))
            if callback:
                callback("FTP_UPLOAD test")
            return {
                "remote_batch": "/remote/test",
                "uploaded_files": 5,
                "total_files": 5,
            }

        def fake_import(_settings, batch_name, batch_uuid):
            return {
                "status": "ok",
                "batch_uuid": batch_uuid,
                "diagnostic_id": batch_name,
                "items": [
                    {
                        "desktop_product_id": first,
                        "status": "created",
                        "server_id": "asset-501",
                        "product_id": 1501,
                        "product_revision": 1,
                        "visible_on_store": True,
                        "public_http_ok": True,
                        "product_url": "/shop/product-one/",
                        "source_hash": "source-1",
                    },
                    {
                        "desktop_product_id": second,
                        "status": "created",
                        "server_id": "asset-502",
                        "product_id": 1502,
                        "product_revision": 1,
                        "visible_on_store": True,
                        "public_http_ok": True,
                        "product_url": "/shop/product-two/",
                        "source_hash": "source-2",
                    },
                ],
            }

        result = publish_many(
            self.db,
            stages,
            SimpleNamespace(),
            [first, second],
            batch_root=self.root / "batches",
            uploader=fake_upload,
            importer=fake_import,
        )
        self.assertEqual(result["published"], 2)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(len(uploaded), 1)

        for product_id in (first, second):
            row = self.db.product(product_id)
            self.assertEqual(row["workflow_status"], "uploaded")
            self.assertEqual(int(row["upload_ready"]), 0)
            self.assertEqual(int(row["needs_update"]), 0)
            self.assertTrue(str(row["server_id"]))
            self.assertTrue(str(row["published_at"]))
        self.assertEqual(self.db.product_count(filter_name="published"), 2)

    def test_incomplete_product_cannot_receive_ready_tick(self):
        product_id = self._product("3491003")
        stages = FakeStages({product_id})
        result = mark_ready_many(self.db, stages, [product_id])
        self.assertEqual(result["marked"], 0)
        self.assertEqual(int(self.db.product(product_id)["upload_ready"]), 0)
        self.assertTrue(result["blocked"])
        self.assertTrue(
            any(
                "SEO Description" in text
                for text in result["blocked"][0]["missing"]
            )
        )

    def test_editing_published_content_sets_needs_update_for_same_identity_republish(self):
        product_id = self._product("3491010")
        self.db.update_product(
            product_id,
            {
                "server_id": "asset-777",
                "server_product_id": 1777,
                "server_status": "updated",
                "workflow_status": "uploaded",
                "needs_update": 0,
                "upload_ready": 0,
            },
        )

        self.kernel.stages.update(
            product_id,
            "content",
            {"description_fa": "توضیح فارسی اصلاح‌شده برای انتشار مجدد"},
        )
        row = dict(self.db.product(product_id))
        self.assertEqual(row["server_id"], "asset-777")
        self.assertEqual(int(row["server_product_id"]), 1777)
        self.assertEqual(row["workflow_status"], "uploaded")
        self.assertEqual(int(row["needs_update"]), 1)
        self.assertEqual(int(row["upload_ready"]), 0)
        self.assertEqual(self.db.product_count(filter_name="published"), 0)

        ready = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(ready["marked"], 1)
        self.assertEqual(int(self.db.product(product_id)["upload_ready"]), 1)

    def test_existing_server_import_contract_updates_asset_product_in_place(self):
        source = (
            Path(__file__).resolve().parents[2]
            / "store"
            / "phase34b_publishing.py"
        ).read_text(encoding="utf-8")
        self.assertIn("if asset.product_id:", source)
        self.assertIn("_sync_product_fields(product, asset)", source)
        self.assertIn("return product", source)

    def test_operations_page_exposes_search_link_review_and_collect_ai_actions(self):
        page = OperationsPage(self.db, kernel=self.kernel)
        try:
            labels = [
                page.workspace_tabs.tabText(index)
                for index in range(page.workspace_tabs.count())
            ]
            self.assertIn("دریافت محصولات از لینک جستجو", labels)
            self.assertIn("مشاهده صفحه محصول", page.queue_open_btn.text())
            self.assertIn("AI", page.queue_collect_ai_btn.text())
        finally:
            page.close()

    def test_products_page_exposes_explicit_ready_and_bulk_publish_actions(self):
        page = ProductsPage(
            self.db,
            open_product=lambda _product_id: None,
            kernel=self.kernel,
        )
        try:
            self.assertIn("آماده انتشار", page.ready_publish_btn.text())
            self.assertIn("باز کردن صفحه محصول", page.open_source_btn.text())
            self.assertIn("انتشار", page.bulk_publish_btn.text())
            self.assertIn("سایت", page.bulk_publish_btn.text())
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
