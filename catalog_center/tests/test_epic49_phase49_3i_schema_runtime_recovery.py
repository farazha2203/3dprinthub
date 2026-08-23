from __future__ import annotations

import json
import types
import unittest
from pathlib import Path

from app.phase49_3i_schema_runtime_recovery import (
    MODEL_TRACE_SAMPLE_LIMIT,
    _compact_model_response,
    _release_busy_state,
    _schema_errors,
    _schema_instruction,
    _structured_compatible_response,
)


ROOT = Path(__file__).resolve().parents[2]


SIMPLE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title_fa": {"type": "string"},
        "seo_title_fa": {"type": "string"},
        "seo_description_fa": {"type": "string"},
        "content_notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["title_fa", "seo_title_fa", "seo_description_fa", "content_notes"],
}


class FakeCompatibleClient:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []
        self.model = "gemini-3.5-flash-lite"
        self.provider = "avalai"
        self.spec = types.SimpleNamespace(label="AvalAI")

    def choose_model(self, preferred=""):
        return preferred or self.model

    def _chat(self, model, messages, *, response_format=None, operation="chat"):
        self.calls.append({
            "model": model,
            "messages": messages,
            "response_format": response_format,
            "operation": operation,
        })
        payload = self.outputs.pop(0)
        return {
            "model": model,
            "choices": [{"message": {"content": json.dumps(payload, ensure_ascii=False)}}],
        }


class Phase493I11SchemaRuntimeRecoveryTests(unittest.TestCase):
    def test_actual_owner_failure_shape_is_detected_as_schema_mismatch(self):
        malformed = {
            "title_fa": "جاشمعی LED گوتیک طرح کدو تنبل هالووین سامهاین",
            "seo_title": "خرید جاشمعی LED گوتیک",
            "seo_description": "توضیح سئو",
            "content_notes": "یادداشت به صورت رشته",
        }
        errors = _schema_errors(malformed, SIMPLE_SCHEMA)
        joined = " | ".join(errors)
        self.assertIn("$.seo_title_fa: missing required key", joined)
        self.assertIn("$.seo_description_fa: missing required key", joined)
        self.assertIn("$.seo_title: unexpected key", joined)
        self.assertIn("$.content_notes: expected array", joined)

    def test_schema_is_sent_and_one_repair_recovers_wrong_aliases(self):
        malformed = {
            "title_fa": "جاشمعی LED گوتیک طرح کدو تنبل هالووین سامهاین",
            "seo_title": "خرید جاشمعی LED گوتیک",
            "seo_description": "توضیح سئو",
            "content_notes": "نیازمند بررسی",
        }
        repaired = {
            "title_fa": "جاشمعی LED گوتیک طرح کدو تنبل هالووین سامهاین",
            "seo_title_fa": "خرید جاشمعی LED گوتیک طرح کدو تنبل هالووین",
            "seo_description_fa": "جاشمعی LED گوتیک طرح کدو تنبل مناسب دکور هالووین.",
            "content_notes": ["نیازمند بررسی اپراتور"],
        }
        client = FakeCompatibleClient([malformed, repaired])
        result, model = _structured_compatible_response(
            client,
            instructions="Translate facts conservatively.",
            input_content=[{"type": "input_text", "text": "Halloween pumpkin tealight holder"}],
            schema=SIMPLE_SCHEMA,
            schema_name="owner_failure_recovery",
            preferred_model="gemini-3.5-flash-lite",
        )
        self.assertEqual(model, "gemini-3.5-flash-lite")
        self.assertEqual(result["seo_title_fa"], repaired["seo_title_fa"])
        self.assertEqual(len(client.calls), 2)
        self.assertEqual(client.calls[0]["response_format"]["type"], "json_schema")
        self.assertIn('"seo_title_fa"', client.calls[0]["messages"][0]["content"])
        self.assertEqual(client.calls[1]["operation"], "structured_content_repair")
        self.assertIn("schema_validation_errors", client.calls[1]["messages"][1]["content"])

    def test_schema_instruction_contains_exact_property_names(self):
        text = _schema_instruction("Do the work.", "x", SIMPLE_SCHEMA)
        self.assertIn("STRICT OUTPUT CONTRACT", text)
        self.assertIn('"seo_title_fa"', text)
        self.assertIn("do not rename fields", text.lower())

    def test_model_catalog_trace_is_summarized_not_dumped(self):
        response = {
            "object": "list",
            "data": [
                {
                    "id": f"model-{index}",
                    "owned_by": "vendor",
                    "mode": "chat",
                    "supports_response_schema": True,
                    "huge_irrelevant_field": "x" * 5000,
                }
                for index in range(MODEL_TRACE_SAMPLE_LIMIT + 10)
            ],
        }
        compact = _compact_model_response(response)
        self.assertEqual(compact["models_count"], MODEL_TRACE_SAMPLE_LIMIT + 10)
        self.assertEqual(len(compact["models_sample"]), MODEL_TRACE_SAMPLE_LIMIT)
        self.assertTrue(compact["truncated"])
        self.assertNotIn("huge_irrelevant_field", json.dumps(compact))

    def test_stop_waiting_release_clears_runtime_busy_flags(self):
        parent = types.SimpleNamespace(
            _phase49_3e_busy=True,
            _ai_busy=True,
            _phase49_3f_source_busy=True,
            _phase49_3i_ai_starting=True,
        )
        _release_busy_state(parent)
        self.assertFalse(parent._phase49_3e_busy)
        self.assertFalse(parent._ai_busy)
        self.assertFalse(parent._phase49_3f_source_busy)
        self.assertFalse(parent._phase49_3i_ai_starting)

    def test_runtime_composition_installs_3i11_after_3i10_trace(self):
        source = (ROOT / "catalog_center/app/phase49_3i_local_qa_hotfix.py").read_text(encoding="utf-8")
        trace_pos = source.index("install_ai_trace_recovery(workspace_class, phase49_3f_workspace_module)")
        schema_pos = source.index("install_schema_runtime_recovery(workspace_class, phase49_3f_workspace_module, trace_module)")
        self.assertLess(trace_pos, schema_pos)

    def test_runtime_source_has_strict_schema_repair_and_model_trace_compaction(self):
        source = (ROOT / "catalog_center/app/phase49_3i_schema_runtime_recovery.py").read_text(encoding="utf-8")
        self.assertIn('"type": "json_schema"', source)
        self.assertIn("structured_content_repair", source)
        self.assertIn("previous_invalid_output", source)
        self.assertIn("MODEL_TRACE_SAMPLE_LIMIT", source)
        self.assertIn("_release_busy_state", source)
        self.assertIn("cached_for_request", source)


if __name__ == "__main__":
    unittest.main()
