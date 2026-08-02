from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import os

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import (
    CatalogAutomationSetting,
    CatalogQueuedJob,
    CatalogSyncRun,
    ExternalSourceFetchLog,
)

ACTIVE_SOURCE_STATUSES = {"queued", "running"}
ACTIVE_CATALOG_STATUSES = {"queued", "running"}
TERMINAL_SOURCE_STATUSES = {"success", "partial", "failed", "cancelled"}
TERMINAL_CATALOG_STATUSES = {"completed", "partial", "failed", "cancelled"}

SOURCE_TIMEOUT_RULES = {
    ("tgju", "test"): 5,
    ("tgju", "fetch_rate"): 5,
    ("bambu", "test"): 10,
    ("bambu", "sync"): 45,
    ("makerworld", "catalog_probe"): 15,
    ("printables", "catalog_probe"): 15,
    ("thingiverse", "catalog_probe"): 10,
    ("grabcad", "catalog_probe"): 10,
    ("makerworld", "sync"): 90,
    ("printables", "sync"): 90,
    ("thingiverse", "sync"): 45,
    ("grabcad", "sync"): 30,
}


class CatalogRunCancelled(RuntimeError):
    pass


class CatalogRunDeadlineExceeded(TimeoutError):
    pass


@dataclass(frozen=True)
class DeadlineState:
    active: bool
    stale: bool
    timeout_minutes: int
    deadline_at: object | None
    seconds_remaining: int | None
    label: str


def _positive_int(value, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def source_timeout_minutes(log: ExternalSourceFetchLog) -> int:
    configured = getattr(settings, "AUTOMATION_SOURCE_TIMEOUTS", {}) or {}
    specific_key = f"{log.source_key}:{log.action}"
    env_names = {
        "tgju:test": "AUTOMATION_TGJU_TEST_TIMEOUT_MINUTES",
        "tgju:fetch_rate": "AUTOMATION_TGJU_FETCH_TIMEOUT_MINUTES",
        "bambu:test": "AUTOMATION_BAMBU_TEST_TIMEOUT_MINUTES",
        "bambu:sync": "AUTOMATION_BAMBU_SYNC_TIMEOUT_MINUTES",
    }
    env_name = env_names.get(specific_key)
    if env_name and os.getenv(env_name):
        return _positive_int(os.getenv(env_name), 60)
    if log.action == "catalog_probe" and os.getenv("AUTOMATION_CATALOG_PROBE_TIMEOUT_MINUTES"):
        return _positive_int(os.getenv("AUTOMATION_CATALOG_PROBE_TIMEOUT_MINUTES"), 15)
    if specific_key in configured:
        return _positive_int(configured[specific_key], 60)
    if log.action in configured:
        return _positive_int(configured[log.action], 60)
    if log.source_key in configured:
        return _positive_int(configured[log.source_key], 60)
    if (log.source_key, log.action) in SOURCE_TIMEOUT_RULES:
        return SOURCE_TIMEOUT_RULES[(log.source_key, log.action)]
    return _positive_int(
        os.getenv(
            "AUTOMATION_SOURCE_TIMEOUT_MINUTES",
            getattr(settings, "AUTOMATION_SOURCE_TIMEOUT_MINUTES", 60),
        ),
        60,
    )


def catalog_timeout_minutes(run: CatalogSyncRun) -> int:
    setting = CatalogAutomationSetting.load()
    return _positive_int(
        os.getenv(
            "AUTOMATION_CATALOG_TIMEOUT_MINUTES",
            getattr(settings, "AUTOMATION_CATALOG_TIMEOUT_MINUTES", setting.stale_run_minutes),
        ),
        90,
    )


def catalog_queue_timeout_minutes() -> int:
    return _positive_int(
        os.getenv(
            "AUTOMATION_CATALOG_QUEUE_TIMEOUT_MINUTES",
            getattr(settings, "AUTOMATION_CATALOG_QUEUE_TIMEOUT_MINUTES", 45),
        ),
        45,
    )


def source_deadline(log: ExternalSourceFetchLog):
    if log.deadline_at:
        return log.deadline_at
    activity_at = log.heartbeat_at or log.updated_at or log.started_at or log.created_at
    return activity_at + timedelta(minutes=source_timeout_minutes(log))


def catalog_deadline(run: CatalogSyncRun):
    if run.deadline_at:
        return run.deadline_at
    if run.status == "queued":
        return run.created_at + timedelta(minutes=catalog_queue_timeout_minutes())
    activity_at = run.heartbeat_at or run.started_at or run.created_at
    return activity_at + timedelta(minutes=catalog_timeout_minutes(run))


def source_deadline_state(log: ExternalSourceFetchLog, *, now=None) -> DeadlineState:
    now = now or timezone.now()
    if log.status not in ACTIVE_SOURCE_STATUSES:
        return DeadlineState(False, False, 0, None, None, "terminal")
    deadline_at = source_deadline(log)
    remaining = int((deadline_at - now).total_seconds())
    stale = remaining <= 0
    return DeadlineState(
        True,
        stale,
        source_timeout_minutes(log),
        deadline_at,
        remaining,
        "expired" if stale else "active",
    )


def catalog_deadline_state(run: CatalogSyncRun, *, now=None) -> DeadlineState:
    now = now or timezone.now()
    if run.status not in ACTIVE_CATALOG_STATUSES:
        return DeadlineState(False, False, 0, None, None, "terminal")
    deadline_at = catalog_deadline(run)
    remaining = int((deadline_at - now).total_seconds())
    stale = remaining <= 0
    timeout = (
        catalog_queue_timeout_minutes()
        if run.status == "queued"
        else catalog_timeout_minutes(run)
    )
    return DeadlineState(
        True,
        stale,
        timeout,
        deadline_at,
        remaining,
        "expired" if stale else "active",
    )


def _source_duration_ms(log: ExternalSourceFetchLog, now) -> int:
    start = log.started_at or log.created_at or now
    return max(int((now - start).total_seconds() * 1000), 0)


def stop_source_log(
    log: ExternalSourceFetchLog,
    *,
    reason: str,
    actor=None,
    timeout: bool = False,
    now=None,
) -> bool:
    now = now or timezone.now()
    actor_label = ""
    if actor is not None and getattr(actor, "is_authenticated", False):
        actor_label = getattr(actor, "get_username", lambda: "")() or str(actor.pk)
    with transaction.atomic():
        locked = ExternalSourceFetchLog.objects.select_for_update().get(pk=log.pk)
        if locked.status not in ACTIVE_SOURCE_STATUSES:
            return False
        details = dict(locked.details or {})
        details["watchdog"] = {
            "reason": reason,
            "actor": actor_label,
            "stopped_at": now.isoformat(),
            "timeout": bool(timeout),
        }
        locked.status = "failed" if timeout else "cancelled"
        locked.progress_percent = 100
        locked.current_stage = "deadline_exceeded" if timeout else "cancelled_by_operator"
        locked.error = reason[:4000]
        locked.details = details
        locked.finished_at = now
        locked.cancelled_at = None if timeout else now
        locked.heartbeat_at = now
        locked.duration_ms = _source_duration_ms(locked, now)
        locked.save(
            update_fields=[
                "status",
                "progress_percent",
                "current_stage",
                "error",
                "details",
                "finished_at",
                "cancelled_at",
                "heartbeat_at",
                "duration_ms",
                "updated_at",
            ]
        )
    return True


def stop_catalog_run(
    run: CatalogSyncRun,
    *,
    reason: str,
    actor=None,
    timeout: bool = False,
    now=None,
) -> bool:
    now = now or timezone.now()
    actor_label = ""
    if actor is not None and getattr(actor, "is_authenticated", False):
        actor_label = getattr(actor, "get_username", lambda: "")() or str(actor.pk)
    with transaction.atomic():
        locked = CatalogSyncRun.objects.select_for_update().get(pk=run.pk)
        if locked.status not in ACTIVE_CATALOG_STATUSES:
            return False
        suffix = f"reason={reason}"
        if actor_label:
            suffix += f" actor={actor_label}"
        locked.status = "failed" if timeout else "cancelled"
        locked.finished_at = now
        locked.cancelled_at = None if timeout else now
        locked.heartbeat_at = now
        locked.log = "\n".join(
            item for item in [locked.log.strip(), f"[watchdog] {suffix}"] if item
        )[-12000:]
        locked.save(
            update_fields=[
                "status",
                "finished_at",
                "cancelled_at",
                "heartbeat_at",
                "log",
            ]
        )
        CatalogQueuedJob.objects.filter(run=locked).update(claimed_at=None)
    return True


def initialize_catalog_run_deadline(run: CatalogSyncRun, *, now=None) -> CatalogSyncRun:
    now = now or timezone.now()
    run.deadline_at = now + timedelta(minutes=catalog_timeout_minutes(run))
    run.heartbeat_at = now
    return run


def touch_catalog_run(run: CatalogSyncRun, *, now=None, update_fields=None) -> CatalogSyncRun:
    now = now or timezone.now()
    state = CatalogSyncRun.objects.filter(pk=run.pk).values(
        "status", "cancelled_at", "deadline_at"
    ).first()
    if state is None:
        raise CatalogRunCancelled("Catalog sync run no longer exists.")
    if state["status"] == "cancelled" or state["cancelled_at"]:
        raise CatalogRunCancelled("Catalog sync run was cancelled by an operator.")
    deadline_at = state["deadline_at"] or catalog_deadline(run)
    if deadline_at and deadline_at <= now:
        raise CatalogRunDeadlineExceeded(
            f"Catalog sync deadline exceeded at {deadline_at.isoformat()}."
        )
    run.heartbeat_at = now
    fields = list(update_fields or [])
    if "heartbeat_at" not in fields:
        fields.append("heartbeat_at")
    run.save(update_fields=fields)
    return run


def expire_stale_automation(*, now=None, actor=None, dry_run=False) -> dict:
    now = now or timezone.now()
    source_candidates = list(
        ExternalSourceFetchLog.objects.filter(status__in=ACTIVE_SOURCE_STATUSES)
        .order_by("created_at", "id")
    )
    catalog_candidates = list(
        CatalogSyncRun.objects.filter(status__in=ACTIVE_CATALOG_STATUSES)
        .order_by("created_at", "id")
    )
    stale_sources = [item for item in source_candidates if source_deadline_state(item, now=now).stale]
    stale_catalog = [item for item in catalog_candidates if catalog_deadline_state(item, now=now).stale]
    stopped_sources = 0
    stopped_catalog = 0
    if not dry_run:
        for item in stale_sources:
            state = source_deadline_state(item, now=now)
            if stop_source_log(
                item,
                reason=(
                    f"AutomationDeadlineExceeded: no heartbeat before "
                    f"{state.deadline_at.isoformat()} ({state.timeout_minutes} minutes)."
                ),
                actor=actor,
                timeout=True,
                now=now,
            ):
                stopped_sources += 1
        for item in stale_catalog:
            state = catalog_deadline_state(item, now=now)
            if stop_catalog_run(
                item,
                reason=(
                    f"AutomationDeadlineExceeded: run exceeded "
                    f"{state.timeout_minutes} minutes."
                ),
                actor=actor,
                timeout=True,
                now=now,
            ):
                stopped_catalog += 1
    return {
        "source_active": len(source_candidates),
        "catalog_active": len(catalog_candidates),
        "source_stale": len(stale_sources),
        "catalog_stale": len(stale_catalog),
        "source_stopped": stopped_sources,
        "catalog_stopped": stopped_catalog,
        "dry_run": bool(dry_run),
    }
