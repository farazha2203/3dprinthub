from __future__ import annotations

import os
import socket
import uuid
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max, Q
from django.utils import timezone

from .link_intelligence import (
    LinkAnalysisError,
    analyze_customer_link,
)
from .models import (
    CustomerLinkAnalysis,
    CustomerLinkAnalysisAttempt,
    CustomerLinkAnalysisJob,
)
from .link_analysis_operations import (
    adapter_is_available,
    notify_job_outcome,
    policy_for_analysis,
    policy_for_job,
    queue_control,
    record_adapter_outcome,
    retry_delay_for_policy,
)

DEFAULT_RETRY_DELAYS = (30, 120, 600, 1800)
STALE_LOCK_MINUTES = 15
TERMINAL_ANALYSIS_STATUSES = {"ready", "needs_input", "partial", "converted"}


def _publish_job(job_id: int, *, include_operations: bool = True) -> None:
    try:
        from .realtime import publish_job
        publish_job(job_id, include_operations=include_operations)
    except Exception:
        pass


def default_worker_id() -> str:
    host = socket.gethostname() or "worker"
    return f"{host}:{os.getpid()}:{uuid.uuid4().hex[:8]}"[:180]


def _retry_delay_seconds(attempt_number: int) -> int:
    index = max(min(int(attempt_number or 1) - 1, len(DEFAULT_RETRY_DELAYS) - 1), 0)
    return DEFAULT_RETRY_DELAYS[index]


def _is_transient_error(exc: Exception) -> bool:
    if isinstance(exc, LinkAnalysisError):
        return bool(getattr(exc, "transient", False))
    if isinstance(exc, (TimeoutError, ConnectionError, OSError)):
        return True
    return False


@transaction.atomic
def enqueue_link_analysis(
    analysis: CustomerLinkAnalysis,
    *,
    priority: int = 100,
    max_attempts: int = 4,
    force: bool = False,
) -> CustomerLinkAnalysisJob:
    if analysis.status == "converted" or analysis.order_id:
        raise ValidationError("تحلیلی که به سفارش تبدیل شده قابل صف‌کردن دوباره نیست.")

    now = timezone.now()
    policy = policy_for_analysis(analysis)
    effective_priority = int(policy.priority_override if policy.priority_override is not None else priority)
    requested_attempts = int(max_attempts or policy.max_attempts or 4)
    effective_attempts = max(1, min(int(policy.max_attempts or requested_attempts), requested_attempts, 10))
    job, created = CustomerLinkAnalysisJob.objects.select_for_update().get_or_create(
        analysis=analysis,
        defaults={
            "status": "queued",
            "priority": effective_priority,
            "adapter_key": policy.adapter_key,
            "max_attempts": effective_attempts,
            "next_run_at": now,
            "progress_percent": 0,
            "progress_stage": "queued" if adapter_is_available(policy, now=now) else "adapter_paused",
            "progress_message": "در انتظار پردازش" if adapter_is_available(policy, now=now) else "Adapter این منبع موقتاً متوقف است",
        },
    )
    if not created:
        if job.status == "running" and not force:
            return job
        if job.status in {"queued", "retry"} and not force:
            return job
        job.status = "queued"
        job.priority = effective_priority
        job.adapter_key = policy.adapter_key
        job.max_attempts = effective_attempts
        job.next_run_at = now
        job.locked_at = None
        job.worker_id = ""
        job.progress_percent = 0
        job.progress_stage = "queued"
        job.progress_message = "در انتظار پردازش مجدد" if force else "در انتظار پردازش"
        job.last_error_type = ""
        job.last_error = ""
        job.completed_at = None
        job.success_notified_at = None
        job.failure_notified_at = None
        if force:
            # attempt_count belongs to the new retry cycle. Attempt row numbers
            # remain monotonic so the audit history can be preserved safely.
            job.attempt_count = 0
        job.save()

    analysis.status = "pending"
    analysis.error_message = ""
    analysis.save(update_fields=["status", "error_message", "updated_at"])
    _publish_job(job.pk)
    return job


def release_stale_link_analysis_jobs(*, stale_minutes: int | None = None) -> int:
    if stale_minutes is None:
        stale_minutes = queue_control().stale_lock_minutes or STALE_LOCK_MINUTES
    cutoff = timezone.now() - timedelta(minutes=max(int(stale_minutes), 1))
    now = timezone.now()
    stale_ids = list(
        CustomerLinkAnalysisJob.objects.filter(status="running")
        .filter(Q(locked_at__lt=cutoff) | Q(locked_at__isnull=True))
        .values_list("pk", flat=True)
    )
    if not stale_ids:
        return 0
    updated = CustomerLinkAnalysisJob.objects.filter(pk__in=stale_ids, status="running").update(
        status="retry",
        next_run_at=now,
        locked_at=None,
        worker_id="",
        progress_stage="recovered",
        progress_message="Worker قبلی متوقف شد؛ Job برای تلاش مجدد آزاد شد",
        last_error_type="StaleWorkerLock",
        last_error="قفل Worker از زمان مجاز عبور کرد.",
    )
    CustomerLinkAnalysis.objects.filter(job__pk__in=stale_ids).exclude(status="converted").update(
        status="pending",
        error_message="",
    )
    completed_at = timezone.now()
    for attempt in CustomerLinkAnalysisAttempt.objects.filter(job_id__in=stale_ids, status="running"):
        duration_ms = max(int((completed_at - attempt.started_at).total_seconds() * 1000), 0)
        attempt.status = "transient_failure"
        attempt.stage = "recovered"
        attempt.error_type = "StaleWorkerLock"
        attempt.error_message = "Worker پیشین بدون تکمیل Attempt متوقف شد."
        attempt.completed_at = completed_at
        attempt.duration_ms = duration_ms
        attempt.save(update_fields=[
            "status", "stage", "error_type", "error_message", "completed_at", "duration_ms"
        ])
    for job_id in stale_ids:
        _publish_job(job_id)
    return updated


@transaction.atomic
def claim_next_link_analysis_job(*, worker_id: str | None = None) -> CustomerLinkAnalysisJob | None:
    worker_id = (worker_id or default_worker_id())[:180]
    now = timezone.now()
    control = queue_control()
    if control.is_paused:
        return None

    candidates = list(
        CustomerLinkAnalysisJob.objects.select_for_update()
        .select_related("analysis")
        .filter(status__in=["queued", "retry"], next_run_at__lte=now)
        .order_by("-priority", "next_run_at", "id")[:25]
    )
    for job in candidates:
        policy = policy_for_job(job)
        if not adapter_is_available(policy, now=now):
            next_run = policy.paused_until if policy.paused_until and policy.paused_until > now else now + timedelta(minutes=5)
            CustomerLinkAnalysisJob.objects.filter(pk=job.pk).update(
                adapter_key=policy.adapter_key,
                next_run_at=next_run,
                progress_stage="adapter_paused",
                progress_message="Adapter این منبع در پنل مدیریت متوقف است",
            )
            continue
        claimed = CustomerLinkAnalysisJob.objects.filter(
            pk=job.pk,
            status__in=["queued", "retry"],
            next_run_at__lte=now,
        ).update(
            status="running",
            adapter_key=policy.adapter_key,
            locked_at=now,
            worker_id=worker_id,
            attempt_count=job.attempt_count + 1,
            last_started_at=now,
            progress_percent=max(int(job.progress_percent or 0), 1),
            progress_stage="starting",
            progress_message="Worker تحلیل را دریافت کرد",
            completed_at=None,
        )
        if claimed:
            claimed_job = CustomerLinkAnalysisJob.objects.select_related("analysis").get(pk=job.pk)
            _publish_job(claimed_job.pk)
            return claimed_job
    return None

def _finish_attempt(
    attempt: CustomerLinkAnalysisAttempt,
    *,
    status: str,
    stage: str,
    error: Exception | None = None,
) -> None:
    completed_at = timezone.now()
    duration_ms = max(int((completed_at - attempt.started_at).total_seconds() * 1000), 0)
    attempt.status = status
    attempt.stage = (stage or "")[:80]
    attempt.error_type = type(error).__name__[:160] if error else ""
    attempt.error_message = str(error) if error else ""
    attempt.completed_at = completed_at
    attempt.duration_ms = duration_ms
    attempt.save(update_fields=[
        "status", "stage", "error_type", "error_message", "completed_at", "duration_ms"
    ])


def process_link_analysis_job(job: CustomerLinkAnalysisJob, *, worker_id: str | None = None) -> CustomerLinkAnalysisJob:
    worker_id = (worker_id or job.worker_id or default_worker_id())[:180]
    job.refresh_from_db()
    if job.status != "running":
        return job

    previous_attempt_number = (
        CustomerLinkAnalysisAttempt.objects.filter(job=job).aggregate(value=Max("attempt_number"))["value"] or 0
    )
    attempt = CustomerLinkAnalysisAttempt.objects.create(
        job=job,
        attempt_number=previous_attempt_number + 1,
        status="running",
        stage="starting",
        worker_id=worker_id,
    )

    def progress(percent: int, stage: str, message: str) -> None:
        CustomerLinkAnalysisJob.objects.filter(pk=job.pk, status="running").update(
            progress_percent=max(0, min(int(percent), 100)),
            progress_stage=(stage or "")[:80],
            progress_message=(message or "")[:300],
            locked_at=timezone.now(),
            worker_id=worker_id,
        )
        CustomerLinkAnalysisAttempt.objects.filter(pk=attempt.pk, status="running").update(stage=(stage or "")[:80])
        _publish_job(job.pk, include_operations=False)

    analysis = CustomerLinkAnalysis.objects.get(pk=job.analysis_id)
    policy = policy_for_job(job)
    try:
        result = analyze_customer_link(
            analysis,
            progress_callback=progress,
            raise_errors=True,
            request_timeout_seconds=policy.request_timeout_seconds,
            cache_remote_images=policy.cache_remote_images,
        )
        if result.status not in TERMINAL_ANALYSIS_STATUSES:
            raise RuntimeError(f"وضعیت نهایی تحلیل معتبر نیست: {result.status}")
    except Exception as exc:
        transient = _is_transient_error(exc)
        can_retry = transient and job.attempt_count < job.max_attempts
        now = timezone.now()
        if can_retry:
            delay = retry_delay_for_policy(policy, job.attempt_count)
            CustomerLinkAnalysisJob.objects.filter(pk=job.pk).update(
                status="retry",
                next_run_at=now + timedelta(seconds=delay),
                locked_at=None,
                worker_id="",
                progress_percent=0,
                progress_stage="retry_wait",
                progress_message=f"خطای موقت؛ تلاش بعدی حدود {delay} ثانیه دیگر",
                last_error_type=type(exc).__name__[:160],
                last_error=str(exc),
                completed_at=None,
            )
            CustomerLinkAnalysis.objects.filter(pk=job.analysis_id).exclude(status="converted").update(
                status="pending",
                error_message="",
            )
            _finish_attempt(attempt, status="transient_failure", stage="retry_wait", error=exc)
            _publish_job(job.pk)
        else:
            CustomerLinkAnalysisJob.objects.filter(pk=job.pk).update(
                status="failed",
                locked_at=None,
                worker_id="",
                progress_percent=100,
                progress_stage="failed",
                progress_message="تحلیل پس از تلاش‌های مجاز ناموفق بود",
                last_error_type=type(exc).__name__[:160],
                last_error=str(exc),
                completed_at=now,
            )
            _finish_attempt(attempt, status="permanent_failure", stage="failed", error=exc)
            try:
                record_adapter_outcome(policy, success=False, error=str(exc))
            except Exception:
                pass
            try:
                notify_job_outcome(CustomerLinkAnalysisJob.objects.get(pk=job.pk), success=False)
            except Exception:
                pass
            try:
                from .manual_review import ensure_manual_review
                ensure_manual_review(
                    CustomerLinkAnalysis.objects.get(pk=job.analysis_id),
                    job=CustomerLinkAnalysisJob.objects.get(pk=job.pk),
                    reason="auto_failed",
                    priority=140,
                )
            except Exception:
                pass
            _publish_job(job.pk)
    else:
        now = timezone.now()
        CustomerLinkAnalysisJob.objects.filter(pk=job.pk).update(
            status="completed",
            locked_at=None,
            worker_id="",
            next_run_at=now,
            progress_percent=100,
            progress_stage="completed",
            progress_message="تحلیل لینک با موفقیت تکمیل شد",
            last_error_type="",
            last_error="",
            completed_at=now,
        )
        _finish_attempt(attempt, status="success", stage="completed")
        try:
            record_adapter_outcome(policy, success=True)
        except Exception:
            pass
        try:
            notify_job_outcome(CustomerLinkAnalysisJob.objects.get(pk=job.pk), success=True)
        except Exception:
            pass
        try:
            from .manual_review import resolve_reviews_after_success
            resolve_reviews_after_success(job.analysis_id)
        except Exception:
            pass
        _publish_job(job.pk)

    return CustomerLinkAnalysisJob.objects.select_related("analysis").get(pk=job.pk)


def process_link_analysis_queue(
    *,
    limit: int = 5,
    worker_id: str | None = None,
    release_stale: bool = True,
) -> list[CustomerLinkAnalysisJob]:
    worker_id = worker_id or default_worker_id()
    if release_stale:
        release_stale_link_analysis_jobs()
    processed: list[CustomerLinkAnalysisJob] = []
    for _ in range(max(int(limit), 1)):
        job = claim_next_link_analysis_job(worker_id=worker_id)
        if job is None:
            break
        processed.append(process_link_analysis_job(job, worker_id=worker_id))
    return processed


def link_analysis_job_payload(job: CustomerLinkAnalysisJob | None, analysis: CustomerLinkAnalysis) -> dict:
    if job is None:
        return {
            "status": analysis.status,
            "job_status": "missing",
            "progress_percent": 100 if analysis.status in TERMINAL_ANALYSIS_STATUSES | {"failed"} else 0,
            "progress_stage": analysis.status,
            "progress_message": "وضعیت صف در دسترس نیست.",
            "attempt_count": 0,
            "max_attempts": 0,
            "next_run_at": None,
            "is_terminal": analysis.status in TERMINAL_ANALYSIS_STATUSES | {"failed"},
        }
    return {
        "status": analysis.status,
        "job_status": job.status,
        "job_status_label": job.get_status_display(),
        "progress_percent": int(job.progress_percent or 0),
        "progress_stage": job.progress_stage,
        "progress_message": job.progress_message,
        "attempt_count": int(job.attempt_count or 0),
        "max_attempts": int(job.max_attempts or 0),
        "attempts_remaining": job.attempts_remaining,
        "adapter_key": job.adapter_key,
        "queue_paused": queue_control().is_paused,
        "next_run_at": job.next_run_at.isoformat() if job.next_run_at else None,
        "last_error_type": job.last_error_type,
        "last_error": job.last_error if job.status == "failed" else "",
        "is_terminal": job.is_terminal,
    }
# END PHASE 24 ASYNC LINK ANALYSIS QUEUE
