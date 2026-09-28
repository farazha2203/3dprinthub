"""Safe local contract for AI-assisted social creative generation.

This module discovers image-capable OpenRouter endpoints at runtime and builds
fact-bound prompts. It does not publish, impersonate human activity, or try to
evade platform detection.
"""
from __future__ import annotations

import json
import base64
import hashlib
from pathlib import Path
import urllib.request
from dataclasses import dataclass
from typing import Any

from .runtime_paths import data_root


@dataclass(frozen=True)
class CreativeStyle:
    key: str
    label: str
    format: str
    description: str


STORY_STYLES = (
    CreativeStyle("hero_natural", "Hero طبیعی", "9:16", "محصول واقعی، نور طبیعی، محیط هماهنگ با کاربرد محصول"),
    CreativeStyle("editorial_luxury", "Editorial لوکس", "9:16", "چیدمان مینیمال، نور استودیویی نرم، رنگ مکمل محصول"),
    CreativeStyle("technical_clean", "Technical تمیز", "9:16", "پس‌زمینه خنثی، زاویه واضح، حس دقیق و مهندسی"),
    CreativeStyle("lifestyle_scene", "Lifestyle", "9:16", "محصول در محیط واقعی و قابل‌تصور برای مشتری"),
    CreativeStyle("surreal_safe", "Surreal کنترل‌شده", "9:16", "فضای خلاقانه اما شکل، رنگ و هویت محصول حفظ شود"),
    CreativeStyle("minimal_frame", "Minimal قاب طلایی", "9:16", "محصول کامل با قاب ظریف طلایی و فضای تنفس زیاد"),
)

POST_STYLES = (
    CreativeStyle("post_hero", "Post Hero", "4:5", "تصویر اصلی محصول با قاب برند و فضای کافی برای عنوان"),
    CreativeStyle("post_detail", "جزئیات محصول", "4:5", "تمرکز روی بافت، فرم و جزئیات واقعی محصول"),
    CreativeStyle("post_use_case", "کاربرد واقعی", "4:5", "محصول در محیط مصرف واقعی، طبیعی و غیرمصنوعی"),
    CreativeStyle("post_comparison", "مقایسه بصری", "4:5", "نمای اصلی و detail در ترکیب خوانا، بدون ادعای جدید"),
    CreativeStyle("post_editorial", "Editorial", "4:5", "سبک مجله‌ای با رنگ هماهنگ و تایپوگرافی فارسی بعد از رندر"),
    CreativeStyle("post_minimal", "Minimal Brand", "4:5", "پس‌زمینه ساده، قاب طلایی ظریف، لوگو در گوشه پایین چپ"),
)


def _price(endpoint: dict[str, Any]) -> float:
    values = []
    for item in endpoint.get("pricing") or []:
        try:
            values.append(float(item.get("cost_usd") or 0))
        except (TypeError, ValueError):
            continue
    return min(values) if values else float("inf")


def discover_cheapest_image_endpoint(api_key: str, *, opener=urllib.request.urlopen) -> dict[str, Any]:
    """Return the cheapest endpoint that accepts image references and outputs images.

    No generation occurs. The key is used only for the official discovery call
    and is never returned in the result.
    """
    if not str(api_key or "").strip():
        raise ValueError("OpenRouter API key is required for model discovery.")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/images/models",
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
    )
    with opener(req, timeout=30) as response:
        models = json.loads(response.read().decode("utf-8"))
    candidates = []
    for model in models.get("data") or []:
        architecture = model.get("architecture") or {}
        if "image" not in (architecture.get("input_modalities") or []):
            continue
        if "image" not in (architecture.get("output_modalities") or []):
            continue
        model_id = str(model.get("id") or "").strip()
        if not model_id or "/" not in model_id:
            continue
        author, slug = model_id.split("/", 1)
        endpoint_req = urllib.request.Request(
            f"https://openrouter.ai/api/v1/images/models/{author}/{slug}/endpoints",
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
        )
        with opener(endpoint_req, timeout=30) as response:
            endpoints = json.loads(response.read().decode("utf-8"))
        for endpoint in endpoints.get("endpoints") or []:
            supported = endpoint.get("supported_parameters") or {}
            if "input_references" not in supported:
                continue
            candidates.append({
                "model": model_id,
                "provider": endpoint.get("provider_slug") or endpoint.get("provider_name") or "",
                "cost_usd": _price(endpoint),
                "supported_parameters": supported,
            })
    if not candidates:
        raise RuntimeError("No OpenRouter image endpoint supports input references.")
    return min(candidates, key=lambda item: (item["cost_usd"], item["model"], item["provider"]))


def build_product_prompt(product: dict[str, Any], style: CreativeStyle, *, language: str = "fa") -> str:
    """Build a fact-bound English prompt; all overlay copy is added locally in Persian."""
    title = str(product.get("source_title") or product.get("title_fa") or "3D printed product").strip()
    description = str(product.get("source_description") or product.get("short_description_fa") or "").strip()
    return (
        "Create a product-focused social creative using the supplied product reference image. "
        f"Product identity: {title}. Authoritative description: {description[:500]}. "
        f"Style: {style.description}. Format: {style.format}. "
        "Preserve the exact product geometry, colors, silhouette and material appearance. "
        "Remove distracting background only when needed; do not invent accessories, dimensions, "
        "price, claims, logos or text. No text inside the generated image; Persian typography, "
        "title, CTA, URL, mention and discount are composed and validated locally. "
        "Natural commercial photography, believable lighting, clean composition, no watermark."
    )


def decode_image_response(response: dict[str, Any]) -> bytes:
    """Decode one OpenRouter image response without accepting remote URLs."""
    items = response.get("data") if isinstance(response, dict) else None
    if not isinstance(items, list) or not items:
        raise ValueError("Mock/OpenRouter image response has no data item.")
    encoded = str((items[0] or {}).get("b64_json") or "").strip()
    if not encoded:
        raise ValueError("Image response is missing b64_json.")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise ValueError("Image response contains invalid base64.") from exc
    if len(raw) < 64:
        raise ValueError("Generated image response is unexpectedly small.")
    return raw


def persist_revision(product_id: int, kind: str, style: CreativeStyle, raw: bytes, metadata: dict[str, Any]) -> dict[str, Any]:
    """Persist an immutable local revision for later operator reuse."""
    digest = hashlib.sha256(raw).hexdigest()[:16]
    root = data_root() / "social" / "ai_revisions" / str(int(product_id)) / str(kind) / style.key
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{digest}.png"
    if not path.is_file():
        path.write_bytes(raw)
    record = {
        **dict(metadata or {}),
        "product_id": int(product_id),
        "kind": str(kind),
        "style": style.key,
        "path": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "immutable_revision": True,
        "published": False,
    }
    return record
