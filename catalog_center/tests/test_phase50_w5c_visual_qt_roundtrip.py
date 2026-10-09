"""W5C actual Qt gallery rendering and QTest click/delete/reopen smoke.

Run normally with unittest: uses a freshly created synthetic SQLite Catalog.
Optional protected external QA run (never on the real Catalog):
W5C_QA_CLONE_ROOT=<verified independent clone directory>
W5C_QA_CLONE_EXPECT_SHA256=<exact pre-run clone SHA256>
This writes *only* a synthetic Product and its images under that QA directory.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton

from app.db import Database
from app.phase50_a2w_media_sync import selected_local_media
from qt6.kernel import build_kernel
from qt6.product_wizard import ProductWizardPage


COLORS = (
    (228, 38, 40),
    (42, 178, 52),
    (46, 70, 221),
    (226, 183, 46),
)
EXPECTED_CATALOG = (
    Path("D:/projects/3dprinthub-catalog-manager/catalog.sqlite3").resolve()
)


class W5CVisualQTRoundTrip(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def setUp(self):
        self.temp = None
        self.qa = os.environ.get("W5C_QA_CLONE_ROOT", "").strip()
        if self.qa:
            self.root = Path(self.qa).resolve()
            path = self.root / "catalog.sqlite3"
            assert self.root.is_dir() and path.is_file()
            assert path.resolve() != EXPECTED_CATALOG, "NEVER USE CANONICAL CATALOG"
            assert "3dprinthub-backups" in self.root.parts
            assert self.root.name.startswith("phase50-w5c-visual-")
            expect = os.environ.get("W5C_QA_CLONE_EXPECT_SHA256", "").lower()
            assert len(expect) == 64 and all(x in "0123456789abcdef" for x in expect)
            with path.open("rb") as stream:
                actual = hashlib.file_digest(stream, "sha256").hexdigest()
            assert actual == expect, "DISPOSABLE CATALOG HASH HAS CHANGED; STOP"
            readonly = Database(self.root / "catalog.sqlite3")
            self.assertEqual(readonly.conn.execute("PRAGMA quick_check").fetchone()[0], "ok")
            self.assertEqual(readonly.conn.execute("select count(*) from products").fetchone()[0], 1076)
            readonly.close()
            print("W5C_QA_CLONE_VERIFIED_BEFORE_WRITE=PASS", flush=True)
        else:
            self.temp = tempfile.TemporaryDirectory(prefix="w5c-qt-visual-")
            self.root = Path(self.temp.name)
        self.db = Database(self.root / "catalog.sqlite3")
        self.db.upsert_source({
            "code": "makerworld", "name": "MakerWorld", "enabled": 1,
            "methods": ["http"], "listing_urls": [],
            "model_url_pattern": "", "requires_login": False,
            "reference_only": False,
        })
        self.kernel = build_kernel(self.db)
        self.page = None

    def tearDown(self):
        if self.page is not None:
            self.page.close()
            self.app.processEvents()
        self.db.close()
        if self.temp is not None:
            self.temp.cleanup()

    def make_visual_product(self):
        source = self.root / "qa-synthetic-product-visual"
        images = source / "images"
        images.mkdir(parents=True, exist_ok=True)
        urls = []
        metadata = []
        for n, color in enumerate(COLORS, 1):
            uri = f"https://makerworld.com/media/w5c-visual-{n}.jpg"
            path = images / f"qa-{n:02d}.jpg"
            Image.new("RGB", (360, 220), color).save(path, "JPEG", quality=98)
            urls.append(uri)
            metadata.append({"url": uri, "local_file": str(path)})
        (source / "page_extract.json").write_text(
            json.dumps({"images": metadata}), encoding="utf-8"
        )
        key = "9910202609"
        old = self.db.conn.execute(
            "select id from products where source_code=? and external_id=?",
            ("makerworld", key),
        ).fetchone()
        self.assertIsNone(old, "QA synthetic fixture is present: don't overwrite")
        self.db.upsert_product({
            "source_code": "makerworld", "external_id": key,
            "source_url": "https://makerworld.com/en/models/9910202609-w5c",
            "source_title": "W5C Disposable Visual Check",
            "title_fa": "آزمون تصویری گالری",
            "local_dir": str(source),
            "workflow_status": "review",
            "images_json": json.dumps(urls),
            "selected_images_json": json.dumps(urls),
            "primary_image_url": urls[0],
        })
        product_id = int(self.db.conn.execute(
            "select id from products where source_code=? and external_id=?",
            ("makerworld", key),
        ).fetchone()[0])
        self.kernel.images.finalize(product_id)
        return product_id, urls

    def capture(self, name):
        self.app.processEvents()
        QTest.qWait(60)
        pix = self.page.image_grid.grab()
        self.assertFalse(pix.isNull())
        # The screenshot is an inspectable local QA artifact, not production media.
        evidence = os.environ.get("W5C_EVIDENCE_ROOT", "").strip()
        if evidence:
            destination = Path(evidence).resolve()
            assert "3dprinthub-backups" in destination.parts
            assert "phase50-w5c-visual-" in str(destination)
        else:
            destination = self.root / "evidence"
        path = destination / f"{name}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.assertTrue(pix.save(str(path), "PNG"))
        print(f"W5C_SCREENSHOT_{name.upper()}={path}", flush=True)
        return path

    def assert_visual_cards(self, urls, allowed):
        cards = {str(card.item["url"]): card for card in self.page.image_grid.cards}
        self.assertEqual(set(cards), set(allowed))
        for url in allowed:
            card = cards[url]
            self.assertFalse(card.preview.pixmap().isNull(), url)
            color = card.preview.pixmap().toImage().pixelColor(
                card.preview.pixmap().width() // 2,
                card.preview.pixmap().height() // 2,
            )
            expected = COLORS[urls.index(url)]
            self.assertLessEqual(
                max(abs(x - y) for x, y in zip(color.toTuple()[:3], expected)),
                32,
                f"visible on-card pixels mismatch {url}",
            )
            final_file = Path(card.item["path"])
            self.assertTrue(final_file.is_file())
            with Image.open(final_file) as image:
                real = image.convert("RGB").getpixel((image.width // 2, image.height // 2))
            self.assertLessEqual(
                max(abs(x - y) for x, y in zip(real, expected)), 32, url
            )
        return cards

    def test_real_qt_render_click_bulk_delete_reopen_media_parity(self):
        product_id, urls = self.make_visual_product()
        self.page = ProductWizardPage(self.db, kernel=self.kernel)
        self.page.resize(1770, 1050)
        self.page.load_product(product_id)
        self.page._set_stage(2)
        self.page.show()
        self.app.processEvents()
        self.assertTrue(self.page.image_grid.isVisible())
        cards = self.assert_visual_cards(urls, urls)
        self.capture("01_before")

        # QTest performs real QWidget preview clicks, not direct setChecked calls.
        for url in (urls[1], urls[3]):
            QTest.mouseClick(cards[url].preview, Qt.MouseButton.LeftButton)
            self.app.processEvents()
            self.assertTrue(cards[url].bulk_selected.isChecked())
        self.assertEqual(self.page.image_grid.operation_urls(), [urls[1], urls[3]])
        self.capture("02_selected")

        delete = next(
            b for b in self.page.image_stage3_toolbar_buttons
            if b.text() == "حذف انتخابی"
        )
        with patch(
            "qt6.product_wizard.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            QTest.mouseClick(delete, Qt.MouseButton.LeftButton)
            self.app.processEvents()
        kept = [urls[0], urls[2]]
        row = dict(self.db.product(product_id))
        self.assertEqual(json.loads(row["images_json"]), kept)
        self.assertEqual(json.loads(row["selected_images_json"]), kept)
        cards_after = self.assert_visual_cards(urls, kept)
        published = {
            item["source_url"]: Path(item["local_path"]).resolve()
            for item in selected_local_media(row)
        }
        self.assertEqual(
            published,
            {url: Path(card.item["path"]).resolve() for url, card in cards_after.items()},
        )
        self.capture("03_after_delete")

        self.page.close()
        self.app.processEvents()
        self.page = ProductWizardPage(self.db, kernel=self.kernel)
        self.page.resize(1770, 1050)
        self.page.load_product(product_id)
        self.page._set_stage(2)
        self.page.show()
        self.app.processEvents()
        self.assert_visual_cards(urls, kept)
        self.capture("04_reopened")
        self.assertEqual(
            self.db.conn.execute("PRAGMA quick_check").fetchone()[0], "ok"
        )
        print("W5C_QT_PREVIEW_CLICK_DELETE_REOPEN_MEDIA_PARITY=PASS", flush=True)

    def test_twenty_cards_scroll_and_click_last_actual_qt_image(self):
        # This covers the owner-facing lower rows rather than a 4-card shortcut.
        product_id, urls = self.make_visual_product()
        row = dict(self.db.product(product_id))
        local_dir = Path(row["local_dir"])
        extract = json.loads((local_dir / "page_extract.json").read_text("utf-8"))
        for n in range(5, 21):
            uri = f"https://makerworld.com/media/w5c-visual-{n}.jpg"
            path = local_dir / "images" / f"qa-{n:02d}.jpg"
            Image.new("RGB", (360, 220), (
                (n * 13) % 235 + 10, (n * 31) % 235 + 10, (n * 47) % 235 + 10
            )).save(path, "JPEG", quality=98)
            urls.append(uri)
            extract["images"].append({"url": uri, "local_file": str(path)})
        (local_dir / "page_extract.json").write_text(
            json.dumps(extract), encoding="utf-8"
        )
        self.db.update_product(product_id, {
            "images_json": json.dumps(urls),
            "selected_images_json": json.dumps(urls),
        })
        self.kernel.images.finalize(product_id)

        self.page = ProductWizardPage(self.db, kernel=self.kernel)
        self.page.resize(1780, 1080)
        self.page.load_product(product_id)
        self.page._set_stage(2)
        self.page.show()
        self.app.processEvents()
        self.assertEqual(len(self.page.image_grid.cards), 20)
        grid = self.page.image_grid
        bar = grid.scroll.verticalScrollBar()
        self.assertGreater(bar.maximum(), 0, "20 cards must scroll down")
        bar.setValue(0)
        self.app.processEvents()
        self.capture("05_twenty_top")
        last = next(c for c in grid.cards if c.item.get("url") == urls[19])
        grid.scroll.ensureWidgetVisible(last.preview)
        self.app.processEvents()
        self.assertGreater(bar.value(), 0, "last card must be reachable")
        self.assertFalse(last.preview.pixmap().isNull())
        QTest.mouseClick(last.preview, Qt.MouseButton.LeftButton)
        self.app.processEvents()
        self.assertTrue(last.bulk_selected.isChecked())
        self.assertEqual(grid.operation_urls(), [urls[19]])
        self.capture("06_twenty_last")
        self.assertEqual(
            len(json.loads(dict(self.db.product(product_id))["images_json"])), 20
        )
        print("W5C_20_CARD_SCROLL_LAST_PREVIEW_CLICK=PASS", flush=True)


if __name__ == "__main__":
    unittest.main()
