from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from PySide6.QtWidgets import QApplication

from app.ai_model_catalog import (
    estimate_request_cost,
    format_model_label,
    model_matches_filter,
    product_model_compatibility,
    rank_models,
)
from app.ai_providers import AIProviderClient
from app.db import Database
from qt6.kernel import build_kernel
from qt6.main_window import MainWindow
from qt6.pages import OperationsPage
from qt6.settings_page import SettingsPage


class _FakeClient:
    def __init__(self):
        self.structured_calls = []
        self.model_catalog_calls = 0

    def test_connection(self, model=""):
        return {
            "model": model,
            "sample": "آماده",
            "request_id": "req-test",
            "usage": {},
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
        self.structured_calls.append(preferred_model)
        return {
            "title_fa": "پایه چراغ رومیزی",
            "seo_title_fa": "پایه چراغ رومیزی چاپ سه بعدی",
            "keywords": ["پایه چراغ", "چاپ سه بعدی"],
        }, preferred_model

    def list_model_info(self):
        self.model_catalog_calls += 1
        raise AssertionError(
            "Provider connection test must not perform a hidden model scan"
        )


class Phase493I42C3AiCrawlParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp.name) / "catalog.sqlite3")
        self.kernel = build_kernel(self.db)

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_model_ranking_puts_persian_free_structured_ahead(self):
        ranked = rank_models([
            {
                "id": "vendor/unknown-expensive",
                "pricing": {
                    "prompt": "0.00001",
                    "completion": "0.00002",
                },
                "supported_parameters": [],
            },
            {
                "id": "qwen/example:free",
                "pricing": {
                    "prompt": "0",
                    "completion": "0",
                },
                "supported_parameters": ["response_format"],
            },
            {
                "id": "gemma/example",
                "pricing": {
                    "prompt": "0.00000005",
                    "completion": "0.0000001",
                },
                "supported_parameters": ["response_format"],
            },
        ])
        self.assertEqual(
            ranked[0]["id"],
            "qwen/example:free",
        )
        label = format_model_label(ranked[0])
        self.assertIn("رایگان", label)
        self.assertIn("فارسی", label)
        self.assertIn("JSON", label)

    def test_live_free_persian_json_filter_prefers_known_strong_models(self):
        ranked = rank_models([
            {
                "id": "openai/gpt-oss-20b:free",
                "pricing": {"prompt": "0", "completion": "0"},
                "supported_parameters": ["response_format"],
                "architecture": {
                    "input_modalities": ["text"],
                    "output_modalities": ["text"],
                },
            },
            {
                "id": "qwen/qwen3-32b:free",
                "description": "Multilingual model across 100+ languages.",
                "pricing": {"prompt": "0", "completion": "0"},
                "supported_parameters": ["response_format"],
                "architecture": {
                    "input_modalities": ["text"],
                    "output_modalities": ["text"],
                },
            },
            {
                "id": "google/gemma-4-31b-it:free",
                "description": "Multilingual support across 140+ languages.",
                "pricing": {"prompt": "0", "completion": "0"},
                "supported_parameters": ["response_format"],
                "architecture": {
                    "input_modalities": ["text", "image"],
                    "output_modalities": ["text"],
                },
            },
        ])
        filtered = [
            item
            for item in ranked
            if model_matches_filter(item, "persian_free")
        ]
        self.assertEqual(len(filtered), 3)
        self.assertEqual(
            filtered[0]["id"],
            "qwen/qwen3-32b:free",
        )
        self.assertTrue(
            filtered[0]["persian_free_preferred"]
        )
        self.assertIn(
            "فارسی پیشنهادی",
            format_model_label(filtered[0]),
        )

    def test_cost_estimate_uses_provider_per_token_pricing(self):
        estimate = estimate_request_cost(
            {
                "id": "qwen/example",
                "pricing": {
                    "prompt": "0.00000008",
                    "completion": "0.00000018",
                },
            },
            input_tokens=1000,
            output_tokens=500,
        )
        self.assertTrue(estimate["known"])
        self.assertAlmostEqual(
            estimate["usd"],
            0.00017,
            places=8,
        )

    def test_simple_provider_test_never_hides_model_catalog_scan(self):
        fake = _FakeClient()
        with patch.object(
            self.kernel.providers,
            "_client",
            return_value=fake,
        ):
            result = self.kernel.providers.test(
                "openrouter",
                "qwen/exact-model:free",
                key_override="test-key",
                structured=False,
            )
        self.assertEqual(
            result["model"],
            "qwen/exact-model:free",
        )
        self.assertEqual(fake.model_catalog_calls, 0)
        self.assertEqual(fake.structured_calls, [])

    def test_structured_probe_keeps_exact_selected_model(self):
        fake = _FakeClient()
        self.kernel.providers._model_cache["openrouter"] = rank_models([
            {
                "id": "qwen/exact-model:free",
                "pricing": {
                    "prompt": "0",
                    "completion": "0",
                },
                "supported_parameters": ["response_format"],
                "architecture": {
                    "input_modalities": ["text"],
                    "output_modalities": ["text"],
                },
            }
        ])
        with patch.object(
            self.kernel.providers,
            "_client",
            return_value=fake,
        ):
            result = self.kernel.providers.test(
                "openrouter",
                "qwen/exact-model:free",
                key_override="test-key",
                structured=True,
            )
        self.assertTrue(result["structured_ok"])
        self.assertEqual(
            fake.structured_calls,
            ["qwen/exact-model:free"],
        )
        self.assertEqual(fake.model_catalog_calls, 0)


    def test_media_generation_model_is_excluded_from_product_filters(self):
        item = rank_models([
            {
                "id": "google/lyria-3-clip-preview",
                "name": "Lyria 3 Clip Preview",
                "description": "Music generation model for audio clips.",
                "pricing": {"request": "0.04"},
                "supported_parameters": ["response_format"],
                "architecture": {
                    "input_modalities": ["text", "image"],
                    "output_modalities": ["audio"],
                },
            }
        ])[0]
        ok, reason = product_model_compatibility(item)
        self.assertFalse(ok)
        self.assertIn("خروجی متنی", reason)
        self.assertFalse(model_matches_filter(item, "all"))
        self.assertFalse(model_matches_filter(item, "recommended"))

    def test_tools_only_code_model_is_not_product_structured_candidate(self):
        item = rank_models([
            {
                "id": "cohere/north-mini-code:free",
                "name": "North Mini Code",
                "description": (
                    "Agentic coding model optimized for software engineering "
                    "and terminal tasks."
                ),
                "pricing": {
                    "prompt": "0",
                    "completion": "0",
                },
                "supported_parameters": ["tools", "tool_choice"],
                "architecture": {
                    "input_modalities": ["text"],
                    "output_modalities": ["text"],
                },
            }
        ])[0]
        ok, reason = product_model_compatibility(item)
        self.assertFalse(ok)
        self.assertTrue(
            "کدنویسی" in reason
            or "response_format" in reason
        )
        self.assertFalse(model_matches_filter(item, "structured"))
        self.assertFalse(model_matches_filter(item, "recommended"))

    def test_openrouter_structured_request_uses_json_schema_and_require_parameters(self):
        captured = {}

        def fake_request(url, api_key, **kwargs):
            payload = dict(kwargs.get("payload") or {})
            captured.update(payload)
            return {
                "id": "req-structured",
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "title_fa": "پایه چراغ رومیزی",
                                    "seo_title_fa": "پایه چراغ رومیزی چاپ سه بعدی",
                                    "keywords": ["پایه چراغ", "چاپ سه بعدی"],
                                },
                                ensure_ascii=False,
                            )
                        }
                    }
                ],
            }

        client = AIProviderClient(
            "openrouter",
            "test-key",
            "qwen/example",
        )
        schema = {
            "type": "object",
            "properties": {
                "title_fa": {"type": "string"},
                "seo_title_fa": {"type": "string"},
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["title_fa", "seo_title_fa", "keywords"],
            "additionalProperties": False,
        }
        with patch(
            "app.ai_providers._json_request",
            side_effect=fake_request,
        ):
            result, selected = client.structured_response(
                instructions="Return Persian Product JSON.",
                input_content=[
                    {
                        "type": "input_text",
                        "text": "پایه چراغ رومیزی",
                    }
                ],
                schema=schema,
                schema_name="product_probe",
                preferred_model="qwen/example",
            )

        self.assertEqual(selected, "qwen/example")
        self.assertEqual(
            captured["response_format"]["type"],
            "json_schema",
        )
        self.assertTrue(
            captured["response_format"]["json_schema"]["strict"]
        )
        self.assertTrue(
            captured["provider"]["require_parameters"]
        )
        self.assertEqual(
            result["title_fa"],
            "پایه چراغ رومیزی",
        )

    def test_settings_model_filter_shows_free_persian_pricing(self):
        page = SettingsPage(
            self.db,
            kernel=self.kernel,
        )
        self.assertGreaterEqual(
            page.model_filter.findData("persian_free"),
            0,
        )
        page._model_info = rank_models([
            {
                "id": "qwen/example:free",
                "name": "Qwen Example",
                "pricing": {
                    "prompt": "0",
                    "completion": "0",
                },
                "supported_parameters": ["response_format"],
            }
        ])
        page._render_models()
        self.assertEqual(page.model.count(), 1)
        text = page.model.itemText(0)
        self.assertIn("رایگان", text)
        self.assertIn("فارسی", text)
        self.assertIn("JSON", text)

    def test_operations_restores_explicit_add_product_modes(self):
        page = OperationsPage(
            self.db,
            kernel=self.kernel,
        )
        values = {
            str(page.mode.itemData(index) or "")
            for index in range(page.mode.count())
        }
        self.assertEqual(
            values,
            {
                "automatic",
                "search",
                "category",
                "site_crawl",
                "single",
            },
        )
        self.assertTrue(hasattr(page, "query"))
        self.assertTrue(
            hasattr(page, "download_images")
        )
        self.assertTrue(
            hasattr(page, "default_url_btn")
        )
        self.assertTrue(hasattr(page, "direct_btn"))

    def test_main_window_names_acquisition_route_explicitly(self):
        window = MainWindow(self.kernel)
        labels = [
            window.nav.item(index).text()
            for index in range(window.nav.count())
        ]
        self.assertIn(
            "افزودن محصولات / Crawl",
            labels,
        )
        self.assertIsNotNone(
            window.products_page.navigate
        )
        window.close()


if __name__ == "__main__":
    unittest.main()
