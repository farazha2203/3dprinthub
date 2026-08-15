from __future__ import annotations
import json
from typing import Any

STATUS_LABELS = {
    "new": "جدید",
    "needs_content": "نیازمند محتوا",
    "ready": "آماده انتشار",
    "queued": "در صف ارسال",
    "published": "منتشرشده",
    "needs_update": "نیازمند بروزرسانی",
    "error": "خطا",
    "blocked": "بلاک‌شده",
}


def _json_list(raw: Any) -> list:
    if isinstance(raw, list): return raw
    try:
        value=json.loads(raw or "[]")
        return value if isinstance(value,list) else []
    except Exception:return []


def product_state(row: Any) -> str:
    def g(k, default=""):
        try:return row[k]
        except Exception:return default
    if int(g("is_blocked", 0) or 0):
        return "blocked"
    if str(g("server_status")) == "failed" or str(g("product_sync_error")):
        return "error"
    if int(g("needs_update",0) or 0):
        return "needs_update"
    if str(g("server_id")) and str(g("workflow_status")) == "uploaded":
        return "published"
    if int(g("upload_ready",0) or 0):
        return "queued"
    if not str(g("title_fa")).strip() or not str(g("description_fa")).strip() or str(g("content_status")) != "ready":
        return "needs_content" if str(g("server_id")) else "new"
    if int(g("approved_for_sale",0) or 0) and int(g("publish_as_product",0) or 0):
        return "ready"
    return "new"


def image_count(row: Any) -> int:
    try:return len(_json_list(row["images_json"]))
    except Exception:return 0


def selected_image_count(row: Any) -> int:
    try:return len(_json_list(row["selected_images_json"]))
    except Exception:return 0


def pricing_suggestion(weight_grams: float | None, material_price_per_gram: int | float, print_minutes: float | None = None,
                       minimum_price: int = 350_000, labor_base: int = 150_000,
                       machine_per_hour: int = 90_000, margin: float = 1.55) -> int:
    """Transparent deterministic suggested price. AI is not allowed to invent source facts."""
    weight=max(0.0,float(weight_grams or 0))
    material=max(0.0,float(material_price_per_gram or 0))
    hours=max(0.0,float(print_minutes or 0))/60.0
    direct=(weight*material)+(hours*machine_per_hour)+labor_base
    if direct <= 0:
        return minimum_price
    rounded=max(minimum_price,int(round((direct*max(1.0,margin))/10_000.0)*10_000))
    return rounded


def should_mark_needs_update(row: Any, new_source_hash: str) -> bool:
    try:
        server_id=str(row["server_id"] or "")
        synced_hash=str(row["last_synced_source_hash"] or "")
        current_hash=str(row["source_hash"] or "")
    except Exception:
        return False
    baseline=synced_hash or current_hash
    return bool(server_id and baseline and new_source_hash and baseline != new_source_hash)
