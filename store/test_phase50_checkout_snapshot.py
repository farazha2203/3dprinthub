from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve, reverse

from website.models import Material

from .models import (
    Category,
    PricingSetting,
    PrintQuality,
    Product,
    ProductVariant,
    ShippingMethod,
    StoreAddress,
    StoreOrder,
    StoreOrderItem,
)
from .phase50_checkout_snapshot import QUOTE_SCHEMA


class Phase50CheckoutSnapshotTests(TestCase):
    def setUp(self):
        PricingSetting.objects.create(
            default_hourly_rate=100_000,
            default_labor_percent=Decimal("30"),
            minimum_order_amount=0,
            packaging_fee=5_000,
            tax_percent=Decimal("10.00"),
            vat_enabled=True,
        )
        self.material = Material.objects.create(
            name="PLA SNAPSHOT TEST",
            price_per_kg=1_000_000,
            strength=3,
            heat_resistance=2,
            flexibility=1,
            chemical_resistance=2,
            printability=5,
            main_usage="test",
            sample_parts="test",
        )
        self.quality = PrintQuality.objects.create(
            code="snapshot-quality",
            name="کیفیت تست اسنپ‌شات",
        )
        self.category = Category.objects.create(
            name="اسنپ‌شات",
            slug="snapshot-category",
            section="industrial",
        )
        self.product = Product.objects.create(
            category=self.category,
            title="محصول اسنپ‌شات",
            slug="snapshot-product",
            sku="SNAPSHOT-001",
            short_description="test",
            description="test",
            main_image="store/products/snapshot.webp",
            sales_profile_selection_mode="size_build",
            sales_profile_selector_label="سایز و مدل ساخت",
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            material=self.material,
            quality=self.quality,
            code="SNAPSHOT-V1",
            material_weight_grams=Decimal("115"),
            final_weight_grams=Decimal("120"),
            shipping_weight_grams=Decimal("0"),
            packaging_weight_grams=Decimal("30"),
            part_length_cm=Decimal("18"),
            part_width_cm=Decimal("11"),
            part_height_cm=Decimal("7"),
            package_length_cm=Decimal("20"),
            package_width_cm=Decimal("12"),
            package_height_cm=Decimal("8"),
            print_time_minutes=90,
            size_label="20 سانتی‌متر",
            build_profile="reinforced",
            sales_profile_name="20 سانتی‌متر تقویت‌شده",
            sales_profile_key="20-reinforced",
            sales_profile_is_default=True,
        )
        self.shipping = ShippingMethod.objects.create(
            code="phase50-test-post",
            title="پست تست",
            flat_fee=30_000,
        )
        self.user = get_user_model().objects.create_user(
            username="phase50-checkout-user",
            password="phase50-test-pass",
            email="checkout@example.com",
        )
        self.address = StoreAddress.objects.create(
            user=self.user,
            title="آدرس تست",
            full_name="خریدار تست",
            phone="09120000000",
            province="اصفهان",
            county="اصفهان",
            city="اصفهان",
            address="خیابان تست",
            postal_code="1234567890",
            is_default=True,
        )
        self.client.login(
            username="phase50-checkout-user",
            password="phase50-test-pass",
        )

    def _checkout(self, quantity=2):
        response = self.client.post(
            reverse("store:cart_add", args=[self.product.slug]),
            {"variant_id": self.variant.pk, "quantity": quantity},
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse("store:checkout"),
            {
                "saved_address": self.address.pk,
                "shipping_method": self.shipping.pk,
                "full_name": self.address.full_name,
                "phone": self.address.phone,
                "email": self.user.email,
                "payment_method": "bank_transfer",
                "coupon_code": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        return StoreOrder.objects.get(user=self.user)

    def test_runtime_fields_and_checkout_wrapper_are_installed(self):
        for name in (
            "sales_profile_name",
            "sales_profile_key",
            "sales_profile_label",
            "sales_profile_selection_mode",
            "sales_profile_selection_value",
            "final_weight_grams",
            "shipping_weight_grams",
            "print_time_minutes",
        ):
            self.assertIsNotNone(StoreOrderItem._meta.get_field(name))

        self.assertIsNotNone(StoreOrder._meta.get_field("insured_value"))
        self.assertIsNotNone(StoreOrder._meta.get_field("shipping_quote_snapshot"))
        self.assertTrue(
            getattr(resolve(reverse("store:checkout")).func, "_phase50_checkout_snapshot", False)
        )

    def test_checkout_freezes_profile_package_weight_and_shipping_quote(self):
        order = self._checkout(quantity=2)
        item = order.items.get()

        self.assertEqual(item.sales_profile_name, "20 سانتی‌متر تقویت‌شده")
        self.assertEqual(item.sales_profile_key, "20-reinforced")
        self.assertEqual(item.sales_profile_label, "20 سانتی‌متر تقویت‌شده")
        self.assertEqual(item.sales_profile_selection_mode, "size_build")
        self.assertEqual(item.sales_profile_selection_value, "20 سانتی‌متر • تقویت‌شده")
        self.assertEqual(item.size_label, "20 سانتی‌متر")
        self.assertEqual(item.build_profile, "reinforced")
        self.assertEqual(item.final_weight_grams, Decimal("120.00"))
        self.assertEqual(item.packaging_weight_grams, Decimal("30.00"))
        self.assertEqual(item.shipping_weight_grams, Decimal("150.00"))
        self.assertEqual(item.unit_weight_grams, Decimal("150.00"))
        self.assertEqual(item.print_time_minutes, 90)
        self.assertEqual(item.part_length_cm, Decimal("18.00"))
        self.assertEqual(item.part_width_cm, Decimal("11.00"))
        self.assertEqual(item.part_height_cm, Decimal("7.00"))
        self.assertEqual(item.package_length_cm, Decimal("20.00"))
        self.assertEqual(item.package_width_cm, Decimal("12.00"))
        self.assertEqual(item.package_height_cm, Decimal("8.00"))
        self.assertEqual(order.total_weight_grams, Decimal("300.00"))

        quote = order.shipping_quote_snapshot
        self.assertEqual(quote["schema"], QUOTE_SCHEMA)
        self.assertEqual(quote["source"], "shipping_method_fallback")
        self.assertFalse(quote["external_carrier_quote"])
        self.assertEqual(quote["method"]["code"], self.shipping.code)
        self.assertEqual(quote["total_weight_grams"], "300.00")
        self.assertEqual(quote["shipping_fee"], 30_000)
        self.assertEqual(quote["insured_value"], order.subtotal)
        self.assertEqual(order.insured_value, order.subtotal)
        self.assertEqual(len(quote["packages"]), 1)
        self.assertEqual(quote["packages"][0]["quantity"], 2)
        self.assertEqual(quote["packages"][0]["unit_shipping_weight_grams"], "150.00")
        self.assertEqual(
            quote["packages"][0]["part_dimensions_cm"],
            {"length": "18.00", "width": "11.00", "height": "7.00"},
        )
        self.assertFalse(quote["combined_parcel_dimensions_inferred"])
        self.assertTrue(quote["requires_final_packing"])
        self.assertEqual(order.payments.get().amount, order.total_amount)

    def test_order_snapshot_stays_immutable_after_variant_changes(self):
        order = self._checkout(quantity=1)
        item = order.items.get()
        original_quote = dict(order.shipping_quote_snapshot)

        self.variant.sales_profile_name = "پروفایل تغییرکرده"
        self.variant.sales_profile_key = "changed"
        self.variant.size_label = "99 سانتی‌متر"
        self.variant.build_profile = "solid"
        self.variant.final_weight_grams = Decimal("999")
        self.variant.packaging_weight_grams = Decimal("99")
        self.variant.part_length_cm = Decimal("88")
        self.variant.part_width_cm = Decimal("88")
        self.variant.part_height_cm = Decimal("88")
        self.variant.package_length_cm = Decimal("99")
        self.variant.save()

        item.refresh_from_db()
        order.refresh_from_db()

        self.assertEqual(item.sales_profile_name, "20 سانتی‌متر تقویت‌شده")
        self.assertEqual(item.sales_profile_key, "20-reinforced")
        self.assertEqual(item.size_label, "20 سانتی‌متر")
        self.assertEqual(item.build_profile, "reinforced")
        self.assertEqual(item.final_weight_grams, Decimal("120.00"))
        self.assertEqual(item.shipping_weight_grams, Decimal("150.00"))
        self.assertEqual(item.part_length_cm, Decimal("18.00"))
        self.assertEqual(item.part_width_cm, Decimal("11.00"))
        self.assertEqual(item.part_height_cm, Decimal("7.00"))
        self.assertEqual(item.package_length_cm, Decimal("20.00"))
        self.assertEqual(order.shipping_quote_snapshot, original_quote)
