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

# BEGIN STORE COMMERCE PHASE 2
from io import BytesIO

from PIL import Image

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import ProductReview, ShippingMethod, StoreOrder, StorePayment


class StoreCheckoutTests(TestCase):
    def setUp(self):
        PricingSetting.objects.create(
            default_hourly_rate=100_000,
            default_labor_percent=Decimal("30"),
            minimum_order_amount=0,
        )
        self.material = Material.objects.create(
            name="PET-CF CHECKOUT",
            price_per_kg=4_000_000,
            strength=5,
            heat_resistance=4,
            flexibility=0,
            chemical_resistance=4,
            printability=4,
            main_usage="test",
            sample_parts="test",
        )
        self.quality = PrintQuality.objects.create(code="checkout-quality", name="کیفیت سفارش")
        self.category = Category.objects.create(name="فروشگاه تست", slug="checkout-category", section="industrial")
        self.product = Product.objects.create(
            category=self.category,
            title="محصول سفارش تست",
            slug="checkout-product",
            sku="CHECKOUT-001",
            short_description="test",
            description="test",
            main_image="store/products/test.webp",
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            material=self.material,
            quality=self.quality,
            code="TEST-CHECKOUT-001",
            material_weight_grams=Decimal("10"),
            final_weight_grams=Decimal("10"),
            shipping_weight_grams=Decimal("15"),
            print_time_minutes=60,
        )
        self.shipping = ShippingMethod.objects.create(code="post", title="پست", flat_fee=30_000)
        self.user = get_user_model().objects.create_user(
            username="buyer",
            password="test-pass-123",
            email="buyer@example.com",
        )
        self.client.login(username="buyer", password="test-pass-123")

    def _checkout(self, quantity=2):
        response = self.client.post(
            reverse("store:cart_add", args=[self.product.slug]),
            {"variant_id": self.variant.pk, "quantity": quantity},
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse("store:checkout"), {
            "shipping_method": self.shipping.pk,
            "full_name": "خریدار تست",
            "phone": "09120000000",
            "email": "buyer@example.com",
            "province": "اصفهان",
            "city": "اصفهان",
            "address": "خیابان تست",
            "postal_code": "1234567890",
            "customer_note": "",
            "payment_method": "bank_transfer",
            "save_address": "on",
        })
        self.assertEqual(response.status_code, 302)
        return StoreOrder.objects.get(user=self.user)

    def test_cart_add_and_checkout_create_vat_inclusive_price_snapshot(self):
        order = self._checkout(quantity=2)
        item = order.items.get()
        self.assertEqual(item.unit_price, 182_000)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.line_total, 364_000)
        self.assertEqual(order.subtotal, 364_000)
        self.assertEqual(order.shipping_fee, 30_000)
        self.assertEqual(order.tax_amount, 39_400)
        self.assertEqual(order.total_amount, 433_400)
        self.assertTrue(StorePayment.objects.filter(order=order, amount=433_400).exists())
        self.variant.fixed_fee = 500_000
        self.variant.save()
        item.refresh_from_db()
        self.assertEqual(item.unit_price, 182_000)

    def test_shipping_method_free_threshold(self):
        self.shipping.free_over = 300_000
        self.shipping.save()
        self.assertEqual(self.shipping.calculate_fee(299_999), 30_000)
        self.assertEqual(self.shipping.calculate_fee(300_000), 0)

    def test_out_of_stock_variant_is_not_added(self):
        self.variant.stock_status = "out_of_stock"
        self.variant.save()
        response = self.client.post(
            reverse("store:cart_add", args=[self.product.slug]),
            {"variant_id": self.variant.pk, "quantity": 1},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get("store_cart_v1", {}))

    def test_manual_receipt_moves_payment_to_review(self):
        order = self._checkout(quantity=1)
        image_buffer = BytesIO()
        Image.new("RGB", (2, 2), "white").save(image_buffer, format="PNG")
        receipt = SimpleUploadedFile("receipt.png", image_buffer.getvalue(), content_type="image/png")
        response = self.client.post(
            reverse("store:manual_payment", args=[order.order_number]),
            {"card_holder": "خریدار تست", "note": "پرداخت شد", "receipt_image": receipt},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        payment = order.payments.get()
        self.assertEqual(order.payment_status, "awaiting_review")
        self.assertEqual(order.status, "payment_review")
        self.assertEqual(payment.status, "awaiting_review")
        self.assertTrue(bool(payment.receipt_image))

    def test_review_requires_verified_paid_order(self):
        response = self.client.get(reverse("store:product_review", args=[self.product.slug]))
        self.assertEqual(response.status_code, 302)

    def test_paid_buyer_can_submit_verified_review(self):
        order = self._checkout(quantity=1)
        order.payments.get().mark_paid("TEST-REF-1")
        response = self.client.get(reverse("store:product_review", args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse("store:product_review", args=[self.product.slug]),
            {"rating": 5, "title": "عالی", "body": "کیفیت ساخت بسیار خوب بود."},
        )
        self.assertEqual(response.status_code, 302)
        review = ProductReview.objects.get(product=self.product, user=self.user)
        self.assertTrue(review.is_verified_purchase)
        self.assertFalse(review.is_approved)
# END STORE COMMERCE PHASE 2
