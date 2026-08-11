from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from tempfile import TemporaryDirectory

from website.models import Material
from store.models import Category, FilamentSpool, PricingSetting, PrintQuality, Product, ProductVariant, ShippingMethod
from store.phase39_models import (
    AccessoryComponent, MaterialColorOption, ProductBOMItem,
    ProductMaterialRecommendation, ProductPromotion, ShippingRateRule,
)


TINY_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class Phase39CommerceTests(TestCase):
    def setUp(self):
        self._media = TemporaryDirectory()
        self._media_override = override_settings(MEDIA_ROOT=self._media.name)
        self._media_override.enable()
        self.addCleanup(self._media_override.disable)
        self.addCleanup(self._media.cleanup)
        self.material = Material.objects.create(
            name="PLA Test", price_per_kg=500000, sale_price_per_gram=600,
            main_usage="دکور", sample_parts="تست",
        )
        self.quality = PrintQuality.objects.create(code="std", name="استاندارد")
        self.category = Category.objects.create(name="تست", slug="phase39-test", section="general")
        self.product = Product.objects.create(
            category=self.category, title="محصول تست", slug="phase39-product", sku="P39-1",
            short_description="تست", description="تست",
            main_image=SimpleUploadedFile("tiny.gif", TINY_GIF, content_type="image/gif"),
        )

    def test_pricing_default_vat_is_ten(self):
        pricing = PricingSetting.load()
        self.assertTrue(pricing.vat_enabled)
        self.assertEqual(Decimal(pricing.tax_percent), Decimal("10.00"))

    def test_color_stock_comes_from_real_spools(self):
        color = MaterialColorOption.objects.create(material=self.material, name="سفید", code="white")
        FilamentSpool.objects.create(material=self.material, color_name="سفید", nominal_weight_grams=1000, remaining_weight_grams=700)
        FilamentSpool.objects.create(material=self.material, color_name="مشکی", nominal_weight_grams=1000, remaining_weight_grams=400)
        self.assertEqual(Decimal(color.current_stock_grams), Decimal("700"))
        self.assertEqual(color.current_roll_count, 1)

    def test_shipping_weight_rule(self):
        shipping = ShippingMethod.objects.create(code="post", title="پست", flat_fee=10000)
        ShippingRateRule.objects.create(
            shipping_method=shipping, title="تا دو کیلو", min_weight_grams=0, max_weight_grams=2000,
            base_fee=40000, per_kg_fee=10000,
        )
        self.assertEqual(shipping.calculate_fee(100000, Decimal("1500")), 55000)

    def test_variant_price_includes_color_bom_assembly_and_profit(self):
        pricing = PricingSetting.load()
        pricing.default_hourly_rate = 60000
        pricing.default_labor_percent = 0
        pricing.assembly_hourly_rate = 60000
        pricing.minimum_order_amount = 0
        pricing.save()
        color = MaterialColorOption.objects.create(
            material=self.material, name="سفید", code="white", sale_price_per_gram_override=Decimal("700")
        )
        component = AccessoryComponent.objects.create(
            name="LED", sku="LED-TEST", unit_cost=20000, default_sale_price=30000,
        )
        ProductBOMItem.objects.create(product=self.product, component=component, quantity=1, assembly_minutes=30)
        variant = ProductVariant.objects.create(
            product=self.product, material=self.material, quality=self.quality, color=color,
            code="P39-PLA-WHITE", material_weight_grams=100, final_weight_grams=110,
            shipping_weight_grams=150, print_time_minutes=60,
        )
        breakdown = variant.price_breakdown()
        self.assertEqual(breakdown["material_cost"], 70000)
        self.assertEqual(breakdown["machine_cost"], 60000)
        self.assertEqual(breakdown["accessory_sale"], 30000)
        self.assertEqual(breakdown["assembly_cost"], 30000)
        self.assertGreater(breakdown["unit_price"], 0)
        self.assertIn("estimated_cost", breakdown)
        self.assertIn("gross_profit", breakdown)

    def test_material_recommendation_and_promotion(self):
        rec = ProductMaterialRecommendation.objects.create(
            product=self.product, material=self.material, recommendation="best", suitability_score=95,
            customer_note="برای این کاربرد اقتصادی و مناسب است.",
        )
        self.assertEqual(rec.recommendation, "best")
        promo = ProductPromotion.objects.create(product=self.product, kind="sale", discount_percent=10)
        self.assertTrue(promo.is_current)
        self.assertEqual(promo.apply(100000), 90000)

    def test_phase39_fields_exist(self):
        for name in ["color", "material_price_per_gram_override", "color_price_adjustment", "assembly_fee_override", "cached_cost_price"]:
            ProductVariant._meta.get_field(name)
        for name in ["editorial_source_url", "hashtags", "show_public_order_count", "customer_gallery_enabled"]:
            Product._meta.get_field(name)
