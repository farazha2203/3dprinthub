from __future__ import annotations

import html
import json
import re
from typing import Any, Iterable


_PERSIAN_RE = re.compile(r"[\u0600-\u06FF]")
_LATIN_RE = re.compile(r"[A-Za-z]")
_SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_BREAK_RE = re.compile(r"<(?:br\s*/?|/p|/div|/li|p\b[^>]*|div\b[^>]*|li\b[^>]*)>", re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

# Text copied from source websites must never become public sales copy.
_BOILERPLATE_MARKERS = (
    "cookie settings",
    "cookie policy",
    "we use cookies",
    "cookies and other tracking",
    "tracking technologies",
    "personalized content",
    "targeted ads",
    "manage your preferences",
    "your consent",
    "privacy policy",
    "accept cookies",
    "reject cookies",
    "all rights reserved",
    "terms and conditions",
    "subscribe to our newsletter",
)

_GENERIC_HERO_TITLE = "محصول منتخب چاپ سه‌بعدی"
_GENERIC_HERO_DESCRIPTION = (
    "برای خرید و سفارش این محصول چاپ سه‌بعدی، مشخصات، متریال‌های قابل انتخاب و قیمت را در صفحه محصول بررسی کنید."
)


def _json_value(value: Any, default):
    if isinstance(value, type(default)):
        return value
    try:
        parsed = json.loads(value or "")
        return parsed if isinstance(parsed, type(default)) else default
    except Exception:
        return default


def clean_public_text(value: Any, *, limit: int = 0) -> str:
    """Convert arbitrary imported HTML/text to plain, compact public text."""
    text = html.unescape(str(value or ""))
    text = _SCRIPT_STYLE_RE.sub(" ", text)
    text = _BREAK_RE.sub(" ", text)
    text = _TAG_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text).strip(" \t\r\n-–—|")
    if limit > 0:
        return text[:limit].rstrip()
    return text


def has_persian(value: Any) -> bool:
    text = clean_public_text(value)
    if not text:
        return False
    persian = len(_PERSIAN_RE.findall(text))
    latin = len(_LATIN_RE.findall(text))
    # A Persian commercial sentence may legitimately contain a model/brand name
    # in Latin characters, but Persian must be the dominant/public language.
    return persian >= 2 and (latin == 0 or persian >= max(2, latin // 2))


def is_source_boilerplate(value: Any) -> bool:
    text = clean_public_text(value).casefold()
    return bool(text) and any(marker in text for marker in _BOILERPLATE_MARKERS)


def safe_persian_text(value: Any, *, limit: int = 0) -> str:
    text = clean_public_text(value, limit=limit)
    if not text or is_source_boilerplate(text) or not has_persian(text):
        return ""
    return text


def first_safe_persian(values: Iterable[Any], *, limit: int = 0) -> str:
    for value in values:
        safe = safe_persian_text(value, limit=limit)
        if safe:
            return safe
    return ""


def _category_name(product) -> str:
    try:
        if product is not None and product.category_id:
            return safe_persian_text(product.category.name, limit=120)
    except Exception:
        pass
    return ""


def _asset_persian(asset, name: str) -> str:
    try:
        return safe_persian_text(getattr(asset, name, ""))
    except Exception:
        return ""


def _content_pack(data: dict) -> dict:
    pack = _json_value(data.get("content_pack_json"), {})
    return pack if isinstance(pack, dict) else {}


def _slider_ai(data: dict) -> dict:
    value = _content_pack(data).get("homepage_slider_seo") or {}
    return value if isinstance(value, dict) else {}


def _list_values(data: dict, key: str) -> list:
    value = _json_value(data.get(key), [])
    return value if isinstance(value, list) else []


def _sales_focus(base_title: str, data: dict, ai: dict) -> str:
    candidates = [
        data.get("homepage_slider_focus_keyword"),
        ai.get("focus_keyword_fa"),
        *_list_values(data, "keywords_json"),
        *_list_values(data, "tags_fa_json"),
    ]
    focus = first_safe_persian(candidates, limit=180)
    if focus:
        return focus
    return clean_public_text(f"خرید {base_title}", limit=180)


def build_slider_sales_copy(data: dict, product=None, asset=None) -> dict:
    """Resolve Persian-only, sales-oriented public Hero copy.

    Dedicated Windows slider fields are authoritative. General Persian product
    SEO is only a fallback. Raw source title/description are deliberately not
    accepted here.
    """
    data = data if isinstance(data, dict) else {}
    ai = _slider_ai(data)

    title = first_safe_persian(
        [
            data.get("homepage_slider_title_fa"),
            ai.get("title_fa"),
            data.get("seo_title_fa"),
            data.get("title_fa"),
            getattr(product, "title", "") if product is not None else "",
            _asset_persian(asset, "persian_title"),
        ],
        limit=220,
    )
    if not title:
        category = _category_name(product)
        title = f"محصول منتخب {category}" if category else _GENERIC_HERO_TITLE
        title = clean_public_text(title, limit=220)

    description = first_safe_persian(
        [
            data.get("homepage_slider_description_fa"),
            ai.get("description_fa"),
            data.get("short_description_fa"),
            data.get("seo_description_fa"),
            data.get("description_fa"),
            getattr(product, "short_description", "") if product is not None else "",
            _asset_persian(asset, "persian_short_description"),
            _asset_persian(asset, "persian_description"),
        ],
        limit=1200,
    ) or _GENERIC_HERO_DESCRIPTION

    image_alts = _list_values(data, "image_alt_texts_json")
    alt_text = first_safe_persian(
        [
            data.get("homepage_slider_alt_text"),
            ai.get("image_alt_fa"),
            *image_alts,
        ],
        limit=240,
    )
    if not alt_text:
        alt_text = clean_public_text(
            f"{title}؛ تصویر محصول برای خرید و سفارش چاپ سه‌بعدی از 3DPrintHub",
            limit=240,
        )

    button = first_safe_persian(
        [data.get("homepage_slider_button_text"), ai.get("button_text_fa")],
        limit=80,
    ) or "مشاهده محصول"

    focus = _sales_focus(title, data, ai)
    return {
        "title_fa": title,
        "description_fa": description,
        "image_alt_fa": alt_text,
        "button_text_fa": button,
        "focus_keyword_fa": focus,
    }


def build_product_sales_seo(data: dict, product=None, asset=None) -> dict:
    """Resolve Persian sales meta fields from the Windows editorial dataset."""
    data = data if isinstance(data, dict) else {}
    explicit_title = first_safe_persian([data.get("seo_title_fa")], limit=180)
    base_title = first_safe_persian(
        [
            data.get("title_fa"),
            getattr(product, "title", "") if product is not None else "",
            _asset_persian(asset, "persian_title"),
        ],
        limit=150,
    ) or _GENERIC_HERO_TITLE

    if explicit_title:
        meta_title = explicit_title
    else:
        meta_title = clean_public_text(f"خرید {base_title} | 3DPrintHub", limit=180)

    explicit_description = first_safe_persian([data.get("seo_description_fa")], limit=320)
    fallback_description = first_safe_persian(
        [
            data.get("short_description_fa"),
            data.get("description_fa"),
            getattr(product, "short_description", "") if product is not None else "",
            _asset_persian(asset, "persian_short_description"),
        ],
        limit=250,
    )
    meta_description = explicit_description or clean_public_text(
        fallback_description
        or f"خرید و سفارش {base_title} با چاپ سه‌بعدی؛ مشخصات، متریال، قیمت و زمان آماده‌سازی را در 3DPrintHub بررسی کنید.",
        limit=320,
    )

    keywords = [*_list_values(data, "keywords_json"), *_list_values(data, "tags_fa_json")]
    focus = first_safe_persian(keywords, limit=180) or clean_public_text(f"خرید {base_title}", limit=180)
    hashtags = [safe_persian_text(value, limit=80) for value in _list_values(data, "hashtags_fa_json")]
    hashtags = [value for value in hashtags if value]

    return {
        "meta_title": meta_title,
        "meta_description": meta_description,
        "focus_keyword": focus,
        "hashtags": hashtags,
    }
