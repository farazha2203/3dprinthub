from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from app.ai_providers import AIProviderClient
from app.phase49_3i23_avalai_chat_contract import (
    _avalai_url_tool_evidence,
    install,
    product_text_model_reason,
)


class Phase493I24AvalAIStructuredContractTests(unittest.TestCase):
    def setUp(self):
        install()

    def test_product_request_uses_saved_model_and_json_schema_without_model_scan(self):
        client = AIProviderClient("avalai", "dummy-key", "gpt-5-chat-latest", product_id=2896217)
        calls = []

        def forbidden_choose_model(_preferred=""):
            raise AssertionError("product-bound AvalAI request must not discover models")

        def fake_chat(model, messages, *, response_format=None, operation="chat"):
            calls.append((model, messages, response_format, operation))
            return {
                "choices": [
                    {"message": {"content": json.dumps({"title_fa": "استند کیک شیاردار"}, ensure_ascii=False)}}
                ]
            }

        client.choose_model = forbidden_choose_model
        client._chat = fake_chat
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {"title_fa": {"type": "string"}},
            "required": ["title_fa"],
        }
        with patch(
            "app.phase49_3i23_avalai_chat_contract._avalai_url_tool_evidence",
            return_value=("", "test_no_tool"),
        ):
            result, model = client.structured_response(
                instructions="Translate the exact product identity to Persian.",
                input_content=[
                    {"type": "input_text", "text": '{"source_title":"Ribbed cake stand, cookie platter","source_url":"https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter"}'},
                    {"type": "input_image", "image_url": "https://example.invalid/image.webp", "detail": "auto"},
                ],
                schema=schema,
                schema_name="catalog_test",
                preferred_model="gpt-5-chat-latest",
            )

        self.assertEqual(model, "gpt-5-chat-latest")
        self.assertEqual(result["title_fa"], "استند کیک شیاردار")
        self.assertEqual(len(calls), 1)
        sent_model, messages, response_format, operation = calls[0]
        self.assertEqual(sent_model, "gpt-5-chat-latest")
        self.assertEqual(response_format["type"], "json_schema")
        self.assertEqual(response_format["json_schema"]["name"], "catalog_test")
        self.assertTrue(response_format["json_schema"]["strict"])
        self.assertEqual(response_format["json_schema"]["schema"], schema)
        self.assertEqual(operation, "structured_content_avalai_json_schema")
        self.assertIn("Ribbed cake stand, cookie platter", messages[1]["content"])
        self.assertIn("makerworld.com/en/models/2896217", messages[1]["content"])
        self.assertNotIn("input_image", messages[1]["content"])
        self.assertNotIn("example.invalid", messages[1]["content"])

    def test_response_format_fallback_is_schema_then_json_object_then_prompt_json(self):
        client = AIProviderClient("avalai", "dummy-key", "gpt-5-chat-latest", product_id=7)
        calls = []

        def fake_chat(model, messages, *, response_format=None, operation="chat"):
            calls.append((model, [dict(item) for item in messages], response_format, operation))
            if response_format is not None:
                raise RuntimeError("AI HTTP 400: unsupported response_format parameter")
            return {"choices": [{"message": {"content": '{"title_fa":"استند کیک"}'}}]}

        client._chat = fake_chat
        with patch(
            "app.phase49_3i23_avalai_chat_contract._avalai_url_tool_evidence",
            return_value=("", "test_no_tool"),
        ):
            result, model = client.structured_response(
                instructions="Return Persian product content.",
                input_content=[{"type": "input_text", "text": '{"source_title":"Cake stand"}'}],
                schema={"type": "object", "properties": {"title_fa": {"type": "string"}}},
                schema_name="catalog_test",
                preferred_model="gpt-5-chat-latest",
            )

        self.assertEqual(result["title_fa"], "استند کیک")
        self.assertEqual(model, "gpt-5-chat-latest")
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0][2]["type"], "json_schema")
        self.assertEqual(calls[1][2], {"type": "json_object"})
        self.assertIsNone(calls[2][2])
        self.assertEqual(calls[2][3], "structured_content_avalai_prompt_json")
        self.assertIn("JSON_SCHEMA", calls[2][1][0]["content"])

    def test_gemini_url_context_uses_explicit_avalai_tool(self):
        client = AIProviderClient("avalai", "dummy-key", "gemini-2.5-flash", product_id=7)
        captured = {}

        def fake_request(url, key, **kwargs):
            captured.update({"url": url, "key": key, **kwargs})
            return {"choices": [{"message": {"content": "source evidence"}}]}

        with patch("app.phase49_3i23_avalai_chat_contract.ai_providers._json_request", side_effect=fake_request):
            evidence, mode = _avalai_url_tool_evidence(
                client,
                "gemini-2.5-flash",
                "https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter",
            )

        self.assertEqual(mode, "gemini_urlContext")
        self.assertEqual(evidence, "source evidence")
        self.assertTrue(captured["url"].endswith("/chat/completions"))
        self.assertEqual(captured["payload"]["tools"], [{"urlContext": {}}])
        self.assertEqual(captured["operation"], "avalai_url_context")

    def test_gpt5_url_evidence_uses_responses_web_search(self):
        client = AIProviderClient("avalai", "dummy-key", "gpt-5-chat-latest", product_id=7)
        captured = {}

        def fake_request(url, key, **kwargs):
            captured.update({"url": url, "key": key, **kwargs})
            return {"output_text": "verified source evidence"}

        with patch("app.phase49_3i23_avalai_chat_contract.ai_providers._json_request", side_effect=fake_request):
            evidence, mode = _avalai_url_tool_evidence(
                client,
                "gpt-5-chat-latest",
                "https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter",
            )

        self.assertEqual(mode, "responses_web_search")
        self.assertEqual(evidence, "verified source evidence")
        self.assertTrue(captured["url"].endswith("/responses"))
        self.assertEqual(
            captured["payload"]["tools"],
            [{"type": "web_search", "search_context_size": "low"}],
        )
        self.assertEqual(captured["operation"], "avalai_url_web_search")

    def test_lyria_is_rejected_for_product_structured_text(self):
        reason = product_text_model_reason("google/lyria-3-pro-preview")
        self.assertIn("مناسب نیست", reason)
        self.assertIn("lyria", reason.lower())
        self.assertEqual(product_text_model_reason("gpt-5-chat-latest"), "")


if __name__ == "__main__":
    unittest.main()
