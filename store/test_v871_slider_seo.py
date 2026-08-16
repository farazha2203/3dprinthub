from __future__ import annotations

import json

from django.test import TestCase

from store.epic49_publish_options import sync_epic49_publish_options
from store.models import Category, ImportedPrintAsset, PrintCatalogSource, Product
from website.models import HomepageHeroSlide


class V871HomepageSliderSeoTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="دکور",
            slug="decor-v871",
            section="creative",
            is_active=True,
        )
        self.product = Product.objects.create(
            category=self.category,
            title="آباژور برگ‌دار",
            title_en="Leaf Lamp",
            slug="leaf-lamp-v871",
            sku="V871-SLIDER-1",
            short_description="آباژور چاپ سه‌بعدی برای دکور داخلی",
            description="توضیح محصول",
            fixed_price=350000,
            is_active=True,
        )
        self.source = PrintCatalogSource.objects.create(
            name="MakerWorld V871",
            code="makerworld-v871",
            base_url="https://makerworld.com",
            default_category=self.category,
            is_active=True,
        )

    def _asset(self, data: dict, external_id: str = "8711"):
        asset = ImportedPrintAsset.objects.create(
            source=self.source,
            source_url=f"https://makerworld.com/en/models/{external_id}",
            external_id=external_id,
            title="Leaf Lamp",
            source_title="Leaf Lamp",
            persian_title="آباژور برگ‌دار",
            fixed_print_price=350000,
            commercial_license_status="allowed",
            source_payload={"desktop_catalog_v85": data},
        )
        ImportedPrintAsset.objects.filter(pk=asset.pk).update(product_id=self.product.pk)
        asset.refresh_from_db()
        return asset

    def test_operator_approved_slider_copy_is_written_to_homepage_slide(self):
        data = {
            "desktop_product_id": 871,
            "product_type": "ready_product",
            "commercial_status": "allowed",
            "price_min": 350000,
            "price_max": 350000,
            "homepage_slider_enabled": True,
            "homepage_slider_sort_order": 12,
            "homepage_slider_title_fa": "آباژور برگ‌دار برای دکور مدرن",
            "homepage_slider_description_fa": "مدلی دکوراتیو برای چاپ سه‌بعدی و استفاده روی میز یا فضای داخلی.",
            "homepage_slider_alt_text": "آباژور برگ‌دار چاپ سه‌بعدی برای دکور داخلی",
            "homepage_slider_button_text": "مشاهده و سفارش",
            "homepage_slider_focus_keyword": "آباژور سه بعدی",
        }
        asset = self._asset(data)
        result = sync_epic49_publish_options(asset)
        slide = HomepageHeroSlide.objects.get(asset=asset)
        self.assertTrue(slide.is_active)
        self.assertEqual(slide.title_override, data["homepage_slider_title_fa"])
        self.assertEqual(slide.description, data["homepage_slider_description_fa"])
        self.assertEqual(slide.image_alt_text, data["homepage_slider_alt_text"])
        self.assertEqual(slide.button_text, data["homepage_slider_button_text"])
        self.assertEqual(slide.sort_order, 12)
        self.assertEqual(result["homepage_slider"]["focus_keyword"], "آباژور سه بعدی")
        self.assertEqual(slide.target_url, self.product.get_absolute_url())

    def test_ai_content_pack_is_backward_compatible_slider_copy_fallback(self):
        ai_slider = {
            "title_fa": "چراغ دکوراتیو چاپ سه‌بعدی",
            "description_fa": "یک انتخاب دکوراتیو برای فضای داخلی با امکان سفارش چاپ سه‌بعدی.",
            "image_alt_fa": "چراغ دکوراتیو سه‌بعدی روی پس‌زمینه روشن",
            "button_text_fa": "دیدن محصول",
            "focus_keyword_fa": "چراغ دکوراتیو سه بعدی",
        }
        data = {
            "desktop_product_id": 872,
            "product_type": "ready_product",
            "commercial_status": "allowed",
            "price_min": 350000,
            "price_max": 350000,
            "homepage_slider_enabled": True,
            "content_pack_json": json.dumps({"homepage_slider_seo": ai_slider}, ensure_ascii=False),
        }
        asset = self._asset(data, external_id="8712")
        sync_epic49_publish_options(asset)
        slide = HomepageHeroSlide.objects.get(asset=asset)
        self.assertEqual(slide.title_override, ai_slider["title_fa"])
        self.assertEqual(slide.description, ai_slider["description_fa"])
        self.assertEqual(slide.image_alt_text, ai_slider["image_alt_fa"])
        self.assertEqual(slide.button_text, ai_slider["button_text_fa"])


if __name__ == "__main__":
    import unittest
    unittest.main()
