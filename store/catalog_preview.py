from __future__ import annotations

import hashlib
import json
import mimetypes
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction

from .catalog_site_adapters import get_source_adapter
from .catalog_site_adapters.common import CatalogCandidate, parse_duration_minutes, parse_weight_grams
from .catalog_sync import save_external_record
from .models import ImportedPrintAsset, ImportedPrintAssetImage, ImportedPrintAssetPrintProfile

MAX_IMAGE_BYTES = 12 * 1024 * 1024
MAX_PROFILE_COUNT = 30

WEIGHT_KEYS = (
    "filamentWeight",
    "filament_weight",
    "filamentUsed",
    "filament_used",
    "materialWeight",
    "material_weight",
    "weightGrams",
    "weight_grams",
    "weight",
)
DURATION_KEYS = (
    "printTime",
    "print_time",
    "printingTime",
    "printing_time",
    "duration",
    "estimatedTime",
    "estimated_time",
)
NAME_KEYS = (
    "profileName",
    "profile_name",
    "printProfileName",
    "print_profile_name",
    "displayName",
    "label",
    "name",
    "title",
)
MATERIAL_KEYS = ("material", "filament", "materialName", "filamentName")
NOZZLE_KEYS = ("nozzle", "nozzleDiameter", "nozzle_diameter")
LAYER_KEYS = ("layerHeight", "layer_height", "layer")
INFILL_KEYS = ("infill", "infillPercent", "infill_percent", "fillDensity")


@dataclass(slots=True)
class PreviewRefreshResult:
    asset_id: int
    title: str
    images_found: int = 0
    images_downloaded: int = 0
    profiles_found: int = 0
    description_updated: bool = False


def _first(mapping: dict[str, Any], keys: Iterable[str]):
    for key in keys:
        value = mapping.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def _decimal(value, places: str = "0.01") -> Decimal | None:
    if value in (None, ""):
        return None
    if isinstance(value, str):
        cleaned = value.strip().lower().replace(",", "")
        for token in ("mm", "%", "میلی‌متر"):
            cleaned = cleaned.replace(token, "")
        value = cleaned.strip()
    try:
        return Decimal(str(value)).quantize(Decimal(places))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _profile_key(row: dict[str, Any]) -> str:
    raw = json.dumps(row, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:32]


def extract_print_profiles(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    raw_payload = parsed.get("raw_payload") or {}
    blobs = raw_payload.get("json_blobs") or []
    rows: list[dict[str, Any]] = []
    seen: set[tuple] = set()

    def append_profile(payload: dict[str, Any], *, fallback_name: str = "پروفایل چاپ") -> None:
        weight = parse_weight_grams(_first(payload, WEIGHT_KEYS))
        duration = parse_duration_minutes(_first(payload, DURATION_KEYS))
        if weight is None and duration is None:
            return

        name_value = _first(payload, NAME_KEYS)
        name = str(name_value or fallback_name).strip()[:220] or fallback_name
        material = str(_first(payload, MATERIAL_KEYS) or "").strip()[:120]
        nozzle = _decimal(_first(payload, NOZZLE_KEYS), "0.01")
        layer = _decimal(_first(payload, LAYER_KEYS), "0.001")
        infill = _decimal(_first(payload, INFILL_KEYS), "0.01")
        signature = (
            name.casefold(),
            round(float(weight), 2) if weight is not None else None,
            duration,
            material.casefold(),
            str(nozzle or ""),
            str(layer or ""),
            str(infill or ""),
        )
        if signature in seen:
            return
        seen.add(signature)
        row = {
            "source_key": _profile_key({
                "name": name,
                "weight": weight,
                "duration": duration,
                "material": material,
                "nozzle": str(nozzle or ""),
                "layer": str(layer or ""),
                "infill": str(infill or ""),
            }),
            "profile_name": name,
            "weight_grams": Decimal(str(weight)).quantize(Decimal("0.01")) if weight is not None else None,
            "print_minutes": duration,
            "material": material,
            "nozzle_mm": nozzle,
            "layer_height_mm": layer,
            "infill_percent": infill,
            "source_payload": payload,
        }
        rows.append(row)

    for mapping in _walk(blobs):
        append_profile(mapping)
        if len(rows) >= MAX_PROFILE_COUNT:
            break

    primary_weight = parse_weight_grams(parsed.get("estimated_weight_grams"))
    primary_minutes = parse_duration_minutes(parsed.get("estimated_print_minutes"))
    if primary_weight is not None or primary_minutes is not None:
        append_profile(
            {
                "name": "پروفایل اصلی منبع",
                "weight": f"{primary_weight} g" if primary_weight is not None else None,
                "duration": primary_minutes,
            },
            fallback_name="پروفایل اصلی منبع",
        )

    rows.sort(key=lambda item: (
        item["weight_grams"] is None,
        item["weight_grams"] or Decimal("999999"),
        item["profile_name"],
    ))
    return rows[:MAX_PROFILE_COUNT]


def sync_print_profiles(asset: ImportedPrintAsset, parsed: dict[str, Any]) -> int:
    profiles = extract_print_profiles(parsed)
    seen: set[str] = set()
    for profile in profiles:
        source_key = profile.pop("source_key")
        seen.add(source_key)
        ImportedPrintAssetPrintProfile.objects.update_or_create(
            asset=asset,
            source_key=source_key,
            defaults={
                **profile,
                "is_manual": False,
                "is_active": True,
            },
        )
    stale = asset.print_profiles.filter(is_manual=False)
    if seen:
        stale = stale.exclude(source_key__in=seen)
    stale.delete()
    return len(profiles)


def _image_extension(content_type: str, url: str) -> str:
    extension = mimetypes.guess_extension(content_type or "")
    if extension:
        return extension
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}:
        return suffix
    return ".jpg"


def _download_image(adapter, url: str) -> tuple[bytes, str]:
    payload, content_type = adapter.client.fetch_bytes(url)
    if not str(content_type or "").lower().startswith("image/"):
        raise ValidationError("پاسخ منبع تصویر معتبر نیست.")
    if len(payload) > MAX_IMAGE_BYTES:
        raise ValidationError("حجم تصویر از سقف مجاز بیشتر است.")
    return payload, content_type


def cache_preview_images(asset: ImportedPrintAsset, adapter, image_urls: list[str], *, max_images: int = 20) -> int:
    downloaded = 0
    unique_urls = list(dict.fromkeys(url for url in image_urls if isinstance(url, str) and url.strip()))[:max_images]
    if not unique_urls:
        return 0

    if not asset.preview_image:
        payload, content_type = _download_image(adapter, unique_urls[0])
        filename = f"catalog-preview-{asset.pk}-{hashlib.sha1(unique_urls[0].encode()).hexdigest()[:12]}{_image_extension(content_type, unique_urls[0])}"
        asset.preview_image.save(filename, ContentFile(payload), save=True)
        downloaded += 1

    for index, url in enumerate(unique_urls):
        row, _ = ImportedPrintAssetImage.objects.get_or_create(
            asset=asset,
            remote_url=url,
            defaults={"alt_text": asset.title, "sort_order": index},
        )
        changed = False
        if row.sort_order != index:
            row.sort_order = index
            changed = True
        if not row.alt_text:
            row.alt_text = asset.title
            changed = True
        if changed:
            row.save(update_fields=["sort_order", "alt_text"])
        if row.image:
            continue
        payload, content_type = _download_image(adapter, url)
        filename = f"catalog-gallery-{asset.pk}-{index}-{hashlib.sha1(url.encode()).hexdigest()[:12]}{_image_extension(content_type, url)}"
        row.image.save(filename, ContentFile(payload), save=True)
        downloaded += 1
    return downloaded


@transaction.atomic
def refresh_asset_metadata(
    asset: ImportedPrintAsset,
    *,
    download_images: bool = True,
    max_images: int = 20,
) -> PreviewRefreshResult:
    try:
        policy = asset.source.sync_policy
    except Exception as exc:
        raise ValidationError("برای منبع این مدل سیاست دریافت تعریف نشده است.") from exc

    adapter = get_source_adapter(asset.source, policy)
    candidate = CatalogCandidate(
        url=asset.source_url,
        external_id=asset.external_id,
        summary={"title": asset.title},
    )
    parsed = adapter.fetch_record(candidate, hydrate_files=False)

    # این گردش‌کار فقط اطلاعات عمومی، تصاویر و پروفایل‌های چاپ را نگه می‌دارد.
    parsed["file_links"] = []
    refreshed_asset, metrics = save_external_record(
        source=asset.source,
        policy=policy,
        parsed=parsed,
        rank=getattr(getattr(asset, "metrics", None), "popularity_rank", 0),
    )

    profile_count = sync_print_profiles(refreshed_asset, parsed)
    technical_specs = dict(refreshed_asset.technical_specs or {})
    technical_specs["metadata_only"] = True
    technical_specs["print_profile_count"] = profile_count
    technical_specs["source_file_reference"] = refreshed_asset.source_url
    refreshed_asset.technical_specs = technical_specs
    refreshed_asset.private_download_url = ""
    refreshed_asset.save(update_fields=["technical_specs", "private_download_url", "updated_at"])
    if metrics.file_links:
        metrics.file_links = []
        metrics.save(update_fields=["file_links", "last_synced_at"])

    image_urls = list(parsed.get("images") or [])[:max_images]
    downloaded = 0
    if download_images and asset.source.download_preview_images:
        downloaded = cache_preview_images(refreshed_asset, adapter, image_urls, max_images=max_images)

    return PreviewRefreshResult(
        asset_id=refreshed_asset.pk,
        title=refreshed_asset.title,
        images_found=len(image_urls),
        images_downloaded=downloaded,
        profiles_found=profile_count,
        description_updated=bool(parsed.get("description")),
    )


def refresh_assets(
    queryset,
    *,
    download_images: bool = True,
    max_images: int = 20,
):
    results: list[PreviewRefreshResult] = []
    errors: list[str] = []
    for asset in queryset.select_related("source").iterator():
        try:
            results.append(
                refresh_asset_metadata(
                    asset,
                    download_images=download_images,
                    max_images=max_images,
                )
            )
        except Exception as exc:
            errors.append(f"{asset.pk} — {asset.title}: {type(exc).__name__}: {exc}")
    return results, errors
