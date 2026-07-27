from __future__ import annotations

from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import (
    Coupon,
    CouponUsage,
    CustomerNotification,
    InventoryMovement,
    ProductVariant,
    Shipment,
    StoreInvoice,
    StoreOrder,
    StoreOrderEvent,
)

RESERVATION_MINUTES = int(getattr(settings, "STORE_RESERVATION_MINUTES", 90))


def notify(user, title, message, *, notification_type="system", url=""):
    notification = CustomerNotification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        url=url,
    )
    try:
        from .realtime import publish_notification
        publish_notification(notification.pk)
    except Exception:
        pass
    return notification


def record_event(order, title, description="", *, status=None, public=True, actor=None):
    return StoreOrderEvent.objects.create(
        order=order,
        status=status if status is not None else order.status,
        title=title,
        description=description,
        is_public=public,
        created_by=actor,
    )


def validate_coupon(code, *, user, cart_lines, subtotal):
    code = (code or "").strip().upper()
    if not code:
        return None, 0
    try:
        coupon = Coupon.objects.prefetch_related("categories", "products").get(code__iexact=code)
    except Coupon.DoesNotExist as exc:
        raise ValidationError("کد تخفیف معتبر نیست.") from exc
    if not coupon.is_currently_valid:
        raise ValidationError("زمان یا ظرفیت استفاده از این کد تخفیف به پایان رسیده است.")
    if int(subtotal) < int(coupon.minimum_order_amount):
        raise ValidationError(f"حداقل مبلغ استفاده از این کد {coupon.minimum_order_amount:,} تومان است.")
    if coupon.per_user_limit and CouponUsage.objects.filter(coupon=coupon, user=user).count() >= coupon.per_user_limit:
        raise ValidationError("سقف استفاده شما از این کد تخفیف تکمیل شده است.")

    product_ids = set(coupon.products.values_list("id", flat=True))
    category_ids = set(coupon.categories.values_list("id", flat=True))
    unrestricted = not product_ids and not category_ids
    eligible_subtotal = 0
    for line in cart_lines:
        variant = line[0]
        line_total = int(line[3])
        if unrestricted or variant.product_id in product_ids or variant.product.category_id in category_ids:
            eligible_subtotal += line_total
    if eligible_subtotal <= 0:
        raise ValidationError("این کد برای محصولات موجود در سبد خرید قابل استفاده نیست.")

    if coupon.discount_type == "percent":
        discount = int((Decimal(eligible_subtotal) * Decimal(coupon.value) / Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    else:
        discount = min(int(coupon.value), eligible_subtotal)
    if coupon.maximum_discount:
        discount = min(discount, int(coupon.maximum_discount))
    return coupon, max(0, discount)


@transaction.atomic
def reserve_order_inventory(order):
    if order.inventory_reserved:
        return
    items = list(order.items.select_related("variant").all())
    variant_ids = [item.variant_id for item in items if item.variant_id]
    variants = {
        variant.pk: variant
        for variant in ProductVariant.objects.select_for_update().filter(pk__in=variant_ids)
    }
    for item in items:
        variant = variants.get(item.variant_id)
        if not variant or not variant.track_inventory:
            continue
        available = max(0, int(variant.stock_quantity) - int(variant.reserved_quantity))
        if not variant.allow_backorder and available < item.quantity:
            raise ValidationError(f"موجودی {item.product_title} کافی نیست؛ موجودی قابل سفارش {available} عدد است.")
        variant.reserved_quantity = int(variant.reserved_quantity) + int(item.quantity)
        variant.save(update_fields=["reserved_quantity"])
        InventoryMovement.objects.create(
            variant=variant,
            order=order,
            movement_type="reserve",
            quantity=int(item.quantity),
            stock_after=variant.stock_quantity,
            reserved_after=variant.reserved_quantity,
            note=f"رزرو برای سفارش {order.order_number}",
        )
    order.inventory_reserved = True
    order.reservation_expires_at = timezone.now() + timedelta(minutes=RESERVATION_MINUTES)
    order.save(update_fields=["inventory_reserved", "reservation_expires_at", "updated_at"])


@transaction.atomic
def release_order_inventory(order, *, reason="آزادسازی رزرو سفارش", actor=None):
    order = StoreOrder.objects.select_for_update().get(pk=order.pk)
    if not order.inventory_reserved:
        return False
    items = list(order.items.all())
    variants = {
        variant.pk: variant
        for variant in ProductVariant.objects.select_for_update().filter(pk__in=[i.variant_id for i in items if i.variant_id])
    }
    for item in items:
        variant = variants.get(item.variant_id)
        if not variant or not variant.track_inventory:
            continue
        released = min(int(item.quantity), int(variant.reserved_quantity))
        variant.reserved_quantity = max(0, int(variant.reserved_quantity) - released)
        variant.save(update_fields=["reserved_quantity"])
        InventoryMovement.objects.create(
            variant=variant,
            order=order,
            movement_type="release",
            quantity=-released,
            stock_after=variant.stock_quantity,
            reserved_after=variant.reserved_quantity,
            note=reason,
            created_by=actor,
        )
    order.inventory_reserved = False
    order.reservation_expires_at = None
    order.save(update_fields=["inventory_reserved", "reservation_expires_at", "updated_at"])
    return True


def create_invoice(order):
    try:
        return order.invoice
    except StoreInvoice.DoesNotExist:
        pass
    try:
        from website.models import SEOSettings
        seo = SEOSettings.objects.first()
    except Exception:
        seo = None
    seller_name = getattr(seo, "organization_name", "") or "3DprintHub"
    seller_phone = getattr(seo, "organization_phone", "") or ""
    seller_parts = [
        getattr(seo, "address_region", "") if seo else "",
        getattr(seo, "address_locality", "") if seo else "",
        getattr(seo, "street_address", "") if seo else "",
        getattr(seo, "organization_postal_code", "") if seo else "",
    ]
    seller_address = "، ".join(part for part in seller_parts if part)
    buyer_address = "، ".join(part for part in [order.province, getattr(order, "county", ""), order.city, order.address, order.postal_code] if part)
    return StoreInvoice.objects.create(
        order=order,
        seller_name=seller_name,
        seller_phone=seller_phone,
        seller_address=seller_address,
        buyer_name=order.full_name,
        buyer_phone=order.phone,
        buyer_address=buyer_address,
        subtotal=order.subtotal,
        discount_amount=order.discount_amount,
        shipping_fee=order.shipping_fee,
        packaging_fee=order.packaging_fee,
        tax_amount=order.tax_amount,
        total_amount=order.total_amount,
    )


@transaction.atomic
def finalize_paid_order(order, *, actor=None):
    order = StoreOrder.objects.select_for_update().get(pk=order.pk)
    items = list(order.items.all())
    if order.inventory_reserved:
        variants = {
            variant.pk: variant
            for variant in ProductVariant.objects.select_for_update().filter(pk__in=[i.variant_id for i in items if i.variant_id])
        }
        for item in items:
            variant = variants.get(item.variant_id)
            if not variant or not variant.track_inventory:
                continue
            qty = int(item.quantity)
            variant.reserved_quantity = max(0, int(variant.reserved_quantity) - qty)
            variant.stock_quantity = max(0, int(variant.stock_quantity) - qty)
            variant.save(update_fields=["stock_quantity", "reserved_quantity"])
            InventoryMovement.objects.create(
                variant=variant,
                order=order,
                movement_type="sale",
                quantity=-qty,
                stock_after=variant.stock_quantity,
                reserved_after=variant.reserved_quantity,
                note=f"فروش قطعی سفارش {order.order_number}",
                created_by=actor,
            )
        order.inventory_reserved = False
        order.reservation_expires_at = None
        order.save(update_fields=["inventory_reserved", "reservation_expires_at", "updated_at"])

    if order.coupon_id and order.discount_amount and not CouponUsage.objects.filter(order=order).exists():
        CouponUsage.objects.create(
            coupon=order.coupon,
            user=order.user,
            order=order,
            discount_amount=order.discount_amount,
        )
        Coupon.objects.filter(pk=order.coupon_id).update(used_count=F("used_count") + 1)

    create_invoice(order)
    from .affiliate_services import create_commission_for_order
    create_commission_for_order(order)
    from .production_services import create_job_for_store_order
    create_job_for_store_order(order)
    if not order.events.filter(title="پرداخت سفارش تأیید شد").exists():
        record_event(order, "پرداخت سفارش تأیید شد", "پرداخت با موفقیت تأیید و سفارش وارد صف اجرا شد.", status=order.status, actor=actor)
        notify(order.user, "پرداخت سفارش تأیید شد", f"پرداخت سفارش {order.order_number} تأیید شد.", notification_type="payment", url=order.get_absolute_url())


@transaction.atomic
def transition_order(order, status, *, actor=None, description="", public=True):
    order = StoreOrder.objects.select_for_update().get(pk=order.pk)
    old_status = order.status
    if old_status == status:
        return order
    if status in {"cancelled", "refunded"}:
        if status == "cancelled":
            release_order_inventory(order, reason="لغو سفارش", actor=actor)
            order.refresh_from_db()
        from .affiliate_services import reverse_commission
        reverse_commission(order, reason="لغو یا استرداد سفارش", actor=actor)
    order.status = status
    update_fields = ["status", "updated_at"]
    shipment = None
    if status in {"ready", "shipped", "delivered"}:
        shipment, _ = Shipment.objects.get_or_create(order=order)
    if status == "shipped":
        shipment.status = "shipped"
        shipment.shipped_at = shipment.shipped_at or timezone.now()
        shipment.tracking_code = shipment.tracking_code or order.tracking_code
        shipment.save()
    elif status == "delivered":
        shipment.status = "delivered"
        shipment.delivered_at = timezone.now()
        shipment.save()
    order.save(update_fields=update_fields)
    if status == "delivered":
        from .production_services import finalize_store_order_job
        finalize_store_order_job(order, actor=actor)
        from .affiliate_services import schedule_commission_after_delivery
        schedule_commission_after_delivery(order)
    title = f"وضعیت سفارش: {order.get_status_display()}"
    record_event(order, title, description, status=status, public=public, actor=actor)
    notify(order.user, title, description or f"وضعیت سفارش {order.order_number} به «{order.get_status_display()}» تغییر کرد.", notification_type="shipping" if status in {"ready", "shipped", "delivered"} else "order", url=order.get_absolute_url())
    return order


def release_expired_reservations():
    qs = StoreOrder.objects.filter(
        inventory_reserved=True,
        reservation_expires_at__lt=timezone.now(),
        payment_status__in=["pending", "failed"],
    )
    count = 0
    for order in qs.iterator():
        if release_order_inventory(order, reason="انقضای مهلت پرداخت"):
            record_event(order, "رزرو موجودی منقضی شد", "به دلیل پایان مهلت پرداخت، موجودی سفارش آزاد شد.")
            notify(order.user, "مهلت رزرو سفارش پایان یافت", f"رزرو موجودی سفارش {order.order_number} آزاد شد؛ برای خرید مجدد سبد را بررسی کنید.", notification_type="order", url=order.get_absolute_url())
            count += 1
    return count
