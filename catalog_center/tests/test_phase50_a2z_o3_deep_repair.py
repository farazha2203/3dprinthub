from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton

from app.db import Database
from qt6 import acquisition_runtime
from qt6.kernel import build_kernel
from qt6.product_wizard import ProductWizardPage


class Phase50A2ZO3DeepRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.old_data_root = os.environ.get("CATALOG_DATA_ROOT")
        os.environ["CATALOG_DATA_ROOT"] = str(self.root / "data")
        self.db = Database(self.root / "catalog.sqlite3")
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

    def _product(self, external_id: str = "520040") -> tuple[int, Path, str]:
        source_url = (
            f"https://makerworld.com/en/models/{external_id}-o3-deep-repair"
        )
        old_dir = (
            self.root / "data" / "collected" / "makerworld" / external_id
        )
        images_dir = old_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (320, 240), "white").save(images_dir / "old.jpg")
        selected = (
            "https://makerworld.bblmw.com/makerworld/model/"
            f"{external_id}/design/2026/09/o3-demo.webp?old=1"
        )
        self.db.upsert_product({
            "source_code": "makerworld",
            "external_id": external_id,
            "source_url": source_url,
            "source_title": "Old Source Title",
            "source_description": "Old source description",
            "title_fa": "عنوان اپراتور",
            "description_fa": "توضیح اپراتور",
            "final_price": 910000,
            "price_is_final": 1,
            "approved_for_sale": 1,
            "publish_as_product": 1,
            "local_dir": str(old_dir),
            "images_json": json.dumps([selected], ensure_ascii=False),
            "selected_images_json": json.dumps([selected], ensure_ascii=False),
            "primary_image_url": selected,
        })
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("makerworld", external_id),
        ).fetchone()
        product_id = int(row["id"])
        self.db.update_product(product_id, {
            "server_id": "39",
            "server_status": "synced",
            "server_ack_json": json.dumps({"revision": 11}),
            "server_product_id": "39",
            "server_product_revision": 11,
            "last_synced_at": "2026-09-21T10:00:00+00:00",
            "published_at": "2026-09-21T10:00:00+00:00",
        })
        self.db.record_sync_receipt(
            product_id,
            "batch-o3",
            "published",
            "39",
            {"revision": 11, "proof": "keep"},
        )
        return product_id, old_dir, selected

    async def _fresh_result(
        self,
        _db,
        _source_cfg,
        *,
        external_id,
        url,
        local_dir,
        **_kwargs,
    ):
        local_dir = Path(local_dir)
        images_dir = local_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        image_file = images_dir / "fresh.webp"
        Image.new("RGB", (640, 480), "white").save(image_file, format="WEBP")
        fresh_url = (
            "https://makerworld.bblmw.com/makerworld/model/"
            f"{external_id}/design/2026/09/o3-demo.webp"
        )
        (local_dir / "page_extract.json").write_text(
            json.dumps({
                "images": [{
                    "url": fresh_url,
                    "local_file": str(image_file),
                }]
            }),
            encoding="utf-8",
        )
        payload = {
            "source_code": "makerworld",
            "external_id": external_id,
            "source_url": url,
            "source_title": "Fresh Source Title",
            "source_description": "Fresh source description with usable data",
            "source_category": "Decor",
            "images_json": json.dumps([fresh_url]),
            "selected_images_json": json.dumps([fresh_url]),
            "primary_image_url": fresh_url,
            "local_dir": str(local_dir),
        }
        return {
            "product_id": 0,
            "source_payload": payload,
            "images_found": 1,
            "images_saved": 1,
            "selected_method": "rich",
            "attempted_methods": ["rich"],
            "fallback_used": False,
            "image_fallback_method": "",
            "quality": {
                "title_ok": True,
                "data_signal": True,
                "local_images": 1,
            },
        }

    @patch(
        "qt6.acquisition_runtime._deep_repair_token",
        return_value="20260925130100000000",
    )
    def test_deep_repair_preserves_identity_site_receipts_and_quarantines_old_local(
        self, _token
    ):
        product_id, old_dir, _selected = self._product()
        before_receipts = [
            dict(row) for row in self.db.sync_receipts(product_id, limit=20)
        ]
        with patch(
            "qt6.acquisition_runtime._collect_one_adaptive",
            new=AsyncMock(side_effect=self._fresh_result),
        ):
            result = acquisition_runtime.deep_repair_product_from_source(
                self.db,
                product_id,
                image_limit=5,
            )
        row = dict(self.db.product(product_id))
        self.assertTrue(result["deep_repair"])
        self.assertEqual(result["product_id"], product_id)
        self.assertEqual(result["source_identity"], "makerworld:520040")
        self.assertTrue(result["site_authority_preserved"])
        self.assertTrue(result["receipts_preserved"])
        self.assertEqual(row["external_id"], "520040")
        self.assertEqual(int(row["server_product_id"]), 39)
        self.assertEqual(int(row["server_product_revision"]), 11)
        self.assertEqual(row["title_fa"], "عنوان اپراتور")
        self.assertEqual(int(row["final_price"]), 910000)
        self.assertIn("_deep_repair_20260925130100000000", row["local_dir"])
        self.assertFalse(old_dir.exists())
        quarantine = Path(result["quarantine"]["to"])
        self.assertTrue((quarantine / "images" / "old.jpg").is_file())
        backup = Path(result["rollback"]["catalog"])
        self.assertTrue(backup.is_file())
        backup_db = sqlite3.connect(str(backup))
        try:
            check = backup_db.execute("PRAGMA quick_check").fetchone()[0]
        finally:
            backup_db.close()
        self.assertEqual(check, "ok")
        after_receipts = [
            dict(row) for row in self.db.sync_receipts(product_id, limit=20)
        ]
        self.assertEqual(after_receipts, before_receipts)
        selected = json.loads(row["selected_images_json"])
        self.assertEqual(len(selected), 1)
        self.assertNotIn("?old=1", selected[0])
        history = self.db.history(product_id, limit=5)
        self.assertEqual(history[0]["event_type"], "source_product_deep_repair")
        self.assertIn("site_authority_preserved=True", history[0]["note"])

    def test_deep_repair_blocks_source_identity_mismatch_before_backup_or_fetch(self):
        product_id, old_dir, _selected = self._product("520041")
        self.db.update_product(product_id, {
            "source_url": "https://makerworld.com/en/models/999999-wrong-product",
        })
        with patch(
            "qt6.acquisition_runtime._collect_one_adaptive",
            new=AsyncMock(side_effect=AssertionError("must not fetch")),
        ):
            with self.assertRaisesRegex(RuntimeError, "does not match"):
                acquisition_runtime.deep_repair_product_from_source(
                    self.db, product_id, image_limit=5
                )
        self.assertTrue(old_dir.is_dir())
        backup_root = self.root / "data" / "repair_backups"
        self.assertFalse(backup_root.exists())

    def test_deep_repair_blocks_operator_owned_local_media(self):
        product_id, old_dir, _selected = self._product("520042")
        manual = old_dir / "images" / "manual-01.webp"
        Image.new("RGB", (200, 200), "white").save(manual, format="WEBP")
        self.db.update_product(product_id, {
            "images_json": json.dumps(["local://manual-01.webp"]),
            "selected_images_json": json.dumps(["local://manual-01.webp"]),
            "primary_image_url": "local://manual-01.webp",
        })
        with patch(
            "qt6.acquisition_runtime._collect_one_adaptive",
            new=AsyncMock(side_effect=AssertionError("must not fetch")),
        ):
            with self.assertRaisesRegex(RuntimeError, "operator-owned"):
                acquisition_runtime.deep_repair_product_from_source(
                    self.db, product_id, image_limit=5
                )
        self.assertTrue(manual.is_file())

    @patch(
        "qt6.acquisition_runtime._deep_repair_token",
        return_value="20260925130200000000",
    )
    def test_failed_fresh_acquisition_keeps_old_product_and_cleans_partial_output(
        self, _token
    ):
        product_id, old_dir, _selected = self._product("520043")
        before = dict(self.db.product(product_id))

        async def fail_after_partial(_db, _source_cfg, *, local_dir, **_kwargs):
            partial = Path(local_dir)
            partial.mkdir(parents=True, exist_ok=True)
            (partial / "partial.tmp").write_text("partial", encoding="utf-8")
            raise acquisition_runtime.AcquisitionQualityError("bad source")

        with patch(
            "qt6.acquisition_runtime._collect_one_adaptive",
            new=AsyncMock(side_effect=fail_after_partial),
        ):
            with self.assertRaises(acquisition_runtime.AcquisitionQualityError):
                acquisition_runtime.deep_repair_product_from_source(
                    self.db, product_id, image_limit=5
                )

        after = dict(self.db.product(product_id))
        self.assertEqual(after["local_dir"], before["local_dir"])
        self.assertEqual(after["server_ack_json"], before["server_ack_json"])
        self.assertTrue(old_dir.is_dir())
        partial = (
            self.root
            / "data"
            / "collected"
            / "makerworld"
            / "520043_deep_repair_20260925130200000000"
        )
        self.assertFalse(partial.exists())
        backups = list((self.root / "data" / "repair_backups").glob("*/catalog-before-deep-repair.sqlite3"))
        self.assertEqual(len(backups), 1)

    @patch(
        "qt6.acquisition_runtime._deep_repair_token",
        return_value="20260925130300000000",
    )
    def test_missing_operator_selected_source_media_fails_closed_without_db_mutation(
        self, _token
    ):
        product_id, old_dir, selected = self._product("520044")
        before = dict(self.db.product(product_id))

        async def other_media(_db, _source_cfg, *, external_id, url, local_dir, **_kwargs):
            local_dir = Path(local_dir)
            images = local_dir / "images"
            images.mkdir(parents=True, exist_ok=True)
            image_file = images / "other.webp"
            Image.new("RGB", (400, 300), "white").save(image_file, format="WEBP")
            fresh_url = (
                "https://makerworld.bblmw.com/makerworld/model/"
                f"{external_id}/design/2026/09/different.webp"
            )
            return {
                "source_payload": {
                    "source_code": "makerworld",
                    "external_id": external_id,
                    "source_url": url,
                    "source_title": "Fresh Other",
                    "source_description": "Fresh other usable description",
                    "images_json": json.dumps([fresh_url]),
                    "selected_images_json": json.dumps([fresh_url]),
                    "primary_image_url": fresh_url,
                    "local_dir": str(local_dir),
                },
                "images_found": 1,
                "images_saved": 1,
                "selected_method": "rich",
                "attempted_methods": ["rich"],
                "fallback_used": False,
                "quality": {"title_ok": True, "data_signal": True, "local_images": 1},
            }

        with patch(
            "qt6.acquisition_runtime._collect_one_adaptive",
            new=AsyncMock(side_effect=other_media),
        ):
            with self.assertRaisesRegex(RuntimeError, "operator-selected media"):
                acquisition_runtime.deep_repair_product_from_source(
                    self.db, product_id, image_limit=5
                )
        after = dict(self.db.product(product_id))
        self.assertEqual(after["selected_images_json"], before["selected_images_json"])
        self.assertIn("?old=1", selected)
        self.assertTrue(old_dir.is_dir())
        partial = (
            self.root
            / "data"
            / "collected"
            / "makerworld"
            / "520044_deep_repair_20260925130300000000"
        )
        self.assertFalse(partial.exists())

    def test_product_wizard_exposes_confirmed_deep_repair_action(self):
        product_id, _old_dir, _selected = self._product("520045")
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            buttons = {
                button.text(): button
                for button in page.findChildren(QPushButton)
            }
            self.assertIn("بازیابی عمیق از صفر", buttons)
            self.assertTrue(buttons["بازیابی عمیق از صفر"].property("danger"))
            self.assertIn(
                "rollback quarantine",
                buttons["بازیابی عمیق از صفر"].toolTip(),
            )
            with patch.object(
                QMessageBox,
                "question",
                return_value=QMessageBox.StandardButton.Yes,
            ), patch.object(page, "_start_image_task") as start:
                page._deep_repair_product()
            self.assertEqual(start.call_count, 1)
            task = start.call_args.args[1]
            with patch.object(
                self.kernel.acquisition,
                "deep_repair_product",
                return_value={"deep_repair": True},
            ) as deep:
                task(None)
            deep.assert_called_once_with(
                product_id,
                image_limit=page.image_recover_limit.value(),
                progress=None,
            )
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
