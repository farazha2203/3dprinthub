from __future__ import annotations

import json
import unittest

from app.ai_providers import AIProviderClient
from app.phase49_3i23_avalai_chat_contract import install


class Phase493I23AvalAIChatContractTests(unittest.TestCase):
    def setUp(self):
        install()

    def test_product_request_uses_saved_model_without_model_scan(self):
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
        self.assertEqual(response_format, {"type": "json_object"})
        self.assertEqual(operation, "structured_content_avalai_exact")
        self.assertIn("JSON_SCHEMA", messages[0]["content"])
        self.assertIn('"title_fa"', messages[0]["content"])
        self.assertIn("Ribbed cake stand, cookie platter", messages[1]["content"])
        self.assertIn("makerworld.com/en/models/2896217", messages[1]["content"])
        self.assertNotIn("input_image", messages[1]["content"])
        self.assertNotIn("example.invalid", messages[1]["content"])

    def test_response_format_compat_fallback_keeps_same_exact_model_and_prompt(self):
        client = AIProviderClient("avalai", "dummy-key", "gpt-5-chat-latest", product_id=7)
        calls = []

        def fake_chat(model, messages, *, response_format=None, operation="chat"):
            calls.append((model, messages, response_format, operation))
            if response_format is not None:
                raise RuntimeError("AI HTTP 400: unsupported response_format parameter")
            return {"choices": [{"message": {"content": '{"title_fa":"استند کیک"}'}}]}

        client._chat = fake_chat
        result, model = client.structured_response(
            instructions="Return Persian product content.",
            input_content=[{"type": "input_text", "text": '{"source_title":"Cake stand"}'}],
            schema={"type": "object", "properties": {"title_fa": {"type": "string"}}},
            schema_name="catalog_test",
            preferred_model="gpt-5-chat-latest",
        )

        self.assertEqual(result["title_fa"], "استند کیک")
        self.assertEqual(model, "gpt-5-chat-latest")
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0], calls[1][0])
        self.assertEqual(calls[0][1], calls[1][1])
        self.assertIsNone(calls[1][2])
        self.assertEqual(calls[1][3], "structured_content_avalai_compat")


if __name__ == "__main__":
    unittest.main()
