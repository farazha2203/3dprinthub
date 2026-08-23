from __future__ import annotations

import json
import time
from typing import Any

from . import ai_providers
from .ai_providers import AIProviderClient


MODEL_INFO_CACHE_SECONDS = 120
MODEL_TRACE_SAMPLE_LIMIT = 24
SCHEMA_ERROR_LIMIT = 24
BUSY_FLAGS = (
    "_phase49_3e_busy",
    "_ai_busy",
    "_phase49_3f_source_busy",
    "_phase49_3i_ai_starting",
)


def _copy_model_info(items) -> list[dict[str, Any]]:
    return [dict(item) for item in (items or []) if isinstance(item, dict)]


def _schema_errors(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Return concise JSON-schema contract errors for the subset used by Catalog AI.

    This is intentionally small and dependency-free. It validates the contract
    features used by the repository schemas: type, required, additionalProperties,
    object properties, arrays/items, maxItems and numeric minimum/maximum.
    """
    errors: list[str] = []

    def add(message: str) -> None:
        if len(errors) < SCHEMA_ERROR_LIMIT:
            errors.append(message)

    def walk(current: Any, current_schema: dict[str, Any], current_path: str) -> None:
        if len(errors) >= SCHEMA_ERROR_LIMIT:
            return
        expected = current_schema.get("type")
        type_ok = True
        if expected == "object":
            type_ok = isinstance(current, dict)
        elif expected == "array":
            type_ok = isinstance(current, list)
        elif expected == "string":
            type_ok = isinstance(current, str)
        elif expected == "boolean":
            type_ok = isinstance(current, bool)
        elif expected == "integer":
            type_ok = isinstance(current, int) and not isinstance(current, bool)
        elif expected == "number":
            type_ok = isinstance(current, (int, float)) and not isinstance(current, bool)

        if not type_ok:
            add(f"{current_path}: expected {expected}, got {type(current).__name__}")
            return

        if expected == "object":
            properties = current_schema.get("properties") or {}
            required = list(current_schema.get("required") or [])
            for key in required:
                if key not in current:
                    add(f"{current_path}.{key}: missing required key")
            if current_schema.get("additionalProperties") is False:
                for key in current:
                    if key not in properties:
                        add(f"{current_path}.{key}: unexpected key")
            for key, child_schema in properties.items():
                if key in current and isinstance(child_schema, dict):
                    walk(current[key], child_schema, f"{current_path}.{key}")
            return

        if expected == "array":
            maximum = current_schema.get("maxItems")
            if maximum is not None and len(current) > int(maximum):
                add(f"{current_path}: has {len(current)} items, maxItems={maximum}")
            item_schema = current_schema.get("items")
            if isinstance(item_schema, dict):
                for index, item in enumerate(current):
                    walk(item, item_schema, f"{current_path}[{index}]")
            return

        if expected in {"number", "integer"}:
            minimum = current_schema.get("minimum")
            maximum = current_schema.get("maximum")
            if minimum is not None and current < minimum:
                add(f"{current_path}: {current} < minimum {minimum}")
            if maximum is not None and current > maximum:
                add(f"{current_path}: {current} > maximum {maximum}")

    walk(value, schema or {}, path)
    return errors


def _parse_json_object(data: dict[str, Any], provider_label: str) -> dict[str, Any]:
    text = ai_providers.response_output_text(data)
    if not text:
        raise RuntimeError(f"{provider_label} returned no output text.")
    text = ai_providers._strip_json_fence(text)
    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{provider_label} returned invalid JSON: {text[:900]}") from exc
    if not isinstance(result, dict):
        raise RuntimeError(f"{provider_label} returned JSON, but the root value is not an object.")
    return result


def _response_format_retryable(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(
        token in text
        for token in (
            "400",
            "422",
            "invalid_request",
            "unsupported",
            "response_format",
            "json_schema",
            "schema",
            "parameter",
        )
    )


def _strict_response_format(schema_name: str, schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": str(schema_name or "catalog_schema")[:64],
            "strict": True,
            "schema": schema,
        },
    }


def _schema_instruction(instructions: str, schema_name: str, schema: dict[str, Any]) -> str:
    schema_text = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    return (
        str(instructions or "").strip()
        + "\n\nSTRICT OUTPUT CONTRACT:\n"
        + f"Schema name: {schema_name}\n"
        + "Return exactly one JSON object matching this schema. Every required key must exist. "
        + "Use the exact property names from the schema; do not rename fields, add aliases, "
        + "or add properties when additionalProperties is false. Arrays/objects must use the exact required types.\n"
        + "JSON Schema:\n"
        + schema_text
        + "\nDo not use Markdown fences or explanatory text outside the JSON object."
    )


def _chat_with_schema(
    client: AIProviderClient,
    *,
    model: str,
    messages: list[dict[str, Any]],
    schema_name: str,
    schema: dict[str, Any],
    operation: str,
) -> dict[str, Any]:
    strict_format = _strict_response_format(schema_name, schema)
    try:
        return client._chat(
            model,
            messages,
            response_format=strict_format,
            operation=operation,
        )
    except RuntimeError as strict_exc:
        if not _response_format_retryable(strict_exc):
            raise
    try:
        return client._chat(
            model,
            messages,
            response_format={"type": "json_object"},
            operation=operation + "_json_object",
        )
    except RuntimeError as json_exc:
        if not _response_format_retryable(json_exc):
            raise
    return client._chat(
        model,
        messages,
        response_format=None,
        operation=operation + "_compat",
    )


def _structured_compatible_response(
    client: AIProviderClient,
    *,
    instructions: str,
    input_content: list[dict[str, Any]],
    schema: dict[str, Any],
    schema_name: str,
    preferred_model: str = "",
) -> tuple[dict[str, Any], str]:
    model = client.choose_model(preferred_model)
    system = _schema_instruction(instructions, schema_name, schema)
    user_payload = json.dumps(input_content, ensure_ascii=False, default=str)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_payload},
    ]
    data = _chat_with_schema(
        client,
        model=model,
        messages=messages,
        schema_name=schema_name,
        schema=schema,
        operation="structured_content",
    )
    result = _parse_json_object(data, client.spec.label)
    errors = _schema_errors(result, schema)
    if not errors:
        return result, model

    repair_payload = {
        "input": input_content,
        "previous_invalid_output": result,
        "schema_validation_errors": errors,
    }
    repair_messages = [
        {
            "role": "system",
            "content": system
            + "\n\nThe previous JSON did not match the schema. Repair it now. "
            + "Do not preserve wrong aliases. Do not omit required fields. "
            + "Return only the corrected JSON object.",
        },
        {"role": "user", "content": json.dumps(repair_payload, ensure_ascii=False, default=str)},
    ]
    repair = _chat_with_schema(
        client,
        model=model,
        messages=repair_messages,
        schema_name=schema_name,
        schema=schema,
        operation="structured_content_repair",
    )
    repaired = _parse_json_object(repair, client.spec.label)
    repair_errors = _schema_errors(repaired, schema)
    if repair_errors:
        summary = "; ".join(repair_errors[:10])
        raise RuntimeError(
            f"{client.spec.label} returned JSON but it still does not match the required schema after one repair attempt: {summary}"
        )
    return repaired, model


def _compact_model_response(response: Any) -> Any:
    if not isinstance(response, dict):
        return response
    rows = response.get("data")
    if not isinstance(rows, list):
        rows = response.get("models")
    if not isinstance(rows, list):
        return response
    models = []
    for item in rows[:MODEL_TRACE_SAMPLE_LIMIT]:
        if not isinstance(item, dict):
            continue
        raw_name = str(item.get("id") or item.get("name") or "")
        models.append(
            {
                "id": raw_name,
                "name": str(item.get("displayName") or item.get("name") or raw_name),
                "owned_by": str(item.get("owned_by") or ""),
                "mode": str(item.get("mode") or ""),
                "supports_response_schema": bool(item.get("supports_response_schema")),
                "supported_endpoints": list(item.get("supported_endpoints") or [])[:8],
            }
        )
    return {
        "object": response.get("object") or "model_list",
        "models_count": len(rows),
        "models_sample": models,
        "truncated": len(rows) > len(models),
        "note": "Model catalog is summarized in the UI to keep Tk responsive; content requests/responses remain visible in detail.",
    }


def _release_busy_state(parent) -> None:
    if parent is None:
        return
    for attr in BUSY_FLAGS:
        if hasattr(parent, attr):
            try:
                setattr(parent, attr, False)
            except Exception:
                pass


def install(workspace_class, phase49_3f_workspace_module, trace_module) -> None:
    """Install 49.3I.11 schema/trace/busy recovery after 49.3I.10.

    Requested delta:
    - providers must receive the actual schema, not only a json_object hint;
    - malformed provider JSON gets one visible repair attempt then a precise error;
    - model-catalog trace cannot flood Tk and look like a hang;
    - Stop Waiting/watchdog immediately releases Product Workspace busy state;
    - explicit operator model selection is used directly for the current request.
    """
    if getattr(workspace_class, "_phase49_3i11_schema_runtime_recovery_installed", False):
        return

    original_list_model_info = AIProviderClient.list_model_info
    original_choose_model = AIProviderClient.choose_model
    original_probe_connection = getattr(AIProviderClient, "probe_connection", None)
    original_structured_response = AIProviderClient.structured_response

    def list_model_info(self):
        cached = getattr(self, "_phase49_3i11_model_info_cache", None)
        if isinstance(cached, tuple) and len(cached) == 2:
            stamp, items = cached
            try:
                if time.monotonic() - float(stamp) <= MODEL_INFO_CACHE_SECONDS:
                    return _copy_model_info(items)
            except Exception:
                pass
        items = original_list_model_info(self)
        copied = _copy_model_info(items)
        self._phase49_3i11_model_info_cache = (time.monotonic(), copied)
        return _copy_model_info(copied)

    def choose_model(self, preferred: str = ""):
        explicit = str(preferred or self.model or "").strip()
        if explicit:
            return explicit
        return original_choose_model(self, preferred)

    def probe_connection(self, timeout=30):
        # A models request is already the existing credential/network probe. Use
        # the cached mature adapter so the same operation does not download the
        # provider model catalog twice before one content request.
        info = self.list_model_info()
        return {
            "provider": self.provider,
            "models_count": len(info),
            "connected": True,
            "cached_for_request": True,
        }

    def structured_response(
        self,
        *,
        instructions,
        input_content,
        schema,
        schema_name,
        preferred_model="",
    ):
        if self.provider in {"avalai", "openrouter"}:
            return _structured_compatible_response(
                self,
                instructions=instructions,
                input_content=input_content,
                schema=schema,
                schema_name=schema_name,
                preferred_model=preferred_model,
            )

        result, model = original_structured_response(
            self,
            instructions=instructions,
            input_content=input_content,
            schema=schema,
            schema_name=schema_name,
            preferred_model=preferred_model,
        )
        errors = _schema_errors(result, schema)
        if errors:
            summary = "; ".join(errors[:10])
            raise RuntimeError(
                f"{self.spec.label} returned JSON that does not match the required schema: {summary}"
            )
        return result, model

    AIProviderClient.list_model_info = list_model_info
    AIProviderClient.choose_model = choose_model
    if callable(original_probe_connection):
        AIProviderClient.probe_connection = probe_connection
    AIProviderClient.structured_response = structured_response

    original_trace_response = trace_module._trace_response

    def compact_trace_response(
        product_id,
        *,
        provider: str,
        model: str,
        operation: str,
        endpoint: str,
        response,
    ):
        traced_response = response
        if str(operation or "") in {"list_models", "connection_probe"} or str(endpoint or "").rstrip("/").endswith("/models"):
            traced_response = _compact_model_response(response)
        return original_trace_response(
            product_id,
            provider=provider,
            model=model,
            operation=operation,
            endpoint=endpoint,
            response=traced_response,
        )

    trace_module._trace_response = compact_trace_response

    ProgressClass = phase49_3f_workspace_module.AIProgress
    original_abort = getattr(ProgressClass, "_phase49_3i8_abort", None)
    if callable(original_abort):
        def _phase49_3i8_abort(self, message: str, *, reason: str):
            _release_busy_state(getattr(self, "_phase49_3i8_parent", None) or getattr(self, "parent", None))
            return original_abort(self, message, reason=reason)

        ProgressClass._phase49_3i8_abort = _phase49_3i8_abort

    original_apply_full = getattr(workspace_class, "_phase49_3f_apply_full_ai", None)
    if callable(original_apply_full):
        def _phase49_3f_apply_full_ai(self, pack, scope, progress, provider, model, started):
            if getattr(progress, "_phase49_3i8_cancelled", False):
                _release_busy_state(self)
            return original_apply_full(self, pack, scope, progress, provider, model, started)

        workspace_class._phase49_3f_apply_full_ai = _phase49_3f_apply_full_ai

    original_apply_images = getattr(workspace_class, "_phase49_3f_apply_selected_image_ai", None)
    if callable(original_apply_images):
        def _phase49_3f_apply_selected_image_ai(self, pack, selected, progress, provider, model, started):
            if getattr(progress, "_phase49_3i8_cancelled", False):
                _release_busy_state(self)
            return original_apply_images(self, pack, selected, progress, provider, model, started)

        workspace_class._phase49_3f_apply_selected_image_ai = _phase49_3f_apply_selected_image_ai

    workspace_class._phase49_3i11_release_busy_state = _release_busy_state
    workspace_class._phase49_3i11_schema_runtime_recovery_installed = True
