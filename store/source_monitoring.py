from __future__ import annotations

import time
from contextlib import contextmanager
from datetime import timedelta

from django.utils import timezone

from .automation_watchdog import source_timeout_minutes
from .models import ExternalSourceFetchLog


class SourceOperationCancelled(RuntimeError):
    pass


class SourceOperationDeadlineExceeded(TimeoutError):
    pass


def _assert_source_log_active(log, *, now=None):
    now = now or timezone.now()
    state = ExternalSourceFetchLog.objects.filter(pk=log.pk).values(
        "status", "cancelled_at", "deadline_at"
    ).first()
    if state is None:
        raise SourceOperationCancelled("Source operation log no longer exists.")
    if state["status"] == "cancelled" or state["cancelled_at"]:
        raise SourceOperationCancelled("Source operation was cancelled by an operator.")
    deadline_at = state["deadline_at"]
    if deadline_at and deadline_at <= now:
        raise SourceOperationDeadlineExceeded(
            f"Source operation deadline exceeded at {deadline_at.isoformat()}."
        )
    return state


@contextmanager
def source_log(*, source_key: str, action: str, actor=None, message: str = ""):
    now = timezone.now()
    probe = ExternalSourceFetchLog(source_key=source_key, action=action)
    timeout_minutes = source_timeout_minutes(probe)
    log = ExternalSourceFetchLog.objects.create(
        source_key=source_key,
        action=action,
        status="running",
        progress_percent=1,
        current_stage="starting",
        message=message,
        started_at=now,
        heartbeat_at=now,
        deadline_at=now + timedelta(minutes=timeout_minutes),
        created_by=actor if getattr(actor, "is_authenticated", False) else None,
        details={"timeout_minutes": timeout_minutes},
    )
    started = time.monotonic()
    try:
        yield log
    except Exception as exc:
        log.refresh_from_db()
        finished_at = timezone.now()
        duration_ms = int((time.monotonic() - started) * 1000)
        if log.status == "cancelled" or log.cancelled_at:
            if not log.finished_at:
                log.finished_at = finished_at
            log.progress_percent = 100
            log.current_stage = "cancelled_by_operator"
            log.duration_ms = duration_ms
            log.heartbeat_at = finished_at
            log.save(update_fields=[
                "progress_percent", "current_stage", "finished_at",
                "duration_ms", "heartbeat_at", "updated_at",
            ])
            raise
        log.status = "failed"
        log.progress_percent = 100
        if isinstance(exc, SourceOperationDeadlineExceeded):
            log.current_stage = "deadline_exceeded"
        else:
            log.current_stage = "failed"
        log.error = f"{type(exc).__name__}: {exc}"[:4000]
        log.finished_at = finished_at
        log.duration_ms = duration_ms
        log.heartbeat_at = finished_at
        log.save(update_fields=[
            "status", "progress_percent", "current_stage", "error",
            "finished_at", "duration_ms", "heartbeat_at", "updated_at",
        ])
        raise
    else:
        log.refresh_from_db()
        finished_at = timezone.now()
        duration_ms = int((time.monotonic() - started) * 1000)
        if log.status == "cancelled" or log.cancelled_at:
            if not log.finished_at:
                log.finished_at = finished_at
            log.progress_percent = 100
            log.current_stage = "cancelled_by_operator"
            log.duration_ms = duration_ms
            log.heartbeat_at = finished_at
            log.save(update_fields=[
                "progress_percent", "current_stage", "finished_at",
                "duration_ms", "heartbeat_at", "updated_at",
            ])
            return
        if log.deadline_at and log.deadline_at <= finished_at:
            log.status = "failed"
            log.current_stage = "deadline_exceeded"
            log.error = (
                f"SourceOperationDeadlineExceeded: deadline was "
                f"{log.deadline_at.isoformat()}."
            )
        else:
            if log.status == "running":
                log.status = "success"
            log.current_stage = "completed"
        log.progress_percent = 100
        log.finished_at = finished_at
        log.duration_ms = duration_ms
        log.heartbeat_at = finished_at
        log.save(update_fields=[
            "status", "progress_percent", "current_stage", "error",
            "finished_at", "duration_ms", "heartbeat_at", "updated_at",
        ])


def update_log(log, *, stage=None, progress=None, message=None, http_status=None,
               records_found=None, records_saved=None, records_updated=None,
               records_failed=None, details=None, status=None):
    now = timezone.now()
    _assert_source_log_active(log, now=now)
    fields = []
    mapping = {
        "current_stage": stage,
        "progress_percent": progress,
        "message": message,
        "http_status": http_status,
        "records_found": records_found,
        "records_saved": records_saved,
        "records_updated": records_updated,
        "records_failed": records_failed,
        "details": details,
        "status": status,
    }
    for field, value in mapping.items():
        if value is not None:
            setattr(log, field, value)
            fields.append(field)
    log.heartbeat_at = now
    fields.append("heartbeat_at")
    fields.append("updated_at")
    log.save(update_fields=list(dict.fromkeys(fields)))
    return log
