from __future__ import annotations

import json
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from catalog_bridge import unified_views
from store.epic49_catalog_profile import ProductCatalogProfile
from store.models import Category, Product


class Phase493I52BBidirectionalBridgeTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="دکور Site Sync",
            slug="phase49-3i52b-decor",
            is_active=True,
        )
        self.factory = RequestFactory()
        self.products = []
        for index in range(3):
            product = Product.objects.create(
                category=self.category,
                title=f"محصول {index}",
                title_en=f"Product {index}",
                slug=f"phase49-3i52b-{index}",
                sku=f"P49I52B-{index}",
                fixed_price=500000 + index,
                source_name="MakerWorld",
                source_external_id=f"52B-{index}",
                source_url=f"https://makerworld.com/en/models/52b-{index}",
                is_active=True,
            )
            profile = ProductCatalogProfile.objects.create(
                product=product,
                public_slug=f"phase49-3i52b-{index}",
                sync_revision=index + 1,
            )
            profile.pricing_strategy = "dynamic"
            profile.pricing_inputs = {"part_weight_grams": 100 + index}
            profile.technical_summary_fa = f"خلاصه فنی {index}"
            profile.save()
            self.products.append((product, profile))

    def test_serialized_product_exposes_source_identity_and_full_pricing_profile(self):
        product, profile = self.products[0]
        payload = unified_views.serialize_product(product)
        self.assertEqual(payload["source_name"], "MakerWorld")
        self.assertEqual(payload["source_external_id"], "52B-0")
        self.assertEqual(payload["source_url"], "https://makerworld.com/en/models/52b-0")
        self.assertEqual(payload["category_slug"], self.category.slug)
        self.assertEqual(payload["profile"]["pricing_strategy"], "dynamic")
        self.assertEqual(payload["profile"]["pricing_inputs"]["part_weight_grams"], 100)
        self.assertEqual(payload["profile"]["technical_summary_fa"], "خلاصه فنی 0")

    def test_products_endpoint_has_deterministic_offset_pagination(self):
        request = self.factory.get(
            "/api/catalog-bridge/v1/products/?limit=2&offset=1"
        )
        with patch.object(unified_views, "_authorized", return_value=True):
            response = unified_views.products_view(request)
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["limit"], 2)
        self.assertEqual(payload["offset"], 1)
        self.assertEqual(payload["count"], 2)
        self.assertEqual(payload["total_count"], 3)
        self.assertFalse(payload["has_more"])

    def test_desktop_sync_round_trips_pricing_strategy_inputs_and_summary(self):
        product, profile = self.products[0]
        request = self.factory.post(
            f"/api/catalog-bridge/v1/products/{product.pk}/sync/",
            data=json.dumps({
                "expected_revision": profile.sync_revision,
                "operator": "desktop-phase52b",
                "profile": {
                    "price_min": 840000,
                    "price_max": 990000,
                    "price_mode": "range",
                    "pricing_strategy": "dynamic",
                    "pricing_inputs": {
                        "part_weight_grams": 125,
                        "support_weight_grams": 15,
                    },
                    "technical_summary_fa": "خلاصه جدید از Desktop",
                },
            }),
            content_type="application/json",
        )
        with patch.object(unified_views, "_authorized", return_value=True):
            response = unified_views.product_sync_view(request, product.pk)
        self.assertEqual(response.status_code, 200, response.content)
        profile.refresh_from_db()
        self.assertEqual(profile.price_min, 840000)
        self.assertEqual(profile.price_max, 990000)
        self.assertEqual(profile.price_mode, "range")
        self.assertEqual(profile.pricing_strategy, "dynamic")
        self.assertEqual(profile.pricing_inputs["part_weight_grams"], 125)
        self.assertEqual(profile.technical_summary_fa, "خلاصه جدید از Desktop")
        self.assertEqual(profile.sync_revision, 2)
