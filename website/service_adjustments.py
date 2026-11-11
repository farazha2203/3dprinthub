"""Audited service-order credit notes and manual *confirmed* payouts.

This module does NOT transfer money, call an online refund API or alter
previously verified Payment records. All writes lock the Quote parent and
create separate immutable credit/debit records.
"""
from __future__ import annotations

from uuid import UUID, uuid4

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import (
    Order, Payment, PaymentLedgerEntry, Quote, ServiceCreditNote, ServiceRefund,
)


class ServiceFinanceError(RuntimeError):
    """A business invariant prevented a financial state transition."""


def _authorized(actor, permission: str) -> None:
    if not (actor and actor.is_authenticated and actor.is_active
            and actor.is_staff and actor.has_perm(permission)):
        raise PermissionDenied("این عملیات مالی به مجوز اختصاصی مسئول مالی نیاز دارد.")


def _locked_quote(quote_id: int) -> Quote:
    return Quote.objects.select_for_update().select_related("order").get(pk=quote_id)


def _frozen_approved_quote(quote: Quote) -> None:
    if quote.status != "accepted" or not quote.pricing_snapshot_at or quote.total_price <= 0:
        raise ServiceFinanceError("اصلاح مالی فقط پس از تأیید و تثبیت قیمت پیش‌فاکتور مجاز است.")
    if quote.order.status == "cancelled":
        raise ServiceFinanceError("برای سفارش لغوشده ابتدا پرونده حسابداری را تعیین تکلیف کنید.")


def issue_service_credit_note(
    *, quote_id: int, amount: int, reference: str, reason: str, actor,
) -> ServiceCreditNote:
    _authorized(actor, "website.add_servicecreditnote")
    amount = int(amount)
    reference, reason = (reference or "").strip(), (reason or "").strip()
    if amount <= 0 or not reference or not reason:
        raise ServiceFinanceError("مبلغ مثبت، شناسه یکتا و دلیل مکتوب اصلاحیه لازم است.")
    with transaction.atomic():
        quote = _locked_quote(quote_id)
        _frozen_approved_quote(quote)
        existing = ServiceCreditNote.objects.filter(reference=reference).first()
        if existing:
            if (existing.quote_id == quote_id and int(existing.amount) == amount
                    and existing.reason == reason):
                return existing
            raise ServiceFinanceError("این شماره اصلاحیه قبلاً برای سند دیگری استفاده شده است.")
        if quote.pending_amount:
            raise ServiceFinanceError(
                "ابتدا تمام رسیدهای در انتظار و تراکنش‌های نیمه‌تمام درگاه را بررسی/لغو کنید."
            )
        if amount > quote.effective_total_price:
            raise ServiceFinanceError("جمع اصلاحیه‌ها نمی‌تواند از مبلغ قطعی اصلی بیشتر شود.")
        # A credit note changes the contractual payable amount, not the cash ledger.
        note = ServiceCreditNote.objects.create(
            quote=quote, amount=amount, reference=reference,
            reason=reason, issued_by=actor,
        )
        return note


def _completed_refunds_for_payment(payment_id: int) -> int:
    return int(PaymentLedgerEntry.objects.filter(
        payment_id=payment_id, entry_type="refund", direction="debit", currency="IRT"
    ).aggregate(value=Sum("amount"))["value"] or 0)


def _requested_refunds(*, quote_id: int, payment_id: int | None = None) -> int:
    # Approval must not release an already reserved overpayment before actual payout.
    q = ServiceRefund.objects.filter(quote_id=quote_id, status__in=["requested", "approved"])
    if payment_id is not None:
        q = q.filter(original_payment_id=payment_id)
    return int(q.aggregate(value=Sum("amount"))["value"] or 0)


def request_service_refund(
    *, quote_id: int, payment_id: int, amount: int, method: str,
    reason: str, actor, request_key: UUID | str | None = None,
) -> ServiceRefund:
    _authorized(actor, "website.add_servicerefund")
    amount = int(amount)
    reason = (reason or "").strip()
    key = UUID(str(request_key)) if request_key else uuid4()
    if amount <= 0 or len(reason) < 8:
        raise ServiceFinanceError("مبلغ مثبت و دلیل توضیحی استرداد (حداقل ۸ نویسه) لازم است.")
    if method not in dict(ServiceRefund.METHOD_CHOICES):
        raise ServiceFinanceError("روش بازپرداخت معتبر نیست.")
    with transaction.atomic():
        quote = _locked_quote(quote_id)
        _frozen_approved_quote(quote)
        existing = ServiceRefund.objects.filter(request_key=key).first()
        if existing:
            if (existing.quote_id == quote.pk and existing.original_payment_id == payment_id
                    and existing.amount == amount and existing.method == method
                    and existing.reason == reason):
                return existing
            raise ServiceFinanceError("کلید ثبت مجدد برای یک درخواست متفاوت به‌کار رفته است.")
        payment = Payment.objects.select_for_update().filter(pk=payment_id, quote=quote).first()
        if not payment or payment.status != "paid":
            raise ServiceFinanceError("دریافت اولیه باید متعلق به این سفارش و قبلاً تأیید شده باشد.")
        if quote.pending_amount:
            raise ServiceFinanceError("ابتدا رسیدهای معلق را تعیین تکلیف کنید.")
        global_available = quote.refundable_excess - _requested_refunds(quote_id=quote.pk)
        payment_available = (
            int(payment.amount) - _completed_refunds_for_payment(payment.pk)
            - _requested_refunds(quote_id=quote.pk, payment_id=payment.pk)
        )
        if amount > min(global_available, payment_available):
            raise ServiceFinanceError(
                "مبلغ استرداد از بستانکاری واقعی مشتری یا سهم بازپرداخت‌نشده این دریافت بیشتر است."
            )
        return ServiceRefund.objects.create(
            quote=quote, original_payment=payment, amount=amount, method=method,
            reason=reason, requested_by=actor, request_key=key, status="requested",
        )


def approve_service_refund(*, refund_id: int, approval_note: str, actor) -> ServiceRefund:
    """Separate reviewer attests the commercial decision; does NOT move money."""
    _authorized(actor, "website.approve_servicerefund")
    note = (approval_note or "").strip()
    if len(note) < 8:
        raise ServiceFinanceError("مسئول مالی دوم باید دلیل تأیید را مستند کند.")
    quote_id = ServiceRefund.objects.only("quote_id").get(pk=refund_id).quote_id
    with transaction.atomic():
        quote = _locked_quote(quote_id)
        _frozen_approved_quote(quote)
        refund = ServiceRefund.objects.select_for_update().select_related(
            "original_payment", "requested_by"
        ).get(pk=refund_id, quote=quote)
        if actor.pk == refund.requested_by_id:
            raise ServiceFinanceError("تأیید مالی توسط همان درخواست‌کننده ممنوع است.")
        if refund.status == "approved":
            if refund.approved_by_id == actor.pk and refund.approval_note == note:
                return refund
            raise ServiceFinanceError("این درخواست قبلاً توسط مسئول دیگری تأیید شده است.")
        if refund.status != "requested":
            raise ServiceFinanceError("فقط درخواست در انتظار تأیید، قابل بررسی است.")
        if refund.original_payment.status != "paid" or quote.refundable_excess < refund.amount:
            raise ServiceFinanceError("مبلغ/دریافت معتبر برای تأیید مستقل کافی نیست.")
        refund.status = "approved"
        refund.approved_by = actor
        refund.approved_at = timezone.now()
        refund.approval_note = note
        refund.save(update_fields=["status", "approved_by", "approved_at", "approval_note"])
        return refund


def confirm_service_refund(
    *, refund_id: int, payout_reference: str, actor, confirmed_external_payout: bool,
) -> ServiceRefund:
    _authorized(actor, "website.change_servicerefund")
    reference = (payout_reference or "").strip()
    if not confirmed_external_payout:
        raise ServiceFinanceError("بدون تأیید اجرای واقعی بازپرداخت هیچ سند بدهکار ثبت نمی‌شود.")
    if len(reference) < 4:
        raise ServiceFinanceError("شماره پیگیری بانک یا رسید مستند تحویل وجه لازم است.")
    # Identify the parent before starting locks; all financial writers lock Quote first.
    quote_id = ServiceRefund.objects.only("quote_id").get(pk=refund_id).quote_id
    with transaction.atomic():
        quote = _locked_quote(quote_id)
        _frozen_approved_quote(quote)
        refund = ServiceRefund.objects.select_for_update().select_related(
            "original_payment", "requested_by", "approved_by",
        ).get(pk=refund_id, quote=quote)
        if actor.pk == refund.requested_by_id:
            raise ServiceFinanceError("ثبت نهایی رسید توسط درخواست‌کننده ممنوع است.")
        if refund.status == "completed":
            if refund.payout_reference == reference and refund.ledger_entry_id:
                return refund
            raise ServiceFinanceError("این استرداد قبلاً با شناسه دیگری بسته شده است.")
        if refund.status != "approved" or not refund.approved_by_id or not refund.approved_at:
            raise ServiceFinanceError("ابتدا تأیید مستقل مسئول مالی دوم باید ثبت شود.")
        if ServiceRefund.objects.filter(payout_reference=reference).exclude(pk=refund.pk).exists():
            raise ServiceFinanceError("این شماره بازپرداخت قبلاً ثبت شده است.")
        if quote.refundable_excess < refund.amount:
            raise ServiceFinanceError("بستانکاری قابل بازپرداخت پس از آخرین تغییر مالی کافی نیست.")
        already = _completed_refunds_for_payment(refund.original_payment_id)
        if refund.amount > refund.original_payment.amount - already:
            raise ServiceFinanceError("مبلغ استرداد تجمعی از دریافت اصلی بیشتر خواهد شد.")
        event_key = f"service-refund:{refund.pk}"
        ledger, created = PaymentLedgerEntry.objects.get_or_create(
            event_key=event_key,
            defaults={
                "quote": quote, "payment": refund.original_payment,
                "entry_type": "refund", "direction": "debit", "amount": refund.amount,
                "currency": "IRT", "provider_ref": reference,
                "description": f"استرداد مستند / {refund.get_method_display()}",
                "metadata": {
                    "refund_id": refund.pk, "confirmed_by_user_id": actor.pk,
                    "requested_by_user_id": refund.requested_by_id,
                    "approved_by_user_id": refund.approved_by_id,
                    "approved_at": refund.approved_at.isoformat(),
                    "method": refund.method, "external_payout_confirmed": True,
                },
            },
        )
        if not created and (
            ledger.quote_id != quote.pk or ledger.payment_id != refund.original_payment_id
            or ledger.entry_type != "refund" or ledger.direction != "debit"
            or ledger.amount != refund.amount or ledger.provider_ref != reference
        ):
            raise ServiceFinanceError("کلید دفتر مالی استرداد با سند دیگری تداخل دارد.")
        refund.payout_reference = reference
        refund.completed_by = actor
        refund.completed_at = timezone.now()
        refund.status = "completed"
        refund.ledger_entry = ledger
        refund.save(update_fields=[
            "payout_reference", "completed_by", "completed_at", "status", "ledger_entry",
        ])
        return refund


def cancel_service_refund(*, refund_id: int, reason: str, actor) -> ServiceRefund:
    _authorized(actor, "website.change_servicerefund")
    reason = (reason or "").strip()
    if len(reason) < 8:
        raise ServiceFinanceError("دلیل لغو درخواست باید حداقل ۸ نویسه داشته باشد.")
    quote_id = ServiceRefund.objects.only("quote_id").get(pk=refund_id).quote_id
    with transaction.atomic():
        _locked_quote(quote_id)
        refund = ServiceRefund.objects.select_for_update().get(pk=refund_id)
        if refund.status not in {"requested", "approved"}:
            raise ServiceFinanceError("فقط درخواست پرداخت‌نشده قابل لغو است.")
        if refund.status == "approved" and (
            actor.pk == refund.requested_by_id or not actor.has_perm("website.approve_servicerefund")
        ):
            raise ServiceFinanceError("لغو درخواست تأییدشده نیز نیازمند مسئول مالی مستقل است.")
        refund.status = "cancelled"
        refund.cancellation_reason = reason
        refund.save(update_fields=["status", "cancellation_reason"])
        return refund
