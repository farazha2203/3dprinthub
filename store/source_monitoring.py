from __future__ import annotations

import time
from contextlib import contextmanager

from django.utils import timezone

from .models import ExternalSourceFetchLog


@contextmanager
def source_log(*, source_key: str, action: str, actor=None, message: str = ""):
    log = ExternalSourceFetchLog.objects.create(
        source_key=source_key,
        action=action,
        status="running",
        progress_percent=1,
        current_stage="شروع",
        message=message,
        started_at=timezone.now(),
        created_by=actor if getattr(actor, "is_authenticated", False) else None,
    )
    started = time.monotonic()
    try:
        yield log
    except Exception as exc:
        log.status = "failed"
        log.progress_percent = 100
        log.current_stage = "ناموفق"
        log.error = f"{type(exc).__name__}: {exc}"[:4000]
        log.finished_at = timezone.now()
        log.duration_ms = int((time.monotonic() - started) * 1000)
        log.save(update_fields=[
            "status", "progress_percent", "current_stage", "error",
            "finished_at", "duration_ms", "updated_at",
        ])
        raise
    else:
        if log.status == "running":
            log.status = "success"
        log.progress_percent = 100
        log.current_stage = "تکمیل"
        log.finished_at = timezone.now()
        log.duration_ms = int((time.monotonic() - started) * 1000)
        log.save(update_fields=[
            "status", "progress_percent", "current_stage", "finished_at",
            "duration_ms", "updated_at",
        ])


def update_log(log, *, stage=None, progress=None, message=None, http_status=None,
               records_found=None, records_saved=None, records_updated=None,
               records_failed=None, details=None, status=None):
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
    if fields:
        fields.append("updated_at")
        log.save(update_fields=fields)
    return log
