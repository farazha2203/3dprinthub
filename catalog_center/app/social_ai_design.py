"""Safe local contract for AI-assisted social creative generation.

This module discovers image-capable OpenRouter endpoints at runtime and builds
fact-bound prompts. It does not publish, impersonate human activity, or try to
evade platform detection.
"""
from __future__ import annotations

import json
import base64
import hashlib
import html
import mimetypes
from pathlib import Path
import re
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
    CreativeStyle("hero_natural", "Brand Monument — امضای سه‌بعدی", "9:16", "کمپین شاخص برند: محصول قهرمان روی سکوی مجسمه‌وار، لوگوی رسمی به‌شکل تابلوی سه‌بعدی نورانی در عمق صحنه، نور سینمایی سرمه‌ای/طلایی و تیتر فارسی در فضای امن بالای کادر."),
    CreativeStyle("editorial_luxury", "Campaign Cover — جلد کمپین", "9:16", "جلد کمپین لوکس و پرقدرت: چیدمان نامتقارن مجله‌ای، قاب چندلایه طلایی، هاله نور کنترل‌شده، محصول بزرگ و برجسته، تیتر فارسی بزرگ با تایپ سریف لوکس و متن کوتاه در پنل مستقل."),
    CreativeStyle("technical_clean", "Precision Grid — گرافیک صنعتی", "9:16", "پوستر تبلیغاتی مهندسی: شبکه‌های هندسی و خطوط نور نازک، سکوی محصول، قاب شکسته، تایپوگرافی فارسی هندسی و پرقدرت؛ بدون اندازه، نمودار، برچسب یا مشخصه ساختگی."),
    CreativeStyle("lifestyle_scene", "Immersive Brand Scene — صحنه برند", "9:16", "محصول در محیط واقعی و چشمگیرِ مناسب کاربردش، روی میز طراحی‌شده با تابلوی کوچک سه‌بعدی 3DPrintHub در پس‌زمینه؛ نور و عمق سینمایی، کادر تبلیغاتی نامتقارن و تیتر فارسی هماهنگ با صحنه."),
    CreativeStyle("surreal_safe", "Controlled Surreal — سورئال کنترل‌شده", "9:16", "فضای سورئال جسور و هنری با پرسپکتیو غیرمنتظره، نور حجمی و عناصر شناور محدود؛ محصول باید از نظر شکل، رنگ، تعداد اجزا و هویت کاملاً واقعی و دست‌نخورده بماند."),
    CreativeStyle("minimal_frame", "Maximal Type & Frame — تایپوگرافی شاخص", "9:16", "پوستر تبلیغاتی تایپوگرافیک نه مینیمال: قاب معماری چندلایه سرمه‌ای/طلایی، برش گرافیکی مورب، محصول بزرگ، تیتر فارسی نمایشی با سایه و برجستگی ظریف و نوار متن متفاوت در پایین کادر."),
)

POST_STYLES = (
    CreativeStyle("post_hero", "Post Hero", "4:5", "تصویر اصلی محصول با قاب برند و فضای کافی برای عنوان"),
    CreativeStyle("post_detail", "جزئیات محصول", "4:5", "تمرکز روی بافت، فرم و جزئیات واقعی محصول"),
    CreativeStyle("post_use_case", "کاربرد واقعی", "4:5", "محصول در محیط مصرف واقعی، طبیعی و غیرمصنوعی"),
    CreativeStyle("post_comparison", "مقایسه بصری", "4:5", "نمای اصلی و detail در ترکیب خوانا، بدون ادعای جدید"),
    CreativeStyle("post_editorial", "Editorial", "4:5", "سبک مجله‌ای با رنگ هماهنگ و تایپوگرافی فارسی بعد از رندر"),
    CreativeStyle("post_minimal", "Minimal Brand", "4:5", "پس‌زمینه ساده، قاب طلایی ظریف، لوگو در گوشه پایین چپ"),
)

STYLE_PROMPTS_EN = {
    "hero_natural": "Create a bold flagship 3DPrintHub brand campaign, not a plain product photo. Treat reference 1 as the exact product and reference 2 as the official brand mark. Place the faithful complete product on a sculptural premium plinth; integrate the supplied logo as a dimensional illuminated brass-and-navy wall sign in the background. Cinematic low-key studio lighting, rich midnight navy, controlled molten-gold edge light, deep perspective, luxurious atmospheric haze. Layout: compact brand sign near the upper safe zone, large Persian headline high in the frame, product owns the central 55%, short copy in a separate lower plaque. Use a distinctive heavy Persian display sans with restrained metallic depth.",
    "editorial_luxury": "Design a high-end vertical fashion-house campaign cover, not a generic centered template. Preserve product identity exactly. Use dramatic asymmetric art direction, an editorial crop with the full object still visible, layered architectural gold rules and a deep oxblood-to-navy chiaroscuro background. Create one elegant dimensional brand medallion from the supplied logo reference. Typography: refined Persian serif display headline aligned to the right in a tall side panel; smaller ivory Persian copy below it; thin gold folio-like frame and a contrasting small CTA plaque. Strong hierarchy, expensive print-campaign finish.",
    "technical_clean": "Create an engineered product launch poster with premium industrial-design art direction. Preserve exact geometry and visible material. Stage the object on a dark graphite laboratory pedestal with precise rim lighting, restrained cyan-to-gold light trails, subtle non-numeric blueprint grids and a large asymmetric split-frame. Place the supplied 3DPrintHub logo as a small real-looking enamel badge, not invented branding. Persian headline uses a bold geometric display face in a clean top band; supporting copy sits in a narrow right-to-left technical label panel. Never draw dimensions, measurements, arrows that imply specifications, charts, or fake technical annotations.",
    "lifestyle_scene": "Create a believable but aspirational interior-design campaign for this exact product and its actual use. Preserve its full recognizable shape and color. Place it naturally on a carefully styled designer table; integrate the supplied logo reference as a tasteful small dimensional 3DPrintHub sign on a distant shelf or wall, like a real branded showroom. Use cinematic golden-hour window light, tactile real materials, layered foreground/background depth and a rich complementary palette. Asymmetric vertical composition: product prominent in the lower-middle, Persian headline in a floating upper-right editorial panel, one short Persian line on a contrasting lower-left ribbon. Distinct premium Persian type; do not make a sterile catalog shot.",
    "surreal_safe": "Make a daring, art-directed surreal product campaign with impossible but elegant spatial perspective, sculptural floating planes, luminous volumetric rays and a dramatic portal-like frame. Keep the actual product completely photorealistic and unchanged: exact silhouette, geometry, colors, count of parts and proportions. The surreal elements must surround the product rather than fuse with or redesign it. Integrate the supplied logo reference as a dimensional floating brass seal. Use a vivid but product-harmonized palette, sharp visual storytelling, asymmetrical frame and expressive custom Persian display lettering; reserve a clean contrasting region for the supplied short Persian copy.",
    "minimal_frame": "Create a bold typography-led luxury advertisement, deliberately not a minimal product card. Use an architectural double frame with a broken diagonal gold corner, deep navy field and a dramatic product-scale crop while keeping the whole object recognizable. Add the supplied brand mark as a precise embossed 3D corner crest. Layout must differ from all other styles: oversized Persian headline spanning the top quarter, a vertical micro-copy strip on one side, the product breaking through the frame, and a compact gold CTA plate at the bottom. Typography is a distinctive Persian Nastaliq-inspired display paired with a clean modern Persian sans for supporting copy; high contrast, polished campaign finish.",
    "post_hero": "Instagram 4:5 campaign key visual; exact complete product, sculptural branded stage, supplied 3DPrintHub mark as a dimensional set element, cinematic navy/gold lighting and a strong Persian headline hierarchy.",
    "post_detail": "Editorial product-detail photograph emphasizing only visible real texture and form; avoid fabricated close-up features or labels.",
    "post_use_case": "Natural product-in-use editorial scene; plausible scale and environment, product remains visually dominant, no invented functions.",
    "post_comparison": "Single-canvas visual composition combining a faithful full-product view with a restrained detail view; do not imply measurements or comparisons not supplied.",
    "post_editorial": "Magazine-style product editorial, controlled complementary colors and refined lighting; reserve negative space for Persian copy added locally.",
    "post_minimal": "Minimal brand-ready product portrait; complete product on a quiet background, fine gold border, small unobtrusive lower-left brand-safe area.",
}


def _price(endpoint: dict[str, Any]) -> float:
    pricing = endpoint.get("pricing") or []
    output_values = []
    unclassified_values = []
    for item in pricing:
        try:
            value = float(item.get("cost_usd"))
        except (TypeError, ValueError):
            continue
        billable = str(item.get("billable") or "").strip().lower()
        if billable == "output_image":
            output_values.append(value)
        elif not billable:
            unclassified_values.append(value)
    if output_values:
        return min(output_values)
    # Older endpoint payloads contained one unlabelled image price. Never infer
    # an output price from a labelled input_image entry (often priced at zero).
    if len(pricing) == 1 and len(unclassified_values) == 1:
        return unclassified_values[0]
    return float("inf")


def _price_unit(endpoint: dict[str, Any]) -> str:
    for item in endpoint.get("pricing") or []:
        if str(item.get("billable") or "").strip().lower() == "output_image":
            return str(item.get("unit") or "unknown").strip().lower()
    pricing = endpoint.get("pricing") or []
    if len(pricing) == 1 and not str(pricing[0].get("billable") or "").strip():
        return str(pricing[0].get("unit") or "unknown").strip().lower()
    return "unknown"


def _billable_rate(endpoint: dict[str, Any], billable: str) -> tuple[float | None, str]:
    for item in endpoint.get("pricing") or []:
        if str(item.get("billable") or "").strip().lower() == billable:
            try:
                return float(item.get("cost_usd")), str(item.get("unit") or "unknown").strip().lower()
            except (TypeError, ValueError):
                return None, "unknown"
    return None, "unknown"


def supports_aspect_ratio(supported_parameters: dict[str, Any], ratio: str) -> bool:
    spec = (supported_parameters or {}).get("aspect_ratio") or {}
    values = spec.get("values") if isinstance(spec, dict) else None
    return isinstance(values, (list, tuple)) and str(ratio) in {str(value) for value in values}


def supports_reference_count(supported_parameters: dict[str, Any], count: int) -> bool:
    spec = (supported_parameters or {}).get("input_references") or {}
    maximum = spec.get("max") if isinstance(spec, dict) else None
    try:
        return int(maximum) >= int(count)
    except (TypeError, ValueError):
        return False


def discover_image_endpoints(api_key: str, *, opener=urllib.request.urlopen) -> list[dict[str, Any]]:
    """Return image endpoints that accept references and a requested ratio.

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
            if "input_references" not in supported or "aspect_ratio" not in supported:
                continue
            if not supports_reference_count(supported, 2):
                continue
            if not supports_aspect_ratio(supported, "9:16") or not supports_aspect_ratio(supported, "4:5"):
                continue
            provider_tag = str(endpoint.get("provider_tag") or "").strip()
            if not provider_tag:
                continue
            output_cost, output_unit = _billable_rate(endpoint, "output_image")
            input_cost, input_unit = _billable_rate(endpoint, "input_image")
            estimated_cost = None
            if output_cost is not None and output_unit == "image":
                if input_cost is None:
                    # No advertised input line is not proof that references are free.
                    estimated_cost = None
                elif input_unit == "image":
                    estimated_cost = output_cost + (2 * input_cost)
            candidates.append({
                "model": model_id,
                "provider": provider_tag,
                "provider_slug": str(endpoint.get("provider_slug") or ""),
                "provider_tag": provider_tag,
                "cost_usd": output_cost if output_cost is not None else _price(endpoint),
                "cost_unit": output_unit if output_cost is not None else _price_unit(endpoint),
                "input_cost_usd": input_cost,
                "input_cost_unit": input_unit,
                "estimated_cost_usd": estimated_cost,
                "estimated_cost_unit": "image" if estimated_cost is not None else "unknown",
                "supported_parameters": supported,
            })
    if not candidates:
        raise RuntimeError("No OpenRouter image endpoint supports both input references and aspect ratio.")
    # Cost units are not directly comparable (USD/image vs USD/output-token).
    # Keep rates grouped by unit; the UI must disclose this distinction.
    return sorted(candidates, key=lambda item: (
        0 if item["estimated_cost_unit"] == "image" else 1,
        item["estimated_cost_unit"],
        item["estimated_cost_usd"] if item["estimated_cost_usd"] is not None else item["cost_usd"],
        item["model"], item["provider"],
    ))


def discover_cheapest_image_endpoint(api_key: str, *, opener=urllib.request.urlopen) -> dict[str, Any]:
    """Return the cheapest compatible image endpoint without generating."""
    return discover_image_endpoints(api_key, opener=opener)[0]


def _plain_text(value: Any, limit: int) -> str:
    text = html.unescape(re.sub(r"<[^>]*>", " ", str(value or "")))
    return re.sub(r"\s+", " ", text).strip()[:limit]


def brand_reference_image() -> tuple[bytes, str]:
    path = Path(__file__).resolve().parents[1] / "assets" / "brand_logo_horizontal.png"
    if not path.is_file():
        return b"", ""
    return path.read_bytes(), mimetypes.guess_type(path.name)[0] or "image/png"


def build_product_prompt(
    product: dict[str, Any],
    style: CreativeStyle,
    *,
    language: str = "fa",
    ai_content: bool = True,
    discount_percent: int = 0,
) -> str:
    """Build a fact-bound English art-direction prompt with explicit Persian copy."""
    title = _plain_text(product.get("title_fa") or product.get("name_fa") or product.get("source_title"), 120)
    description = _plain_text(
        product.get("short_description_fa") or product.get("source_description") or product.get("description"),
        320,
    )
    copy_lines = []
    if ai_content:
        copy_lines.extend((f"Exact Persian headline: «{title}»", "Exact Persian CTA: «مشاهده محصول»"))
        if description:
            copy_lines.append(f"Exact Persian supporting line, fact-bound: «{description[:110]}»")
        if int(discount_percent or 0) > 0:
            copy_lines.append(f"Operator-approved exact discount badge: «{int(discount_percent)}٪ تخفیف»")
    copy_contract = "\n".join(copy_lines) if copy_lines else "Do not add any advertising copy or text."
    return (
        "Create a complete premium branded Instagram advertising composition, not a plain product cutout. "
        "Reference image 1 is the authoritative physical Product; reference image 2 is the official 3DPrintHub logo. "
        f"Product identity (never rename): {title}. Verified Product facts only: {description}. "
        f"Art direction {style.key}: {STYLE_PROMPTS_EN.get(style.key, style.description)} "
        f"Canvas ratio: {style.format}. Product-specific Persian copy supplied for the layout:\n{copy_contract}\n"
        "Render only these exact Persian words, right-to-left with correct spelling and connected glyphs; "
        "do not translate, paraphrase, add claims, prices, specifications, dimensions, hashtags, or extra text. "
        "Use the exact supplied logo as a dimensional sign/badge in the scene; do not invent or alter the brand mark. "
        "Keep the product silhouette, geometry, proportions, color and number of parts faithful to reference 1. "
        "Never print a URL, @mention, link sticker, or unapproved discount inside the image; those are handled as publication metadata. "
        "Distinctive Persian display typography, visually varied frame geometry and text placement unique to this selected style; "
        "professional campaign art direction, strong contrast, deliberate safe margins, no watermark."
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
    reference_mime_type: str = "image/png",
    brand_reference_bytes: bytes = b"",
    brand_reference_mime_type: str = "image/png",
    provider_tag: str = "",
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
    if not isinstance(brand_reference_bytes, (bytes, bytearray)) or len(brand_reference_bytes) < 64:
        raise ValueError("The official 3DPrintHub brand reference image is required.")
    mime = str(reference_mime_type or "").strip().lower()
    if not mime.startswith("image/"):
        mime = mimetypes.guess_type("product.png")[0] or "image/png"
    reference = f"data:{mime};base64,{base64.b64encode(bytes(reference_bytes)).decode('ascii')}"
    brand_mime = str(brand_reference_mime_type or "").strip().lower()
    if not brand_mime.startswith("image/"):
        brand_mime = mimetypes.guess_type("brand.png")[0] or "image/png"
    brand_reference = f"data:{brand_mime};base64,{base64.b64encode(bytes(brand_reference_bytes)).decode('ascii')}"
    payload = {
        "model": model_id,
        "prompt": str(prompt or "").strip(),
        "input_references": [
            {"type": "image_url", "image_url": {"url": reference}},
            {"type": "image_url", "image_url": {"url": brand_reference}},
        ],
        "aspect_ratio": str(aspect_ratio or "1:1"),
        "n": 1,
        "output_format": "png",
    }
    tag = str(provider_tag or "").strip()
    if not tag:
        raise ValueError("A discovered and pinned OpenRouter image provider is required.")
    payload["provider"] = {"only": [tag], "allow_fallbacks": False}
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
    *,
    provider_tag: str = "",
    brand_reference_bytes: bytes = b"",
) -> str:
    """Stable identity used to avoid paying twice for the same generation request."""
    digest = hashlib.sha256()
    for value in (
        str(int(product_id)), str(kind), style.key, str(model).strip(),
        str(prompt), str(provider_tag).strip(), hashlib.sha256(bytes(reference_bytes)).hexdigest(),
        hashlib.sha256(bytes(brand_reference_bytes)).hexdigest() if brand_reference_bytes else "no-brand-reference",
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
