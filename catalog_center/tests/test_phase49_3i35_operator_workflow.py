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
    install_workspace,
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

    def test_filament_preview_uses_sale_roll_rate_even_when_usd_snapshot_is_higher(self):
        offer = {
            "roll_weight_grams": 1000,
            "sale_price_per_roll": 3_600_000,
            "usd_price_per_roll": 30,
            "usd_fx_rate_toman": 130_000,
        }
        production = {"weight_grams": 100, "support_weight_grams": 20}
        self.assertEqual(offer_price_preview(offer, production), 432_000)

        no_fx = dict(offer)
        no_fx["usd_fx_rate_toman"] = 0
        self.assertEqual(offer_price_preview(no_fx, production), 432_000)

    def test_product_ai_candidates_are_openrouter_only(self):
        app = SimpleNamespace(db=_SettingsDB({
            "ai_fallback_enabled": "1",
            "ai_fallback_openrouter_free": "1",
        }))
        with patch.object(
            resilient_ai,
            "active_ai_config",
            return_value=("openrouter", "sk-or-v1-primary", "nvidia/test-model"),
        ):
            candidates = resilient_ai.configured_ai_candidates(app)

        self.assertEqual(
            candidates,
            [
                ("openrouter", "sk-or-v1-primary", "nvidia/test-model", "primary"),
                ("openrouter", "sk-or-v1-primary", "openrouter/free", "openrouter-free-router"),
            ],
        )
        self.assertEqual({item[0] for item in candidates}, {"openrouter"})

    def test_non_openrouter_active_provider_is_rejected_for_product_ai(self):
        app = SimpleNamespace(db=_SettingsDB())
        with patch.object(
            resilient_ai,
            "active_ai_config",
            return_value=("avalai", "avalai-key", "gemini-test"),
        ):
            with self.assertRaisesRegex(RuntimeError, "OpenRouter"):
                resilient_ai.configured_ai_candidates(app)

    def test_openrouter_free_is_not_duplicated_when_already_primary(self):
        app = SimpleNamespace(db=_SettingsDB({
            "ai_fallback_enabled": "1",
            "ai_fallback_openrouter_free": "1",
        }))
        with patch.object(
            resilient_ai,
            "active_ai_config",
            return_value=("openrouter", "sk-or-v1-primary", "openrouter/free"),
        ):
            candidates = resilient_ai.configured_ai_candidates(app)
        self.assertEqual(candidates, [("openrouter", "sk-or-v1-primary", "openrouter/free", "primary")])

    def test_retry_exhaustion_falls_through_to_openrouter_free_route(self):
        app = SimpleNamespace(db=_SettingsDB({"ai_retry_attempts": "3"}))
        dialog = _Dialog()
        candidates = [
            ("openrouter", "key-1", "model-1", "primary"),
            ("openrouter", "key-1", "openrouter/free", "openrouter-free-router"),
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

    def test_ai_resilience_settings_are_pack_managed_and_openrouter_only(self):
        source = (ROOT / "app" / "phase49_3i35_resilient_ai.py").read_text(encoding="utf-8")
        self.assertIn('panel.pack(fill="x", padx=8, pady=8)', source)
        self.assertNotIn('panel.grid(row=50, column=0, columnspan=2', source)
        self.assertIn("پایداری AI محصول — فقط OpenRouter", source)
        self.assertIn('self.db.set_setting("ai_fallback_order", "openrouter")', source)
        self.assertIn("AvalAI / Google / OpenAI در این مسیر استفاده نمی‌شوند", source)

    def test_operator_ledger_skips_obsolete_listbox_actions_when_modern_picker_is_installed(self):
        class DummyWorkspace:
            def __init__(self, *args, **kwargs):
                pass

            def reload(self):
                return None

            def save(self, silent=False):
                return True

        install_workspace(DummyWorkspace)
        workspace = SimpleNamespace(_epic49_materials_box=object())
        with patch("app.phase49_3i35_operator_ledger.ttk.Frame") as frame:
            DummyWorkspace._phase49_3i35_build_material_actions(workspace)
        frame.assert_not_called()

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
        from app.version import APP_VERSION
        self.assertEqual(manifest["version"], APP_VERSION)
        for path in (
            "app/phase49_3i35_operator_ledger.py",
            "app/phase49_3i35_resilient_ai.py",
            "app/phase49_3i35_readiness_review.py",
        ):
            self.assertIn(path, manifest["files"])


if __name__ == "__main__":
    unittest.main()
