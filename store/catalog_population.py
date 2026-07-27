from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Iterable
from urllib.parse import quote_plus, urljoin

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .catalog_automation import _publication_for
from .catalog_site_adapters import get_source_adapter
from .catalog_site_adapters.common import CatalogCandidate, link_discovery, robots_allowed
from .catalog_sync import approve_asset_for_public, save_external_record
from .models import (
    CatalogAssetMetrics,
    CatalogSourcePolicy,
    CatalogSourceSchedule,
    CatalogSyncRun,
    ImportedPrintAsset,
    PrintCatalogSource,
)
from .source_monitoring import source_log, update_log


PUBLIC_SOURCE_KEYS = ("makerworld", "printables")
DEFAULT_SORT_MODES = ("views", "downloads", "likes", "trending")

# These are ordinary public listing/search pages. The importer never bypasses
# login, CAPTCHA, robots.txt or platform protection.
COMMERCIAL_DISCOVERY_URLS = {
    "makerworld": (
        "https://makerworld.com/en/3d-models?keyword=commercial%20use&orderBy=downloadCount&page={page}",
        "https://makerworld.com/en/3d-models?keyword=cc0&orderBy=downloadCount&page={page}",
        "https://makerworld.com/en/collections/3980491-commercial-use",
    ),
    "printables": (
        "https://www.printables.com/search/models?q=commercial%20use&page={page}",
        "https://www.printables.com/search/models?q=cc0&page={page}",
        "https://www.printables.com/search/models?q=cc%20by&page={page}",
    ),
}


@dataclass
class SourcePopulationResult:
    source_key: str
    discovered: int = 0
    imported: int = 0
    updated: int = 0
    failed: int = 0
    allowed: int = 0
    published: int = 0
    images_cached: int = 0
    runs: list[int] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def as_dict(self):
        return {
            "source": self.source_key,
            "discovered": self.discovered,
            "imported": self.imported,
            "updated": self.updated,
            "failed": self.failed,
            "allowed": self.allowed,
            "published": self.published,
            "images_cached": self.images_cached,
            "runs": self.runs,
            "errors": self.errors[-20:],
        }


def configure_population_schedule(policy: CatalogSourcePolicy, *, requested_limit: int) -> CatalogSourceSchedule:
    schedule, _ = CatalogSourceSchedule.objects.get_or_create(policy=policy)
    schedule.enabled = True
    schedule.requested_limit = policy.clamp_limit(requested_limit)
    schedule.hydrate_files = True
    schedule.auto_approve_commercial = True
    schedule.cache_images_after_approval = True
    schedule.show_approved_on_homepage = True
    schedule.save()
    return schedule


def _candidate_key(candidate: CatalogCandidate) -> str:
    return (candidate.url or "").split("?", 1)[0].rstrip("/")


def _merge_candidates(target: OrderedDict[str, CatalogCandidate], candidates: Iterable[CatalogCandidate], limit: int):
    for candidate in candidates:
        key = _candidate_key(candidate)
        if not key or key in target:
            continue
        target[key] = CatalogCandidate(
            url=key,
            external_id=candidate.external_id,
            summary=candidate.summary or {},
        )
        if len(target) >= limit:
            break


def _discover_from_url(adapter, url: str, limit: int) -> list[CatalogCandidate]:
    adapter.assert_url_allowed(url)
    if adapter.source.respect_robots_txt and not robots_allowed(
        url,
        timeout=adapter.source.request_timeout_seconds,
    ):
        return []
    raw_html = adapter.client.fetch_text(url)
    candidates = link_discovery(raw_html, adapter.source.base_url, adapter.model_link_pattern, limit)
    decoded = raw_html.replace("\\/", "/")
    for match in adapter.model_link_pattern.finditer(decoded):
        path = match.group(0)
        if not path.startswith("/"):
            continue
        candidates.append(
            CatalogCandidate(
                url=urljoin(adapter.source.base_url, path),
                external_id=match.group(1),
            )
        )
    return candidates


def discover_population_candidates(adapter, *, source_key: str, limit: int, sort_modes=DEFAULT_SORT_MODES):
    output: OrderedDict[str, CatalogCandidate] = OrderedDict()
    errors: list[str] = []

    # First use the normal adapter discovery in multiple rankings.
    for sort_mode in sort_modes:
        if len(output) >= limit:
            break
        try:
            found = adapter.discover(limit=limit - len(output), sort_mode=sort_mode)
            _merge_candidates(output, found, limit)
        except Exception as exc:
            errors.append(f"{sort_mode}: {type(exc).__name__}: {exc}")

    # Then target public search pages that are more likely to contain
    # explicitly commercial Creative Commons models.
    pages = max(1, min(8, (limit // 20) + 1))
    for template in COMMERCIAL_DISCOVERY_URLS.get(source_key, ()):
        if len(output) >= limit:
            break
        for page in range(1, pages + 1):
            if len(output) >= limit:
                break
            url = template.format(page=page, keyword=quote_plus("commercial use"))
            try:
                found = _discover_from_url(adapter, url, limit - len(output))
                _merge_candidates(output, found, limit)
            except Exception as exc:
                errors.append(f"{url}: {type(exc).__name__}: {exc}")
                break

    return list(output.values())[:limit], errors


def _mark_source_file_availability(asset: ImportedPrintAsset, parsed: dict) -> None:
    specs = dict(asset.technical_specs or {})
    explicit_links = parsed.get("file_links") or []
    explicit_formats = parsed.get("file_formats") or []
    # Public model pages on MakerWorld/Printables represent downloadable model
    # records. The source page remains an admin-only acquisition reference when
    # no direct file URL is exposed in HTML.
    source_available = bool(
        explicit_links
        or explicit_formats
        or parsed.get("source_file_available")
        or (
            asset.source.adapter_key in {"makerworld", "printables"}
            and parsed.get("images")
        )
    )
    if specs.get("source_file_available") != source_available:
        specs["source_file_available"] = source_available
        specs["source_file_reference"] = asset.source_url if source_available else ""
        asset.technical_specs = specs
        asset.save(update_fields=["technical_specs", "updated_at"])


def _publish_eligible_for_source(
    source: PrintCatalogSource,
    *,
    publish_limit: int,
    actor=None,
) -> tuple[int, int, list[str]]:
    published = 0
    images_cached = 0
    errors: list[str] = []
    queryset = (
        CatalogAssetMetrics.objects.select_related("asset", "asset__source")
        .filter(
            asset__source=source,
            commercial_use_allowed=True,
            license_review_status="allowed",
        )
        .exclude(source_kind="grabcad")
        .order_by("public_approved", "-views_count", "-downloads_count", "-likes_count", "popularity_rank", "id")
    )
    for metrics in queryset[: max(1, int(publish_limit))]:
        asset = metrics.asset
        if not (asset.remote_image_url or metrics.image_urls or asset.preview_image):
            continue
        before_image = bool(asset.preview_image)
        try:
            approve_asset_for_public(
                asset,
                actor=actor,
                create_product=False,
                cache_images=True,
            )
            metrics.refresh_from_db()
            asset.refresh_from_db()
            publication = _publication_for(metrics, show_on_homepage=True)
            if not publication.show_on_homepage:
                publication.show_on_homepage = True
                publication.save(update_fields=["show_on_homepage", "updated_at"])
            published += 1
            if not before_image and asset.preview_image:
                images_cached += 1
        except Exception as exc:
            errors.append(f"{asset.source_url}: {type(exc).__name__}: {exc}")
    return published, images_cached, errors


def populate_source(
    source_key: str,
    *,
    limit: int = 80,
    publish_limit: int = 60,
    actor=None,
    delay_ms: int | None = None,
) -> SourcePopulationResult:
    if source_key not in PUBLIC_SOURCE_KEYS:
        raise ValidationError("پر کردن عمومی فقط برای MakerWorld و Printables فعال است.")

    policy = CatalogSourcePolicy.objects.select_related("source").get(source_kind=source_key)
    source = policy.source
    if not source.is_active or not policy.is_active:
        raise ValidationError(f"منبع {source.name} غیرفعال است.")
    schedule = configure_population_schedule(policy, requested_limit=limit)
    adapter = get_source_adapter(source, policy)
    result = SourcePopulationResult(source_key=source_key)

    with source_log(
        source_key=source_key,
        action="sync",
        actor=actor,
        message="دریافت واقعی، ذخیره تصویر و انتشار کاتالوگ",
    ) as log:
        update_log(log, stage="کشف فهرست‌های عمومی", progress=5)
        candidates, discovery_errors = discover_population_candidates(
            adapter,
            source_key=source_key,
            limit=policy.clamp_limit(limit),
        )
        result.discovered = len(candidates)
        result.errors.extend(discovery_errors)
        update_log(
            log,
            stage="دریافت جزئیات مدل‌ها",
            progress=15,
            records_found=result.discovered,
            details={"discovery_errors": discovery_errors[-10:]},
        )
        if not candidates:
            raise ValidationError(
                f"هیچ مدل عمومی از {source.name} کشف نشد؛ دسترسی فهرست یا لینک‌های بذر را بررسی کنید."
            )

        run = CatalogSyncRun.objects.create(
            source=source,
            sort_mode="views",
            requested_limit=len(candidates),
            status="running",
            requested_by=actor if getattr(actor, "is_authenticated", False) else None,
            discovered_count=len(candidates),
            started_at=timezone.now(),
            log="شروع پر کردن واقعی کاتالوگ",
        )
        result.runs.append(run.pk)
        sleep_seconds = max(0, int(delay_ms if delay_ms is not None else policy.request_delay_ms)) / 1000

        for index, candidate in enumerate(candidates, start=1):
            try:
                existed = ImportedPrintAsset.objects.filter(
                    source=source,
                    source_url=_candidate_key(candidate),
                ).exists()
                parsed = adapter.fetch_record(candidate, hydrate_files=True)
                asset, metrics = save_external_record(
                    source=source,
                    policy=policy,
                    parsed=parsed,
                    rank=index,
                )
                _mark_source_file_availability(asset, parsed)
                if existed:
                    result.updated += 1
                else:
                    result.imported += 1
                if metrics.commercial_use_allowed is True and metrics.license_review_status == "allowed":
                    result.allowed += 1
            except Exception as exc:
                result.failed += 1
                result.errors.append(f"{candidate.url}: {type(exc).__name__}: {exc}")

            progress = 15 + int((index / max(len(candidates), 1)) * 60)
            update_log(
                log,
                stage=f"مدل {index} از {len(candidates)}",
                progress=min(progress, 75),
                records_found=result.discovered,
                records_saved=result.imported,
                records_updated=result.updated,
                records_failed=result.failed,
                message=f"مجاز تشخیص داده‌شده: {result.allowed}",
            )
            if sleep_seconds and index < len(candidates):
                time.sleep(sleep_seconds)

        update_log(log, stage="تأیید مجوز و ذخیره تصاویر", progress=80)
        published, cached, publish_errors = _publish_eligible_for_source(
            source,
            publish_limit=publish_limit,
            actor=actor,
        )
        result.published = published
        result.images_cached = cached
        result.errors.extend(publish_errors)

        run.imported_count = result.imported + result.updated
        run.failed_count = result.failed
        run.status = "completed" if not result.errors else ("partial" if run.imported_count else "failed")
        run.finished_at = timezone.now()
        run.log = "\n".join(result.errors[-100:]) or "بدون خطا"
        run.save(
            update_fields=[
                "imported_count",
                "failed_count",
                "status",
                "finished_at",
                "log",
            ]
        )
        policy.last_synced_at = run.finished_at
        policy.save(update_fields=["last_synced_at", "updated_at"])
        schedule.last_completed_at = run.finished_at
        schedule.save(update_fields=["last_completed_at", "updated_at"])

        final_status = "success" if result.published else "partial"
        update_log(
            log,
            stage="انتشار عمومی",
            progress=100,
            status=final_status,
            records_found=result.discovered,
            records_saved=result.imported,
            records_updated=result.updated,
            records_failed=result.failed,
            message=(
                f"{result.imported} مدل جدید، {result.updated} بروزرسانی، "
                f"{result.allowed} مجاز و {result.published} مدل منتشر شد."
            ),
            details=result.as_dict(),
        )
    return result


def populate_ready_catalog(
    *,
    source_keys: Iterable[str] = PUBLIC_SOURCE_KEYS,
    limit_per_source: int = 80,
    publish_limit_per_source: int = 60,
    actor=None,
    delay_ms: int | None = None,
):
    results = []
    for source_key in source_keys:
        results.append(
            populate_source(
                source_key,
                limit=limit_per_source,
                publish_limit=publish_limit_per_source,
                actor=actor,
                delay_ms=delay_ms,
            )
        )
    return results


def catalog_population_counts():
    return {
        "all_imported": ImportedPrintAsset.objects.count(),
        "makerworld": ImportedPrintAsset.objects.filter(metrics__source_kind="makerworld").count(),
        "printables": ImportedPrintAsset.objects.filter(metrics__source_kind="printables").count(),
        "allowed": CatalogAssetMetrics.objects.filter(
            commercial_use_allowed=True,
            license_review_status="allowed",
        ).count(),
        "public": CatalogAssetMetrics.objects.filter(public_approved=True).count(),
        "public_with_image": CatalogAssetMetrics.objects.filter(
            public_approved=True,
            asset__preview_image__isnull=False,
        ).exclude(asset__preview_image="").count(),
    }


def publish_existing_catalog(*, publish_limit_per_source: int = 200, actor=None):
    results = []
    for source_key in PUBLIC_SOURCE_KEYS:
        policy = CatalogSourcePolicy.objects.select_related("source").filter(source_kind=source_key).first()
        if not policy:
            continue
        published, cached, errors = _publish_eligible_for_source(
            policy.source,
            publish_limit=publish_limit_per_source,
            actor=actor,
        )
        results.append({
            "source": source_key,
            "published": published,
            "images_cached": cached,
            "errors": errors,
        })
    return results
