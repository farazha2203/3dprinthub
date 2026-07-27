from __future__ import annotations

import os
import socket
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlsplit

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, Q
from django.urls import reverse
from django.utils import timezone

from .models import (
    CustomerLinkAnalysis,
    CustomerLinkAnalysisAttempt,
    CustomerLinkAnalysisJob,
    LinkAnalysisAdapterPolicy,
    LinkAnalysisQueueControl,
    LinkAnalysisWorkerHeartbeat,
    LinkAnalysisManualReview,
)
from .services import notify

PHASE25_VERSION = "25.0"


def _publish_operations() -> None:
    try:
        from .realtime import publish_operations
        publish_operations()
    except Exception:
        pass

DIRECT_FILE_EXTENSIONS = {
    ".stl", ".3mf", ".step", ".stp", ".obj", ".iges", ".igs", ".ply", ".amf", ".gcode"
}
DEFAULT_ADAPTERS = {
    "makerworld": {"display_name": "MakerWorld", "domain_patterns": ["makerworld.com"]},
    "printables": {"display_name": "Printables", "domain_patterns": ["printables.com"]},
    "thingiverse": {"display_name": "Thingiverse", "domain_patterns": ["thingiverse.com"]},
    "grabcad": {"display_name": "GrabCAD", "domain_patterns": ["grabcad.com"]},
    "direct_file": {"display_name": "لینک مستقیم فایل", "domain_patterns": []},
    "generic": {"display_name": "تحلیل عمومی وب", "domain_patterns": []},
}


def queue_control() -> LinkAnalysisQueueControl:
    return LinkAnalysisQueueControl.load()


def ensure_adapter_policies() -> dict[str, LinkAnalysisAdapterPolicy]:
    result = {}
    for key, defaults in DEFAULT_ADAPTERS.items():
        policy, _ = LinkAnalysisAdapterPolicy.objects.get_or_create(
            adapter_key=key,
            defaults={
                **defaults,
                "retry_delays_seconds": [30, 120, 600, 1800],
                "max_attempts": 4 if key not in {"direct_file", "grabcad"} else (2 if key == "direct_file" else 3),
                "request_timeout_seconds": 20 if key == "generic" else 25,
            },
        )
        result[key] = policy
    return result


def resolve_adapter_key(*, source_url: str = "", source_domain: str = "") -> str:
    source_url = str(source_url or "").strip()
    domain = str(source_domain or "").lower().strip().removeprefix("www.")
    if not domain and source_url:
        domain = (urlsplit(source_url).hostname or "").lower().removeprefix("www.")
    path = (urlsplit(source_url).path or "").lower()
    if Path(path).suffix.lower() in DIRECT_FILE_EXTENSIONS:
        return "direct_file"
    policies = ensure_adapter_policies()
    for key in ("makerworld", "printables", "thingiverse", "grabcad"):
        policy = policies[key]
        patterns = list(policy.domain_patterns or DEFAULT_ADAPTERS[key]["domain_patterns"])
        if any(domain == pattern or domain.endswith("." + pattern) for pattern in patterns if pattern):
            return key
    return "generic"


def policy_for_analysis(analysis: CustomerLinkAnalysis) -> LinkAnalysisAdapterPolicy:
    key = resolve_adapter_key(
        source_url=analysis.normalized_url or analysis.source_url,
        source_domain=analysis.source_domain,
    )
    return ensure_adapter_policies().get(key) or LinkAnalysisAdapterPolicy.objects.get(adapter_key="generic")


def policy_for_job(job: CustomerLinkAnalysisJob) -> LinkAnalysisAdapterPolicy:
    policies = ensure_adapter_policies()
    return policies.get(job.adapter_key) or policy_for_analysis(job.analysis)


def retry_delay_for_policy(policy: LinkAnalysisAdapterPolicy, attempt_number: int) -> int:
    delays = [int(item) for item in (policy.retry_delays_seconds or []) if str(item).isdigit() and int(item) >= 0]
    if not delays:
        delays = [30, 120, 600, 1800]
    index = max(min(int(attempt_number or 1) - 1, len(delays) - 1), 0)
    return delays[index]


def adapter_is_available(policy: LinkAnalysisAdapterPolicy, *, now=None) -> bool:
    now = now or timezone.now()
    return bool(policy.is_enabled and (policy.paused_until is None or policy.paused_until <= now))


def register_worker(worker_id: str, *, metadata: dict | None = None) -> LinkAnalysisWorkerHeartbeat:
    now = timezone.now()
    defaults = {
        "hostname": socket.gethostname()[:180],
        "process_id": os.getpid(),
        "status": "starting",
        "started_at": now,
        "last_seen_at": now,
        "stopped_at": None,
        "last_error": "",
        "worker_version": PHASE25_VERSION,
        "metadata": metadata or {},
    }
    heartbeat, created = LinkAnalysisWorkerHeartbeat.objects.get_or_create(worker_id=worker_id[:180], defaults=defaults)
    if not created:
        for key, value in defaults.items():
            setattr(heartbeat, key, value)
        heartbeat.current_job = None
        heartbeat.save()
    _publish_operations()
    return heartbeat


def touch_worker(
    heartbeat: LinkAnalysisWorkerHeartbeat,
    *,
    status: str,
    current_job: CustomerLinkAnalysisJob | None = None,
    loop_increment: int = 0,
    processed_increment: int = 0,
    succeeded_increment: int = 0,
    failed_increment: int = 0,
    last_error: str | None = None,
) -> LinkAnalysisWorkerHeartbeat:
    now = timezone.now()
    updates = {
        "status": status,
        "current_job": current_job,
        "last_seen_at": now,
        "process_id": os.getpid(),
        "hostname": socket.gethostname()[:180],
        "worker_version": PHASE25_VERSION,
    }
    if last_error is not None:
        updates["last_error"] = str(last_error)
    with transaction.atomic():
        row = LinkAnalysisWorkerHeartbeat.objects.select_for_update().get(pk=heartbeat.pk)
        for key, value in updates.items():
            setattr(row, key, value)
        row.loop_count += max(int(loop_increment), 0)
        row.processed_count += max(int(processed_increment), 0)
        row.succeeded_count += max(int(succeeded_increment), 0)
        row.failed_count += max(int(failed_increment), 0)
        row.stopped_at = now if status in {"stopped", "error"} else None
        row.save()
    heartbeat.refresh_from_db()
    _publish_operations()
    return heartbeat


def mark_worker_stopped(heartbeat: LinkAnalysisWorkerHeartbeat, *, error: str = "") -> None:
    touch_worker(heartbeat, status="error" if error else "stopped", current_job=None, last_error=error)


def worker_is_alive(worker: LinkAnalysisWorkerHeartbeat, *, control: LinkAnalysisQueueControl | None = None) -> bool:
    control = control or queue_control()
    timeout = max(int(control.heartbeat_timeout_seconds or 90), 15)
    cutoff = timezone.now() - timedelta(seconds=timeout)
    return worker.status in {"starting", "idle", "running"} and worker.last_seen_at >= cutoff


def mark_stale_workers() -> int:
    control = queue_control()
    cutoff = timezone.now() - timedelta(seconds=max(int(control.heartbeat_timeout_seconds or 90), 15))
    count = LinkAnalysisWorkerHeartbeat.objects.filter(
        status__in=["starting", "idle", "running"],
        last_seen_at__lt=cutoff,
    ).update(status="error", stopped_at=timezone.now(), last_error="Heartbeat Worker منقضی شد.", current_job=None)
    if count:
        _publish_operations()
    return count


def _analysis_url(analysis: CustomerLinkAnalysis) -> str:
    try:
        return reverse("store:external_link_analysis", args=[analysis.public_token])
    except Exception:
        return f"/store/link-analyzer/{analysis.public_token}/"


def _send_email(user, subject: str, message: str) -> bool:
    email = str(getattr(user, "email", "") or "").strip()
    if not email:
        return False
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@3dprinthub.ir")
    try:
        return bool(send_mail(subject, message, from_email, [email], fail_silently=True))
    except Exception:
        return False


def notify_job_outcome(job: CustomerLinkAnalysisJob, *, success: bool) -> bool:
    job = CustomerLinkAnalysisJob.objects.select_related("analysis", "analysis__user").get(pk=job.pk)
    analysis = job.analysis
    user = analysis.user
    if user is None:
        return False
    control = queue_control()
    policy = policy_for_job(job)
    now = timezone.now()
    url = _analysis_url(analysis)
    if success:
        if job.success_notified_at:
            return False
        title = "تحلیل لینک شما آماده شد"
        message = f"اطلاعات «{analysis.title or analysis.source_name or 'محصول'}» استخراج شد و برای برآورد قیمت آماده است."
        should_notify = control.notify_customer_on_success and policy.notify_on_success
        should_email = control.email_customer_on_success
        if should_notify:
            notify(user, title, message, notification_type="system", url=url)
        if should_email:
            _send_email(user, title, message)
        CustomerLinkAnalysisJob.objects.filter(pk=job.pk, success_notified_at__isnull=True).update(success_notified_at=now)
        return should_notify or should_email
    if job.failure_notified_at:
        return False
    title = "تحلیل لینک نیازمند بررسی است"
    message = "تحلیل خودکار لینک پس از چند تلاش کامل نشد. لینک و اطلاعات ثبت شده‌اند و می‌توانید دوباره تلاش کنید یا برای بررسی دستی ارسال کنید."
    should_notify = control.notify_customer_on_failure and policy.notify_on_failure
    should_email = control.email_customer_on_failure
    if should_notify:
        notify(user, title, message, notification_type="system", url=url)
    if should_email:
        _send_email(user, title, message)
    CustomerLinkAnalysisJob.objects.filter(pk=job.pk, failure_notified_at__isnull=True).update(failure_notified_at=now)
    return should_notify or should_email


def record_adapter_outcome(policy: LinkAnalysisAdapterPolicy, *, success: bool, error: str = "") -> None:
    now = timezone.now()
    with transaction.atomic():
        row = LinkAnalysisAdapterPolicy.objects.select_for_update().get(pk=policy.pk)
        if success:
            row.success_count += 1
            row.consecutive_failure_count = 0
            row.last_success_at = now
            row.last_error = ""
        else:
            row.failure_count += 1
            row.consecutive_failure_count += 1
            row.last_failure_at = now
            row.last_error = str(error)[:5000]
        row.save(update_fields=[
            "success_count", "failure_count", "consecutive_failure_count",
            "last_success_at", "last_failure_at", "last_error", "updated_at",
        ])


def queue_metrics() -> dict:
    now = timezone.now()
    control = queue_control()
    mark_stale_workers()
    counts = dict(CustomerLinkAnalysisJob.objects.values("status").annotate(total=Count("id")).values_list("status", "total"))
    oldest = CustomerLinkAnalysisJob.objects.filter(status__in=["queued", "retry"]).order_by("next_run_at", "id").first()
    workers = list(LinkAnalysisWorkerHeartbeat.objects.select_related("current_job").order_by("-last_seen_at")[:20])
    active_workers = sum(1 for worker in workers if worker_is_alive(worker, control=control))
    recent_attempts = CustomerLinkAnalysisAttempt.objects.filter(started_at__gte=now - timedelta(hours=24))
    attempts = dict(recent_attempts.values("status").annotate(total=Count("id")).values_list("status", "total"))
    return {
        "control": control,
        "counts": counts,
        "queued": counts.get("queued", 0),
        "running": counts.get("running", 0),
        "retry": counts.get("retry", 0),
        "completed": counts.get("completed", 0),
        "failed": counts.get("failed", 0),
        "cancelled": counts.get("cancelled", 0),
        "oldest_job": oldest,
        "oldest_wait_seconds": max(int((now - oldest.next_run_at).total_seconds()), 0) if oldest and oldest.next_run_at <= now else 0,
        "workers": workers,
        "active_workers": active_workers,
        "attempts_24h": attempts,
        "success_24h": attempts.get("success", 0),
        "failure_24h": attempts.get("transient_failure", 0) + attempts.get("permanent_failure", 0),
        "policies": LinkAnalysisAdapterPolicy.objects.order_by("adapter_key"),
        "recent_jobs": CustomerLinkAnalysisJob.objects.select_related("analysis", "analysis__user").order_by("-updated_at")[:20],
        "recent_attempts": CustomerLinkAnalysisAttempt.objects.select_related("job", "job__analysis").order_by("-started_at")[:20],
        "manual_review_pending": LinkAnalysisManualReview.objects.filter(status="pending").count(),
        "manual_review_in_progress": LinkAnalysisManualReview.objects.filter(status="in_progress").count(),
        "recent_manual_reviews": LinkAnalysisManualReview.objects.select_related(
            "analysis", "analysis__user", "assigned_to"
        ).order_by("-priority", "requested_at")[:15],
    }


def health_payload() -> tuple[dict, int]:
    metrics = queue_metrics()
    control = metrics["control"]
    healthy = bool(metrics["active_workers"] > 0 or (control.is_paused and metrics["running"] == 0))
    degraded = bool(metrics["failed"] or metrics["oldest_wait_seconds"] > 300)
    status = "paused" if control.is_paused else ("healthy" if healthy and not degraded else "degraded")
    code = 200 if healthy else 503
    return {
        "status": status,
        "queue_paused": control.is_paused,
        "active_workers": metrics["active_workers"],
        "queued": metrics["queued"],
        "running": metrics["running"],
        "retry": metrics["retry"],
        "failed": metrics["failed"],
        "oldest_wait_seconds": metrics["oldest_wait_seconds"],
        "timestamp": timezone.now().isoformat(),
        "version": PHASE25_VERSION,
    }, code
