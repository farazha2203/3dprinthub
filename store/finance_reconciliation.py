from __future__ import annotations

from collections import Counter
from typing import Any

from django.db.models import Sum

from .models import CostEntry, ProductionJob, StoreOrder, StorePayment
from .production_services import finance_summary


STORE_PAYMENT_REVIEW_EVENT = "پرداخت سفارش تأیید شد"
ACTIVE_CUSTOM_ORDER_STATUSES = {"accepted", "paid", "in_progress", "done"}


def _receipt_state(field) -> tuple[bool, bool | None]:
    if not field:
        return False, False
    name = str(getattr(field, "name", "") or "").strip()
    if not name:
        return False, False
    try:
        return True, bool(field.storage.exists(name))
    except Exception:
        return True, None


def collect_finance_reconciliation(*, check_storage: bool = True) -> dict[str, Any]:
    from website.models import Order as WebsiteOrder
    from website.models import Payment, PaymentLedgerEntry, Quote

    failures: Counter[str] = Counter()
    warnings: Counter[str] = Counter()
    metrics: dict[str, int] = {}
    store_payments = StorePayment.objects.select_related("order").all()
    metrics["store_payments_total"] = store_payments.count()
    metrics["store_paid_count"] = store_payments.filter(status="paid").count()
    metrics["store_paid_sum"] = int(
        store_payments.filter(status="paid").aggregate(value=Sum("amount"))["value"] or 0
    )
    metrics["store_awaiting_review"] = store_payments.filter(status="awaiting_review").count()

    for payment in store_payments:
        if int(payment.amount or 0) <= 0:
            failures["store_payment_nonpositive_amount"] += 1
        manual_reviewed = payment.method == "bank_transfer" and payment.status in {
            "awaiting_review",
            "paid",
        }
        if manual_reviewed:
            present, exists = _receipt_state(payment.receipt_image)
            if not present:
                failures["store_manual_receipt_missing"] += 1
            elif check_storage and exists is False:
                failures["store_manual_receipt_file_missing"] += 1
            elif check_storage and exists is None:
                warnings["store_manual_receipt_storage_unverified"] += 1
        if payment.status == "paid" and payment.order.payment_status != "paid":
            failures["store_paid_payment_order_not_paid"] += 1
        if payment.method == "bank_transfer" and payment.status == "paid":
            event = payment.order.events.filter(title=STORE_PAYMENT_REVIEW_EVENT).order_by("-id").first()
            if event is None:
                failures["store_manual_paid_review_event_missing"] += 1
            elif not event.created_by_id:
                failures["store_manual_paid_reviewer_missing"] += 1
    paid_store_orders = StoreOrder.objects.filter(payment_status="paid").prefetch_related("payments")
    metrics["store_paid_orders"] = paid_store_orders.count()
    metrics["store_paid_order_total"] = int(
        paid_store_orders.aggregate(value=Sum("total_amount"))["value"] or 0
    )
    for order in paid_store_orders:
        paid_sum = sum(int(p.amount or 0) for p in order.payments.all() if p.status == "paid")
        if paid_sum != int(order.total_amount or 0):
            failures["store_paid_order_amount_mismatch"] += 1
        try:
            job = order.production_job
        except ProductionJob.DoesNotExist:
            job = None
        if job is None:
            failures["store_paid_order_job_missing"] += 1

    jobs = ProductionJob.objects.select_related("store_order", "custom_order").exclude(status="cancelled")
    metrics["production_jobs"] = jobs.count()
    metrics["store_jobs"] = jobs.filter(store_order__isnull=False).count()
    metrics["custom_jobs"] = jobs.filter(custom_order__isnull=False).count()
    metrics["job_revenue_snapshot_sum"] = int(
        jobs.aggregate(value=Sum("revenue_snapshot"))["value"] or 0
    )
    for job in jobs:
        if job.store_order_id:
            expected = max(
                0,
                int(job.store_order.total_amount or 0) - int(job.store_order.tax_amount or 0),
            )
            if int(job.revenue_snapshot or 0) != expected:
                warnings["store_job_revenue_snapshot_differs"] += 1
        elif job.custom_order_id:
            try:
                quote = job.custom_order.quote
            except Exception:
                quote = None
            expected = int(getattr(quote, "total_price", 0) or 0)
            if quote is not None and int(job.revenue_snapshot or 0) != expected:
                warnings["custom_job_revenue_snapshot_differs"] += 1

    website_payments = Payment.objects.select_related("quote", "quote__order").all()
    metrics["website_payments_total"] = website_payments.count()
    metrics["website_paid_count"] = website_payments.filter(status="paid").count()
    metrics["website_paid_sum"] = int(
        website_payments.filter(status="paid").aggregate(value=Sum("amount"))["value"] or 0
    )
    metrics["website_awaiting_review"] = website_payments.filter(
        status="awaiting_review"
    ).count()

    for payment in website_payments:
        if int(payment.amount or 0) <= 0:
            failures["website_payment_nonpositive_amount"] += 1
        manual_reviewed = payment.method == "bank_transfer" and payment.status in {
            "awaiting_review",
            "paid",
        }
        if manual_reviewed:
            present, exists = _receipt_state(payment.receipt_image)
            if not present:
                failures["website_manual_receipt_missing"] += 1
            elif check_storage and exists is False:
                failures["website_manual_receipt_file_missing"] += 1
            elif check_storage and exists is None:
                warnings["website_manual_receipt_storage_unverified"] += 1
        if payment.status != "paid":
            continue
        ledgers = list(
            payment.ledger_entries.filter(entry_type="payment", direction="credit").order_by("id")
        )
        if len(ledgers) != 1:
            failures["website_paid_payment_ledger_count"] += 1
            continue
        ledger = ledgers[0]
        if int(ledger.amount or 0) != int(payment.amount or 0):
            failures["website_paid_payment_ledger_amount"] += 1
        if ledger.quote_id != payment.quote_id:
            failures["website_paid_payment_ledger_quote"] += 1
        if str(ledger.currency or "") != "IRT":
            failures["website_paid_payment_ledger_currency"] += 1
        if payment.method == "bank_transfer":
            reviewer = (ledger.metadata or {}).get("reviewed_by_user_id")
            source = str((ledger.metadata or {}).get("review_source") or "")
            if not reviewer or source != "admin_manual":
                failures["website_manual_paid_reviewer_missing"] += 1

    ledger_entries = PaymentLedgerEntry.objects.select_related("payment", "quote").all()
    metrics["website_ledger_entries"] = ledger_entries.count()
    metrics["website_ledger_credit_sum"] = int(
        ledger_entries.filter(entry_type="payment", direction="credit").aggregate(
            value=Sum("amount")
        )["value"]
        or 0
    )
    for ledger in ledger_entries.filter(entry_type="payment"):
        if ledger.payment_id and ledger.quote_id != ledger.payment.quote_id:
            failures["website_ledger_cross_quote"] += 1

    for quote in Quote.objects.prefetch_related("payments").all():
        paid_sum = sum(int(p.amount or 0) for p in quote.payments.all() if p.status == "paid")
        if paid_sum > int(quote.total_price or 0):
            failures["website_quote_overpaid"] += 1

    active_custom = WebsiteOrder.objects.filter(status__in=ACTIVE_CUSTOM_ORDER_STATUSES)
    metrics["active_custom_orders"] = active_custom.count()
    metrics["active_custom_orders_no_job"] = active_custom.filter(
        production_job__isnull=True
    ).count()
    if metrics["active_custom_orders_no_job"]:
        failures["active_custom_order_job_missing"] += metrics["active_custom_orders_no_job"]

    metrics["general_expense_sum"] = int(
        CostEntry.objects.filter(job__isnull=True).aggregate(value=Sum("actual_cost"))["value"]
        or 0
    )
    summary = finance_summary()
    metrics["finance_revenue"] = int(summary["revenue"])
    metrics["finance_project_cost"] = int(summary["project_cost"])
    metrics["finance_general_expenses"] = int(summary["general_expenses"])
    metrics["finance_net_profit"] = int(summary["net_profit"])

    return {
        "ok": not failures,
        "metrics": metrics,
        "failures": dict(sorted(failures.items())),
        "warnings": dict(sorted(warnings.items())),
    }
