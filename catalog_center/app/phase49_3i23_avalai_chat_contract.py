from __future__ import annotations

import json
from typing import Any

from . import ai_providers
from .phase49_diagnostics import audit_event


PHASE = "49.3I.24"

_NON_TEXT_MODEL_TOKENS = (
    "lyria",
    "music",
    "imagegen",
    "image-generation",
    "text-to-image",
    "tts",
    "whisper",
    "embedding",
    "moderation",
    "video-generation",
)


def _clean_model(value: str) -> str:
    model = str(value or "").strip()
    return model.replace("models/", "", 1) if model.startswith("models/") else model


def product_text_model_reason(model: str) -> str:
    """Reject obviously non-text models without a hidden /models request."""
    value = _clean_model(model).lower()
    token = next((item for item in _NON_TEXT_MODEL_TOKENS if item in value), "")
    if token:
        return f"مدل «{model}» برای تولید متن ساختاریافته محصول مناسب نیست ({token}). یک مدل متنی/Reasoning انتخاب کن."
    return ""


def _plain_input_text(input_content: list[dict[str, Any]]) -> str:
    """Convert Responses-style content into deterministic extracted source text."""
    parts: list[str] = []
    for item in input_content or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("type") or "") != "input_text":
            continue
        text = str(item.get("text") or "").strip()
        if text:
            parts.append(text)
    return "\n\n".join(parts).strip()


def _unsupported_format_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(
        token in text
        for token in (
            "400",
            "invalid_request",
            "unsupported",
            "response_format",
            "json_schema",
            "parameter",
        )
    )


def install() -> None:
    """Use AvalAI's documented Chat Completions structured-output contract.

    Product requests use the exact operator-saved model and do not perform a
    hidden GET /models. We prefer json_schema, fall back to json_object for
    routes that do not support strict schemas, and finally fall back to
    prompt-enforced JSON when response_format itself is unsupported.
    """
    Client = ai_providers.AIProviderClient
    if getattr(Client, "_phase49_3i24_avalai_structured_contract", False):
        return

    original = Client.structured_response

    def structured_response(
        self,
        *,
        instructions: str,
        input_content: list[dict[str, Any]],
        schema: dict[str, Any],
        schema_name: str,
        preferred_model: str = "",
    ) -> tuple[dict[str, Any], str]:
        if self.provider != "avalai" or self.product_id is None:
            return original(
                self,
                instructions=instructions,
                input_content=input_content,
                schema=schema,
                schema_name=schema_name,
                preferred_model=preferred_model,
            )

        model = _clean_model(preferred_model or self.model)
        if not model:
            raise RuntimeError("برای AvalAI یک Model فعال و ذخیره‌شده انتخاب نشده است.")
        rejection = product_text_model_reason(model)
        if rejection:
            raise RuntimeError(rejection)

        product_payload = _plain_input_text(input_content)
        if not product_payload:
            raise RuntimeError("AvalAI product request has no extracted source text payload.")

        schema_json = json.dumps(schema or {}, ensure_ascii=False, separators=(",", ":"))
        system_text = (
            str(instructions or "").strip()
            + "\n\nOUTPUT CONTRACT: Return exactly one valid JSON object. "
            + "Do not use Markdown fences. Do not add commentary before or after JSON. "
            + f"The object must match schema '{schema_name}'."
        ).strip()
        user_text = (
            "PRODUCT_SOURCE_AND_OPERATOR_DATA:\n"
            + product_payload
            + "\n\nUse only the extracted source/operator facts above. "
            + "A URL by itself is not evidence that you browsed the page. Missing facts must not be invented."
        )
        messages = [
            {"role": "system", "content": system_text},
            {"role": "user", "content": user_text},
        ]

        audit_event(
            "ai",
            "avalai_exact_structured_contract",
            status="running",
            product_id=self.product_id,
            source_file=__file__,
            message=f"AvalAI structured product request prepared; model={model}",
            detail={
                "provider": "avalai",
                "model": model,
                "schema_name": schema_name,
                "schema_chars": len(schema_json),
                "source_chars": len(product_payload),
                "hidden_model_list_request": False,
                "source_strategy": "app_fetch_sanitize_then_prompt",
            },
        )

        strict_format = {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": schema,
            },
        }
        try:
            data = self._chat(
                model,
                messages,
                response_format=strict_format,
                operation="structured_content_avalai_json_schema",
            )
        except RuntimeError as strict_exc:
            if not _unsupported_format_error(strict_exc):
                raise
            audit_event(
                "ai",
                "avalai_json_schema_fallback",
                status="fallback",
                product_id=self.product_id,
                source_file=__file__,
                message=str(strict_exc)[:700],
                detail={"provider": "avalai", "model": model, "next": "json_object"},
            )
            try:
                data = self._chat(
                    model,
                    messages,
                    response_format={"type": "json_object"},
                    operation="structured_content_avalai_json_object",
                )
            except RuntimeError as json_exc:
                if not _unsupported_format_error(json_exc):
                    raise
                audit_event(
                    "ai",
                    "avalai_json_object_fallback",
                    status="fallback",
                    product_id=self.product_id,
                    source_file=__file__,
                    message=str(json_exc)[:700],
                    detail={"provider": "avalai", "model": model, "next": "prompt_json"},
                )
                messages[0]["content"] += "\nJSON_SCHEMA:\n" + schema_json
                data = self._chat(
                    model,
                    messages,
                    response_format=None,
                    operation="structured_content_avalai_prompt_json",
                )

        output = ai_providers.response_output_text(data)
        if not output:
            raise RuntimeError("AvalAI returned no output text.")
        output = ai_providers._strip_json_fence(output)
        try:
            result = json.loads(output)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"AvalAI returned invalid JSON: {output[:700]}") from exc
        if not isinstance(result, dict):
            raise RuntimeError("AvalAI returned JSON, but the root value is not an object.")
        return result, model

    Client.structured_response = structured_response
    Client._phase49_3i24_avalai_structured_contract = True
    Client._phase49_3i23_avalai_chat_contract = True
