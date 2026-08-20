from __future__ import annotations

import json
import time
from typing import Any
from urllib import error, request

from . import ai_providers
from .ai_providers import AIProviderClient, ProviderSpec

GOOGLE_CODE = "google"
GOOGLE_BASE = "https://generativelanguage.googleapis.com/v1beta"


def _request_id(headers) -> str:
    if headers is None:
        return ""
    for key in ("x-request-id", "x-goog-request-id", "x-cloud-trace-context"):
        try:
            value = headers.get(key)
        except Exception:
            value = ""
        if value:
            return str(value)
    return ""


def _google_request(
    api_key: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    method: str = "GET",
    timeout: int = 30,
    model: str = "",
    operation: str = "",
    product_id: int | None = None,
) -> dict[str, Any]:
    url = GOOGLE_BASE.rstrip("/") + "/" + path.lstrip("/")
    headers = {
        "x-goog-api-key": str(api_key or "").strip(),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "3DPrintHub-Catalog-Intelligence/8.7.1",
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = request.Request(url, data=body, headers=headers, method=method)
    started = time.perf_counter()
    try:
        with request.urlopen(req, timeout=max(1, min(210, int(timeout or 30)))) as response:
            raw = response.read().decode("utf-8", errors="replace")
            data = json.loads(raw) if raw.strip() else {}
            metadata = data.get("usageMetadata") if isinstance(data, dict) else {}
            usage = {
                "prompt_tokens": int((metadata or {}).get("promptTokenCount") or 0),
                "completion_tokens": int((metadata or {}).get("candidatesTokenCount") or 0),
                "total_tokens": int((metadata or {}).get("totalTokenCount") or 0),
            }
            rid = _request_id(response.headers)
            ai_providers.ai_request_event(
                provider=GOOGLE_CODE,
                model=model,
                operation=operation or method.lower(),
                endpoint=url,  # API key is in a header, never in this logged URL.
                request_id=rid,
                http_status=getattr(response, "status", 200),
                status="ok",
                duration_ms=int((time.perf_counter() - started) * 1000),
                usage=usage,
                product_id=product_id,
                request_summary={"method": method, "payload_keys": sorted((payload or {}).keys())},
                response_summary={"model": model, "usage": usage},
            )
            if isinstance(data, dict):
                data.setdefault("_request_id", rid)
                data.setdefault("usage", usage)
            return data
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        rid = _request_id(exc.headers)
        ai_providers.ai_request_event(
            provider=GOOGLE_CODE,
            model=model,
            operation=operation or method.lower(),
            endpoint=url,
            request_id=rid,
            http_status=exc.code,
            status="error",
            duration_ms=int((time.perf_counter() - started) * 1000),
            product_id=product_id,
            error_text=detail,
        )
        raise RuntimeError(f"Google Gemini HTTP {exc.code}: {detail[:1400]}") from exc
    except error.URLError as exc:
        ai_providers.ai_request_event(
            provider=GOOGLE_CODE,
            model=model,
            operation=operation or method.lower(),
            endpoint=url,
            status="error",
            duration_ms=int((time.perf_counter() - started) * 1000),
            product_id=product_id,
            error_text=str(exc),
        )
        raise RuntimeError(f"Google Gemini connection error: {exc}") from exc


def _gemini_text(data: dict[str, Any]) -> str:
    chunks = []
    for candidate in data.get("candidates") or []:
        if not isinstance(candidate, dict):
            continue
        content = candidate.get("content") or {}
        for part in content.get("parts") or []:
            if isinstance(part, dict) and part.get("text"):
                chunks.append(str(part.get("text")))
    return "\n".join(chunks).strip()


def _strip_fence(text: str) -> str:
    value = str(text or "").strip()
    if value.startswith("```"):
        lines = value.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        value = "\n".join(lines).strip()
    return value


def _google_model_info(client: AIProviderClient, timeout=30) -> list[dict[str, Any]]:
    data = _google_request(
        client.api_key,
        "models",
        timeout=timeout,
        operation="list_models",
        product_id=client.product_id,
    )
    output = []
    for item in data.get("models") or []:
        if not isinstance(item, dict):
            continue
        methods = list(item.get("supportedGenerationMethods") or [])
        if "generateContent" not in methods:
            continue
        raw_name = str(item.get("name") or "")
        model_id = raw_name.split("models/", 1)[-1].strip()
        if not model_id:
            continue
        output.append({
            "id": model_id,
            "name": str(item.get("displayName") or model_id),
            "pricing": {},
            "supported_parameters": methods,
            "context_length": item.get("inputTokenLimit"),
            "free": False,
        })
    return output


def _generate(client: AIProviderClient, model: str, prompt: str, *, schema=None, timeout=180, operation="structured_content") -> dict:
    config: dict[str, Any] = {"responseMimeType": "application/json" if schema is not None else "text/plain"}
    if schema is not None:
        config["responseSchema"] = schema
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": config,
    }
    path = f"models/{model}:generateContent"
    try:
        return _google_request(
            client.api_key,
            path,
            payload=payload,
            method="POST",
            timeout=timeout,
            model=model,
            operation=operation,
            product_id=client.product_id,
        )
    except RuntimeError as exc:
        if schema is None or not any(token in str(exc).lower() for token in ("400", "schema", "generationconfig", "response")):
            raise
        # Some Gemini models expose generateContent but do not accept the full
        # JSON schema dialect. Retry once with JSON MIME only and keep client-side
        # validation, matching the existing OpenRouter/AvalAI compatibility rule.
        payload["generationConfig"] = {"responseMimeType": "application/json"}
        return _google_request(
            client.api_key,
            path,
            payload=payload,
            method="POST",
            timeout=timeout,
            model=model,
            operation=operation + "_compat",
            product_id=client.product_id,
        )


def install() -> None:
    if getattr(AIProviderClient, "_phase49_3f_google_installed", False):
        return

    ai_providers.PROVIDERS[GOOGLE_CODE] = ProviderSpec(
        GOOGLE_CODE,
        "Google Gemini Direct",
        GOOGLE_BASE,
        False,
    )

    original_list = AIProviderClient.list_model_info
    original_test = AIProviderClient.test_connection
    original_balance = AIProviderClient.balance_info
    original_structured = AIProviderClient.structured_response

    def list_model_info(self):
        if self.provider != GOOGLE_CODE:
            return original_list(self)
        return _google_model_info(self, timeout=30)

    def test_connection(self, preferred=""):
        if self.provider != GOOGLE_CODE:
            return original_test(self, preferred)
        info = _google_model_info(self, timeout=30)
        models = [item["id"] for item in info]
        preferred_clean = str(preferred or self.model or "").replace("models/", "").strip()
        model = preferred_clean if preferred_clean in models else (models[0] if models else "")
        if not model:
            raise RuntimeError("Google Gemini متصل شد اما هیچ مدل generateContent در این API Key دیده نشد.")
        data = _generate(self, model, "فقط واژه فارسی «آماده» را برگردان.", schema=None, timeout=30, operation="connection_test")
        text = _gemini_text(data)
        if not text:
            raise RuntimeError("Google Gemini پاسخ تست متنی برنگرداند.")
        return {
            "provider": GOOGLE_CODE,
            "provider_label": "Google Gemini Direct",
            "model": model,
            "models_count": len(info),
            "sample": text[:120],
            "free": False,
            "pricing": {},
            "request_id": data.get("_request_id") or "",
            "usage": data.get("usage") or {},
        }

    def balance_info(self, *, management_key="", admin_key=""):
        if self.provider != GOOGLE_CODE:
            return original_balance(self, management_key=management_key, admin_key=admin_key)
        return {
            "available": False,
            "reason": "Google AI Studio مانده اعتبار استاندارد را از این API Key ارائه نمی‌کند؛ مصرف از کنسول Google بررسی می‌شود.",
        }

    def structured_response(self, *, instructions, input_content, schema, schema_name, preferred_model=""):
        if self.provider != GOOGLE_CODE:
            return original_structured(
                self,
                instructions=instructions,
                input_content=input_content,
                schema=schema,
                schema_name=schema_name,
                preferred_model=preferred_model,
            )
        info = _google_model_info(self, timeout=30)
        models = [item["id"] for item in info]
        preferred_clean = str(preferred_model or self.model or "").replace("models/", "").strip()
        model = preferred_clean if preferred_clean in models else (models[0] if models else "")
        if not model:
            raise RuntimeError("هیچ مدل Gemini سازگار برای تولید محتوا پیدا نشد.")
        prompt = (
            instructions.strip()
            + "\n\nReturn exactly one valid JSON object. Do not use Markdown fences."
            + f"\nSchema name: {schema_name}"
            + "\nInput facts:\n"
            + json.dumps(input_content, ensure_ascii=False, default=str)
        )
        data = _generate(self, model, prompt, schema=schema, timeout=180, operation="structured_content")
        text = _strip_fence(_gemini_text(data))
        if not text:
            raise RuntimeError("Google Gemini خروجی JSON برنگرداند.")
        try:
            result = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Google Gemini JSON نامعتبر برگرداند: {text[:700]}") from exc
        if not isinstance(result, dict):
            raise RuntimeError("Google Gemini JSON برگرداند اما مقدار ریشه Object نیست.")
        return result, model

    def probe_connection(self, timeout=30):
        timeout = max(1, min(30, int(timeout or 30)))
        if self.provider == GOOGLE_CODE:
            info = _google_model_info(self, timeout=timeout)
            return {"provider": self.provider, "models_count": len(info), "connected": True}
        suffix = "?sort=pricing-low-to-high" if self.provider == "openrouter" else ""
        data = ai_providers._json_request(
            f"{self.spec.base_url}/models{suffix}",
            self.api_key,
            timeout=timeout,
            provider=self.provider,
            operation="connection_probe",
            product_id=self.product_id,
        )
        count = len(data.get("data") or []) if isinstance(data, dict) else 0
        return {"provider": self.provider, "models_count": count, "connected": True}

    AIProviderClient.list_model_info = list_model_info
    AIProviderClient.test_connection = test_connection
    AIProviderClient.balance_info = balance_info
    AIProviderClient.structured_response = structured_response
    AIProviderClient.probe_connection = probe_connection
    AIProviderClient._phase49_3f_google_installed = True
