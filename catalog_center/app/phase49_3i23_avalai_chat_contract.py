from __future__ import annotations

import json
from typing import Any

from . import ai_providers
from .phase49_diagnostics import audit_event


PHASE = "49.3I.23"


def _clean_model(value: str) -> str:
    model = str(value or "").strip()
    return model.replace("models/", "", 1) if model.startswith("models/") else model


def _plain_input_text(input_content: list[dict[str, Any]]) -> str:
    """Convert Responses-style content into the plain text Chat Completions needs.

    AvalAI's documented chat endpoint expects model + messages. Product content
    generation is source/link grounded, so image placeholders must not be serialized
    into the user message as fake JSON instructions.
    """
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


def install() -> None:
    """Use the operator-saved AvalAI model and a real Chat Completions prompt.

    Previous product requests re-ran model discovery, serialized Responses API
    content wrappers as a string, and told the model to match a schema that was
    never actually included in the chat prompt. That differs from AvalAI's
    documented model/messages contract and can make a request slow or unusable.
    """
    Client = ai_providers.AIProviderClient
    if getattr(Client, "_phase49_3i23_avalai_chat_contract", False):
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

        # Product AI has one explicit operator-saved model. Do not issue a hidden
        # GET /models before the real content request.
        model = _clean_model(preferred_model or self.model)
        if not model:
            return original(
                self,
                instructions=instructions,
                input_content=input_content,
                schema=schema,
                schema_name=schema_name,
                preferred_model=preferred_model,
            )

        product_payload = _plain_input_text(input_content)
        if not product_payload:
            raise RuntimeError("AvalAI product request has no text payload.")

        schema_json = json.dumps(schema or {}, ensure_ascii=False, separators=(",", ":"))
        system_text = (
            str(instructions or "").strip()
            + "\n\nOUTPUT CONTRACT: Return exactly one valid JSON object. "
            + "Do not use Markdown fences. Do not add commentary before or after JSON. "
            + f"The JSON object must match schema '{schema_name}'.\nJSON_SCHEMA:\n{schema_json}"
        ).strip()
        user_text = (
            "PRODUCT_SOURCE_AND_OPERATOR_DATA:\n"
            + product_payload
            + "\n\nUse only the source/operator facts above. Missing facts must not be invented."
        )
        messages = [
            {"role": "system", "content": system_text},
            {"role": "user", "content": user_text},
        ]

        audit_event(
            "ai",
            "avalai_exact_chat_contract",
            status="running",
            product_id=self.product_id,
            provider="avalai",
            model=model,
            source_file=__file__,
            message="AvalAI product request prepared with exact saved model and chat/completions contract",
            detail={
                "schema_name": str(schema_name or ""),
                "product_payload_chars": len(product_payload),
                "schema_chars": len(schema_json),
                "hidden_model_discovery": False,
                "serialized_image_placeholders": False,
            },
        )

        try:
            data = self._chat(
                model,
                messages,
                response_format={"type": "json_object"},
                operation="structured_content_avalai_exact",
            )
        except RuntimeError as exc:
            text = str(exc).lower()
            if not any(token in text for token in ("400", "invalid_request", "unsupported", "response_format", "parameter")):
                raise
            data = self._chat(
                model,
                messages,
                response_format=None,
                operation="structured_content_avalai_compat",
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
    Client._phase49_3i23_avalai_chat_contract = True
