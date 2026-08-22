from __future__ import annotations

from types import SimpleNamespace

from django.test import TestCase

from store import epic49_catalog_profile, epic49_publish_options
from store.epic49_catalog_profile import ProductCatalogProfile
from store.models import Category, Product


class Phase493IServerPricingTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="دکور", slug="decor-49i")
        self.product = Product.objects.create(
            category=self.category,
            title="استند کیک",
            slug="cake-stand-49i",
            sku="EP49-3I-CAKE",
            short_description="استند کیک چاپ سه‌بعدی",
            description="شرح",
            fixed_price=500000,
            source_url="https://makerworld.com/en/models/2845731-cake-stand",
            source_name="MakerWorld",
            source_attribution="MakerWorld",
        )
        self.asset = SimpleNamespace(
            fixed_print_price=0,
            commercial_license_status="unknown",
            license_name="",
            license_url="",
            technical_specs={},
            source_payload={},
        )

    def test_runtime_pricing_strategy_choices_include_range(self):
        field = ProductCatalogProfile._meta.get_field("pricing_strategy")
        choices = {code: label for code, label in field.choices}
        self.assertIn("fixed", choices)
        self.assertIn("range", choices)
        self.assertIn("dynamic", choices)

    def test_range_publish_uses_existing_consultation_contract(self):
        minimum, maximum = epic49_publish_options.apply_price_range(
            self.product,
            self.asset,
            {
                "pricing_strategy": "range",
                "price_min": 200000,
                "price_max": 500000,
                "price_is_final": 0,
            },
        )
        self.product.refresh_from_db()
        self.assertEqual((minimum, maximum), (200000, 500000))
        self.assertEqual(self.product.fixed_price, 200000)
        self.assertFalse(self.product.price_is_final)
        self.assertTrue(self.product.consultation_required)
        self.assertIn("200,000", self.product.price_note)
        self.assertIn("500,000", self.product.price_note)

    def test_profile_preserves_explicit_range_mode(self):
        profile = epic49_catalog_profile.sync_catalog_profile(
            self.product,
            self.asset,
            {
                "pricing_strategy": "range",
                "price_min": 200000,
                "price_max": 500000,
                "product_type": "ready_product",
                "availability_status": "made_to_order",
                "desktop_product_id": 49301,
            },
            price_min=200000,
            price_max=500000,
        )
        self.assertEqual(profile.pricing_strategy, "range")
        self.assertEqual(profile.price_mode, "range")
        self.assertEqual(profile.price_min, 200000)
        self.assertEqual(profile.price_max, 500000)

    def test_range_strategy_is_not_dynamic_formula_strategy(self):
        profile = ProductCatalogProfile.objects.create(
            product=self.product,
            public_slug="cake-stand-49i-range",
            pricing_strategy="range",
            price_mode="range",
            price_min=200000,
            price_max=500000,
        )
        self.assertNotEqual(profile.pricing_strategy, "dynamic")
        self.assertEqual(profile.price_mode, "range")


if __name__ == "__main__":
    import unittest
    unittest.main()
