from __future__ import annotations

import hashlib
import mimetypes
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import IntegerField, Q, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.text import slugify

from .catalog_classification import classify_external_asset
from .automation_watchdog import (
    CatalogRunCancelled,
    CatalogRunDeadlineExceeded,
    initialize_catalog_run_deadline,
    touch_catalog_run,
)
from .catalog_site_adapters import get_source_adapter
from .catalog_site_adapters.common import (
    all_values,
    extract_file_formats,
    first_value,
    normalize_text,
    parse_duration_minutes,
    parse_weight_grams,
    safe_int,
    unique_urls,
)
from .models import (
    CatalogAssetMetrics,
    CatalogPricingReview,
    CatalogSyncRun,
    ImportedPrintAsset,
    ImportedPrintAssetImage,
    PrintCatalogSource,
    Product,
)

MAX_IMAGE_BYTES = 12 * 1024 * 1024


def _safe_decimal(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _safe_slug(title: str, source_code: str, external_id: str) -> str:
    base = slugify(title, allow_unicode=True)[:220] or "external-model"
    suffix = hashlib.sha1(f"{source_code}:{external_id}".encode("utf-8")).hexdigest()[:10]
    return f"{base}-{suffix}"


def _asset_tags(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if str(item).strip())[:700]
    return str(value or "")[:700]


def _flatten_summary_values(values):
    """Flatten common API/JSON shapes without trusting source-specific schemas."""
    output = []

    def walk(value):
        if isinstance(value, (list, tuple, set)):
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            direct = (
                value.get("url")
                or value.get("contentUrl")
                or value.get("downloadUrl")
                or value.get("image_url")
                or value.get("imageUrl")
                or value.get("public_url")
            )
            if direct:
                output.append(direct)
            else:
                for item in value.values():
                    walk(item)
        elif value not in (None, ""):
            output.append(value)

    walk(values)
    return output


def _fallback_candidate_record(candidate, *, source_name: str, error: Exception) -> dict[str, Any]:
    """Preserve listing/API metadata when the detail page cannot be hydrated."""
    summary = candidate.summary if isinstance(candidate.summary, dict) else {}
    title = normalize_text(first_value(
        summary,
        ["title", "name", "displayName", "modelName", "filename", "fileName", "slug"],
        "",
    ))
    description = normalize_text(first_value(
        summary,
        ["description", "summary", "caption", "excerpt", "instructions"],
        "",
    ))
    image_values = _flatten_summary_values(all_values(
        summary,
        [
            "images", "image", "imageUrl", "image_url", "thumbnail", "thumbnailUrl",
            "thumbnail_url", "preview", "previewUrl", "preview_url", "cover", "coverUrl",
            "defaultImage", "featuredImage", "photo", "photos",
        ],
    ))
    images = unique_urls(image_values, candidate.url)[:20]
    file_values = _flatten_summary_values(all_values(
        summary,
        ["files", "file", "downloadUrl", "contentUrl", "fileUrl", "filename", "fileName"],
    ))
    file_links = [url for url in unique_urls(file_values, candidate.url) if url != candidate.url][:100]
    formats = extract_file_formats([*file_values, *file_links])
    tags = first_value(summary, ["tags", "keywords", "labels"], [])
    if not isinstance(tags, list):
        tags = [tags] if tags else []
    tags = [
        normalize_text(item.get("name") or item.get("title") or item.get("label"))
        if isinstance(item, dict) else normalize_text(item)
        for item in tags
    ]
    tags = [item for item in tags if item]
    author = first_value(summary, ["author", "creator", "designer", "username"], "")
    if isinstance(author, dict):
        author = author.get("name") or author.get("displayName") or author.get("username") or ""

    return {
        "source_url": candidate.url,
        "external_id": candidate.external_id,
        "title": title,
        "short_description": description[:500],
        "description": description,
        "images": images,
        "file_links": file_links,
        "file_formats": formats,
        "tags": tags,
        "author_name": normalize_text(author),
        "source_category": normalize_text(first_value(summary, ["category", "categoryName", "typeName", "section"], "")),
        "estimated_weight_grams": parse_weight_grams(first_value(
            summary, ["weight", "weightGrams", "filamentWeight", "materialWeight"], None
        )),
        "estimated_print_minutes": parse_duration_minutes(first_value(
            summary, ["printTime", "printingTime", "duration", "estimatedTime"], None
        )),
        "metrics": {
            "views_count": safe_int(first_value(summary, ["viewCount", "views"], 0)),
            "likes_count": safe_int(first_value(summary, ["likeCount", "likes", "collectCount"], 0)),
            "downloads_count": safe_int(first_value(summary, ["downloadCount", "downloads"], 0)),
            "makes_count": safe_int(first_value(summary, ["makeCount", "makes"], 0)),
            "comments_count": safe_int(first_value(summary, ["commentCount", "comments"], 0)),
        },
        "license_review_status": "manual",
        "commercial_use_allowed": None,
        "blocked_reason": "جزئیات کامل دریافت نشد؛ آیتم به‌صورت مرجع لینک منبع ذخیره شد.",
        "raw_payload": {
            "candidate_summary": summary,
            "fetch_error": f"{type(error).__name__}: {error}",
            "fallback_source": source_name,
        },
    }


def _download_approved_image(asset: ImportedPrintAsset, image_url: str, adapter, *, gallery: bool = False):
    payload, content_type = adapter.client.fetch_bytes(image_url)
    if not content_type.startswith("image/"):
        raise ValidationError("فایل تصویر معتبر نیست.")
    extension = mimetypes.guess_extension(content_type) or Path(urlparse(image_url).path).suffix or ".jpg"
    filename = f"catalog-{asset.pk}-{abs(hash(image_url)) % 1_000_000}{extension}"
    if gallery:
        image = ImportedPrintAssetImage(asset=asset, remote_url=image_url, alt_text=asset.title)
        image.image.save(filename, ContentFile(payload), save=True)
        return image
    asset.preview_image.save(filename, ContentFile(payload), save=True)
    return asset


@transaction.atomic
def save_external_record(*, source: PrintCatalogSource, policy, parsed: dict[str, Any], rank: int = 0):
    source_url = parsed.get("source_url")
    if not source_url:
        raise ValidationError("آدرس صفحه منبع در داده Adapter وجود ندارد.")
    external_id = str(parsed.get("external_id") or "")[:160]
    title = str(parsed.get("title") or "").strip()
    if not title:
        path_name = urlparse(source_url).path.rstrip("/").rsplit("/", 1)[-1]
        title = path_name.replace("-", " ").replace("_", " ").strip() or f"مدل از {source.name}"
    title = title[:260]
    image_urls = [url for url in parsed.get("images", []) if isinstance(url, str)][:20]
    file_links = [url for url in parsed.get("file_links", []) if isinstance(url, str)][:100]
    first_download = file_links[0] if file_links and source.store_private_download_url and policy.store_download_links else ""

    asset, _created = ImportedPrintAsset.objects.update_or_create(
        source=source,
        source_url=source_url,
        defaults={
            "external_id": external_id,
            "title": title,
            "slug": _safe_slug(title, source.code, external_id or source_url),
            "short_description": str(parsed.get("short_description") or "")[:500],
            "description": str(parsed.get("description") or ""),
            "technical_specs": {
                "source_category": parsed.get("source_category") or "",
                "estimated_weight_grams": parsed.get("estimated_weight_grams"),
                "estimated_print_minutes": parsed.get("estimated_print_minutes"),
                "file_formats": parsed.get("file_formats") or [],
                "source_file_available": bool(
                    file_links
                    or parsed.get("file_formats")
                    or parsed.get("source_file_available")
                ),
                "source_file_reference": source_url,
            },
            "tags": _asset_tags(parsed.get("tags")),
            "author_name": str(parsed.get("author_name") or "")[:200],
            "license_name": str(parsed.get("license_name") or "")[:200],
            "license_url": str(parsed.get("license_url") or "")[:1000],
            "remote_image_url": image_urls[0] if image_urls else "",
            "private_download_url": first_download[:2000],
            "file_format": ", ".join(parsed.get("file_formats") or [])[:80],
            "source_title": title,
            "source_description": str(parsed.get("description") or ""),
            "editorial_status": "license_review" if str(parsed.get("license_review_status") or "manual") != "allowed" else "review",
            "commercial_license_status": "allowed" if parsed.get("commercial_use_allowed") is True else ("blocked" if str(parsed.get("license_review_status") or "") == "blocked" else "review"),
            "commercial_license_note": str(parsed.get("license_text") or parsed.get("blocked_reason") or ""),
            "source_payload": parsed.get("raw_payload") or {},
        },
    )

    classification = classify_external_asset(
        source_kind=policy.source_kind,
        title=title,
        description=str(parsed.get("description") or ""),
        tags=parsed.get("tags") or [],
        source_category=str(parsed.get("source_category") or ""),
    )
    metrics_data = parsed.get("metrics") or {}
    rating = _safe_decimal(metrics_data.get("rating"))
    allowed = parsed.get("commercial_use_allowed")
    review_status = str(parsed.get("license_review_status") or "manual")
    if policy.public_display_policy == "admin_only":
        allowed = False
        review_status = "blocked"

    metrics, _ = CatalogAssetMetrics.objects.update_or_create(
        asset=asset,
        defaults={
            "source_kind": policy.source_kind,
            "source_category": str(parsed.get("source_category") or "")[:250],
            "segment": classification.segment,
            "target_category": classification.category or source.default_category,
            "popularity_rank": rank,
            "views_count": int(metrics_data.get("views_count") or 0),
            "likes_count": int(metrics_data.get("likes_count") or 0),
            "downloads_count": int(metrics_data.get("downloads_count") or 0),
            "makes_count": int(metrics_data.get("makes_count") or 0),
            "comments_count": int(metrics_data.get("comments_count") or 0),
            "rating": rating,
            "estimated_weight_grams": _safe_decimal(parsed.get("estimated_weight_grams")),
            "estimated_print_minutes": parsed.get("estimated_print_minutes"),
            "estimate_source": str(parsed.get("estimate_source") or "")[:100],
            "file_formats": parsed.get("file_formats") or [],
            "file_links": file_links if policy.store_download_links else [],
            "image_urls": image_urls,
            "creator_url": str(parsed.get("creator_url") or "")[:2000],
            "license_code": str(parsed.get("license_name") or "")[:120],
            "commercial_use_allowed": allowed,
            "license_review_status": review_status,
            "blocked_reason": str(parsed.get("blocked_reason") or ""),
            "attribution_text": str(parsed.get("attribution_text") or "")[:500],
            "raw_metrics": metrics_data,
            "last_synced_at": timezone.now(),
        },
    )

    # Every catalog item enters the operator queue. Alerts are sent when a
    # customer requests a quote, not for every background-imported record.
    CatalogPricingReview.objects.get_or_create(asset=asset)

    existing_urls = set(asset.images.values_list("remote_url", flat=True))
    for index, image_url in enumerate(image_urls):
        if image_url not in existing_urls:
            image_records = parsed.get("image_records") or []
            image_meta = image_records[index] if index < len(image_records) and isinstance(image_records[index], dict) else {}
            ImportedPrintAssetImage.objects.create(
                asset=asset,
                remote_url=image_url,
                alt_text=str(image_meta.get("name") or title)[:260],
                sort_order=index,
                source_name=source.name,
                source_page_url=source_url,
                source_content_type=str(image_meta.get("content_type") or "")[:80],
                source_width=int(image_meta.get("width") or 0),
                source_height=int(image_meta.get("height") or 0),
                is_primary=index == 0,
                is_selected=True,
            )
    return asset, metrics


def sync_catalog_source(*, source: PrintCatalogSource, requested_limit=None, sort_mode="downloads", actor=None, hydrate_files=False, sync_run=None):
    if not source.is_active:
        raise ValidationError("منبع غیرفعال است.")
    try:
        policy = source.sync_policy
    except Exception as exc:
        raise ValidationError("سیاست دریافت برای این منبع تعریف نشده است.") from exc
    if not policy.is_active:
        raise ValidationError("سیاست دریافت منبع غیرفعال است.")

    limit = policy.clamp_limit(requested_limit)
    run = sync_run or CatalogSyncRun.objects.create(
        source=source,
        sort_mode=sort_mode,
        requested_limit=limit,
        requested_by=actor,
    )
    run.status = "running"
    run.started_at = timezone.now()
    run.cancelled_at = None
    run.log = "شروع دریافت\n"
    initialize_catalog_run_deadline(run, now=run.started_at)
    run.save(update_fields=[
        "status", "started_at", "cancelled_at", "deadline_at",
        "heartbeat_at", "log",
    ])

    adapter = get_source_adapter(source, policy)
    errors: list[str] = []
    try:
        touch_catalog_run(run)
        try:
            candidates = adapter.discover(limit=limit, sort_mode=sort_mode)
        except ValueError as exc:
            message = str(exc)
            if policy.source_kind == "thingiverse" and "توکن رسمی Thingiverse" in message:
                run.status = "partial"
                run.log = "نیازمند تنظیمات: " + message
                run.finished_at = timezone.now()
                run.heartbeat_at = run.finished_at
                run.save(update_fields=["status", "log", "finished_at", "heartbeat_at"])
                return run
            raise
        run.discovered_count = len(candidates)
        touch_catalog_run(run, update_fields=["discovered_count"])
        if not candidates:
            if policy.source_kind in {"makerworld", "grabcad"}:
                run.status = "partial"
                run.log = (
                    "منبع فهرست خودکار را مسدود کرده یا JavaScript-only است. "
                    "دورزدن انجام نشد؛ لینک بذر عمومی را از ادمین ثبت کنید."
                )
                run.finished_at = timezone.now()
                run.heartbeat_at = run.finished_at
                run.save(update_fields=["status", "log", "finished_at", "heartbeat_at"])
                return run
            raise ValidationError(
                "هیچ مدل عمومی کشف نشد؛ ساختار منبع، robots.txt، دسترسی شبکه یا تنظیم URL فهرست را بررسی کنید."
            )
        for rank, candidate in enumerate(candidates, start=1):
            touch_catalog_run(run)
            try:
                parsed = adapter.fetch_record(candidate, hydrate_files=hydrate_files)
                touch_catalog_run(run)
                asset, metrics = save_external_record(source=source, policy=policy, parsed=parsed, rank=rank)
                if source.download_preview_images and not asset.preview_image and metrics.image_urls:
                    try:
                        _download_approved_image(asset, metrics.image_urls[0], adapter)
                    except Exception as image_exc:
                        errors.append(f"{candidate.url}: image warning: {image_exc}")
                run.imported_count += 1
            except (CatalogRunCancelled, CatalogRunDeadlineExceeded):
                raise
            except Exception as exc:
                fallback = _fallback_candidate_record(candidate, source_name=source.name, error=exc)
                try:
                    save_external_record(source=source, policy=policy, parsed=fallback, rank=rank)
                    run.imported_count += 1
                except Exception as fallback_exc:
                    run.failed_count += 1
                    errors.append(f"{candidate.url}: {type(fallback_exc).__name__}: {fallback_exc}")
                else:
                    run.failed_count += 1
                    errors.append(f"{candidate.url}: partial: {type(exc).__name__}: {exc}")
            run.current_page = rank
            if rank % 10 == 0:
                run.log = "\n".join(["در حال اجرا", *errors[-20:]])
            touch_catalog_run(
                run,
                update_fields=[
                    "current_page", "imported_count", "failed_count", "log"
                ],
            )
        run.status = "completed" if not errors else ("partial" if run.imported_count else "failed")
    except CatalogRunCancelled:
        run.refresh_from_db()
        if run.status != "cancelled":
            run.status = "cancelled"
            run.cancelled_at = timezone.now()
            run.finished_at = run.cancelled_at
            run.heartbeat_at = run.cancelled_at
            run.log = "اجرای کاتالوگ توسط اپراتور متوقف شد."
            run.save(update_fields=[
                "status", "cancelled_at", "finished_at", "heartbeat_at", "log"
            ])
        return run
    except CatalogRunDeadlineExceeded as exc:
        run.status = "failed"
        errors.append(f"{type(exc).__name__}: {exc}")
    except Exception as exc:
        run.status = "failed"
        errors.append(f"{type(exc).__name__}: {exc}")

    persisted_state = CatalogSyncRun.objects.filter(pk=run.pk).values(
        "status", "cancelled_at"
    ).first()
    if persisted_state and (
        persisted_state["status"] == "cancelled"
        or persisted_state["cancelled_at"]
    ):
        run.refresh_from_db()
        return run
    run.log = "\n".join(errors[-100:]) or "بدون خطا"
    run.finished_at = timezone.now()
    run.heartbeat_at = run.finished_at
    run.save(update_fields=[
        "status", "imported_count", "failed_count", "current_page",
        "log", "finished_at", "heartbeat_at",
    ])
    policy.last_synced_at = run.finished_at
    policy.save(update_fields=["last_synced_at"])
    return run


@transaction.atomic
def approve_asset_for_public(asset: ImportedPrintAsset, *, actor=None, create_product=False, cache_images=True):
    metrics = asset.metrics
    if metrics.source_kind == "grabcad":
        raise ValidationError("GrabCAD در این سامانه فقط برای مرجع داخلی ادمین است.")
    if metrics.commercial_use_allowed is not True or metrics.license_review_status != "allowed":
        raise ValidationError("مجوز فروش چاپ فیزیکی این فایل تأیید نشده است.")
    metrics.public_approved = True
    metrics.full_clean()
    metrics.save(update_fields=["public_approved"])

    policy = asset.source.sync_policy
    adapter = get_source_adapter(asset.source, policy)
    if cache_images and policy.cache_images_after_approval and not asset.preview_image and metrics.image_urls:
        _download_approved_image(asset, metrics.image_urls[0], adapter)
        for image_url in metrics.image_urls[1:10]:
            image_obj = asset.images.filter(remote_url=image_url).first()
            if image_obj and not image_obj.image:
                try:
                    payload, content_type = adapter.client.fetch_bytes(image_url)
                    if not content_type.startswith("image/"):
                        continue
                    extension = mimetypes.guess_extension(content_type) or ".jpg"
                    filename = f"catalog-{asset.pk}-{abs(hash(image_url)) % 1_000_000}{extension}"
                    image_obj.image.save(filename, ContentFile(payload), save=True)
                except Exception:
                    continue

    if create_product or policy.auto_create_draft_products:
        return convert_approved_asset_to_product(asset)
    return asset


@transaction.atomic
def convert_approved_asset_to_product(asset: ImportedPrintAsset) -> Product:
    metrics = asset.metrics
    if not metrics.may_be_public:
        raise ValidationError("ابتدا مجوز و نمایش عمومی فایل را تأیید کنید.")
    if asset.product_id:
        return asset.product
    category = metrics.target_category or asset.source.default_category
    if category is None:
        raise ValidationError("برای فایل دسته مقصد تعیین نشده است.")
    if not asset.preview_image:
        raise ValidationError("برای ساخت محصول باید حداقل یک تصویر محلی تأییدشده وجود داشته باشد.")
    token = hashlib.sha1(f"{asset.source_id}:{asset.external_id or asset.pk}".encode()).hexdigest()[:10].upper()
    product = Product.objects.create(
        category=category,
        title=asset.title[:220],
        slug=_safe_slug(asset.title, asset.source.code, asset.external_id or str(asset.pk))[:240],
        sku=f"EXT-{asset.source.code[:8].upper()}-{token}"[:80],
        short_description=asset.short_description or asset.description[:350],
        description=asset.description,
        main_image=asset.preview_image,
        dimensions="",
        technical_notes=(
            f"منبع: {asset.source.name}\n"
            f"طراح: {asset.author_name or '-'}\n"
            f"مجوز: {asset.license_name or '-'}\n"
            f"انتساب: {metrics.attribution_text}"
        ),
        is_active=False,
        robots_index=False,
        robots_follow=False,
    )
    asset.product = product
    asset.status = "converted"
    asset.save(update_fields=["product", "status"])
    return product


def public_catalog_queryset():
    """All references allowed by the explicit per-source public-reference switch.

    License and digital-file rules control direct ordering, not metadata visibility.
    Public templates expose only metadata, images and source attribution; private
    download links never leave admin.
    """
    return (
        ImportedPrintAsset.objects.select_related(
            "source", "source__sync_policy", "metrics", "metrics__target_category", "product"
        )
        .filter(
            Q(source__is_active=True)
            | Q(keep_public_when_source_disabled=True)
            | Q(archive_status__in=["downloaded", "archived", "ordered"])
            | (Q(archived_model_file__isnull=False) & ~Q(archived_model_file=""))
            | (Q(product__model_file__isnull=False) & ~Q(product__model_file=""))
        )
        .filter(
            Q(keep_public_when_source_disabled=True)
            | Q(archive_status__in=["downloaded", "archived", "ordered"])
            | (Q(archived_model_file__isnull=False) & ~Q(archived_model_file=""))
            | (Q(product__model_file__isnull=False) & ~Q(product__model_file=""))
            | Q(source__sync_policy__isnull=True)
            | Q(
                source__sync_policy__is_active=True,
                source__sync_policy__public_reference_enabled=True,
            )
        )
        .exclude(title="")
        .annotate(
            source_priority_order=Coalesce(
                "source__sync_policy__source_priority", Value(100), output_field=IntegerField()
            )
        )
        .order_by("source_priority_order", "metrics__popularity_rank", "-metrics__downloads_count", "-imported_at", "title")
    )
