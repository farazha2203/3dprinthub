from __future__ import annotations

import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from app.ai_providers import AIProviderClient, PROVIDERS
from app.db import Database
from app import secure_secrets
from app.phase49_diagnostics import (
    ai_request_event,
    audit_event,
    configure,
    export_diagnostic_bundle,
    recent_ai_requests,
    recent_app_events,
)


class Phase493BAIProviderTests(unittest.TestCase):
    def test_product_ai_runtime_imports_cleanly(self):
        module = importlib.import_module("app.phase49_3b_ai_product_runtime")
        self.assertTrue(callable(module.install))
        self.assertTrue(callable(module._sync_reference_lists))

    def test_openrouter_is_first_class_provider(self):
        self.assertIn("openrouter", PROVIDERS)
        self.assertEqual(PROVIDERS["openrouter"].base_url, "https://openrouter.ai/api/v1")
        client = AIProviderClient("openrouter", "test-key", "")
        with patch.object(client, "list_model_info", return_value=[
            {"id": "openrouter/free", "free": True},
            {"id": "vendor/paid", "free": False},
        ]):
            self.assertEqual(client.choose_model(""), "openrouter/free")

    def test_openrouter_secret_registry_is_static_and_isolated(self):
        self.assertEqual(secure_secrets.USERS["openai"], "OPENAI_API_KEY")
        self.assertEqual(secure_secrets.USERS["avalai"], "AVALAI_API_KEY")
        self.assertEqual(secure_secrets.USERS["openrouter"], "OPENROUTER_API_KEY")
        self.assertEqual(
            secure_secrets.CONNECTION_USERS["openrouter_management_key"],
            "OPENROUTER_MANAGEMENT_KEY",
        )
        self.assertEqual(
            secure_secrets.CONNECTION_USERS["openai_admin_key"],
            "OPENAI_ADMIN_KEY",
        )
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "openai-key",
                "OPENROUTER_API_KEY": "openrouter-key",
            },
            clear=False,
        ):
            self.assertEqual(secure_secrets.get_provider_key("openai"), "openai-key")
            self.assertEqual(secure_secrets.get_provider_key("openrouter"), "openrouter-key")

    def test_avalai_structured_400_retries_without_response_format(self):
        client = AIProviderClient("avalai", "test-key", "model-x")
        client.choose_model = Mock(return_value="model-x")
        client._chat = Mock(side_effect=[
            RuntimeError("AI HTTP 400: invalid_request unsupported response_format"),
            {"choices": [{"message": {"content": '{"title_fa":"عنوان فارسی"}'}}]},
        ])
        result, model = client.structured_response(
            instructions="Return JSON",
            input_content=[{"type": "input_text", "text": "hello"}],
            schema={"type": "object", "properties": {"title_fa": {"type": "string"}}},
            schema_name="test",
        )
        self.assertEqual(model, "model-x")
        self.assertEqual(result["title_fa"], "عنوان فارسی")
        self.assertEqual(client._chat.call_count, 2)
        first = client._chat.call_args_list[0].kwargs
        second = client._chat.call_args_list[1].kwargs
        self.assertEqual(first["response_format"], {"type": "json_object"})
        self.assertIsNone(second["response_format"])

    def test_provider_hub_has_independent_cards_and_balance_contracts(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "app" / "phase49_ai_provider_hub.py").read_text(encoding="utf-8")
        for token in (
            "AvalAI — پرداخت",
            "OpenRouter — مدل‌های متعدد",
            "OpenAI Direct",
            "Management Key",
            "Admin Key",
            "اعتبار / هزینه",
        ):
            self.assertIn(token, text)
        providers = (root / "app" / "ai_providers.py").read_text(encoding="utf-8")
        self.assertIn("openrouter/free", providers)
        self.assertIn("/user/v1/credit", providers)
        self.assertIn("/v1/credits", providers)


class Phase493BDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = Database(self.root / "catalog.sqlite3")
        configure(self.db)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_audit_and_ai_logs_are_persistent_and_secrets_redacted(self):
        audit_event(
            "settings",
            "save",
            message="Authorization: Bearer super-secret-token",
            detail={"api_key": "sk-test-secret"},
        )
        ai_request_event(
            provider="openrouter",
            model="openrouter/free",
            operation="test",
            endpoint="https://openrouter.ai/api/v1/chat/completions",
            request_id="req-123",
            http_status=200,
            usage={"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18, "cost": 0},
            cost_usd=0.0,
            product_id=42,
            request_summary={"token": "do-not-store"},
            response_summary={"ok": True},
        )
        app_rows = recent_app_events(50)
        ai_rows = recent_ai_requests(50)
        self.assertTrue(app_rows)
        self.assertTrue(ai_rows)
        serialized = json.dumps(app_rows, ensure_ascii=False)
        self.assertNotIn("super-secret-token", serialized)
        self.assertNotIn("sk-test-secret", serialized)
        self.assertEqual(ai_rows[0]["request_id"], "req-123")
        self.assertEqual(ai_rows[0]["product_id"], 42)
        self.assertEqual(ai_rows[0]["total_tokens"], 18)

    def test_diagnostic_bundle_is_shareable_json_without_secret(self):
        audit_event("runtime", "error", status="error", message="password=secret-password")
        path = export_diagnostic_bundle(self.root)
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("app_events", text)
        self.assertIn("ai_requests", text)
        self.assertNotIn("secret-password", text)


if __name__ == "__main__":
    unittest.main()
