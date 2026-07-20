from datetime import timedelta
from decimal import Decimal
import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from website.models import Material, SEOSettings
from .models import (
    Category, Coupon, CouponUsage, CustomerNotification, InventoryMovement,
    PricingSetting, PrintQuality, Product, ProductFAQ, ProductVariant,
    Shipment, ShippingMethod, StoreOrder, StoreOrderItem, StorePayment,
)
from .services import finalize_paid_order, release_expired_reservations, reserve_order_inventory, validate_coupon
from .templatetags.store_seo import product_faq_schema_json


class StoreOperationsPhase6Tests(TestCase):
    def setUp(self):
        PricingSetting.objects.create(default_hourly_rate=100_000, default_labor_percent=Decimal("30"))
        self.material = Material.objects.create(
            name="PHASE6 PETG", price_per_kg=1_000_000, strength=3, heat_resistance=3,
            flexibility=1, chemical_resistance=3, printability=4, main_usage="test", sample_parts="test",
        )
        self.quality = PrintQuality.objects.create(code="phase6-standard", name="استاندارد فاز ۶")
        self.category = Category.objects.create(name="فاز شش", slug="phase-6", section="industrial")
        self.product = Product.objects.create(
            category=self.category, title="محصول عملیات", slug="operations-product", sku="OPS-1",
            short_description="توضیح محصول عملیات", description="توضیحات کامل محصول عملیات",
            main_image="store/products/test.webp", brand_name="3DprintHub",
        )
        self.variant = ProductVariant.objects.create(
            product=self.product, material=self.material, quality=self.quality, code="OPS-V1",
            material_weight_grams=Decimal("10"), final_weight_grams=Decimal("10"),
            shipping_weight_grams=Decimal("12"), print_time_minutes=60,
            track_inventory=True, stock_quantity=5, low_stock_threshold=1,
        )
        self.shipping = ShippingMethod.objects.create(code="phase6-post", title="پست فاز ۶", flat_fee=20_000)
        self.user = get_user_model().objects.create_user(username="phase6buyer", password="StrongPass123!", first_name="فراز", last_name="حراجی")
        SEOSettings.objects.create(site_url="https://3dprinthub.ir", organization_name="3DprintHub", shipping_rate=20_000)

    def make_order(self, quantity=2, *, status="awaiting_payment", payment_status="pending"):
        unit_price = self.variant.cached_unit_price
        order = StoreOrder.objects.create(
            user=self.user, status=status, payment_status=payment_status,
            shipping_method=self.shipping, shipping_title=self.shipping.title,
            full_name="فراز حراجی", phone="09120000000", email="buyer@example.com",
            province="اصفهان", county="اصفهان", city="اصفهان", address="خیابان تست",
            postal_code="1234567890", subtotal=unit_price * quantity, shipping_fee=20_000,
            total_amount=unit_price * quantity + 20_000, total_weight_grams=Decimal("12") * quantity,
        )
        StoreOrderItem.objects.create(
            order=order, product=self.product, variant=self.variant, product_title=self.product.title,
            product_sku=self.product.sku, variant_code=self.variant.code, material_name=self.material.name,
            quality_name=self.quality.name, unit_price=unit_price, quantity=quantity,
            line_total=unit_price * quantity, unit_weight_grams=Decimal("12"),
        )
        return order

    def test_inventory_is_reserved_and_consumed_after_payment(self):
        order = self.make_order(2)
        reserve_order_inventory(order)
        self.variant.refresh_from_db(); order.refresh_from_db()
        self.assertEqual(self.variant.reserved_quantity, 2)
        self.assertTrue(order.inventory_reserved)
        payment = StorePayment.objects.create(order=order, amount=order.total_amount)
        payment.mark_paid("PHASE6-REF")
        self.variant.refresh_from_db(); order.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 3)
        self.assertEqual(self.variant.reserved_quantity, 0)
        self.assertFalse(order.inventory_reserved)
        self.assertTrue(hasattr(order, "invoice"))
        self.assertTrue(InventoryMovement.objects.filter(order=order, movement_type="sale").exists())
        self.assertTrue(CustomerNotification.objects.filter(user=self.user, notification_type="payment").exists())

    def test_reservation_rejects_quantity_above_stock(self):
        order = self.make_order(6)
        with self.assertRaises(ValidationError):
            reserve_order_inventory(order)

    def test_expired_reservation_is_released(self):
        order = self.make_order(2)
        reserve_order_inventory(order)
        StoreOrder.objects.filter(pk=order.pk).update(reservation_expires_at=timezone.now() - timedelta(minutes=1))
        self.assertEqual(release_expired_reservations(), 1)
        self.variant.refresh_from_db(); order.refresh_from_db()
        self.assertEqual(self.variant.reserved_quantity, 0)
        self.assertFalse(order.inventory_reserved)

    def test_percent_coupon_respects_maximum_discount(self):
        coupon = Coupon.objects.create(code="SAVE50", title="نصف قیمت", discount_type="percent", value=50, maximum_discount=30_000)
        lines = [(self.variant, 2, 100_000, 200_000, Decimal("12"))]
        result, amount = validate_coupon("save50", user=self.user, cart_lines=lines, subtotal=200_000)
        self.assertEqual(result, coupon)
        self.assertEqual(amount, 30_000)

    def test_coupon_usage_is_recorded_after_payment(self):
        coupon = Coupon.objects.create(code="FIXED", title="تخفیف ثابت", discount_type="fixed", value=10_000)
        order = self.make_order(1)
        order.coupon = coupon; order.coupon_code = coupon.code; order.discount_amount = 10_000; order.save()
        reserve_order_inventory(order)
        order.mark_paid()
        finalize_paid_order(order)
        self.assertTrue(CouponUsage.objects.filter(order=order, coupon=coupon).exists())
        coupon.refresh_from_db(); self.assertEqual(coupon.used_count, 1)

    def test_notifications_are_private_to_current_user(self):
        other = get_user_model().objects.create_user(username="other-phase6", password="StrongPass123!")
        CustomerNotification.objects.create(user=self.user, title="پیام من", message="متن")
        CustomerNotification.objects.create(user=other, title="پیام دیگری", message="متن")
        self.client.login(username=self.user.username, password="StrongPass123!")
        response = self.client.get(reverse("store:notifications"))
        self.assertContains(response, "پیام من")
        self.assertNotContains(response, "پیام دیگری")

    def test_merchant_feed_contains_required_product_data(self):
        response = self.client.get(reverse("store:merchant_feed"))
        self.assertEqual(response.status_code, 200)
        text = response.content.decode("utf-8")
        self.assertIn('xmlns:g="http://base.google.com/ns/1.0"', text)
        self.assertIn("<g:id>OPS-V1</g:id>", text)
        self.assertIn("<g:price>", text)
        self.assertIn(" IRR</g:price>", text)
        self.assertIn("<g:availability>in_stock</g:availability>", text)

    def test_delivered_order_can_open_return_request(self):
        order = self.make_order(1, status="delivered", payment_status="paid")
        Shipment.objects.create(order=order, status="delivered", delivered_at=timezone.now())
        self.client.login(username=self.user.username, password="StrongPass123!")
        response = self.client.get(reverse("store:return_request", args=[order.order_number]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "درخواست مرجوعی")

    def test_product_faq_schema_matches_visible_faq(self):
        ProductFAQ.objects.create(product=self.product, question="آیا مقاوم است؟", answer="بله، برای کاربرد مشخص مناسب است.")
        request = RequestFactory().get(self.product.get_absolute_url(), HTTP_HOST="testserver")
        data = json.loads(str(product_faq_schema_json(self.product, request)))
        self.assertEqual(data["@type"], "FAQPage")
        self.assertEqual(data["mainEntity"][0]["name"], "آیا مقاوم است؟")


    def test_operations_dashboard_loads_for_staff(self):
        staff = get_user_model().objects.create_superuser(username="phase6admin", password="StrongPass123!", email="admin@example.com")
        self.client.login(username=staff.username, password="StrongPass123!")
        response = self.client.get(reverse("admin:store_storeoperationsdashboard_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "داشبورد عملیات فروشگاه")

    def test_operations_dashboard_requires_staff(self):
        self.client.login(username=self.user.username, password="StrongPass123!")
        response = self.client.get(reverse("admin:store_storeoperationsdashboard_changelist"))
        self.assertEqual(response.status_code, 404)
