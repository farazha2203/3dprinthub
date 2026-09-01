from __future__ import annotations

import json
import os
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.db import Database
from qt6.kernel import build_kernel
from qt6.product_wizard import ProductWizardPage


class Phase493I48OwnerFilamentSiteFoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = Database(self.root / "catalog.sqlite3")
        self.db.upsert_source(
            {
                "code": "makerworld",
                "name": "MakerWorld",
                "enabled": 1,
                "methods": ["browser", "http"],
                "listing_urls": ["https://makerworld.com/en/search/models?keyword={query}"],
                "model_url_pattern": (
                    r"https?://(?:www\\.)?makerworld\\.com/"
                    r"(?:[a-z]{2}/)?models/(?P<external_id>\\d+)"
                ),
                "requires_login": False,
                "reference_only": False,
            }
        )
        self.kernel = build_kernel(self.db)

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def _make_product(
        self,
        external_id: str,
        *,
        local_dir: Path | None = None,
        image_url: str = "",
    ) -> int:
        urls = [image_url] if image_url else []
        self.db.upsert_product(
            {
                "source_code": "makerworld",
                "external_id": external_id,
                "source_url": f"https://makerworld.com/en/models/{external_id}-owner",
                "source_title": "Owner Test Product",
                "source_short_description": "heavy source description",
                "source_description": "heavy source description",
                "title_fa": "محصول تست مالک",
                "short_description_fa": "توضیح فارسی سنگین",
                "description_fa": "توضیح فارسی سنگین",
                "workflow_status": "review",
                "local_dir": str(local_dir or ""),
                "images_json": json.dumps(urls, ensure_ascii=False),
                "selected_images_json": json.dumps(urls, ensure_ascii=False),
                "primary_image_url": image_url,
                "image_alt_texts_json": json.dumps(
                    ["محصول تست مالک"] if image_url else [],
                    ensure_ascii=False,
                ),
                "suggested_price": 900000,
                "final_price": 950000,
                "price_is_final": 1,
            }
        )
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("makerworld", external_id),
        ).fetchone()
        return int(row["id"])

    def test_stage5_is_owner_approved_and_auto_finalizes_green(self):
        product_id = self._make_product("3148001")
        row = dict(self.db.product(product_id))
        self.assertEqual(int(row["source_license_owner_approved"]), 1)

        specs = next(
            item
            for item in self.kernel.stages.statuses(product_id)
            if item["stage"] == "specs"
        )
        self.assertTrue(specs["data_ready"])

        result = self.kernel.stages.auto_finalize_ready(
            product_id,
            {"specs"},
        )
        self.assertIn("specs", result["finalized"])
        specs_after = next(
            item
            for item in self.kernel.stages.statuses(product_id)
            if item["stage"] == "specs"
        )
        self.assertTrue(specs_after["finalized"])
        self.assertEqual(specs_after["status"], "finalized")

    def test_reject_keeps_link_title_and_one_thumbnail_but_purges_heavy_state(self):
        local_dir = self.root / "collected" / "makerworld" / "3148002"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        source_image = image_dir / "source.jpg"
        Image.new("RGB", (500, 360), "white").save(source_image, "JPEG")
        url = "https://cdn.example.com/owner-product.jpg"
        (local_dir / "page_extract.json").write_text(
            json.dumps(
                {"images": [{"url": url, "local_file": str(source_image)}]},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        product_id = self._make_product(
            "3148002",
            local_dir=local_dir,
            image_url=url,
        )

        self.assertEqual(self.kernel.products.remove_many([product_id]), 1)
        row = dict(self.db.product(product_id))

        self.assertEqual(int(row["is_blocked"]), 1)
        self.assertEqual(row["workflow_status"], "blocked")
        self.assertTrue(row["source_url"].endswith("3148002-owner"))
        self.assertEqual(row["title_fa"], "محصول تست مالک")
        self.assertTrue(row["blocked_at"])
        self.assertTrue(row["blocked_reason"])

        thumbnail = Path(str(row["rejected_thumbnail_path"] or ""))
        self.assertTrue(thumbnail.is_file())
        self.assertEqual(thumbnail.suffix.lower(), ".webp")
        self.assertEqual(self.kernel.images.image_count(row), 1)

        self.assertEqual(row["images_json"], "[]")
        self.assertEqual(row["selected_images_json"], "[]")
        self.assertEqual(row["primary_image_url"], "")
        self.assertEqual(row["local_dir"], "")
        self.assertEqual(row["description_fa"], "")
        self.assertEqual(int(row["final_price"]), 0)
        self.assertFalse(local_dir.exists())

    def test_filament_brand_palette_finish_image_and_roll_price_are_authoritative(self):
        source = self.root / "filament-source.jpg"
        Image.new("RGB", (900, 900), "pink").save(source, "JPEG")

        saved = self.kernel.filaments.save(
            {
                "material": "PLA",
                "brand": "Bambu Lab",
                "manufacturer": "Legacy Company Must Not Win",
                "color": "Pink Dual",
                "color_type": "dual",
                "color_finish": "glossy",
                "palette_hexes": ["#F15D9C", "#7C3AED"],
                "roll_weight_grams": 750,
                "stock_roll_count": 2.5,
                "purchase_price_per_roll": 2_100_000,
                "sale_price_per_roll": 3_000_000,
                "usd_price_per_roll": 999,
                "usd_fx_rate_toman": 999999,
                "filament_image_path": str(source),
            }
        )

        self.assertEqual(saved["brand_name"], "Bambu Lab")
        self.assertEqual(saved["manufacturer_name"], "Bambu Lab")
        self.assertEqual(saved["color_type"], "dual")
        self.assertEqual(saved["color_finish"], "glossy")
        self.assertEqual(
            json.loads(saved["palette_hex_json"]),
            ["#F15D9C", "#7C3AED"],
        )
        self.assertEqual(
            Decimal(str(saved["effective_sale_price_per_gram"])),
            Decimal("4000"),
        )
        image_path = Path(saved["filament_image_path"])
        self.assertTrue(image_path.is_file())
        self.assertEqual(image_path.suffix.lower(), ".webp")

        listed = self.kernel.filaments.list()
        item = next(
            row for row in listed
            if row["color_name"] == "Pink Dual"
            and row["brand_name"] == "Bambu Lab"
        )
        self.assertEqual(item["manufacturer_name"], "Bambu Lab")
        self.assertEqual(item["brand_name"], "Bambu Lab")
        self.assertEqual(
            json.loads(item["palette_hex_json"]),
            ["#F15D9C", "#7C3AED"],
        )
        self.assertEqual(float(item["effective_sale_price_per_gram"]), 4000.0)

    def test_stage3_save_does_not_cross_write_locked_slider_stage(self):
        product_id = self._make_product("3148003")
        self.kernel.stages.finalize(
            product_id,
            "slider",
            manual_approval=False,
        )
        before = dict(self.db.product(product_id))

        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            page._save_stage3()
        finally:
            page.close()

        after = dict(self.db.product(product_id))
        self.assertEqual(
            before["homepage_slider_enabled"],
            after["homepage_slider_enabled"],
        )
        self.assertEqual(
            before["homepage_slider_image_url"],
            after["homepage_slider_image_url"],
        )
        slider = next(
            item
            for item in self.kernel.stages.statuses(product_id)
            if item["stage"] == "slider"
        )
        self.assertTrue(slider["finalized"])

    def test_full_ai_postprocess_marks_product_and_source_mode(self):
        product_id = self._make_product("3148004")
        self.kernel.providers.active = lambda: {
            "provider": "test-provider",
            "model": "test-model",
        }

        result = self.kernel.postprocess_full_product_ai(
            product_id,
            {"requested_source_mode": "link"},
        )
        row = dict(self.db.product(product_id))

        self.assertTrue(result["ai_completed_once"])
        self.assertEqual(int(row["ai_completed_once"]), 1)
        self.assertEqual(row["ai_completed_source_mode"], "link")
        self.assertEqual(row["ai_completed_provider"], "test-provider")
        self.assertEqual(row["ai_completed_model"], "test-model")
        self.assertTrue(row["ai_completed_at"])


if __name__ == "__main__":
    unittest.main()
