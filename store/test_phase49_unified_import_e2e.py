from __future__ import annotations

import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase, override_settings

from store.epic49_catalog_profile import ProductCatalogProfile
from store.models import ImportedPrintAsset, PrintQuality, Product
from website.models import HomepageHeroSlide, Material


TINY_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class Epic49UnifiedImportE2ETests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.media = tempfile.TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.media.name)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(self.media.cleanup)
        self.addCleanup(self.temp.cleanup)
        Material.objects.create(
            name="PLA Epic49",
            price_per_kg=500000,
            sale_price_per_gram=600,
            main_usage="تست Epic49",
            sample_parts="محصول تست",
            is_active=True,
        )
        PrintQuality.objects.create(code="ep49-std", name="استاندارد Epic49", is_active=True)

    def _build_batch(self) -> Path:
        root = Path(self.temp.name) / "desktop_catalog_v85_20260818_130600"
        model = root / "models" / "makerworld_EP49-E2E-001"
        images = model / "images"
        images.mkdir(parents=True)
        (images / "hero.gif").write_bytes(TINY_GIF)

        remote = "https://example.com/media/hero.gif"
        data = {
            "source_code": "makerworld",
            "source_name": "MakerWorld",
            "source_url": "https://example.com/models/ep49-e2e-001",
            "external_id": "EP49-E2E-001",
            "source_title": "Epic49 E2E Gear",
            "source_short_description": "Source short",
            "source_description": "Source description",
            "title_fa": "چرخ‌دنده تست Epic49",
            "short_description_fa": "چرخ‌دنده آزمایشی برای تست زنجیره کامل",
            "description_fa": "توضیحات کامل فارسی محصول تست Epic49",
            "seo_title_fa": "خرید چرخ‌دنده تست Epic49",
            "seo_description_fa": "توضیح سئو عمومی محصول تست Epic49",
            "tags_fa_json": ["چرخ دنده", "پرینت سه بعدی"],
            "keywords_json": ["چرخ دنده سه بعدی", "Epic49"],
            "hashtags_fa_json": ["#پرینت_سه_بعدی"],
            "image_alt_texts_json": ["چرخ‌دنده تست Epic49 روی اسلایدر"],
            "local_category_slug": "ep49-e2e-category",
            "local_category_name": "قطعات تست Epic49",
            "approved_for_sale": True,
            "publish_as_product": True,
            "publish_as_portfolio": False,
            "commercial_status": "allowed",
            "license_name": "Commercial allowed",
            "license_url": "https://example.com/license",
            "suggested_price": 750000,
            "final_price": 750000,
            "price_is_final": True,
            "product_type": "ready_product",
            "use_description": "تست فرایند Windows تا Store",
            "availability_status": "made_to_order",
            "stock_quantity": 0,
            "lead_time_min_days": 2,
            "lead_time_max_days": 4,
            "has_3d_file": True,
            "technical_features_json": {"test": "epic49"},
            "materials_json": ["PLA"],
            "colors_json": ["مشکی"],
            "material_color_options_json": [],
            "download_image_limit": 10,
            "images_json": [remote],
            "selected_images_json": [remote],
            "primary_image_url": remote,
            "local_image_files_json": ["hero.gif"],
            "homepage_slider_enabled": True,
            "homepage_slider_image_url": remote,
            "homepage_slider_sort_order": 11,
            "homepage_slider_title_fa": "عنوان اختصاصی چرخ‌دنده آزمایشی",
            "homepage_slider_description_fa": "توضیح کاملاً مستقل مخصوص اسلایدر برای معرفی و خرید محصول",
            "homepage_slider_alt_text": "تصویر اختصاصی چرخ‌دنده برای خرید و سفارش محصول",
            "homepage_slider_button_text": "مشاهده چرخ‌دنده",
            "homepage_slider_focus_keyword": "خرید چرخ دنده سه بعدی",
            "homepage_slider_transition_effect": "wedding_dissolve",
            "homepage_slider_transition_duration_ms": 1900,
            "homepage_slider_display_duration_ms": 8700,
            "server_product_revision": 0,
            "server_slider_revision": 0,
            "operator_name": "employee-e2e",
            "batch_uuid": "epic49-e2e-batch",
            "source_hash": "e" * 64,
        }
        (model / "desktop_editorial.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        manifest = {
            "schema_version": "8.5",
            "batch_uuid": "epic49-e2e-batch",
            "batch_name": root.name,
            "models": [{
                "desktop_product_id": 991,
                "source_code": "makerworld",
                "external_id": "EP49-E2E-001",
                "editorial": "models/makerworld_EP49-E2E-001/desktop_editorial.json",
                "selected_images": 1,
                "local_images": 1,
                "source_hash": "e" * 64,
            }],
        }
        (root / "batch_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return root

    def test_windows_batch_creates_product_profile_and_cinematic_hero_then_reimport_is_idempotent(self):
        batch = self._build_batch()
        out = StringIO()
        call_command("phase37_import_catalog_center", str(batch), stdout=out)
        output = out.getvalue()
        self.assertIn("PRODUCT_COUNT=1", output)
        self.assertIn("FAILED_COUNT=0", output)

        asset = ImportedPrintAsset.objects.get(external_id="EP49-E2E-001")
        self.assertIsNotNone(asset.product_id)
        product = Product.objects.get(pk=asset.product_id)
        profile = ProductCatalogProfile.objects.get(product=product)
        slide = HomepageHeroSlide.objects.get(asset=asset)

        self.assertEqual(product.title, "چرخ‌دنده تست Epic49")
        self.assertEqual(product.meta_title, "خرید چرخ‌دنده تست Epic49")
        self.assertEqual(profile.homepage_slider_title_fa, "عنوان اختصاصی چرخ‌دنده آزمایشی")
        self.assertEqual(profile.homepage_slider_description_fa, "توضیح کاملاً مستقل مخصوص اسلایدر برای معرفی و خرید محصول")
        self.assertEqual(profile.homepage_slider_alt_text, "تصویر اختصاصی چرخ‌دنده برای خرید و سفارش محصول")
        self.assertEqual(profile.homepage_slider_focus_keyword, "خرید چرخ دنده سه بعدی")
        self.assertEqual(profile.homepage_slider_transition_effect, "wedding_dissolve")
        self.assertEqual(profile.homepage_slider_transition_duration_ms, 1900)
        self.assertEqual(profile.homepage_slider_display_duration_ms, 8700)
        self.assertEqual(profile.last_modified_by, "employee-e2e")

        self.assertEqual(slide.title_override, "عنوان اختصاصی چرخ‌دنده آزمایشی")
        self.assertEqual(slide.description, "توضیح کاملاً مستقل مخصوص اسلایدر برای معرفی و خرید محصول")
        self.assertEqual(slide.image_alt_text, "تصویر اختصاصی چرخ‌دنده برای خرید و سفارش محصول")
        self.assertEqual(slide.transition_effect, "wedding_dissolve")
        self.assertEqual(slide.transition_duration_ms, 1900)
        self.assertEqual(slide.display_duration_ms, 8700)
        self.assertTrue(slide.is_active)
        self.assertIsNotNone(slide.selected_asset_image_id)
        self.assertEqual(slide.selected_asset_image.asset_id, asset.pk)
        self.assertTrue(slide.selected_asset_image.image.name.endswith("hero.gif"))

        product_revision = profile.sync_revision
        slider_revision = slide.sync_revision
        out2 = StringIO()
        call_command("phase37_import_catalog_center", str(batch), stdout=out2)
        profile.refresh_from_db()
        slide.refresh_from_db()
        self.assertEqual(profile.sync_revision, product_revision)
        self.assertEqual(slide.sync_revision, slider_revision)
        self.assertEqual(Product.objects.filter(pk=product.pk).count(), 1)
        self.assertEqual(HomepageHeroSlide.objects.filter(asset=asset).count(), 1)
