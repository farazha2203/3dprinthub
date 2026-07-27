from __future__ import annotations

from datetime import timedelta

from django import template
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.db.models import F, Sum
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from store.models import ProductVariant, ReturnRequest, StoreOrder, StorePayment
from website.models import Order, Payment


register = template.Library()


def _can_view(user, model) -> bool:
    opts = model._meta
    return bool(
        user.is_active
        and user.is_staff
        and user.has_perm(f"{opts.app_label}.view_{opts.model_name}")
    )


def _safe_count(queryset) -> int:
    try:
        return queryset.count()
    except DatabaseError:
        return 0


def _safe_sum(queryset, field: str) -> int:
    try:
        return int(queryset.aggregate(value=Sum(field))["value"] or 0)
    except (DatabaseError, TypeError, ValueError):
        return 0


def _admin_url(model, object_id) -> str:
    opts = model._meta
    try:
        return reverse(
            f"admin:{opts.app_label}_{opts.model_name}_change",
            args=(object_id,),
        )
    except NoReverseMatch:
        return "#"


def _recent_orders(user, limit: int = 8) -> list[dict]:
    records: list[dict] = []

    if _can_view(user, Order):
        try:
            for order in Order.objects.select_related("customer").order_by("-created_at")[:limit]:
                records.append(
                    {
                        "timestamp": order.created_at,
                        "number": f"سفارش خدمات #{order.pk}",
                        "kind": "خدمات",
                        "customer": f"{order.first_name} {order.last_name}".strip() or order.phone,
                        "amount": None,
                        "status": order.get_status_display(),
                        "url": _admin_url(Order, order.pk),
                    }
                )
        except DatabaseError:
            pass

    if _can_view(user, StoreOrder):
        try:
            for order in StoreOrder.objects.select_related("user").order_by("-created_at")[:limit]:
                records.append(
                    {
                        "timestamp": order.created_at,
                        "number": order.order_number,
                        "kind": "فروشگاه",
                        "customer": order.full_name or order.phone,
                        "amount": int(order.total_amount or 0),
                        "status": order.get_status_display(),
                        "url": _admin_url(StoreOrder, order.pk),
                    }
                )
        except DatabaseError:
            pass

    return sorted(records, key=lambda item: item["timestamp"], reverse=True)[:limit]


def _revenue_chart(user, days: int = 7) -> tuple[list[str], list[int]]:
    today = timezone.localdate()
    labels: list[str] = []
    values: list[int] = []

    for offset in range(days - 1, -1, -1):
        day = today - timedelta(days=offset)
        labels.append(day.strftime("%m/%d"))
        value = 0

        if _can_view(user, Payment):
            value += _safe_sum(
                Payment.objects.filter(status="paid", created_at__date=day),
                "amount",
            )
        if _can_view(user, StorePayment):
            value += _safe_sum(
                StorePayment.objects.filter(status="paid", created_at__date=day),
                "amount",
            )
        values.append(value)

    return labels, values


@register.simple_tag(takes_context=True)
def admin_dashboard_data(context):
    user = context["request"].user
    today = timezone.localdate()
    since_30 = timezone.now() - timedelta(days=30)

    can_view_service_orders = _can_view(user, Order)
    can_view_store_orders = _can_view(user, StoreOrder)
    can_view_service_payments = _can_view(user, Payment)
    can_view_store_payments = _can_view(user, StorePayment)
    can_view_inventory = _can_view(user, ProductVariant)
    can_view_returns = _can_view(user, ReturnRequest)

    revenue_30 = 0
    if can_view_service_payments:
        revenue_30 += _safe_sum(
            Payment.objects.filter(status="paid", created_at__gte=since_30),
            "amount",
        )
    if can_view_store_payments:
        revenue_30 += _safe_sum(
            StorePayment.objects.filter(status="paid", created_at__gte=since_30),
            "amount",
        )

    today_orders = 0
    active_orders = 0
    if can_view_service_orders:
        today_orders += _safe_count(Order.objects.filter(created_at__date=today))
        active_orders += _safe_count(
            Order.objects.exclude(status__in={"done", "cancelled"})
        )
    if can_view_store_orders:
        today_orders += _safe_count(StoreOrder.objects.filter(created_at__date=today))
        active_orders += _safe_count(
            StoreOrder.objects.exclude(
                status__in={"delivered", "cancelled", "refunded"}
            )
        )

    pending_payments = 0
    if can_view_service_payments:
        pending_payments += _safe_count(Payment.objects.filter(status="pending"))
    if can_view_store_payments:
        pending_payments += _safe_count(
            StorePayment.objects.filter(status__in={"pending", "awaiting_review"})
        )

    open_returns = 0
    if can_view_returns:
        open_returns = _safe_count(
            ReturnRequest.objects.exclude(status__in={"rejected", "refunded", "closed"})
        )

    low_stock_variants = []
    if can_view_inventory:
        try:
            low_stock_variants = list(
                ProductVariant.objects.select_related("product")
                .annotate(
                    available_for_dashboard=F("stock_quantity") - F("reserved_quantity")
                )
                .filter(
                    is_active=True,
                    track_inventory=True,
                    available_for_dashboard__lte=F("low_stock_threshold"),
                )
                .order_by("available_for_dashboard", "product__title")[:6]
            )
        except DatabaseError:
            low_stock_variants = []

    new_customers = 0
    user_model = get_user_model()
    if _can_view(user, user_model):
        new_customers = _safe_count(user_model.objects.filter(date_joined__gte=since_30))

    chart_labels, chart_values = _revenue_chart(user)

    return {
        "revenue_30": revenue_30,
        "today_orders": today_orders,
        "active_orders": active_orders,
        "pending_payments": pending_payments,
        "open_returns": open_returns,
        "follow_up_count": pending_payments + open_returns,
        "low_stock_count": len(low_stock_variants),
        "low_stock_variants": low_stock_variants,
        "new_customers_30": new_customers,
        "recent_orders": _recent_orders(user),
        "chart_labels": chart_labels,
        "chart_values": chart_values,
        "permissions": {
            "service_orders": can_view_service_orders,
            "store_orders": can_view_store_orders,
            "inventory": can_view_inventory,
            "returns": can_view_returns,
        },
    }


@register.simple_tag(takes_context=True)
def admin_shell_data(context):
    user = context["request"].user
    if not user.is_authenticated:
        return {"recent_activity": []}

    try:
        recent_activity = list(
            LogEntry.objects.filter(user=user)
            .select_related("content_type")
            .order_by("-action_time")[:6]
        )
    except DatabaseError:
        recent_activity = []

    return {"recent_activity": recent_activity}
