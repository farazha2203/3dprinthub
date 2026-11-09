from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Material, Order, Quote, Payment, PaymentLedgerEntry


class ServiceOrderAdminFinanceTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_superuser("finance-admin", "admin@example.invalid", "test-only-password")
        self.client.force_login(self.staff)
        material = Material.objects.create(
            name="Admin finance test PLA", price_per_kg=1_000_000,
            strength=1, heat_resistance=1, flexibility=1,
            chemical_resistance=1, printability=1,
            main_usage="test", sample_parts="test",
        )
        self.order = Order.objects.create(
            first_name="Test", last_name="User", phone="09120000010",
            material=material, quantity=1, description="finance QA",
        )
        self.quote = Quote.objects.create(
            order=self.order, material=material, weight_grams=100,
            print_time_minutes=60, machine_hourly_rate=100_000,
            status="accepted", discount=20_000,
        )
        self.url = reverse("admin:website_order_record_receipt", args=[self.order.pk])

    def post(self, amount, ref, confirmed=True):
        return self.client.post(self.url, {
            "amount": amount, "ref_id": ref,
            "payment_kind": "deposit",
            "note": "Finance unit QA",
            **({"confirmed": "on"} if confirmed else {}),
        })

    def test_finance_summary_and_receipt_link_render(self):
        response = self.client.get(reverse("admin:website_order_change", args=[self.order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.url)
        self.assertContains(response, "مانده قابل وصول")

    def test_confirmed_manual_receipt_updates_ledger_and_remaining(self):
        self.assertEqual(self.quote.total_price, 180_000)
        response = self.post(60_000, "ref-test-1")
        self.assertEqual(response.status_code, 302)
        payment = Payment.objects.get(quote=self.quote)
        self.assertEqual(payment.status, "paid")
        self.assertEqual(self.quote.paid_amount, 60_000)
        self.assertEqual(self.quote.remaining_amount, 120_000)
        self.assertEqual(PaymentLedgerEntry.objects.filter(payment=payment, entry_type="payment").count(), 1)

    def test_pending_receipt_reserves_but_does_not_reduce_debt(self):
        self.post(70_000, "ref-test-2", confirmed=False)
        self.assertEqual(self.quote.remaining_amount, 180_000)
        self.assertEqual(self.quote.pending_amount, 70_000)
        self.assertEqual(self.quote.available_payment_amount, 110_000)

    def test_overpayment_and_duplicate_reference_blocked(self):
        self.post(60_000, "ref-test-3")
        response = self.post(140_000, "ref-test-4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.count(), 1)
        response = self.post(20_000, "ref-test-3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.count(), 1)

    def test_order_amount_fields_readonly_after_payment(self):
        self.post(20_000, "ref-test-5")
        response = self.client.get(reverse("admin:website_order_change", args=[self.order.pk]))
        self.assertContains(response, "مانده قابل وصول")
        self.assertNotContains(response, 'name="quantity"')
        self.assertNotContains(response, 'name="material"')

    def test_draft_quote_finance_admin_renders_without_action_or_html_error(self):
        from django.contrib import admin
        from .order_finance_admin import order_finance_summary
        Quote.objects.filter(pk=self.quote.pk).update(status="draft", pricing_snapshot_at=None)
        order = Order.objects.get(pk=self.order.pk)
        panel = str(order_finance_summary(order))
        self.assertIn("قیمت هنوز تثبیت نشده است", panel)
        self.assertNotIn("record-receipt/", panel)
        response = self.client.get(reverse("admin:website_order_change", args=[order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "قیمت هنوز تثبیت نشده است")
