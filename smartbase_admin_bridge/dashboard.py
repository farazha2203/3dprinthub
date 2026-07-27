from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from django_smartbase_admin.admin.site import sb_admin_site
from django_smartbase_admin.audit.models import AdminAuditLog
from django_smartbase_admin.engine.dashboard import SBAdminDashboardHtmlWidget
from django_smartbase_admin.messaging.models import MessageRecipient

from .utils import (
    DATE_FIELD_CANDIDATES,
    STATUS_FIELD_CANDIDATES,
    concrete_field_names,
    get_date_field_name,
    get_order_models,
    get_status_field_name,
)


@dataclass(frozen=True)
class RecentOrder:
    title: str
    status: str
    created_at: Any
    url: str


def _status_label(obj, status_field: str | None) -> str:
    if not status_field:
        return "—"
    display = getattr(obj, f"get_{status_field}_display", None)
    if callable(display):
        try:
            return str(display())
        except Exception:
            pass
    return str(getattr(obj, status_field, "") or "—")


def _detail_url(obj) -> str:
    view = sb_admin_site._registry.get(type(obj))
    if view is None:
        return ""
    try:
        return view.get_detail_url(obj.pk)
    except Exception:
        return ""


def _count_status(model, tokens: tuple[str, ...]) -> int:
    status_field = get_status_field_name(model)
    if not status_field:
        return 0

    field = model._meta.get_field(status_field)
    matching_values = []
    for value, label in getattr(field, "choices", ()) or ():
        text = f"{value} {label}".lower()
        if any(token.lower() in text for token in tokens):
            matching_values.append(value)

    try:
        if matching_values:
            return model._default_manager.filter(
                **{f"{status_field}__in": matching_values}
            ).count()

        query = Q()
        for token in tokens:
            query |= Q(**{f"{status_field}__icontains": token})
        return model._default_manager.filter(query).count()
    except Exception:
        return 0


class AdminOverviewWidget(SBAdminDashboardHtmlWidget):
    widget_id = "project_overview"
    name = "نمای کلی 3DPrintHub"
    content_template_name = "smartbase_admin_bridge/dashboard_overview.html"

    def has_view_or_change_permission(self, request, obj=None):
        return bool(getattr(request.user, "is_staff", False))

    def get_html_context_data(self, request):
        today = timezone.localdate()
        order_models = get_order_models()

        total_orders = 0
        today_orders = 0
        pending_orders = 0
        active_orders = 0
        ready_orders = 0
        recent: list[RecentOrder] = []

        for model in order_models:
            manager = model._default_manager
            try:
                total_orders += manager.count()
            except Exception:
                continue

            date_field = get_date_field_name(model)
            status_field = get_status_field_name(model)

            if date_field:
                try:
                    today_orders += manager.filter(
                        **{f"{date_field}__date": today}
                    ).count()
                except Exception:
                    pass

            pending_orders += _count_status(
                model,
                (
                    "new",
                    "pending",
                    "review",
                    "quote",
                    "جدید",
                    "منتظر",
                    "بررسی",
                    "قیمت",
                ),
            )
            active_orders += _count_status(
                model,
                (
                    "processing",
                    "production",
                    "printing",
                    "progress",
                    "تولید",
                    "چاپ",
                    "انجام",
                ),
            )
            ready_orders += _count_status(
                model,
                (
                    "ready",
                    "completed",
                    "delivered",
                    "آماده",
                    "تکمیل",
                    "تحویل",
                ),
            )

            try:
                queryset = manager.all()
                queryset = (
                    queryset.order_by(f"-{date_field}")
                    if date_field
                    else queryset.order_by(f"-{model._meta.pk.name}")
                )
                for obj in queryset[:8]:
                    recent.append(
                        RecentOrder(
                            title=str(obj),
                            status=_status_label(obj, status_field),
                            created_at=(
                                getattr(obj, date_field, None)
                                if date_field
                                else None
                            ),
                            url=_detail_url(obj),
                        )
                    )
            except Exception:
                continue

        recent.sort(
            key=lambda item: item.created_at
            or timezone.make_aware(datetime(1970, 1, 1)),
            reverse=True,
        )

        unread_messages = 0
        try:
            unread_messages = MessageRecipient.objects.filter(
                user=request.user,
                read_at__isnull=True,
            ).count()
        except Exception:
            pass

        audit_count = 0
        try:
            audit_count = AdminAuditLog.objects.count()
        except Exception:
            pass

        active_users = 0
        try:
            active_users = get_user_model().objects.filter(
                is_active=True
            ).count()
        except Exception:
            pass

        return {
            "total_orders": total_orders,
            "today_orders": today_orders,
            "pending_orders": pending_orders,
            "active_orders": active_orders,
            "ready_orders": ready_orders,
            "unread_messages": unread_messages,
            "audit_count": audit_count,
            "active_users": active_users,
            "registered_views": len(sb_admin_site._registry),
            "recent_orders": recent[:10],
        }
