from __future__ import annotations

import json
import re
import shutil
import time
from pathlib import Path
from typing import Any, Callable

from .batch_packaging import (
    IMAGE_EXTENSIONS,
    copy_images_into_model,
    materialize_selected_images,
    validate_batch_package,
)
from .crawler import download_public_file
from .db import utc_now
from .site_connection import import_batch, test_publish_readiness, upload_batch
from .epic49_site_sync import get_product as get_site_product
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


def _row_dict(row) -> dict[str, Any]:
    return dict(row) if row is not None else {}


def _safe_part(value: Any, fallback: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip()).strip("._-")
    return text[:96] or fallback


def publish_gate(db, stage_core, product_id: int) -> dict[str, Any]:
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
    if already_public:
        missing.append("محصول قبلاً منتشر شده و تغییر جدیدی برای ارسال ندارد")

    deduped = list(dict.fromkeys(str(item) for item in missing if str(item).strip()))
    return {
        "product_id": product_id,
        "ready": not deduped,
        "missing": deduped,
        "already_public": already_public,
    }


def preflight_many(db, stage_core, product_ids) -> dict[str, Any]:
    requested_ids = _ids(product_ids)
    publishable_ids: list[int] = []
    queued_ids: list[int] = []
    blocked: list[dict[str, Any]] = []

    for product_id in requested_ids:
        state = publish_gate(db, stage_core, product_id)
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
    preflight = preflight_many(db, stage_core, product_ids)
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
    name = "desktop_catalog_v85_" + time.strftime("%Y%m%d_%H%M%S")
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

            selected_pairs = materialize_selected_images(
                row,
                material_dir,
                downloader=_download_batch_image,
            )
            selected_urls = [url for url, _path in selected_pairs]
            local_image_files = copy_images_into_model(selected_pairs, target)

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
            editorial["workflow_status"] = "batched"
            editorial["batch_local_image_count"] = len(local_image_files)

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
        server_id = str(item.get("server_id") or "")
        payload = dict(item)
        payload["diagnostic_id"] = str(ack.get("diagnostic_id") or "")
        payload["bridge_status"] = str(ack.get("bridge_status") or "")
        payload["batch_name"] = batch.name
        db.record_sync_receipt(
            product_id,
            batch_uuid,
            state,
            server_id,
            payload,
        )

        values = {
            "server_id": server_id,
            "server_status": state,
            "server_ack_json": json.dumps(payload, ensure_ascii=False),
            "last_synced_at": now,
            "server_product_id": int(
                item.get("server_product_id")
                or item.get("product_id")
                or 0
            ),
            "server_product_revision": int(item.get("product_revision") or 0),
            "server_slider_id": int(item.get("slider_id") or 0),
            "server_slider_revision": int(item.get("slider_revision") or 0),
            "last_sync_conflict": "",
        }

        if ack_item_confirms_publish(
            item,
            row,
            require_store_visibility=True,
        ):
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
