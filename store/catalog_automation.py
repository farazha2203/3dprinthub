from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .catalog_sync import approve_asset_for_public, public_catalog_queryset, sync_catalog_source
from .automation_watchdog import expire_stale_automation
from .models import (
    CatalogAssetMetrics,
    CatalogAssetPublication,
    CatalogAutomationSetting,
    CatalogQueuedJob,
    CatalogSourceSchedule,
    CatalogSyncRun,
)


def external_model_sync_enabled() -> bool:
    """Phase 49.2A kill-switch for legacy external model ingestion.

    Windows Catalog Center remains the canonical product publishing path. This
    switch only controls the legacy external-model scheduler/worker; material
    reference pricing and FX services are separate and remain available.
    """
    return bool(getattr(settings, "EXTERNAL_MODEL_SYNC_ENABLED", False))


def _local_now(setting: CatalogAutomationSetting, now=None):
    now = now or timezone.now()
    try:
        zone = ZoneInfo(setting.timezone_name)
    except ZoneInfoNotFoundError:
        zone = ZoneInfo("Asia/Tehran")
    return now.astimezone(zone)


def queue_catalog_source(*, schedule: CatalogSourceSchedule, actor=None, trigger="manual", scheduled_for=None):
    if not external_model_sync_enabled():
        raise ValidationError(
            "دریافت مدل از منابع خارجی در Phase 49.2A غیرفعال است؛ انتشار محصول فقط از Catalog Center ویندوز انجام می‌شود."
        )
    if not schedule.policy.is_active or not schedule.policy.source.is_active:
        raise ValidationError("منبع یا سیاست دریافت غیرفعال است.")
    duplicate = CatalogSyncRun.objects.filter(
        source=schedule.policy.source,
        status__in=["queued", "running"],
    ).exists()
    if duplicate:
        raise ValidationError("برای این منبع یک اجرا در صف یا در حال اجرا وجود دارد.")
    limit = schedule.policy.clamp_limit(schedule.requested_limit)
    run = CatalogSyncRun.objects.create(
        source=schedule.policy.source,
        sort_mode=schedule.sort_mode,
        requested_limit=limit,
        status="queued",
        requested_by=actor,
        log="در صف پردازش",
    )
    CatalogQueuedJob.objects.create(
        run=run,
        trigger=trigger,
        scheduled_for=scheduled_for,
        hydrate_files=schedule.hydrate_files,
    )
    return run


def queue_due_catalog_sources(*, now=None):
    if not external_model_sync_enabled():
        return []
    setting = CatalogAutomationSetting.load()
    if not setting.queue_enabled:
        return []
    local_now = _local_now(setting, now)
    today = local_now.date()
    queued = []
    for schedule in CatalogSourceSchedule.objects.select_related("policy", "policy__source").filter(enabled=True):
        if local_now.weekday() not in schedule.active_weekdays():
            continue
        if schedule.last_queued_on == today:
            continue
        scheduled_dt = datetime.combine(today, schedule.run_time, tzinfo=local_now.tzinfo)
        if local_now < scheduled_dt:
            continue
        try:
            run = queue_catalog_source(
                schedule=schedule,
                trigger="scheduled",
                scheduled_for=scheduled_dt.astimezone(timezone.get_current_timezone()),
            )
        except ValidationError:
            continue
        schedule.last_queued_on = today
        schedule.save(update_fields=["last_queued_on", "updated_at"])
        queued.append(run)
    setting.last_queue_scan_at = timezone.now()
    setting.save(update_fields=["last_queue_scan_at", "updated_at"])
    return queued


def _publication_for(metrics: CatalogAssetMetrics, *, show_on_homepage=False):
    publication, _ = CatalogAssetPublication.objects.get_or_create(metrics=metrics)
    changed = False
    if show_on_homepage and not publication.show_on_homepage:
        publication.show_on_homepage = True
        changed = True
    if metrics.public_approved and not publication.first_published_at:
        publication.first_published_at = timezone.now()
        changed = True
    publication.last_public_refresh_at = timezone.now()
    publication.ensure_defaults()
    changed = True
    if changed:
        publication.save()
    return publication


def postprocess_sync_run(run: CatalogSyncRun, schedule: CatalogSourceSchedule | None):
    if not run.started_at:
        return
    queryset = CatalogAssetMetrics.objects.select_related("asset", "asset__source").filter(
        asset__source=run.source,
        last_synced_at__gte=run.started_at - timedelta(minutes=2),
    )
    for metrics in queryset:
        if (
            schedule
            and schedule.auto_approve_commercial
            and metrics.commercial_use_allowed is True
            and metrics.license_review_status == "allowed"
            and metrics.source_kind != "grabcad"
        ):
            try:
                approve_asset_for_public(
                    metrics.asset,
                    cache_images=schedule.cache_images_after_approval,
                    create_product=False,
                )
                metrics.refresh_from_db()
            except Exception:
                pass
        if metrics.public_approved and metrics.commercial_use_allowed is True and metrics.license_review_status == "allowed":
            _publication_for(metrics, show_on_homepage=bool(schedule and schedule.show_approved_on_homepage))
    if schedule and run.status in ["completed", "partial"]:
        schedule.last_completed_at = timezone.now()
        schedule.save(update_fields=["last_completed_at", "updated_at"])


def reset_stale_catalog_runs(*, now=None):
    summary = expire_stale_automation(now=now)
    return int(summary.get("catalog_stopped") or 0)


def process_catalog_queue(*, limit=None):
    if not external_model_sync_enabled():
        return []
    setting = CatalogAutomationSetting.load()
    limit = int(limit or setting.process_batch_size or 1)
    processed = []
    reset_stale_catalog_runs()
    for _ in range(max(limit, 1)):
        with transaction.atomic():
            job = (
                CatalogQueuedJob.objects.select_for_update()
                .select_related("run", "run__source")
                .filter(run__status="queued")
                .order_by("created_at")
                .first()
            )
            if not job:
                break
            job.attempts += 1
            job.claimed_at = timezone.now()
            job.save(update_fields=["attempts", "claimed_at"])
            run = job.run
            run.status = "running"
            run.started_at = timezone.now()
            run.log = "Worker اجرا را دریافت کرد."
            run.save(update_fields=["status", "started_at", "log"])
        try:
            schedule = getattr(run.source.sync_policy, "schedule", None)
            run = sync_catalog_source(
                source=run.source,
                requested_limit=run.requested_limit,
                sort_mode=run.sort_mode,
                actor=run.requested_by,
                hydrate_files=job.hydrate_files,
                sync_run=run,
            )
            postprocess_sync_run(run, schedule)
        except Exception as exc:
            run.refresh_from_db()
            if run.status != "cancelled":
                run.status = "failed"
                run.finished_at = timezone.now()
                run.heartbeat_at = run.finished_at
                run.log = f"{type(exc).__name__}: {exc}"
                run.save(update_fields=["status", "finished_at", "heartbeat_at", "log"])
        processed.append(run)
    return processed


def homepage_catalog_assets(*, slider=False, limit=None):
    """Return legacy public references only when external model sync is enabled."""
    from django.db.models import Q

    if not external_model_sync_enabled():
        return public_catalog_queryset().none()

    setting = CatalogAutomationSetting.load()
    limit = max(1, min(int(limit or (setting.homepage_slider_count if slider else setting.homepage_grid_count)), 60))
    queryset = public_catalog_queryset().select_related("metrics__publication", "source")
    if slider:
        queryset = queryset.filter(
            (Q(preview_image__isnull=False) & ~Q(preview_image=""))
            | ~Q(remote_image_url="")
            | ~Q(metrics__image_urls=[])
        )
    return queryset.order_by(
        "source_priority_order",
        "metrics__popularity_rank",
        "-metrics__downloads_count",
        "-imported_at",
    )[:limit]
