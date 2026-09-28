"""Safe local contract for AI-assisted social creative generation.

This module discovers image-capable OpenRouter endpoints at runtime and builds
fact-bound prompts. It does not publish, impersonate human activity, or try to
evade platform detection.
"""
from __future__ import annotations

import json
import base64
import hashlib
import mimetypes
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


def discover_image_endpoints(api_key: str, *, opener=urllib.request.urlopen) -> list[dict[str, Any]]:
    """Return image endpoints that accept references, ordered by cost.

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
    return sorted(candidates, key=lambda item: (item["cost_usd"], item["model"], item["provider"]))


def discover_cheapest_image_endpoint(api_key: str, *, opener=urllib.request.urlopen) -> dict[str, Any]:
    """Return the cheapest reference-capable image endpoint without generating."""
    return discover_image_endpoints(api_key, opener=opener)[0]


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


def generate_image_revision(
    api_key: str,
    model: str,
    prompt: str,
    reference_bytes: bytes,
    *,
    aspect_ratio: str = "1:1",
    opener=urllib.request.urlopen,
) -> dict[str, Any]:
    """Generate one reference-guided image and return bytes plus provider usage.

    This is deliberately a pure provider adapter: it does not write files,
    SQLite, Product rows, or publish anything. Callers own idempotent
    persistence and approval state.
    """
    key = str(api_key or "").strip()
    model_id = str(model or "").strip()
    if not key:
        raise ValueError("OpenRouter API key is required for image generation.")
    if not model_id:
        raise ValueError("Image Model is required for image generation.")
    if not isinstance(reference_bytes, (bytes, bytearray)) or len(reference_bytes) < 64:
        raise ValueError("A valid Product reference image is required.")
    mime = mimetypes.guess_type("product.png")[0] or "image/png"
    reference = f"data:{mime};base64,{base64.b64encode(bytes(reference_bytes)).decode('ascii')}"
    payload = {
        "model": model_id,
        "prompt": str(prompt or "").strip(),
        "input_references": [{"type": "image_url", "image_url": {"url": reference}}],
        "aspect_ratio": str(aspect_ratio or "1:1"),
        "n": 1,
        "output_format": "png",
    }
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/images",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with opener(request, timeout=180) as response:
        raw = response.read().decode("utf-8", errors="replace")
        status = int(getattr(response, "status", 200) or 200)
    if status >= 400:
        raise RuntimeError(f"OpenRouter image HTTP {status}: {raw[:800]}")
    result = json.loads(raw or "{}")
    image_bytes = decode_image_response(result)
    usage = result.get("usage") if isinstance(result.get("usage"), dict) else {}
    return {
        "bytes": image_bytes,
        "model": str(result.get("model") or model_id),
        "usage": usage,
        "cost_usd": usage.get("cost"),
        "payload_contract": "openrouter_images_input_reference_v1",
    }


def generation_request_fingerprint(
    product_id: int,
    kind: str,
    style: CreativeStyle,
    model: str,
    prompt: str,
    reference_bytes: bytes,
) -> str:
    """Stable identity used to avoid paying twice for the same generation request."""
    digest = hashlib.sha256()
    for value in (
        str(int(product_id)), str(kind), style.key, str(model).strip(),
        str(prompt), hashlib.sha256(bytes(reference_bytes)).hexdigest(),
    ):
        digest.update(value.encode("utf-8"))
        digest.update(b"\x00")
    return digest.hexdigest()


def materialize_selected_revision(db, product_id: int, kind: str) -> dict[str, Any] | None:
    """Expose an approved SQLite BLOB as a guarded send-path derivative.

    SQLite remains the authority. The materialized PNG exists only because the
    existing Buffer/Site adapters consume local paths; it is never a second
    revision store and is created only after explicit operator selection.
    """
    row = db.social_ai_revision_for_publish(int(product_id), str(kind))
    if not row:
        return None
    blob = bytes(row.get("image_blob") or b"")
    if len(blob) < 64:
        raise ValueError("Selected Social AI revision has no valid image BLOB.")
    digest = str(row.get("sha256") or hashlib.sha256(blob).hexdigest()).strip()
    root = data_root() / "social" / "ai_handoff" / str(int(product_id)) / str(kind)
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{digest}.png"
    if not path.is_file() or path.stat().st_size != len(blob):
        path.write_bytes(blob)
    return {
        "revision_id": int(row["id"]),
        "sha256": digest,
        "local_path": str(path),
        "mime_type": str(row.get("mime_type") or "image/png"),
        "metadata_json": str(row.get("metadata_json") or "{}"),
    }


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
