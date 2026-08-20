from __future__ import annotations

from decimal import Decimal
from importlib import import_module

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from store.epic49_catalog_profile import ProductCatalogProfile
from store.models import Category, PricingSetting, PrintQuality, Product, ProductVariant
from website.models import Material


class Phase493FPricingTests(TestCase):
    def setUp(self):
        pricing = PricingSetting.load()
        pricing.default_hourly_rate = 100_000
        pricing.minimum_billable_minutes = 60
        pricing.billing_increment_minutes = 60
        pricing.default_labor_percent = Decimal("30")
        pricing.minimum_order_amount = 0
        pricing.assembly_hourly_rate = 100_000
        pricing.save()

        self.category = Category.objects.create(name="اسباب‌بازی", slug="toys")
        self.product = Product.objects.create(
            category=self.category,
            title="گکو مفصلی",
            slug="flexi-gecko",
            sku="EP49-3F-GECKO",
            short_description="مدل سه‌بعدی مفصلی برای چاپ سفارشی",
            description="توضیحات محصول",
            main_image="store/products/flexi-gecko.jpg",
            fixed_price=900_000,
            source_url="https://example.com/flexi-gecko",
            source_name="Username",
            source_attribution="Username",
        )
        self.profile = ProductCatalogProfile.objects.create(
            product=self.product,
            public_slug="flexi-gecko",
            product_type="ready_product",
            availability_status="made_to_order",
            pricing_strategy="dynamic",
            technical_summary_fa="این محصول مفصلی است و برای چاپ سفارشی آماده می‌شود.",
        )
        self.material = Material.objects.create(
            name="PLA سفید مات",
            price_per_kg=2_600_000,
            sale_price_per_gram=0,
            print_hourly_rate_toman=150_000,
            supervision_hourly_rate_toman=50_000,
            main_usage="چاپ عمومی",
            sample_parts="فیگور و قطعات سبک",
        )
        self.quality = PrintQuality.objects.create(code="standard", name="استاندارد")
        self.variant = ProductVariant.objects.create(
            product=self.product,
            material=self.material,
            quality=self.quality,
            code="EP49-3F-TEST",
            material_weight_grams=Decimal("150"),
            final_weight_grams=Decimal("100"),
            shipping_weight_grams=Decimal("100"),
            print_time_minutes=180,
            part_weight_grams=Decimal("100"),
            support_weight_grams=Decimal("50"),
            support_cost_multiplier=Decimal("2"),
            hourly_rate_override=150_000,
            supervision_hourly_rate_override=50_000,
            assembly_fee_override=0,
            post_processing_fee=0,
            fixed_fee=0,
            color_price_adjustment=0,
            is_active=True,
        )

    def test_dynamic_formula_matches_operator_example(self):
        self.profile.pricing_strategy = "dynamic"
        self.profile.save(update_fields=["pricing_strategy", "updated_at"])
        result = self.variant.price_breakdown()
        self.assertEqual(result["pricing_strategy"], "dynamic")
        self.assertEqual(result["material_cost"], 520_000)
        self.assertEqual(result["machine_cost"], 450_000)
        self.assertEqual(result["supervision_cost"], 150_000)
        self.assertEqual(result["assembly_cost"], 0)
        self.assertEqual(result["unit_price"], 1_120_000)
        self.assertEqual(result["actual_material_grams"], "150")
        self.assertEqual(result["chargeable_material_grams"], "200")
        self.assertEqual(result["actual_print_minutes"], 180)
        self.assertEqual(result["billable_print_minutes"], 180)

    def test_fixed_strategy_uses_operator_fixed_price(self):
        self.profile.pricing_strategy = "fixed"
        self.profile.price_min = 900_000
        self.profile.price_max = 900_000
        self.profile.save(update_fields=["pricing_strategy", "price_min", "price_max", "updated_at"])
        self.product.fixed_price = 900_000
        self.product.save(update_fields=["fixed_price", "updated_at"])
        result = self.variant.price_breakdown()
        self.assertEqual(result["pricing_strategy"], "fixed")
        self.assertEqual(result["unit_price"], 900_000)

    def test_legacy_strategy_preserves_mature_engine(self):
        self.profile.pricing_strategy = "legacy"
        self.profile.save(update_fields=["pricing_strategy", "updated_at"])
        result = self.variant.price_breakdown()
        self.assertNotEqual(result.get("pricing_strategy"), "dynamic")
        self.assertIn("unit_price", result)

    def test_persian_public_labels(self):
        self.assertEqual(self.profile.product_type_label, "محصول آماده سفارش")
        self.assertEqual(self.profile.availability_status_label, "تولید پس از سفارش")

    def test_public_product_page_hides_internal_source_username_and_raw_codes(self):
        user = get_user_model().objects.create_user(username="operator-test", password="pass1234")
        self.client.force_login(user)
        response = self.client.get(reverse("store:product_detail", kwargs={"slug": self.product.slug}))
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        self.assertNotIn("Username", body)
        self.assertNotIn("ready_product", body)
        self.assertNotIn("made_to_order", body)
        self.assertIn("محصول آماده سفارش", body)
        self.assertIn("تولید پس از سفارش", body)
        self.assertIn("خلاصه فنی و کاربردی", body)
        self.assertIn("data-supervision-cost", body)
        self.assertIn("data-chargeable-weight", body)
        self.assertIn("وزن قابل محاسبه", body)

    def test_phase493f_admin_extensions_are_registered(self):
        profile_admin = admin.site._registry[ProductCatalogProfile]
        material_admin = admin.site._registry[Material]
        self.assertIn("pricing_strategy", profile_admin.list_display)
        self.assertIn("pricing_strategy", profile_admin.list_filter)
        self.assertIn("print_hourly_rate_toman", material_admin.list_display)
        self.assertIn("supervision_hourly_rate_toman", material_admin.list_editable)

    def test_phase493f_migrations_are_additive_only(self):
        forbidden = {"DeleteModel", "RemoveField", "RunSQL", "RunPython", "SeparateDatabaseAndState"}
        modules = [
            import_module("store.migrations.0033_phase49_3f_pricing_intelligence"),
            import_module("website.migrations.0023_phase49_3f_material_runtime_rates"),
        ]
        operation_names = {
            type(operation).__name__
            for module in modules
            for operation in module.Migration.operations
        }
        self.assertTrue(operation_names)
        self.assertTrue(operation_names.isdisjoint(forbidden), operation_names & forbidden)
        self.assertEqual(operation_names, {"AddField"})
