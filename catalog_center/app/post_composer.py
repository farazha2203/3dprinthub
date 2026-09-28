"""Deterministic, no-invention Post-tab helpers."""
from __future__ import annotations
import re
from urllib.parse import urlparse

POST_STYLES = (
    ("minimal", "مینیمال"), ("warm", "گرم و صمیمی"), ("professional", "حرفه‌ای"),
    ("storytelling", "روایت‌محور"), ("technical", "فنی"), ("benefit", "مزیت‌محور"),
    ("educational", "آموزشی"), ("luxury", "لوکس"), ("playful", "خلاقانه"),
    ("launch", "معرفی محصول"), ("community", "جامعه‌محور"), ("short", "کوتاه"),
)

def _valid_url(value: str) -> bool:
    parsed = urlparse(str(value or "").strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

def mock_openrouter_post(product: dict, style: str, explicit_mentions: str = "") -> dict:
    """Return a test-only response; never invents product facts or performs I/O."""
    title = str(product.get("title_fa") or product.get("source_title") or "").strip()
    if not title:
        raise ValueError("POST_SOURCE_TITLE_REQUIRED")
    allowed = {key for key, _label in POST_STYLES}
    if style not in allowed:
        raise ValueError("POST_STYLE_INVALID")
    source_url = str(product.get("source_url") or "").strip()
    links = [source_url] if _valid_url(source_url) else []
    mentions = sorted(set(re.findall(r"@[A-Za-z0-9_\u0600-\u06ff]+", explicit_mentions or "")))
    caption = f"{title}\n\nاین متن فقط بر اساس اطلاعات ثبت‌شدهٔ محصول آماده شده است."
    return {
        "provider": "openrouter-mock", "model": "mock-post-v1", "style": style,
        "caption": caption, "links": links, "mentions": mentions,
        "no_invention": True,
    }

def validate_post_metadata(response: dict, product: dict) -> bool:
    title = str(product.get("title_fa") or product.get("source_title") or "").strip()
    return bool(response.get("no_invention") is True and title and title in response.get("caption", "") and all(_valid_url(x) for x in response.get("links", [])))
