"""Service Quote credit notes and real-world refund attestations (no bank calls)."""
from uuid import UUID, uuid4

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse

from store.models import ShippingMethod
from store.finance_reconciliation import collect_finance_reconciliation
from website.models import (
    Material, Order, Payment, PaymentLedgerEntry, Quote,
    ServiceCreditNote, ServiceRefund, ServiceOrderDelivery,
)
from website.payment_services import PaymentFlowError
from website.service_adjustments import (
    ServiceFinanceError, approve_service_refund, cancel_service_refund, confirm_service_refund,
    issue_service_credit_note, request_service_refund,
)


class ServiceAdjustmentTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="service-refund-finance", email="finance@example.invalid",
            password="unit-test-password",
        )
        self.checker = User.objects.create_superuser(
            username="service-refund-checker", email="checker@example.invalid",
            password="unit-test-password",
        )
        self.customer = User.objects.create_user(
            username="service-refund-buyer", email="buyer@example.invalid",
            password="unit-test-password",
        )
        self.material = Material.objects.create(
            name="Refund test PETG", price_per_kg=1000000,
            sale_price_per_gram=1000, main_usage="test", sample_parts="test",
            is_active=True,
        )
        self.order = Order.objects.create(
            customer=self.customer, first_name="Buyer", last_name="Test",
            phone="09120000012", service_type="3d_print", material=self.material,
            description="Credit and refund cycle", quantity=1, status="accepted",
        )
        self.quote = Quote.objects.create(
            order=self.order, material=self.material, weight_grams=100,
            print_time_minutes=60, machine_hourly_rate=100000, status="accepted",
        )
        self.assertEqual(self.quote.total_price, 200000)
        self.assertIsNotNone(self.quote.pricing_snapshot_at)

    def pay(self, amount=200000, method="cash", ref="original-cash-100"):
        p = Payment.objects.create(
            quote=self.quote, amount=amount, method=method,
            payment_kind="full", status="awaiting_review", ref_id=ref,
        )
        p.mark_paid(
            ref_id=ref, metadata={
                "review_source": "order_admin", "reviewed_by_user_id": self.owner.pk,
            },
        )
        return p

    def credit(self, amount=60000, reference="credit-A"):
        return issue_service_credit_note(
            quote_id=self.quote.pk, amount=amount,
            reference=reference, reason="Production price reduction approved",
            actor=self.owner,
        )

    def request_refund(self, payment, amount=25000, key=None, method="bank_transfer"):
        return request_service_refund(
            quote_id=self.quote.pk, payment_id=payment.pk,
            amount=amount, method=method, reason="Customer overpayment on revised invoice",
            actor=self.owner, request_key=key,
        )

    def approve_refund(self, refund):
        return approve_service_refund(
            refund_id=refund.pk, approval_note="Independent payment decision verified",
            actor=self.checker,
        )

    def test_credit_reduces_collectible_debt_without_rewriting_original_quote(self):
        note = self.credit()
        self.assertEqual(self.quote.total_price, 200000)
        self.assertEqual(self.quote.pricing_snapshot_total, 200000)
        self.assertEqual(self.quote.credit_note_total, 60000)
        self.assertEqual(self.quote.effective_total_price, 140000)
        self.assertEqual(self.quote.remaining_amount, 140000)
        self.assertEqual(self.quote.available_payment_amount, 140000)
        self.assertEqual(Payment.objects.count(), 0)
        self.assertEqual(PaymentLedgerEntry.objects.count(), 0)
        self.assertEqual(note.issued_by, self.owner)
        self.assertIsNotNone(note.created_at)

    def test_credit_is_idempotent_and_cannot_be_rewritten_or_deleted(self):
        original = self.credit()
        same = self.credit()
        self.assertEqual(original.pk, same.pk)
        self.assertEqual(ServiceCreditNote.objects.count(), 1)
        with self.assertRaises(ServiceFinanceError):
            self.credit(amount=61000)
        original.amount = 1000
        with self.assertRaises(ValidationError):
            original.save()
        with self.assertRaises(ValidationError):
            original.delete()
        original.refresh_from_db()
        self.assertEqual(original.amount, 60000)

    def test_cannot_credit_above_original_or_with_pending_gateway_or_receipt(self):
        with self.assertRaises(ServiceFinanceError):
            self.credit(amount=200001)
        pending = Payment.objects.create(
            quote=self.quote, amount=50000,
            method="gateway", payment_kind="deposit", status="pending",
        )
        with self.assertRaises(ServiceFinanceError):
            self.credit()
        pending.status = "cancelled"
        pending.save()
        self.assertEqual(self.credit().amount, 60000)

    def test_credit_requires_finalized_accepted_quote(self):
        Quote.objects.filter(pk=self.quote.pk).update(status="sent")
        with self.assertRaises(ServiceFinanceError):
            self.credit()
        Quote.objects.filter(pk=self.quote.pk).update(status="accepted", pricing_snapshot_at=None)
        with self.assertRaises(ServiceFinanceError):
            self.credit()

    def test_only_staff_with_appropriate_permission_can_issue_credit(self):
        with self.assertRaises(PermissionDenied):
            issue_service_credit_note(
                quote_id=self.quote.pk, amount=100,
                reference="credit-untrusted", reason="Untrusted control",
                actor=self.customer,
            )

    def test_refund_request_does_not_touch_cash_ledger_until_external_confirmation(self):
        p = self.pay()
        self.credit()
        old_credit_count = PaymentLedgerEntry.objects.filter(entry_type="payment").count()
        requested = self.request_refund(p)
        self.assertEqual(requested.status, "requested")
        self.assertEqual(self.quote.gross_paid_amount, 200000)
        self.assertEqual(self.quote.refunded_amount, 0)
        self.assertEqual(self.quote.paid_amount, 200000)
        self.assertEqual(self.quote.refundable_excess, 60000)
        self.assertEqual(PaymentLedgerEntry.objects.count(), old_credit_count)
        self.assertIsNone(requested.ledger_entry_id)
        self.assertIsNone(requested.payout_reference)

    def test_real_refund_debits_ledger_and_preserves_paid_receipt(self):
        p = self.pay()
        note = self.credit()
        requested = self.request_refund(p, amount=60000)
        self.approve_refund(requested)
        with self.assertRaises(ServiceFinanceError):
            confirm_service_refund(
                refund_id=requested.pk, actor=self.checker,
                payout_reference="bank-real-123", confirmed_external_payout=False,
            )
        done = confirm_service_refund(
            refund_id=requested.pk, actor=self.checker,
            payout_reference="bank-real-123", confirmed_external_payout=True,
        )
        self.assertEqual(done.status, "completed")
        self.assertEqual(done.ledger_entry.entry_type, "refund")
        self.assertEqual(done.ledger_entry.direction, "debit")
        self.assertEqual(done.ledger_entry.amount, 60000)
        self.assertEqual(done.ledger_entry.payment_id, p.pk)
        self.assertEqual(done.completed_by, self.checker)
        self.assertEqual(done.ledger_entry.metadata["refund_id"], requested.pk)
        self.assertEqual(self.quote.refunded_amount, 60000)
        self.assertEqual(self.quote.paid_amount, 140000)
        self.assertEqual(self.quote.remaining_amount, 0)
        self.assertEqual(self.quote.refundable_excess, 0)
        self.assertEqual(self.quote.total_price, 200000)
        self.assertEqual(self.quote.effective_total_price, 140000)
        self.assertEqual(note.amount, 60000)
        p.refresh_from_db()
        self.assertEqual(p.status, "paid")
        self.assertEqual(p.amount, 200000)
        self.assertEqual(PaymentLedgerEntry.objects.count(), 2)

    def test_confirm_repeat_same_proof_is_idempotent_different_proof_blocked(self):
        p = self.pay()
        self.credit()
        req = self.request_refund(p, amount=30000)
        self.approve_refund(req)
        one = confirm_service_refund(
            refund_id=req.pk, actor=self.checker,
            payout_reference="refund-confirm-01", confirmed_external_payout=True,
        )
        two = confirm_service_refund(
            refund_id=req.pk, actor=self.checker,
            payout_reference="refund-confirm-01", confirmed_external_payout=True,
        )
        self.assertEqual(one.ledger_entry_id, two.ledger_entry_id)
        self.assertEqual(PaymentLedgerEntry.objects.filter(entry_type="refund").count(), 1)
        with self.assertRaises(ServiceFinanceError):
            confirm_service_refund(
                refund_id=req.pk, actor=self.checker,
                payout_reference="another-bank-trace", confirmed_external_payout=True,
            )
        one.reason = "changed"
        with self.assertRaises(ValidationError):
            one.save()
        with self.assertRaises(ValidationError):
            one.delete()

    def test_pending_requests_reserve_excess_and_cancel_releases_it(self):
        p = self.pay()
        self.credit()
        req = self.request_refund(p, amount=40000)
        with self.assertRaises(ServiceFinanceError):
            self.request_refund(p, amount=30000)
        cancel_service_refund(
            refund_id=req.pk, actor=self.owner,
            reason="Finance cancelled duplicate refund request",
        )
        self.assertEqual(req.__class__.objects.get(pk=req.pk).status, "cancelled")
        self.assertEqual(PaymentLedgerEntry.objects.filter(entry_type="refund").count(), 0)
        new = self.request_refund(p, amount=60000)
        self.assertEqual(new.amount, 60000)
        with self.assertRaises(ServiceFinanceError):
            confirm_service_refund(
                refund_id=req.pk, actor=self.checker,
                payout_reference="refund-cancelled", confirmed_external_payout=True,
            )

    def test_request_token_idempotency_and_cross_payment_protection(self):
        p = self.pay()
        self.credit()
        key = uuid4()
        first = self.request_refund(p, amount=30000, key=key)
        second = self.request_refund(p, amount=30000, key=key)
        self.assertEqual(first.pk, second.pk)
        with self.assertRaises(ServiceFinanceError):
            self.request_refund(p, amount=20000, key=key)
        other = Payment.objects.create(
            quote=self.quote, status="awaiting_review", amount=12000, method="cash",
        )
        with self.assertRaises(ServiceFinanceError):
            self.request_refund(other, amount=20000)

    def test_no_refund_before_credit_or_over_paid_amount(self):
        p = self.pay(100000)
        with self.assertRaises(ServiceFinanceError):
            self.request_refund(p)
        self.credit(amount=150000)
        self.assertEqual(self.quote.refundable_excess, 50000)
        with self.assertRaises(ServiceFinanceError):
            self.request_refund(p, amount=51000)
        req = self.request_refund(p, amount=50000)
        self.assertEqual(req.amount, 50000)

    def test_payment_cannot_be_marked_paid_after_credit_above_adjusted_remainder(self):
        self.credit(amount=60000)
        pending = Payment.objects.create(
            quote=self.quote, status="awaiting_review",
            amount=200000, method="bank_transfer", ref_id="invalid-after-credit",
        )
        with self.assertRaises(PaymentFlowError):
            pending.mark_paid(
                ref_id="invalid-after-credit",
                metadata={"reviewed_by_user_id": self.owner.pk, "review_source": "admin_manual"},
            )
        pending.refresh_from_db()
        self.assertEqual(pending.status, "awaiting_review")
        self.assertEqual(PaymentLedgerEntry.objects.count(), 0)

    def test_refund_cannot_complete_with_reused_external_bank_proof(self):
        p = self.pay()
        self.credit()
        one = self.request_refund(p, amount=20000)
        two = self.request_refund(p, amount=20000)
        self.approve_refund(one)
        self.approve_refund(two)
        confirm_service_refund(
            refund_id=one.pk, actor=self.checker,
            payout_reference="BANK-REUSED-1", confirmed_external_payout=True,
        )
        with self.assertRaises(ServiceFinanceError):
            confirm_service_refund(
                refund_id=two.pk, actor=self.checker,
                payout_reference="BANK-REUSED-1", confirmed_external_payout=True,
            )
        self.assertEqual(self.quote.refunded_amount, 20000)

    def test_admin_credit_and_refund_forms_enforce_permissions(self):
        credit_url = reverse("admin:website_order_issue_credit_note", args=[self.order.pk])
        refund_url = reverse("admin:website_order_request_refund", args=[self.order.pk])
        self.client.force_login(self.customer)
        self.assertNotEqual(self.client.get(credit_url).status_code, 200)
        self.assertNotEqual(self.client.get(refund_url).status_code, 200)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(credit_url).status_code, 200)
        self.assertEqual(self.client.get(refund_url).status_code, 200)

    def test_admin_browser_flow_credit_request_confirm_and_customer_visibility(self):
        p = self.pay()
        self.client.force_login(self.owner)
        credit_url = reverse("admin:website_order_issue_credit_note", args=[self.order.pk])
        response = self.client.post(credit_url, {
            "amount": 60000, "reference": "CN-WEB-123",
            "reason": "Verified agreement reduction on client request", "acknowledged": "on",
        })
        self.assertEqual(response.status_code, 302, getattr(response, "content", b""))
        self.assertEqual(self.quote.credit_note_total, 60000)
        req_url = reverse("admin:website_order_request_refund", args=[self.order.pk])
        r = self.client.post(req_url, {
            "request_key": str(uuid4()), "original_payment": p.pk,
            "amount": 60000, "method": "bank_transfer",
            "reason": "Customer was charged original amount before revised invoice",
            "acknowledged": "on",
        })
        self.assertEqual(r.status_code, 302)
        refund = ServiceRefund.objects.get(quote=self.quote)
        complete_url = reverse(
            "admin:website_order_complete_refund", args=[self.order.pk, refund.pk]
        )
        self.client.force_login(self.checker)
        approved = self.client.post(complete_url, {
            "action": "approve", "approval_note": "Independent refund approved after proof review",
        })
        self.assertEqual(approved.status_code, 302)
        no_real_payout = self.client.post(complete_url, {
            "action": "complete", "payout_reference": "BANK-WEB-VERIFY-01",
        })
        self.assertEqual(no_real_payout.status_code, 200)
        self.assertEqual(self.quote.refunded_amount, 0)
        completed = self.client.post(complete_url, {
            "action": "complete", "payout_reference": "BANK-WEB-VERIFY-01",
            "confirmed": "on",
        })
        self.assertEqual(completed.status_code, 302)
        self.assertEqual(self.quote.refunded_amount, 60000)
        self.client.force_login(self.customer)
        customer_url = reverse("website:quote_detail", args=[self.order.public_token])
        view = self.client.get(customer_url)
        self.assertEqual(view.status_code, 200)
        self.assertContains(view, "CN-WEB-123")
        self.assertEqual(self.quote.effective_total_price, 140000)
        self.assertContains(view, "مبلغ قرارداد پس از اصلاحیه")
        self.assertContains(view, "استرداد")

    def test_delivery_uses_net_settlement_after_approved_credit_note(self):
        p = self.pay(140000)
        self.credit()
        pickup, _ = ShippingMethod.objects.update_or_create(
            code="pickup", defaults={"title": "Customer pickup", "is_active": True}
        )
        delivery = ServiceOrderDelivery.objects.create(
            order=self.order, shipping_method=pickup, status="delivered",
            recipient_name="Paying customer", recorded_by=self.owner,
        )
        self.assertEqual(delivery.status, "delivered")
        self.assertEqual(self.quote.remaining_amount, 0)
        self.assertEqual(self.quote.paid_amount, 140000)

    def test_full_credit_cannot_permit_free_delivery_without_real_receipt(self):
        self.credit(amount=200000)
        pickup, _ = ShippingMethod.objects.update_or_create(
            code="pickup", defaults={"title": "Customer pickup", "is_active": True}
        )
        with self.assertRaises(ValidationError):
            ServiceOrderDelivery.objects.create(
                order=self.order, shipping_method=pickup, status="delivered",
                recipient_name="Customer", recorded_by=self.owner,
            )

    def test_reconciliation_sees_cash_refund_debit_and_credit_note_as_distinct(self):
        p = self.pay()
        self.credit()
        ref = self.request_refund(p, amount=20000, method="cash")
        self.approve_refund(ref)
        confirm_service_refund(
            refund_id=ref.pk, actor=self.checker,
            payout_reference="CASH-VOUCHER-001", confirmed_external_payout=True,
        )
        result = collect_finance_reconciliation(check_storage=False)
        self.assertIn("website_ledger_credit_sum", result["metrics"])
        # Existing diagnostics remain callable and the original payment credit survives.
        self.assertEqual(PaymentLedgerEntry.objects.filter(entry_type="payment").count(), 1)
        self.assertEqual(PaymentLedgerEntry.objects.filter(entry_type="refund").count(), 1)

    def test_multiple_partial_receipts_and_refunds_respect_original_payment_caps(self):
        first = self.pay(70000, ref="cash-first")
        second = self.pay(130000, ref="cash-second")
        self.credit(amount=90000)
        one = self.request_refund(first, amount=70000)
        two = self.request_refund(second, amount=20000)
        self.approve_refund(one)
        self.approve_refund(two)
        confirm_service_refund(
            refund_id=one.pk, actor=self.checker,
            payout_reference="BANK-FIRST-REFUND", confirmed_external_payout=True,
        )
        confirm_service_refund(
            refund_id=two.pk, actor=self.checker,
            payout_reference="BANK-SECOND-REFUND", confirmed_external_payout=True,
        )
        self.assertEqual(self.quote.refunded_amount, 90000)
        self.assertEqual(self.quote.paid_amount, 110000)
        self.assertEqual(self.quote.effective_total_price, 110000)
        self.assertEqual(self.quote.remaining_amount, 0)
        self.assertEqual(PaymentLedgerEntry.objects.filter(entry_type="refund").count(), 2)
        self.assertEqual(first.amount, 70000)
        self.assertEqual(second.amount, 130000)

    def test_multiple_credit_notes_do_not_overcredit(self):
        self.credit(amount=120000, reference="CN-ONE")
        self.credit(amount=80000, reference="CN-TWO")
        self.assertEqual(self.quote.effective_total_price, 0)
        with self.assertRaises(ServiceFinanceError):
            self.credit(amount=1, reference="CN-THREE")
        self.assertEqual(ServiceCreditNote.objects.count(), 2)
        self.assertEqual(self.quote.total_price, 200000)

    def test_refund_ledger_entries_cannot_be_overwritten_or_deleted(self):
        original = self.pay()
        self.credit()
        requested = self.request_refund(original, amount=50000)
        self.approve_refund(requested)
        refund = confirm_service_refund(
            refund_id=requested.pk, actor=self.checker,
            payout_reference="PROOF-AUDIT-001", confirmed_external_payout=True,
        )
        ledger = refund.ledger_entry
        ledger.amount = 1
        with self.assertRaises(ValidationError):
            ledger.save()
        ledger.refresh_from_db()
        ledger.direction = "credit"
        with self.assertRaises(ValidationError):
            ledger.save()
        with self.assertRaises(ValidationError):
            ledger.delete()
        self.assertEqual(PaymentLedgerEntry.objects.get(pk=ledger.pk).amount, 50000)

    def test_customer_cannot_view_another_customer_refund_or_credit(self):
        self.pay()
        self.credit()
        second_user = User.objects.create_user("unrelated-service-user", password="test-password")
        self.client.force_login(second_user)
        response = self.client.get(reverse("website:quote_detail", args=[self.order.public_token]))
        self.assertEqual(response.status_code, 404)

    def test_late_receipt_does_not_regress_completed_production_status(self):
        self.order.status = "done"
        self.order.save(update_fields=["status"])
        payment = self.pay(amount=200000)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "done")
        self.assertEqual(self.quote.paid_amount, 200000)
        payment.refresh_from_db()
        self.assertEqual(payment.status, "paid")

    def test_operator_confirmed_bank_receipt_can_use_private_finance_evidence(self):
        self.pay(amount=200000, method="bank_transfer", ref="bank-office-verified")
        report = collect_finance_reconciliation(check_storage=False)
        self.assertNotIn("website_manual_receipt_missing", report["failures"])
        self.assertNotIn("website_manual_paid_reviewer_missing", report["failures"])

    def test_direct_overcredit_model_save_is_rejected(self):
        with self.assertRaises(ValidationError):
            ServiceCreditNote.objects.create(
                quote=self.quote, amount=200001, reference="UNSAFE-CREDIT-DIRECT",
                reason="This is an invalid over-credit attempt", issued_by=self.owner,
            )
        self.assertEqual(ServiceCreditNote.objects.count(), 0)

    def test_independent_checker_required_before_any_service_refund_debit(self):
        p = self.pay()
        self.credit()
        refund = self.request_refund(p, amount=45000)
        with self.assertRaises(ServiceFinanceError):
            approve_service_refund(
                refund_id=refund.pk, approval_note="Trying to approve own refund",
                actor=self.owner,
            )
        with self.assertRaises(ServiceFinanceError):
            confirm_service_refund(
                refund_id=refund.pk, payout_reference="PREAPPROVAL-BANK-01",
                actor=self.checker, confirmed_external_payout=True,
            )
        self.assertEqual(self.quote.refunded_amount, 0)
        approved = self.approve_refund(refund)
        self.assertEqual(approved.status, "approved")
        self.assertEqual(approved.approved_by_id, self.checker.pk)
        self.assertEqual(approved.requested_by_id, self.owner.pk)
        self.assertEqual(PaymentLedgerEntry.objects.filter(entry_type="refund").count(), 0)
        self.assertEqual(self.quote.refundable_excess, 60000)
        self.assertEqual(self.quote.remaining_amount, 0)
        with self.assertRaises(ServiceFinanceError):
            self.request_refund(p, amount=16000)
        with self.assertRaises(ServiceFinanceError):
            confirm_service_refund(
                refund_id=refund.pk, payout_reference="OWNER-SELF-PAYOUT",
                actor=self.owner, confirmed_external_payout=True,
            )
        closed = confirm_service_refund(
            refund_id=refund.pk, payout_reference="CHECKER-PAYOUT-01",
            actor=self.checker, confirmed_external_payout=True,
        )
        self.assertEqual(closed.status, "completed")
        self.assertEqual(closed.ledger_entry.metadata["approved_by_user_id"], self.checker.pk)
        self.assertEqual(closed.ledger_entry.metadata["requested_by_user_id"], self.owner.pk)
        self.assertEqual(closed.ledger_entry.metadata["confirmed_by_user_id"], self.checker.pk)

    def test_service_approval_is_idempotent_immutable_and_cancel_releases_hold(self):
        payment = self.pay()
        self.credit()
        refund = self.request_refund(payment, amount=40000)
        first = self.approve_refund(refund)
        second = self.approve_refund(refund)
        self.assertEqual(first.pk, second.pk)
        with self.assertRaises(ServiceFinanceError):
            approve_service_refund(
                refund_id=refund.pk, approval_note="Conflicting second endorsement",
                actor=self.checker,
            )
        first.approval_note = "Edited after approval"
        with self.assertRaises(ValidationError):
            first.save()
        first.refresh_from_db()
        with self.assertRaises(ServiceFinanceError):
            self.request_refund(payment, amount=30000)
        cancel_service_refund(
            refund_id=refund.pk, reason="Approved but external payout was cancelled",
            actor=self.checker,
        )
        self.assertEqual(ServiceRefund.objects.get(pk=refund.pk).status, "cancelled")
        self.assertEqual(PaymentLedgerEntry.objects.filter(entry_type="refund").count(), 0)
        new = self.request_refund(payment, amount=60000)
        self.assertEqual(new.status, "requested")

    def test_service_dedicated_approval_permission_cannot_be_bypassed(self):
        payment = self.pay()
        self.credit()
        refund = self.request_refund(payment, amount=50000)
        finance_user = User.objects.create_user(
            username="service-finance-request-only", password="test-password",
            is_staff=True, is_active=True,
        )
        with self.assertRaises(PermissionDenied):
            approve_service_refund(
                refund_id=refund.pk, approval_note="Not authorized to endorse",
                actor=finance_user,
            )
        with self.assertRaises(PermissionDenied):
            approve_service_refund(
                refund_id=refund.pk, approval_note="Untrusted customer actor",
                actor=self.customer,
            )
        refund.status = "completed"
        with self.assertRaises(ValidationError):
            refund.save()
        self.assertEqual(self.quote.refunded_amount, 0)

    def test_independent_approval_reconciliation_flags_malicious_updated_record(self):
        payment = self.pay()
        self.credit()
        refund = self.request_refund(payment, amount=30000)
        self.approve_refund(refund)
        ServiceRefund.objects.filter(pk=refund.pk).update(approved_by=self.owner)
        audit = collect_finance_reconciliation(check_storage=False)
        self.assertEqual(audit["failures"].get("website_refund_independent_approval_missing"), 1)

    def test_approved_service_refund_cannot_be_cancelled_by_original_requester(self):
        payment = self.pay()
        self.credit()
        refund = self.request_refund(payment, amount=45000)
        self.approve_refund(refund)
        with self.assertRaises(ServiceFinanceError):
            cancel_service_refund(
                refund_id=refund.pk, reason="Requester tries to cancel approved payment",
                actor=self.owner,
            )
        self.assertEqual(ServiceRefund.objects.get(pk=refund.pk).status, "approved")
        cancel_service_refund(
            refund_id=refund.pk, reason="Authorized second finance reviewer cancelled",
            actor=self.checker,
        )
        self.assertEqual(ServiceRefund.objects.get(pk=refund.pk).status, "cancelled")
        self.assertEqual(self.quote.refunded_amount, 0)

    def test_service_approval_only_staff_cannot_finalize_without_change_permission(self):
        from django.contrib.auth.models import Permission
        payment = self.pay()
        self.credit()
        refund = self.request_refund(payment, amount=30000)
        reviewer = User.objects.create_user(
            username="service-approver-only", password="test-password",
            is_staff=True, is_active=True,
        )
        reviewer.user_permissions.add(
            Permission.objects.get(content_type__app_label="website", codename="approve_servicerefund")
        )
        approved = approve_service_refund(
            refund_id=refund.pk, approval_note="Separate limited finance reviewer",
            actor=reviewer,
        )
        self.assertEqual(approved.status, "approved")
        with self.assertRaises(PermissionDenied):
            confirm_service_refund(
                refund_id=refund.pk, payout_reference="ROLE-NO-PAYOUT-PERMISSION",
                actor=reviewer, confirmed_external_payout=True,
            )
        self.assertEqual(PaymentLedgerEntry.objects.filter(entry_type="refund").count(), 0)

    def test_admin_limited_second_reviewer_can_approve_but_never_edit_order_or_pay(self):
        from django.contrib.auth.models import Permission

        original_payment = self.pay()
        self.credit()
        refund = self.request_refund(original_payment, amount=30000)
        reviewer = User.objects.create_user(
            username="service-limited-admin-reviewer", password="test-password",
            is_staff=True, is_active=True,
        )
        reviewer.user_permissions.add(*Permission.objects.filter(
            content_type__app_label="website",
            codename__in=["view_order", "approve_servicerefund"],
        ))
        self.assertTrue(reviewer.has_perm("website.view_order"))
        self.assertTrue(reviewer.has_perm("website.approve_servicerefund"))
        self.assertFalse(reviewer.has_perm("website.change_order"))
        self.assertFalse(reviewer.has_perm("website.change_servicerefund"))
        self.client.force_login(reviewer)
        url = reverse("admin:website_order_complete_refund",
                      args=[self.order.pk, refund.pk])
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "تأیید مستقل بدون انتقال وجه")
        self.assertNotContains(page, "لغو درخواست بدون پرداخت")
        # Even crafting a POST cannot bypass the custom reviewer permission.
        invalid = self.client.post(url, {
            "action": "cancel",
            "cancellation_reason": "Not authorized to cancel a refund",
        })
        self.assertEqual(invalid.status_code, 200)
        self.assertEqual(ServiceRefund.objects.get(pk=refund.pk).status, "requested")
        reviewed = self.client.post(url, {
            "action": "approve",
            "approval_note": "Independent limited reviewer verified this refund",
        })
        self.assertEqual(reviewed.status_code, 302)
        self.assertEqual(ServiceRefund.objects.get(pk=refund.pk).status, "approved")
        self.assertEqual(PaymentLedgerEntry.objects.filter(entry_type="refund").count(), 0)
        # Reviewer cannot create a real bank debit or modify the parent order.
        readonly = self.client.get(url)
        self.assertEqual(readonly.status_code, 200)
        self.assertNotContains(readonly, 'name="action"')
        denied = self.client.post(url, {
            "action": "complete", "payout_reference": "NO-BANK-RECEIPT",
            "confirmed": "on",
        })
        self.assertEqual(denied.status_code, 200)
        self.assertEqual(PaymentLedgerEntry.objects.filter(entry_type="refund").count(), 0)
        self.assertNotEqual(
            self.client.get(reverse("admin:website_order_request_refund",
                                    args=[self.order.pk])).status_code, 200,
        )
