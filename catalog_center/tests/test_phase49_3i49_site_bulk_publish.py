from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from app.db import Database
from app.phase49_3c_image_pipeline import (
    finalize_selected_images,
    promote_selected_product_local_seo_files,
)
from app.epic49_desktop_schema import add_available_material_color
from app.phase49_3i49_site_publish import (
    _next_batch_name,
    build_publish_batch,
    mark_ready_many,
    publish_many,
    publish_media_gate,
    refresh_hero_revision_authority,
)
from app.epic49_site_sync import BridgeNotFoundError
from qt6.kernel import build_kernel
from qt6.pages import OperationsPage, ProductsPage
from qt6.product_wizard import ProductWizardPage


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

    def _product(
        self,
        external_id: str,
        *,
        finalize_images: bool = True,
        with_profiles: bool = True,
    ) -> int:
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
            "sales_profiles_json": json.dumps([{
                "key": "test-profile-1",
                "name": "Default",
                "size_label": "Default",
                "weight_grams": 100,
                "material_weight_grams": 100,
                "print_time_minutes": 60,
                "build_profile": "standard",
                "material": "PLA",
                "color": "Black",
                "quality": "standard",
                "stock_status": "made_to_order",
                "track_inventory": False,
                "is_active": True,
            }] if with_profiles else []),
            "sales_profile_ledger_json": json.dumps([{
                "key": "test-ledger-1",
                "name": "Default",
                "size_label": "Default",
                "production_rows": [{
                    "weight_grams": 100,
                    "print_time_minutes": 60,
                    "support_weight_grams": 0,
                }],
                "material_options": [{"material": "PLA", "color": "Black"}],
            }] if with_profiles else []),
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
        product_id = int(row["id"])
        if finalize_images:
            finalize_selected_images(self.db, product_id)
        return product_id

    def test_ready_refreshes_filament_snapshot_and_price_range_without_opening_product(self):
        product_id = self._product("3491097")
        add_available_material_color(
            self.db,
            "PLA",
            "Black",
            roll_weight_grams=1000,
            stock_roll_count=1,
            purchase_price_per_roll=3_500_000,
            sale_price_per_roll=4_500_000,
            print_hourly_rate=150_000,
            supervision_hourly_rate=50_000,
            preheat_hours=4,
            preheat_temperature_c=55,
            preheat_hourly_rate=30_000,
        )

        before = dict(self.db.product(product_id))
        before_profiles = json.loads(before["sales_profiles_json"])
        self.assertNotIn("print_hourly_rate", before_profiles[0])

        ready = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(ready["marked"], 1)
        self.assertEqual(ready["pricing_refreshed_ids"], [product_id])

        row = dict(self.db.product(product_id))
        self.assertEqual(int(row["price_min"]), 770_000)
        self.assertEqual(int(row["price_max"]), 770_000)
        profiles = json.loads(row["sales_profiles_json"])
        ledger = json.loads(row["sales_profile_ledger_json"])
        self.assertEqual(profiles[0]["print_hourly_rate"], 150_000)
        self.assertEqual(profiles[0]["supervision_hourly_rate"], 50_000)
        self.assertEqual(profiles[0]["preheat_hours"], 4)
        self.assertEqual(profiles[0]["preheat_hourly_rate"], 30_000)
        self.assertEqual(profiles[0]["support_cost_multiplier"], 1)
        self.assertEqual(profiles[0]["assembly_fee"], 0)
        self.assertEqual(
            ledger[0]["material_options"][0]["print_hourly_rate"],
            150_000,
        )
        self.assertEqual(
            ledger[0]["material_options"][0]["supervision_hourly_rate"],
            50_000,
        )

    def test_ready_refreshes_edited_source_bytes_before_republish(self):
        product_id = self._product("3491098")
        row = dict(self.db.product(product_id))
        selected_before = json.loads(row["selected_images_json"])
        metadata_before = json.loads(row["image_metadata_json"])
        self.assertEqual(len(metadata_before), 1)
        old_original_sha = metadata_before[0]["original_sha256"]
        old_final_sha = metadata_before[0]["final_sha256"]

        source_path = Path(row["local_dir"]) / "images" / "source.jpg"
        Image.new("RGB", (720, 540), (25, 190, 80)).save(
            source_path,
            "JPEG",
            quality=94,
        )
        new_source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
        self.assertNotEqual(new_source_sha, old_original_sha)

        stale = publish_media_gate(self.db.product(product_id))
        self.assertFalse(stale["ready"])
        self.assertTrue(
            any(
                "source image changed after finalization" in item
                for item in stale["missing"]
            )
        )

        ready = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(ready["marked"], 1)
        self.assertEqual(ready["media_refreshed_ids"], [product_id])
        self.assertEqual(ready["media_refresh_failed"], [])

        refreshed = dict(self.db.product(product_id))
        self.assertEqual(
            json.loads(refreshed["selected_images_json"]),
            selected_before,
        )
        metadata_after = json.loads(refreshed["image_metadata_json"])
        self.assertEqual(metadata_after[0]["original_sha256"], new_source_sha)
        self.assertNotEqual(metadata_after[0]["final_sha256"], old_final_sha)
        self.assertTrue(publish_media_gate(refreshed)["ready"])

    def test_physical_seo_promotion_does_not_create_false_source_drift(self):
        product_id = self._product("3491098p")
        before = dict(self.db.product(product_id))
        metadata_before = json.loads(before["image_metadata_json"])
        self.assertEqual(len(metadata_before), 1)
        original_sha = metadata_before[0]["original_sha256"]

        promoted = promote_selected_product_local_seo_files(
            self.db,
            product_id,
        )
        self.assertEqual(promoted["selected"], 1)
        self.assertEqual(promoted["renamed_local"], 1)

        after = dict(self.db.product(product_id))
        metadata_after = json.loads(after["image_metadata_json"])
        self.assertEqual(
            hashlib.sha256(
                Path(metadata_after[0]["original_local_file"]).read_bytes()
            ).hexdigest(),
            original_sha,
        )
        self.assertEqual(
            Path(metadata_after[0]["source_local_file"]).name,
            metadata_after[0]["seo_filename"],
        )
        self.assertNotEqual(
            hashlib.sha256(
                Path(metadata_after[0]["source_local_file"]).read_bytes()
            ).hexdigest(),
            original_sha,
        )
        gate = publish_media_gate(after)
        self.assertTrue(gate["ready"], gate["missing"])

    def test_publish_media_fails_closed_when_selected_images_are_outside_canonical_authority(self):
        product_id = self._product("34910981")
        row = dict(self.db.product(product_id))
        selected = json.loads(row["selected_images_json"])
        self.assertEqual(len(selected), 1)
        self.db.update_product(
            product_id,
            {
                "images_json": json.dumps(
                    ["https://cdn.example.com/current-authority.jpg"]
                )
            },
        )

        gated = publish_media_gate(self.db.product(product_id))
        self.assertFalse(gated["ready"])
        self.assertTrue(
            any(
                "selected image authority drift" in item
                and selected[0] in item
                for item in gated["missing"]
            )
        )

        ready = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(ready["marked"], 0)
        self.assertEqual(int(self.db.product(product_id)["upload_ready"]), 0)

    def test_product_without_canonical_sales_profile_never_becomes_ready(self):
        product_id = self._product("3491099", with_profiles=False)
        result = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(result["marked"], 0)
        self.assertEqual(result["publishable_ids"], [])
        missing = result["blocked"][0]["missing"]
        expected = "سفارش و قیمت: حداقل یک پروفایل فروش canonical لازم است"
        self.assertIn(expected, missing)
        self.assertFalse(any("????" in item for item in missing))
        self.assertEqual(int(self.db.product(product_id)["upload_ready"]), 0)

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
            readiness_checker=lambda _settings: {
                "ready": True,
                "blockers": [],
            },
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

    def test_hero_revision_refresh_updates_only_revision_authority(self):
        product_id = self._product("3491099hero")
        self.db.update_product(
            product_id,
            {
                "server_slider_id": 4,
                "server_slider_revision": 3,
                "homepage_slider_enabled": 1,
                "homepage_slider_title_fa": "عنوان اسلایدر اپراتور",
                "homepage_slider_description_fa": "توضیح اسلایدر اپراتور",
                "homepage_slider_image_url": "https://example.com/operator-slider.webp",
                "upload_ready": 1,
                "workflow_status": "approved",
            },
        )
        before = dict(self.db.product(product_id))

        result = refresh_hero_revision_authority(
            self.db,
            SimpleNamespace(),
            [product_id],
            hero_getter=lambda _settings, slide_id: {
                "id": slide_id,
                "sync_revision": 5,
                "is_active": False,
                "title_override": "نسخه قدیمی روی سایت",
                "image_url": "https://example.com/site-old.webp",
            },
        )

        self.assertEqual(result["safe_ids"], [product_id])
        self.assertEqual(result["refreshed_ids"], [product_id])
        self.assertEqual(result["conflicts"], [])
        after = dict(self.db.product(product_id))
        self.assertEqual(int(after["server_slider_id"]), 4)
        self.assertEqual(int(after["server_slider_revision"]), 5)
        self.assertEqual(
            int(after["homepage_slider_enabled"]),
            int(before["homepage_slider_enabled"]),
        )
        self.assertEqual(
            after["homepage_slider_title_fa"],
            before["homepage_slider_title_fa"],
        )
        self.assertEqual(
            after["homepage_slider_description_fa"],
            before["homepage_slider_description_fa"],
        )
        self.assertEqual(
            after["homepage_slider_image_url"],
            before["homepage_slider_image_url"],
        )
        self.assertEqual(int(after["upload_ready"]), 1)
        self.assertEqual(after["workflow_status"], "approved")

    def test_publish_refreshes_stale_hero_revision_before_batch(self):
        product_id = self._product("3491099batch")
        self.db.update_product(
            product_id,
            {
                "server_slider_id": 2,
                "server_slider_revision": 1,
                "homepage_slider_enabled": 1,
            },
        )
        ready = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(ready["marked"], 1)
        seen_revision = {}

        def fake_upload(_settings, batch, callback=None):
            manifest = json.loads(
                (Path(batch) / "batch_manifest.json").read_text(encoding="utf-8")
            )
            model = (manifest.get("models") or [])[0]
            editorial = json.loads(
                (Path(batch) / str(model["editorial"])).read_text(
                    encoding="utf-8"
                )
            )
            seen_revision["value"] = int(
                editorial.get("server_slider_revision") or 0
            )
            return {
                "remote_batch": "/remote/hero-refresh",
                "uploaded_files": 1,
                "total_files": 1,
            }

        def fake_import(_settings, batch_name, batch_uuid):
            return {
                "status": "completed",
                "batch_uuid": batch_uuid,
                "diagnostic_id": batch_name,
                "items": [
                    {
                        "desktop_product_id": product_id,
                        "status": "created",
                        "server_id": "hero-refresh-asset",
                        "product_id": 5001,
                        "product_revision": 1,
                        "slider_id": 2,
                        "slider_revision": 3,
                        "visible_on_store": True,
                        "public_http_ok": True,
                        "product_url": "/store/product/hero-refresh/",
                    }
                ],
            }

        result = publish_many(
            self.db,
            FakeStages(),
            SimpleNamespace(),
            [product_id],
            batch_root=self.root / "hero-refresh-batches",
            uploader=fake_upload,
            importer=fake_import,
            hero_getter=lambda _settings, slide_id: {
                "id": slide_id,
                "sync_revision": 2,
            },
            readiness_checker=lambda _settings: {
                "ready": True,
                "blockers": [],
            },
        )
        self.assertEqual(seen_revision["value"], 2)
        self.assertEqual(result["published"], 1)
        row = dict(self.db.product(product_id))
        self.assertEqual(int(row["server_slider_revision"]), 3)

    def test_failed_republish_preserves_last_verified_site_identity_and_ack(self):
        product_id = self._product("3491003")
        previous_ack = {
            "status": "updated",
            "server_id": 143,
            "product_id": 39,
            "product_revision": 7,
            "visible_on_store": True,
            "public_http_ok": True,
            "product_url": "/store/product/existing-product/",
        }
        self.db.update_product(
            product_id,
            {
                "server_id": "143",
                "server_status": "updated",
                "server_ack_json": json.dumps(previous_ack, ensure_ascii=False),
                "server_product_id": 39,
                "server_product_revision": 7,
                "server_slider_id": 12,
                "server_slider_revision": 4,
                "workflow_status": "uploaded",
                "upload_ready": 0,
            },
        )
        self.db.update_product(product_id, {"needs_update": 1})
        ready = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(ready["marked"], 1)

        def fake_upload(_settings, _batch, callback=None):
            return {"remote_batch": "/remote/fail", "uploaded_files": 1, "total_files": 1}

        def fake_import(_settings, batch_name, batch_uuid):
            return {
                "status": "completed_with_errors",
                "batch_uuid": batch_uuid,
                "diagnostic_id": batch_name,
                "items": [{
                    "desktop_product_id": product_id,
                    "status": "failed",
                    "error": "REPUBLISH_PARITY_MISMATCH: test failure",
                }],
            }

        result = publish_many(
            self.db,
            FakeStages(),
            SimpleNamespace(),
            [product_id],
            batch_root=self.root / "failed-republish-batches",
            uploader=fake_upload,
            importer=fake_import,
            server_getter=lambda _settings, _server_id: {
                "profile": {"sync_revision": 7},
            },
            hero_getter=lambda _settings, slide_id: {
                "id": slide_id,
                "sync_revision": 4,
            },
            readiness_checker=lambda _settings: {"ready": True, "blockers": []},
        )
        self.assertEqual(result["published"], 0)
        self.assertEqual(result["failed"], 1)

        row = dict(self.db.product(product_id))
        self.assertEqual(int(row["server_product_id"]), 39)
        self.assertEqual(int(row["server_product_revision"]), 7)
        self.assertEqual(int(row["server_slider_id"]), 12)
        self.assertEqual(int(row["server_slider_revision"]), 4)
        self.assertEqual(str(row["server_id"]), "143")
        self.assertEqual(json.loads(row["server_ack_json"]), previous_ack)
        self.assertEqual(row["server_status"], "failed")
        self.assertIn("REPUBLISH_PARITY_MISMATCH", row["product_sync_error"])
        failed_receipts = [
            item for item in self.db.sync_receipts(product_id, limit=20)
            if str(item["status"] or "") == "failed"
        ]
        self.assertEqual(len(failed_receipts), 1)

    def test_publish_ready_requires_current_final_seo_webp(self):
        product_id = self._product("3491012", finalize_images=False)
        blocked = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(blocked["marked"], 0)
        self.assertTrue(
            any(
                "Publish media" in text
                for text in blocked["blocked"][0]["missing"]
            )
        )

        finalized = finalize_selected_images(self.db, product_id)
        self.assertEqual(finalized["kept"], 1)
        row = dict(self.db.product(product_id))
        metadata = json.loads(row["image_metadata_json"])
        self.assertEqual(len(metadata), 1)
        final_path = Path(metadata[0]["final_local_file"])
        self.assertEqual(final_path.suffix.lower(), ".webp")
        self.assertTrue(final_path.is_file())

        ready = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(ready["marked"], 1)

    def test_stale_image_seo_signature_blocks_ready_until_refinalized(self):
        product_id = self._product("3491013")
        self.db.update_product(
            product_id,
            {"seo_title_fa": "SEO title changed after image finalization"},
        )
        blocked = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(blocked["marked"], 0)
        self.assertTrue(
            any(
                "stale" in text.lower()
                for text in blocked["blocked"][0]["missing"]
            )
        )
        finalize_selected_images(self.db, product_id)
        ready = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(ready["marked"], 1)

    def test_publish_batch_preserves_final_seo_webp_bytes_and_filename(self):
        product_id = self._product("3491014")
        mark_ready_many(self.db, FakeStages(), [product_id])
        row = dict(self.db.product(product_id))
        metadata = json.loads(row["image_metadata_json"])
        expected_name = metadata[0]["seo_filename"]
        expected_sha = metadata[0]["final_sha256"]
        seen = {}

        def fake_upload(_settings, batch, callback=None):
            matches = list(Path(batch).rglob(f"images/{expected_name}"))
            self.assertEqual(len(matches), 1)
            packaged = matches[0]
            seen["name"] = packaged.name
            seen["sha"] = hashlib.sha256(packaged.read_bytes()).hexdigest()
            return {"remote_batch": "/remote/test", "uploaded_files": 1, "total_files": 1}

        def fake_import(_settings, batch_name, batch_uuid):
            return {
                "status": "ok",
                "batch_uuid": batch_uuid,
                "diagnostic_id": batch_name,
                "items": [{
                    "desktop_product_id": product_id,
                    "status": "created",
                    "server_id": "asset-media",
                    "product_id": 1514,
                    "product_revision": 1,
                    "visible_on_store": True,
                    "public_http_ok": True,
                    "product_url": "/shop/media/",
                    "source_hash": "source-media",
                }],
            }

        result = publish_many(
            self.db,
            FakeStages(),
            SimpleNamespace(),
            [product_id],
            batch_root=self.root / "media-batches",
            uploader=fake_upload,
            importer=fake_import,
            readiness_checker=lambda _settings: {"ready": True, "blockers": []},
        )
        self.assertEqual(result["published"], 1)
        self.assertEqual(seen["name"], expected_name)
        self.assertEqual(seen["sha"], expected_sha)

    def test_publish_batch_carries_every_selected_image_with_unique_seo_filename(self):
        product_id = self._product("3491014m", finalize_images=False)
        row = dict(self.db.product(product_id))
        local_dir = Path(row["local_dir"])
        image_dir = local_dir / "images"
        selected = json.loads(row["selected_images_json"])
        canonical = json.loads(row["images_json"])
        for index, rgb in enumerate(
            [(20, 40, 60), (80, 100, 120), (140, 160, 180)],
            start=2,
        ):
            path = image_dir / f"{index:02d}.webp"
            Image.new("RGB", (720 + index, 540 + index), rgb).save(
                path,
                "WEBP",
                quality=90,
            )
            pseudo = f"local://{index:02d}.webp"
            canonical.append(pseudo)
            selected.append(pseudo)
        self.db.update_product(
            product_id,
            {
                "images_json": json.dumps(canonical, ensure_ascii=False),
                "selected_images_json": json.dumps(selected, ensure_ascii=False),
                "image_alt_texts_json": json.dumps(
                    [f"ALT {index}" for index in range(1, len(selected) + 1)],
                    ensure_ascii=False,
                ),
            },
        )
        finalized = finalize_selected_images(
            self.db,
            product_id,
            deduplicate=False,
            image_limit=len(selected),
        )
        self.assertEqual(finalized["kept"], 4)
        gate = publish_media_gate(self.db.product(product_id))
        self.assertTrue(gate["ready"], gate["missing"])
        self.assertEqual(len(gate["items"]), 4)
        seo_names = [item["seo_filename"] for item in gate["items"]]
        self.assertEqual(len(set(name.casefold() for name in seo_names)), 4)
        self.assertTrue(all(name.endswith(".webp") for name in seo_names))

        mark_ready_many(self.db, FakeStages(), [product_id])
        captured = {}

        def fake_upload(_settings, batch, callback=None):
            packaged = sorted(Path(batch).rglob("images/*.webp"))
            captured["names"] = [path.name for path in packaged]
            return {
                "remote_batch": "/remote/test",
                "uploaded_files": len(packaged),
                "total_files": len(packaged),
            }

        def fake_import(_settings, batch_name, batch_uuid):
            return {
                "status": "ok",
                "batch_uuid": batch_uuid,
                "diagnostic_id": batch_name,
                "items": [{
                    "desktop_product_id": product_id,
                    "status": "created",
                    "server_id": "asset-multi-media",
                    "product_id": 1515,
                    "product_revision": 1,
                    "visible_on_store": True,
                    "public_http_ok": True,
                    "product_url": "/shop/multi-media/",
                    "source_hash": "source-multi-media",
                }],
            }

        result = publish_many(
            self.db,
            FakeStages(),
            SimpleNamespace(),
            [product_id],
            batch_root=self.root / "multi-media-batches",
            uploader=fake_upload,
            importer=fake_import,
            readiness_checker=lambda _settings: {
                "ready": True,
                "blockers": [],
            },
        )
        self.assertEqual(result["published"], 1)
        self.assertEqual(
            sorted(captured["names"]),
            sorted(seo_names),
        )

    def test_site_receiver_readiness_blocks_before_ftp(self):
        product_id = self._product("3491011")
        mark_ready_many(self.db, FakeStages(), [product_id])
        uploaded = []

        def fake_upload(*_args, **_kwargs):
            uploaded.append(True)
            return {}

        with self.assertRaisesRegex(RuntimeError, "گیرنده انتشار سایت آماده نیست"):
            publish_many(
                self.db,
                FakeStages(),
                SimpleNamespace(),
                [product_id],
                batch_root=self.root / "blocked-batches",
                uploader=fake_upload,
                importer=lambda *_args, **_kwargs: {},
                readiness_checker=lambda _settings: {
                    "ready": False,
                    "blockers": [
                        "migration:store.0042_phase49_3i51_filament_registry_descriptions:missing",
                        "media_root:not_writable",
                    ],
                },
            )

        self.assertEqual(uploaded, [])
        self.assertEqual(
            int(self.db.product(product_id)["upload_ready"]),
            1,
        )

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
        self.assertEqual(self.db.product_count(filter_name="published"), 1)
        self.assertEqual(self.db.product_count(filter_name="work_queue"), 1)

        ready = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(ready["marked"], 1)
        self.assertEqual(int(self.db.product(product_id)["upload_ready"]), 1)

    def test_explicit_ready_requeues_unchanged_uploaded_product(self):
        product_id = self._product("3491021")
        self.db.update_product(product_id, {
            "server_id": "asset-900",
            "server_product_id": 1900,
            "server_product_revision": 4,
            "workflow_status": "uploaded",
            "needs_update": 0,
            "upload_ready": 0,
        })
        ready = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(ready["marked"], 1)
        row = dict(self.db.product(product_id))
        self.assertEqual(row["workflow_status"], "approved")
        self.assertEqual(int(row["upload_ready"]), 1)
        self.assertEqual(row["server_id"], "asset-900")
        self.assertEqual(int(row["server_product_id"]), 1900)

    def test_batch_name_stays_bridge_compatible_when_current_second_is_taken(self):
        root = self.root / "batch-name-collision"
        root.mkdir(parents=True, exist_ok=True)
        first = _next_batch_name(root)
        (root / first).mkdir()
        second = _next_batch_name(root)
        self.assertRegex(first, r"^desktop_catalog_v85_[0-9]{8}_[0-9]{6}$")
        self.assertRegex(second, r"^desktop_catalog_v85_[0-9]{8}_[0-9]{6}$")
        self.assertNotEqual(first, second)

    def test_republish_batch_carries_updated_profile_filament_and_print_time(self):
        product_id = self._product("3491023")
        self.db.update_product(product_id, {
            "server_id": "asset-902",
            "server_product_id": 1902,
            "server_product_revision": 2,
            "workflow_status": "uploaded",
            "needs_update": 0,
            "upload_ready": 0,
        })
        profiles = [{
            "key": "updated-profile",
            "name": "Updated",
            "size_label": "30cm",
            "weight_grams": 180,
            "material_weight_grams": 180,
            "print_time_minutes": 150,
            "build_profile": "standard",
            "material": "PETG",
            "color": "Black",
            "quality": "standard",
            "stock_status": "made_to_order",
            "track_inventory": False,
            "is_active": True,
        }]
        ledger = [{
            "key": "updated-profile",
            "name": "Updated",
            "size_label": "30cm",
            "production_rows": [{
                "weight_grams": 180,
                "print_time_minutes": 150,
                "support_weight_grams": 12,
            }],
            "material_options": [{
                "material": "PETG",
                "brand": "E-Sun",
                "color": "Black",
            }],
        }]
        self.kernel.stages.update(product_id, "commerce", {
            "sales_profiles_json": json.dumps(profiles),
            "sales_profile_ledger_json": json.dumps(ledger),
        })
        self.assertEqual(int(self.db.product(product_id)["needs_update"]), 1)
        ready = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(ready["marked"], 1)
        batch = build_publish_batch(self.db, [product_id], batch_root=self.root / "updated-batches")
        manifest = json.loads((Path(batch["batch"]) / "batch_manifest.json").read_text(encoding="utf-8"))
        editorial_path = Path(batch["batch"]) / manifest["models"][0]["editorial"]
        editorial = json.loads(editorial_path.read_text(encoding="utf-8"))
        carried_profiles = json.loads(editorial["sales_profiles_json"])
        carried_ledger = json.loads(editorial["sales_profile_ledger_json"])
        self.assertEqual(carried_profiles[0]["print_time_minutes"], 150)
        self.assertEqual(carried_profiles[0]["material"], "PETG")
        self.assertEqual(carried_ledger[0]["production_rows"][0]["print_time_minutes"], 150)
        self.assertEqual(carried_ledger[0]["material_options"][0]["brand"], "E-Sun")

    def test_missing_site_product_recreates_from_preserved_asset_identity(self):
        product_id = self._product("3491022")
        self.db.update_product(product_id, {
            "server_id": "asset-901",
            "server_product_id": 1901,
            "server_product_revision": 8,
            "workflow_status": "uploaded",
            "needs_update": 0,
            "upload_ready": 0,
        })
        mark_ready_many(self.db, FakeStages(), [product_id])
        def missing(*_args, **_kwargs):
            raise BridgeNotFoundError(path="products/1901/", payload={"detail": "not found"})
        def upload(*_args, **_kwargs):
            return {"remote_batch": "/remote/recreate", "uploaded_files": 1, "total_files": 1}
        def imported(_settings, _batch_name, batch_uuid):
            return {"status":"ok","batch_uuid":batch_uuid,"items":[{
                "desktop_product_id":product_id,"status":"updated","server_id":"asset-901",
                "product_id":2901,"product_revision":1,"visible_on_store":True,"public_http_ok":True,
                "product_url":"/store/product/recreated/","source_hash":"recreated-source",
            }]}
        result = publish_many(self.db, FakeStages(), SimpleNamespace(), [product_id],
            batch_root=self.root / "recreate-batches", uploader=upload, importer=imported,
            server_getter=missing, readiness_checker=lambda _settings:{"ready":True,"blockers":[]})
        self.assertEqual(result["published"], 1)
        row = dict(self.db.product(product_id))
        self.assertEqual(int(row["server_product_id"]), 2901)
        self.assertEqual(int(row["server_product_revision"]), 1)
        self.assertEqual(row["workflow_status"], "uploaded")

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

    def test_product_wizard_stage7_exposes_single_product_publish_actions(self):
        product_id = self._product("3491020")
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            self.assertIn("آماده انتشار همین محصول", page.ready_current_btn.text())
            self.assertIn("ارسال همین محصول به سایت", page.publish_current_btn.text())
            page.approved_for_sale.setChecked(True)
            page.publish_product.setChecked(True)
            page.kernel.publish.mark_ready_many = lambda ids: mark_ready_many(
                self.db, FakeStages(), ids
            )
            with patch.object(QMessageBox, "information"), patch.object(
                QMessageBox, "warning"
            ):
                page._mark_current_ready()
            row = self.db.product(product_id)
            self.assertEqual(int(row["approved_for_sale"]), 1)
            self.assertEqual(int(row["publish_as_product"]), 1)
            self.assertEqual(int(row["upload_ready"]), 1)
            self.assertEqual(str(row["workflow_status"]), "approved")
        finally:
            page.close()

    def test_ready_finalizes_newly_selected_screenshot_before_publish_gate(self):
        product_id = self._product("3491100")
        row = dict(self.db.product(product_id))
        image_dir = Path(row["local_dir"]) / "images"
        screenshot = image_dir / "source-page-screenshot-a2w.png"
        Image.new("RGB", (640, 480), (35, 140, 210)).save(screenshot, "PNG")
        pseudo = "local://source-page-screenshot-a2w.png"
        canonical = json.loads(row["images_json"])
        selected = json.loads(row["selected_images_json"])
        canonical.append(pseudo)
        selected.append(pseudo)
        self.db.update_product(product_id, {
            "images_json": json.dumps(canonical),
            "selected_images_json": json.dumps(selected),
        })

        stale = publish_media_gate(self.db.product(product_id))
        self.assertFalse(stale["ready"])
        self.assertTrue(any("SEO metadata is missing" in value for value in stale["missing"]))

        ready = mark_ready_many(self.db, FakeStages(), [product_id])
        self.assertEqual(ready["marked"], 1)
        self.assertIn(product_id, ready["media_prepared_ids"])
        self.assertEqual(ready["media_prepare_failed"], [])
        gate = publish_media_gate(self.db.product(product_id))
        self.assertTrue(gate["ready"], gate["missing"])
        after = dict(self.db.product(product_id))
        self.assertEqual(json.loads(after["selected_images_json"]), selected)
        metadata = json.loads(after["image_metadata_json"])
        self.assertEqual({item["source_url"] for item in metadata}, set(selected))
        self.assertEqual(len(gate["items"]), 2)

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
            self.assertIn("Post + Story خودکار", page.instagram_publish_btn.text())
        finally:
            page.close()

    def test_products_page_blocks_social_before_worker_when_buffer_mobile_missing(self):
        product_id = self._product("3491101")
        page = ProductsPage(
            self.db,
            open_product=lambda _product_id: None,
            kernel=self.kernel,
        )
        try:
            page._selected_product_ids = lambda: [product_id]
            page.kernel.instagram.delivery_readiness = lambda: {
                "provider": "buffer",
                "ready": False,
                "has_active_member_device": False,
                "blockers": ["Story لینک‌دار نیازمند Buffer mobile فعال است."],
            }
            with patch.object(QMessageBox, "warning") as warning:
                page._publish_instagram_selected()
            self.assertIsNone(page._instagram_worker)
            warning.assert_called_once()
            self.assertIn(
                "Post رفت ولی Story نرفت",
                str(warning.call_args.args[2]),
            )
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
