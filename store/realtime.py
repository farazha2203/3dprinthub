from __future__ import annotations

import logging
import time
from typing import Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.db.models import Count
from django.urls import reverse

logger = logging.getLogger(__name__)
_REALTIME_FAILURE_LOGGED_AT = 0.0
_REALTIME_FAILURE_COOLDOWN = 60.0


def user_notification_group(user_id: int) -> str:
    return f"user-notifications-{int(user_id)}"


def analysis_group(token) -> str:
    return f"link-analysis-{str(token)}"


def operations_group() -> str:
    return "link-analysis-operations"


def _send(group: str, event: str, payload: dict[str, Any]) -> bool:
    layer = get_channel_layer()
    if layer is None:
        return False
    try:
        async_to_sync(layer.group_send)(
            group,
            {"type": "realtime.message", "event": event, "payload": payload},
        )
        return True
    except Exception as exc:
        global _REALTIME_FAILURE_LOGGED_AT
        now = time.monotonic()
        if now - _REALTIME_FAILURE_LOGGED_AT >= _REALTIME_FAILURE_COOLDOWN:
            _REALTIME_FAILURE_LOGGED_AT = now
            logger.warning(
                "Realtime temporarily unavailable; polling remains active. group=%s event=%s error=%s",
                group,
                event,
                exc,
            )
        return False


def send_after_commit(group: str, event: str, payload_factory) -> None:
    def callback():
        try:
            payload = payload_factory() if callable(payload_factory) else payload_factory
            if payload is not None:
                _send(group, event, payload)
        except Exception:
            logger.exception("Realtime after-commit callback failed")

    transaction.on_commit(callback)


def notification_payload(notification) -> dict[str, Any]:
    from .models import CustomerNotification

    unread_count = CustomerNotification.objects.filter(user_id=notification.user_id, read_at__isnull=True).count()
    return {
        "id": notification.pk,
        "title": notification.title,
        "message": notification.message,
        "url": notification.url or reverse("store:notifications"),
        "notification_type": notification.notification_type,
        "created_at": notification.created_at.isoformat(),
        "unread_count": unread_count,
    }


def publish_notification(notification_id: int) -> None:
    from .models import CustomerNotification

    def payload():
        item = CustomerNotification.objects.get(pk=notification_id)
        return notification_payload(item)

    item = CustomerNotification.objects.only("user_id").get(pk=notification_id)
    send_after_commit(user_notification_group(item.user_id), "notification.created", payload)


def publish_notification_count(user_id: int) -> None:
    from .models import CustomerNotification

    send_after_commit(
        user_notification_group(user_id),
        "notification.count",
        lambda: {
            "unread_count": CustomerNotification.objects.filter(user_id=user_id, read_at__isnull=True).count()
        },
    )


def job_realtime_payload(job_id: int) -> dict[str, Any]:
    from .link_analysis_queue import link_analysis_job_payload
    from .models import CustomerLinkAnalysisJob

    job = CustomerLinkAnalysisJob.objects.select_related("analysis").get(pk=job_id)
    payload = link_analysis_job_payload(job, job.analysis)
    payload.update({
        "analysis_title": job.analysis.title or "",
        "estimated_price": int(job.analysis.estimated_price or 0),
        "result_url": reverse("store:external_link_analysis", args=[job.analysis.public_token]),
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    })
    return payload


def publish_job(job_id: int, *, include_operations: bool = True) -> None:
    from .models import CustomerLinkAnalysisJob

    row = CustomerLinkAnalysisJob.objects.select_related("analysis").only("id", "analysis__public_token").get(pk=job_id)
    send_after_commit(analysis_group(row.analysis.public_token), "link.job", lambda: job_realtime_payload(job_id))
    if include_operations:
        publish_operations()


def operations_snapshot() -> dict[str, Any]:
    from .link_analysis_operations import queue_metrics
    from .models import LinkAnalysisManualReview

    metrics = queue_metrics()
    open_reviews = LinkAnalysisManualReview.objects.filter(status__in=["pending", "in_progress"])
    workers = []
    for worker in metrics["workers"][:10]:
        workers.append({
            "worker_id": worker.worker_id,
            "status": worker.status,
            "status_label": worker.get_status_display(),
            "last_seen_at": worker.last_seen_at.isoformat(),
            "current_job_id": worker.current_job_id,
            "succeeded_count": int(worker.succeeded_count),
            "failed_count": int(worker.failed_count),
        })
    jobs = []
    for job in metrics["recent_jobs"][:12]:
        jobs.append({
            "id": job.pk,
            "title": job.analysis.title or job.analysis.source_domain,
            "status": job.status,
            "status_label": job.get_status_display(),
            "adapter_key": job.adapter_key,
            "progress_percent": int(job.progress_percent or 0),
            "progress_stage": job.progress_stage,
            "progress_message": job.progress_message,
            "attempt_count": int(job.attempt_count or 0),
            "max_attempts": int(job.max_attempts or 0),
            "updated_at": job.updated_at.isoformat(),
        })
    return {
        "queue_paused": bool(metrics["control"].is_paused),
        "pause_reason": metrics["control"].pause_reason,
        "active_workers": metrics["active_workers"],
        "queued": metrics["queued"],
        "running": metrics["running"],
        "retry": metrics["retry"],
        "completed": metrics["completed"],
        "failed": metrics["failed"],
        "success_24h": metrics["success_24h"],
        "failure_24h": metrics["failure_24h"],
        "manual_review_pending": open_reviews.filter(status="pending").count(),
        "manual_review_in_progress": open_reviews.filter(status="in_progress").count(),
        "workers": workers,
        "jobs": jobs,
    }


def publish_operations() -> None:
    send_after_commit(operations_group(), "operations.snapshot", operations_snapshot)
