"""StoreOrder ProductVariant return merchandise authorization (RMA).

There is only one stock authority: ProductVariant + InventoryMovement.
A customer request is not physical receipt, and a refund request is not money
sent. Only an inspection may restock a tracked variant, and only verified
external payout proof may create a refund debit.
"""
from __future__ import annotations

from uuid import UUID, uuid4

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import (
    InventoryMovement, ProductVariant, ReturnRequest, StoreOrder,
    StoreOrderItem, StorePayment, StoreReturnInspection,
    StoreReturnRefund, StoreReturnRefundLedger,
)
from .services import record_event


class StoreRMAError(RuntimeError):
    pass


def _staff(actor, permission):
    if not (actor and actor.is_authenticated and actor.is_active
            and actor.is_staff and actor.has_perm(permission)):
        raise PermissionDenied("این مرحله مرجوعی به مجوز مستقل کارشناس نیاز دارد.")


def _order(order_id):
    # All RMA and checkout/stock operations should lock StoreOrder before variant writes.
    return StoreOrder.objects.select_for_update().get(pk=order_id)


def _request(rma_id):
    return ReturnRequest.objects.select_for_update().select_related(
        "order", "item", "item__variant", "user"
    ).get(pk=rma_id)


def _historical_return_quantity(item_id, *, omit=None):
    qs = ReturnRequest.objects.filter(item_id=item_id).exclude(status="rejected")
    if omit is not None:
        qs = qs.exclude(pk=omit)
    used = 0
    for prior in qs.select_related("inspection"):
        # Once a partial physical receipt is final, unreceived units may have a new RMA.
        used += int(prior.inspection.received_quantity) if hasattr(prior, "inspection") else int(prior.quantity)
    return used


@transaction.atomic
def submit_return_request(*, order_id, item_id, quantity, reason, description, user, image=None):
    order = _order(order_id)
    if not user.is_authenticated or order.user_id != user.pk or not order.can_request_return:
        raise StoreRMAError("درخواست مرجوعی فقط توسط خریدار سفارش تحویل‌شده و تسویه‌شده ثبت می‌شود.")
    item = StoreOrderItem.objects.filter(pk=item_id, order=order).first()
    quantity = int(quantity)
    if not item or quantity < 1 or not reason or not (description or "").strip():
        raise StoreRMAError("ردیف اصلی سفارش، تعداد مثبت و دلیل مرجوعی الزامی هستند.")
    if quantity + _historical_return_quantity(item.pk) > item.quantity:
        raise StoreRMAError("مجموع تعدادهای مرجوعی فعال از تعداد فروخته‌شده این تنوع بیشتر است.")
    rma = ReturnRequest.objects.create(
        order=order, item=item, user=user, quantity=quantity,
        reason=reason, description=description.strip(), image=image,
        status="submitted",
    )
    record_event(order, "درخواست مرجوعی ثبت شد",
        f"مرجوعی شماره {rma.pk}: {quantity} عدد از ردیف {item.variant_code}، در انتظار بررسی.",
        actor=None)
    return rma


def decide_store_return(*, return_id, decision, response, actor):
    _staff(actor, "store.change_returnrequest")
    decision = (decision or "").strip()
    response = (response or "").strip()
    if decision not in {"reviewing", "approved", "rejected"} or len(response) < 8:
        raise StoreRMAError("تصمیم معتبر و توضیح کارشناسی حداقل هشت نویسه الزامی است.")
    order_id = ReturnRequest.objects.only("order_id").get(pk=return_id).order_id
    with transaction.atomic():
        order = _order(order_id)
        rma = _request(return_id)
        if rma.status not in {"submitted", "reviewing"}:
            raise StoreRMAError("مرجوعی تأیید، دریافت یا بسته‌شده قابل بازگشت به بررسی نیست.")
        if rma.status == decision and rma.admin_response == response:
            return rma
        rma.status, rma.admin_response = decision, response
        rma.save(update_fields=["status", "admin_response", "updated_at"])
        record_event(order, "بررسی مرجوعی",
            f"درخواست {rma.pk}: {rma.get_status_display()}؛ {response[:220]}",
            actor=actor, public=True)
        return rma


def inspect_return(*, return_id, received_quantity, restock_quantity, inspection_note, actor):
    _staff(actor, "store.add_storereturninspection")
    received_quantity, restock_quantity = int(received_quantity), int(restock_quantity)
    inspection_note = (inspection_note or "").strip()
    if not inspection_note:
        raise StoreRMAError("یافته‌های بازرسی باید مستند باشند.")
    order_id = ReturnRequest.objects.only("order_id").get(pk=return_id).order_id
    with transaction.atomic():
        order = _order(order_id)
        rma = _request(return_id)
        prior = StoreReturnInspection.objects.filter(return_request=rma).first()
        if prior:
            if (prior.received_quantity, prior.restock_quantity, prior.inspection_note) == (
                received_quantity, restock_quantity, inspection_note
            ):
                return prior
            raise StoreRMAError("بازرسی قبلاً قطعی ثبت شده و نمی‌توان موجودی را دوباره اضافه کرد.")
        if rma.status != "approved":
            raise StoreRMAError("تنها پس از تأیید درخواست می‌توان کالای فیزیکی را تحویل گرفت.")
        if order.status not in {"delivered", "refunded"} or order.payment_status not in {"paid", "refunded"}:
            raise StoreRMAError("کالای برگشتی باید متعلق به سفارش واقعی تحویل‌شده و تسویه‌شده باشد.")
        if not rma.item_id or rma.item.order_id != order.pk:
            raise StoreRMAError("ردیف کالا به سفارش معتبر متصل نیست.")
        if (received_quantity < 1 or received_quantity > rma.quantity
                or restock_quantity < 0 or restock_quantity > received_quantity):
            raise StoreRMAError("تعداد دریافتی یا تعداد سالم برای بازگشت به موجودی معتبر نیست.")
        variant = (ProductVariant.objects.select_for_update()
                   .filter(pk=rma.item.variant_id).first()) if rma.item.variant_id else None
        if restock_quantity and (not variant or not variant.track_inventory):
            raise StoreRMAError("بازگشت عددی فقط برای تنوع اصلی دارای کنترل موجودی مجاز است.")
        if restock_quantity:
            # Never add more sellable units than the number genuinely consumed at checkout.
            sale_delta = int(InventoryMovement.objects.filter(
                variant=variant, order=order, movement_type="sale"
            ).aggregate(total=Sum("quantity"))["total"] or 0)
            returned = int(InventoryMovement.objects.filter(
                variant=variant, order=order, movement_type="return"
            ).aggregate(total=Sum("quantity"))["total"] or 0)
            if restock_quantity > max(0, -sale_delta - returned):
                raise StoreRMAError("گردش فروش قطعی معتبر برای این تعداد وجود ندارد؛ موجودی نباید بی‌مدرک افزایش یابد.")
        movement = None
        if restock_quantity:
            variant.stock_quantity = int(variant.stock_quantity) + restock_quantity
            variant.save(update_fields=["stock_quantity"])
            movement = InventoryMovement.objects.create(
                variant=variant, order=order, movement_type="return",
                quantity=restock_quantity, stock_after=variant.stock_quantity,
                reserved_after=variant.reserved_quantity,
                note=f"رسید بازرسی مرجوعی {rma.pk}: {inspection_note[:190]}",
                created_by=actor,
            )
        inspection = StoreReturnInspection.objects.create(
            return_request=rma, variant=variant,
            received_quantity=received_quantity, restock_quantity=restock_quantity,
            inspection_note=inspection_note, inspected_by=actor, inventory_movement=movement,
        )
        rma.status = "received"
        rma.save(update_fields=["status", "updated_at"])
        record_event(order, "بازرسی کالای برگشتی",
            f"مرجوعی {rma.pk}: دریافت {received_quantity}، سالم و برگشت به انبار {restock_quantity}.",
            actor=actor)
        return inspection


def _outstanding_refunds(*, order_id, payment_id=None, rma_id=None):
    qs = StoreReturnRefund.objects.filter(
        return_request__order_id=order_id, status__in=["requested", "approved", "completed"]
    )
    if payment_id is not None:
        qs = qs.filter(payment_id=payment_id)
    if rma_id is not None:
        qs = qs.filter(return_request_id=rma_id)
    return int(qs.aggregate(total=Sum("amount"))["total"] or 0)


@transaction.atomic
def request_store_return_refund(
    *, return_id, payment_id, amount, method, reason, actor, request_key: UUID | str | None = None,
):
    _staff(actor, "store.add_storereturnrefund")
    amount = int(amount)
    reason = (reason or "").strip()
    key = UUID(str(request_key)) if request_key else uuid4()
    if amount < 1 or len(reason) < 8 or method not in dict(StoreReturnRefund.METHOD_CHOICES):
        raise StoreRMAError("روش، مبلغ مثبت و دلیل مستند بازپرداخت الزامی است.")
    order_id = ReturnRequest.objects.only("order_id").get(pk=return_id).order_id
    order = _order(order_id)
    rma = _request(return_id)
    existing = StoreReturnRefund.objects.filter(request_key=key).first()
    if existing:
        if (existing.return_request_id == return_id and existing.payment_id == payment_id
                and existing.amount == amount and existing.method == method and existing.reason == reason):
            return existing
        raise StoreRMAError("شناسه تکراری برای درخواست متفاوت استفاده شده است.")
    if rma.status not in {"received", "refunded"} or not hasattr(rma, "inspection"):
        raise StoreRMAError("درخواست استرداد پیش از دریافت و بازرسی واقعی کالا مجاز نیست.")
    if order.payment_status not in {"paid", "refunded"} or order.status == "cancelled":
        raise StoreRMAError("سفارش باید واقعاً پرداخت شده باشد.")
    payment = StorePayment.objects.select_for_update().filter(
        pk=payment_id, order=order, status="paid"
    ).first()
    if payment is None:
        raise StoreRMAError("بازپرداخت باید به یک دریافت قبلاً تأییدشده همان سفارش متصل باشد.")
    if not rma.item_id or rma.item.order_id != order.pk:
        raise StoreRMAError("هیچ ردیف اصلی قابل استناد برای این مرجوعی وجود ندارد.")
    line_cap = int(rma.item.unit_price) * int(rma.inspection.received_quantity)
    line_remaining = line_cap - _outstanding_refunds(order_id=order.pk, rma_id=rma.pk)
    gross = int(StorePayment.objects.filter(order=order, status="paid").aggregate(
        total=Sum("amount"))["total"] or 0)
    order_remaining = gross - _outstanding_refunds(order_id=order.pk)
    payment_remaining = int(payment.amount) - _outstanding_refunds(
        order_id=order.pk, payment_id=payment.pk
    )
    if amount > min(line_remaining, order_remaining, payment_remaining):
        raise StoreRMAError("استرداد از سهم کالای بازرسی‌شده یا وجه دریافتی بازپرداخت‌نشده بیشتر است.")
    return StoreReturnRefund.objects.create(
        return_request=rma, payment=payment, amount=amount,
        method=method, reason=reason, request_key=key,
        requested_by=actor, status="requested",
    )


def approve_store_return_refund(*, refund_id, approval_note, actor):
    """A distinct finance reviewer approves the amount, never sends money."""
    _staff(actor, "store.approve_storereturnrefund")
    note = (approval_note or "").strip()
    if len(note) < 8:
        raise StoreRMAError("دلیل تأیید مستقل باید حداقل هشت نویسه باشد.")
    order_id = StoreReturnRefund.objects.select_related("return_request").get(
        pk=refund_id
    ).return_request.order_id
    with transaction.atomic():
        order = _order(order_id)
        refund = StoreReturnRefund.objects.select_for_update().select_related(
            "return_request", "payment"
        ).get(pk=refund_id)
        if actor.pk == refund.requested_by_id:
            raise StoreRMAError("درخواست‌کننده اجازه تأیید استرداد خودش را ندارد.")
        if refund.status == "approved":
            if refund.approved_by_id == actor.pk and refund.approval_note == note:
                return refund
            raise StoreRMAError("این درخواست پیش‌تر تأیید شده است.")
        if refund.status != "requested":
            raise StoreRMAError("فقط درخواست ثبت‌شده قابل تأیید مستقل است.")
        if refund.payment.status != "paid" or refund.payment.order_id != order.pk:
            raise StoreRMAError("دریافت معتبر برای بازپرداخت وجود ندارد.")
        rma = _request(refund.return_request_id)
        if rma.status not in {"received", "refunded"} or not hasattr(rma, "inspection"):
            raise StoreRMAError("کالا هنوز دریافت و بررسی نشده است.")
        refund.approved_by = actor
        refund.approved_at = timezone.now()
        refund.approval_note = note
        refund.status = "approved"
        refund.save(update_fields=["approved_by", "approved_at", "approval_note", "status"])
        return refund


def confirm_store_return_refund(
    *, refund_id, payout_reference, actor, confirmed_external_payout=False,
):
    _staff(actor, "store.change_storereturnrefund")
    reference = (payout_reference or "").strip()
    if not confirmed_external_payout or len(reference) < 4:
        raise StoreRMAError("تأیید و کد رسید پرداخت واقعی به مشتری الزامی است؛ سیستم انتقال وجه انجام نمی‌دهد.")
    order_id = StoreReturnRefund.objects.select_related("return_request").get(
        pk=refund_id
    ).return_request.order_id
    with transaction.atomic():
        order = _order(order_id)
        refund = StoreReturnRefund.objects.select_for_update().select_related(
            "return_request", "payment", "requested_by", "approved_by"
        ).get(pk=refund_id)
        if actor.pk == refund.requested_by_id:
            raise StoreRMAError("درخواست‌کننده حق ثبت تأیید پرداخت خودش را ندارد.")
        if refund.status == "completed":
            if refund.payout_reference == reference and StoreReturnRefundLedger.objects.filter(refund=refund).exists():
                return refund
            raise StoreRMAError("این بازپرداخت پیش‌تر با رسید دیگری قطعی شده است.")
        if refund.status != "approved" or not refund.approved_by_id or not refund.approved_at:
            raise StoreRMAError("استرداد باید ابتدا توسط مسئول مالی مستقل تأیید شده باشد.")
        if StoreReturnRefund.objects.filter(payout_reference=reference).exclude(pk=refund.pk).exists():
            raise StoreRMAError("شماره رسید استرداد قبلاً استفاده شده است.")
        if refund.payment.status != "paid" or refund.payment.order_id != order.pk:
            raise StoreRMAError("رسید اولیه دیگر دریافت واقعی معتبر برای این سفارش نیست.")
        rma = _request(refund.return_request_id)
        if rma.status not in {"received", "refunded"} or not hasattr(rma, "inspection"):
            raise StoreRMAError("مرجوعی هنوز بازرسی معتبر ندارد.")
        if not refund.amount or refund.amount > (int(refund.payment.amount) -
                int(StoreReturnRefundLedger.objects.filter(payment=refund.payment).aggregate(
                    total=Sum("amount"))["total"] or 0)):
            raise StoreRMAError("مجموع استردادهای واقعی از دریافتی اولیه بیشتر می‌شود.")
        if StoreReturnRefundLedger.objects.filter(order=order).aggregate(
            total=Sum("amount")
        )["total"] and int(StoreReturnRefundLedger.objects.filter(order=order).aggregate(
            total=Sum("amount")
        )["total"] or 0) + refund.amount > int(StorePayment.objects.filter(
            order=order, status="paid").aggregate(total=Sum("amount"))["total"] or 0):
            raise StoreRMAError("استرداد تجمعی از دریافت واقعی سفارش بیشتر است.")
        ledger = StoreReturnRefundLedger.objects.create(
            refund=refund, order=order, payment=refund.payment,
            amount=refund.amount, currency="IRT",
            event_key=f"store-rma-refund:{refund.pk}", provider_ref=reference,
            description=f"مرجوعی {rma.pk} | {refund.get_method_display()}",
            created_by=actor,
        )
        refund.status, refund.completed_by, refund.completed_at = "completed", actor, timezone.now()
        refund.payout_reference = reference
        refund.save(update_fields=["status", "payout_reference", "completed_by", "completed_at"])
        if rma.status == "received":
            rma.status = "refunded"
            rma.save(update_fields=["status", "updated_at"])
        record_event(order, "وجه مرجوعی بازگردانده شد",
            f"مرجوعی {rma.pk}: {refund.amount:,} تومان با رسید {reference} در دفتر استرداد ثبت شد.",
            actor=actor, public=True)
        return refund


def cancel_store_return_refund(*, refund_id, cancellation_reason, actor):
    _staff(actor, "store.change_storereturnrefund")
    reason = (cancellation_reason or "").strip()
    if len(reason) < 8:
        raise StoreRMAError("دلیل لغو بازپرداخت حداقل هشت نویسه باشد.")
    order_id = StoreReturnRefund.objects.select_related("return_request").get(
        pk=refund_id).return_request.order_id
    with transaction.atomic():
        _order(order_id)
        refund = StoreReturnRefund.objects.select_for_update().get(pk=refund_id)
        if refund.status not in {"requested", "approved"}:
            raise StoreRMAError("فقط درخواست پرداخت‌نشده قابل لغو است.")
        if refund.status == "approved" and (
            actor.pk == refund.requested_by_id or not actor.has_perm("store.approve_storereturnrefund")
        ):
            raise StoreRMAError("لغو درخواست تأییدشده نیازمند مسئول مالی مستقل است.")
        refund.status, refund.cancelled_reason = "cancelled", reason
        refund.save(update_fields=["status", "cancelled_reason"])
        return refund


def full_store_order_refund_proven(order):
    """No partial RMA can reverse the entire affiliate commission or order payment."""
    if not order.pk:
        return False
    gross = int(StorePayment.objects.filter(order=order, status="paid").aggregate(
        total=Sum("amount"))["total"] or 0)
    if gross < 1:
        return False
    returned = int(StoreReturnRefundLedger.objects.filter(order=order).aggregate(
        total=Sum("amount"))["total"] or 0)
    if returned < gross:
        return False
    for item in order.items.all():
        qty = int(StoreReturnInspection.objects.filter(
            return_request__order=order, return_request__item=item,
            return_request__status="refunded"
        ).aggregate(total=Sum("received_quantity"))["total"] or 0)
        if qty < item.quantity:
            return False
    return True
