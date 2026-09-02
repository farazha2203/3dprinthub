from __future__ import annotations

import hashlib
import os
import re
import time
from dataclasses import dataclass
from typing import Any

from catalog_center.app.ai_providers import AIProviderClient


_PROVIDER_KEYS = {
    "openrouter": "OPENROUTER_API_KEY",
    "avalai": "AVALAI_API_KEY",
    "google": "GOOGLE_GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
}
_PROVIDER_ORDER = ("openrouter", "avalai", "google", "openai")
_PERSIAN_RE = re.compile(r"[\u0600-\u06FF]")
_SELECTION_CACHE: dict[str, tuple[float, "RuntimeSelection"]] = {}


@dataclass(frozen=True)
class RuntimeSelection:
    provider: str
    model: str
    free: bool
    pricing: dict[str, Any]
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "free": self.free,
            "pricing": dict(self.pricing or {}),
            "reason": self.reason,
        }


def _env_int(name: str, default: int) -> int:
    try:
        return int(str(os.getenv(name, default)).strip())
    except Exception:
        return int(default)


def _env_float(name: str, default: float) -> float:
    try:
        return float(str(os.getenv(name, default)).strip())
    except Exception:
        return float(default)


def provider_key(provider: str) -> str:
    provider = str(provider or "").strip().lower()
    env_name = _PROVIDER_KEYS.get(provider, "")
    if env_name:
        value = str(os.getenv(env_name, "") or "").strip()
        if value:
            return value

    # Desktop may keep the same provider secret in Windows Credential Store.
    # Shared-host Django normally reaches this function through environment
    # variables only. The fallback never persists the secret to Django/SQLite.
    try:
        from catalog_center.app.secure_secrets import get_provider_key

        return str(get_provider_key(provider) or "").strip()
    except Exception:
        return ""


def _ensure_provider_installed(provider: str) -> None:
    if provider != "google":
        return
    from catalog_center.app.phase49_3f_gemini_provider import install

    install()


def configured_provider() -> str:
    explicit = str(
        os.getenv("AI_SITE_PROVIDER")
        or os.getenv("AI_DEFAULT_PROVIDER")
        or ""
    ).strip().lower()
    if explicit:
        if explicit not in _PROVIDER_ORDER:
            raise RuntimeError(
                f"AI provider {explicit!r} is not supported by the shared policy."
            )
        if not provider_key(explicit):
            raise RuntimeError(
                f"{_PROVIDER_KEYS[explicit]} is not configured for AI provider {explicit}."
            )
        _ensure_provider_installed(explicit)
        return explicit

    for provider in _PROVIDER_ORDER:
        if provider_key(provider):
            _ensure_provider_installed(provider)
            return provider
    raise RuntimeError(
        "No AI provider key is configured. Prefer OPENROUTER_API_KEY for the "
        "dynamic free/low-cost Persian Product policy."
    )


def _model_id(item: dict[str, Any]) -> str:
    return str((item or {}).get("id") or "").strip()


def _is_variable_router(model_id: str) -> bool:
    folded = str(model_id or "").strip().casefold()
    if folded in {"openrouter/free", "openrouter/auto", "openrouter/auto-beta"}:
        return True
    return (
        folded.endswith("/auto")
        or "/auto-" in folded
        or folded.endswith(":auto")
    )


def _looks_text_product_safe(item: dict[str, Any]) -> bool:
    model_id = _model_id(item)
    folded = (
        model_id
        + " "
        + str((item or {}).get("name") or "")
        + " "
        + str((item or {}).get("description") or "")
    ).casefold()
    banned = (
        "image generation",
        "text-to-image",
        "image-to-image",
        "embedding",
        "rerank",
        "moderation",
        "speech",
        "whisper",
        "text-to-speech",
        "audio",
        "music",
        "video generation",
        "vision-only",
    )
    if any(token in folded for token in banned):
        return False
    if any(token in model_id.casefold() for token in ("embed", "rerank", "moderation", "tts", "whisper")):
        return False
    return bool(model_id) and not _is_variable_router(model_id)


def _structured_capable(provider: str, item: dict[str, Any]) -> bool:
    if provider != "openrouter":
        return True
    supported = {
        str(value or "").strip().casefold()
        for value in ((item or {}).get("supported_parameters") or [])
    }
    return bool(
        supported.intersection(
            {"structured_outputs", "json_schema", "response_format"}
        )
    )


def _pricing_per_million(item: dict[str, Any]) -> tuple[float | None, float | None]:
    pricing = (item or {}).get("pricing")
    if not isinstance(pricing, dict):
        return None, None

    def value(name: str) -> float | None:
        try:
            raw = pricing.get(name)
            if raw in (None, ""):
                return None
            return max(0.0, float(raw) * 1_000_000)
        except Exception:
            return None

    return value("prompt"), value("completion")


def _is_free(item: dict[str, Any]) -> bool:
    model_id = _model_id(item)
    if bool((item or {}).get("free")) or model_id.endswith(":free"):
        return True
    prompt, completion = _pricing_per_million(item)
    values = [value for value in (prompt, completion) if value is not None]
    return bool(values) and max(values) == 0


def _within_paid_budget(item: dict[str, Any]) -> bool:
    limit = max(0.0, _env_float("AI_SITE_MAX_TOTAL_USD_PER_1M", 2.0))
    prompt, completion = _pricing_per_million(item)
    if prompt is None or completion is None:
        return False
    return (prompt + completion) <= limit


def _candidate_score(item: dict[str, Any]) -> tuple[int, int, float]:
    folded = (
        str((item or {}).get("name") or "")
        + " "
        + str((item or {}).get("description") or "")
    ).casefold()
    multilingual = int(
        any(token in folded for token in ("multilingual", "multi-lingual", "international"))
    )
    instruct = int(any(token in folded for token in ("instruct", "chat")))
    try:
        context = float((item or {}).get("context_length") or 0)
    except Exception:
        context = 0.0
    return multilingual, instruct, context


def _probe_persian_structured(
    provider: str,
    key: str,
    model_id: str,
) -> bool:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"answer": {"type": "string"}},
        "required": ["answer"],
    }
    client = AIProviderClient(provider, key, model_id)
    result, selected = client.structured_response(
        instructions=(
            "This is a tiny capability check for Persian ecommerce content. "
            "Return one natural Persian word only in answer."
        ),
        input_content=[
            {
                "type": "input_text",
                "text": "در answer فقط واژه فارسی «آماده» را برگردان.",
            }
        ],
        schema=schema,
        schema_name="shared_persian_probe_v1",
        preferred_model=model_id,
    )
    answer = str((result or {}).get("answer") or "").strip()
    return selected == model_id and bool(_PERSIAN_RE.search(answer))


def _selection_cache_key(provider: str, key: str) -> str:
    fingerprint = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
    return f"{provider}:{fingerprint}"


def resolve_product_model(*, force_refresh: bool = False) -> RuntimeSelection:
    provider = configured_provider()
    key = provider_key(provider)
    explicit_model = str(
        os.getenv("AI_SITE_PRODUCT_MODEL")
        or os.getenv("AI_DEFAULT_MODEL")
        or ""
    ).strip()
    if explicit_model:
        return RuntimeSelection(
            provider=provider,
            model=explicit_model,
            free=explicit_model.endswith(":free"),
            pricing={},
            reason="explicit-environment-model",
        )

    cache_key = _selection_cache_key(provider, key)
    ttl = max(300, _env_int("AI_SITE_MODEL_CACHE_SECONDS", 21_600))
    if not force_refresh:
        cached = _SELECTION_CACHE.get(cache_key)
        if cached and (time.time() - cached[0]) < ttl:
            return cached[1]

    client = AIProviderClient(provider, key)
    info = [
        dict(item)
        for item in client.list_model_info()
        if isinstance(item, dict)
        and _looks_text_product_safe(item)
        and _structured_capable(provider, item)
    ]
    if not info:
        raise RuntimeError(
            f"{provider} returned no Product-safe Structured text model."
        )

    free_candidates = sorted(
        [item for item in info if _is_free(item)],
        key=_candidate_score,
        reverse=True,
    )
    paid_candidates = sorted(
        [item for item in info if not _is_free(item) and _within_paid_budget(item)],
        key=lambda item: (
            sum(value or 0 for value in _pricing_per_million(item)),
            -_candidate_score(item)[0],
            -_candidate_score(item)[1],
        ),
    )

    probe_limit = min(8, max(1, _env_int("AI_SITE_MODEL_PROBE_LIMIT", 4)))
    failures: list[str] = []
    for group_name, candidates in (
        ("free-persian-structured", free_candidates[:probe_limit]),
        ("cheap-persian-structured", paid_candidates[:probe_limit]),
    ):
        for item in candidates:
            model_id = _model_id(item)
            try:
                if not _probe_persian_structured(provider, key, model_id):
                    failures.append(f"{model_id}: Persian probe failed")
                    continue
            except Exception as exc:
                failures.append(f"{model_id}: {type(exc).__name__}")
                continue
            selection = RuntimeSelection(
                provider=provider,
                model=model_id,
                free=_is_free(item),
                pricing=dict(item.get("pricing") or {}),
                reason=group_name,
            )
            _SELECTION_CACHE[cache_key] = (time.time(), selection)
            return selection

    detail = ", ".join(failures[:6])
    raise RuntimeError(
        "No verified free/low-cost Persian Structured Product model is currently "
        f"routable for {provider}. {detail}".strip()
    )


def runtime_config_status() -> dict[str, Any]:
    explicit = str(
        os.getenv("AI_SITE_PROVIDER")
        or os.getenv("AI_DEFAULT_PROVIDER")
        or ""
    ).strip().lower()
    configured = []
    for provider, env_name in _PROVIDER_KEYS.items():
        if provider_key(provider):
            configured.append({"provider": provider, "secret_source": env_name})
    return {
        "configured": bool(configured),
        "preferred_provider": explicit or "auto: openrouter -> avalai -> google -> openai",
        "providers": configured,
        "model_override": str(
            os.getenv("AI_SITE_PRODUCT_MODEL")
            or os.getenv("AI_DEFAULT_MODEL")
            or ""
        ).strip(),
        "policy": (
            "exact explicit model when configured; otherwise verified free "
            "Persian Structured model, then verified low-cost model within budget"
        ),
        "paid_budget_usd_per_1m": _env_float(
            "AI_SITE_MAX_TOTAL_USD_PER_1M", 2.0
        ),
    }
