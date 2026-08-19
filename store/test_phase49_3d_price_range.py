from __future__ import annotations

import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from store.epic49_catalog_profile import ProductCatalogProfile
from store.models import Category, Product


class Phase493DPriceRangePublicTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.media.name, ALLOWED_HOSTS=["testserver"])
        self.override.enable()
        self.category = Category.objects.create(
            name="دکور",
            slug="decor-phase493d",
            section="creative",
            is_active=True,
        )
        self.product = Product.objects.create(
            category=self.category,
            title="استند نمایش سه‌بعدی",
            title_en="3D Display Stand",
            slug="phase493d-display-stand",
            sku="P493D-PRICE-1",
            short_description="استند قابل سفارش برای چاپ سه‌بعدی",
            description="توضیحات فارسی محصول",
            main_image=SimpleUploadedFile(
                "stand.jpg",
                b"fake-image-content",
                content_type="image/jpeg",
            ),
            is_active=True,
            fixed_price=450000,
            robots_index=True,
            robots_follow=True,
        )
        ProductCatalogProfile.objects.create(
            product=self.product,
            public_slug=self.product.slug,
            legacy_slug="",
            product_type="ready_product",
            price_min=450000,
            price_max=750000,
            price_mode="range",
        )

    def tearDown(self):
        self.override.disable()
        self.media.cleanup()

    def test_store_list_shows_full_price_range(self):
        response = self.client.get(reverse("store:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "بازه قیمت")
        self.assertContains(response, "450,000")
        self.assertContains(response, "750,000")

    def test_product_detail_shows_full_price_range(self):
        response = self.client.get(self.product.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "بازه قیمت")
        self.assertContains(response, "450,000")
        self.assertContains(response, "750,000")


if __name__ == "__main__":
    import unittest
    unittest.main()
