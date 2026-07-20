import json
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from store.models import Category, PricingSetting, PrintQuality, Product, ProductReview, ProductVariant
from store.templatetags.store_seo import product_schema_json
from website.models import Material, SEOSettings

class ProductSchemaTests(TestCase):
    def setUp(self):
        PricingSetting.objects.create(default_hourly_rate=100000,default_labor_percent=Decimal("30"))
        m=Material.objects.create(name="PETG",price_per_kg=1000000,strength=1,heat_resistance=1,flexibility=1,chemical_resistance=1,printability=1,main_usage="test",sample_parts="test")
        q=PrintQuality.objects.create(code="std",name="استاندارد")
        c=Category.objects.create(name="قطعات صنعتی",slug="industrial",section="industrial")
        image=SimpleUploadedFile("p.jpg",b"file",content_type="image/jpeg")
        self.product=Product.objects.create(category=c,title="چرخ دنده تست",slug="gear",sku="P-1",short_description="قطعه تست",description="توضیح",main_image=image)
        self.variant=ProductVariant.objects.create(product=self.product,material=m,quality=q,code="P-1-PETG",material_weight_grams=Decimal("10"),final_weight_grams=Decimal("10"),print_time_minutes=60)
        self.seo=SEOSettings.objects.create(site_url="https://3dprinthub.ir",organization_name="3DprintHub")
    def test_product_group_schema_has_offer_and_breadcrumb(self):
        request=RequestFactory().get("/store/product/gear/",HTTP_HOST="testserver")
        data=json.loads(str(product_schema_json(self.product,[self.variant],request,self.seo)))
        graph=data["@graph"]
        self.assertEqual(graph[0]["@type"],"ProductGroup")
        self.assertEqual(graph[0]["hasVariant"][0]["offers"]["priceCurrency"],"IRR")
        self.assertEqual(graph[1]["@type"],"BreadcrumbList")
