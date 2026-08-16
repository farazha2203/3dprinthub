from __future__ import annotations

import json
import tempfile
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from django.urls import resolve

from store.epic49_catalog_profile import ProductCatalogProfile, sync_catalog_profile, sync_product_seo
from store.models import Category, ImportedPrintAsset, PrintCatalogSource, Product
from store.templatetags.store_seo import product_schema_json
from website.models import HomepageHeroSlide


class Epic49ServerSchemaTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.media.name, ALLOWED_HOSTS=["testserver"])
        self.override.enable()
        self.category = Category.objects.create(name="دکور", slug="decor", section="creative", is_active=True)
        self.product = Product.objects.create(
            category=self.category,
            title="آباژور برگی",
            title_en="Leaf Lamp Table Light",
            slug="آباژور-برگی",
            sku="EP49-TEST-1",
            short_description="آباژور دکوراتیو قابل چاپ",
            description="توضیح کامل محصول",
            main_image=SimpleUploadedFile("lamp.jpg", b"fake-image-content", content_type="image/jpeg"),
            is_active=True,
            fixed_price=350000,
            robots_index=True,
            robots_follow=True,
        )
        self.source = PrintCatalogSource.objects.create(
            name="MakerWorld",
            code="makerworld-test",
            base_url="https://makerworld.com",
            default_category=self.category,
            is_active=True,
        )
        self.data = {
            "desktop_product_id": 44,
            "batch_uuid": "batch-epic49-test",
            "source_hash": "a" * 64,
            "product_type": "ready_product",
            "use_description": "مناسب میز کار و دکور منزل",
            "availability_status": "made_to_order",
            "stock_quantity": 3,
            "lead_time_min_days": 2,
            "lead_time_max_days": 5,
            "has_3d_file": True,
            "commercial_status": "allowed",
            "license_name": "Commercial use allowed",
            "license_url": "https://example.com/license",
            "technical_features_json": {"ارتفاع": "۲۵ سانتی‌متر", "کاربری": "دکور"},
            "keywords_json": ["آباژور سه بعدی", "چاپ سه بعدی دکور"],
            "tags_fa_json": ["آباژور"],
            "hashtags_fa_json": ["#پرینت_سه_بعدی", "#آباژور"],
            "seo_title_fa": "خرید و سفارش چاپ سه‌بعدی آباژور برگی",
            "seo_description_fa": "سفارش چاپ سه‌بعدی آباژور برگی با انتخاب متریال و رنگ.",
            "source_url": "https://makerworld.com/en/models/1913623",
            "author_name": "Designer",
            "price_min": 350000,
            "price_max": 650000,
            "download_image_limit": 10,
            "homepage_slider_enabled": True,
            "homepage_slider_image_url": "https://example.com/lamp.jpg",
            "homepage_slider_sort_order": 20,
        }
        self.asset = ImportedPrintAsset.objects.create(
            source=self.source,
            source_url=self.data["source_url"],
            external_id="1913623",
            title="Leaf Lamp",
            source_title="Leaf Lamp Table Light",
            persian_title="آباژور برگی",
            fixed_print_price=350000,
            commercial_license_status="allowed",
            source_payload={"desktop_catalog_v85": self.data},
        )
        # Avoid the post_save sync while constructing the fixture; production
        # assigns this relation through the importer after the Product exists.
        ImportedPrintAsset.objects.filter(pk=self.asset.pk).update(product_id=self.product.pk)
        self.asset.refresh_from_db()

    def tearDown(self):
        self.override.disable()
        self.media.cleanup()

    def test_profile_sync_makes_existing_store_slug_ascii_and_persists_operator_fields(self):
        profile = sync_catalog_profile(self.product, self.asset, self.data, price_min=350000, price_max=650000)
        self.product.refresh_from_db()
        self.assertEqual(profile.product_id, self.product.pk)
        self.assertEqual(profile.desktop_product_id, 44)
        self.assertEqual(profile.price_min, 350000)
        self.assertEqual(profile.price_max, 650000)
        self.assertEqual(profile.price_mode, "range")
        self.assertEqual(profile.download_image_limit, 10)
        self.assertTrue(profile.homepage_slider_enabled)
        self.assertEqual(profile.technical_features["کاربری"], "دکور")
        self.assertEqual(self.product.slug, profile.public_slug)
        self.product.slug.encode("ascii")
        self.assertNotIn("%", self.product.slug)
        path = self.product.get_absolute_url()
        self.assertEqual(resolve(path).view_name, "store:product_detail")
        self.assertIn(profile.public_slug, path)

    def test_seo_sync_and_schema_use_structured_catalog_data(self):
        sync_catalog_profile(self.product, self.asset, self.data, price_min=350000, price_max=650000)
        sync_product_seo(self.product, self.asset, self.data)
        self.product.refresh_from_db()
        self.assertEqual(self.product.meta_title, self.data["seo_title_fa"])
        self.assertEqual(self.product.meta_description, self.data["seo_description_fa"])
        self.assertEqual(self.product.seo_focus_keyword, "آباژور سه بعدی")
        self.assertIn("#آباژور", self.product.hashtags)
        self.assertEqual(self.product.canonical_url, "")

        request = RequestFactory().get(self.product.get_absolute_url(), HTTP_HOST="testserver")
        payload = json.loads(str(product_schema_json(self.product, [], request, None)))
        group = payload["@graph"][0]
        self.assertEqual(group["offers"]["@type"], "AggregateOffer")
        self.assertEqual(group["offers"]["lowPrice"], 3500000)
        self.assertEqual(group["offers"]["highPrice"], 6500000)
        self.assertIn("آباژور سه بعدی", group["keywords"])
        names = {item["name"] for item in group["additionalProperty"]}
        self.assertIn("نوع محصول", names)
        self.assertIn("ارتفاع", names)

    def test_active_homepage_slide_targets_store_product_after_ascii_sync(self):
        sync_catalog_profile(self.product, self.asset, self.data, price_min=350000, price_max=650000)
        slide = HomepageHeroSlide.objects.create(
            asset=self.asset,
            title_override="آباژور برگی",
            description="مدل منتخب برای دکور",
            image_url="https://example.com/lamp.jpg",
            is_active=True,
        )
        self.product.refresh_from_db()
        self.assertEqual(slide.target_url, self.product.get_absolute_url())
        self.assertEqual(resolve(slide.target_url).view_name, "store:product_detail")

    def test_model_is_registered_as_real_store_database_model(self):
        field_names = {field.name for field in ProductCatalogProfile._meta.fields}
        for name in {
            "product", "public_slug", "desktop_product_id", "price_min", "price_max",
            "technical_features", "keywords", "homepage_slider_enabled", "last_synced_at",
        }:
            self.assertIn(name, field_names)
        self.assertEqual(ProductCatalogProfile._meta.app_label, "store")


class Epic49MigrationContractTests(TestCase):
    def test_migration_0028_is_present_and_additive(self):
        root = Path(__file__).resolve().parent
        migration = (root / "migrations" / "0028_epic49_catalog_product_schema.py").read_text(encoding="utf-8")
        self.assertIn("migrations.CreateModel", migration)
        self.assertIn('name="ProductCatalogProfile"', migration)
        self.assertIn("migrations.RunPython(backfill_catalog_profiles, noop_reverse)", migration)
        self.assertNotIn("DeleteModel", migration)
        self.assertNotIn("RemoveField", migration)
