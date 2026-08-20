from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from app import phase49_3f_gemini_provider as gemini
from app import phase49_3f_runtime_trace as runtime_trace
from app.phase49_3f_ai_experience import PROVIDER_ORDER, prepare_provider_modules
from app.phase49_3f_selected_image_ai import (
    generate_selected_image_text,
    merge_selected_metadata,
    selected_image_text_payload,
)
from app import secure_secrets


class _FakeAIService:
    provider = "google"
    model = "gemini-flash-lite-test"

    def __init__(self):
        self.client = Mock()
        self.client.structured_response.return_value = (
            {
                "items": [
                    {
                        "slot": 1,
                        "alt_text": "نمای محصول چاپ سه‌بعدی",
                        "title": "محصول چاپ سه‌بعدی",
                        "caption": "نمای منتخب محصول",
                        "keywords": ["چاپ سه‌بعدی"],
                    }
                ]
            },
            self.model,
        )


class Phase493FSelectedImageAITests(unittest.TestCase):
    def setUp(self):
        self.selected = [
            "https://cdn.example.test/private-product-image-1.jpg",
            "https://cdn.example.test/private-product-image-2.jpg",
        ]
        self.row = {
            "title_fa": "گکو مفصلی",
            "source_title": "Flexi Gecko",
            "short_description_fa": "مدل مفصلی چاپ سه‌بعدی",
            "description_fa": "توضیحات محصول",
            "seo_title_fa": "خرید گکو مفصلی چاپ سه‌بعدی",
            "seo_description_fa": "سفارش چاپ گکو مفصلی",
            "keywords_json": json.dumps(["گکو", "چاپ سه‌بعدی"], ensure_ascii=False),
            "tags_fa_json": "[]",
            "hashtags_fa_json": "[]",
            "source_specs_json": json.dumps({"print": "FDM"}),
            "image_alt_texts_json": json.dumps(["نمای اول", "نمای دوم"], ensure_ascii=False),
        }

    def test_text_payload_contains_no_selected_image_url_or_binary_reference(self):
        payload = selected_image_text_payload(self.row, self.selected)
        raw = json.dumps(payload, ensure_ascii=False)
        for url in self.selected:
            self.assertNotIn(url, raw)
        self.assertNotIn("input_image", raw)
        self.assertNotIn("image_url", raw)
        self.assertEqual(payload["selected_count"], 2)
        self.assertEqual([item["slot"] for item in payload["selected_image_slots"]], [1, 2])

    def test_generate_selected_image_text_sends_only_input_text(self):
        service = _FakeAIService()
        result = generate_selected_image_text(service, self.row, self.selected)
        kwargs = service.client.structured_response.call_args.kwargs
        content = kwargs["input_content"]
        self.assertEqual([item.get("type") for item in content], ["input_text"])
        serialized = json.dumps(content, ensure_ascii=False)
        for url in self.selected:
            self.assertNotIn(url, serialized)
        self.assertEqual(result["_ai_provider"], "google")
        self.assertEqual(result["_ai_model"], service.model)

    def test_merge_edits_selected_and_preserves_unselected_metadata(self):
        selected_url = self.selected[0]
        unselected_url = "https://cdn.example.test/unselected.jpg"
        unselected = {
            "source_url": unselected_url,
            "alt_text": "این رکورد نباید تغییر کند",
            "creator": "Original creator",
            "custom": {"keep": True},
        }
        existing = [
            {"source_url": selected_url, "alt_text": "قدیمی", "creator": "Creator A"},
            unselected,
        ]
        pack = {
            "items": [
                {
                    "slot": 1,
                    "alt_text": "Alt جدید",
                    "title": "Title جدید",
                    "caption": "Caption جدید",
                    "keywords": ["SEO"],
                }
            ]
        }
        merged = merge_selected_metadata(existing, [selected_url], pack)
        by_url = {item["source_url"]: item for item in merged}
        self.assertEqual(by_url[selected_url]["alt_text"], "Alt جدید")
        self.assertEqual(by_url[selected_url]["creator"], "Creator A")
        self.assertEqual(by_url[unselected_url], unselected)


class Phase493FGeminiAndProviderTests(unittest.TestCase):
    def test_google_is_first_class_selectable_provider_and_secret_is_isolated(self):
        gemini.install()
        prepare_provider_modules()
        self.assertIn("google", PROVIDER_ORDER)
        self.assertEqual(secure_secrets.USERS["google"], "GOOGLE_GEMINI_API_KEY")
        self.assertEqual(gemini.ai_providers.PROVIDERS["google"].base_url, gemini.GOOGLE_BASE)

    def test_google_model_list_filters_to_generate_content_models(self):
        gemini.install()
        client = gemini.AIProviderClient("google", "test-secret-key", "")
        payload = {
            "models": [
                {
                    "name": "models/gemini-2.5-flash-lite",
                    "displayName": "Gemini 2.5 Flash-Lite",
                    "supportedGenerationMethods": ["generateContent", "countTokens"],
                    "inputTokenLimit": 1000000,
                },
                {
                    "name": "models/embedding-001",
                    "displayName": "Embedding",
                    "supportedGenerationMethods": ["embedContent"],
                },
            ]
        }
        with patch.object(gemini, "_google_request", return_value=payload):
            info = client.list_model_info()
        self.assertEqual([item["id"] for item in info], ["gemini-2.5-flash-lite"])
        self.assertEqual(info[0]["name"], "Gemini 2.5 Flash-Lite")


class Phase493FRuntimeTraceTests(unittest.TestCase):
    def test_runtime_trace_redacts_structured_and_inline_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = runtime_trace.configure(tmp, operator="qa-operator", workstation="qa-pc")
            record = runtime_trace.event(
                "ai",
                "secret-test",
                provider="google",
                model="gemini-test",
                message="Authorization: Bearer very-secret-token password=hunter2 secret=topsecret",
                detail={
                    "api_key": "AIza-secret-value",
                    "nested": {"refresh_token": "refresh-secret", "safe": "ok"},
                },
            )
            raw = path.read_text(encoding="utf-8")
            for forbidden in (
                "very-secret-token",
                "hunter2",
                "topsecret",
                "AIza-secret-value",
                "refresh-secret",
            ):
                self.assertNotIn(forbidden, raw)
            self.assertEqual(record["operator"], "qa-operator")
            self.assertEqual(record["workstation"], "qa-pc")
            self.assertEqual(record["detail"]["nested"]["safe"], "ok")
            self.assertIn("***", raw)


class Phase493FSourceRefreshGuardTests(unittest.TestCase):
    def test_generic_updated_at_change_does_not_trigger_ai(self):
        from app import phase49_3f_source_refresh_guard as guard
        from app import phase49_3f_workspace as workspace_module

        class FakeProgress:
            def __init__(self, *_args, **_kwargs):
                self.steps = []
            def step(self, *args):
                self.steps.append(args)
            def fail(self, *args):
                self.steps.append(args)

        class FakeDB:
            def __init__(self):
                self.row = {
                    "source_url": "https://example.test/item",
                    "last_refetched_at": "2026-08-20T01:00:00Z",
                    "updated_at": "2026-08-20T01:00:00Z",
                }
            def product(self, _product_id):
                return dict(self.row)

        class Workspace:
            pass

        original_progress = workspace_module.AIProgress
        workspace_module.AIProgress = FakeProgress
        try:
            guard.install(Workspace)
        finally:
            workspace_module.AIProgress = original_progress

        obj = Workspace()
        obj.product_id = 7
        obj.db = FakeDB()
        obj.footer_status = Mock()
        obj.save = Mock()
        obj._phase49_3f_source_busy = False
        obj._phase49_3f_generate_technical = Mock()
        scheduled = []
        obj.after = lambda _ms, callback: scheduled.append(callback)

        def refetch_only_changes_editor_timestamp():
            obj.db.row["updated_at"] = "2026-08-20T01:01:00Z"
        obj.refetch = refetch_only_changes_editor_timestamp

        with patch.object(guard.runtime_trace, "event"):
            obj._phase49_3f_refresh_source_and_generate()
            self.assertTrue(scheduled)
            first_poll = scheduled.pop(0)
            first_poll()
            self.assertFalse(obj._phase49_3f_generate_technical.called)
            self.assertTrue(scheduled, "poll must continue while last_refetched_at is unchanged")
            obj.db.row["last_refetched_at"] = "2026-08-20T01:02:00Z"
            next_poll = scheduled.pop(0)
            next_poll()
            self.assertTrue(obj._phase49_3f_generate_technical.called)
