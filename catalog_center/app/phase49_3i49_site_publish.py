from __future__ import annotations

import hashlib
import json
import re
import shutil
import time
from pathlib import Path
from typing import Any, Callable

from PIL import Image

from . import phase49_3c_image_pipeline as image_pipeline
from .batch_packaging import (
    IMAGE_EXTENSIONS,
    copy_images_into_model,
    materialize_selected_images,
    validate_batch_package,
)
from .crawler import download_public_file
from .db import utc_now
from .site_connection import import_batch, test_publish_readiness, upload_batch
from .epic49_site_sync import BridgeNotFoundError, get_product as get_site_product
from .epic49_desktop_schema import (
    list_available_material_colors,
    normalize_material_color_options,
)
from .phase49_3i35_operator_ledger import (
    flatten_ledger_profiles,
    normalize_ledger_profile,
)
from .phase49_3i39_professional_commerce import (
    merge_global_offer,
    offer_key,
    pricing_summary_range,
)
from .v8_features import (
    ack_item_confirms_publish,
    new_batch_uuid,
    product_fingerprint,
    source_payload_hash,
)


Progress = Callable[[int, str], None]


def _ids(values) -> list[int]:
    output = set()
    for value in values or []:
        try:
            parsed = int(value)
        except Exception:
            continue
        if parsed > 0:
            output.add(parsed)
    return sorted(output)


def _next_batch_name(root: Path) -> str:
    """Return a server-compatible unique second-resolution batch name."""
    base = int(time.time())
    for offset in range(120):
        stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(base + offset))
        name = "desktop_catalog_v85_" + stamp
        if not (root / name).exists() and not (root / (name + ".building")).exists():
            return name
    raise RuntimeError("Unable to allocate a unique publish batch name.")


def _row_dict(row) -> dict[str, Any]:
    return dict(row) if row is not None else {}


def _safe_part(value: Any, fallback: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip()).strip("._-")
    return text[:96] or fallback


def _json_list(value: Any) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def _refresh_product_pricing_snapshot(db, product_id: int) -> dict[str, Any]:
    """Refresh Product-owned Filament/Profile snapshots from current inventory.

    Publishing must not depend on the owner reopening Stage 2 after global
    Filament rates change. Exact Product selections are preserved by identity;
    only their operational Offer facts are refreshed before a Batch is built.
    """
    row = db.product(int(product_id))
    if row is None:
        return {"product_id": int(product_id), "changed": False, "matched_offers": 0}

    before = dict(row)
    global_offers = normalize_material_color_options(
        list_available_material_colors(db)
    )
    global_by_key = {offer_key(item): item for item in global_offers}

    selected = normalize_material_color_options(
        before.get("material_color_options_json") or "[]"
    )
    refreshed_selected: list[dict[str, Any]] = []
    matched = 0
    for item in selected:
        current = global_by_key.get(offer_key(item))
        if current is None:
            refreshed_selected.append(item)
            continue
        refreshed_selected.append(merge_global_offer(item, current))
        matched += 1

    raw_ledger = _json_list(before.get("sales_profile_ledger_json"))
    refreshed_ledger: list[dict[str, Any]] = []
    ranges: list[dict[str, int]] = []
    ledger_matches = 0
    for index, raw_profile in enumerate(raw_ledger, 1):
        if not isinstance(raw_profile, dict):
            continue
        profile = normalize_ledger_profile(raw_profile, index)
        refreshed_profile_offers: list[dict[str, Any]] = []
        for item in profile.get("material_options") or []:
            current = global_by_key.get(offer_key(item))
            if current is None:
                refreshed_profile_offers.append(item)
                continue
            refreshed_profile_offers.append(merge_global_offer(item, current))
            ledger_matches += 1
        profile["material_options"] = refreshed_profile_offers
        refreshed_ledger.append(profile)
        if profile.get("is_active", True):
            summary = pricing_summary_range(
                refreshed_profile_offers,
                profile.get("production_rows") or [],
                profile.get("pricing_strategy") or "dynamic",
                support_multiplier=profile.get("support_cost_multiplier") or 1,
                assembly_fee=profile.get("assembly_fee") or 0,
                price_min=profile.get("price_min") or 0,
                price_max=profile.get("price_max") or 0,
            )
            if int(summary.get("count") or 0) > 0:
                ranges.append({
                    "min": int(summary.get("min") or 0),
                    "max": int(summary.get("max") or 0),
                })

    total_matches = matched + ledger_matches
    if total_matches <= 0:
        return {
            "product_id": int(product_id),
            "changed": False,
            "matched_offers": 0,
        }

    flattened = flatten_ledger_profiles(refreshed_ledger)
    positive_min = [item["min"] for item in ranges if int(item.get("min") or 0) > 0]
    positive_max = [item["max"] for item in ranges if int(item.get("max") or 0) > 0]
    price_min = min(positive_min) if positive_min else int(before.get("price_min") or 0)
    price_max = max(positive_max) if positive_max else int(before.get("price_max") or price_min)

    materials = list(dict.fromkeys(
        str(item.get("material") or "").strip()
        for item in refreshed_selected
        if str(item.get("material") or "").strip()
    ))
    colors = list(dict.fromkeys(
        str(item.get("color") or "").strip()
        for item in refreshed_selected
        if str(item.get("color") or "").strip()
    ))
    updates = {
        "material_color_options_json": json.dumps(refreshed_selected, ensure_ascii=False),
        "sales_profile_ledger_json": json.dumps(refreshed_ledger, ensure_ascii=False),
        "sales_profiles_json": json.dumps(flattened, ensure_ascii=False),
        "materials_json": json.dumps(materials, ensure_ascii=False),
        "colors_json": json.dumps(colors, ensure_ascii=False),
        "price_min": int(price_min),
        "price_max": int(price_max),
    }
    changed = any(str(before.get(key) or "") != str(value) for key, value in updates.items())
    if changed:
        db.update_product(int(product_id), updates)
        try:
            db.save_history(
                int(product_id),
                "qt_publish_pricing_snapshot_refresh",
                before,
                dict(db.product(int(product_id))),
                (
                    "Publish refreshed selected Filament facts and recalculated "
                    f"price range {price_min}-{price_max} from current inventory."
                ),
            )
        except Exception:
            pass
    return {
        "product_id": int(product_id),
        "changed": bool(changed),
        "matched_offers": int(total_matches),
        "price_min": int(price_min),
        "price_max": int(price_max),
    }


def _refresh_publish_pricing_snapshots(db, product_ids) -> dict[str, Any]:
    items = [
        _refresh_product_pricing_snapshot(db, product_id)
        for product_id in _ids(product_ids)
    ]
    return {
        "items": items,
        "changed_ids": [
            int(item["product_id"])
            for item in items
            if item.get("changed")
        ],
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _selected_source_media_drift(row) -> dict[str, Any]:
    """Detect selected source bytes that changed after the last SEO finalization."""
    data = _row_dict(row)
    selected = image_pipeline.cap_unique_urls(
        [
            str(item or "").strip()
            for item in _json_list(data.get("selected_images_json"))
        ]
    )
    metadata = [
        dict(item)
        for item in _json_list(data.get("image_metadata_json"))
        if isinstance(item, dict)
    ]
    by_url = {
        str(item.get("source_url") or "").strip(): item
        for item in metadata
        if str(item.get("source_url") or "").strip()
    }
    changed: list[dict[str, str]] = []
    for source_url in selected:
        meta = by_url.get(source_url) or {}
        expected = str(meta.get("original_sha256") or "").strip()
        final_path_value = str(meta.get("final_local_file") or "").strip()
        final_sha = str(meta.get("final_sha256") or "").strip()
        if (
            meta.get("metadata_ready") is not True
            or not expected
            or not final_path_value
            or not final_sha
        ):
            # This is not an already-finalized image with changed source bytes.
            # Missing/incomplete SEO media must keep the mature fail-closed gate.
            continue
        try:
            final_path = Path(final_path_value).resolve()
        except Exception:
            continue
        if not final_path.is_file():
            continue

        source_value = image_pipeline.strict_source_local_image(
            data,
            source_url,
        )
        if not str(source_value or "").strip():
            continue
        source_path = Path(str(source_value)).resolve()
        if not source_path.is_file():
            continue
        actual = _sha256_file(source_path)
        if expected != actual:
            changed.append(
                {
                    "source_url": source_url,
                    "path": str(source_path),
                    "expected": expected,
                    "actual": actual,
                }
            )
    return {
        "changed": bool(changed),
        "items": changed,
        "selected_count": len(selected),
    }


def _refresh_changed_publish_media(db, product_ids) -> dict[str, Any]:
    """Refresh selected final WebPs only when their source bytes actually changed."""
    refreshed: list[int] = []
    failed: list[dict[str, Any]] = []
    for product_id in _ids(product_ids):
        row = db.product(product_id)
        if row is None:
            continue
        drift = _selected_source_media_drift(row)
        if not drift["changed"]:
            continue
        try:
            image_pipeline.finalize_selected_images(
                db,
                product_id,
                deduplicate=False,
                image_limit=max(1, int(drift["selected_count"] or 0)),
            )
            refreshed.append(product_id)
        except Exception as exc:
            failed.append(
                {
                    "product_id": product_id,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    return {
        "refreshed_ids": refreshed,
        "refreshed": len(refreshed),
        "failed": failed,
    }


def publish_media_gate(row) -> dict[str, Any]:
    """Fail closed unless every selected Product image is current final SEO WebP."""
    data = _row_dict(row)
    product_id = int(data.get("id") or 0)
    selected = image_pipeline.cap_unique_urls(
        [str(item or "").strip() for item in _json_list(data.get("selected_images_json"))]
    )
    primary = str(data.get("primary_image_url") or "").strip()
    missing: list[str] = []
    items: list[dict[str, Any]] = []

    if not selected:
        missing.append("Publish media: at least one selected image is required")
        return {"product_id": product_id, "ready": False, "missing": missing, "items": []}
    if not primary or primary not in selected:
        missing.append("Publish media: primary image must be one of the selected images")

    raw_local_dir = str(data.get("local_dir") or "").strip()
    if not raw_local_dir:
        missing.append("Publish media: Product local directory is missing")
        return {"product_id": product_id, "ready": False, "missing": missing, "items": []}
    local_dir = Path(raw_local_dir).resolve()
    seo_root = (local_dir / "seo_images").resolve()
    metadata = [item for item in _json_list(data.get("image_metadata_json")) if isinstance(item, dict)]
    by_url = {str(item.get("source_url") or "").strip(): dict(item) for item in metadata if str(item.get("source_url") or "").strip()}
    current_signature = image_pipeline.image_seo_signature(data)
    source_drift = {
        str(item.get("source_url") or ""): item
        for item in _selected_source_media_drift(data).get("items") or []
        if str(item.get("source_url") or "")
    }
    seen_names: set[str] = set()

    for index, source_url in enumerate(selected, start=1):
        prefix = f"Publish media image {index}"
        meta = by_url.get(source_url)
        if not meta:
            missing.append(f"{prefix}: SEO metadata is missing")
            continue
        for key, label in (
            ("seo_filename", "SEO filename"),
            ("alt_text", "Alt text"),
            ("title", "title"),
            ("caption", "caption"),
            ("creator", "creator"),
            ("source_page_url", "source page"),
        ):
            if not str(meta.get(key) or "").strip():
                missing.append(f"{prefix}: {label} is missing")
        keywords = meta.get("keywords")
        if not isinstance(keywords, list) or not any(str(item or "").strip() for item in keywords):
            missing.append(f"{prefix}: SEO keywords are missing")
        if meta.get("metadata_ready") is not True:
            missing.append(f"{prefix}: metadata_ready is not true")
        if str(meta.get("seo_signature") or "") != current_signature:
            missing.append(f"{prefix}: SEO metadata is stale and must be finalized again")
        if source_url in source_drift:
            missing.append(
                f"{prefix}: source image changed after finalization; "
                "SEO WebP must be rebuilt"
            )

        filename = Path(str(meta.get("seo_filename") or "")).name
        raw_final = str(meta.get("final_local_file") or "").strip()
        if not raw_final:
            missing.append(f"{prefix}: final SEO file is missing")
            continue
        final_path = Path(raw_final).resolve()
        try:
            final_path.relative_to(seo_root)
        except ValueError:
            missing.append(f"{prefix}: final file is outside seo_images")
            continue
        if final_path.suffix.lower() != ".webp":
            missing.append(f"{prefix}: final file must be WebP")
        if filename and final_path.name != filename:
            missing.append(f"{prefix}: final filename does not match SEO metadata")
        if final_path.name.casefold() in seen_names:
            missing.append(f"{prefix}: duplicate final SEO filename")
        seen_names.add(final_path.name.casefold())
        if not final_path.is_file() or final_path.stat().st_size < 512:
            missing.append(f"{prefix}: final WebP file is missing or empty")
            continue
        actual_sha = _sha256_file(final_path)
        if str(meta.get("final_sha256") or "") != actual_sha:
            missing.append(f"{prefix}: final WebP checksum mismatch")
        try:
            with Image.open(final_path) as image:
                width, height = image.size
                image_format = str(image.format or "").upper()
                image.verify()
            if image_format != "WEBP" or width <= 0 or height <= 0:
                raise ValueError("not a valid WebP")
        except Exception:
            missing.append(f"{prefix}: final image is not a valid WebP")
            continue
        items.append({
            "source_url": source_url,
            "path": str(final_path),
            "seo_filename": filename or final_path.name,
            "sha256": actual_sha,
            "width": int(width),
            "height": int(height),
        })

    deduped = list(dict.fromkeys(item for item in missing if item))
    return {
        "product_id": product_id,
        "ready": not deduped and len(items) == len(selected),
        "missing": deduped,
        "items": items,
    }


def _copy_publish_media(items: list[dict[str, Any]], model_dir: Path) -> list[str]:
    image_target = Path(model_dir) / "images"
    image_target.mkdir(parents=True, exist_ok=True)
    names: list[str] = []
    seen: set[str] = set()
    for item in items:
        source = Path(str(item.get("path") or "")).resolve()
        name = Path(str(item.get("seo_filename") or source.name)).name
        if not name.lower().endswith(".webp") or name.casefold() in seen:
            raise RuntimeError(f"Publish media filename is not a unique WebP: {name}")
        seen.add(name.casefold())
        destination = image_target / name
        shutil.copy2(source, destination)
        expected_sha = str(item.get("sha256") or "")
        if not destination.is_file() or destination.stat().st_size < 512 or _sha256_file(destination) != expected_sha:
            raise RuntimeError(f"Publish media copy verification failed: {name}")
        names.append(name)
    return names


def _copy_publish_videos(row: dict[str, Any], source_dir: Path | None, model_dir: Path) -> list[str]:
    try:
        raw = json.loads(str(row.get("local_video_files_json") or "[]"))
    except Exception:
        raw = []
    if not isinstance(raw, list) or not raw:
        return []

    video_root = (Path(source_dir).resolve() / "videos") if source_dir is not None else None
    target = Path(model_dir) / "videos"
    names: list[str] = []
    for index, value in enumerate(raw[:5], 1):
        source = Path(str(value or "")).resolve()
        if video_root is None or not source.is_file():
            raise RuntimeError(f"Publish video is missing: {source}")
        try:
            source.relative_to(video_root)
        except ValueError as exc:
            raise RuntimeError(f"Publish video escapes Product video root: {source}") from exc
        suffix = source.suffix.lower()
        if suffix not in {".mp4", ".webm", ".mov", ".m4v", ".gif"}:
            raise RuntimeError(f"Unsupported Product video type: {source.name}")
        if source.stat().st_size < 512 or source.stat().st_size > 80_000_000:
            raise RuntimeError(f"Product video size is outside the publish boundary: {source.name}")
        target.mkdir(parents=True, exist_ok=True)
        name = f"product-video-{index:02d}{suffix}"
        destination = target / name
        shutil.copy2(source, destination)
        if destination.stat().st_size != source.stat().st_size or _sha256_file(destination) != _sha256_file(source):
            raise RuntimeError(f"Publish video copy verification failed: {name}")
        names.append(name)
    return names


def publish_gate(db, stage_core, product_id: int, *, allow_already_public: bool = False) -> dict[str, Any]:
    product_id = int(product_id)
    row = db.product(product_id)
    if row is None:
        return {
            "product_id": product_id,
            "ready": False,
            "missing": ["رکورد محصول پیدا نشد."],
        }

    missing: list[str] = []
    for item in stage_core.statuses(product_id):
        stage = str(item.get("stage") or "")
        # The operator's explicit ready checkbox is the final publish approval.
        # All data stages must be factually ready first, but the legacy publish
        # stage itself may still carry the presentation-only final-approval gate.
        if stage == "publish":
            continue
        if not bool(item.get("data_ready")):
            label = str(item.get("label") or stage or "مرحله")
            details = list(item.get("missing") or [])
            if details:
                missing.extend(f"{label}: {detail}" for detail in details)
            else:
                missing.append(f"{label}: اطلاعات لازم ناقص است")

    data = _row_dict(row)
    canonical_profiles = []
    for key in ("sales_profile_ledger_json", "sales_profiles_json"):
        try:
            parsed = json.loads(data.get(key) or "[]")
        except Exception:
            parsed = []
        if isinstance(parsed, list) and any(isinstance(item, dict) for item in parsed):
            canonical_profiles = parsed
            break
    if not canonical_profiles:
        missing.append('سفارش و قیمت: حداقل یک پروفایل فروش canonical لازم است')
    media_state = publish_media_gate(data)
    missing.extend(media_state["missing"])
    if not bool(int(data.get("approved_for_sale") or 0)):
        missing.append("بررسی و انتشار: تأیید برای فروش")
    if not bool(int(data.get("publish_as_product") or 0)):
        # Marking ready is the explicit Product publish intent. This missing item
        # is converted into the publish flag by mark_ready_many, so it is not a
        # factual blocker.
        pass
    if bool(int(data.get("is_blocked") or 0)):
        missing.append("محصول در وضعیت رد/حذف است")
    if str(data.get("workflow_status") or "").strip().lower() == "archived":
        missing.append("محصول آرشیو شده است")
    if bool(int(data.get("reference_only") or 0)):
        missing.append("محصول فقط مرجع است و قابل انتشار فروشگاهی نیست")

    already_public = (
        bool(str(data.get("server_id") or "").strip())
        and str(data.get("workflow_status") or "").strip().lower() == "uploaded"
        and not bool(int(data.get("needs_update") or 0))
    )
    if already_public and not allow_already_public:
        missing.append("محصول قبلاً منتشر شده و تغییر جدیدی برای ارسال ندارد")

    deduped = list(dict.fromkeys(str(item) for item in missing if str(item).strip()))
    return {
        "product_id": product_id,
        "ready": not deduped,
        "missing": deduped,
        "already_public": already_public,
    }


def preflight_many(db, stage_core, product_ids, *, allow_already_public: bool = False) -> dict[str, Any]:
    requested_ids = _ids(product_ids)
    publishable_ids: list[int] = []
    queued_ids: list[int] = []
    blocked: list[dict[str, Any]] = []

    for product_id in requested_ids:
        state = publish_gate(db, stage_core, product_id, allow_already_public=allow_already_public)
        if not state["ready"]:
            blocked.append({
                "product_id": product_id,
                "missing": list(state["missing"]),
            })
            continue
        publishable_ids.append(product_id)
        row = db.product(product_id)
        if row is not None and bool(int(row["upload_ready"] or 0)):
            queued_ids.append(product_id)

    return {
        "requested": len(requested_ids),
        "requested_ids": requested_ids,
        "publishable_ids": publishable_ids,
        "queued_ids": queued_ids,
        "blocked": blocked,
        "blocked_count": len(blocked),
    }


def mark_ready_many(db, stage_core, product_ids) -> dict[str, Any]:
    requested_ids = _ids(product_ids)
    pricing_refresh = _refresh_publish_pricing_snapshots(db, requested_ids)
    media_refresh = _refresh_changed_publish_media(db, requested_ids)
    preflight = preflight_many(
        db,
        stage_core,
        requested_ids,
        allow_already_public=True,
    )
    marked: list[int] = []

    for product_id in preflight["publishable_ids"]:
        row = db.product(product_id)
        if row is None:
            continue
        before = dict(row)
        fingerprint = (
            str(row["fingerprint"] or "").strip()
            or product_fingerprint(row["source_code"], row["external_id"], row["source_url"])
        )
        db.update_product(product_id, {
            "publish_as_product": 1,
            "upload_ready": 1,
            "workflow_status": "approved",
            "fingerprint": fingerprint,
            "product_sync_error": "",
        })
        marked.append(product_id)
        try:
            db.save_history(
                product_id,
                "qt_bulk_publish_ready",
                before,
                dict(db.product(product_id)),
                "Product passed all factual gates and was explicitly marked ready for site publish.",
            )
        except Exception:
            pass

    result = dict(preflight)
    result["marked_ids"] = marked
    result["marked"] = len(marked)
    result["pricing_refreshed_ids"] = list(
        pricing_refresh.get("changed_ids") or []
    )
    result["pricing_refresh"] = list(pricing_refresh.get("items") or [])
    result["media_refreshed_ids"] = list(
        media_refresh.get("refreshed_ids") or []
    )
    result["media_refresh_failed"] = list(
        media_refresh.get("failed") or []
    )
    return result


def _download_batch_image(url: str, target: Path, referer: str) -> Path:
    return Path(
        download_public_file(
            url,
            target,
            max_bytes=20_000_000,
            referer=referer or url,
        )
    )


def build_publish_batch(
    db,
    product_ids,
    *,
    batch_root: Path | None = None,
    progress: Progress | None = None,
) -> dict[str, Any]:
    wanted = set(_ids(product_ids))
    exportable = {
        int(row["id"]): row
        for row in db.exportable()
        if int(row["id"]) in wanted
    }
    missing_ids = sorted(wanted - set(exportable))
    if missing_ids:
        raise RuntimeError(
            "این محصولات دیگر در صف انتشار معتبر نیستند: "
            + ", ".join(f"#{value}" for value in missing_ids)
        )
    if not exportable:
        raise RuntimeError("هیچ محصول آماده‌ای برای ساخت Batch انتخاب نشده است.")

    root = Path(batch_root or (Path(db.path).resolve().parent / "publish_batches"))
    root.mkdir(parents=True, exist_ok=True)
    batch_uuid = new_batch_uuid()
    name = _next_batch_name(root)
    batch = root / name
    building = root / (name + ".building")
    if batch.exists() or building.exists():
        raise RuntimeError(f"مسیر Batch از قبل وجود دارد: {batch}")

    models_root = building / "models"
    manifest: list[dict[str, Any]] = []
    batched_ids: list[int] = []
    rows = [exportable[product_id] for product_id in sorted(exportable)]
    total = max(1, len(rows))

    try:
        models_root.mkdir(parents=True, exist_ok=False)
        for index, row in enumerate(rows, 1):
            if progress:
                progress(
                    int((index - 1) / total * 22),
                    f"بسته‌بندی محصول {index}/{total}",
                )

            target = models_root / (
                _safe_part(row["source_code"], "source")
                + "_"
                + _safe_part(row["external_id"], f"product-{row['id']}")
            )
            target.mkdir(parents=True, exist_ok=False)

            raw_local_dir = str(row["local_dir"] or "").strip()
            source_dir = Path(raw_local_dir) if raw_local_dir else None
            material_dir = (
                source_dir
                if source_dir is not None and source_dir.is_dir()
                else root / "_publish_cache" / f"product-{int(row['id'])}"
            )
            material_dir.mkdir(parents=True, exist_ok=True)

            if source_dir is not None and source_dir.is_dir():
                for source_file in source_dir.iterdir():
                    if not source_file.is_file():
                        continue
                    if source_file.suffix.lower() in IMAGE_EXTENSIONS:
                        continue
                    shutil.copy2(source_file, target / source_file.name)

            media_state = publish_media_gate(row)
            if media_state.get("ready") is not True:
                raise RuntimeError(
                    f"Product #{int(row['id'])} publish media is not ready: "
                    + "; ".join(media_state.get("missing") or [])
                )
            selected_urls = [str(item["source_url"]) for item in media_state["items"]]
            local_image_files = _copy_publish_media(media_state["items"], target)
            local_video_files = _copy_publish_videos(dict(row), source_dir, target)

            editorial = {
                key: row[key]
                for key in row.keys()
                if key not in {"id", "created_at", "updated_at"}
            }
            editorial["desktop_product_id"] = int(row["id"])
            editorial["batch_uuid"] = batch_uuid
            editorial["local_category_name"] = (
                str(row["local_category_slug"] or "").strip() or "سایر محصولات"
            )
            editorial["fingerprint"] = (
                str(row["fingerprint"] or "").strip()
                or product_fingerprint(
                    row["source_code"],
                    row["external_id"],
                    row["source_url"],
                )
            )
            editorial["source_hash"] = (
                str(row["source_hash"] or "").strip()
                or source_payload_hash(editorial)
            )
            editorial["images_json"] = json.dumps(selected_urls, ensure_ascii=False)
            editorial["selected_images_json"] = json.dumps(selected_urls, ensure_ascii=False)
            editorial["primary_image_url"] = selected_urls[0] if selected_urls else ""
            editorial["local_image_files_json"] = json.dumps(local_image_files, ensure_ascii=False)
            editorial["local_video_files_json"] = json.dumps(local_video_files, ensure_ascii=False)
            editorial["workflow_status"] = "batched"
            editorial["batch_local_image_count"] = len(local_image_files)
            editorial["batch_local_video_count"] = len(local_video_files)

            editorial_rel = f"models/{target.name}/desktop_editorial.json"
            (target / "desktop_editorial.json").write_text(
                json.dumps(editorial, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            manifest.append({
                "desktop_product_id": int(row["id"]),
                "source_code": row["source_code"],
                "external_id": row["external_id"],
                "editorial": editorial_rel,
                "selected_images": len(selected_urls),
                "local_images": len(local_image_files),
                "local_videos": len(local_video_files),
                "fingerprint": editorial["fingerprint"],
                "source_hash": editorial["source_hash"],
            })
            batched_ids.append(int(row["id"]))

        (building / "batch_manifest.json").write_text(
            json.dumps({
                "schema_version": "8.5",
                "batch_uuid": batch_uuid,
                "batch_name": name,
                "models": manifest,
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        validation = validate_batch_package(building)
        building.rename(batch)
    except Exception:
        shutil.rmtree(building, ignore_errors=True)
        raise

    for product_id in batched_ids:
        db.update_product(product_id, {"workflow_status": "batched"})
        db.record_sync_receipt(
            product_id,
            batch_uuid,
            "desktop_batch_ready",
            "",
            {
                "batch_name": name,
                "models": validation.get("models"),
                "images": validation.get("images"),
            },
        )
    db.set_setting("last_batch_dir", str(batch))
    db.set_setting("last_batch_uuid", batch_uuid)
    if progress:
        progress(25, f"Batch آماده شد • {len(batched_ids)} محصول")

    return {
        "batch": batch,
        "batch_uuid": batch_uuid,
        "validation": validation,
        "product_ids": batched_ids,
    }


def _record_failed(
    db,
    product_ids,
    batch_uuid: str,
    batch_name: str,
    error: str,
) -> None:
    now = utc_now()
    for product_id in product_ids:
        db.record_sync_receipt(
            product_id,
            batch_uuid,
            "desktop_publish_failed",
            "",
            {"batch_name": batch_name, "error": error},
        )
        db.update_product(product_id, {
            "server_status": "failed",
            "product_sync_error": error[:1000],
            "last_synced_at": now,
        })


def guard_site_revisions(
    db,
    settings,
    product_ids,
    *,
    server_getter=get_site_product,
) -> dict[str, Any]:
    safe: list[int] = []
    conflicts: list[dict[str, Any]] = []
    for product_id in _ids(product_ids):
        row = db.product(product_id)
        if row is None:
            continue
        server_product_id = int(row["server_product_id"] or 0)
        local_revision = int(row["server_product_revision"] or 0)
        if server_product_id <= 0:
            safe.append(product_id)
            continue
        try:
            server = server_getter(settings, server_product_id)
            profile = (
                server.get("profile")
                if isinstance(server.get("profile"), dict)
                else {}
            )
            server_revision = int(profile.get("sync_revision") or 0)
            if server_revision != local_revision:
                detail = (
                    f"Site revision {server_revision} != Local accepted revision "
                    f"{local_revision}. Pull Site changes before publishing."
                )
                db.update_product(product_id, {"last_sync_conflict": detail})
                conflicts.append({
                    "product_id": product_id,
                    "server_product_id": server_product_id,
                    "local_revision": local_revision,
                    "server_revision": server_revision,
                    "missing": [detail],
                })
                continue
            db.update_product(product_id, {"last_sync_conflict": ""})
            safe.append(product_id)
        except BridgeNotFoundError:
            before = dict(row)
            db.update_product(product_id, {
                "server_product_id": 0,
                "server_product_revision": 0,
                "server_slider_id": 0,
                "server_slider_revision": 0,
                "workflow_status": "approved",
                "needs_update": 1,
                "last_sync_conflict": "",
                "product_sync_error": "",
            })
            try:
                db.save_history(
                    product_id,
                    "qt_site_product_missing_republish",
                    before,
                    dict(db.product(product_id)),
                    "Site Product was removed; preserved source asset identity and reopened Product recreation.",
                )
            except Exception:
                pass
            safe.append(product_id)
        except Exception as exc:
            detail = (
                "Site revision verification failed; publish stopped closed: "
                f"{type(exc).__name__}: {exc}"
            )
            db.update_product(product_id, {"last_sync_conflict": detail})
            conflicts.append({
                "product_id": product_id,
                "server_product_id": server_product_id,
                "local_revision": local_revision,
                "server_revision": None,
                "missing": [detail],
            })
    return {"safe_ids": safe, "conflicts": conflicts}


def publish_many(
    db,
    stage_core,
    settings,
    product_ids,
    *,
    progress: Progress | None = None,
    batch_root: Path | None = None,
    uploader=upload_batch,
    importer=import_batch,
    server_getter=get_site_product,
    readiness_checker=test_publish_readiness,
) -> dict[str, Any]:
    requested = _ids(product_ids)
    _refresh_publish_pricing_snapshots(db, requested)
    preflight = preflight_many(db, stage_core, requested)
    queued = list(preflight["queued_ids"])

    if queued:
        readiness = dict(readiness_checker(settings) or {})
        if readiness.get("ready") is not True:
            blockers = [
                str(item).strip()
                for item in (readiness.get("blockers") or [])
                if str(item).strip()
            ]
            detail = "، ".join(blockers[:12]) or "receiver_not_ready"
            raise RuntimeError(
                "گیرنده انتشار سایت آماده نیست؛ قبل از FTP/Import مشکل Host را رفع کن: "
                + detail
            )

    revision_guard = guard_site_revisions(
        db,
        settings,
        queued,
        server_getter=server_getter,
    )
    queued = list(revision_guard["safe_ids"])
    not_checked = sorted(set(preflight["publishable_ids"]) - set(preflight["queued_ids"]))
    skipped = list(preflight["blocked"])
    skipped.extend(list(revision_guard["conflicts"]))
    skipped.extend(
        {
            "product_id": product_id,
            "missing": ["تیک «آماده انتشار» برای این محصول فعال نیست."],
        }
        for product_id in not_checked
    )

    if not queued:
        return {
            "requested": len(requested),
            "published": 0,
            "failed": 0,
            "skipped": skipped,
            "skipped_count": len(skipped),
            "items": [],
        }

    batch_info = build_publish_batch(
        db,
        queued,
        batch_root=batch_root,
        progress=progress,
    )
    batch = Path(batch_info["batch"])
    batch_uuid = str(batch_info["batch_uuid"])
    batch_ids = list(batch_info["product_ids"])

    for product_id in batch_ids:
        db.record_sync_receipt(
            product_id,
            batch_uuid,
            "desktop_publish_started",
            "",
            {"batch_name": batch.name, "stage": "publish_start"},
        )

    try:
        if progress:
            progress(35, "شروع FTP Upload")
        ftp_result = uploader(
            settings,
            batch,
            (lambda line: progress(55, str(line))) if progress else None,
        )
        for product_id in batch_ids:
            db.record_sync_receipt(
                product_id,
                batch_uuid,
                "desktop_ftp_uploaded",
                "",
                dict(ftp_result or {}),
            )
        if progress:
            progress(70, "FTP کامل شد • شروع Bridge Import")
        ack = importer(settings, batch.name, batch_uuid)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        _record_failed(db, batch_ids, batch_uuid, batch.name, error)
        raise RuntimeError(f"انتشار گروهی ناموفق بود: {error}") from exc

    ack_items = {
        int(item.get("desktop_product_id") or 0): dict(item)
        for item in (ack.get("items") or [])
        if isinstance(item, dict)
        and int(item.get("desktop_product_id") or 0) > 0
    }
    published = 0
    failed = 0
    results: list[dict[str, Any]] = []
    now = utc_now()

    for product_id in batch_ids:
        row = db.product(product_id)
        if row is None:
            continue
        item = ack_items.get(product_id)
        if item is None:
            item = {
                "desktop_product_id": product_id,
                "status": "failed",
                "error": "Bridge ACK برای محصول برنگشت.",
            }

        state = str(item.get("status") or "")
        incoming_server_id = str(item.get("server_id") or "")
        payload = dict(item)
        payload["diagnostic_id"] = str(ack.get("diagnostic_id") or "")
        payload["bridge_status"] = str(ack.get("bridge_status") or "")
        payload["batch_name"] = batch.name
        db.record_sync_receipt(
            product_id,
            batch_uuid,
            state,
            incoming_server_id,
            payload,
        )

        confirmed = ack_item_confirms_publish(
            item,
            row,
            require_store_visibility=True,
        )
        values = {
            "server_status": state,
            "last_synced_at": now,
            "last_sync_conflict": "",
        }

        if confirmed:
            server_id = incoming_server_id
            values.update({
                "server_id": server_id,
                "server_ack_json": json.dumps(payload, ensure_ascii=False),
                "server_product_id": int(
                    item.get("server_product_id")
                    or item.get("product_id")
                    or 0
                ),
                "server_product_revision": int(item.get("product_revision") or 0),
                "server_slider_id": int(item.get("slider_id") or 0),
                "server_slider_revision": int(item.get("slider_revision") or 0),
            })
        else:
            # A failed re-publish transaction must not erase the last verified
            # Site identity/ACK. The failure receipt above remains the complete
            # diagnostic record, while these stable fields keep the next retry
            # on the same Product instead of degrading into a create/unknown path.
            server_id = str(row["server_id"] or "")
            values.update({
                "server_id": server_id,
                "server_ack_json": str(row["server_ack_json"] or "{}"),
                "server_product_id": int(row["server_product_id"] or 0),
                "server_product_revision": int(row["server_product_revision"] or 0),
                "server_slider_id": int(row["server_slider_id"] or 0),
                "server_slider_revision": int(row["server_slider_revision"] or 0),
            })

        if confirmed:
            values.update({
                "workflow_status": "uploaded",
                "upload_ready": 0,
                "needs_update": 0,
                "product_sync_error": "",
                "published_at": row["published_at"] or now,
                "last_synced_source_hash": (
                    item.get("source_hash")
                    or row["source_hash"]
                    or ""
                ),
            })
            published += 1
            ok = True
        else:
            values["product_sync_error"] = str(
                item.get("error")
                or "ACK دریافت شد اما محصول در Store عمومی تأیید نشد."
            )[:1000]
            failed += 1
            ok = False

        db.update_product(product_id, values)
        try:
            db.save_history(
                product_id,
                "qt_bulk_site_publish",
                dict(row),
                dict(db.product(product_id)),
                f"Bulk site publish ok={int(ok)} batch={batch_uuid}",
            )
        except Exception:
            pass
        results.append({
            "product_id": product_id,
            "ok": ok,
            "status": state,
            "server_id": server_id,
            "server_product_id": int(item.get("product_id") or 0),
            "product_url": str(item.get("product_url") or ""),
            "error": str(
                item.get("error")
                or values.get("product_sync_error")
                or ""
            ),
        })

    if progress:
        progress(
            100,
            f"انتشار تمام شد • موفق {published} • خطا {failed}",
        )
    return {
        "requested": len(requested),
        "batch_uuid": batch_uuid,
        "batch_name": batch.name,
        "published": published,
        "failed": failed,
        "skipped": skipped,
        "skipped_count": len(skipped),
        "items": results,
        "ack": ack,
    }
