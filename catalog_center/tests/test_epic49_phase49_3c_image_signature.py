from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from app.phase49_3c_image_pipeline import finalize_selected_images, image_metadata_missing


class Phase493CImageSignatureTests(unittest.TestCase):
    def test_seo_edit_after_finalize_requires_metadata_refresh(self):
        class FakeDB:
            def __init__(self, row):
                self.row = row
                self.conn = sqlite3.connect(":memory:")
                self.conn.row_factory = sqlite3.Row
                self.conn.execute(
                    "CREATE TABLE products(id INTEGER PRIMARY KEY, image_metadata_json TEXT NOT NULL DEFAULT '[]')"
                )
                self.conn.commit()

            def product(self, product_id):
                return self.row if int(product_id) == int(self.row["id"]) else None

            def update_product(self, product_id, values):
                self.row.update(values)

            def setting(self, key, default=""):
                return "QA Operator" if key == "operator_name" else default

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image_dir = root / "images"
            image_dir.mkdir()
            source = image_dir / "source.jpg"
            Image.new("RGB", (80, 80), (120, 80, 40)).save(source)
            url = "https://cdn.example.test/product.jpg"
            (root / "page_extract.json").write_text(
                json.dumps({"images": [{"url": url, "local_file": str(source)}]}),
                encoding="utf-8",
            )
            row = {
                "id": 1,
                "local_dir": str(root),
                "source_title": "Gear Cover",
                "title_fa": "کاور چرخ دنده",
                "short_description_fa": "قطعه چاپ سه‌بعدی",
                "seo_title_fa": "خرید کاور چرخ دنده",
                "seo_description_fa": "سفارش چاپ سه‌بعدی کاور چرخ دنده",
                "keywords_json": json.dumps(["خرید کاور چرخ دنده"]),
                "tags_fa_json": json.dumps(["چرخ دنده"]),
                "hashtags_fa_json": json.dumps(["#چاپ_سه_بعدی"]),
                "image_alt_texts_json": json.dumps(["کاور چرخ دنده - نمای اصلی"]),
                "author_name": "Original Designer",
                "source_name": "MakerWorld",
                "source_code": "makerworld",
                "source_url": "https://makerworld.com/model/1",
                "license_name": "Creator License",
                "license_url": "https://example.test/license",
                "commercial_status": "allowed",
                "images_json": json.dumps([url]),
                "selected_images_json": json.dumps([url]),
                "primary_image_url": url,
                "image_metadata_json": "[]",
            }
            db = FakeDB(row)
            try:
                finalize_selected_images(db, 1)
                self.assertEqual(image_metadata_missing(row), [])
                row["seo_title_fa"] = "عنوان SEO جدید"
                missing = image_metadata_missing(row)
            finally:
                db.conn.close()

            self.assertTrue(
                any("بروزرسانی Metadata تصویر" in item for item in missing),
                missing,
            )


if __name__ == "__main__":
    unittest.main()
