from __future__ import annotations

import json

from django.test import TestCase, override_settings

from store.epic49_catalog_profile import ProductCatalogProfile
from store.models import Category, ImportedPrintAsset, ImportedPrintAssetImage, PrintCatalogSource, Product
from website.models import HomepageHeroSlide


TOKEN = "epic49-test-token-12345678901234567890"
HEADERS = {"HTTP_AUTHORIZATION": f"Bearer {TOKEN}"}


@override_settings(CATALOG_BRIDGE_TOKEN=TOKEN)
class Epic49UnifiedBridgeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="قطعات تست Bridge", slug="bridge-category")
        cls.product = Product.objects.create(
            category=cls.category,
            title="محصول تست Bridge",
            title_en="Bridge Product EN",
            slug="bridge-product",
            sku="BRIDGE-001",
            short_description="توضیح کوتاه محصول Bridge",
            description="توضیحات کامل محصول Bridge",
            meta_title="خرید محصول تست Bridge",
            main_image="store/products/bridge.jpg",
            is_active=True,
        )
        cls.source = PrintCatalogSource.objects.create(
            name="Bridge Source",
            code="bridge-source",
            base_url="https://example.com/",
        )
        cls.asset = ImportedPrintAsset.objects.create(
            source=cls.source,
            source_url="https://example.com/models/bridge",
            external_id="BRIDGE-ASSET-001",
            title="Bridge Asset",
            persian_title="محصول فارسی Bridge",
            persian_short_description="توضیح فارسی اختصاصی محصول Bridge",
            product=cls.product,
        )
        cls.image = ImportedPrintAssetImage.objects.create(
            asset=cls.asset,
            remote_url="https://example.com/images/bridge.jpg",
            image="store/imported-models/gallery/bridge.jpg",
            alt_text="تصویر اسلایدر محصول Bridge",
            is_selected=True,
            is_primary=True,
        )
        cls.profile = ProductCatalogProfile.objects.create(
            product=cls.product,
            public_slug="bridge-product-public",
            legacy_slug=cls.product.slug,
            homepage_slider_enabled=True,
            homepage_slider_title_fa="عنوان اسلایدر Bridge",
            homepage_slider_description_fa="توضیح فارسی اسلایدر Bridge برای خرید محصول",
            homepage_slider_alt_text="تصویر محصول Bridge برای خرید و سفارش",
            homepage_slider_focus_keyword="خرید محصول Bridge",
            homepage_slider_button_text="مشاهده محصول",
            sync_revision=3,
            last_modified_source="desktop",
        )
        cls.slide = HomepageHeroSlide.objects.create(
            asset=cls.asset,
            selected_asset_image=cls.image,
            title_override="عنوان اسلایدر Bridge",
            description="توضیح فارسی اسلایدر Bridge برای خرید محصول",
            image_alt_text="تصویر محصول Bridge برای خرید و سفارش",
            button_text="مشاهده محصول",
            transition_effect="cinematic_fade",
            transition_duration_ms=1400,
            display_duration_ms=7000,
            sync_revision=2,
            is_active=True,
        )

        cls.other_product = Product.objects.create(
            category=cls.category,
            title="محصول دیگر",
            slug="other-product",
            sku="BRIDGE-OTHER",
            short_description="توضیح محصول دیگر",
            description="توضیحات محصول دیگر",
            main_image="store/products/other.jpg",
            is_active=True,
        )
        cls.other_asset = ImportedPrintAsset.objects.create(
            source=cls.source,
            source_url="https://example.com/models/other",
            external_id="BRIDGE-ASSET-OTHER",
            title="Other Asset",
            persian_title="محصول فارسی دیگر",
            product=cls.other_product,
        )
        cls.other_image = ImportedPrintAssetImage.objects.create(
            asset=cls.other_asset,
            remote_url="https://example.com/images/other.jpg",
            image="store/imported-models/gallery/other.jpg",
            alt_text="تصویر محصول دیگر",
        )

    def _post(self, path, payload):
        return self.client.post(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            **HEADERS,
        )

    def test_management_endpoints_require_existing_bridge_token(self):
        response = self.client.get("/api/catalog-bridge/v1/products/")
        self.assertEqual(response.status_code, 401)
        response = self.client.get("/api/catalog-bridge/v1/hero-slides/")
        self.assertEqual(response.status_code, 401)

    def test_product_and_hero_can_be_read_with_unified_contract(self):
        products = self.client.get("/api/catalog-bridge/v1/products/?q=BRIDGE-001", **HEADERS)
        self.assertEqual(products.status_code, 200)
        payload = products.json()
        self.assertEqual(payload["contract"], "epic49-unified-v1")
        match = next(item for item in payload["items"] if item["id"] == self.product.pk)
        self.assertEqual(match["profile"]["sync_revision"], 3)
        self.assertEqual(match["hero_revision"], 2)
        self.assertEqual(match["images"][0]["id"], self.image.pk)

        slides = self.client.get("/api/catalog-bridge/v1/hero-slides/", **HEADERS)
        self.assertEqual(slides.status_code, 200)
        row = next(item for item in slides.json()["items"] if item["id"] == self.slide.pk)
        self.assertEqual(row["focus_keyword"], "خرید محصول Bridge")
        self.assertEqual(row["sync_revision"], 2)

    def test_product_update_increments_revision_and_stale_update_returns_409(self):
        path = f"/api/catalog-bridge/v1/products/{self.product.pk}/sync/"
        response = self._post(path, {
            "expected_revision": 3,
            "operator": "employee-02",
            "product": {
                "title": "عنوان جدید از Windows",
                "meta_title": "خرید عنوان جدید از Windows",
                "meta_description": "توضیح فارسی فروش برای عنوان جدید از Windows",
            },
            "profile": {
                "homepage_slider_title_fa": "عنوان جدید اسلایدر",
                "homepage_slider_alt_text": "تصویر جدید اسلایدر برای خرید محصول",
                "homepage_slider_focus_keyword": "خرید عنوان جدید",
                "homepage_slider_transition_effect": "cinematic_zoom",
                "homepage_slider_transition_duration_ms": 1900,
                "homepage_slider_display_duration_ms": 8800,
            },
        })
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.product.title, "عنوان جدید از Windows")
        self.assertEqual(self.profile.sync_revision, 4)
        self.assertEqual(self.profile.last_modified_source, "desktop")
        self.assertEqual(self.profile.last_modified_by, "employee-02")
        self.assertEqual(self.profile.homepage_slider_transition_effect, "cinematic_zoom")
        self.assertEqual(self.profile.homepage_slider_focus_keyword, "خرید عنوان جدید")

        stale = self._post(path, {
            "expected_revision": 3,
            "operator": "stale-employee",
            "product": {"title": "نباید ذخیره شود"},
        })
        self.assertEqual(stale.status_code, 409)
        conflict = stale.json()
        self.assertEqual(conflict["status"], "conflict")
        self.assertEqual(conflict["current_revision"], 4)
        self.product.refresh_from_db()
        self.assertEqual(self.product.title, "عنوان جدید از Windows")

    def test_hero_update_uses_independent_revision_and_validates_image_ownership(self):
        path = f"/api/catalog-bridge/v1/hero-slides/{self.slide.pk}/sync/"
        response = self._post(path, {
            "expected_revision": 2,
            "operator": "employee-slider",
            "slide": {
                "title_override": "عنوان اسلایدر از Windows",
                "description": "توضیح فارسی اسلایدر از Windows برای خرید و سفارش محصول",
                "image_alt_text": "تصویر اسلایدر از Windows برای خرید محصول",
                "focus_keyword": "خرید محصول از Windows",
                "selected_asset_image_id": self.image.pk,
                "transition_effect": "wedding_dissolve",
                "transition_duration_ms": 2100,
                "display_duration_ms": 9200,
                "sort_order": 7,
                "is_active": True,
            },
        })
        self.assertEqual(response.status_code, 200)
        self.slide.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.slide.sync_revision, 3)
        self.assertEqual(self.slide.last_modified_source, "desktop")
        self.assertEqual(self.slide.last_modified_by, "employee-slider")
        self.assertEqual(self.slide.transition_effect, "wedding_dissolve")
        self.assertEqual(self.profile.homepage_slider_focus_keyword, "خرید محصول از Windows")
        self.assertEqual(self.profile.homepage_slider_title_fa, "عنوان اسلایدر از Windows")

        stale = self._post(path, {
            "expected_revision": 2,
            "slide": {"title_override": "نسخه قدیمی"},
        })
        self.assertEqual(stale.status_code, 409)

        wrong_image = self._post(path, {
            "expected_revision": 3,
            "slide": {"selected_asset_image_id": self.other_image.pk},
        })
        self.assertEqual(wrong_image.status_code, 404)
        self.slide.refresh_from_db()
        self.assertEqual(self.slide.selected_asset_image_id, self.image.pk)
        self.assertEqual(self.slide.sync_revision, 3)
