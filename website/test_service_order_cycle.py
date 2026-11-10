"""Service order cashflow, shipping and Desktop Offer pricing acceptance."""
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from store.models import ShippingMethod
from store.phase39_models import MaterialColorOption

from .models import Material, Order, Payment, PaymentLedgerEntry, Quote, ServiceOrderDelivery
from .quote_catalog_offer import available_filament_offers

GIF_1X1 = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class ServiceCycleTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_superuser(
            "service-finance-admin", "finance@example.invalid", "test-password"
        )
        self.customer = User.objects.create_user(
            "service-customer", "customer@example.invalid", "test-password"
        )
        self.material = Material.objects.create(
            name="PLA color professional", is_active=True, sale_price_per_gram=1000,
            price_per_kg=1000000, main_usage="test", sample_parts="test",
        )
        self.offer = MaterialColorOption.objects.create(
            material=self.material, name="matte black", code="matte-black",
            brand_name="E-Sun", is_active=True,
            sale_price_per_roll=4000000, roll_weight_grams=1000,
            stock_roll_count_snapshot=2, print_hourly_rate=120000,
            supervision_hourly_rate=50000, preheat_hours=Decimal("2.00"),
            preheat_hourly_rate=30000,
        )
        self.post, _ = ShippingMethod.objects.update_or_create(
            code="post", defaults={"title": "Post", "flat_fee": 0, "is_active": True}
        )
        self.pickup, _ = ShippingMethod.objects.update_or_create(
            code="pickup", defaults={"title": "Pickup", "flat_fee": 0, "is_active": True}
        )
        self.courier, _ = ShippingMethod.objects.update_or_create(
            code="courier", defaults={"title": "Courier", "flat_fee": 0, "is_active": True}
        )
        self.order = Order.objects.create(
            customer=self.customer, first_name="Test", last_name="Buyer",
            phone="09120000000", quantity=1, material=self.material,
            description="service-cycle test", status="reviewing",
        )
        self.quote = Quote.objects.create(
            order=self.order, material=self.material, filament_offer=self.offer,
            weight_grams=30, support_weight_grams=10,
            support_cost_multiplier=Decimal("1.500"),
            print_time_minutes=90, machine_hourly_rate=999999,
            assembly_fee_per_unit=20000, status="draft",
        )

    def accept_quote(self):
        self.quote.status = "sent"
        self.quote.save(update_fields=["status"])
        self.quote.status = "accepted"
        self.quote.save(update_fields=["status"])
        self.quote.refresh_from_db()

    def pay_full(self, method="cash", ref=""):
        self.accept_quote()
        p = Payment.objects.create(
            quote=self.quote, amount=self.quote.total_price, method=method,
            payment_kind="full", ref_id=ref, status="awaiting_review",
        )
        p.mark_paid(ref_id=ref, metadata={"reviewed_by_user_id": self.staff.pk})
        return p

    def test_offer_prices_match_desktop_formula_each_component(self):
        # Exact Desktop professional offer formula for one production row.
        from catalog_center.app.phase49_3i39_professional_commerce import formula_price_breakdown
        desktop = formula_price_breakdown({
            "brand_name": "E-Sun", "material_name": "PLA color professional",
            "color_name": "matte black", "sale_price_per_roll": 4000000,
            "roll_weight_grams": 1000, "print_hourly_rate": 120000,
            "supervision_hourly_rate": 50000, "preheat_hours": 2,
            "preheat_hourly_rate": 30000,
        }, {
            "weight_grams": 30, "support_weight_grams": 10,
            "print_time_minutes": 90,
        }, support_multiplier=Decimal("1.5"), assembly_fee=20000)
        self.assertEqual(self.quote.material_cost, desktop["material_cost"])
        self.assertEqual(self.quote.machine_cost, desktop["print_cost"])
        self.assertEqual(self.quote.supervision_cost, desktop["supervision_cost"])
        self.assertEqual(self.quote.preheat_cost, desktop["preheat_cost"])
        self.assertEqual(self.quote.assembly_cost, desktop["assembly_fee"])
        self.assertEqual(self.quote.subtotal, desktop["total"])
        self.assertEqual(self.quote.total_price, 515000)

    def test_quantity_preserves_exact_offer_unit_charges(self):
        self.order.quantity = 3
        self.order.save()
        self.assertEqual(self.quote.total_price, 515000 * 3)
        self.quote.print_time_scope = "batch"
        self.assertEqual(self.quote.material_cost, 540000)
        self.assertEqual(self.quote.machine_cost, 180000)
        self.assertEqual(self.quote.supervision_cost, 75000)
        self.assertEqual(self.quote.preheat_cost, 60000)
        self.assertEqual(self.quote.assembly_cost, 60000)

    def test_finalized_offer_pricing_stays_immutable_after_catalog_changes(self):
        self.accept_quote()
        self.assertEqual(self.quote.pricing_snapshot_supervision_cost, 75000)
        self.assertEqual(self.quote.pricing_snapshot_preheat_cost, 60000)
        self.assertEqual(self.quote.pricing_snapshot_assembly_cost, 20000)
        self.offer.sale_price_per_roll = 9000000
        self.offer.print_hourly_rate = 300000
        self.offer.supervision_hourly_rate = 0
        self.offer.preheat_hourly_rate = 500000
        self.offer.save()
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.material_cost, 180000)
        self.assertEqual(self.quote.machine_cost, 180000)
        self.assertEqual(self.quote.supervision_cost, 75000)
        self.assertEqual(self.quote.preheat_cost, 60000)
        self.assertEqual(self.quote.total_price, 515000)
        self.quote.filament_offer = None
        with self.assertRaises(ValidationError):
            self.quote.save()

    def test_only_price_ready_active_catalog_offers_are_selectable(self):
        self.assertTrue(available_filament_offers().filter(pk=self.offer.pk).exists())
        self.offer.is_active = False
        self.offer.save(update_fields=["is_active"])
        self.assertFalse(available_filament_offers().filter(pk=self.offer.pk).exists())
        self.quote.status = "sent"
        with self.assertRaises(ValidationError):
            self.quote.save()

    def test_new_admin_quote_shows_real_catalog_offer_choices(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("admin:website_order_change", args=[self.order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "E-Sun")
        self.assertContains(response, "matte black")
        self.assertContains(response, "فیلامنت قابل فروش")
        self.assertContains(response, "نظارت بر چاپ")

    def test_admin_cash_receipt_with_no_bank_reference_is_ledger_backed(self):
        self.accept_quote()
        self.client.force_login(self.staff)
        response = self.client.post(reverse("admin:website_order_record_receipt", args=[self.order.pk]), {
            "amount": 100000, "payment_kind": "partial", "method": "cash",
            "ref_id": "", "submission_key": "a0e945be-2244-46e8-8dc3-1c593ac53e3e",
            "confirmed": "on", "note": "Cash counted by finance",
        })
        self.assertEqual(response.status_code, 302)
        payment = Payment.objects.get(quote=self.quote)
        self.assertEqual(payment.method, "cash")
        self.assertEqual(payment.status, "paid")
        self.assertEqual(self.quote.remaining_amount, 415000)
        self.assertEqual(PaymentLedgerEntry.objects.filter(payment=payment).count(), 1)

    def test_admin_pos_requires_reference_and_pending_does_not_reduce_debt(self):
        self.accept_quote()
        self.client.force_login(self.staff)
        url = reverse("admin:website_order_record_receipt", args=[self.order.pk])
        missing = self.client.post(url, {
            "amount": 40000, "payment_kind": "partial", "method": "pos",
            "ref_id": "", "note": "POS", "confirmed": "on",
        })
        self.assertEqual(missing.status_code, 200)
        self.assertEqual(Payment.objects.count(), 0)
        pending = self.client.post(url, {
            "amount": 40000, "payment_kind": "partial", "method": "pos",
            "ref_id": "pos-2026-0001", "note": "POS",
        })
        self.assertEqual(pending.status_code, 302)
        self.assertEqual(self.quote.paid_amount, 0)
        self.assertEqual(self.quote.pending_amount, 40000)

    def test_customer_custom_partial_receipt_and_pending_prevents_overpayment(self):
        self.accept_quote()
        self.client.force_login(self.customer)
        url = reverse("website:quote_payment", args=[self.order.public_token])
        response = self.client.post(url, {
            "payment_kind": "partial", "partial_amount": 70000,
            "receipt_image": SimpleUploadedFile("receipt.gif", GIF_1X1, content_type="image/gif"),
            "note": "Partial bank transfer",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(self.quote.pending_amount, 70000)
        self.assertEqual(self.quote.paid_amount, 0)
        repeat = self.client.post(url, {
            "payment_kind": "partial", "partial_amount": 500000,
            "receipt_image": SimpleUploadedFile("receipt2.gif", GIF_1X1, content_type="image/gif"),
        })
        self.assertEqual(repeat.status_code, 302)
        self.assertEqual(Payment.objects.count(), 1)

    def test_delivery_blocked_without_confirmed_full_payment(self):
        self.accept_quote()
        self.client.force_login(self.staff)
        response = self.client.post(reverse("admin:website_order_record_delivery", args=[self.order.pk]), {
            "shipping_method": self.pickup.pk, "status": "delivered",
            "recipient_name": "Customer",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ServiceOrderDelivery.objects.filter(order=self.order).exists())

    def test_paid_pickup_can_be_recorded_and_is_immutable(self):
        self.pay_full()
        self.client.force_login(self.staff)
        url = reverse("admin:website_order_record_delivery", args=[self.order.pk])
        response = self.client.post(url, {
            "shipping_method": self.pickup.pk, "status": "delivered",
            "recipient_name": "Buyer", "note": "Handover at office",
        })
        self.assertEqual(response.status_code, 302)
        obj = ServiceOrderDelivery.objects.get(order=self.order)
        self.assertEqual(obj.status, "delivered")
        self.assertEqual(obj.shipping_method, self.pickup)
        self.assertEqual(obj.recorded_by, self.staff)
        self.assertIsNotNone(obj.delivered_at)
        second = self.client.post(url, {
            "shipping_method": self.pickup.pk, "status": "delivered",
            "recipient_name": "Other",
        })
        self.assertEqual(second.status_code, 200)
        obj.refresh_from_db()
        self.assertEqual(obj.recipient_name, "Buyer")

    def test_post_requires_tracking_code_and_courier_is_supported(self):
        self.pay_full()
        self.client.force_login(self.staff)
        url = reverse("admin:website_order_record_delivery", args=[self.order.pk])
        bad = self.client.post(url, {"shipping_method": self.post.pk, "status": "dispatched"})
        self.assertEqual(bad.status_code, 200)
        self.assertEqual(ServiceOrderDelivery.objects.count(), 0)
        shipped = self.client.post(url, {
            "shipping_method": self.post.pk, "status": "dispatched",
            "tracking_code": "POST-001", "recipient_address": "QA street address",
        })
        self.assertEqual(shipped.status_code, 302, shipped.context["form"].errors if shipped.context else "")
        self.assertIsNotNone(ServiceOrderDelivery.objects.get(order=self.order).shipped_at)
        delivered = self.client.post(url, {
            "shipping_method": self.post.pk, "status": "delivered",
            "tracking_code": "POST-001", "recipient_name": "Receiver",
            "recipient_address": "QA street address",
        })
        self.assertEqual(delivered.status_code, 302)
        self.assertEqual(ServiceOrderDelivery.objects.get(order=self.order).status, "delivered")

    def test_payment_gateway_cannot_be_marked_paid_from_manual_receipt_form(self):
        self.accept_quote()
        self.client.force_login(self.staff)
        response = self.client.post(reverse("admin:website_order_record_receipt", args=[self.order.pk]), {
            "amount": 100000, "payment_kind": "partial", "method": "gateway",
            "ref_id": "fake-gateway", "confirmed": "on",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Payment.objects.exists())

    def test_cannot_finalize_unavailable_or_understocked_catalog_offer(self):
        self.offer.stock_roll_count_snapshot = Decimal("0")
        self.offer.save(update_fields=["stock_roll_count_snapshot"])
        self.quote.status = "sent"
        with self.assertRaises(ValidationError):
            self.quote.save()
        self.offer.stock_roll_count_snapshot = Decimal("2")
        self.offer.save(update_fields=["stock_roll_count_snapshot"])
        self.order.quantity = 100
        self.order.save()
        with self.assertRaises(ValidationError):
            self.quote.save()

    def test_no_negative_support_weight_or_multiplier(self):
        self.quote.support_weight_grams = Decimal("-1")
        with self.assertRaises(ValidationError):
            self.quote.save()
        self.quote.support_weight_grams = Decimal("10")
        self.quote.support_cost_multiplier = Decimal("-0.5")
        with self.assertRaises(ValidationError):
            self.quote.save()

    def test_duplicate_cash_form_post_cannot_book_same_cash_twice(self):
        self.accept_quote()
        self.client.force_login(self.staff)
        payload = {
            "amount": 50000, "payment_kind": "partial", "method": "cash",
            "submission_key": "b79f874b-7c6b-4e83-9b0d-7ed4aca23c42",
            "ref_id": "", "confirmed": "on",
        }
        url = reverse("admin:website_order_record_receipt", args=[self.order.pk])
        first = self.client.post(url, payload)
        self.assertEqual(first.status_code, 302)
        second = self.client.post(url, payload)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(self.quote.paid_amount, 50000)
        self.assertEqual(PaymentLedgerEntry.objects.count(), 1)

    def test_fractional_rates_have_exact_desktop_total_rounding_parity(self):
        from catalog_center.app.phase49_3i39_professional_commerce import formula_price_breakdown
        self.offer.sale_price_per_roll = 1500
        self.offer.print_hourly_rate = 30
        self.offer.supervision_hourly_rate = 30
        self.offer.preheat_hours = Decimal("0")
        self.offer.preheat_hourly_rate = 0
        self.offer.save()
        self.quote.weight_grams = Decimal("1")
        self.quote.support_weight_grams = Decimal("0")
        self.quote.print_time_minutes = 1
        self.quote.assembly_fee_per_unit = 0
        self.quote.save()
        desktop = formula_price_breakdown(
            {
                "sale_price_per_roll": 1500, "roll_weight_grams": 1000,
                "print_hourly_rate": 30, "supervision_hourly_rate": 30,
                "preheat_hours": 0, "preheat_hourly_rate": 0,
            },
            {"weight_grams": 1, "support_weight_grams": 0, "print_time_minutes": 1},
        )
        self.assertEqual(self.quote.material_cost, desktop["material_cost"])
        self.assertEqual(self.quote.machine_cost, desktop["print_cost"])
        self.assertEqual(self.quote.supervision_cost, desktop["supervision_cost"])
        self.assertEqual(self.quote.offer_rounding_adjustment, -1)
        self.assertEqual(self.quote.total_price, desktop["total"])
        self.assertEqual(self.quote.total_price, 3)
        self.quote.status = "sent"
        self.quote.save()
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.pricing_snapshot_offer_rounding_adjustment, -1)
        self.assertEqual(self.quote.total_price, desktop["total"])

    def test_office_courier_shipment_uses_live_store_method_and_address(self):
        self.pay_full()
        self.client.force_login(self.staff)
        url = reverse("admin:website_order_record_delivery", args=[self.order.pk])
        missing = self.client.post(url, {
            "shipping_method": self.courier.pk, "status": "dispatched",
            "note": "Courier out for delivery",
        })
        self.assertEqual(missing.status_code, 200)
        self.assertFalse(ServiceOrderDelivery.objects.filter(order=self.order).exists())
        sent = self.client.post(url, {
            "shipping_method": self.courier.pk, "status": "dispatched",
            "recipient_address": "QA destination address", "note": "Courier dispatched",
        })
        self.assertEqual(sent.status_code, 302)
        delivery = ServiceOrderDelivery.objects.get(order=self.order)
        self.assertEqual(delivery.shipping_method_id, self.courier.pk)
        self.assertEqual(delivery.status, "dispatched")
        self.assertEqual(delivery.recipient_address, "QA destination address")
