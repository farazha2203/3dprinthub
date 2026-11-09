"""Pricing agreement must be stable and transparent across later catalog edits."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Material, Order, Quote, Payment
from .payment_services import PaymentFlowError


class QuotePricingSnapshotTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_superuser("pricing-auditor", "pricing@example.invalid", "local-test-password")
        self.material = Material.objects.create(
            name="Pricing snapshot test material", price_per_kg=1_000_000,
            sale_price_per_gram=1_000, main_usage="test", sample_parts="test",
        )
        self.order = Order.objects.create(
            first_name="Sample", last_name="Buyer", phone="09120000030",
            material=self.material, quantity=1, description="Pricing snapshot regression",
        )
        self.quote = Quote.objects.create(
            order=self.order, material=self.material,
            status="draft", weight_grams=100,
            print_time_minutes=61, machine_hourly_rate=100_000,
            labor_fee=30_000, shipping_fee=20_000, discount=20_000,
        )

    def finalize(self):
        self.quote.status = "sent"
        self.quote.save(update_fields=["status"])
        self.quote.refresh_from_db()
        return self.quote

    def test_draft_tracks_live_material_but_sent_price_stays_fixed(self):
        self.assertEqual(self.quote.material_cost, 100_000)
        self.assertEqual(self.quote.machine_cost, 200_000)
        self.assertEqual(self.quote.subtotal, 350_000)
        self.assertEqual(self.quote.total_price, 330_000)
        self.finalize()
        self.assertEqual(self.quote.pricing_snapshot_total, 330_000)
        self.assertEqual(self.quote.pricing_snapshot_discount, 20_000)
        self.assertEqual(self.quote.pricing_snapshot_quantity, 1)
        self.assertEqual(self.quote.pricing_snapshot_material_rate, Decimal("1000.0000"))

        self.material.sale_price_per_gram = 3_000
        self.material.price_per_kg = 3_000_000
        self.material.save(update_fields=["sale_price_per_gram", "price_per_kg"])
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.material_price_per_gram, Decimal("1000.0000"))
        self.assertEqual(self.quote.material_cost, 100_000)
        self.assertEqual(self.quote.total_price, 330_000)

    def test_draft_remains_repriceable_until_sent(self):
        self.material.sale_price_per_gram = 1_500
        self.material.save(update_fields=["sale_price_per_gram"])
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.total_price, 380_000)
        self.assertIsNone(self.quote.pricing_snapshot_at)

    def test_sent_to_accepted_does_not_regenerate_price(self):
        self.finalize()
        timestamp = self.quote.pricing_snapshot_at
        self.quote.status = "accepted"
        self.quote.save(update_fields=["status"])
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.pricing_snapshot_at, timestamp)
        self.assertEqual(self.quote.total_price, 330_000)

    def test_prevent_quote_financial_edit_and_reset_after_sent(self):
        self.finalize()
        self.quote.discount = 25_000
        with self.assertRaises(ValidationError):
            self.quote.save()
        self.quote.refresh_from_db()
        self.quote.status = "draft"
        with self.assertRaises(ValidationError):
            self.quote.save()

    def test_prevent_quantity_and_material_change_after_sent(self):
        self.finalize()
        self.order.quantity = 2
        with self.assertRaises(ValidationError):
            self.order.save()
        self.order.refresh_from_db()
        other = Material.objects.create(name="Other snapshot material", price_per_kg=2_000_000)
        self.order.material = other
        with self.assertRaises(ValidationError):
            self.order.save()

    def test_prevent_discount_exceeding_total_and_excess_deposit(self):
        self.quote.discount = self.quote.subtotal + 1
        self.quote.status = "sent"
        with self.assertRaises(ValidationError):
            self.quote.save()
        self.quote.status = "draft"
        self.quote.discount = 0
        self.quote.deposit_percent = 101
        self.quote.status = "sent"
        with self.assertRaises(ValidationError):
            self.quote.save()

    def test_immediately_accepted_quote_is_snapshotted(self):
        self.quote.delete()
        quote = Quote.objects.create(
            order=self.order, status="accepted", material=self.material,
            weight_grams=100, print_time_minutes=60, machine_hourly_rate=100_000,
        )
        self.assertIsNotNone(quote.pricing_snapshot_at)
        self.assertEqual(quote.total_price, 200_000)

    def test_payment_uses_frozen_agreement(self):
        self.finalize()
        self.quote.status = "accepted"
        self.quote.save(update_fields=["status"])
        self.material.sale_price_per_gram = 9_000
        self.material.save(update_fields=["sale_price_per_gram"])
        payment = Payment.objects.create(
            quote=self.quote, method="bank_transfer", payment_kind="balance",
            amount=130_000, status="awaiting_review", ref_id="snapshot-bank-01",
        )
        payment.mark_paid(ref_id="snapshot-bank-01", metadata={"review_source": "test"})
        self.assertEqual(self.quote.paid_amount, 130_000)
        self.assertEqual(self.quote.remaining_amount, 200_000)
        self.assertEqual(self.quote.total_price, 330_000)

    def test_legacy_unfrozen_quote_cannot_receive_manual_admin_money(self):
        # A pre-upgrade finalized quote is detectable and must not be repriced invisibly.
        Quote.objects.filter(pk=self.quote.pk).update(status="accepted")
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("admin:website_order_record_receipt", args=[self.order.pk]),
            {
                "amount": 20_000, "ref_id": "legacy-unfrozen-ref",
                "payment_kind": "deposit", "confirmed": "on",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.count(), 0)

    def test_order_admin_cannot_forge_payment_status(self):
        self.client.force_login(self.staff)
        from .order_finance_admin import ManagedOrderAdminForm
        form = ManagedOrderAdminForm(data={
            "customer": "", "first_name": self.order.first_name, "last_name": self.order.last_name,
            "phone": self.order.phone, "service_type": "3d_print",
            "material": self.material.pk, "color": "", "quantity": 1,
            "description": "regression", "status": "paid",
        }, instance=self.order)
        self.assertFalse(form.is_valid())
        self.assertIn("status", form.errors)

    def test_confirmed_payment_amount_and_status_cannot_be_rewritten(self):
        self.finalize()
        self.quote.status = "accepted"
        self.quote.save(update_fields=["status"])
        payment = Payment.objects.create(
            quote=self.quote, method="bank_transfer", amount=40_000,
            payment_kind="deposit", status="awaiting_review", ref_id="paid-immutable-01",
        )
        payment.mark_paid(ref_id="paid-immutable-01")
        payment.refresh_from_db()
        payment.amount = 50_000
        with self.assertRaises(ValidationError):
            payment.save()
        payment.refresh_from_db()
        payment.status = "failed"
        with self.assertRaises(ValidationError):
            payment.save()
        self.assertEqual(Payment.objects.get(pk=payment.pk).status, "paid")
        self.assertEqual(Payment.objects.get(pk=payment.pk).amount, 40_000)

    def test_manual_bank_reference_cannot_be_double_used_on_other_order(self):
        self.finalize()
        self.quote.status = "accepted"
        self.quote.save(update_fields=["status"])
        Payment.objects.create(
            quote=self.quote, method="bank_transfer", amount=10_000,
            payment_kind="deposit", status="awaiting_review", ref_id="shared-bank-reference",
        )
        second_order = Order.objects.create(
            first_name="Other", last_name="Buyer", phone="09120000031",
            material=self.material, description="another legitimate order",
        )
        Quote.objects.create(
            order=second_order, material=self.material, status="accepted",
            weight_grams=100, print_time_minutes=60, machine_hourly_rate=100_000,
        )
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("admin:website_order_record_receipt", args=[second_order.pk]),
            {"amount": 20_000, "payment_kind": "deposit",
             "ref_id": "shared-bank-reference", "confirmed": "on"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.count(), 1)
