from __future__ import annotations

import logging
from html import escape

from django.contrib.auth import get_user_model
from django.db import DatabaseError, transaction
from django.db.models.signals import post_save, pre_save

from django_smartbase_admin.messaging.services import SBAdminMessagingService

from .utils import get_order_models, get_status_field_name


logger = logging.getLogger(__name__)
_previous_status: dict[tuple[str, object], str] = {}


def _before_order_save(sender, instance, raw=False, **kwargs):
    if raw or not instance.pk:
        return

    status_field = get_status_field_name(sender)
    if not status_field:
        return

    try:
        previous = sender._default_manager.only(status_field).get(
            pk=instance.pk
        )
    except sender.DoesNotExist:
        return
    except Exception:
        return

    _previous_status[(sender._meta.label_lower, instance.pk)] = str(
        getattr(previous, status_field, "") or ""
    )


def _send_staff_message(
    *,
    title: str,
    content: str,
    message_type: str,
) -> None:
    try:
        user_ids = list(
            get_user_model()
            .objects.filter(is_active=True, is_staff=True)
            .values_list("pk", flat=True)
        )
        if not user_ids:
            return
        SBAdminMessagingService.create_message(
            title=title,
            type=message_type,
            content=content,
            user_ids=user_ids,
        )
    except DatabaseError:
        # Tables may not exist yet while migrations are being applied.
        logger.debug("SmartBase messaging tables are not ready yet")
    except Exception:
        logger.exception("Could not create SmartBase order notification")


def _after_order_save(sender, instance, created, raw=False, **kwargs):
    if raw:
        return

    status_field = get_status_field_name(sender)
    previous = _previous_status.pop(
        (sender._meta.label_lower, instance.pk),
        "",
    )
    current = (
        str(getattr(instance, status_field, "") or "")
        if status_field
        else ""
    )

    if not created and (not status_field or previous == current):
        return

    if created:
        title = "سفارش جدید ثبت شد"
        content = (
            f"<strong>{escape(str(instance))}</strong>"
            f"<br>نوع رکورد: {escape(str(sender._meta.verbose_name))}"
        )
        message_type = "info"
    else:
        title = "وضعیت سفارش تغییر کرد"
        content = (
            f"<strong>{escape(str(instance))}</strong>"
            f"<br>وضعیت قبلی: {escape(previous or '—')}"
            f"<br>وضعیت جدید: {escape(current or '—')}"
        )
        message_type = "warning"

    transaction.on_commit(
        lambda: _send_staff_message(
            title=title,
            content=content,
            message_type=message_type,
        )
    )


def connect_order_notification_signals() -> None:
    for model in get_order_models():
        pre_save.connect(
            _before_order_save,
            sender=model,
            weak=False,
            dispatch_uid=(
                "smartbase_admin_bridge.pre_save."
                f"{model._meta.label_lower}"
            ),
        )
        post_save.connect(
            _after_order_save,
            sender=model,
            weak=False,
            dispatch_uid=(
                "smartbase_admin_bridge.post_save."
                f"{model._meta.label_lower}"
            ),
        )


connect_order_notification_signals()
