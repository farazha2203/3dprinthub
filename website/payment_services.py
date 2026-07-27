from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from .models import Payment, PaymentLedgerEntry, Quote, SiteSetting
from .payment_gateways import gateway_configuration_status, get_payment_gateway
from .payment_gateways.base import PaymentGatewayError, PaymentGatewayTemporaryError


class PaymentFlowError(RuntimeError):
    pass


def quote_payment_amounts(quote: Quote) -> dict[str, int]:
    if not quote or not quote.total_price:
        return {}
    paid = int(quote.paid_amount)
    pending = int(quote.pending_amount)
    available = int(quote.available_payment_amount)
    values: dict[str, int] = {}
    deposit_due = max(int(quote.deposit_amount) - paid - pending, 0)
    deposit_due = min(deposit_due, available)
    if deposit_due > 0:
        values["deposit"] = deposit_due
    if available > 0:
        kind = "balance" if (paid or pending) else "full"
        values[kind] = available
    return values


def _client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",", 1)[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def payment_gateway_status(site_setting: SiteSetting | None = None) -> tuple[bool, str]:
    return gateway_configuration_status(site_setting)


def _payment_description(payment: Payment) -> str:
    prefix = str(getattr(settings, "PAYMENT_GATEWAY_DESCRIPTION_PREFIX", "3DPrintHub") or "3DPrintHub")
    return f"{prefix} | سفارش {payment.quote.order_id} | {payment.get_payment_kind_display()}"[:255]


def _expire_stale_gateway_attempts(quote: Quote) -> None:
    ttl_minutes = max(int(getattr(settings, "PAYMENT_GATEWAY_PENDING_TTL_MINUTES", 30) or 30), 5)
    threshold = timezone.now() - timedelta(minutes=ttl_minutes)
    stale = quote.payments.filter(
        method="gateway",
        status__in=["pending", "verifying"],
        created_at__lt=threshold,
    )
    stale.update(
        status="cancelled",
        failed_at=timezone.now(),
        provider_message="مهلت تلاش پرداخت قبلی پایان یافت.",
    )


def start_quote_gateway_payment(*, quote: Quote, payment_kind: str, request, site_setting: SiteSetting | None = None) -> tuple[Payment, str, bool]:
    ready, reason = payment_gateway_status(site_setting)
    if not ready:
        raise PaymentFlowError(reason)

    with transaction.atomic():
        locked_quote = Quote.objects.select_for_update().select_related("order", "order__customer").get(pk=quote.pk)
        if locked_quote.status != "accepted" or not locked_quote.total_price:
            raise PaymentFlowError("این پیش‌فاکتور در حال حاضر قابل پرداخت نیست.")
        _expire_stale_gateway_attempts(locked_quote)
        amounts = quote_payment_amounts(locked_quote)
        amount = int(amounts.get(payment_kind, 0) or 0)
        if amount <= 0:
            raise PaymentFlowError("مبلغ قابل پرداخت برای این گزینه وجود ندارد.")
        minimum = int(getattr(site_setting, "online_payment_minimum_toman", 0) or 0)
        if minimum and amount < minimum:
            raise PaymentFlowError(f"حداقل مبلغ پرداخت آنلاین {minimum:,} تومان است.")

        duplicate = locked_quote.payments.filter(
            method="gateway",
            payment_kind=payment_kind,
            amount=amount,
            status__in=["pending", "verifying"],
        ).order_by("-created_at").first()
        if duplicate and duplicate.checkout_url and duplicate.authority:
            return duplicate, duplicate.checkout_url, True

        payment = Payment.objects.create(
            quote=locked_quote,
            amount=amount,
            payment_kind=payment_kind,
            method="gateway",
            status="pending",
            provider=str(getattr(site_setting, "online_payment_provider", "zarinpal") or "zarinpal"),
            client_ip=_client_ip(request),
            user_agent=str(request.META.get("HTTP_USER_AGENT", ""))[:500],
        )

    gateway = get_payment_gateway(site_setting)
    callback_url = request.build_absolute_uri(
        reverse("website:quote_gateway_callback", kwargs={"callback_token": payment.callback_token})
    )
    request_payload = {
        "amount_toman": payment.amount,
        "gateway_amount": gateway.amount_for_provider(payment.amount),
        "currency": gateway.currency,
        "callback_url": callback_url,
        "description": _payment_description(payment),
    }
    try:
        result = gateway.create_payment(
            amount_toman=payment.amount,
            callback_url=callback_url,
            description=request_payload["description"],
            mobile=payment.quote.order.phone,
            email=getattr(payment.quote.order.customer, "email", "") or "",
        )
    except PaymentGatewayError as exc:
        Payment.objects.filter(pk=payment.pk, status="pending").update(
            status="failed",
            failed_at=timezone.now(),
            provider_status_code=exc.code,
            provider_message=exc.message[:500],
            request_payload=request_payload,
            raw_response=exc.payload,
        )
        raise PaymentFlowError(exc.message) from exc

    updated = Payment.objects.filter(pk=payment.pk, status="pending").update(
        authority=result.authority,
        checkout_url=result.checkout_url,
        gateway_amount=request_payload["gateway_amount"],
        gateway_currency=gateway.currency,
        provider_status_code=result.status_code,
        provider_message=result.message[:500],
        request_payload=request_payload,
        raw_response=result.raw_response,
        initiated_at=timezone.now(),
    )
    if not updated:
        raise PaymentFlowError("وضعیت پرداخت در زمان اتصال به درگاه تغییر کرد. دوباره تلاش کنید.")
    payment.refresh_from_db()
    return payment, result.checkout_url, False


def _create_payment_ledger(payment: Payment, *, metadata: dict[str, Any] | None = None) -> PaymentLedgerEntry:
    ref = payment.ref_id or payment.authority or str(payment.idempotency_key)
    event_key = f"payment:{payment.pk}:{ref}"
    entry, _ = PaymentLedgerEntry.objects.get_or_create(
        event_key=event_key,
        defaults={
            "quote": payment.quote,
            "payment": payment,
            "entry_type": "payment",
            "direction": "credit",
            "amount": payment.amount,
            "currency": "IRT",
            "provider_ref": ref,
            "description": f"{payment.get_payment_kind_display()} از {payment.provider or payment.get_method_display()}",
            "metadata": metadata or {},
        },
    )
    return entry


def _notify_payment_success(payment: Payment) -> None:
    customer = payment.quote.order.customer
    email = getattr(customer, "email", "") if customer else ""
    if not email:
        return
    try:
        send_mail(
            subject=f"پرداخت سفارش {payment.quote.order_id} تأیید شد",
            message=f"پرداخت {payment.amount:,} تومان با کد پیگیری {payment.ref_id or '—'} با موفقیت تأیید شد.",
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[email],
            fail_silently=True,
        )
    except Exception:
        return


def mark_payment_paid(payment: Payment, ref_id: str = "", *, provider_status_code: int | None = None, provider_message: str = "", metadata: dict[str, Any] | None = None) -> Payment:
    with transaction.atomic():
        locked = Payment.objects.select_for_update().select_related("quote", "quote__order").get(pk=payment.pk)
        if locked.status == "paid":
            _create_payment_ledger(locked, metadata=metadata)
            return locked
        if locked.status in {"refunded"}:
            raise PaymentFlowError("پرداخت مستردشده را نمی‌توان دوباره تأیید کرد.")
        locked.status = "paid"
        if ref_id:
            locked.ref_id = str(ref_id)
        locked.provider_status_code = provider_status_code
        if provider_message:
            locked.provider_message = provider_message[:500]
        now = timezone.now()
        locked.paid_at = now
        locked.verified_at = now
        locked.save(update_fields=[
            "status", "ref_id", "provider_status_code", "provider_message",
            "paid_at", "verified_at", "updated_at",
        ])
        _create_payment_ledger(locked, metadata=metadata)
        quote = locked.quote
        order = quote.order
        if quote.paid_amount >= quote.total_price:
            order.status = "paid"
        elif order.status not in {"in_progress", "done"}:
            order.status = "accepted"
        order.save(update_fields=["status"])
        transaction.on_commit(lambda: _notify_payment_success(locked))
        return locked


def process_gateway_callback(*, callback_token, callback_payload: dict[str, Any], site_setting: SiteSetting | None = None) -> tuple[Payment, str]:
    status_value = str(callback_payload.get("Status") or callback_payload.get("status") or "").upper()
    authority_value = str(callback_payload.get("Authority") or callback_payload.get("authority") or "").strip()

    with transaction.atomic():
        payment = Payment.objects.select_for_update().select_related("quote", "quote__order").get(callback_token=callback_token)
        payment.callback_payload = callback_payload
        payment.callback_received_at = timezone.now()
        if payment.status == "paid":
            payment.save(update_fields=["callback_payload", "callback_received_at", "updated_at"])
            _create_payment_ledger(payment, metadata={"callback": callback_payload, "idempotent": True})
            return payment, "paid"
        if payment.method != "gateway":
            payment.status = "failed"
            payment.failed_at = timezone.now()
            payment.provider_message = "Callback برای پرداخت غیرآنلاین دریافت شد."
            payment.save(update_fields=["status", "failed_at", "provider_message", "callback_payload", "callback_received_at", "updated_at"])
            return payment, "failed"
        if status_value != "OK":
            payment.status = "cancelled"
            payment.failed_at = timezone.now()
            payment.provider_message = "پرداخت در صفحه درگاه تکمیل نشد یا توسط کاربر لغو شد."
            payment.save(update_fields=["status", "failed_at", "provider_message", "callback_payload", "callback_received_at", "updated_at"])
            return payment, "cancelled"
        if not payment.authority or authority_value != payment.authority:
            payment.status = "failed"
            payment.failed_at = timezone.now()
            payment.provider_message = "Authority بازگشتی با پرداخت ثبت‌شده مطابقت ندارد."
            payment.save(update_fields=["status", "failed_at", "provider_message", "callback_payload", "callback_received_at", "updated_at"])
            return payment, "failed"
        if payment.status == "verifying":
            previous_update = payment.updated_at
            payment.save(update_fields=["callback_payload", "callback_received_at", "updated_at"])
            lock_seconds = max(int(getattr(settings, "PAYMENT_GATEWAY_VERIFY_LOCK_SECONDS", 60) or 60), 15)
            if previous_update and previous_update >= timezone.now() - timedelta(seconds=lock_seconds):
                return payment, "verifying"
            payment.status = "pending"
        payment.status = "verifying"
        payment.retry_count += 1
        payment.save(update_fields=["status", "retry_count", "callback_payload", "callback_received_at", "updated_at"])

    try:
        gateway = get_payment_gateway(site_setting, require_enabled=False, provider_slug=payment.provider)
    except PaymentGatewayError as exc:
        Payment.objects.filter(pk=payment.pk, status="verifying").update(
            status="pending",
            provider_message=exc.message[:500],
        )
        payment.refresh_from_db()
        return payment, "retry"
    try:
        result = gateway.verify_payment(
            amount_toman=payment.amount,
            authority=payment.authority,
            gateway_amount=payment.gateway_amount,
            currency=payment.gateway_currency,
        )
    except PaymentGatewayTemporaryError as exc:
        Payment.objects.filter(pk=payment.pk, status="verifying").update(
            status="pending",
            provider_message=exc.message[:500],
            raw_response=exc.payload,
        )
        payment.refresh_from_db()
        return payment, "retry"
    except PaymentGatewayError as exc:
        Payment.objects.filter(pk=payment.pk, status="verifying").update(
            status="failed",
            failed_at=timezone.now(),
            provider_status_code=exc.code,
            provider_message=exc.message[:500],
            raw_response=exc.payload,
        )
        payment.refresh_from_db()
        return payment, "failed"

    with transaction.atomic():
        locked = Payment.objects.select_for_update().select_related("quote", "quote__order").get(pk=payment.pk)
        if locked.status == "paid":
            _create_payment_ledger(locked, metadata={"verify": result.raw_response, "idempotent": True})
            return locked, "paid"
        locked.raw_response = result.raw_response
        locked.provider_status_code = result.status_code
        locked.provider_message = result.message[:500]
        if not result.success:
            locked.status = "failed"
            locked.failed_at = timezone.now()
            locked.save(update_fields=["status", "failed_at", "raw_response", "provider_status_code", "provider_message", "updated_at"])
            return locked, "failed"
        locked.save(update_fields=["raw_response", "provider_status_code", "provider_message", "updated_at"])

    paid = mark_payment_paid(
        locked,
        ref_id=result.ref_id,
        provider_status_code=result.status_code,
        provider_message=result.message,
        metadata={
            "verify": result.raw_response,
            "already_verified": result.already_verified,
            "card_pan": result.card_pan,
            "fee": result.fee,
        },
    )
    return paid, "paid"
