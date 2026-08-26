from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest import mock

from app.ai_providers import AIProviderClient
from app.openai_content import AIContentService
from app.phase49_3i17_single_active_ai_runtime import active_ai_config
from app.phase49_3i29_windows_performance_ai import (
    PRODUCT_PAGE_SIZE,
    _install_exact_saved_model_execution,
    _install_minimal_product_ai_payload,
    minimal_product_payload,
    page_slice,
)


class _SettingsDB:
    def __init__(self, values):
        self.values = dict(values)

    def setting(self, key, default=""):
        return self.values.get(key, default)


class _App:
    def __init__(self, values):
        self.db = _SettingsDB(values)


class Phase49I29WindowsPerformanceAITests(unittest.TestCase):
    def test_product_page_is_bounded_without_losing_full_result_set(self):
        rows = list(range(125))
        page, pages, visible = page_slice(rows, 1)
        self.assertEqual(PRODUCT_PAGE_SIZE, 48)
        self.assertEqual(page, 1)
        self.assertEqual(pages, 3)
        self.assertEqual(visible, list(range(48, 96)))
        self.assertEqual(len(rows), 125)

    def test_product_page_clamps_out_of_range_page(self):
        page, pages, visible = page_slice(list(range(50)), 999)
        self.assertEqual((page, pages), (1, 2))
        self.assertEqual(visible, [48, 49])

    def test_ai_business_payload_contains_only_title_and_description(self):
        payload = minimal_product_payload({
            "source_title": "Minimal Lamp",
            "source_description": "Decorative wired lamp.",
            "source_price": 99,
            "selected_materials": ["PLA"],
            "selected_colors": ["black"],
            "license_name": "example",
            "internal_id": 123,
        })
        self.assertEqual(
            payload,
            {
                "source_title": "Minimal Lamp",
                "source_description": "Decorative wired lamp.",
            },
        )

    def test_active_openrouter_uses_provider_specific_saved_model(self):
        app = _App({
            "ai_provider": "openrouter",
            "ai_model": "avalai/stale-model",
            "ai_model_openrouter": "qwen/qwen3-32b",
        })
        with mock.patch(
            "app.phase49_3i17_single_active_ai_runtime.secure_secrets.get_provider_key",
            return_value="sk-or-test",
        ):
            provider, key, model = active_ai_config(app)
        self.assertEqual(provider, "openrouter")
        self.assertEqual(key, "sk-or-test")
        self.assertEqual(model, "qwen/qwen3-32b")

    def test_product_execution_never_runs_hidden_model_listing(self):
        _install_exact_saved_model_execution()
        client = AIProviderClient("openrouter", "sk-or-test", "qwen/qwen3-32b", product_id=7)
        with mock.patch.object(client, "list_model_info", side_effect=AssertionError("hidden /models request")):
            self.assertEqual(client.choose_model("qwen/qwen3-32b"), "qwen/qwen3-32b")

    def test_enrich_product_serializes_only_two_business_fields(self):
        _install_exact_saved_model_execution()
        _install_minimal_product_ai_payload()
        service = AIContentService("sk-or-test", "qwen/qwen3-32b", "openrouter", product_id=9)
        captured = {}

        def structured_response(**kwargs):
            captured.update(kwargs)
            return {"title_fa": "چراغ", "seo_title_fa": "چراغ", "seo_description_fa": "چراغ دکوراتیو"}, "qwen/qwen3-32b"

        service.client.structured_response = structured_response
        with mock.patch("app.openai_content.validate_content_pack", return_value=None):
            result = service.enrich_product(
                {
                    "source_title": "Lamp",
                    "source_description": "Decorative lamp",
                    "source_price": 100,
                    "selected_materials": ["PLA"],
                },
                [{"slug": "decor", "name": "Decor"}],
                image_count=0,
                image_urls=[],
            )
        self.assertEqual(result["_ai_provider"], "openrouter")
        text_items = [item for item in captured["input_content"] if item.get("type") == "input_text"]
        self.assertEqual(len(text_items), 1)
        sent = json.loads(text_items[0]["text"])
        self.assertEqual(set(sent), {"source_title", "source_description"})
        self.assertNotIn("allowed_site_categories", sent)
        self.assertNotIn("selected_materials", sent)
        self.assertNotIn("source_price", sent)

    def test_final_composition_wires_phase49_3i29_after_3i26(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "app" / "phase49_3i_pricing_modes.py").read_text(encoding="utf-8")
        app_26 = text.index("_install_phase49_3i26_app(app_class)")
        app_29 = text.index("_install_phase49_3i29_app(app_class)")
        workspace_27 = text.index("_install_phase49_3i27_workspace(workspace_class)")
        workspace_29 = text.index("_install_phase49_3i29_workspace(workspace_class")
        self.assertLess(app_26, app_29)
        self.assertLess(workspace_27, workspace_29)

    def test_workspace_save_regression_is_explicitly_deferred(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "app" / "phase49_3i29_windows_performance_ai.py").read_text(encoding="utf-8")
        self.assertIn('for name in ("refresh_products", "refresh_published", "load_product")', text)
        self.assertIn("_phase49_3i29_mark_products_dirty", text)
        self.assertIn("_phase49_3i29_flush_products_refresh", text)
        self.assertIn("PRODUCT_PAGE_SIZE = 48", text)


if __name__ == "__main__":
    unittest.main()
