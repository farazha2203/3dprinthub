"""RMA acceptance across StoreOrderItem, ProductVariant, physical stock and proven refunds."""
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from website.models import Material, SEOSettings
from store.models import (
    Category, InventoryMovement, PricingSetting, PrintQuality,
    Product, ProductVariant, ReturnRequest, Shipment, ShippingMethod,
    StoreOrder, StoreOrderItem, StorePayment, StoreReturnInspection,
    StoreReturnRefund, StoreReturnRefundLedger,
)
from store.services import reserve_order_inventory, transition_order
from store.rma_services import (
    StoreRMAError, submit_return_request, decide_store_return, inspect_return,
    request_store_return_refund, approve_store_return_refund,
    confirm_store_return_refund, cancel_store_return_refund,
    full_store_order_refund_proven,
)

User = get_user_model()


class StoreVariantRMATests(TestCase):
    def setUp(self):
        PricingSetting.objects.create(default_hourly_rate=100000, default_labor_percent=Decimal("20"))
        self.staff = User.objects.create_superuser("rma-finance-operator", "rma@example.invalid", "test-password")
        self.checker = User.objects.create_superuser("rma-finance-reviewer", "reviewer@example.invalid", "test-password")
        self.buyer = User.objects.create_user("rma-shopper", "buyer@example.invalid", "test-password")
        self.other = User.objects.create_user("unrelated-buyer", "other@example.invalid", "test-password")
        self.material = Material.objects.create(
            name="RMA ABS", price_per_kg=1000000,
            main_usage="RMA regression", sample_parts="test part",
        )
        self.quality = PrintQuality.objects.create(code="rma-pro", name="RMA Pro")
        self.category = Category.objects.create(name="RMA parts", slug="rma-parts", section="industrial")
        self.product = Product.objects.create(
            category=self.category, title="Machine bracket", sku="RMA-01", slug="rma-bracket",
            short_description="Test SKU", description="RMA test SKU", main_image="store/test.webp",
        )
        self.variant = ProductVariant.objects.create(
            product=self.product, material=self.material, quality=self.quality,
            code="RMA-ABS-BLACK", material_weight_grams=Decimal("25"),
            final_weight_grams=Decimal("20"), shipping_weight_grams=Decimal("30"),
            print_time_minutes=50, track_inventory=True, stock_quantity=8,
            reserved_quantity=0, stock_status="in_stock",
        )
        self.shipping, _ = ShippingMethod.objects.update_or_create(
            code="rma-courier", defaults={"title": "Courier", "flat_fee": 0, "is_active": True}
        )
        SEOSettings.objects.create(site_url="https://3dprinthub.ir", merchant_return_days=7)
        self.order = StoreOrder.objects.create(
            user=self.buyer, status="awaiting_payment", payment_status="pending",
            shipping_method=self.shipping, shipping_title=self.shipping.title,
            full_name="Buyer Test", phone="09120000008", province="اصفهان", county="اصفهان",
            city="اصفهان", address="Fake test address", postal_code="1234567890",
            subtotal=300000, shipping_fee=20000, total_amount=320000,
        )
        self.item = StoreOrderItem.objects.create(
            order=self.order, product=self.product, variant=self.variant,
            product_title=self.product.title, product_sku=self.product.sku,
            variant_code=self.variant.code, material_name=self.material.name,
            quality_name=self.quality.name, unit_price=100000,
            quantity=3, line_total=300000, unit_weight_grams=Decimal("30"),
        )
        reserve_order_inventory(self.order)
        self.payment = StorePayment.objects.create(
            order=self.order, amount=320000, method="bank_transfer",
            status="awaiting_review", ref_id="RMA-ORIGINAL-01",
        )
        self.payment.mark_paid("RMA-ORIGINAL-01", actor=self.staff)
        transition_order(self.order, "delivered", actor=self.staff)
        self.variant.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 5)
        self.assertEqual(self.variant.reserved_quantity, 0)
        self.assertEqual(self.order.payment_status, "paid")

    def submit(self, quantity=1, item=None, user=None):
        return submit_return_request(
            order_id=self.order.pk,
            item_id=(item or self.item).pk,
            quantity=quantity, reason="defect",
            description="Product cracked during first test",
            user=user or self.buyer,
        )

    def approve(self, quantity=1):
        r = self.submit(quantity)
        decide_store_return(
            return_id=r.pk, decision="approved",
            response="Photos verified and authorized physical return", actor=self.staff,
        )
        r.refresh_from_db()
        return r

    def inspect(self, quantity=2, restock=1):
        r = self.approve(quantity)
        receipt = inspect_return(
            return_id=r.pk, received_quantity=quantity,
            restock_quantity=restock, inspection_note="Restock usable pieces, scrap the broken ones",
            actor=self.staff,
        )
        return r, receipt

    def refund(self, rma, amount=100000, *, payment=None, key=None):
        return request_store_return_refund(
            return_id=rma.pk, payment_id=(payment or self.payment).pk,
            amount=amount, method="bank_transfer",
            reason="Refund after certified physical return",
            actor=self.staff, request_key=key,
        )

    def approve_refund(self, refund):
        return approve_store_return_refund(
            refund_id=refund.pk, approval_note="Independent store return finance review",
            actor=self.checker,
        )

    def test_checkout_sale_consumes_real_variant_stock_before_return(self):
        self.assertEqual(self.variant.stock_quantity, 5)
        self.assertEqual(self.item.variant_code, self.variant.code)
        self.assertEqual(InventoryMovement.objects.filter(
            order=self.order, variant=self.variant, movement_type="sale"
        ).count(), 1)

    def test_customer_cannot_overclaim_or_claim_other_buyer_order(self):
        self.submit(2)
        with self.assertRaises(StoreRMAError):
            self.submit(2)
        with self.assertRaises(StoreRMAError):
            self.submit(1, user=self.other)
        self.assertEqual(ReturnRequest.objects.filter(order=self.order).count(), 1)

    def test_rejection_releases_claimed_quantity(self):
        a = self.submit(3)
        decide_store_return(
            return_id=a.pk, decision="rejected",
            response="No physical defect on photographs; rejected", actor=self.staff,
        )
        b = self.submit(3)
        self.assertEqual(b.quantity, 3)

    def test_only_authorized_operator_can_approve_or_inspect(self):
        r = self.submit()
        with self.assertRaises(PermissionDenied):
            decide_store_return(
                return_id=r.pk, decision="approved",
                response="Unauthorized reviewer attempt", actor=self.buyer,
            )
        with self.assertRaises(PermissionDenied):
            inspect_return(
                return_id=r.pk, received_quantity=1, restock_quantity=1,
                inspection_note="Unauthorized restock attempt", actor=self.buyer,
            )
        self.assertEqual(InventoryMovement.objects.filter(movement_type="return").count(), 0)

    def test_cannot_restock_before_review_or_past_sold_count(self):
        r = self.submit(quantity=2)
        with self.assertRaises(StoreRMAError):
            inspect_return(
                return_id=r.pk, received_quantity=2, restock_quantity=2,
                inspection_note="Physically still missing", actor=self.staff,
            )
        decide_store_return(
            return_id=r.pk, decision="approved",
            response="Decision confirmed after review", actor=self.staff,
        )
        with self.assertRaises(StoreRMAError):
            inspect_return(
                return_id=r.pk, received_quantity=3, restock_quantity=3,
                inspection_note="Greater than purchased return", actor=self.staff,
            )
        with self.assertRaises(StoreRMAError):
            inspect_return(
                return_id=r.pk, received_quantity=2, restock_quantity=3,
                inspection_note="No more stock than returned", actor=self.staff,
            )
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 5)

    def test_received_item_restock_only_usable_and_only_once(self):
        r, receipt = self.inspect(quantity=2, restock=1)
        self.assertEqual(receipt.variant_id, self.variant.pk)
        self.assertEqual(receipt.received_quantity, 2)
        self.assertEqual(receipt.restock_quantity, 1)
        self.assertEqual(StoreReturnInspection.objects.count(), 1)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 6)
        self.assertEqual(self.variant.reserved_quantity, 0)
        movements = InventoryMovement.objects.filter(
            order=self.order, variant=self.variant, movement_type="return",
        )
        self.assertEqual(movements.count(), 1)
        self.assertEqual(movements.get().quantity, 1)
        same = inspect_return(
            return_id=r.pk, received_quantity=2, restock_quantity=1,
            inspection_note="Restock usable pieces, scrap the broken ones",
            actor=self.staff,
        )
        self.assertEqual(same.pk, receipt.pk)
        with self.assertRaises(StoreRMAError):
            inspect_return(
                return_id=r.pk, received_quantity=2, restock_quantity=2,
                inspection_note="Restock usable pieces, scrap the broken ones",
                actor=self.staff,
            )
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 6)
        with self.assertRaises(ValidationError):
            receipt.delete()

    def test_defective_return_does_not_restock_and_remaining_unit_can_return(self):
        r = self.approve(quantity=2)
        inspected = inspect_return(
            return_id=r.pk, received_quantity=1, restock_quantity=0,
            inspection_note="One physically cracked, no usable stock",
            actor=self.staff,
        )
        self.assertIsNone(inspected.inventory_movement_id)
        next_rma = self.submit(quantity=2)
        self.assertEqual(next_rma.quantity, 2)
        self.assertEqual(InventoryMovement.objects.filter(movement_type="return").count(), 0)

    def test_return_for_not_stock_tracked_variant_cannot_increase_stock(self):
        self.variant.track_inventory = False
        self.variant.save(update_fields=["track_inventory"])
        r = self.approve(quantity=1)
        with self.assertRaises(StoreRMAError):
            inspect_return(
                return_id=r.pk, received_quantity=1, restock_quantity=1,
                inspection_note="Untracked stock cannot be restored numerically", actor=self.staff,
            )
        okay = inspect_return(
            return_id=r.pk, received_quantity=1, restock_quantity=0,
            inspection_note="Received, but stock is not numerically tracked", actor=self.staff,
        )
        self.assertIsNone(okay.inventory_movement_id)

    def test_refund_requires_physical_inspection_and_real_paid_source(self):
        r = self.approve(quantity=1)
        with self.assertRaises(StoreRMAError):
            self.refund(r)
        inspect_return(
            return_id=r.pk, received_quantity=1, restock_quantity=0,
            inspection_note="Damaged original product; refund approved", actor=self.staff,
        )
        pending = StorePayment.objects.create(
            order=self.order, amount=50000, method="bank_transfer", status="awaiting_review",
        )
        with self.assertRaises(StoreRMAError):
            self.refund(r, payment=pending)
        with self.assertRaises(StoreRMAError):
            self.refund(r, amount=100001)

    def test_refund_request_does_not_change_original_paid_receipt_or_order(self):
        r, _ = self.inspect(quantity=1, restock=0)
        request = self.refund(r, amount=50000)
        self.assertEqual(request.status, "requested")
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 0)
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        self.assertEqual(self.order.status, "delivered")
        self.assertEqual(self.payment.status, "paid")
        self.assertEqual(self.payment.amount, 320000)

    def test_complete_external_refund_requires_proof_and_is_idempotent(self):
        r, _ = self.inspect(quantity=1, restock=0)
        refund = self.refund(r, amount=75000)
        self.approve_refund(refund)
        with self.assertRaises(StoreRMAError):
            confirm_store_return_refund(
                refund_id=refund.pk, payout_reference="BANK-RMA-001",
                actor=self.checker, confirmed_external_payout=False,
            )
        finished = confirm_store_return_refund(
            refund_id=refund.pk, payout_reference="BANK-RMA-001",
            actor=self.checker, confirmed_external_payout=True,
        )
        r.refresh_from_db()
        self.assertEqual(r.status, "refunded")
        ledger = StoreReturnRefundLedger.objects.get(refund=finished)
        self.assertEqual(ledger.order_id, self.order.pk)
        self.assertEqual(ledger.payment_id, self.payment.pk)
        self.assertEqual(ledger.amount, 75000)
        self.assertEqual(ledger.currency, "IRT")
        self.assertEqual(ledger.provider_ref, "BANK-RMA-001")
        repeat = confirm_store_return_refund(
            refund_id=refund.pk, payout_reference="BANK-RMA-001",
            actor=self.checker, confirmed_external_payout=True,
        )
        self.assertEqual(repeat.pk, finished.pk)
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 1)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 5)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "delivered")
        self.assertEqual(self.order.payment_status, "paid")

    def test_same_external_proof_cannot_refund_twice(self):
        a, _ = self.inspect(quantity=1, restock=0)
        first = self.refund(a, amount=80000)
        self.approve_refund(first)
        confirm_store_return_refund(
            refund_id=first.pk, payout_reference="BANK-SAME-001",
            actor=self.checker, confirmed_external_payout=True,
        )
        b = self.approve(quantity=1)
        inspect_return(
            return_id=b.pk, received_quantity=1, restock_quantity=0,
            inspection_note="Second verified item returned", actor=self.staff,
        )
        second = self.refund(b, amount=50000)
        self.approve_refund(second)
        with self.assertRaises(StoreRMAError):
            confirm_store_return_refund(
                refund_id=second.pk, payout_reference="BANK-SAME-001",
                actor=self.checker, confirmed_external_payout=True,
            )
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 1)

    def test_refund_amount_caps_by_line_paid_and_reserved(self):
        r, _ = self.inspect(quantity=2, restock=0)
        a = self.refund(r, amount=150000)
        with self.assertRaises(StoreRMAError):
            self.refund(r, amount=60000)
        with self.assertRaises(StoreRMAError):
            self.refund(r, amount=50000, payment=StorePayment.objects.create(
                order=self.order, amount=60000, status="awaiting_review",
            ))
        cancel_store_return_refund(
            refund_id=a.pk, cancellation_reason="Mistake in original refund amount",
            actor=self.staff,
        )
        b = self.refund(r, amount=200000)
        self.assertEqual(b.amount, 200000)
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 0)

    def test_request_key_idempotent_and_scope_mismatch_blocked(self):
        r, _ = self.inspect(quantity=1, restock=0)
        key = uuid4()
        a = self.refund(r, amount=50000, key=key)
        b = self.refund(r, amount=50000, key=key)
        self.assertEqual(a.pk, b.pk)
        with self.assertRaises(StoreRMAError):
            self.refund(r, amount=50001, key=key)

    def test_customer_form_requires_real_order_item_and_quantity(self):
        self.client.force_login(self.buyer)
        url = reverse("store:return_request", args=[self.order.order_number])
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "quantity")
        missing_item = self.client.post(url, {
            "item": "", "quantity": 1, "reason": "defect", "description": "Cracked body",
        })
        self.assertEqual(missing_item.status_code, 200)
        self.assertEqual(ReturnRequest.objects.count(), 0)
        submitted = self.client.post(url, {
            "item": self.item.pk, "quantity": 2,
            "reason": "defect", "description": "Broken part",
        })
        self.assertEqual(submitted.status_code, 302)
        self.assertEqual(ReturnRequest.objects.get(order=self.order).quantity, 2)

    def test_admin_workflow_browser_review_inspection_refund(self):
        r = self.submit(quantity=1)
        self.client.force_login(self.staff)
        change = self.client.get(reverse("admin:store_returnrequest_change", args=[r.pk]))
        self.assertEqual(change.status_code, 200)
        self.assertContains(change, "چرخه بررسی")
        review_url = reverse("admin:store_returnrequest_workflow_review", args=[r.pk])
        result = self.client.post(review_url, {
            "decision": "approved", "response": "Return approved after technical review",
        })
        self.assertEqual(result.status_code, 302)
        inspect_url = reverse("admin:store_returnrequest_workflow_inspect", args=[r.pk])
        checked = self.client.post(inspect_url, {
            "received_quantity": 1, "restock_quantity": 1,
            "inspection_note": "One complete usable piece received",
            "approved": "on",
        })
        self.assertEqual(checked.status_code, 302)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 6)
        request_url = reverse("admin:store_returnrequest_workflow_request_refund", args=[r.pk])
        requested = self.client.post(request_url, {
            "request_key": str(uuid4()), "payment": self.payment.pk,
            "amount": 60000, "method": "bank_transfer",
            "reason": "Actual partial refund after inspection", "approved": "on",
        })
        self.assertEqual(requested.status_code, 302)
        refund = StoreReturnRefund.objects.get(return_request=r)
        confirm_url = reverse("admin:store_returnrequest_workflow_decide_refund", args=[r.pk, refund.pk])
        self.client.force_login(self.checker)
        approval = self.client.post(confirm_url, {
            "action": "approve", "approval_note": "Independent RMA refund review and authorization",
        })
        self.assertEqual(approval.status_code, 302)
        denied = self.client.post(confirm_url, {
            "action": "complete", "payout_reference": "RMA-WEBBANK-01",
        })
        self.assertEqual(denied.status_code, 200)
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 0)
        confirmed = self.client.post(confirm_url, {
            "action": "complete", "payout_reference": "RMA-WEBBANK-01",
            "confirmed": "on",
        })
        self.assertEqual(confirmed.status_code, 302)
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 1)

    def test_customer_cannot_access_operator_rma_workflow(self):
        r = self.submit()
        self.client.force_login(self.buyer)
        review = self.client.get(reverse("admin:store_returnrequest_workflow_review", args=[r.pk]))
        self.assertNotEqual(review.status_code, 200)

    def test_full_refund_proof_requires_every_item_and_total_cash(self):
        r, _ = self.inspect(quantity=3, restock=0)
        refund = self.refund(r, amount=300000)
        self.approve_refund(refund)
        confirm_store_return_refund(
            refund_id=refund.pk, payout_reference="RMA-LINE-300K",
            actor=self.checker, confirmed_external_payout=True,
        )
        self.assertFalse(full_store_order_refund_proven(self.order))
        # Shipping was paid and was not part of the returned product line.
        self.assertEqual(StoreReturnRefundLedger.objects.aggregate(
            total=__import__("django").db.models.Sum("amount"))["total"], 300000)

    def test_return_stock_cannot_be_inflated_without_prior_sale_movement(self):
        r = self.approve(quantity=1)
        InventoryMovement.objects.filter(
            order=self.order, variant=self.variant, movement_type="sale"
        ).delete()
        with self.assertRaises(StoreRMAError):
            inspect_return(
                return_id=r.pk, received_quantity=1, restock_quantity=1,
                inspection_note="No verified sale stock movement available",
                actor=self.staff,
            )
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 5)

    def test_shipping_status_and_refunded_order_cannot_be_forged(self):
        other_order = StoreOrder.objects.create(
            user=self.buyer, status="awaiting_payment",
            payment_status="pending", shipping_title="Pickup",
            full_name="Pending buyer", phone="09120000010",
            province="اصفهان", city="اصفهان",
            address="Test address", postal_code="1234567890",
            total_amount=30000,
        )
        with self.assertRaises(ValidationError):
            transition_order(other_order, "delivered", actor=self.staff)
        with self.assertRaises(ValidationError):
            transition_order(self.order, "refunded", actor=self.staff)

    def test_store_manual_admin_cannot_forge_gateway_and_reject_paid_receipt(self):
        from django.contrib import admin
        from store.admin import StorePaymentAdmin
        payment_admin = StorePaymentAdmin(StorePayment, admin.site)
        gateway = StorePayment.objects.create(
            order=self.order, amount=12000, method="gateway", status="awaiting_review",
        )
        class Request:
            user = self.staff
        payment_admin.approve_payments(
            Request(), StorePayment.objects.filter(pk=gateway.pk),
        )
        gateway.refresh_from_db()
        self.assertEqual(gateway.status, "awaiting_review")
        payment_admin.reject_payments(
            Request(), StorePayment.objects.filter(pk=self.payment.pk),
        )
        self.payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.payment.status, "paid")
        self.assertEqual(self.order.payment_status, "paid")

    def test_return_admin_status_is_read_only_and_no_list_inline_change(self):
        from django.contrib import admin
        from store.admin import ReturnRequestAdmin
        rma_admin = ReturnRequestAdmin(ReturnRequest, admin.site)
        self.assertNotIn("status", rma_admin.list_editable)
        self.assertIn("status", rma_admin.readonly_fields)
        self.assertFalse(rma_admin.has_add_permission(None))

    def test_finance_reconciliation_counts_distinct_return_inventory_and_debit(self):
        from store.finance_reconciliation import collect_finance_reconciliation
        self.payment.receipt_image = "store/payments/receipts/rma-test.jpg"
        self.payment.save(update_fields=["receipt_image"])
        rma, inspected = self.inspect(quantity=2, restock=1)
        request = self.refund(rma, amount=120000)
        self.approve_refund(request)
        confirm_store_return_refund(
            refund_id=request.pk, payout_reference="RMA-AUDIT-001",
            actor=self.checker, confirmed_external_payout=True,
        )
        report = collect_finance_reconciliation(check_storage=False)
        self.assertTrue(report["ok"], report["failures"])
        self.assertEqual(report["metrics"]["store_return_inspection_count"], 1)
        self.assertEqual(report["metrics"]["store_return_restock_sum"], 1)
        self.assertEqual(report["metrics"]["store_refund_ledger_count"], 1)
        self.assertEqual(report["metrics"]["store_refund_debit_sum"], 120000)

    def test_reconciliation_detects_corrupt_refund_and_stock_movement(self):
        from store.finance_reconciliation import collect_finance_reconciliation
        self.payment.receipt_image = "store/payments/receipts/rma-test.jpg"
        self.payment.save(update_fields=["receipt_image"])
        rma, receipt = self.inspect(quantity=1, restock=1)
        payout = self.refund(rma, amount=50000)
        self.approve_refund(payout)
        confirm_store_return_refund(
            refund_id=payout.pk, payout_reference="RMA-CORRUPT-TEST",
            actor=self.checker, confirmed_external_payout=True,
        )
        StoreReturnRefundLedger.objects.filter(refund=payout).update(amount=60000)
        InventoryMovement.objects.filter(pk=receipt.inventory_movement_id).update(quantity=2)
        report = collect_finance_reconciliation(check_storage=False)
        self.assertFalse(report["ok"])
        self.assertEqual(report["failures"].get("store_rma_refund_ledger_invalid"), 1)
        self.assertEqual(report["failures"].get("store_rma_restock_movement_mismatch"), 1)

    def test_store_requester_cannot_approve_or_confirm_own_refund(self):
        rma, inspection = self.inspect(quantity=1, restock=0)
        refund = self.refund(rma, amount=70000)
        with self.assertRaises(StoreRMAError):
            approve_store_return_refund(
                refund_id=refund.pk, approval_note="Same operator approval attempt",
                actor=self.staff,
            )
        with self.assertRaises(StoreRMAError):
            confirm_store_return_refund(
                refund_id=refund.pk, payout_reference="NO-REVIEW-1234",
                actor=self.checker, confirmed_external_payout=True,
            )
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 0)
        approved = self.approve_refund(refund)
        self.assertEqual(approved.status, "approved")
        self.assertEqual(approved.approved_by_id, self.checker.pk)
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 0)
        with self.assertRaises(StoreRMAError):
            confirm_store_return_refund(
                refund_id=refund.pk, payout_reference="SELF-RECEIPT-1234",
                actor=self.staff, confirmed_external_payout=True,
            )
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 0)
        confirmed = confirm_store_return_refund(
            refund_id=refund.pk, payout_reference="REVIEWER-RECEIPT-1234",
            actor=self.checker, confirmed_external_payout=True,
        )
        self.assertEqual(confirmed.completed_by_id, self.checker.pk)
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 1)
        self.assertEqual(self.payment.status, "paid")

    def test_store_approved_hold_cannot_double_spend_or_mutate_endorsement(self):
        rma, inspected = self.inspect(quantity=1, restock=0)
        refund = self.refund(rma, amount=70000)
        self.approve_refund(refund)
        with self.assertRaises(StoreRMAError):
            self.refund(rma, amount=30001)
        with self.assertRaises(StoreRMAError):
            approve_store_return_refund(
                refund_id=refund.pk, approval_note="Conflicting independent signoff",
                actor=self.checker,
            )
        refund.refresh_from_db()
        refund.approval_note = "Overwritten"
        with self.assertRaises(ValidationError):
            refund.save()
        cancel_store_return_refund(
            refund_id=refund.pk,
            cancellation_reason="Unpaid approval was cancelled after finance review",
            actor=self.checker,
        )
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 0)
        new = self.refund(rma, amount=100000)
        self.assertEqual(new.status, "requested")

    def test_store_reviewer_permission_required_and_direct_status_jump_blocked(self):
        rma, inspected = self.inspect(quantity=1, restock=0)
        refund = self.refund(rma, amount=40000)
        with self.assertRaises(PermissionDenied):
            approve_store_return_refund(
                refund_id=refund.pk, approval_note="Customer self-approved maliciously",
                actor=self.buyer,
            )
        refund.status = "completed"
        with self.assertRaises(ValidationError):
            refund.save()
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 0)

    def test_store_reconciliation_detects_fake_independent_approval(self):
        from store.finance_reconciliation import collect_finance_reconciliation
        self.payment.receipt_image = "store/payments/receipts/rma-test.jpg"
        self.payment.save(update_fields=["receipt_image"])
        rma, inspected = self.inspect(quantity=1, restock=0)
        refund = self.refund(rma, amount=50000)
        self.approve_refund(refund)
        StoreReturnRefund.objects.filter(pk=refund.pk).update(approved_by=self.staff)
        audit = collect_finance_reconciliation(check_storage=False)
        self.assertEqual(audit["failures"].get("store_rma_independent_approval_missing"), 1)

    def test_approved_store_refund_cannot_be_cancelled_by_original_requester(self):
        rma, inspection = self.inspect(quantity=1, restock=0)
        refund = self.refund(rma, amount=50000)
        self.approve_refund(refund)
        with self.assertRaises(StoreRMAError):
            cancel_store_return_refund(
                refund_id=refund.pk,
                cancellation_reason="Requester tries to undo second-person approval",
                actor=self.staff,
            )
        self.assertEqual(StoreReturnRefund.objects.get(pk=refund.pk).status, "approved")
        cancel_store_return_refund(
            refund_id=refund.pk,
            cancellation_reason="Independent reviewer cancelled before actual payout",
            actor=self.checker,
        )
        self.assertEqual(StoreReturnRefund.objects.get(pk=refund.pk).status, "cancelled")
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 0)

    def test_store_approval_only_staff_cannot_finalize_without_change_permission(self):
        from django.contrib.auth.models import Permission
        rma, inspection = self.inspect(quantity=1, restock=0)
        refund = self.refund(rma, amount=50000)
        reviewer = User.objects.create_user(
            username="store-rma-approval-only", password="test-password",
            is_staff=True, is_active=True,
        )
        reviewer.user_permissions.add(
            Permission.objects.get(content_type__app_label="store", codename="approve_storereturnrefund")
        )
        approval = approve_store_return_refund(
            refund_id=refund.pk, approval_note="Separate RMA finance endorsement",
            actor=reviewer,
        )
        self.assertEqual(approval.status, "approved")
        with self.assertRaises(PermissionDenied):
            confirm_store_return_refund(
                refund_id=refund.pk, payout_reference="RMA-NO-FINALIZE-PERM",
                actor=reviewer, confirmed_external_payout=True,
            )
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 0)

    def test_admin_limited_second_reviewer_can_sign_off_without_editing_rma(self):
        from django.contrib.auth.models import Permission

        rma, _ = self.inspect(quantity=1, restock=0)
        refund = self.refund(rma, amount=50000)
        reviewer = User.objects.create_user(
            username="rma-limited-admin-reviewer", password="test-password",
            is_staff=True, is_active=True,
        )
        reviewer.user_permissions.add(*Permission.objects.filter(
            content_type__app_label="store",
            codename__in=["view_returnrequest", "approve_storereturnrefund"],
        ))
        self.assertTrue(reviewer.has_perm("store.view_returnrequest"))
        self.assertTrue(reviewer.has_perm("store.approve_storereturnrefund"))
        self.assertFalse(reviewer.has_perm("store.change_returnrequest"))
        self.assertFalse(reviewer.has_perm("store.change_storereturnrefund"))
        self.client.force_login(reviewer)
        url = reverse(
            "admin:store_returnrequest_workflow_decide_refund",
            args=[rma.pk, refund.pk],
        )
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "تأیید مستقل بدون جابه‌جایی پول")
        self.assertNotContains(page, "لغو درخواست بدون پرداخت")
        blocked = self.client.post(url, {
            "action": "cancel",
            "cancellation_reason": "Finance reviewer cannot cancel alone",
        })
        self.assertEqual(blocked.status_code, 200)
        self.assertEqual(StoreReturnRefund.objects.get(pk=refund.pk).status, "requested")
        approved = self.client.post(url, {
            "action": "approve",
            "approval_note": "Independent limited RMA reviewer authorized amount",
        })
        self.assertEqual(approved.status_code, 302)
        self.assertEqual(StoreReturnRefund.objects.get(pk=refund.pk).status, "approved")
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 0)
        no_pay = self.client.get(url)
        self.assertEqual(no_pay.status_code, 200)
        self.assertNotContains(no_pay, 'name="action"')
        denied = self.client.post(url, {
            "action": "complete", "payout_reference": "NO-RMA-BANK-RECEIPT",
            "confirmed": "on",
        })
        self.assertEqual(denied.status_code, 200)
        self.assertEqual(StoreReturnRefundLedger.objects.count(), 0)
        forbidden = reverse("admin:store_returnrequest_workflow_review",
                            args=[rma.pk])
        self.assertNotEqual(self.client.get(forbidden).status_code, 200)
