from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import error, request


@dataclass(frozen=True)
class ProviderSpec:
    code: str
    label: str
    base_url: str


PROVIDERS = {
    "openai": ProviderSpec("openai", "OpenAI Direct", "https://api.openai.com/v1"),
    "avalai": ProviderSpec("avalai", "AvalAI", "https://api.avalai.ir/v1"),
}


def _json_request(url: str, key: str, *, payload: dict[str, Any] | None = None, method: str = "GET", timeout: int = 120) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {key.strip()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "3DPrintHub-Catalog-Intelligence/8.5",
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = request.Request(url, data=body, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw.strip() else {}
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"AI HTTP {exc.code}: {detail[:1600]}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"AI connection error: {exc}") from exc


def response_output_text(data: dict[str, Any]) -> str:
    if data.get("output_text"):
        return str(data["output_text"]).strip()
    parts: list[str] = []
    for item in data.get("output") or []:
        if not isinstance(item, dict):
            continue
        for content in item.get("content") or []:
            if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                parts.append(str(content.get("text") or ""))
    if parts:
        return "\n".join(parts).strip()
    choices = data.get("choices") or []
    if choices and isinstance(choices[0], dict):
        msg = choices[0].get("message") or {}
        content = msg.get("content")
        if isinstance(content, str):
            return content.strip()
    return ""


class AIProviderClient:
    def __init__(self, provider: str, api_key: str, model: str = ""):
        self.provider = provider if provider in PROVIDERS else "openai"
        self.spec = PROVIDERS[self.provider]
        self.api_key = (api_key or "").strip()
        self.model = (model or "").strip()
        if not self.api_key:
            raise RuntimeError(f"{self.spec.label} API key is not configured.")

    def list_models(self) -> list[str]:
        data = _json_request(f"{self.spec.base_url}/models", self.api_key, timeout=45)
        models = sorted({str(x.get("id")) for x in data.get("data", []) if isinstance(x, dict) and x.get("id")})
        return models

    def choose_model(self, preferred: str = "") -> str:
        models = self.list_models()
        preferred = (preferred or self.model or "").strip()
        if preferred and preferred in models:
            return preferred
        priorities = (
            ["gpt-5.4-mini", "gpt-5-mini", "gpt-5.4", "gpt-5"]
            if self.provider == "avalai"
            else ["gpt-5.4-mini", "gpt-5-mini", "gpt-5.4", "gpt-5"]
        )
        for candidate in priorities:
            if candidate in models:
                return candidate
        textish = [m for m in models if not any(t in m.lower() for t in ("image", "audio", "embedding", "tts", "whisper", "moderation"))]
        if textish:
            return textish[0]
        if models:
            return models[0]
        raise RuntimeError(f"No accessible models were returned by {self.spec.label}.")

    def test_connection(self, preferred: str = "") -> dict[str, Any]:
        models = self.list_models()
        model = self.choose_model(preferred)
        payload = {
            "model": model,
            "input": "Return only the Persian word: آماده",
            "max_output_tokens": 20,
        }
        try:
            data = _json_request(f"{self.spec.base_url}/responses", self.api_key, payload=payload, method="POST", timeout=90)
            text = response_output_text(data)
        except RuntimeError as exc:
            if self.provider != "avalai" or not any(token in str(exc).lower() for token in ("404", "unsupported", "unknown", "responses")):
                raise
            fallback = {
                "model": model,
                "messages": [{"role": "user", "content": "Return only the Persian word: آماده"}],
                "max_tokens": 20,
            }
            data = _json_request(f"{self.spec.base_url}/chat/completions", self.api_key, payload=fallback, method="POST", timeout=90)
            text = response_output_text(data)
        if not text:
            raise RuntimeError(f"{self.spec.label} connected, but the live response test returned no text.")
        return {"provider": self.provider, "provider_label": self.spec.label, "model": model, "models_count": len(models), "sample": text[:120]}

    def structured_response(self, *, instructions: str, input_content: list[dict[str, Any]], schema: dict[str, Any], schema_name: str, preferred_model: str = "") -> tuple[dict[str, Any], str]:
        model = self.choose_model(preferred_model)
        payload = {
            "model": model,
            "instructions": instructions,
            "input": [{"role": "user", "content": input_content}],
            "text": {"format": {"type": "json_schema", "name": schema_name, "schema": schema, "strict": True}},
        }
        try:
            data = _json_request(f"{self.spec.base_url}/responses", self.api_key, payload=payload, method="POST", timeout=210)
            text = response_output_text(data)
        except RuntimeError as exc:
            # Some OpenAI-compatible gateways may expose chat/completions but not full Responses structured format.
            if self.provider != "avalai" or not any(token in str(exc).lower() for token in ("404", "unsupported", "unknown", "response")):
                raise
            fallback = {
                "model": model,
                "messages": [
                    {"role": "system", "content": instructions + " Return valid JSON only, matching the requested schema."},
                    {"role": "user", "content": json.dumps(input_content, ensure_ascii=False)},
                ],
                "response_format": {"type": "json_object"},
            }
            data = _json_request(f"{self.spec.base_url}/chat/completions", self.api_key, payload=fallback, method="POST", timeout=210)
            text = response_output_text(data)
        if not text:
            raise RuntimeError(f"{self.spec.label} returned no output text.")
        try:
            return json.loads(text), model
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"{self.spec.label} returned invalid JSON: {text[:700]}") from exc
