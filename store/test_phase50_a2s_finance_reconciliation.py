from __future__ import annotations

from io import StringIO

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import RequestFactory, TestCase

from store.admin import StorePaymentAdmin
from store.finance_reconciliation import (
    STORE_PAYMENT_REVIEW_EVENT,
    collect_finance_reconciliation,
)
from store.models import ProductionJob, StoreOrder, StorePayment
from website.admin import PaymentAdmin as WebsitePaymentAdmin
from website.models import Order as WebsiteOrder
from website.models import Payment, PaymentLedgerEntry, Quote


class Phase50A2SFinanceReconciliationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.customer = user_model.objects.create_user(
            username="a2s-customer",
            email="a2s-customer@example.com",
            password="pass12345",
        )
        self.admin_user = user_model.objects.create_superuser(
            username="a2s-admin",
            email="a2s-admin@example.com",
            password="pass12345",
        )
        self.factory = RequestFactory()

    def _request(self):
        request = self.factory.post("/admin/")
        request.user = self.admin_user
        return request

    def _store_payment(self):
        order = StoreOrder.objects.create(
            user=self.customer,
            shipping_title="پست تست",
            full_name="مشتری تست",
            phone="09120000000",
            email="a2s-customer@example.com",
            province="اصفهان",
            county="اصفهان",
            city="اصفهان",
            address="نشانی تست",
            postal_code="1234567890",
            subtotal=100_000,
            total_amount=100_000,
            status="payment_review",
            payment_status="awaiting_review",
        )
        payment = StorePayment.objects.create(
            order=order,
            amount=100_000,
            method="bank_transfer",
            status="awaiting_review",
            receipt_image="store/payments/receipts/a2s-store.png",
        )
        return order, payment

    def _website_payment(self):
        order = WebsiteOrder.objects.create(
            customer=self.customer,
            first_name="مشتری",
            last_name="تست",
            phone="09120000000",
            quantity=1,
            description="سفارش تست مالی",
            status="accepted",
        )
        quote = Quote.objects.create(
            order=order,
            labor_fee=120_000,
            status="accepted",
            deposit_percent=100,
        )
        payment = Payment.objects.create(
            quote=quote,
            amount=quote.total_price,
            payment_kind="full",
            method="bank_transfer",
            status="awaiting_review",
            receipt_image="payments/receipts/a2s-website.png",
        )
        return order, quote, payment

    def test_empty_reconciliation_is_clean(self):
        result = collect_finance_reconciliation(check_storage=False)
        self.assertTrue(result["ok"])
        self.assertEqual(result["failures"], {})
        self.assertEqual(result["metrics"]["store_payments_total"], 0)
        self.assertEqual(result["metrics"]["website_payments_total"], 0)

    def test_store_admin_approval_records_reviewer_event(self):
        order, payment = self._store_payment()
        model_admin = StorePaymentAdmin(StorePayment, admin.site)
        model_admin.approve_payments(
            self._request(),
            StorePayment.objects.filter(pk=payment.pk),
        )

        payment.refresh_from_db()
        order.refresh_from_db()
        event = order.events.get(title=STORE_PAYMENT_REVIEW_EVENT)

        self.assertEqual(payment.status, "paid")
        self.assertEqual(order.payment_status, "paid")
        self.assertEqual(event.created_by_id, self.admin_user.pk)
        self.assertTrue(ProductionJob.objects.filter(store_order=order).exists())

        result = collect_finance_reconciliation(check_storage=False)
        self.assertTrue(result["ok"], result["failures"])

    def test_store_manual_paid_without_reviewer_fails_closed(self):
        _order, payment = self._store_payment()
        payment.mark_paid("NO-ACTOR")

        result = collect_finance_reconciliation(check_storage=False)

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["failures"].get("store_manual_paid_reviewer_missing"),
            1,
        )

    def test_website_admin_approval_records_reviewer_in_ledger(self):
        order, _quote, payment = self._website_payment()
        model_admin = WebsitePaymentAdmin(Payment, admin.site)
        model_admin.mark_selected_paid(
            self._request(),
            Payment.objects.filter(pk=payment.pk),
        )

        payment.refresh_from_db()
        order.refresh_from_db()
        ledger = PaymentLedgerEntry.objects.get(payment=payment)

        self.assertEqual(payment.status, "paid")
        self.assertEqual(order.status, "paid")
        self.assertEqual(
            ledger.metadata.get("reviewed_by_user_id"),
            self.admin_user.pk,
        )
        self.assertEqual(ledger.metadata.get("review_source"), "admin_manual")
        self.assertTrue(ProductionJob.objects.filter(custom_order=order).exists())

        result = collect_finance_reconciliation(check_storage=False)
        self.assertTrue(result["ok"], result["failures"])

    def test_website_manual_paid_without_reviewer_fails_closed(self):
        _order, _quote, payment = self._website_payment()
        payment.mark_paid(ref_id="NO-REVIEWER")

        result = collect_finance_reconciliation(check_storage=False)

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["failures"].get("website_manual_paid_reviewer_missing"),
            1,
        )

    def test_command_reports_clean_empty_authorities(self):
        output = StringIO()
        call_command(
            "phase50_finance_reconciliation",
            skip_storage_check=True,
            stdout=output,
        )
        self.assertIn("PHASE50_FINANCE_RECONCILIATION=OK", output.getvalue())

    def test_command_fails_on_missing_reviewer_evidence(self):
        _order, payment = self._store_payment()
        payment.mark_paid("NO-ACTOR")
        output = StringIO()
        with self.assertRaises(CommandError):
            call_command(
                "phase50_finance_reconciliation",
                skip_storage_check=True,
                stdout=output,
            )
        self.assertIn(
            "FAIL:store_manual_paid_reviewer_missing=1",
            output.getvalue(),
        )
