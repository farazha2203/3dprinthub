from __future__ import annotations

import math
import re
from typing import Any

_PERSIAN_RE = re.compile(r"[\u0600-\u06FF]")

# Internal operational ranking, not a provider guarantee.
# Live Provider catalogues remain the authority for model identity and price.
_FAMILY_RULES = (
    (("qwen",), 5, 96, "عالی"),
    (("gemini",), 5, 98, "عالی"),
    (("gpt-", "openai/"), 5, 99, "عالی"),
    (("claude",), 5, 98, "عالی"),
    (("deepseek",), 5, 94, "عالی"),
    (("gemma",), 4, 90, "خوب"),
    (("command-r", "command-a", "cohere"), 4, 89, "خوب"),
    (("mistral", "mixtral"), 4, 87, "خوب"),
    (("llama",), 4, 85, "خوب"),
    (("phi",), 3, 78, "احتمالی"),
)

_NATIVE_STRUCTURED_HINTS = {
    "response_format",
    "structured_outputs",
    "json_schema",
}

_TOOL_STRUCTURED_HINTS = {
    "tools",
    "tool_choice",
}

_MEDIA_PRODUCT_BLOCK_HINTS = (
    "lyria",
    "music generation",
    "audio generation",
    "video generation",
    "image generation",
    "text-to-audio",
    "text to audio",
    "text-to-video",
    "text to video",
    "embedding",
    "rerank",
    "moderation",
    "text-to-speech",
    "text to speech",
    "speech-to-text",
    "speech to text",
    "whisper",
)

_CODE_SPECIALIST_HINTS = (
    "north-mini-code",
    "agentic coding",
    "coding model",
    "code model",
    "software engineering",
    "terminal tasks",
)

# Live catalog presence/capability is still mandatory. These are only a
# current Persian/free preference boost when the exact model is actually
# returned by OpenRouter and passes Product text + Structured checks.
_PERSIAN_FREE_PREFERRED = {
    "qwen/qwen3-32b:free": 100,
    "google/gemma-4-31b-it:free": 96,
    "openai/gpt-oss-20b:free": 94,
    "google/gemma-4-26b-a4b-it:free": 90,
    "qwen/qwen3-30b-a3b:free": 88,
}


def _number(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def pricing_per_million(pricing: dict[str, Any] | None) -> dict[str, float | None]:
    pricing = pricing if isinstance(pricing, dict) else {}
    prompt = _number(pricing.get("prompt"))
    completion = _number(pricing.get("completion"))
    request = _number(pricing.get("request"))
    return {
        "prompt": prompt * 1_000_000 if prompt is not None else None,
        "completion": completion * 1_000_000 if completion is not None else None,
        "request": request,
    }


def persian_profile(
    model_id: str,
    *,
    name: str = "",
    description: str = "",
) -> dict[str, Any]:
    text = " ".join(
        (str(model_id or ""), str(name or ""), str(description or ""))
    ).casefold()

    if "persian" in text or "farsi" in text or "فارسی" in text:
        return {
            "score": 6,
            "label": "تأییدشده در توضیح مدل",
            "source": "provider_description",
            "quality": 100,
        }

    for needles, score, quality, label in _FAMILY_RULES:
        if any(needle in text for needle in needles):
            return {
                "score": score,
                "label": label,
                "source": "3dprinthub_family_rank",
                "quality": quality,
            }

    multilingual = any(
        token in text
        for token in (
            "multilingual",
            "multi-lingual",
            "many languages",
            "100+ languages",
            "140 languages",
        )
    )
    if multilingual:
        return {
            "score": 3,
            "label": "احتمالی",
            "source": "provider_multilingual_description",
            "quality": 76,
        }

    return {
        "score": 1,
        "label": "نامشخص",
        "source": "unknown",
        "quality": 60,
    }


def _modalities(item: dict[str, Any]) -> tuple[set[str], set[str]]:
    architecture = (
        item.get("architecture")
        if isinstance(item.get("architecture"), dict)
        else {}
    )

    def normalize(value: Any) -> set[str]:
        if isinstance(value, (list, tuple, set)):
            return {
                str(part or "").strip().casefold()
                for part in value
                if str(part or "").strip()
            }
        if isinstance(value, str) and value.strip():
            return {
                part.strip().casefold()
                for part in re.split(r"[,+/|]", value)
                if part.strip()
            }
        return set()

    input_modalities = normalize(architecture.get("input_modalities"))
    output_modalities = normalize(architecture.get("output_modalities"))

    raw_modality = str(architecture.get("modality") or "").strip().casefold()
    if raw_modality and "->" in raw_modality:
        left, right = raw_modality.split("->", 1)
        input_modalities |= normalize(left)
        output_modalities |= normalize(right)

    return input_modalities, output_modalities


def enrich_model_info(item: dict[str, Any]) -> dict[str, Any]:
    output = dict(item or {})
    model_id = str(output.get("id") or output.get("name") or "").strip()
    name = str(output.get("name") or model_id).strip()
    description = str(output.get("description") or "").strip()
    pricing = (
        output.get("pricing")
        if isinstance(output.get("pricing"), dict)
        else {}
    )
    per_million = pricing_per_million(pricing)

    numeric_prices = [
        value
        for value in (
            per_million["prompt"],
            per_million["completion"],
        )
        if value is not None
    ]
    explicit_free = (
        bool(output.get("free"))
        or model_id.endswith(":free")
        or model_id == "openrouter/free"
    )
    zero_priced = bool(numeric_prices) and max(numeric_prices) == 0
    free = bool(explicit_free or zero_priced)

    supported = {
        str(value or "").strip().lower()
        for value in (output.get("supported_parameters") or [])
        if str(value or "").strip()
    }
    native_structured_score = len(
        supported & _NATIVE_STRUCTURED_HINTS
    )
    tool_structured_score = len(
        supported & _TOOL_STRUCTURED_HINTS
    )

    input_modalities, output_modalities = _modalities(output)
    identity_text = " ".join(
        (model_id, name, description)
    ).casefold()
    blocked_media_hint = any(
        token in identity_text
        for token in _MEDIA_PRODUCT_BLOCK_HINTS
    )

    if output_modalities:
        text_output = "text" in output_modalities
    else:
        text_output = not blocked_media_hint

    if input_modalities:
        text_input = "text" in input_modalities
    else:
        text_input = True

    product_text_capable = bool(
        text_input
        and text_output
        and not blocked_media_hint
    )
    code_specialized = any(
        token in identity_text
        for token in _CODE_SPECIALIST_HINTS
    )
    native_structured = native_structured_score > 0
    tool_structured_only = (
        tool_structured_score > 0
        and not native_structured
    )

    persian = persian_profile(
        model_id,
        name=name,
        description=description,
    )

    avg_cost = (
        sum(numeric_prices) / len(numeric_prices)
        if numeric_prices
        else float("inf")
    )

    product_ready = bool(
        product_text_capable
        and native_structured
        and not code_specialized
    )

    preferred_free_score = int(
        _PERSIAN_FREE_PREFERRED.get(model_id, 0)
    )

    output.update(
        {
            "id": model_id,
            "name": name,
            "description": description,
            "pricing": pricing,
            "price_per_million": per_million,
            "free": free,
            "persian_score": int(persian["score"]),
            "persian_label": str(persian["label"]),
            "persian_rank_source": str(persian["source"]),
            "quality_score": int(persian["quality"]),
            "structured_score": int(native_structured_score),
            "native_structured": native_structured,
            "tool_structured_only": tool_structured_only,
            "product_text_capable": product_text_capable,
            "product_ready": product_ready,
            "code_specialized": code_specialized,
            "persian_free_preferred_score": preferred_free_score,
            "persian_free_preferred": bool(preferred_free_score),
            "input_modalities": sorted(input_modalities),
            "output_modalities": sorted(output_modalities),
            "_avg_cost": avg_cost,
        }
    )
    return output


def model_sort_key(item: dict[str, Any]) -> tuple:
    model = enrich_model_info(item)
    return (
        0 if model.get("product_ready") else 1,
        0 if model.get("product_text_capable") else 1,
        -int(model.get("persian_score") or 0),
        0 if model.get("native_structured") else 1,
        0 if model.get("free") else 1,
        -int(model.get("persian_free_preferred_score") or 0),
        1 if model.get("code_specialized") else 0,
        -int(model.get("quality_score") or 0),
        float(model.get("_avg_cost") or float("inf")),
        str(model.get("id") or "").casefold(),
    )


def rank_models(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched = [
        enrich_model_info(item)
        for item in (items or [])
        if isinstance(item, dict)
    ]
    return sorted(enriched, key=model_sort_key)


def pricing_summary_text(item: dict[str, Any]) -> str:
    model = enrich_model_info(item)
    if model.get("free"):
        return "رایگان"

    prices = model.get("price_per_million") or {}
    prompt = prices.get("prompt")
    completion = prices.get("completion")
    if prompt is None and completion is None:
        return "هزینه: نامشخص"

    left = "—" if prompt is None else "$" + f"{float(prompt):.4g}"
    right = "—" if completion is None else "$" + f"{float(completion):.4g}"
    return f"ورودی {left} / خروجی {right} به‌ازای 1M توکن"


def format_model_label(item: dict[str, Any]) -> str:
    model = enrich_model_info(item)
    badges = []
    if model.get("free"):
        badges.append("🆓 رایگان")
    if (
        model.get("persian_free_preferred")
        and model.get("product_ready")
    ):
        badges.append("⭐ فارسی پیشنهادی")
    if int(model.get("persian_score") or 0) >= 4:
        badges.append(f"🇮🇷 فارسی {model.get('persian_label')}")
    elif int(model.get("persian_score") or 0) >= 2:
        badges.append(f"FA {model.get('persian_label')}")
    if model.get("native_structured"):
        badges.append("JSON✓")
    elif model.get("tool_structured_only"):
        badges.append("⚠️ Tools-only")
    if model.get("code_specialized"):
        badges.append("⚠️ تخصص کدنویسی")
    if not model.get("product_text_capable"):
        badges.append("⛔ غیرمتنی")

    prefix = " • ".join(badges)
    name = str(model.get("name") or model.get("id") or "")
    model_id = str(model.get("id") or "")
    identity = model_id if name == model_id else f"{name} — {model_id}"
    price = pricing_summary_text(model)
    return " • ".join(part for part in (prefix, identity, price) if part)


def model_matches_filter(item: dict[str, Any], filter_code: str) -> bool:
    model = enrich_model_info(item)
    code = str(filter_code or "all")
    if code == "free":
        return bool(
            model.get("free")
            and model.get("product_text_capable")
        )
    if code == "persian_free":
        return bool(
            model.get("free")
            and model.get("product_ready")
            and int(model.get("persian_score") or 0) >= 4
        )
    if code == "persian":
        return bool(
            model.get("product_text_capable")
            and int(model.get("persian_score") or 0) >= 4
        )
    if code == "structured":
        return bool(
            model.get("product_text_capable")
            and model.get("native_structured")
        )
    if code == "recommended":
        return bool(
            model.get("product_ready")
            and int(model.get("persian_score") or 0) >= 4
        )
    return bool(model.get("product_text_capable"))


def product_model_compatibility(
    item: dict[str, Any],
    *,
    require_structured: bool = True,
) -> tuple[bool, str]:
    model = enrich_model_info(item)
    model_id = str(model.get("id") or "مدل انتخابی")

    if not model.get("product_text_capable"):
        return (
            False,
            f"{model_id} خروجی متنی مناسب Product ندارد؛ "
            "مدل‌های Music/Audio/Video/Image/Embedding/Rerank "
            "برای تولید محتوای محصول قابل استفاده نیستند.",
        )

    if model.get("code_specialized"):
        return (
            False,
            f"{model_id} مدل تخصصی کدنویسی/Agentic Code است و "
            "برای ترجمه، SEO و محتوای فارسی Product انتخاب مطمئنی نیست.",
        )

    if require_structured and not model.get("native_structured"):
        if model.get("tool_structured_only"):
            return (
                False,
                f"{model_id} فقط Tools/Tool Calling دارد ولی "
                "response_format / JSON Schema اجباری را برای این مسیر "
                "Product پشتیبانی نمی‌کند.",
            )
        return (
            False,
            f"{model_id} پشتیبانی قابل تأیید response_format / "
            "Structured JSON برای مسیر Product ندارد.",
        )

    return True, ""


def estimate_text_tokens(text: str) -> int:
    value = str(text or "")
    if not value:
        return 0
    persian_chars = len(_PERSIAN_RE.findall(value))
    latinish = max(0, len(value) - persian_chars)
    return max(
        1,
        int(math.ceil(persian_chars / 2.2 + latinish / 3.8)),
    )


def estimate_request_cost(
    item: dict[str, Any],
    *,
    input_tokens: int,
    output_tokens: int,
) -> dict[str, Any]:
    model = enrich_model_info(item)
    prices = model.get("price_per_million") or {}
    prompt = prices.get("prompt")
    completion = prices.get("completion")
    request_fee = prices.get("request")

    if model.get("free"):
        return {
            "known": True,
            "usd": 0.0,
            "free": True,
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
        }

    if prompt is None and completion is None and request_fee is None:
        return {
            "known": False,
            "usd": None,
            "free": False,
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
        }

    total = 0.0
    if prompt is not None:
        total += max(0, int(input_tokens)) * float(prompt) / 1_000_000
    if completion is not None:
        total += max(0, int(output_tokens)) * float(completion) / 1_000_000
    if request_fee is not None:
        total += max(0.0, float(request_fee))

    return {
        "known": True,
        "usd": total,
        "free": total == 0,
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
    }


def contains_persian(value: Any) -> bool:
    return bool(_PERSIAN_RE.search(str(value or "")))


def format_cost_quote(quote: dict[str, Any]) -> str:
    provider = str(quote.get("provider") or "—")
    model = str(quote.get("model") or "—")
    scope = str(quote.get("scope_label") or "—")
    persian = str(quote.get("persian_label") or "نامشخص")
    input_tokens = int(quote.get("input_tokens") or 0)
    output_tokens = int(quote.get("output_tokens") or 0)

    if quote.get("free"):
        cost = "رایگان"
    elif quote.get("cost_known"):
        usd = float(quote.get("estimated_usd") or 0)
        cost = "حدود $" + f"{usd:.6f}"
        toman = float(quote.get("estimated_toman") or 0)
        if toman > 0:
            cost += f"  ≈  {toman:,.0f} تومان"
    else:
        cost = "نامشخص؛ Provider قیمت قابل محاسبه برنگرداند"

    return (
        f"Provider: {provider}\n"
        f"Model: {model}\n"
        f"رتبه فارسی داخلی: {persian}\n"
        f"محدوده اجرا: {scope}\n"
        f"توکن تخمینی ورودی/خروجی: {input_tokens:,} / {output_tokens:,}\n"
        f"هزینه تخمینی این اجرا: {cost}\n\n"
        "این عدد تقریبی است و بر اساس Model metadata و اندازه فعلی Product محاسبه می‌شود."
    )
