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
from qt6.product_explorer import ProductGalleryModel, product_lifecycle_status
from qt6.product_wizard import ProductWizardPage


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

    def test_image_reorder_preserves_url_owned_facts_and_rebuilds_numbered_seo(self):
        product_id, urls, _local_dir = self._mapped_image_product()
        for index, url in enumerate(urls, start=1):
            self.kernel.images.update_metadata(
                product_id,
                [url],
                {"alt_text": f"ALT-{index}"},
            )
        self.db.update_product(
            product_id,
            {
                "homepage_slider_image_url": urls[2],
                "server_id": "site-product:901",
                "workflow_status": "uploaded",
                "needs_update": 0,
                "upload_ready": 1,
            },
        )

        moved = self.kernel.images.reorder_selected(product_id, urls[2], -1)
        self.assertTrue(moved["changed"])
        self.assertEqual(moved["order"], [urls[0], urls[2], urls[1]])

        row = dict(self.db.product(product_id))
        self.assertEqual(
            json.loads(row["selected_images_json"]),
            [urls[0], urls[2], urls[1]],
        )
        self.assertEqual(
            json.loads(row["image_alt_texts_json"]),
            ["ALT-1", "ALT-3", "ALT-2"],
        )
        self.assertEqual(row["primary_image_url"], urls[0])
        self.assertEqual(row["homepage_slider_image_url"], urls[2])
        self.assertEqual(int(row["needs_update"]), 1)
        self.assertEqual(int(row["upload_ready"]), 0)

        self.kernel.images.renumber(product_id)
        refreshed = dict(self.db.product(product_id))
        metadata = json.loads(refreshed["image_metadata_json"])
        self.assertEqual(
            [item["source_url"] for item in metadata],
            [urls[0], urls[2], urls[1]],
        )
        self.assertEqual(
            [item["alt_text"] for item in metadata],
            ["ALT-1", "ALT-3", "ALT-2"],
        )
        self.assertEqual(
            [item["seo_filename"].rsplit("-", 1)[-1] for item in metadata],
            ["01.webp", "02.webp", "03.webp"],
        )

    def test_image_stage_exposes_reorder_controls_with_primary_pinned(self):
        product_id, urls, _local_dir = self._mapped_image_product()
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            cards = {
                str(card.item.get("url") or ""): card
                for card in page.image_grid.cards
            }
            self.assertEqual(set(cards), set(urls))
            self.assertFalse(cards[urls[0]].move_earlier.isEnabled())
            self.assertFalse(cards[urls[0]].move_later.isEnabled())
            self.assertFalse(cards[urls[1]].move_earlier.isEnabled())
            self.assertTrue(cards[urls[1]].move_later.isEnabled())
            self.assertTrue(cards[urls[2]].move_earlier.isEnabled())
            self.assertFalse(cards[urls[2]].move_later.isEnabled())
            self.assertGreaterEqual(cards[urls[2]].minimumHeight(), 390)

            cards[urls[2]].move_earlier.click()
            reordered = dict(self.db.product(product_id))
            self.assertEqual(
                json.loads(reordered["selected_images_json"]),
                [urls[0], urls[2], urls[1]],
            )
            self.assertEqual(
                [item["url"] for item in self.kernel.images.local_items(product_id)],
                [urls[0], urls[2], urls[1]],
            )
            self.assertIn("شماره‌های SEO", page.image_task_status.text())
        finally:
            page.close()

    def test_full_ai_repair_rebuilds_derived_image_seo_but_preserves_operator_title(self):
        product_id, urls, _local_dir = self._mapped_image_product()
        self.kernel.images.update_metadata(
            product_id,
            [urls[0]],
            {"title": "عنوان دستی تصویر اول"},
        )
        before = json.loads(self.db.product(product_id)["image_metadata_json"])
        self.assertTrue(all(item["metadata_ready"] for item in before))

        opened = self.kernel.stages.prepare_ai_content_repair(product_id)
        self.assertEqual(opened["image_refresh"]["selected"], 3)
        staged = json.loads(self.db.product(product_id)["image_metadata_json"])
        first = next(item for item in staged if item["source_url"] == urls[0])
        second = next(item for item in staged if item["source_url"] == urls[1])
        self.assertEqual(first["title"], "عنوان دستی تصویر اول")
        self.assertIn("title", first["_operator_override_fields"])
        self.assertFalse(first["metadata_ready"])
        self.assertNotIn("title", second)
        self.assertFalse(second["metadata_ready"])

        self.kernel.stages.update(
            product_id,
            "content",
            {"seo_title_fa": "چراغ رومیزی جدید چاپ سه بعدی"},
        )
        self.kernel.images.finalize(product_id)
        refreshed = json.loads(self.db.product(product_id)["image_metadata_json"])
        first = next(item for item in refreshed if item["source_url"] == urls[0])
        second = next(item for item in refreshed if item["source_url"] == urls[1])
        self.assertEqual(first["title"], "عنوان دستی تصویر اول")
        self.assertEqual(second["title"], "چراغ رومیزی جدید چاپ سه بعدی")
        self.assertTrue(all(item["metadata_ready"] for item in refreshed))

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

    def test_published_workspace_keeps_uploaded_product_with_local_updates(self):
        product_id = self._make_product("3147010")
        self.db.update_product(
            product_id,
            {
                "server_id": "site-product:901",
                "server_status": "updated",
                "workflow_status": "uploaded",
                "needs_update": 1,
            },
        )
        row = dict(self.db.product(product_id))
        self.assertEqual(product_lifecycle_status(row), "published")
        self.assertEqual(self.db.product_count("published"), 1)

        model = ProductGalleryModel(self.kernel.products, self.kernel.images)
        model.refresh(filter_name="published")
        self.assertEqual(model.total_count, 1)
        self.assertEqual(model.rowCount(), 1)

    def test_legacy_numbered_images_render_real_files_not_sixty_placeholders(self):
        local_dir = self.root / "legacy-numbered"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        for slot in (1, 2, 4):
            Image.new("RGB", (400 + slot, 300 + slot), "white").save(
                image_dir / f"{slot:02d}.webp",
                format="WEBP",
            )
        urls = [f"https://cdn.example.com/source-{index:02d}.jpg" for index in range(1, 61)]
        product_id = self._make_product(
            "3147011",
            local_dir=local_dir,
            urls=urls,
        )
        row = dict(self.db.product(product_id))

        items = self.kernel.images.local_items(product_id)
        self.assertEqual(self.kernel.images.source_image_count(row), 60)
        self.assertEqual(self.kernel.images.image_count(row), 3)
        self.assertEqual(len(items), 3)
        self.assertTrue(all(item["downloaded"] for item in items))
        self.assertEqual(
            [item["filename"] for item in items],
            ["01.webp", "02.webp", "04.webp"],
        )
        self.assertEqual(
            [item["url"] for item in items],
            [urls[0], urls[1], urls[3]],
        )

        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            self.assertEqual(page.image_grid.columns, 4)
            self.assertEqual(len(page.image_grid.cards), 3)
            self.assertGreaterEqual(page.image_grid.cards[0].minimumWidth(), 280)
            self.assertGreaterEqual(page.image_grid.cards[0].preview.minimumHeight(), 250)
            self.assertGreaterEqual(page.image_grid.cards[0].preview.minimumWidth(), 250)
            self.assertIn("60", page.image_task_status.text())
            self.assertIn("3", page.image_task_status.text())
        finally:
            page.close()

    def test_source_urls_without_local_files_do_not_create_broken_gallery_cards(self):
        urls = [f"https://cdn.example.com/missing-{index:02d}.jpg" for index in range(1, 61)]
        product_id = self._make_product(
            "3147012",
            local_dir=self.root / "missing-local",
            urls=urls,
        )
        row = dict(self.db.product(product_id))
        self.assertEqual(self.kernel.images.source_image_count(row), 60)
        self.assertEqual(self.kernel.images.image_count(row), 0)
        self.assertEqual(self.kernel.images.local_items(product_id), [])

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
