from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from typing import Any

from .db import normalize_url


ALLOWED_COMMERCIAL_STATUSES = frozenset({"allowed", "owned", "public_domain"})


def _json(value: Any, default):
    if isinstance(value, (list, dict)):
        return value
    try:
        result = json.loads(value or "")
        return result if isinstance(result, type(default)) else default
    except Exception:
        return default


def product_fingerprint(source_code: str, external_id: str, source_url: str) -> str:
    canonical = f"{(source_code or '').strip().lower()}|{(external_id or '').strip()}|{normalize_url(source_url or '')}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def source_payload_hash(payload: dict[str, Any]) -> str:
    fields = {
        "source_url": normalize_url(str(payload.get("source_url") or "")),
        "source_title": payload.get("source_title") or "",
        "source_description": payload.get("source_description") or "",
        "author_name": payload.get("author_name") or "",
        "license_name": payload.get("license_name") or "",
        "license_url": payload.get("license_url") or "",
        "source_category": payload.get("source_category") or "",
        "source_categories": _json(payload.get("source_categories_json"), []),
        "tags": _json(payload.get("tags_json"), []),
        "images": _json(payload.get("images_json"), []),
        "files": _json(payload.get("file_links_json"), []),
        "specs": _json(payload.get("source_specs_json"), {}),
        "source_price": payload.get("source_price"),
        "source_currency": payload.get("source_currency") or "",
        "estimated_weight_grams": payload.get("estimated_weight_grams"),
        "estimated_print_minutes": payload.get("estimated_print_minutes"),
        "source_rating": payload.get("source_rating"),
        "source_rating_count": payload.get("source_rating_count"),
        "source_like_count": payload.get("source_like_count"),
        "source_download_count": payload.get("source_download_count"),
        "source_view_count": payload.get("source_view_count"),
        "source_published_at": payload.get("source_published_at") or "",
        "source_updated_at": payload.get("source_updated_at") or "",
    }
    raw = json.dumps(fields, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def product_diff(old: dict[str, Any] | Any, new: dict[str, Any]) -> dict[str, dict[str, Any]]:
    def get(obj, key, default=""):
        if isinstance(obj, dict):
            return obj.get(key, default)
        try:
            return obj[key]
        except Exception:
            return default

    keys = [
        "source_title", "source_description", "author_name", "license_name", "license_url",
        "source_category", "source_categories_json", "tags_json", "images_json", "file_links_json",
        "source_specs_json", "source_price", "source_currency", "estimated_weight_grams",
        "estimated_print_minutes", "source_rating", "source_rating_count", "source_like_count",
        "source_download_count", "source_view_count", "source_published_at", "source_updated_at",
    ]
    out: dict[str, dict[str, Any]] = {}
    for key in keys:
        before = get(old, key, None)
        after = new.get(key, before)
        if key.endswith("_json"):
            before_cmp = json.dumps(_json(before, [] if key != "source_specs_json" else {}), ensure_ascii=False, sort_keys=True)
            after_cmp = json.dumps(_json(after, [] if key != "source_specs_json" else {}), ensure_ascii=False, sort_keys=True)
        else:
            before_cmp, after_cmp = before, after
        if before_cmp != after_cmp:
            out[key] = {"before": before, "after": after}
    return out


def diff_summary(diff: dict[str, dict[str, Any]]) -> str:
    labels = {
        "source_title": "عنوان اصلی", "source_description": "توضیحات", "author_name": "طراح/سازنده",
        "license_name": "مجوز", "license_url": "لینک مجوز", "source_category": "دسته منبع",
        "source_categories_json": "مسیر دسته‌بندی", "tags_json": "تگ‌ها", "images_json": "تصاویر",
        "file_links_json": "فایل‌ها", "source_specs_json": "مشخصات", "source_price": "قیمت منبع",
        "source_currency": "ارز", "estimated_weight_grams": "وزن", "estimated_print_minutes": "زمان چاپ",
        "source_rating": "امتیاز", "source_rating_count": "تعداد رأی", "source_like_count": "پسند",
        "source_download_count": "دانلود", "source_view_count": "بازدید",
        "source_published_at": "تاریخ انتشار منبع", "source_updated_at": "تاریخ بروزرسانی منبع",
    }
    if not diff:
        return "هیچ تغییر محتوایی نسبت به آخرین دریافت پیدا نشد."
    lines = []
    for key, change in diff.items():
        if key in {"images_json", "file_links_json", "tags_json", "source_categories_json"}:
            before = _json(change["before"], [])
            after = _json(change["after"], [])
            lines.append(f"• {labels.get(key,key)}: {len(before)} ← {len(after)}")
        elif key == "source_specs_json":
            before = _json(change["before"], {})
            after = _json(change["after"], {})
            lines.append(f"• {labels.get(key,key)}: {len(before)} ← {len(after)} فیلد")
        else:
            before = str(change["before"] or "")
            after = str(change["after"] or "")
            if len(before) > 70: before = before[:67] + "…"
            if len(after) > 70: after = after[:67] + "…"
            lines.append(f"• {labels.get(key,key)}: {before!r} → {after!r}")
    return "\n".join(lines)


def merge_refetch(old: Any, fresh: dict[str, Any]) -> dict[str, Any]:
    """Apply source-derived fields while preserving all human editorial decisions."""
    preserve = {
        "source_code", "external_id",
        "title_fa", "short_description_fa", "description_fa", "local_category_slug",
        "material_price_per_gram", "suggested_price", "final_price", "price_is_final",
        "approved_for_sale", "publish_as_product", "publish_as_portfolio", "translation_status",
        "commercial_status", "workflow_status", "upload_ready", "custom_notes", "categories_fa_json",
        "specs_fa_json", "tags_fa_json", "seo_title_fa", "seo_description_fa", "sales_bullets_json",
        "social_caption_fa", "image_alt_texts_json", "ai_suggested_category_slug", "ai_confidence",
        "content_pack_json", "server_id", "server_status", "server_ack_json", "last_synced_at",
        "last_synced_source_hash", "published_at", "last_ai_at", "product_sync_error",
        "product_type", "use_description", "dimensions", "materials_json", "colors_json",
        "availability_status", "stock_quantity", "lead_time_min_days", "lead_time_max_days",
        "has_3d_file", "source_name", "technical_features_json", "keywords_json",
        "is_blocked", "blocked_at", "blocked_reason", "source_state",
    }
    result = dict(fresh)
    old_keys = set(old.keys()) if hasattr(old, "keys") else set()
    for key in preserve:
        if key in old_keys:
            result[key] = old[key]

    old_selected = _json(old["selected_images_json"] if "selected_images_json" in old_keys else "[]", [])
    new_all = _json(fresh.get("images_json"), [])
    kept = [url for url in old_selected if url in new_all]
    fresh_selected = _json(fresh.get("selected_images_json"), [])
    if not kept:
        kept = fresh_selected
    result["selected_images_json"] = json.dumps(kept, ensure_ascii=False)
    old_primary = old["primary_image_url"] if "primary_image_url" in old_keys else ""
    result["primary_image_url"] = old_primary if old_primary in new_all else (kept[0] if kept else (new_all[0] if new_all else ""))
    return result


def new_batch_uuid() -> str:
    return str(uuid.uuid4())


def parse_ack_lines(stdout: str) -> dict[str, Any] | None:
    marker = "CATALOG_ACK_JSON="
    for line in reversed((stdout or "").splitlines()):
        if line.startswith(marker):
            try:
                value = json.loads(line[len(marker):])
                return value if isinstance(value, dict) else None
            except Exception:
                return None
    return None


def commercial_license_allows_publish(status: Any) -> bool:
    return str(status or "").strip().lower() in ALLOWED_COMMERCIAL_STATUSES


def ack_item_confirms_publish(
    item: dict[str, Any],
    row: Any,
    *,
    require_store_visibility: bool = False,
) -> bool:
    """Return True only when the ACK contains every requested publish target.

    Legacy callers keep the pre-Phase49 contract by default. Phase49 publish
    paths opt in to strict store visibility, which prevents an inactive Product
    from being marked as published on the desktop.
    """
    if str(item.get("status") or "") not in {"created", "updated"}:
        return False
    if not str(item.get("server_id") or "").strip():
        return False

    def row_flag(name: str) -> bool:
        try:
            return bool(int(row[name] or 0))
        except Exception:
            return False

    wants_product = row_flag("publish_as_product")
    wants_portfolio = row_flag("publish_as_portfolio")
    if not (wants_product or wants_portfolio):
        return False
    if wants_product and not item.get("product_id"):
        return False
    if require_store_visibility and wants_product and item.get("visible_on_store") is not True:
        return False
    if wants_portfolio and not item.get("portfolio_id"):
        return False
    return True


def safe_slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return value[:80] or "external-other"
