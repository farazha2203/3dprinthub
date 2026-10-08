import json
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from store.models import Category, PricingSetting, PrintQuality, Product, ProductReview, ProductVariant
from store.templatetags.store_seo import organization_schema_json, product_schema_json
from website.models import Material, SEOSettings

@override_settings(SECURE_SSL_REDIRECT=False)
class ProductSchemaTests(TestCase):
    def setUp(self):
        PricingSetting.objects.create(default_hourly_rate=100000,default_labor_percent=Decimal("30"))
        m=Material.objects.create(name="PETG",price_per_kg=1000000,strength=1,heat_resistance=1,flexibility=1,chemical_resistance=1,printability=1,main_usage="test",sample_parts="test")
        q=PrintQuality.objects.create(code="std",name="استاندارد")
        c=Category.objects.create(name="قطعات صنعتی",slug="industrial",section="industrial")
        image=SimpleUploadedFile("p.jpg",b"file",content_type="image/jpeg")
        self.product=Product.objects.create(category=c,title="چرخ دنده تست",slug="gear",sku="P-1",short_description="قطعه تست",description="توضیح",main_image=image)
        self.variant=ProductVariant.objects.create(product=self.product,material=m,quality=q,code="P-1-PETG",material_weight_grams=Decimal("10"),final_weight_grams=Decimal("10"),print_time_minutes=60,cached_unit_price=250000)
        self.seo=SEOSettings.objects.create(site_url="https://3dprinthub.ir",organization_name="3DprintHub")
    def test_product_group_schema_has_offer_and_breadcrumb(self):
        request=RequestFactory().get("/store/product/gear/",HTTP_HOST="testserver")
        data=json.loads(str(product_schema_json(self.product,[self.variant],request,self.seo)))
        graph=data["@graph"]
        self.assertEqual(graph[0]["@type"],"ProductGroup")
        self.assertEqual(graph[0]["hasVariant"][0]["offers"]["priceCurrency"],"IRR")
        self.assertEqual(graph[1]["@type"],"BreadcrumbList")

    def test_unconfigured_shipping_cost_is_not_published_as_free_in_schema(self):
        self.seo.shipping_rate = 0
        request=RequestFactory().get("/store/product/gear/",HTTP_HOST="testserver")
        data=json.loads(str(product_schema_json(self.product,[self.variant],request,self.seo)))
        offer=data["@graph"][0]["hasVariant"][0]["offers"]
        self.assertNotIn("shippingDetails", offer)

    def test_variant_schema_has_direct_preselect_url_and_merchant_fields(self):
        request=RequestFactory().get("/store/product/gear/",HTTP_HOST="testserver")
        data=json.loads(str(product_schema_json(self.product,[self.variant],request,self.seo)))
        variant=data["@graph"][0]["hasVariant"][0]

        self.assertEqual(
            variant["url"],
            "http://testserver/store/product/gear/?variant=P-1-PETG",
        )
        self.assertEqual(variant["offers"]["url"], variant["url"])
        self.assertEqual(len(variant["image"]), 1)
        self.assertTrue(
            variant["image"][0].startswith(
                "http://testserver/media/store/products/"
            )
        )
        self.assertEqual(variant["description"], self.product.short_description)
        self.assertEqual(variant["brand"]["name"], "3DprintHub")
        self.assertGreater(variant["offers"]["price"], 0)

    def test_zero_price_variant_is_not_advertised_as_merchant_offer(self):
        self.variant.cached_unit_price=0
        self.variant.price_breakdown = lambda: {"unit_price": 0}
        request=RequestFactory().get("/store/product/gear/",HTTP_HOST="testserver")
        data=json.loads(str(product_schema_json(self.product,[self.variant],request,self.seo)))

        self.assertNotIn("hasVariant", data["@graph"][0])

    def test_organization_schema_omits_unverified_return_policy_and_search_action(self):
        request=RequestFactory().get("/",HTTP_HOST="testserver")
        data=json.loads(str(organization_schema_json(self.seo,request)))
        organization, website=data["@graph"]

        self.assertNotIn("hasMerchantReturnPolicy", organization)
        self.assertNotIn("potentialAction", website)

    def test_variant_query_preselects_the_real_native_variant(self):
        self.seo.allow_search_indexing=True
        self.seo.save()
        response=self.client.get(
            self.product.get_absolute_url(),
            {"variant": self.variant.code},
        )
        body=response.content.decode()

        self.assertEqual(response.status_code,200)
        self.assertIn(
            f'<option value="{self.variant.id}" selected',
            body,
        )
        self.assertIn(
            f"?variant={self.variant.code}",
            body,
        )

    def test_product_image_sitemap_contains_only_public_product_media(self):
        response=self.client.get("/sitemap-images.xml")
        body=response.content.decode()

        self.assertEqual(response.status_code,200)
        self.assertIn("application/xml",response["Content-Type"])
        self.assertIn(
            "http://testserver/store/product/gear/",
            body,
        )
        self.assertIn(
            "http://testserver/media/store/products/",
            body,
        )
        self.assertNotIn("private-models",body)

    def test_store_search_and_filter_urls_are_noindex_with_canonical_base(self):
        self.seo.allow_search_indexing=True
        self.seo.save()

        response=self.client.get("/store/",{"q":"gear","sort":"popular"})
        body=response.content.decode()

        self.assertEqual(response.status_code,200)
        self.assertIn(
            'meta name="robots" content="noindex,follow"',
            body,
        )
        self.assertIn(
            'rel="canonical" href="http://testserver/store/"',
            body,
        )

    def test_variant_family_uses_individual_offers_not_aggregate_offer(self):
        request = RequestFactory().get("/store/product/gear/", HTTP_HOST="testserver")
        data = json.loads(str(product_schema_json(self.product, [self.variant], request, self.seo)))
        family = data["@graph"][0]
        self.assertEqual(family["@type"], "ProductGroup")
        self.assertNotIn("offers", family)
        variant = family["hasVariant"][0]
        self.assertEqual(variant["@type"], "Product")
        self.assertEqual(variant["offers"]["@type"], "Offer")
        self.assertEqual(variant["offers"]["price"], self.variant.cached_unit_price * 10)

    def test_direct_fixed_price_exposes_real_single_product_offer(self):
        self.product.order_mode = "fixed"
        self.product.fixed_price = 123456
        self.product.save(update_fields=["order_mode", "fixed_price"])
        request = RequestFactory().get("/store/product/gear/", HTTP_HOST="testserver")
        data = json.loads(str(product_schema_json(self.product, [self.variant], request, self.seo)))
        product = data["@graph"][0]
        self.assertEqual(product["@type"], "Product")
        self.assertNotIn("hasVariant", product)
        self.assertNotIn("productGroupID", product)
        self.assertEqual(product["offers"]["@type"], "Offer")
        self.assertEqual(product["offers"]["price"], 1234560)
        self.assertEqual(product["offers"]["priceCurrency"], "IRR")

    def test_unknown_price_never_creates_incomplete_product_or_fake_offer(self):
        self.variant.cached_unit_price = 0
        self.variant.price_breakdown = lambda: {"unit_price": 0}
        request = RequestFactory().get("/store/product/gear/", HTTP_HOST="testserver")
        data = json.loads(str(product_schema_json(self.product, [self.variant], request, self.seo)))
        self.assertEqual([item["@type"] for item in data["@graph"]], ["BreadcrumbList"])

    def test_approved_genuine_review_allows_review_only_product(self):
        self.variant.cached_unit_price = 0
        self.variant.price_breakdown = lambda: {"unit_price": 0}
        user = User.objects.create_user(username="real_customer", password="test-pass")
        ProductReview.objects.create(
            product=self.product,
            user=user,
            rating=4,
            body="Real customer review",
            is_approved=True,
        )
        request = RequestFactory().get("/store/product/gear/", HTTP_HOST="testserver")
        data = json.loads(str(product_schema_json(self.product, [self.variant], request, self.seo)))
        product = data["@graph"][0]
        self.assertEqual(product["@type"], "Product")
        self.assertNotIn("offers", product)
        self.assertEqual(product["aggregateRating"]["reviewCount"], 1)
        self.assertEqual(product["review"][0]["reviewRating"]["ratingValue"], 4)

    def test_default_price_and_google_offer_use_same_first_orderable_variant(self):
        import re

        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn(f'data-default-variant-id="{self.variant.id}"', body)
        self.assertIn(f'<option value="{self.variant.id}" selected', body)
        self.assertIn(f'data-total="{self.variant.price_breakdown()["unit_price"]}"', body)
        schemas = [
            json.loads(source)
            for source in re.findall(r'<script type="application/ld[+]json">(.*?)</script>', body, re.S)
        ]
        family = next(
            item
            for schema in schemas
            for item in schema.get("@graph", [])
            if item.get("@type") == "ProductGroup"
        )
        self.assertEqual(
            family["hasVariant"][0]["offers"]["price"],
            self.variant.price_breakdown()["unit_price"] * 10,
        )

    def test_first_filament_then_profile_then_real_first_color_is_default(self):
        from unittest.mock import patch
        from store.phase39_models import MaterialColorOption

        self.variant.material.sort_order = 90
        self.variant.material.save(update_fields=["sort_order"])
        preferred = Material.objects.create(
            name="PLA-FIRST", price_per_kg=1000000, sort_order=1,
            strength=1, heat_resistance=1, flexibility=1,
            chemical_resistance=1, printability=1, main_usage="test", sample_parts="test",
        )
        later_color = MaterialColorOption.objects.create(
            material=preferred, name="Red", code="red", sort_order=20
        )
        earlier_color = MaterialColorOption.objects.create(
            material=preferred, name="Blue", code="blue", sort_order=10
        )
        later = ProductVariant.objects.create(
            product=self.product, material=preferred, quality=self.variant.quality,
            color=later_color, code="P-1-PLA-LATER", sales_profile_sort_order=10,
            material_weight_grams=Decimal("12"), final_weight_grams=Decimal("12"),
            print_time_minutes=60,
        )
        earlier = ProductVariant.objects.create(
            product=self.product, material=preferred, quality=self.variant.quality,
            color=earlier_color, code="P-1-PLA-FIRST", sales_profile_sort_order=10,
            material_weight_grams=Decimal("12"), final_weight_grams=Decimal("12"),
            print_time_minutes=60,
        )
        # Selection-order test only: real color-stock orderability is covered
        # by the separate fallback test and remains enforced in production.
        with patch("store.phase50_public_offer.variant_is_orderable", return_value=True):
            response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn(f'data-default-variant-id="{earlier.id}"', body)
        self.assertIn(f'<option value="{earlier.id}" selected', body)
        self.assertNotIn(f'data-default-variant-id="{later.id}"', body)

    def test_no_unavailable_or_unpriced_default_but_query_override_works(self):
        other_material = Material.objects.create(
            name="PETG-FALLBACK", price_per_kg=1000000, sort_order=50,
            strength=1, heat_resistance=1, flexibility=1,
            chemical_resistance=1, printability=1, main_usage="test", sample_parts="test",
        )
        fallback = ProductVariant.objects.create(
            product=self.product, material=other_material, quality=self.variant.quality,
            code="P-1-FALLBACK", material_weight_grams=Decimal("10"),
            final_weight_grams=Decimal("10"), print_time_minutes=60,
        )
        self.variant.stock_status = "out_of_stock"
        self.variant.save(update_fields=["stock_status"])
        response = self.client.get(self.product.get_absolute_url())
        self.assertIn(
            f'data-default-variant-id="{fallback.id}"',
            response.content.decode(),
        )
        # Google must prefer the same first orderable Offer, and mark the
        # skipped variant unavailable without inventing stock.
        import re
        body = response.content.decode()
        graphs = [
            json.loads(source) for source in re.findall(
                r'<script type="application/ld[+]json">(.*?)</script>', body, re.S
            )
        ]
        family = next(
            node for graph in graphs for node in graph.get("@graph", [])
            if node.get("@type") == "ProductGroup"
        )
        self.assertEqual(
            family["hasVariant"][0]["sku"], fallback.code
        )
        self.assertEqual(
            next(node for node in family["hasVariant"]
                 if node["sku"] == self.variant.code)["offers"]["availability"],
            "https://schema.org/OutOfStock",
        )
        self.variant.stock_status = "made_to_order"
        self.variant.save(update_fields=["stock_status"])
        response = self.client.get(
            self.product.get_absolute_url(), {"variant": fallback.code}
        )
        self.assertIn(
            f'<option value="{fallback.id}" selected',
            response.content.decode(),
        )

    def test_google_offer_uses_current_customer_price_not_stale_cached_price(self):
        self.variant.cached_unit_price = 1
        self.variant.price_breakdown = lambda: {"unit_price": 270000}
        request = RequestFactory().get("/store/product/gear/", HTTP_HOST="testserver")
        data = json.loads(str(product_schema_json(self.product, [self.variant], request, self.seo)))
        self.assertEqual(
            data["@graph"][0]["hasVariant"][0]["offers"]["price"],
            2700000,
        )
