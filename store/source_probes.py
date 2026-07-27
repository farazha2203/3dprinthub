from __future__ import annotations

import os
from urllib.error import HTTPError

from django.utils import timezone

from .catalog_site_adapters import get_source_adapter
from .catalog_site_adapters.common import CatalogCandidate
from .models import CatalogSeedURL, CatalogSourcePolicy
from .source_monitoring import source_log, update_log


EXPECTED_SOURCE_STATES = {"configuration_required", "blocked_by_source", "manual_only"}


def _expected_result(policy, log, *, state: str, message: str):
    update_log(
        log,
        stage=message,
        progress=100,
        status="partial",
        message=message,
        details={"probe_status": state, "source_kind": policy.source_kind},
    )
    return {
        "_probe_status": state,
        "title": message,
        "images": [],
        "source_url": policy.source.base_url,
    }, log


def _seed_candidates(policy: CatalogSourcePolicy, limit=1):
    rows = CatalogSeedURL.objects.filter(source=policy.source, is_active=True).order_by("priority", "id")[:limit]
    return [CatalogCandidate(url=row.url, external_id="", summary={"seed_id": row.pk}) for row in rows]


def _update_seed(candidate: CatalogCandidate, *, ok: bool, error: str = ""):
    seed_id = (candidate.summary or {}).get("seed_id")
    if not seed_id:
        return
    CatalogSeedURL.objects.filter(pk=seed_id).update(
        last_status="success" if ok else "failed",
        last_error=error[:2000],
        last_checked_at=timezone.now(),
    )


def test_catalog_source(policy: CatalogSourcePolicy, *, actor=None):
    source = policy.source
    with source_log(source_key=policy.source_kind, action="catalog_probe", actor=actor) as log:
        update_log(log, stage="ساخت Adapter", progress=10, message=source.name)

        if policy.source_kind == "thingiverse":
            env_name = policy.api_token_env or "THINGIVERSE_ACCESS_TOKEN"
            if not os.environ.get(env_name, "").strip():
                return _expected_result(
                    policy,
                    log,
                    state="configuration_required",
                    message=f"توکن رسمی Thingiverse تنظیم نشده است؛ متغیر {env_name} را در محیط سرور وارد کنید.",
                )

        if policy.source_kind == "grabcad" and not CatalogSeedURL.objects.filter(source=source, is_active=True).exists():
            return _expected_result(
                policy,
                log,
                state="manual_only",
                message="GrabCAD به‌علت پاسخ 403 و محدودیت استفاده تجاری فقط با لینک بذر ادمین و به‌صورت مرجع داخلی بررسی می‌شود.",
            )

        adapter = get_source_adapter(source, policy)
        update_log(log, stage="دریافت فهرست نمونه", progress=35)
        try:
            candidates = adapter.discover(limit=1, sort_mode="downloads")
        except HTTPError as exc:
            if exc.code in {401, 403, 429}:
                candidates = _seed_candidates(policy)
                if not candidates:
                    return _expected_result(
                        policy,
                        log,
                        state="blocked_by_source",
                        message=f"منبع درخواست خودکار را با HTTP {exc.code} مسدود کرده است؛ دورزدن انجام نمی‌شود. یک لینک بذر عمومی در ادمین ثبت کنید.",
                    )
            else:
                raise

        if not candidates:
            candidates = _seed_candidates(policy)
        if not candidates:
            state = "blocked_by_source" if policy.source_kind == "makerworld" else "manual_only"
            return _expected_result(
                policy,
                log,
                state=state,
                message=(
                    "فهرست MakerWorld از این سرور قابل کشف نیست؛ Sitemap و فهرست عمومی بررسی شد. "
                    "برای تست، یک لینک مدل عمومی در بخش لینک‌های بذر ثبت کنید."
                    if policy.source_kind == "makerworld"
                    else "هیچ مدل نمونه یا لینک بذر فعالی برای این منبع پیدا نشد."
                ),
            )

        candidate = candidates[0]
        update_log(
            log,
            stage="دریافت جزئیات نمونه",
            progress=65,
            records_found=1,
            details={"candidate_url": candidate.url, "external_id": candidate.external_id},
        )
        try:
            record = adapter.fetch_record(candidate, hydrate_files=False)
        except HTTPError as exc:
            _update_seed(candidate, ok=False, error=f"HTTP {exc.code}")
            if exc.code in {401, 403, 429}:
                return _expected_result(
                    policy,
                    log,
                    state="blocked_by_source",
                    message=f"صفحه نمونه با HTTP {exc.code} مسدود شد؛ محدودیت منبع دور زده نمی‌شود.",
                )
            raise
        except Exception as exc:
            _update_seed(candidate, ok=False, error=f"{type(exc).__name__}: {exc}")
            raise

        _update_seed(candidate, ok=True)
        title = record.get("title") or candidate.external_id
        images = record.get("images") or []
        update_log(
            log,
            stage="اعتبارسنجی پارسر",
            progress=92,
            records_found=1,
            details={
                "probe_status": "success",
                "candidate_url": candidate.url,
                "title": title,
                "image_count": len(images),
                "license": record.get("license_name"),
                "commercial_use_allowed": record.get("commercial_use_allowed"),
            },
            message=f"نمونه «{title}» با {len(images)} تصویر تحلیل شد.",
        )
        record["_probe_status"] = "success"
        return record, log
