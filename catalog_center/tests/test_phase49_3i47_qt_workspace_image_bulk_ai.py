from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication, QMessageBox

from app.db import Database
from qt6.image_gallery import ImageSeoDialog
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
            self.assertTrue((local_dir / "images" / filename).is_file())
        self.assertEqual(
            sorted(path.name for path in (local_dir / "images").glob("*.webp")),
            filenames,
        )
        self.assertEqual(
            sorted(path.name for path in (local_dir / "source_originals").iterdir()),
            ["source-1.jpg", "source-2.jpg", "source-3.jpg"],
        )
        extract = json.loads(
            (local_dir / "page_extract.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [Path(item["local_file"]).name for item in extract["images"]],
            filenames,
        )
        self.assertEqual(
            [Path(item["source_local_file"]).name for item in metadata],
            filenames,
        )

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

    def test_query_variant_cards_keep_exact_unique_seo_filename_identity(self):
        local_dir = self.root / "query-variant-product"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        first = image_dir / "01.webp"
        second = image_dir / "02.webp"
        Image.new("RGB", (640, 480), "white").save(first, format="WEBP")
        Image.new("RGB", (641, 481), "black").save(second, format="WEBP")
        urls = [
            "https://cdn.example.com/product.png?resize=1200",
            "https://cdn.example.com/product.png",
        ]
        (local_dir / "page_extract.json").write_text(
            json.dumps(
                {
                    "images": [
                        {"url": urls[0], "local_file": str(first)},
                        {"url": urls[1], "local_file": str(second)},
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        product_id = self._make_product(
            "3147002q",
            source_title="Goth Baroque Necklace Display Bust",
            local_dir=local_dir,
            urls=urls,
        )

        self.kernel.images.update_metadata(
            product_id,
            urls,
            {
                "seo_filename": "goth-baroque-necklace-display-bust-3d-print.webp",
                "alt_text": "مجسمه نمایش گردنبند گوتیک باروک",
            },
        )
        items = {
            str(item.get("url") or ""): item
            for item in self.kernel.images.local_items(product_id)
        }
        self.assertEqual(
            items[urls[0]]["planned_filename"],
            "goth-baroque-necklace-display-bust-3d-print-01.webp",
        )
        self.assertEqual(
            items[urls[1]]["planned_filename"],
            "goth-baroque-necklace-display-bust-3d-print-02.webp",
        )
        self.assertEqual(
            sorted(path.name for path in image_dir.glob("*.webp")),
            [
                "goth-baroque-necklace-display-bust-3d-print-01.webp",
                "goth-baroque-necklace-display-bust-3d-print-02.webp",
            ],
        )
        self.assertFalse((image_dir / "01.webp").exists())
        self.assertFalse((image_dir / "02.webp").exists())
        self.assertTrue((local_dir / "source_originals" / "01.webp").is_file())
        self.assertTrue((local_dir / "source_originals" / "02.webp").is_file())
        self.assertEqual(
            items[urls[0]]["metadata"]["source_url"],
            urls[0],
        )
        self.assertEqual(
            items[urls[1]]["metadata"]["source_url"],
            urls[1],
        )
        metadata = json.loads(
            self.db.product(product_id)["image_metadata_json"]
        )
        final_names = [
            Path(item["final_local_file"]).name
            for item in metadata
        ]
        self.assertEqual(
            final_names,
            [
                "goth-baroque-necklace-display-bust-3d-print-01.webp",
                "goth-baroque-necklace-display-bust-3d-print-02.webp",
            ],
        )
        self.assertEqual(len(set(final_names)), 2)
        self.assertTrue(
            all(
                (local_dir / "seo_images" / name).is_file()
                for name in final_names
            )
        )

    def test_stage3_site_selection_promotes_trusted_local_card_to_canonical_media(self):
        local_dir = self.root / "site-selection-canonical"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        first = image_dir / "01.webp"
        second = image_dir / "02.webp"
        Image.new("RGB", (400, 300), "white").save(first, format="WEBP")
        Image.new("RGB", (420, 320), "black").save(second, format="WEBP")
        source_url = "https://cdn.example.com/source-01.jpg"
        (local_dir / "page_extract.json").write_text(
            json.dumps(
                {
                    "images": [
                        {"url": source_url, "local_file": str(first)}
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        product_id = self._make_product(
            "3147002s",
            local_dir=local_dir,
            urls=[source_url],
        )
        legacy_alias = "local-display://makerworld/3147002s/02.webp"
        self.db.update_product(
            product_id,
            {
                "selected_images_json": json.dumps(
                    [source_url, legacy_alias],
                    ensure_ascii=False,
                ),
            },
        )

        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            self.assertIn("local://02.webp", page.image_grid.selected_urls())
            page._save_stage3()
        finally:
            page.close()

        row = dict(self.db.product(product_id))
        canonical = json.loads(row["images_json"])
        selected = json.loads(row["selected_images_json"])
        self.assertIn("local://02.webp", canonical)
        self.assertIn("local://02.webp", selected)
        self.assertNotIn(legacy_alias, selected)

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
            self.assertEqual(cards[urls[2]].minimumHeight(), 206)
            self.assertEqual(cards[urls[2]].maximumHeight(), 206)

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
            self.assertEqual(page.workspace_tabs.count(), 4)
            self.assertEqual(
                [
                    page.workspace_tabs.tabText(index)
                    for index in range(page.workspace_tabs.count())
                ],
                [
                    "موجودی محصولات",
                    "تک محصول",
                    "جستجو / لینک جستجو",
                    "گزارش و History",
                ],
            )
            self.assertEqual(page.workspace_tabs.currentIndex(), 0)
            self.assertEqual(page.queue_views.count(), 2)
            # O2D accepted contract: once this identity is a Product it must
            # disappear from Add/Crawl inventory and remain update-only.
            self.assertEqual(page.queue_gallery.count(), 0)
            self.assertEqual(page.queue_table.rowCount(), 0)
            self.assertEqual(
                self.kernel.acquisition.queue_count("", "all"),
                0,
            )
            self.assertIsNotNone(self.db.product(product_id))
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
            self.assertEqual(page.image_grid.columns, 3)
            self.assertTrue(page.image_grid.large_cards)
            self.assertEqual(len(page.image_grid.cards), 3)
            self.assertEqual(page.image_grid.cards[0].minimumWidth(), 300)
            self.assertEqual(page.image_grid.cards[0].minimumHeight(), 206)
            self.assertEqual(page.image_grid.cards[0].preview.minimumWidth(), 260)
            self.assertEqual(page.image_grid.cards[0].preview.minimumHeight(), 90)
            self.assertGreaterEqual(page.image_grid.host.minimumHeight(), 206)
            self.assertEqual(page.image_grid.minimumHeight(), 670)
            self.assertGreaterEqual(
                page.image_grid.scroll.verticalScrollBar().width(),
                18,
            )
            self.assertEqual(
                page.image_grid.scroll.verticalScrollBarPolicy(),
                Qt.ScrollBarPolicy.ScrollBarAlwaysOn,
            )
            self.assertIn("60", page.image_task_status.text())
            self.assertIn("3", page.image_task_status.text())
        finally:
            page.close()

    def test_wheel_over_large_preview_scrolls_gallery_and_window_stays_shrinkable(self):
        product_id, _urls, _local_dir = self._mapped_image_product()
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.resize(1800, 1000)
            page.show()
            page.load_product(product_id)
            page._set_stage(2)
            for _ in range(4):
                self.app.processEvents()

            grid = page.image_grid
            bar = grid.scroll.verticalScrollBar()
            self.assertEqual(grid.minimumHeight(), 670)
            self.assertEqual(grid.columns, 3)

            toolbar_y = {
                button.mapTo(page, QPoint(0, 0)).y()
                for button in page.image_stage3_toolbar_buttons
            }
            self.assertEqual(len(toolbar_y), 1)
            self.assertTrue(
                all(
                    button.maximumHeight() == 26
                    and button.font().pointSize() <= 7
                    for button in page.image_stage3_toolbar_buttons
                )
            )

            bottom_widgets = (
                page.save_stage_btn,
                page.finalize_stage_btn,
                page.unlock_stage_btn,
                page.footer.previous,
                page.footer.next,
            )
            bottom_centers = [
                widget.mapTo(page, QPoint(0, 0)).y() + widget.height() // 2
                for widget in bottom_widgets
            ]
            self.assertLessEqual(
                max(bottom_centers) - min(bottom_centers),
                2,
            )
            self.assertTrue(page.footer.compact)

            grid.set_items([
                {
                    "url": f"https://img.example/wheel-{index:02d}.jpg",
                    "filename": f"wheel-{index:02d}.jpg",
                    "planned_filename": f"wheel-seo-{index:02d}.webp",
                    "selected": True,
                }
                for index in range(1, 13)
            ])
            for _ in range(4):
                self.app.processEvents()
            self.assertGreater(bar.maximum(), 0)

            bar.setValue(0)
            event = QWheelEvent(
                QPointF(50, 50),
                QPointF(50, 50),
                QPoint(0, 0),
                QPoint(0, -120),
                Qt.MouseButton.NoButton,
                Qt.KeyboardModifier.NoModifier,
                Qt.ScrollPhase.ScrollUpdate,
                False,
            )
            QApplication.sendEvent(grid.cards[0].preview, event)
            self.app.processEvents()
            self.assertGreater(bar.value(), 0)
        finally:
            page.close()

    def test_operation_multiselect_is_independent_from_site_image_selection(self):
        product_id, urls, _local_dir = self._mapped_image_product()
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            self.assertEqual(set(page.image_grid.selected_urls()), set(urls))
            self.assertEqual(page.image_grid.operation_urls(), [])

            cards = {
                str(card.item.get("url") or ""): card
                for card in page.image_grid.cards
            }
            first = cards[urls[0]]
            self.assertEqual(first.bulk_selected.text(), "ویرایش")
            self.assertEqual(first.selected.text(), "ارسال سایت")
            self.assertIn("به سایت نمی‌فرستد", first.bulk_selected.toolTip())
            self.assertIn("مرجع واقعی تصاویر Product", first.selected.toolTip())
            cards[urls[0]].bulk_selected.setChecked(True)
            cards[urls[2]].bulk_selected.setChecked(True)

            self.assertEqual(
                page.image_grid.operation_urls(),
                [urls[0], urls[2]],
            )
            self.assertEqual(set(page.image_grid.selected_urls()), set(urls))

            page.image_grid.set_all_operation_selected(True)
            self.assertEqual(set(page.image_grid.operation_urls()), set(urls))
            page.image_grid.set_all_operation_selected(False)
            self.assertEqual(page.image_grid.operation_urls(), [])
            self.assertEqual(set(page.image_grid.selected_urls()), set(urls))
        finally:
            page.close()

    def test_bulk_delete_removes_only_operation_selected_images(self):
        product_id, urls, _local_dir = self._mapped_image_product()
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            cards = {
                str(card.item.get("url") or ""): card
                for card in page.image_grid.cards
            }
            cards[urls[1]].bulk_selected.setChecked(True)
            cards[urls[2]].bulk_selected.setChecked(True)
            with patch(
                "qt6.product_wizard.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ):
                page._delete_selected_images()

            row = dict(self.db.product(product_id))
            self.assertEqual(json.loads(row["images_json"]), [urls[0]])
            self.assertEqual(json.loads(row["selected_images_json"]), [urls[0]])
            self.assertEqual(row["primary_image_url"], urls[0])
        finally:
            page.close()

    def test_apply_product_seo_targets_only_operation_selected_images(self):
        product_id, urls, _local_dir = self._mapped_image_product()
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            cards = {
                str(card.item.get("url") or ""): card
                for card in page.image_grid.cards
            }
            cards[urls[1]].bulk_selected.setChecked(True)
            page._apply_product_image_seo()

            metadata = json.loads(
                self.db.product(product_id)["image_metadata_json"]
            )
            by_url = {
                str(item.get("source_url") or ""): item
                for item in metadata
            }
            self.assertIn("alt_text", by_url[urls[1]].get("_operator_override_fields", []))
            self.assertNotIn(
                "alt_text",
                by_url[urls[0]].get("_operator_override_fields", []),
            )
            self.assertNotIn(
                "alt_text",
                by_url[urls[2]].get("_operator_override_fields", []),
            )
        finally:
            page.close()

    def test_name_and_seo_button_repairs_all_site_images_when_no_operation_subset(self):
        product_id, urls, _local_dir = self._mapped_image_product()
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            self.assertEqual(page.image_grid.operation_urls(), [])
            self.assertEqual(page.image_name_seo_btn.text(), "اصلاح اسم و سئو")

            page._apply_product_image_seo()

            row = dict(self.db.product(product_id))
            metadata = [
                dict(item)
                for item in json.loads(row["image_metadata_json"])
            ]
            by_url = {
                str(item.get("source_url") or ""): item
                for item in metadata
            }
            self.assertEqual(set(by_url), set(urls))
            self.assertEqual(
                [by_url[url]["seo_filename"] for url in urls],
                [
                    "table-lamp-3d-print-01.webp",
                    "table-lamp-3d-print-02.webp",
                    "table-lamp-3d-print-03.webp",
                ],
            )
            for url in urls:
                self.assertIn(
                    "alt_text",
                    by_url[url].get("_operator_override_fields", []),
                )
            self.assertEqual(
                json.loads(row["selected_images_json"]),
                urls,
            )
            self.assertEqual(row["primary_image_url"], urls[0])
        finally:
            page.close()

    def test_published_image_seo_edit_marks_same_product_for_republish(self):
        product_id, urls, _local_dir = self._mapped_image_product()
        self.db.update_product(
            product_id,
            {
                "server_id": "asset-existing",
                "server_product_id": 1902,
                "workflow_status": "uploaded",
                "needs_update": 0,
                "upload_ready": 0,
            },
        )

        self.kernel.images.update_metadata(
            product_id,
            [urls[0]],
            {"alt_text": "ALT updated after publish"},
        )

        row = dict(self.db.product(product_id))
        self.assertEqual(row["server_id"], "asset-existing")
        self.assertEqual(int(row["server_product_id"]), 1902)
        self.assertEqual(row["workflow_status"], "uploaded")
        self.assertEqual(int(row["needs_update"]), 1)
        self.assertEqual(int(row["upload_ready"]), 0)

    def test_published_operator_field_edit_marks_same_product_for_republish(self):
        product_id = self._make_product("3147019")
        self.db.update_product(
            product_id,
            {
                "server_id": "asset-existing-operator",
                "server_product_id": 1919,
                "workflow_status": "uploaded",
                "needs_update": 0,
                "upload_ready": 0,
            },
        )

        self.kernel.products.update_operator_fields(
            product_id,
            {"title_fa": "عنوان اصلاح‌شده پس از انتشار"},
        )

        row = dict(self.db.product(product_id))
        self.assertEqual(row["server_id"], "asset-existing-operator")
        self.assertEqual(int(row["server_product_id"]), 1919)
        self.assertEqual(int(row["needs_update"]), 1)
        self.assertEqual(int(row["upload_ready"]), 0)

    def test_card_shows_seo_filename_and_keeps_source_filename_secondary(self):
        product_id, urls, _local_dir = self._mapped_image_product()
        self.kernel.images.finalize(product_id)
        items = {
            str(item.get("url") or ""): item
            for item in self.kernel.images.local_items(product_id)
        }
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            cards = {
                str(card.item.get("url") or ""): card
                for card in page.image_grid.cards
            }
            first = cards[urls[0]]
            self.assertEqual(
                first.filename.text(),
                items[urls[0]]["planned_filename"],
            )
            self.assertIn(
                items[urls[0]]["filename"],
                first.source_filename.text(),
            )
            self.assertTrue(first.filename.text().endswith("-01.webp"))
        finally:
            page.close()

    def test_manual_source_screenshot_is_visible_without_stealing_numbered_source_slot(self):
        local_dir = self.root / "manual-screenshot"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (400, 300), "white").save(image_dir / "01.webp", format="WEBP")
        Image.new("RGB", (420, 320), "white").save(image_dir / "02.webp", format="WEBP")
        screenshot_name = "source-page-screenshot-20260918-101500.png"
        Image.new("RGB", (900, 700), "white").save(image_dir / screenshot_name, format="PNG")

        source_url = "https://cdn.example.com/source-01.jpg"
        screenshot_url = f"local://{screenshot_name}"
        product_id = self._make_product(
            "3147013",
            local_dir=local_dir,
            urls=[source_url, screenshot_url],
        )
        self.db.update_product(
            product_id,
            {"selected_images_json": json.dumps([source_url], ensure_ascii=False)},
        )

        items = self.kernel.images.local_items(product_id)
        by_name = {item["filename"]: item for item in items}
        self.assertEqual(set(by_name), {"01.webp", "02.webp", screenshot_name})
        self.assertEqual(by_name["01.webp"]["url"], source_url)
        self.assertEqual(by_name["02.webp"]["url"], "local://02.webp")
        self.assertFalse(by_name["02.webp"]["display_only"])
        self.assertTrue(by_name["02.webp"]["planned_filename"].endswith("-02.webp"))
        self.assertEqual(by_name[screenshot_name]["url"], screenshot_url)
        self.assertFalse(by_name[screenshot_name]["display_only"])
        self.assertFalse(by_name[screenshot_name]["selected"])

    def test_screenshot_seo_defaults_and_metadata_persist_without_site_selection(self):
        local_dir = self.root / "screenshot-seo"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (500, 360), "white").save(
            image_dir / "01.webp",
            format="WEBP",
        )
        screenshot_name = "source-page-screenshot-20260918-152830.png"
        Image.new("RGB", (1100, 760), "white").save(
            image_dir / screenshot_name,
            format="PNG",
        )

        source_url = "https://cdn.example.com/owner-source.jpg"
        screenshot_url = f"local://{screenshot_name}"
        (local_dir / "page_extract.json").write_text(
            json.dumps(
                {
                    "images": [
                        {
                            "url": source_url,
                            "local_file": str(image_dir / "01.webp"),
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        product_id = self._make_product(
            "3147020",
            title="اسپینوزور مینی",
            source_title="Mini Skeletal Spinosaurus",
            local_dir=local_dir,
            urls=[source_url, screenshot_url],
        )
        self.db.update_product(
            product_id,
            {
                "selected_images_json": json.dumps(
                    [source_url],
                    ensure_ascii=False,
                ),
                "primary_image_url": source_url,
                "seo_title_fa": "اسپینوزور مینی - چاپ 3 بعدی رایگان | 3DPrintHub",
                "keywords_json": json.dumps(
                    ["اسپینوزور", "چاپ سه بعدی"],
                    ensure_ascii=False,
                ),
            },
        )
        self.kernel.images.finalize(product_id)

        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            screenshot_item = page.image_grid.item_for_url(screenshot_url)
            self.assertIsNotNone(screenshot_item)
            self.assertFalse(bool(screenshot_item.get("selected")))

            defaults = page._product_image_seo_values()
            dialog = ImageSeoDialog(
                [screenshot_item],
                parent=page,
                defaults=defaults,
            )
            try:
                self.assertEqual(
                    dialog.alt.text(),
                    "اسپینوزور مینی | سفارش چاپ سه‌بعدی در 3DPrintHub",
                )
                self.assertEqual(
                    dialog.title.text(),
                    "اسپینوزور مینی | سفارش چاپ سه‌بعدی در 3DPrintHub",
                )
                self.assertTrue(dialog.caption.toPlainText().strip())
                self.assertIn("اسپینوزور", dialog.keywords.toPlainText())
                self.assertTrue(dialog.filename.text().endswith(".webp"))
            finally:
                dialog.close()

            self.kernel.images.update_metadata(
                product_id,
                [screenshot_url],
                defaults,
            )
            row = dict(self.db.product(product_id))
            self.assertEqual(
                json.loads(row["selected_images_json"]),
                [source_url],
            )
            metadata = {
                str(item.get("source_url") or ""): dict(item)
                for item in json.loads(row["image_metadata_json"])
            }
            self.assertIn(screenshot_url, metadata)
            screenshot_meta = metadata[screenshot_url]
            self.assertEqual(
                screenshot_meta["alt_text"],
                "اسپینوزور مینی | سفارش چاپ سه‌بعدی در 3DPrintHub",
            )
            self.assertEqual(
                screenshot_meta["title"],
                "اسپینوزور مینی | سفارش چاپ سه‌بعدی در 3DPrintHub",
            )
            self.assertFalse(screenshot_meta["metadata_ready"])
            self.assertFalse(
                str(screenshot_meta.get("final_local_file") or "")
            )

            page.load_product(product_id)
            refreshed_item = page.image_grid.item_for_url(screenshot_url)
            self.assertEqual(
                refreshed_item["alt_text"],
                "اسپینوزور مینی | سفارش چاپ سه‌بعدی در 3DPrintHub",
            )
            self.assertEqual(
                refreshed_item["seo_title"],
                "اسپینوزور مینی | سفارش چاپ سه‌بعدی در 3DPrintHub",
            )
        finally:
            page.close()

    def test_name_and_seo_without_operation_subset_includes_unselected_screenshot(self):
        local_dir = self.root / "screenshot-bulk-seo"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (500, 360), "white").save(
            image_dir / "01.webp",
            format="WEBP",
        )
        screenshot_name = "source-page-screenshot-20260918-160000.png"
        Image.new("RGB", (1100, 760), "white").save(
            image_dir / screenshot_name,
            format="PNG",
        )

        source_url = "https://cdn.example.com/bulk-source.jpg"
        screenshot_url = f"local://{screenshot_name}"
        (local_dir / "page_extract.json").write_text(
            json.dumps(
                {
                    "images": [
                        {
                            "url": source_url,
                            "local_file": str(image_dir / "01.webp"),
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        product_id = self._make_product(
            "3147021",
            title="محصول تست سئو",
            source_title="SEO Test Product",
            local_dir=local_dir,
            urls=[source_url, screenshot_url],
        )
        self.db.update_product(
            product_id,
            {
                "selected_images_json": json.dumps(
                    [source_url],
                    ensure_ascii=False,
                ),
                "primary_image_url": source_url,
            },
        )
        self.kernel.images.finalize(product_id)

        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            self.assertEqual(page.image_grid.operation_urls(), [])
            self.assertIn(screenshot_url, page.image_grid.editable_urls())
            page._apply_product_image_seo()

            row = dict(self.db.product(product_id))
            self.assertEqual(
                json.loads(row["selected_images_json"]),
                [source_url],
            )
            metadata = {
                str(item.get("source_url") or ""): dict(item)
                for item in json.loads(row["image_metadata_json"])
            }
            self.assertIn(source_url, metadata)
            self.assertIn(screenshot_url, metadata)
            self.assertTrue(metadata[source_url]["metadata_ready"])
            self.assertFalse(metadata[screenshot_url]["metadata_ready"])
            self.assertTrue(
                str(metadata[screenshot_url].get("seo_filename") or "").endswith(
                    ".webp"
                )
            )
            self.assertEqual(
                metadata[screenshot_url]["alt_text"],
                page._product_image_seo_values()["alt_text"],
            )
        finally:
            page.close()

    def test_trusted_legacy_numbered_local_image_is_editable_and_removal_is_recoverable(self):
        local_dir = self.root / "legacy-editable-local"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (400, 300), "white").save(
            image_dir / "01.webp",
            format="WEBP",
        )
        Image.new("RGB", (420, 320), "white").save(
            image_dir / "02.webp",
            format="WEBP",
        )

        source_url = "https://cdn.example.com/source-01.jpg"
        (local_dir / "page_extract.json").write_text(
            json.dumps(
                {
                    "images": [
                        {
                            "url": source_url,
                            "local_file": str(image_dir / "01.webp"),
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        product_id = self._make_product(
            "3147014",
            local_dir=local_dir,
            urls=[source_url],
        )
        legacy_alias = "local-display://makerworld/3147014/02.webp"
        self.db.update_product(
            product_id,
            {
                "selected_images_json": json.dumps(
                    [source_url, legacy_alias],
                    ensure_ascii=False,
                ),
            },
        )

        items = {
            item["filename"]: item
            for item in self.kernel.images.local_items(product_id)
        }
        self.assertEqual(items["02.webp"]["url"], "local://02.webp")
        self.assertFalse(items["02.webp"]["display_only"])
        self.assertTrue(items["02.webp"]["selected"])
        self.assertTrue(items["02.webp"]["planned_filename"].endswith("-02.webp"))

        self.kernel.images.update_metadata(
            product_id,
            ["local://02.webp"],
            {"alt_text": "نمای دوم محصول"},
        )
        seo_row = dict(self.db.product(product_id))
        seo_selected = json.loads(seo_row["selected_images_json"])
        renamed_url = "local://table-lamp-3d-print-02.webp"
        self.assertIn(renamed_url, seo_selected)
        self.assertNotIn("local://02.webp", seo_selected)
        self.assertNotIn(legacy_alias, seo_selected)
        seo_metadata = {
            str(item.get("source_url") or ""): item
            for item in json.loads(seo_row["image_metadata_json"])
        }
        self.assertTrue(
            Path(seo_metadata[renamed_url]["final_local_file"]).is_file()
        )
        self.assertTrue(
            Path(seo_metadata[renamed_url]["source_local_file"]).is_file()
        )
        self.assertEqual(
            Path(seo_metadata[renamed_url]["source_local_file"]).name,
            "table-lamp-3d-print-02.webp",
        )
        self.assertTrue((local_dir / "source_originals" / "02.webp").is_file())

        self.kernel.images.remove_urls(product_id, [renamed_url])

        refreshed = dict(self.db.product(product_id))
        self.assertNotIn(
            legacy_alias,
            json.loads(refreshed["selected_images_json"]),
        )
        self.assertFalse((image_dir / "02.webp").exists())
        self.assertFalse(
            (image_dir / "table-lamp-3d-print-02.webp").exists()
        )
        self.assertTrue(
            (
                local_dir
                / "removed_images"
                / "table-lamp-3d-print-02.webp"
            ).is_file()
        )
        self.assertNotIn(
            "table-lamp-3d-print-02.webp",
            {
                item["filename"]
                for item in self.kernel.images.local_items(product_id)
            },
        )

    def test_add_local_file_is_persisted_and_selected_for_next_publish(self):
        local_dir = self.root / "manual-add-product"
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (400, 300), "white").save(
            image_dir / "01.webp",
            format="WEBP",
        )
        product_id = self._make_product(
            "3147015",
            local_dir=local_dir,
            urls=["local://01.webp"],
        )
        source = self.root / "owner-added.png"
        Image.new("RGB", (640, 480), "navy").save(source, format="PNG")

        result = self.kernel.images.add_local_files(product_id, [str(source)])

        self.assertEqual(len(result["added"]), 1)
        added = result["added"][0]
        self.assertTrue(added.startswith("local://manual-owner-added-"))
        refreshed = dict(self.db.product(product_id))
        self.assertIn(added, json.loads(refreshed["images_json"]))
        self.assertIn(added, json.loads(refreshed["selected_images_json"]))
        copied = local_dir / "images" / added.split("local://", 1)[1]
        self.assertTrue(copied.is_file())
        self.assertIn(
            added,
            [item["url"] for item in self.kernel.images.local_items(product_id)],
        )

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

    def test_publish_intent_flushes_current_site_selection_before_ready(self):
        product_id, urls, _local_dir = self._mapped_image_product()
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            page.approved_for_sale.setChecked(True)
            page.publish_product.setChecked(True)
            labels = [button.text() for button in page.image_stage3_toolbar_buttons]
            self.assertIn("رفرش رسانه از DB/Local", labels)
            cards = {
                str(card.item.get("url") or ""): card
                for card in page.image_grid.cards
            }
            cards[urls[2]].selected.setChecked(False)
            self.assertEqual(page.image_grid.selected_urls(), urls[:2])

            with patch.object(QMessageBox, "warning"):
                self.assertTrue(page._publish_intent_ready())

            row = dict(self.db.product(product_id))
            self.assertEqual(json.loads(row["selected_images_json"]), urls[:2])
            self.assertEqual(row["primary_image_url"], urls[0])
        finally:
            page.close()

    def test_product_page_full_edit_unlocks_all_stages_without_marking_publish_dirty(self):
        product_id = self._make_product("3147005")
        locks = {
            stage: {"locked": True, "locked_at": "2026-09-22T12:00:00Z"}
            for stage in (
                "quick",
                "commerce",
                "images",
                "content",
                "specs",
                "slider",
                "publish",
            )
        }
        self.db.update_product(
            product_id,
            {
                "operator_stage_locks_json": json.dumps(
                    locks,
                    ensure_ascii=False,
                ),
                "workflow_status": "uploaded",
                "server_id": "site:3147005",
                "needs_update": 0,
                "upload_ready": 0,
            },
        )

        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            self.assertEqual(page.edit_all_btn.text(), "✏ ویرایش کامل")
            self.assertTrue(page.edit_all_btn.isEnabled())
            with patch.object(
                QMessageBox,
                "question",
                return_value=QMessageBox.StandardButton.Yes,
            ), patch.object(QMessageBox, "information"):
                page._unlock_all_for_edit()
        finally:
            page.close()

        row = dict(self.db.product(product_id))
        self.assertEqual(
            json.loads(row["operator_stage_locks_json"]),
            {},
        )
        self.assertEqual(int(row["needs_update"] or 0), 0)
        self.assertEqual(row["workflow_status"], "uploaded")

    def test_stage_core_full_registration_explicitly_approves_all_seven_without_publish(self):
        product_id = self._make_product("3147007")
        called = []

        def finalize(product_id_arg, stage, *, manual_approval=True, event_type=""):
            called.append(
                (
                    int(product_id_arg),
                    str(stage),
                    bool(manual_approval),
                    str(event_type),
                )
            )
            return {}

        with patch.object(self.kernel.stages, "finalize", side_effect=finalize):
            result = self.kernel.stages.finalize_all_ready(product_id)

        expected = [
            "quick",
            "commerce",
            "images",
            "content",
            "specs",
            "slider",
            "publish",
        ]
        self.assertEqual([item[1] for item in called], expected)
        self.assertTrue(all(item[2] for item in called))
        self.assertTrue(
            all(item[3] == "qt_all_stages_finalized" for item in called)
        )
        self.assertEqual(result["finalized"], expected)
        self.assertEqual(result["blocked"], {})
        self.assertTrue(result["all_finalized"])

    def test_product_page_full_registration_saves_current_then_confirms_all_without_send(self):
        product_id = self._make_product("3147008")
        page = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            page.load_product(product_id)
            self.assertEqual(page.finalize_all_btn.text(), "✅ ثبت کامل")
            self.assertTrue(page.finalize_all_btn.isEnabled())
            result = {
                "product_id": product_id,
                "finalized": [
                    "quick",
                    "commerce",
                    "images",
                    "content",
                    "specs",
                    "slider",
                    "publish",
                ],
                "already_finalized": [],
                "blocked": {},
                "all_finalized": True,
            }
            with (
                patch.object(
                    QMessageBox,
                    "question",
                    return_value=QMessageBox.StandardButton.Yes,
                ),
                patch.object(QMessageBox, "information"),
                patch.object(page, "_save_current", return_value=True) as save,
                patch.object(
                    self.kernel.stages,
                    "finalize_all_ready",
                    return_value=result,
                ) as finalize_all,
                patch.object(
                    self.kernel.publish,
                    "mark_ready_many",
                ) as mark_ready,
                patch.object(
                    self.kernel.publish,
                    "publish_many",
                ) as publish_many,
            ):
                page._finalize_all()

            save.assert_called_once_with(notify=False)
            finalize_all.assert_called_once_with(product_id)
            mark_ready.assert_not_called()
            publish_many.assert_not_called()
        finally:
            page.close()

    def test_bulk_ai_preparation_opens_commerce_but_not_publish(self):
        product_id = self._make_product("3147006")
        self.db.update_product(
            product_id,
            {
                "operator_stage_locks_json": json.dumps(
                    {
                        "quick": {"locked": True},
                        "commerce": {"locked": True},
                        "slider": {"locked": True},
                        "publish": {"locked": True},
                    },
                    ensure_ascii=False,
                )
            },
        )
        self.kernel.ai.bind_executor(
            lambda product_id, mode, **kwargs: {
                "product_id": int(product_id),
                "requested_source_mode": str(mode),
            }
        )
        seen = []
        extended_flags = []

        def postprocess(
            _kernel,
            product_id,
            result,
            *,
            extended_bulk=False,
        ):
            seen.append(int(product_id))
            extended_flags.append(bool(extended_bulk))
            return dict(result or {})

        with patch.object(
            type(self.kernel),
            "postprocess_full_product_ai",
            new=postprocess,
        ):
            result = self.kernel.complete_products_with_ai(
                [product_id],
                "link",
            )

        self.assertEqual(result["completed"], 1)
        self.assertEqual(seen, [product_id])
        self.assertEqual(extended_flags, [True])
        locks = json.loads(
            self.db.product(product_id)["operator_stage_locks_json"]
        )
        self.assertNotIn("quick", locks)
        self.assertNotIn("commerce", locks)
        self.assertNotIn("slider", locks)
        self.assertIn("publish", locks)

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
