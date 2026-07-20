from decimal import Decimal

from django.test import TestCase

from website.models import Material

from .models import Category, PricingSetting, PrintQuality, Product, ProductVariant


class ProductPricingTests(TestCase):
    def setUp(self):
        PricingSetting.objects.create(
            default_hourly_rate=100_000,
            default_labor_percent=Decimal("30"),
            minimum_order_amount=0,
        )
        self.material = Material.objects.create(
            name="PET-CF TEST",
            price_per_kg=4_000_000,
            strength=5,
            heat_resistance=4,
            flexibility=0,
            chemical_resistance=4,
            printability=4,
            main_usage="test",
            sample_parts="test",
        )
        self.quality = PrintQuality.objects.create(code="standard-test", name="استاندارد")
        self.category = Category.objects.create(name="تست", slug="test", section="industrial")
        self.product = Product.objects.create(
            category=self.category,
            title="محصول تست",
            slug="test-product",
            sku="TEST-001",
            short_description="test",
            description="test",
            main_image="store/products/test.webp",
        )

    def test_requested_pricing_example_equals_182000(self):
        variant = ProductVariant.objects.create(
            product=self.product,
            material=self.material,
            quality=self.quality,
            code="TEST-VAR-001",
            material_weight_grams=Decimal("10"),
            final_weight_grams=Decimal("10"),
            print_time_minutes=60,
        )
        breakdown = variant.price_breakdown()
        self.assertEqual(breakdown["material_cost"], 40_000)
        self.assertEqual(breakdown["machine_cost"], 100_000)
        self.assertEqual(breakdown["labor_cost"], 42_000)
        self.assertEqual(breakdown["unit_price"], 182_000)
        self.assertEqual(variant.cached_unit_price, 182_000)
