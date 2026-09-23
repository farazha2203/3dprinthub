from __future__ import annotations

import json
import re
from typing import Any

POLICY_VERSION = "instagram-product-v5-20260923"
MAX_HASHTAGS = 8
NATIONWIDE_SHIPPING_COPY = "ارسال سفارش به سراسر ایران"
BRAND_ORDER_COPY = "سفارش این محصول از 3DPrintHub.ir"
FORBIDDEN_FREE_CLAIMS = (
    "چاپ سه بعدی رایگان",
    "چاپ سه‌بعدی رایگان",
    "دانلود رایگان",
    "رایگان",
)
MAX_CAPTION = 2200
MAX_ALT_TEXT = 1000
STORY_STYLE_ID = "3dprinthub_instagram_gold_navy_v3_iransans_bio"
APPROVED_HIGHLIGHTS = (
    "آباژور",
    "پایه کیک",
    "اکسسوری کریسمس",
    "اکسسوری تولد",
    "اسباب بازی",
    "فلکسیبل",
    "قطعات سفارشی",
    "قطعات خودرو",
)


def _json_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def _strip_false_free_claims(value: Any) -> str:
    text = str(value or "")
    for claim in FORBIDDEN_FREE_CLAIMS:
        text = re.sub(re.escape(claim), " ", text, flags=re.IGNORECASE)
    text = re.sub(r"[ \t]+([،,:؛;.!؟?])", r"\\1", text)
    return re.sub(r"\s+", " ", text).strip(" -–—|،,:؛;")


def _plain(value: Any, limit: int = 0) -> str:
    text = _strip_false_free_claims(value)
    return text[:limit].rstrip() if limit and len(text) > limit else text


def _unique(values):
    out = []
    seen = set()
    for value in values:
        text = _plain(value)
        key = text.casefold()
        if text and key not in seen:
            seen.add(key)
            out.append(text)
    return out
def build_hashtags(row: dict[str, Any]) -> list[str]:
    raw = []
    raw += [row.get("seo_focus_keyword")]
    raw += _json_list(row.get("keywords_json"))
    raw += _json_list(row.get("tags_fa_json"))
    raw += _json_list(row.get("hashtags_fa_json"))
    raw += _json_list(row.get("categories_fa_json"))
    raw += [row.get("local_category_slug"), row.get("use_case_class")]
    fixed_tags = (
        "#چاپ_سه_بعدی",
        "#ارسال_سراسری",
        "#3DPrintHub",
    )
    dynamic_limit = max(0, MAX_HASHTAGS - len(fixed_tags))
    tags = []
    for item in _unique(raw):
        text = item.lstrip("#").strip().replace(" ", "_")
        text = re.sub(r"[^\w\u0600-\u06FF_]+", "", text)
        if len(text) < 2:
            continue
        tag = f"#{text}"
        if tag not in tags and tag not in fixed_tags:
            tags.append(tag)
        if len(tags) >= dynamic_limit:
            break
    for fixed in fixed_tags:
        if fixed not in tags:
            tags.append(fixed)
    return tags[:MAX_HASHTAGS]


def _description(row: dict[str, Any]) -> str:
    for key in ("social_caption_fa", "seo_description_fa", "short_description_fa", "description_fa"):
        text = _plain(row.get(key), 700)
        if text:
            return text
    return ""


def _sales_bullets(row: dict[str, Any]) -> list[str]:
    values = _json_list(row.get("sales_bullets_json"))
    if not values:
        values = _json_list(row.get("technical_features_json"))
    return [_plain(v, 160) for v in values if _plain(v)][:4]


def build_caption(row: dict[str, Any], tracking_url: str) -> tuple[str, list[str]]:
    title = _plain(row.get("seo_title_fa") or row.get("title_fa") or row.get("source_title"), 180)
    description = _description(row)
    bullets = _sales_bullets(row)
    hashtags = build_hashtags(row)
    focus_keyword = _plain(
        row.get("seo_focus_keyword")
        or ((_json_list(row.get("keywords_json")) or [""])[0]),
        120,
    )
    parts = [title] if title else []
    if focus_keyword and focus_keyword.casefold() not in (title or "").casefold():
        parts.append(f"🔎 {focus_keyword}")
    if description and description.casefold() != title.casefold():
        parts.append(description)
    if bullets:
        parts.append("\n".join(f"• {item}" for item in bullets))
    dimensions = _plain(row.get("dimensions"), 120)
    materials = [_plain(item, 80) for item in _json_list(row.get("materials_json")) if _plain(item)]
    specs = []
    if dimensions:
        specs.append(f"ابعاد: {dimensions}")
    if materials:
        specs.append("متریال: " + "، ".join(materials[:3]))
    if specs:
        parts.append("مشخصات: " + " | ".join(specs))
    parts.append(f"🛒 {BRAND_ORDER_COPY}")
    parts.append(f"🚚 {NATIONWIDE_SHIPPING_COPY}")
    parts.append("🔗 خرید این محصول: لینک بیو را باز کنید و روی همین پست در فروشگاه 3DPrintHub بزنید.")
    if hashtags:
        parts.append(" ".join(hashtags))
    caption = "\n\n".join(part for part in parts if part).strip()
    return caption[:MAX_CAPTION].rstrip(), hashtags
def build_alt_texts(row: dict[str, Any], media_urls: list[str]) -> list[str]:
    provided = [_plain(x, MAX_ALT_TEXT) for x in _json_list(row.get("image_alt_texts_json"))]
    title = _plain(row.get("seo_title_fa") or row.get("title_fa") or row.get("source_title"), 180)
    category = _plain(((_json_list(row.get("categories_fa_json")) or [""])[0]), 80)
    material_values = _json_list(row.get("materials_json"))
    material = _plain(material_values[0] if material_values else "", 80)
    out = []
    total = len(media_urls)
    for index, _url in enumerate(media_urls):
        if index < len(provided) and provided[index]:
            out.append(provided[index])
            continue
        bits = [title or "محصول چاپ سه‌بعدی 3DPrintHub"]
        if category:
            bits.append(category)
        if material:
            bits.append(f"متریال {material}")
        bits.append(f"نمای {index + 1} از {total}")
        out.append(" — ".join(bits)[:MAX_ALT_TEXT])
    return out


def highlight_target_for_product(row: dict[str, Any]) -> str:
    explicit = _plain(
        row.get("instagram_highlight")
        or row.get("social_highlight")
    )
    if explicit in APPROVED_HIGHLIGHTS:
        return explicit

    slug = _plain(row.get("local_category_slug")).casefold()
    slug_map = {
        "toys-games": "اسباب بازی",
        "automotive": "قطعات خودرو",
        "automotive-dashboard": "قطعات خودرو",
        "automotive-clips": "قطعات خودرو",
        "automotive-air-vents": "قطعات خودرو",
        "replacement-parts": "قطعات سفارشی",
        "gears": "قطعات سفارشی",
        "industrial-parts": "قطعات سفارشی",
        "tools-jigs": "قطعات سفارشی",
        "electronics-cases": "قطعات سفارشی",
        "workshop": "قطعات سفارشی",
        "mounts-brackets": "قطعات سفارشی",
        "adapters-couplers": "قطعات سفارشی",
        "spare-parts": "قطعات سفارشی",
    }
    if slug in slug_map:
        return slug_map[slug]

    text_parts = [
        row.get("title_fa"),
        row.get("seo_title_fa"),
        row.get("source_title"),
        row.get("use_case_class"),
        *_json_list(row.get("categories_fa_json")),
        *_json_list(row.get("tags_fa_json")),
        *_json_list(row.get("keywords_json")),
    ]
    text = " ".join(_plain(item).casefold() for item in text_parts if _plain(item))
    keyword_groups = (
        ("اکسسوری کریسمس", ("christmas", "کریسمس")),
        ("اکسسوری تولد", ("birthday", "تولد")),
        ("پایه کیک", ("cake stand", "cake", "پایه کیک", "استند کیک")),
        ("آباژور", ("lamp", "lighting", "آباژور", "چراغ")),
        ("فلکسیبل", ("flexible", "flexi", "انعطاف")),
        ("قطعات خودرو", ("automotive", "vehicle", "خودرو", "ماشین")),
        ("اسباب بازی", ("toy", "game", "اسباب بازی", "دیناسور", "فیگور")),
    )
    for target, terms in keyword_groups:
        if any(term in text for term in terms):
            return target

    return "قطعات سفارشی"


def build_story_copy(row: dict[str, Any]) -> dict[str, Any]:
    title = _plain(row.get("title_fa") or row.get("source_title") or row.get("seo_title_fa"), 90)
    subtitle = _plain(row.get("short_description_fa") or row.get("seo_description_fa"), 150)
    bullets = _sales_bullets(row)
    if not bullets:
        fallback = _json_list(row.get("tags_fa_json")) + _json_list(row.get("categories_fa_json"))
        bullets = [_plain(x, 60) for x in fallback if _plain(x)][:4]
    while len(bullets) < 3:
        for default in ("طراحی دقیق", "چاپ سه‌بعدی باکیفیت", "قابل سفارش"):
            if default not in bullets:
                bullets.append(default)
            if len(bullets) >= 3:
                break
    bullets = [
        item for item in bullets
        if item and NATIONWIDE_SHIPPING_COPY not in item
    ][:3]
    bullets.append(NATIONWIDE_SHIPPING_COPY)
    return {
        "title": title or "محصول سه‌بعدی",
        "subtitle": subtitle or "طراحی و چاپ سه‌بعدی توسط 3DPrintHub",
        "bullets": bullets[:4],
        "style_id": STORY_STYLE_ID,
        "font_family": "IRANSansWeb(FaNum)",
    }
