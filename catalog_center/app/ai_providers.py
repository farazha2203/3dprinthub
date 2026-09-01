from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from typing import Any
from urllib import parse

import httpx

try:
    from .phase49_diagnostics import ai_request_event
except Exception:  # pragma: no cover - diagnostics is additive
    def ai_request_event(**_kwargs):
        return None


@dataclass(frozen=True)
class ProviderSpec:
    code: str
    label: str
    base_url: str
    chat_first: bool = False


PROVIDERS = {
    "openai": ProviderSpec("openai", "OpenAI Direct", "https://api.openai.com/v1", False),
    "avalai": ProviderSpec("avalai", "AvalAI", "https://api.avalai.ir/v1", True),
    "openrouter": ProviderSpec("openrouter", "OpenRouter", "https://openrouter.ai/api/v1", True),
}

_HTTP_CLIENT = None
_HTTP_CLIENT_LOCK = threading.Lock()
_OPENROUTER_MODEL_CAPABILITIES: dict[str, dict[str, bool]] = {}
_OPENROUTER_CAPABILITY_LOCK = threading.Lock()


def remember_model_capability(item: dict[str, Any]) -> None:
    """Remember non-secret OpenRouter response-format capability facts."""
    model_id = str((item or {}).get("id") or "").strip()
    if not model_id:
        return
    supported = {
        str(value or "").strip().lower()
        for value in ((item or {}).get("supported_parameters") or [])
        if str(value or "").strip()
    }
    strict = bool(
        (item or {}).get("strict_json_schema")
        or supported.intersection({"structured_outputs", "json_schema"})
    )
    json_mode = bool(
        strict
        or (item or {}).get("json_mode")
        or "response_format" in supported
    )
    with _OPENROUTER_CAPABILITY_LOCK:
        _OPENROUTER_MODEL_CAPABILITIES[model_id] = {
            "strict_json_schema": strict,
            "json_mode": json_mode,
        }


def _openrouter_structured_mode(model: str) -> str:
    with _OPENROUTER_CAPABILITY_LOCK:
        info = dict(_OPENROUTER_MODEL_CAPABILITIES.get(str(model or "").strip()) or {})
    if not info:
        return "strict"
    if info.get("strict_json_schema"):
        return "strict"
    if info.get("json_mode"):
        return "json"
    return "none"


def _reset_pooled_http_client() -> None:
    global _HTTP_CLIENT
    with _HTTP_CLIENT_LOCK:
        current = _HTTP_CLIENT
        _HTTP_CLIENT = None
        if current is not None:
            try:
                current.close()
            except Exception:
                pass


def _pooled_http_client() -> httpx.Client:
    """Return one keep-alive pool for AI traffic; auth stays per request."""
    global _HTTP_CLIENT
    with _HTTP_CLIENT_LOCK:
        if _HTTP_CLIENT is None or _HTTP_CLIENT.is_closed:
            limits = httpx.Limits(
                max_connections=20,
                max_keepalive_connections=10,
                keepalive_expiry=60.0,
            )
            transport = httpx.HTTPTransport(retries=1, limits=limits)
            _HTTP_CLIENT = httpx.Client(
                transport=transport,
                limits=limits,
                follow_redirects=True,
                timeout=httpx.Timeout(
                    connect=8.0,
                    read=120.0,
                    write=30.0,
                    pool=8.0,
                ),
            )
        return _HTTP_CLIENT


def _extract_request_id(headers) -> str:
    if headers is None:
        return ""
    for key in ("x-request-id", "x-openrouter-generation-id", "x-requestid"):
        try:
            value = headers.get(key)
        except Exception:
            value = ""
        if value:
            return str(value)
    return ""


def _usage_cost(data: dict[str, Any]) -> tuple[dict[str, Any], float | None]:
    usage = data.get("usage") or {}
    if not isinstance(usage, dict):
        usage = {}
    raw_cost = usage.get("cost")
    try:
        cost = float(raw_cost) if raw_cost is not None else None
    except Exception:
        cost = None
    return usage, cost


def _json_request(
    url: str,
    key: str,
    *,
    payload: dict[str, Any] | None = None,
    method: str = "GET",
    timeout: int = 120,
    provider: str = "",
    model: str = "",
    operation: str = "",
    product_id: int | None = None,
) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {key.strip()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "3DPrintHub-Catalog-Intelligence/8.9.9",
    }
    if provider == "openrouter":
        headers["HTTP-Referer"] = "https://3dprinthub.ir"
        headers["X-OpenRouter-Title"] = "3DPrintHub Catalog Center"

    body = (
        json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if payload is not None
        else None
    )
    started = time.perf_counter()
    connect_timeout = min(
        20.0 if provider == "openrouter" else 10.0,
        float(timeout),
    )
    response = None
    last_connect_error: httpx.RequestError | None = None

    for attempt in range(1, 3):
        try:
            response = _pooled_http_client().request(
                method,
                url,
                headers=headers,
                content=body,
                timeout=httpx.Timeout(
                    connect=connect_timeout,
                    read=float(timeout),
                    write=min(30.0, float(timeout)),
                    pool=min(10.0, float(timeout)),
                ),
            )
            break
        except (httpx.ConnectTimeout, httpx.ConnectError) as exc:
            last_connect_error = exc
            if attempt >= 2:
                break
            _reset_pooled_http_client()
            time.sleep(0.65)
        except httpx.RequestError as exc:
            ai_request_event(
                provider=provider,
                model=model,
                operation=operation or method.lower(),
                endpoint=url,
                status="error",
                duration_ms=int((time.perf_counter() - started) * 1000),
                product_id=product_id,
                error_text=str(exc),
            )
            raise RuntimeError(f"AI connection error: {exc}") from exc

    if response is None:
        exc = last_connect_error or httpx.ConnectError(
            "connection failed before an HTTP response"
        )
        ai_request_event(
            provider=provider,
            model=model,
            operation=operation or method.lower(),
            endpoint=url,
            status="error",
            duration_ms=int((time.perf_counter() - started) * 1000),
            product_id=product_id,
            error_text=str(exc),
            request_summary={"method": method, "connect_attempts": 2},
        )
        raise RuntimeError(
            "AI connection timeout/error after 2 bounded TLS/connect attempts: "
            f"{exc}"
        ) from exc

    raw = response.text
    request_id = _extract_request_id(response.headers)
    if response.status_code >= 400:
        ai_request_event(
            provider=provider,
            model=model,
            operation=operation or method.lower(),
            endpoint=url,
            request_id=request_id,
            http_status=int(response.status_code),
            status="error",
            duration_ms=int((time.perf_counter() - started) * 1000),
            product_id=product_id,
            request_summary={
                "method": method,
                "payload_keys": sorted((payload or {}).keys()),
            },
            error_text=raw,
        )
        raise RuntimeError(f"AI HTTP {response.status_code}: {raw[:1600]}")

    try:
        data = response.json() if raw.strip() else {}
    except Exception as exc:
        raise RuntimeError(
            f"AI HTTP {response.status_code} returned invalid JSON: {raw[:800]}"
        ) from exc

    usage, cost_usd = _usage_cost(data)
    ai_request_event(
        provider=provider,
        model=model or str(data.get("model") or ""),
        operation=operation or method.lower(),
        endpoint=url,
        request_id=request_id,
        http_status=int(response.status_code),
        status="ok",
        duration_ms=int((time.perf_counter() - started) * 1000),
        usage=usage,
        cost_usd=cost_usd,
        cost_source="provider_response" if cost_usd is not None else "",
        product_id=product_id,
        request_summary={
            "method": method,
            "payload_keys": sorted((payload or {}).keys()),
        },
        response_summary={
            "id": data.get("id"),
            "model": data.get("model"),
            "usage": usage,
        },
    )
    if request_id and isinstance(data, dict):
        data.setdefault("_request_id", request_id)
    return data


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
        if isinstance(content, list):
            return "\n".join(str(item.get("text") or "") for item in content if isinstance(item, dict)).strip()
    return ""


def _strip_json_fence(text: str) -> str:
    value = (text or "").strip()
    if value.startswith("```"):
        lines = value.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        value = "\n".join(lines).strip()
    return value


def _schema_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def _validate_schema_value(value: Any, schema: dict[str, Any], path: str = "$") -> None:
    if not isinstance(schema, dict):
        return
    if "anyOf" in schema:
        for branch in schema.get("anyOf") or []:
            try:
                _validate_schema_value(value, branch, path)
                return
            except RuntimeError:
                pass
        raise RuntimeError(f"Structured JSON schema mismatch at {path}: anyOf failed")
    if "oneOf" in schema:
        matched = 0
        for branch in schema.get("oneOf") or []:
            try:
                _validate_schema_value(value, branch, path)
                matched += 1
            except RuntimeError:
                pass
        if matched != 1:
            raise RuntimeError(f"Structured JSON schema mismatch at {path}: oneOf failed")
        return

    expected = schema.get("type")
    expected_types = [expected] if isinstance(expected, str) else list(expected or [])
    if expected_types and not any(
        _schema_type_matches(value, str(item))
        for item in expected_types
    ):
        raise RuntimeError(
            f"Structured JSON schema mismatch at {path}: "
            f"expected {expected_types}, got {type(value).__name__}"
        )

    if "enum" in schema and value not in (schema.get("enum") or []):
        raise RuntimeError(f"Structured JSON schema mismatch at {path}: enum")

    if isinstance(value, dict):
        properties = schema.get("properties") or {}
        required = schema.get("required") or []
        missing = [key for key in required if key not in value]
        if missing:
            raise RuntimeError(
                f"Structured JSON schema mismatch at {path}: "
                f"missing {', '.join(str(x) for x in missing)}"
            )
        if schema.get("additionalProperties") is False:
            extra = [key for key in value if key not in properties]
            if extra:
                raise RuntimeError(
                    f"Structured JSON schema mismatch at {path}: "
                    f"unexpected {', '.join(str(x) for x in extra)}"
                )
        for key, child in properties.items():
            if key in value:
                _validate_schema_value(value[key], child, f"{path}.{key}")

    if isinstance(value, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate_schema_value(item, item_schema, f"{path}[{index}]")


class AIProviderClient:
    def __init__(self, provider: str, api_key: str, model: str = "", product_id: int | None = None):
        self.provider = provider if provider in PROVIDERS else "openai"
        self.spec = PROVIDERS[self.provider]
        self.api_key = (api_key or "").strip()
        self.model = (model or "").strip()
        self.product_id = product_id
        if not self.api_key:
            raise RuntimeError(f"{self.spec.label} API key is not configured.")

    def list_model_info(self) -> list[dict[str, Any]]:
        data = _json_request(
            f"{self.spec.base_url}/models",
            self.api_key,
            timeout=20,
            provider=self.provider,
            operation="list_models",
            product_id=self.product_id,
        )
        output = []
        for item in data.get("data", []):
            if not isinstance(item, dict) or not item.get("id"):
                continue
            pricing = item.get("pricing") if isinstance(item.get("pricing"), dict) else {}
            model_id = str(item.get("id"))
            free = model_id.endswith(":free") or model_id == "openrouter/free"
            if pricing:
                numeric = []
                for key in ("prompt", "completion", "request"):
                    try:
                        numeric.append(float(pricing.get(key) or 0))
                    except Exception:
                        pass
                free = free or (numeric and max(numeric) == 0)
            model_info = {
                "id": model_id,
                "name": str(item.get("name") or model_id),
                "pricing": pricing,
                "supported_parameters": list(item.get("supported_parameters") or []),
                "context_length": item.get("context_length"),
                "description": str(item.get("description") or ""),
                "architecture": item.get("architecture") if isinstance(item.get("architecture"), dict) else {},
                "top_provider": item.get("top_provider") if isinstance(item.get("top_provider"), dict) else {},
                "created": item.get("created"),
                "free": bool(free),
            }
            output.append(model_info)
            if self.provider == "openrouter":
                remember_model_capability(model_info)
        if self.provider == "openrouter" and not any(x["id"] == "openrouter/free" for x in output):
            output.insert(0, {"id": "openrouter/free", "name": "OpenRouter Free Models Router", "pricing": {"prompt": "0", "completion": "0"}, "supported_parameters": [], "context_length": None, "free": True})
        return output

    def list_models(self) -> list[str]:
        return [item["id"] for item in self.list_model_info()]

    def choose_model(
        self,
        preferred: str = "",
        *,
        model_info: list[dict[str, Any]] | None = None,
    ) -> str:
        preferred = (preferred or self.model or "").strip()
        if preferred:
            return preferred
        info = model_info if model_info is not None else self.list_model_info()
        models = [item["id"] for item in info]
        if self.provider == "openrouter":
            if "openrouter/free" in models:
                return "openrouter/free"
            free = next((item["id"] for item in info if item.get("free")), "")
            if free:
                return free
        priorities = ["gpt-5.4-mini", "gpt-5-mini", "gpt-5.4", "gpt-5"]
        for candidate in priorities:
            if candidate in models:
                return candidate
        textish = [
            m for m in models
            if not str(m).casefold().endswith(":batch")
            and not any(
                t in m.lower()
                for t in ("image", "audio", "embedding", "tts", "whisper", "moderation")
            )
        ]
        if textish:
            return textish[0]
        if models:
            return models[0]
        raise RuntimeError(f"No accessible models were returned by {self.spec.label}.")

    def _chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        *,
        response_format: dict[str, Any] | None = None,
        operation: str = "chat",
        require_parameters: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"model": model, "messages": messages}
        if self.provider == "openrouter":
            latency_first = operation in {
                "connection_test",
                "structured_content",
                "structured_content_compat",
                "screenshot_fact_extract",
            }
            provider_options: dict[str, Any] = {
                "sort": "latency" if latency_first else "throughput",
                "allow_fallbacks": True,
            }
            if require_parameters or response_format is not None:
                provider_options["require_parameters"] = True
            payload["provider"] = provider_options
        if response_format is not None:
            payload["response_format"] = response_format
        return _json_request(
            f"{self.spec.base_url}/chat/completions",
            self.api_key,
            payload=payload,
            method="POST",
            timeout=210,
            provider=self.provider,
            model=model,
            operation=operation,
            product_id=self.product_id,
        )

    def test_connection(self, preferred: str = "") -> dict[str, Any]:
        requested = (preferred or self.model or "").strip()
        info: list[dict[str, Any]] = []
        if requested:
            model = requested
        else:
            info = self.list_model_info()
            model = self.choose_model(model_info=info)

        if self.spec.chat_first:
            data = self._chat(
                model,
                [{"role": "user", "content": "Return only the Persian word: آماده"}],
                operation="connection_test",
            )
        else:
            payload = {
                "model": model,
                "input": "Return only the Persian word: آماده",
                "max_output_tokens": 20,
            }
            data = _json_request(
                f"{self.spec.base_url}/responses",
                self.api_key,
                payload=payload,
                method="POST",
                timeout=60,
                provider=self.provider,
                model=model,
                operation="connection_test",
                product_id=self.product_id,
            )
        text = response_output_text(data)
        if not text:
            raise RuntimeError(
                f"{self.spec.label} connected, but the live response test returned no text."
            )
        selected_info = next((item for item in info if item["id"] == model), {})
        inferred_free = model.endswith(":free") or model == "openrouter/free"
        return {
            "provider": self.provider,
            "provider_label": self.spec.label,
            "model": model,
            "models_count": len(info),
            "model_catalog_checked": bool(info),
            "sample": text[:120],
            "free": bool(selected_info.get("free")) or inferred_free,
            "pricing": selected_info.get("pricing") or {},
            "request_id": data.get("_request_id") or data.get("id") or "",
            "usage": data.get("usage") or {},
        }

    def balance_info(self, *, management_key: str = "", admin_key: str = "") -> dict[str, Any]:
        if self.provider == "avalai":
            data = _json_request(
                "https://api.avalai.ir/user/v1/credit",
                self.api_key,
                timeout=45,
                provider=self.provider,
                operation="balance",
            )
            return {
                "available": True,
                "remaining_irt": float(data.get("remaining_irt") or 0),
                "remaining_usd": float(data.get("remaining_unit") or 0),
                "exchange_rate": float(data.get("exchange_rate") or 0),
                "account_tier": data.get("account_tier"),
                "raw": data,
            }
        if self.provider == "openrouter":
            key = (management_key or "").strip()
            if not key:
                return {"available": False, "reason": "برای مانده اعتبار OpenRouter یک Management Key لازم است."}
            data = _json_request(
                "https://openrouter.ai/api/v1/credits",
                key,
                timeout=45,
                provider=self.provider,
                operation="balance",
            )
            credits = data.get("data") or {}
            total = float(credits.get("total_credits") or 0)
            used = float(credits.get("total_usage") or 0)
            return {"available": True, "total_credits": total, "total_usage": used, "remaining_usd": max(0.0, total - used), "raw": data}
        if self.provider == "openai":
            if not (admin_key or "").strip():
                return {"available": False, "reason": "OpenAI مانده‌اعتبار مستقیم را در پاسخ API Key عادی ارائه نمی‌کند؛ Admin Key اختیاری فقط برای گزارش هزینه سازمانی است."}
            now = int(time.time())
            start = now - 30 * 86400
            query = parse.urlencode({"start_time": start, "end_time": now, "limit": 31})
            data = _json_request(
                f"https://api.openai.com/v1/organization/costs?{query}",
                admin_key,
                timeout=45,
                provider=self.provider,
                operation="organization_costs",
            )
            total = 0.0
            for bucket in data.get("data") or []:
                for item in (bucket.get("results") or []) if isinstance(bucket, dict) else []:
                    try:
                        total += float((item.get("amount") or {}).get("value") or 0)
                    except Exception:
                        pass
            return {"available": True, "spend_30d_usd": total, "note": "هزینه ۳۰ روز اخیر؛ این عدد مانده اعتبار نیست.", "raw": data}
        return {"available": False, "reason": "Provider balance adapter is not implemented."}

    def lookup_avalai_cost(self, request_id: str) -> dict[str, Any]:
        if self.provider != "avalai" or not str(request_id or "").strip():
            return {}
        data = _json_request(
            "https://api.avalai.ir/user/v1/transactions/lookup",
            self.api_key,
            payload={"transaction_ids": [str(request_id)]},
            method="POST",
            timeout=45,
            provider=self.provider,
            operation="cost_lookup",
        )
        txs = data.get("transactions") or []
        return txs[0] if txs and isinstance(txs[0], dict) else {}

    def structured_response(self, *, instructions: str, input_content: list[dict[str, Any]], schema: dict[str, Any], schema_name: str, preferred_model: str = "") -> tuple[dict[str, Any], str]:
        model = self.choose_model(preferred_model)
        if self.provider == "openai":
            payload = {
                "model": model,
                "instructions": instructions,
                "input": [{"role": "user", "content": input_content}],
                "text": {"format": {"type": "json_schema", "name": schema_name, "schema": schema, "strict": True}},
            }
            data = _json_request(
                f"{self.spec.base_url}/responses",
                self.api_key,
                payload=payload,
                method="POST",
                timeout=210,
                provider=self.provider,
                model=model,
                operation="structured_content",
                product_id=self.product_id,
            )
            text = response_output_text(data)
        else:
            user_payload = json.dumps(input_content, ensure_ascii=False)
            messages = [
                {
                    "role": "system",
                    "content": (
                        instructions
                        + " Return exactly one valid JSON object matching the requested schema. "
                        "Do not use Markdown fences."
                    ),
                },
                {"role": "user", "content": user_payload},
            ]
            if self.provider == "openrouter":
                structured_mode = _openrouter_structured_mode(model)
                if structured_mode == "none":
                    raise RuntimeError(
                        f"{self.spec.label} model {model} does not expose "
                        "response_format JSON capability for Product work."
                    )
                if structured_mode == "strict":
                    response_format = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": schema_name,
                            "strict": True,
                            "schema": schema,
                        },
                    }
                    operation = "structured_content"
                else:
                    response_format = {"type": "json_object"}
                    operation = "structured_content_json_mode"
                try:
                    data = self._chat(
                        model,
                        messages,
                        response_format=response_format,
                        operation=operation,
                        require_parameters=True,
                    )
                except RuntimeError as exc:
                    folded = str(exc).casefold()
                    if any(
                        token in folded
                        for token in (
                            "response_format",
                            "json_schema",
                            "unsupported",
                            "no endpoints found",
                            "require_parameters",
                            "parameter",
                            "400",
                            "404",
                        )
                    ):
                        capability = (
                            "strict JSON Schema"
                            if structured_mode == "strict"
                            else "JSON response_format"
                        )
                        raise RuntimeError(
                            f"{self.spec.label} model {model} has no currently "
                            f"routable endpoint for {capability}. Reload the live "
                            "model list or choose another Product-capable endpoint/model."
                        ) from exc
                    raise
            else:
                try:
                    data = self._chat(
                        model,
                        messages,
                        response_format={"type": "json_object"},
                        operation="structured_content",
                    )
                except RuntimeError as exc:
                    # AvalAI/other OpenAI-compatible gateways can expose models
                    # that reject response_format. Keep the mature compatibility
                    # fallback outside OpenRouter, where the model catalogue gives
                    # us an explicit structured-output capability signal.
                    if not any(
                        token in str(exc).lower()
                        for token in (
                            "400",
                            "invalid_request",
                            "unsupported",
                            "response_format",
                            "parameter",
                        )
                    ):
                        raise
                    data = self._chat(
                        model,
                        messages,
                        response_format=None,
                        operation="structured_content_compat",
                    )
            text = response_output_text(data)
        if not text:
            raise RuntimeError(f"{self.spec.label} returned no output text.")
        text = _strip_json_fence(text)
        try:
            result = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"{self.spec.label} model {model} returned invalid JSON for a "
                f"Structured Product request: {text[:700]}"
            ) from exc
        if not isinstance(result, dict):
            raise RuntimeError(f"{self.spec.label} returned JSON, but the root value is not an object.")
        _validate_schema_value(result, schema)
        return result, model
