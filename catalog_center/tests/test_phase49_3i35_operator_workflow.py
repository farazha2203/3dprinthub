from __future__ import annotations

import json
import threading
import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.phase49_3i35_operator_ledger import (
    flatten_ledger_profiles,
    normalize_ledger_profile,
    offer_price_preview,
)
from app import phase49_3i35_resilient_ai as resilient_ai


ROOT = Path(__file__).resolve().parents[1]


class _SettingsDB:
    def __init__(self, values=None):
        self.values = dict(values or {})

    def setting(self, key, default=""):
        return self.values.get(key, default)


class _Dialog:
    def __init__(self):
        self.cancelled = threading.Event()
        self.events = []
        self.progress = []

    def event(self, code, message, detail=None):
        self.events.append((code, message, detail or {}))

    def set_progress(self, value, message=""):
        self.progress.append((float(value), message))


class Phase493I35OperatorWorkflowTests(unittest.TestCase):
    def test_ledger_flattens_working_form_into_independent_transport_rows(self):
        ledger = [{
            "key": "cake-20",
            "name": "سایز ۲۰",
            "size_label": "20 سانتی‌متر",
            "pricing_strategy": "dynamic",
            "production_rows": [
                {"weight_grams": 100, "print_time_minutes": 90, "support_weight_grams": 12},
                {"weight_grams": 150, "print_time_minutes": 120, "support_weight_grams": 18},
            ],
            "material_options": [{
                "material": "PLA",
                "brand": "Bambu Lab",
                "manufacturer": "Bambu Lab",
                "color": "سفید مات",
                "roll_weight_grams": 1000,
                "stock_roll_count": 1,
                "purchase_price_per_roll": 2_500_000,
                "sale_price_per_roll": 3_600_000,
                "usd_price_per_roll": 30,
                "usd_fx_rate_toman": 130_000,
            }],
            "is_default": True,
        }]
        rows = flatten_ledger_profiles(ledger)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["brand"], "Bambu Lab")
        self.assertEqual(rows[0]["manufacturer"], "Bambu Lab")
        self.assertEqual(rows[0]["support_weight_grams"], 12)
        self.assertEqual(rows[0]["material_weight_grams"], 112)
        self.assertEqual(rows[0]["fixed_price"], 0)
        self.assertEqual(rows[1]["weight_grams"], 150)
        self.assertNotEqual(rows[0]["key"], rows[1]["key"])

    def test_fixed_profile_has_one_explicit_price_authority(self):
        profile = normalize_ledger_profile({
            "key": "fixed-30",
            "name": "۳۰ سانت",
            "pricing_strategy": "fixed",
            "price_min": 850_000,
            "price_max": 850_000,
            "production_rows": [{"weight_grams": 300, "print_time_minutes": 210, "support_weight_grams": 20}],
        })
        row = flatten_ledger_profiles([profile])[0]
        self.assertEqual(row["fixed_price"], 850_000)

    def test_filament_preview_uses_higher_explicit_sale_basis_without_guessing_fx(self):
        offer = {
            "roll_weight_grams": 1000,
            "sale_price_per_roll": 3_600_000,
            "usd_price_per_roll": 30,
            "usd_fx_rate_toman": 130_000,
        }
        production = {"weight_grams": 100, "support_weight_grams": 20}
        self.assertEqual(offer_price_preview(offer, production), 468_000)

        no_fx = dict(offer)
        no_fx["usd_fx_rate_toman"] = 0
        self.assertEqual(offer_price_preview(no_fx, production), 432_000)

    def test_configured_fallbacks_are_explicit_and_bounded(self):
        app = SimpleNamespace(db=_SettingsDB({
            "ai_fallback_enabled": "1",
            "ai_fallback_openrouter_free": "1",
            "ai_fallback_order": "openrouter,google,avalai,openai",
            "ai_model_google": "gemini-test",
            "ai_model_avalai": "avalai-test",
        }))
        keys = {"openrouter": "or-key", "google": "g-key", "avalai": "a-key", "openai": "primary-key"}
        with patch.object(resilient_ai, "active_ai_config", return_value=("openai", "primary-key", "gpt-test")), \
             patch.object(resilient_ai, "get_provider_key", side_effect=lambda provider: keys.get(provider, "")):
            candidates = resilient_ai.configured_ai_candidates(app)
        self.assertEqual(candidates[0], ("openai", "primary-key", "gpt-test", "primary"))
        self.assertEqual(candidates[1], ("openrouter", "or-key", "openrouter/free", "fallback-free"))
        self.assertEqual(candidates[2], ("google", "g-key", "gemini-test", "fallback"))
        self.assertEqual(len(candidates), 3)

    def test_retry_exhaustion_falls_through_to_next_provider(self):
        app = SimpleNamespace(db=_SettingsDB({"ai_retry_attempts": "3"}))
        dialog = _Dialog()
        candidates = [
            ("openai", "key-1", "model-1", "primary"),
            ("google", "key-2", "model-2", "fallback"),
        ]
        good = {"title_fa": "عنوان فارسی", "changed_fields": ["title_fa"]}
        failures = [RuntimeError("one"), RuntimeError("two"), RuntimeError("three"), good]
        with patch.object(resilient_ai, "configured_ai_candidates", return_value=candidates), \
             patch.object(resilient_ai, "_preflight", side_effect=lambda _d, _p, _k, model, _s, _c: {"model": model}), \
             patch.object(resilient_ai, "run_ai_mode", side_effect=failures) as runner:
            result = resilient_ai.run_resilient_ai(app, 77, "link", dialog)
        self.assertEqual(result["title_fa"], "عنوان فارسی")
        self.assertEqual(runner.call_count, 4)
        self.assertIn("fallback", [item[0] for item in dialog.events])
        self.assertIn("reply", [item[0] for item in dialog.events])
        self.assertEqual(dialog.progress[-1][0], 100.0)

    def test_ai_resilience_settings_respects_pack_managed_settings_tab(self):
        source = (ROOT / "app" / "phase49_3i35_resilient_ai.py").read_text(encoding="utf-8")
        self.assertIn('panel.pack(fill="x", padx=8, pady=8)', source)
        self.assertNotIn('panel.grid(row=50, column=0, columnspan=2', source)

    def test_final_composition_and_release_manifest_include_3i35(self):
        composition = (ROOT / "app" / "phase49_3i_pricing_modes.py").read_text(encoding="utf-8")
        launcher = (ROOT / "launch.py").read_text(encoding="utf-8")
        manifest = json.loads((ROOT / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
        for marker in (
            "_install_phase49_3i35_operator_ledger(workspace_class)",
            "_install_phase49_3i35_resilient_workspace(workspace_class)",
            "_install_phase49_3i35_readiness_review(workspace_class)",
            "_install_phase49_3i35_resilient_app(app_class)",
        ):
            self.assertIn(marker, composition)
        for marker in (
            "EPIC49_3I35_OPERATOR_LEDGER=ENABLED",
            "EPIC49_3I35_RESILIENT_AI_RETRY_FAILOVER=ENABLED",
            "EPIC49_3I35_MANUAL_SEO_SOURCE_REVIEW=ENABLED",
        ):
            self.assertIn(marker, launcher)
        self.assertEqual(manifest["version"], "8.9.4")
        for path in (
            "app/phase49_3i35_operator_ledger.py",
            "app/phase49_3i35_resilient_ai.py",
            "app/phase49_3i35_readiness_review.py",
        ):
            self.assertIn(path, manifest["files"])


if __name__ == "__main__":
    unittest.main()
