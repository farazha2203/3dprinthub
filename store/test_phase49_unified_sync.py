from __future__ import annotations

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase

from store.epic49_catalog_profile import ProductCatalogProfile
from store.epic49_publish_options import sync_epic49_publish_options
from store.models import Category, ImportedPrintAsset, ImportedPrintAssetImage, PrintCatalogSource, Product
from website.models import HomepageHeroSlide


class Epic49UnifiedSyncBehaviorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username="epic49-manager",
            email="epic49@example.com",
            password="StrongTestPass123!",
        )
        cls.category = Category.objects.create(name="Epic49 Unified", slug="epic49-unified")
        cls.product = Product.objects.create(
            category=cls.category,
            title="محصول Epic49",
            title_en="Epic49 Unified Product",
            slug="epic49-unified-product",
            sku="EP49-U-001",
            short_description="توضیح محصول",
            description="توضیحات کامل محصول",
            fixed_price=900000,
            main_image="store/products/epic49-unified.jpg",
            is_active=True,
        )
        cls.source = PrintCatalogSource.objects.create(
            name="Epic49 Source",
            code="epic49-unified-source",
            base_url="https://example.com/",
        )
        # Create without desktop payload so the post_save publish signal cannot
        # mutate state before this test explicitly invokes the unified service.
        cls.asset = ImportedPrintAsset.objects.create(
            source=cls.source,
            source_url="https://example.com/models/epic49",
            external_id="EP49-ASSET-001",
            title="Epic49 Source Product",
            persian_title="محصول فارسی Epic49",
            product=cls.product,
        )
        cls.image = ImportedPrintAssetImage.objects.create(
            asset=cls.asset,
            remote_url="https://example.com/images/epic49-hero.jpg",
            image="store/imported-models/gallery/epic49-hero.jpg",
            alt_text="تصویر Hero Epic49",
            is_primary=True,
            is_selected=True,
            sort_order=0,
        )

    def setUp(self):
        self.factory = RequestFactory()

    def _payload(self, *, batch="batch-a", source_hash="hash-a", product_revision=0, slider_revision=0, title="Hero A"):
        return {
            "desktop_product_id": 77,
            "batch_uuid": batch,
            "source_hash": source_hash,
            "server_product_revision": product_revision,
            "server_slider_revision": slider_revision,
            "product_type": "ready_product",
            "availability_status": "made_to_order",
            "commercial_status": "allowed",
            "download_image_limit": 10,
            "price_min": 900000,
            "price_max": 900000,
            "keywords_json": '["چاپ سه بعدی","Epic49"]',
            "tags_fa_json": '["تست"]',
            "technical_features_json": "{}",
            "material_color_options_json": "[]",
            "homepage_slider_enabled": True,
            "homepage_slider_image_url": self.image.remote_url,
            "homepage_slider_sort_order": 25,
            "homepage_slider_title_fa": title,
            "homepage_slider_description_fa": "توضیح اختصاصی Hero",
            "homepage_slider_alt_text": "Alt اختصاصی Hero",
            "homepage_slider_button_text": "مشاهده قطعه",
            "homepage_slider_focus_keyword": "Hero Epic49",
            "homepage_slider_transition_effect": "wedding_dissolve",
            "homepage_slider_transition_duration_ms": 1800,
            "homepage_slider_display_duration_ms": 8500,
            "seo_title_fa": "SEO محصول Epic49",
            "seo_description_fa": "توضیح SEO محصول Epic49",
            "operator_name": "employee-01",
        }

    def _set_payload(self, data):
        ImportedPrintAsset.objects.filter(pk=self.asset.pk).update(
            source_payload={"desktop_catalog_v85": data}
        )
        self.asset.refresh_from_db()

    def test_same_batch_is_idempotent_and_new_batch_increments_once(self):
        self._set_payload(self._payload())
        first = sync_epic49_publish_options(self.asset)
        profile = ProductCatalogProfile.objects.get(product=self.product)
        slide = HomepageHeroSlide.objects.get(asset=self.asset)
        self.assertEqual(profile.sync_revision, 1)
        self.assertEqual(slide.sync_revision, 1)
        self.assertEqual(slide.selected_asset_image_id, self.image.pk)
        self.assertEqual(slide.transition_effect, "wedding_dissolve")
        self.assertEqual(slide.transition_duration_ms, 1800)
        self.assertEqual(slide.display_duration_ms, 8500)
        self.assertEqual(profile.homepage_slider_focus_keyword, "Hero Epic49")
        self.assertEqual(first["product_revision"], 1)
        self.assertEqual(first["slider_revision"], 1)

        second = sync_epic49_publish_options(self.asset)
        profile.refresh_from_db()
        slide.refresh_from_db()
        self.assertEqual(profile.sync_revision, 1)
        self.assertEqual(slide.sync_revision, 1)
        self.assertEqual(second["product_revision"], 1)
        self.assertEqual(second["slider_revision"], 1)

        self._set_payload(self._payload(
            batch="batch-b",
            source_hash="hash-b",
            product_revision=1,
            slider_revision=1,
            title="Hero B",
        ))
        third = sync_epic49_publish_options(self.asset)
        profile.refresh_from_db()
        slide.refresh_from_db()
        self.assertEqual(profile.sync_revision, 2)
        self.assertEqual(slide.sync_revision, 2)
        self.assertEqual(slide.title_override, "Hero B")
        self.assertEqual(third["product_revision"], 2)
        self.assertEqual(third["slider_revision"], 2)

    def test_admin_product_edit_blocks_stale_desktop_batch(self):
        self._set_payload(self._payload())
        sync_epic49_publish_options(self.asset)
        profile = ProductCatalogProfile.objects.get(product=self.product)
        self.assertEqual(profile.sync_revision, 1)

        request = self.factory.post("/admin/store/product/")
        request.user = self.user
        product_admin = admin.site._registry[Product]
        self.product.title = "ویرایش انسانی مدیر"
        product_admin.save_model(request, self.product, form=None, change=True)
        profile.refresh_from_db()
        self.assertEqual(profile.sync_revision, 2)
        self.assertEqual(profile.last_modified_source, "admin")
        self.assertEqual(profile.last_modified_by, self.user.username)

        stale = self._payload(
            batch="batch-c",
            source_hash="hash-c",
            product_revision=1,
            slider_revision=1,
            title="نباید اعمال شود",
        )
        self._set_payload(stale)
        with self.assertRaisesMessage(ValidationError, "EPIC49_SYNC_CONFLICT"):
            sync_epic49_publish_options(self.asset)
        self.product.refresh_from_db()
        profile.refresh_from_db()
        self.assertEqual(self.product.title, "ویرایش انسانی مدیر")
        self.assertEqual(profile.sync_revision, 2)

    def test_profile_admin_and_hero_admin_keep_slider_mirror_aligned(self):
        self._set_payload(self._payload())
        sync_epic49_publish_options(self.asset)
        profile = ProductCatalogProfile.objects.get(product=self.product)
        slide = HomepageHeroSlide.objects.get(asset=self.asset)

        request = self.factory.post("/admin/store/productcatalogprofile/")
        request.user = self.user
        profile_admin = admin.site._registry[ProductCatalogProfile]
        profile.homepage_slider_title_fa = "عنوان از Profile Admin"
        profile.homepage_slider_description_fa = "توضیح از Profile Admin"
        profile.homepage_slider_transition_effect = "soft_blur"
        profile.homepage_slider_transition_duration_ms = 2200
        profile.homepage_slider_display_duration_ms = 9100
        profile_admin.save_model(request, profile, form=None, change=True)

        slide.refresh_from_db()
        profile.refresh_from_db()
        self.assertEqual(slide.title_override, "عنوان از Profile Admin")
        self.assertEqual(slide.transition_effect, "soft_blur")
        self.assertEqual(slide.transition_duration_ms, 2200)
        self.assertEqual(slide.display_duration_ms, 9100)
        self.assertEqual(slide.last_modified_source, "admin")

        hero_admin = admin.site._registry[HomepageHeroSlide]
        slide.description = "توضیح جدید از Hero Admin"
        slide.transition_effect = "cinematic_reveal"
        hero_admin.save_model(request, slide, form=None, change=True)
        profile.refresh_from_db()
        slide.refresh_from_db()
        self.assertEqual(profile.homepage_slider_description_fa, "توضیح جدید از Hero Admin")
        self.assertEqual(profile.homepage_slider_transition_effect, "cinematic_reveal")
        self.assertEqual(profile.last_modified_source, "admin")
        self.assertGreaterEqual(profile.sync_revision, 3)
        self.assertGreaterEqual(slide.sync_revision, 3)
