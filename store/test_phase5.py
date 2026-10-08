import json
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from store.models import Category, PricingSetting, PrintQuality, Product, ProductReview, ProductVariant
from store.templatetags.store_seo import organization_schema_json, product_schema_json
from website.models import Material, SEOSettings

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
