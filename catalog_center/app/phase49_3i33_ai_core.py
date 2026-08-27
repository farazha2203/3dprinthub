from __future__ import annotations

import asyncio
import base64
import io
import json
import math
import re
import shutil
import time
from pathlib import Path
from typing import Any

from PIL import Image

from . import crawler
from . import phase49_3c_image_pipeline as image_pipeline
from .ai_providers import AIProviderClient, _json_request, _strip_json_fence, response_output_text
from .openai_content import CONTENT_SCHEMA, validate_content_pack
from .phase49_3i18_operator_editing import _list, ai_updates
from .phase49_3i19_source_identity import canonical_source_title, is_generic_source_title
from .phase49_3i25_product_first_workflow import makerworld_profile_weight_from_html, normalized_source_facts
from .phase49_3i31_smart_link_bulk_ai import build_image_metadata_updates
from .phase49_diagnostics import audit_event, redact


PHASE = "49.3I.33"

AI_MODES = {
    "link": "ترجمه + SEO با لینک محصول",
    "data": "ترجمه + SEO با دیتای دریافتی",
    "screenshot": "ترجمه + SEO از اسکرین‌شات",
    "repair": "رفع نقص با هوش مصنوعی",
}
AI_MODE_BY_LABEL = {label: key for key, label in AI_MODES.items()}

DESKTOP_COLUMNS = {
    "source_save_count": "INTEGER NOT NULL DEFAULT 0",
    "source_boost_count": "INTEGER NOT NULL DEFAULT 0",
    "source_print_count": "INTEGER NOT NULL DEFAULT 0",
    "source_print_profiles_json": "TEXT NOT NULL DEFAULT '[]'",
    "source_page_screenshot_path": "TEXT NOT NULL DEFAULT ''",
    "ai_last_mode": "TEXT NOT NULL DEFAULT ''",
    "ai_last_completed_at": "TEXT NOT NULL DEFAULT ''",
}

BLOCKED_FACT_TOKENS = ("material", "filament", "colour", "color")

COMMON_TRANSLATIONS = {
    "christmas tree": ("درخت", "کریسمس"),
    "night light": ("چراغ",),
    "lamp": ("چراغ",),
    "stand": ("پایه",),
    "holder": ("نگهدار", "پایه"),
    "organizer": ("نظم", "سامان", "مرتب"),
    "organiser": ("نظم", "سامان", "مرتب"),
    "bracket": ("براکت", "پایه"),
    "mount": ("پایه", "نگهدار"),
    "box": ("جعبه",),
    "case": ("قاب", "محفظه"),
    "vase": ("گلدان",),
    "pot": ("گلدان",),
    "gear": ("چرخ", "دنده"),
    "clip": ("گیره", "خار", "کلیپس"),
    "tray": ("سینی",),
    "shelf": ("قفسه",),
    "hook": ("قلاب",),
    "keychain": ("جاکلیدی",),
    "toy": ("اسباب", "بازی"),
    "flexi": ("انعطاف", "مفصل"),
}

SCREENSHOT_FACT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "source_title": {"type": "string"},
        "source_description": {"type": "string"},
        "estimated_weight_grams": {"type": ["number", "null"]},
        "estimated_print_minutes": {"type": ["number", "null"]},
        "like_count": {"type": ["integer", "null"]},
        "save_count": {"type": ["integer", "null"]},
        "download_count": {"type": ["integer", "null"]},
        "print_count": {"type": ["integer", "null"]},
        "boost_count": {"type": ["integer", "null"]},
        "print_profiles": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "print_minutes": {"type": ["number", "null"]},
                    "plate_count": {"type": ["integer", "null"]},
                    "layer_height_mm": {"type": ["number", "null"]},
                    "wall_count": {"type": ["integer", "null"]},
                    "infill_percent": {"type": ["number", "null"]},
                    "rating": {"type": ["number", "null"]},
                },
                "required": [
                    "name", "print_minutes", "plate_count", "layer_height_mm",
                    "wall_count", "infill_percent", "rating",
                ],
            },
        },
    },
    "required": [
        "source_title", "source_description", "estimated_weight_grams",
        "estimated_print_minutes", "like_count", "save_count", "download_count",
        "print_count", "boost_count", "print_profiles",
    ],
}


def row_value(row, key: str, default=""):
    try:
        value = row.get(key, default) if isinstance(row, dict) else row[key]
    except Exception:
        value = default
    return default if value is None else value


def json_value(value, kind):
    if isinstance(value, kind):
        return value
    try:
        parsed = json.loads(value or ("[]" if kind is list else "{}"))
    except Exception:
        return kind()
    return parsed if isinstance(parsed, kind) else kind()


def positive(value):
    try:
        number = float(value)
    except Exception:
        return None
    return number if math.isfinite(number) and 0 < number < 10_000_000 else None


def count_value(value):
    number = positive(value)
    return int(round(number)) if number is not None else None


def sanitize_product_facts(value: Any) -> Any:
    if isinstance(value, dict):
        output = {}
        for key, item in value.items():
            folded = re.sub(r"[^a-z0-9]+", "_", str(key).casefold()).strip("_")
            if any(token in folded for token in BLOCKED_FACT_TOKENS):
                continue
            output[key] = sanitize_product_facts(item)
        return output
    if isinstance(value, list):
        return [sanitize_product_facts(item) for item in value]
    return value


def safe_text(value, limit=12000) -> str:
    if value in (None, "", [], {}):
        return ""
    if isinstance(value, str):
        return " ".join(value.split())[:limit]
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "، ".join(filter(None, (safe_text(item, 1000) for item in value[:80])))[:limit]
    if isinstance(value, dict):
        rows = []
        for key, item in list(value.items())[:100]:
            text = safe_text(item, 1800)
            if text:
                rows.append(f"- {key}: {text}")
        return "\n".join(rows)[:limit]
    return safe_text(str(value), limit)


def _max_metric(nodes, names):
    keys = {name.casefold() for name in names}
    values = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        for key, value in node.items():
            if str(key).casefold() in keys:
                number = count_value(value)
                if number is not None:
                    values.append(number)
    return max(values) if values else None


def _profile_minutes(node):
    for key in ("printMinutes", "print_minutes", "durationMinutes", "estimatedPrintMinutes", "printingMinutes"):
        number = positive(node.get(key))
        if number is not None:
            return round(number, 2)
    for key in ("printTimeSeconds", "print_time_seconds", "durationSeconds", "prediction", "predictionSeconds"):
        number = positive(node.get(key))
        if number is not None:
            return round(number / 60.0, 2)
    return None


def makerworld_evidence_from_html(html: str, source_url: str) -> dict[str, Any]:
    if "makerworld.com" not in str(source_url or "").lower():
        return {}
    try:
        nodes = list(crawler._walk_json(crawler._next_data(html)))
    except Exception:
        return {}

    result = {}
    metric_keys = {
        "like_count": {"likeCount", "likes", "like_count"},
        "save_count": {"collectCount", "favoriteCount", "bookmarkCount", "saveCount", "collect_count"},
        "download_count": {"downloadCount", "downloads", "download_count"},
        "print_count": {"printCount", "prints", "print_count"},
        "boost_count": {"boostCount", "boosts", "boost_count"},
    }
    for target, keys in metric_keys.items():
        value = _max_metric(nodes, keys)
        if value is not None:
            result[target] = value

    match = re.search(r"profileId[-=](\d+)", str(source_url or ""), re.I)
    wanted = match.group(1) if match else ""
    profiles = []
    seen = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        identity = str(node.get("id") or node.get("profileId") or node.get("profile_id") or "")
        minutes = _profile_minutes(node)
        settings = any(
            key in node for key in (
                "layerHeight", "layer_height", "wallCount", "wall_count",
                "infill", "infillPercent", "plateCount", "plate_count",
            )
        )
        if minutes is None and not settings:
            continue
        name = str(node.get("profileName") or node.get("title") or node.get("name") or node.get("instanceName") or "").strip()
        if not name and not identity:
            continue
        row = {
            "id": identity,
            "name": name,
            "print_minutes": minutes,
            "plate_count": count_value(node.get("plateCount") or node.get("plate_count")),
            "layer_height_mm": positive(node.get("layerHeight") or node.get("layer_height")),
            "wall_count": count_value(node.get("wallCount") or node.get("wall_count") or node.get("walls")),
            "infill_percent": positive(node.get("infillPercent") or node.get("infill_percent") or node.get("infill")),
            "rating": positive(node.get("rating") or node.get("score")),
        }
        signature = json.dumps(row, ensure_ascii=False, sort_keys=True)
        if signature in seen:
            continue
        seen.add(signature)
        profiles.append(row)
        if len(profiles) >= 16:
            break
    if wanted:
        profiles.sort(key=lambda item: 0 if str(item.get("id") or "") == wanted else 1)
    profiles = profiles[:10]
    result["print_profiles"] = profiles
    exact = next((item for item in profiles if wanted and str(item.get("id") or "") == wanted), profiles[0] if profiles else None)
    if exact and exact.get("print_minutes"):
        result["estimated_print_minutes"] = exact["print_minutes"]
    return result


def _profiles_text(profiles) -> str:
    rows = []
    for index, item in enumerate(profiles[:10], 1):
        bits = []
        for key, label, suffix in (
            ("print_minutes", "زمان چاپ", "دقیقه"),
            ("plate_count", "صفحه چاپ", ""),
            ("layer_height_mm", "ارتفاع لایه", "میلی‌متر"),
            ("wall_count", "دیواره", ""),
            ("infill_percent", "پرشدگی", "٪"),
            ("rating", "امتیاز", ""),
        ):
            value = item.get(key)
            if value not in (None, ""):
                bits.append(f"{label} {value}{(' ' + suffix) if suffix else ''}")
        rows.append(f"- {item.get('name') or f'پروفایل {index}'}: " + ("، ".join(bits) if bits else "جزئیات محدود"))
    return "\n".join(rows)


def structured_ai_text(source_url: str, source: dict[str, Any], evidence=None) -> str:
    source = sanitize_product_facts(dict(source or {}))
    evidence = sanitize_product_facts(dict(evidence or {}))
    lines = [
        "مرجع واقعی محصول برای ترجمه و SEO",
        f"لینک منبع: {str(source_url or '').strip()}",
        "فقط از شواهد زیر استفاده کن؛ داده ناموجود را حدس نزن.",
        "متریال و رنگ عمداً حذف شده‌اند و فقط اپراتور 3DPrintHub آن‌ها را تعیین می‌کند.",
    ]
    for label, raw in (
        ("توضیحات منبع", source.get("source_description")),
        ("مشخصات منبع", source.get("source_specs") or source.get("source_specs_json")),
        ("دسته/برچسب‌های منبع", source.get("source_category") or source.get("source_categories")),
        ("طراح / سازنده", source.get("author_name")),
        ("مجوز", source.get("license_name")),
    ):
        text = safe_text(raw)
        if text:
            lines.extend(("", f"## {label}", text))

    merged = {**source, **evidence}
    metrics = []
    for key, label, unit in (
        ("estimated_weight_grams", "وزن ثبت‌شده", "گرم"),
        ("estimated_print_minutes", "زمان چاپ", "دقیقه"),
        ("like_count", "تعداد پسند", ""),
        ("save_count", "تعداد ذخیره/Collection", ""),
        ("download_count", "تعداد دانلود", ""),
        ("print_count", "تعداد چاپ", ""),
        ("boost_count", "تعداد Boost", ""),
    ):
        value = merged.get(key)
        if value not in (None, ""):
            metrics.append(f"- {label}: {value}{(' ' + unit) if unit else ''}")
    if metrics:
        lines.extend(("", "## آمار و زمان/وزن قابل استناد", *metrics))
    profiles = merged.get("print_profiles") or []
    if isinstance(profiles, list) and profiles:
        lines.extend(("", "## پروفایل‌ها و تنظیمات چاپ", _profiles_text(profiles)))
    return "\n".join(lines).strip()[:26000]


def saved_source_for_ai(row) -> dict[str, Any]:
    return sanitize_product_facts({
        "source_title": str(row_value(row, "source_title", "") or "").strip(),
        "source_description": str(row_value(row, "source_description", "") or "").strip(),
        "source_specs": json_value(row_value(row, "source_specs_json", "{}"), dict),
        "source_categories": json_value(row_value(row, "source_categories_json", "[]"), list),
        "source_category": row_value(row, "source_category", ""),
        "author_name": row_value(row, "author_name", ""),
        "license_name": row_value(row, "license_name", ""),
        "estimated_weight_grams": row_value(row, "estimated_weight_grams", None),
        "estimated_print_minutes": row_value(row, "estimated_print_minutes", None),
        "like_count": row_value(row, "source_like_count", None),
        "save_count": row_value(row, "source_save_count", None),
        "download_count": row_value(row, "source_download_count", None),
        "print_count": row_value(row, "source_print_count", None),
        "boost_count": row_value(row, "source_boost_count", None),
        "print_profiles": json_value(row_value(row, "source_print_profiles_json", "[]"), list),
    })


def live_source_for_ai(app, row) -> dict[str, Any]:
    source_url = str(row_value(row, "source_url", "") or "").strip()
    if not source_url.startswith(("http://", "https://")):
        raise RuntimeError("لینک منبع معتبر برای این محصول ثبت نشده است.")
    html = crawler.public_http(source_url, 25)
    parsed = crawler.parse_product(html, source_url, "", []) or {}
    exact_weight = makerworld_profile_weight_from_html(html, source_url)
    if exact_weight is not None:
        parsed["estimated_weight_grams"] = exact_weight
    evidence = makerworld_evidence_from_html(html, source_url)
    if evidence.get("estimated_print_minutes") and not parsed.get("estimated_print_minutes"):
        parsed["estimated_print_minutes"] = evidence["estimated_print_minutes"]
    facts = normalized_source_facts(parsed, source_url)
    external_id = str(row_value(row, "external_id", "") or "")
    source_title = canonical_source_title(
        str(parsed.get("source_title") or row_value(row, "source_title", "") or ""),
        source_url,
        external_id,
        candidates=(parsed.get("source_title") or "", row_value(row, "source_title", "") or ""),
    )
    if not source_title or is_generic_source_title(source_title, external_id):
        raise RuntimeError("عنوان واقعی و معتبر محصول از لینک منبع استخراج نشد.")
    combined = sanitize_product_facts({**parsed, **facts})
    return {
        "source_url": source_url,
        "source_title": source_title,
        "source_description": structured_ai_text(source_url, combined, evidence),
        "raw_source_description": str(parsed.get("source_description") or "").strip(),
        "facts": {**sanitize_product_facts(facts), **evidence},
        "evidence": evidence,
    }


def _ai_instructions() -> str:
    return (
        "تو مترجم فنی فارسی و ویراستار SEO فروشگاه ایرانی 3DPrintHub هستی. "
        "ترجمه باید فارسی طبیعی و معنایی باشد؛ آوانویسی واژه‌های عمومی انگلیسی با حروف فارسی ممنوع است. "
        "برای نمونه stand=پایه، holder=نگهدارنده، Christmas tree=درخت کریسمس و flexi=انعطاف‌پذیر. "
        "Twistmas Tree یک بازی واژه برای Christmas Tree پیچ‌خورده/اسپیرال است؛ آن را «درخت کریسمس اسپیرال» یا ترجمه معنایی هم‌ارز بنویس، نه «تویست‌ماس تری». "
        "نام خاص یا برند را فقط وقتی ترجمه معنایی هویت را خراب می‌کند حفظ کن. "
        "source_title هویت قطعی محصول و source_description تنها منبع واقعیت است. "
        "وزن، زمان چاپ، لایک/ذخیره/دانلود/چاپ/Boost و تنظیمات layer/wall/infill/plate را فقط وقتی در منبع صریح‌اند در متن و مشخصات فنی منعکس کن. "
        "متریال و رنگ عمداً حذف شده‌اند؛ هیچ متریال یا رنگی نساز، پیشنهاد نده و material_recommendations را خالی برگردان. "
        "قیمت، موجودی، مجوز فروش و دسته داخلی سایت را حدس نزن. suggested_category_slug را خالی بگذار. "
        "عنوان فارسی، توضیح کوتاه و کامل، کاربرد، SEO title/description، عبارات هدف، sales bullets، social caption و Alt تصاویر را مختص همین محصول بساز. "
        "اگر داده‌ای نیست در content_notes ذکر کن. فقط JSON مطابق Schema و بدون Markdown برگردان."
    )


def title_quality_guard(source_title: str, title_fa: str) -> None:
    title = str(title_fa or "").strip()
    if not re.search(r"[\u0600-\u06ff]", title):
        raise RuntimeError("خروجی AI ترجمه فارسی معتبر نیست.")
    source = str(source_title or "").casefold()
    fa = title.replace("ي", "ی").replace("ك", "ک")
    if "twistmas tree" in source:
        required_groups = (
            ("درخت",),
            ("کریسمس",),
            ("اسپیرال", "مارپیچ", "پیچ"),
        )
        if any(not any(token in fa for token in group) for group in required_groups):
            raise RuntimeError(
                "ترجمه Twistmas Tree باید معنایی باشد (درخت کریسمس اسپیرال/مارپیچ)؛ آوانویسی «تویست‌ماس تری» پذیرفته نیست."
            )
    for english, tokens in COMMON_TRANSLATIONS.items():
        if english in source and not any(token in fa for token in tokens):
            raise RuntimeError(
                f"ترجمه AI برای «{english}» معنایی نیست و احتمال آوانویسی/فینگلیش وجود دارد؛ هیچ تغییری ذخیره نشد."
            )


def generate_translation_pack(provider: str, key: str, model: str, source_title: str, source_description: str, product_id: int):
    client = AIProviderClient(provider, key, model, product_id=product_id)
    payload = {"source_title": str(source_title or "").strip(), "source_description": str(source_description or "").strip()}
    if not payload["source_title"]:
        raise RuntimeError("عنوان منبع برای ترجمه/SEO خالی است.")
    result, selected_model = client.structured_response(
        instructions=_ai_instructions(),
        input_content=[{"type": "input_text", "text": json.dumps(payload, ensure_ascii=False)}],
        schema=CONTENT_SCHEMA,
        schema_name="catalog_content_pack_3i33",
        preferred_model=model,
    )
    result["material_recommendations"] = []
    result["suggested_category_slug"] = ""
    validate_content_pack(result, payload["source_title"])
    title_quality_guard(payload["source_title"], result.get("title_fa") or "")
    result["_ai_provider"] = provider
    result["_ai_model"] = selected_model
    return result


def screenshot_chunks(path: Path, max_chunks=4):
    with Image.open(path) as opened:
        image = opened.convert("RGB")
        if image.width > 1200:
            ratio = 1200 / float(image.width)
            image = image.resize((1200, max(1, int(image.height * ratio))), Image.Resampling.LANCZOS)
        chunks = max(1, min(max_chunks, int(math.ceil(image.height / 1500.0))))
        height = int(math.ceil(image.height / chunks))
        output = []
        for index in range(chunks):
            top = index * height
            bottom = min(image.height, (index + 1) * height)
            crop = image.crop((0, top, image.width, bottom))
            stream = io.BytesIO()
            crop.save(stream, "JPEG", quality=78, optimize=True)
            output.append(base64.b64encode(stream.getvalue()).decode("ascii"))
        return output


def screenshot_facts(provider: str, key: str, model: str, screenshot: Path, product_id: int):
    chunks = screenshot_chunks(screenshot)
    client = AIProviderClient(provider, key, model, product_id=product_id)
    exact_model = client.choose_model(model)
    prompt = (
        "این تصاویر بخش‌های یک اسکرین‌شات کامل صفحه واقعی محصول هستند. فقط داده قابل مشاهده را استخراج کن. "
        "عنوان، توضیح، وزن، زمان چاپ profileها، plate، layer height، walls، infill، rating و شمارنده‌های like/save/download/print/boost را در صورت مشاهده استخراج کن. "
        "متریال و رنگ را استخراج یا حدس نزن. زمان ساعت/دقیقه را به دقیقه تبدیل کن. فقط JSON برگردان."
    )
    if provider == "openai":
        content = [{"type": "input_text", "text": prompt}]
        content += [{"type": "input_image", "image_url": f"data:image/jpeg;base64,{chunk}", "detail": "high"} for chunk in chunks]
        data = _json_request(
            f"{client.spec.base_url}/responses", key,
            payload={
                "model": exact_model,
                "instructions": "Extract factual product-page data. Never invent.",
                "input": [{"role": "user", "content": content}],
                "text": {"format": {"type": "json_schema", "name": "screenshot_facts_3i33", "schema": SCREENSHOT_FACT_SCHEMA, "strict": True}},
            },
            method="POST", timeout=210, provider=provider, model=exact_model,
            operation="screenshot_fact_extract", product_id=product_id,
        )
        text = response_output_text(data)
    elif provider == "google":
        from . import phase49_3f_gemini_provider as gemini
        parts = [{"text": prompt + " Only JSON."}]
        parts += [{"inlineData": {"mimeType": "image/jpeg", "data": chunk}} for chunk in chunks]
        data = gemini._google_request(
            key, f"models/{exact_model.replace('models/', '')}:generateContent",
            payload={"contents": [{"role": "user", "parts": parts}], "generationConfig": {"responseMimeType": "application/json"}},
            method="POST", timeout=210, model=exact_model, operation="screenshot_fact_extract", product_id=product_id,
        )
        text = gemini._gemini_text(data)
    else:
        content = [{"type": "text", "text": prompt + " Only JSON."}]
        content += [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{chunk}"}} for chunk in chunks]
        messages = [{"role": "system", "content": "Extract factual product-page data. Never invent. Return one JSON object."}, {"role": "user", "content": content}]
        try:
            data = client._chat(exact_model, messages, response_format={"type": "json_object"}, operation="screenshot_fact_extract")
        except RuntimeError as exc:
            if not any(token in str(exc).casefold() for token in ("400", "response_format", "unsupported", "parameter")):
                raise
            data = client._chat(exact_model, messages, response_format=None, operation="screenshot_fact_extract_compat")
        text = response_output_text(data)

    text = _strip_json_fence(text)
    try:
        result = json.loads(text)
    except Exception as exc:
        raise RuntimeError(f"خروجی اسکرین‌شات JSON معتبر نیست: {str(text)[:700]}") from exc
    if not isinstance(result, dict):
        raise RuntimeError("خروجی اسکرین‌شات باید Object باشد.")
    return sanitize_product_facts(result)


def ensure_schema(db) -> None:
    columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
    changed = False
    for name, ddl in DESKTOP_COLUMNS.items():
        if name not in columns:
            db.conn.execute(f"ALTER TABLE products ADD COLUMN {name} {ddl}")
            changed = True
    if changed:
        db.conn.commit()


def db_columns(db):
    return {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}


def source_updates(db, source: dict[str, Any], mode: str):
    columns = db_columns(db)
    merged = {**dict(source.get("facts") or {}), **dict(source.get("evidence") or {})}
    updates = {}
    for column, key in {
        "source_like_count": "like_count",
        "source_download_count": "download_count",
        "source_save_count": "save_count",
        "source_boost_count": "boost_count",
        "source_print_count": "print_count",
        "estimated_weight_grams": "estimated_weight_grams",
        "estimated_print_minutes": "estimated_print_minutes",
    }.items():
        if column in columns:
            number = positive(merged.get(key))
            if number is not None:
                updates[column] = int(round(number)) if column.startswith("source_") else number
    profiles = merged.get("print_profiles")
    if "source_print_profiles_json" in columns and isinstance(profiles, list) and profiles:
        updates["source_print_profiles_json"] = json.dumps(profiles[:10], ensure_ascii=False)
    if "ai_last_mode" in columns:
        updates["ai_last_mode"] = mode
    if "ai_last_completed_at" in columns:
        updates["ai_last_completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return updates


def missing_value(value):
    return str(value or "").strip() in {"", "—", "-", "None", "null", "[]", "{}", "0"}


def repair_allowed(row, key):
    if key == "title_fa":
        current = str(row_value(row, key, "") or "").strip()
        return missing_value(current) or is_generic_source_title(current, str(row_value(row, "external_id", "") or ""))
    if key in {"estimated_weight_grams", "estimated_print_minutes"}:
        return positive(row_value(row, key, None)) is None
    return missing_value(row_value(row, key, ""))


def apply_ai_pack(app, product_id: int, pack: dict[str, Any], source: dict[str, Any], mode: str, repair_only=False):
    row = app.db.product(product_id)
    before = dict(row)
    pack = dict(pack)
    pack["material_recommendations"] = []
    pack["suggested_category_slug"] = ""
    title = str(pack.get("title_fa") or "").strip()
    updates = ai_updates(row, pack, title)
    updates.update(build_image_metadata_updates(row, pack, title))
    updates.update(source_updates(app.db, source, mode))
    if source.get("raw_source_description"):
        updates["source_description"] = str(source["raw_source_description"]).strip()
    if source.get("source_title"):
        updates["source_title"] = str(source["source_title"]).strip()

    if repair_only:
        always = {"source_like_count", "source_download_count", "source_save_count", "source_boost_count", "source_print_count", "source_print_profiles_json", "ai_last_mode", "ai_last_completed_at"}
        updates = {key: value for key, value in updates.items() if key in always or repair_allowed(row, key)}

    for forbidden in ("materials_json", "colors_json", "material_options_json", "color_options_json", "material_color_options_json", "fixed_price_material_name", "fixed_price_color_name"):
        updates.pop(forbidden, None)

    from .phase49_3i36_stage_finalization import filter_ai_updates, is_stage_locked
    updates, blocked = filter_ai_updates(row, updates)
    if blocked:
        audit_event(
            "ai", "locked_stage_fields_skipped", status="blocked", level="WARNING",
            product_id=product_id, source_file=__file__, message="AI respected finalized stages",
            detail={"fields": blocked, "mode": mode},
        )

    app.db.update_product(product_id, updates)
    selected = image_pipeline.cap_unique_urls(_list(row_value(row, "selected_images_json", "[]")))
    if selected and not is_stage_locked(row, "images"):
        try:
            image_pipeline.finalize_selected_images(app.db, product_id)
        except Exception as exc:
            audit_event("images", "phase49_3i33_finalize_error", status="error", level="ERROR", product_id=product_id, source_file=__file__, message=redact(exc))
    after = app.db.product(product_id)
    try:
        app.db.save_history(product_id, f"phase49_3i33_ai_{mode}", before, dict(after), f"3I.33 {mode} translation/SEO")
    except Exception:
        pass
    return {"product_id": product_id, "mode": mode, "title_fa": title, "changed_fields": sorted(updates)}


def local_dir_for_product(app, row):
    raw = str(row_value(row, "local_dir", "") or "").strip()
    if raw:
        return Path(raw)
    data_root = Path(getattr(app, "DATA", Path.cwd()))
    return data_root / "collected" / str(row_value(row, "source_code", "source")) / str(row_value(row, "external_id", "product"))


def capture_source_screenshot(app, product_id: int) -> Path:
    row = app.db.product(product_id)
    source_url = str(row_value(row, "source_url", "") or "").strip()
    if not source_url.startswith(("http://", "https://")):
        raise RuntimeError("برای دریافت اسکرین‌شات، لینک منبع معتبر لازم است.")
    local_dir = local_dir_for_product(app, row)
    capture_dir = local_dir / "source_page_capture_manual" / time.strftime("%Y%m%d-%H%M%S")
    from .classic_methods import collect_classic_exact
    result = asyncio.run(collect_classic_exact(source_url, capture_dir, headed=False, capture_network=False, download_images=False))
    screenshot = Path(str(result.get("screenshot_path") or ""))
    if not screenshot.is_file():
        raise RuntimeError("مرورگر اسکرین‌شات صفحه محصول را تولید نکرد.")
    image_dir = local_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    target = image_dir / f"source-page-screenshot-{time.strftime('%Y%m%d-%H%M%S')}.png"
    shutil.copy2(screenshot, target)
    pseudo = f"local://{target.name}"
    urls = list(dict.fromkeys(_list(row_value(row, "images_json", "[]")) + [pseudo]))
    values = {"local_dir": str(local_dir), "images_json": json.dumps(urls, ensure_ascii=False)}
    if "source_page_screenshot_path" in db_columns(app.db):
        values["source_page_screenshot_path"] = str(target)
    app.db.update_product(product_id, values)
    audit_event("acquisition", "phase49_3i33_source_screenshot", product_id=product_id, source_file=__file__, message=f"source screenshot saved: {target.name}", detail={"bytes": target.stat().st_size})
    return target


def find_source_screenshot(app, row):
    raw = str(row_value(row, "source_page_screenshot_path", "") or "").strip()
    if raw and Path(raw).is_file():
        return Path(raw)
    image_dir = local_dir_for_product(app, row) / "images"
    if image_dir.is_dir():
        items = sorted(image_dir.glob("source-page-screenshot*.png"), key=lambda path: path.stat().st_mtime, reverse=True)
        return items[0] if items else None
    return None


def source_from_screenshot(app, row, provider, key, model):
    product_id = int(row_value(row, "id", 0))
    screenshot = find_source_screenshot(app, row) or capture_source_screenshot(app, product_id)
    facts = screenshot_facts(provider, key, model, screenshot, product_id)
    source_url = str(row_value(row, "source_url", "") or "").strip()
    title = str(facts.get("source_title") or row_value(row, "source_title", "") or "").strip()
    if not title:
        raise RuntimeError("از اسکرین‌شات عنوان واقعی محصول استخراج نشد.")
    return {
        "source_url": source_url,
        "source_title": title,
        "source_description": structured_ai_text(source_url, facts, facts),
        "raw_source_description": str(facts.get("source_description") or "").strip(),
        "facts": facts,
        "evidence": facts,
        "screenshot_path": str(screenshot),
    }


def choose_repair_source(app, row, provider, key, model):
    saved = saved_source_for_ai(row)
    source_url = str(row_value(row, "source_url", "") or "").strip()
    title = str(saved.get("source_title") or "")
    description = str(saved.get("source_description") or "")
    if title and not is_generic_source_title(title, str(row_value(row, "external_id", "") or "")) and len(description) >= 80:
        return {
            "source_url": source_url,
            "source_title": title,
            "source_description": structured_ai_text(source_url, saved, saved),
            "raw_source_description": description,
            "facts": saved,
            "evidence": saved,
        }
    if source_url.startswith(("http://", "https://")):
        try:
            return live_source_for_ai(app, row)
        except Exception as exc:
            audit_event("ai", "phase49_3i33_repair_link_fallback", status="warning", level="WARNING", product_id=int(row_value(row, "id", 0)), source_file=__file__, message=redact(exc))
    return source_from_screenshot(app, row, provider, key, model)


def run_ai_mode(app, product_id: int, mode: str, provider: str, key: str, model: str):
    row = app.db.product(product_id)
    if row is None:
        raise RuntimeError(f"محصول #{product_id} پیدا نشد.")
    ensure_schema(app.db)
    if mode == "link":
        source = live_source_for_ai(app, row)
    elif mode == "data":
        saved = saved_source_for_ai(row)
        source_url = str(row_value(row, "source_url", "") or "").strip()
        if not saved.get("source_title"):
            raise RuntimeError("دیتای ذخیره‌شده عنوان منبع ندارد؛ از حالت لینک یا اسکرین‌شات استفاده کن.")
        source = {
            "source_url": source_url,
            "source_title": str(saved["source_title"]).strip(),
            "source_description": structured_ai_text(source_url, saved, saved),
            "raw_source_description": str(saved.get("source_description") or "").strip(),
            "facts": saved,
            "evidence": saved,
        }
    elif mode == "screenshot":
        source = source_from_screenshot(app, row, provider, key, model)
    elif mode == "repair":
        source = choose_repair_source(app, row, provider, key, model)
    else:
        raise RuntimeError(f"حالت AI ناشناخته است: {mode}")
    pack = generate_translation_pack(provider, key, model, source["source_title"], source["source_description"], product_id)
    return apply_ai_pack(app, product_id, pack, source, mode, repair_only=(mode == "repair"))


class OperationTelemetry:
    def __init__(self, name: str, product_id=None):
        self.name = name
        self.product_id = product_id
        self.started = time.perf_counter()
        self.start = self.sample()

    @staticmethod
    def sample():
        try:
            import psutil
            process = psutil.Process()
            cpu = process.cpu_times()
            net = psutil.net_io_counters()
            return {
                "rss": process.memory_info().rss,
                "cpu_time": cpu.user + cpu.system,
                "threads": process.num_threads(),
                "system_ram": psutil.virtual_memory().percent,
                "sent": net.bytes_sent,
                "recv": net.bytes_recv,
            }
        except Exception:
            return {}

    def finish(self, status="ok", extra=None):
        end = self.sample()
        detail = {"phase": PHASE, "duration_ms": int((time.perf_counter() - self.started) * 1000)}
        if self.start and end:
            detail.update({
                "rss_mb_end": round(end["rss"] / 1048576, 1),
                "rss_delta_mb": round((end["rss"] - self.start["rss"]) / 1048576, 1),
                "cpu_time_delta_seconds": round(end["cpu_time"] - self.start["cpu_time"], 3),
                "threads_end": end["threads"],
                "system_ram_percent": end["system_ram"],
                "system_net_sent_delta_bytes": max(0, end["sent"] - self.start["sent"]),
                "system_net_recv_delta_bytes": max(0, end["recv"] - self.start["recv"]),
                "network_scope": "system-wide delta during operation, not exact per-process traffic",
            })
        if extra:
            detail.update(extra)
        audit_event("performance", "phase49_3i33_operation", status=status, product_id=self.product_id, source_file=__file__, message=self.name, detail=detail)
