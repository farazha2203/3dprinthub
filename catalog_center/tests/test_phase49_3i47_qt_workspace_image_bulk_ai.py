from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.db import Database
from qt6.kernel import AICore, build_kernel
from qt6.pages import OperationsPage, ProductsPage
from qt6.parity_dialogs import ProfileEditorDialog
from qt6.product_explorer import ProductGalleryModel


class Phase493I47QtWorkspaceImageBulkAITests(unittest.TestCase):
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
                "methods": ["browser", "http", "sitemap"],
                "listing_urls": [
                    "https://makerworld.com/en/search/models?keyword={query}"
                ],
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
        title: str = "چراغ رومیزی",
        source_title: str = "Table Lamp",
        description: str = "چراغ رومیزی دکوراتیو چاپ سه بعدی",
        local_dir: Path | None = None,
        urls: list[str] | None = None,
    ) -> int:
        urls = list(urls or [])
        self.db.upsert_product(
            {
                "source_code": "makerworld",
                "external_id": external_id,
                "source_url": f"https://makerworld.com/en/models/{external_id}-test",
                "source_title": source_title,
                "source_short_description": description,
                "source_description": description,
                "title_fa": title,
                "short_description_fa": description,
                "description_fa": description,
                "seo_title_fa": title + " چاپ سه بعدی",
                "seo_description_fa": description,
                "workflow_status": "review",
                "local_dir": str(local_dir or ""),
                "images_json": json.dumps(urls, ensure_ascii=False),
                "selected_images_json": json.dumps(urls, ensure_ascii=False),
                "primary_image_url": urls[0] if urls else "",
                "image_alt_texts_json": json.dumps(
                    [title for _ in urls],
                    ensure_ascii=False,
                ),
            }
        )
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("makerworld", external_id),
        ).fetchone()
        return int(row["id"])

    def _mapped_image_product(self) -> tuple[int, list[str], Path]:
        local_dir = self.root / "image-product"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        urls = []
        extract_images = []
        for index in range(1, 4):
            url = f"https://cdn.example.com/lamp-{index}.jpg"
            path = image_dir / f"source-{index}.jpg"
            Image.new("RGB", (640 + index, 480 + index), "white").save(
                path,
                format="JPEG",
            )
            urls.append(url)
            extract_images.append({"url": url, "local_file": str(path)})
        (local_dir / "page_extract.json").write_text(
            json.dumps({"images": extract_images}, ensure_ascii=False),
            encoding="utf-8",
        )
        product_id = self._make_product(
            "3147001",
            local_dir=local_dir,
            urls=urls,
        )
        return product_id, urls, local_dir

    def test_multi_image_seo_uses_one_semantic_set_and_unique_numbered_files(self):
        product_id, urls, local_dir = self._mapped_image_product()

        self.kernel.images.update_metadata(
            product_id,
            urls,
            {
                "alt_text": "چراغ رومیزی ارگانیک چاپ سه بعدی",
                "title": "چراغ رومیزی ارگانیک",
                "caption": "چراغ رومیزی ارگانیک چاپ سه بعدی",
                "keywords": ["چراغ رومیزی", "چاپ سه بعدی"],
                "seo_filename": "organic-table-lamp.webp",
            },
        )

        row = dict(self.db.product(product_id))
        metadata = json.loads(row["image_metadata_json"])
        self.assertEqual(len(metadata), 3)
        filenames = [item["seo_filename"] for item in metadata]
        self.assertEqual(
            filenames,
            [
                "organic-table-lamp-01.webp",
                "organic-table-lamp-02.webp",
                "organic-table-lamp-03.webp",
            ],
        )
        self.assertEqual(len(set(filenames)), 3)

        for filename in filenames:
            self.assertTrue((local_dir / "seo_images" / filename).is_file())

        self.assertEqual(
            {item["alt_text"] for item in metadata},
            {"چراغ رومیزی ارگانیک چاپ سه بعدی"},
        )
        self.assertEqual(
            {item["title"] for item in metadata},
            {"چراغ رومیزی ارگانیک"},
        )
        self.assertEqual(
            {item["caption"] for item in metadata},
            {"چراغ رومیزی ارگانیک چاپ سه بعدی"},
        )
        self.assertEqual(
            {tuple(item["keywords"]) for item in metadata},
            {("چراغ رومیزی", "چاپ سه بعدی")},
        )

    def test_legacy_product_without_url_mapping_still_shows_local_image(self):
        local_dir = self.root / "legacy-product"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        legacy = image_dir / "old-local-preview.jpg"
        Image.new("RGB", (300, 200), "white").save(legacy, format="JPEG")

        product_id = self._make_product(
            "3147002",
            local_dir=local_dir,
            urls=[],
        )
        row = self.kernel.products.get(product_id)

        self.assertEqual(
            Path(self.kernel.images.preferred_local_path(row)),
            legacy.resolve(),
        )
        self.assertEqual(self.kernel.images.image_count(row), 1)

        model = ProductGalleryModel(
            self.kernel.products,
            self.kernel.images,
        )
        display = str(
            model.data(
                model.index(0, 0),
                Qt.ItemDataRole.DisplayRole,
            )
        )
        self.assertIn("🖼 1", display)
        self.assertIn("چراغ رومیزی", display)

    def test_acquisition_inventory_is_tabbed_and_has_windows_like_views(self):
        local_dir = self.root / "queue-product"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (320, 240), "white").save(
            image_dir / "preview.jpg",
            format="JPEG",
        )
        external_id = "3147003"
        product_id = self._make_product(
            external_id,
            local_dir=local_dir,
            urls=[],
            description="توضیح محصول دریافت‌شده برای نمایش در موجودی",
        )
        self.db.add_discovered(
            "makerworld",
            external_id,
            f"https://makerworld.com/en/models/{external_id}-queue",
            "phase49-3i47-test",
        )

        page = OperationsPage(self.db, kernel=self.kernel)
        try:
            page.refresh()
            self.assertEqual(page.workspace_tabs.count(), 3)
            self.assertEqual(page.workspace_tabs.currentIndex(), 0)
            self.assertEqual(page.queue_views.count(), 2)
            self.assertEqual(page.queue_gallery.count(), 1)
            self.assertEqual(page.queue_table.rowCount(), 1)
            text = page.queue_gallery.item(0).text()
            self.assertIn("🖼 1", text)
            self.assertIn("توضیح محصول دریافت‌شده", text)
            self.assertEqual(
                int(page._queue_rows_by_id[
                    int(page.queue_gallery.item(0).data(Qt.ItemDataRole.UserRole))
                ]["product_id"]),
                product_id,
            )
        finally:
            page.close()

    def test_profile_editor_uses_three_full_height_tabs(self):
        profile = {
            "name": "سایز 20",
            "size_label": "20 cm",
            "part_length_cm": 20,
            "part_width_cm": 15,
            "part_height_cm": 8,
            "pricing_strategy": "dynamic",
            "production_rows": [
                {
                    "weight_grams": 80,
                    "support_weight_grams": 5,
                    "print_time_minutes": 120,
                },
                {
                    "weight_grams": 95,
                    "support_weight_grams": 8,
                    "print_time_minutes": 145,
                },
            ],
            "material_options": [],
        }
        dialog = ProfileEditorDialog([], profile)
        try:
            self.assertEqual(dialog.profile_tabs.count(), 3)
            self.assertEqual(
                [dialog.profile_tabs.tabText(i) for i in range(3)],
                [
                    "پروفایل و روش قیمت",
                    "وزن و زمان تولید",
                    "فیلامنت، رنگ و قیمت قطعی",
                ],
            )
            self.assertEqual(dialog.production.rowCount(), 2)
            self.assertGreaterEqual(dialog.production.minimumHeight(), 430)
            self.assertGreaterEqual(dialog.filament_table.minimumHeight(), 470)
        finally:
            dialog.close()

    def test_ai_core_executes_multi_product_batch_sequentially_under_one_core(self):
        core = AICore()
        calls: list[int] = []

        def fake_executor(
            product_id,
            mode,
            *,
            target_stage=None,
            refresh_existing=False,
        ):
            calls.append(int(product_id))
            return {
                "product_id": int(product_id),
                "mode": mode,
                "target_stage": target_stage,
                "refresh_existing": refresh_existing,
            }

        core.bind_executor(fake_executor)
        result = core.execute_many(
            [
                {"product_id": 7, "mode": "data", "refresh_existing": True},
                {"product_id": 8, "mode": "data", "refresh_existing": True},
                {"product_id": 9, "mode": "data", "refresh_existing": True},
            ]
        )
        self.assertEqual(calls, [7, 8, 9])
        self.assertTrue(all(item["ok"] for item in result))

    def test_products_page_exposes_lifecycle_tabs_and_bulk_ai_action(self):
        self._make_product("3147004")
        page = ProductsPage(
            self.db,
            lambda _product_id: None,
            kernel=self.kernel,
        )
        try:
            self.assertEqual(
                [page.lifecycle_tabs.tabText(i) for i in range(4)],
                [
                    "محصولات فعال",
                    "ارسال / منتشرشده",
                    "آرشیو شده",
                    "حذف / رد شده",
                ],
            )
            self.assertIn(
                "AI تکمیل همه موارد",
                page.bulk_ai_btn.text(),
            )
            self.assertGreaterEqual(page.bulk_ai_source.count(), 2)
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
