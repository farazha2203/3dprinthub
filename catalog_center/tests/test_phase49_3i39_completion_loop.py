from __future__ import annotations

import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.phase49_3i39_professional_commerce import pricing_summary_range
from app.phase49_3i39_completion_loop import (
    _claim_ai_runtime,
    _done_message,
    _refresh_workspace_after_ai,
    _release_ai_runtime,
    confirm_current_stage,
    defect_snapshot,
    repair_until_stable,
)


ROOT = Path(__file__).resolve().parents[1]


class _DB:
    def __init__(self, row=None):
        self.row = row or {"operator_stage_locks_json": "{}"}

    def product(self, _product_id):
        return self.row


class _Dialog:
    def __init__(self):
        self.cancelled = threading.Event()
        self.events = []
        self.progress = []

    def event(self, stage, message, payload=None):
        self.events.append((stage, message, payload))

    def set_progress(self, value, message):
        self.progress.append((value, message))


def _snapshot(content_missing=None, operator=None, quick_missing=None):
    content_missing = list(content_missing or [])
    quick_missing = list(quick_missing or [])
    operator = dict(operator or {})
    data = {
        "quick": quick_missing,
        "commerce": operator.get("commerce", []),
        "images": [],
        "content": content_missing,
        "specs": operator.get("specs", []),
        "slider": [],
        "publish": operator.get("publish", []),
    }
    ai_fixable = {}
    if quick_missing:
        ai_fixable["quick"] = quick_missing
    if content_missing:
        ai_fixable["content"] = content_missing
    return {
        "state": {},
        "data_missing": data,
        "ai_fixable": ai_fixable,
        "operator_only": operator,
        "ai_fixable_flat": [
            f"{stage}:{item}"
            for stage, items in ai_fixable.items()
            for item in items
        ],
        "operator_only_flat": [],
        "finalization_pending": [],
        "total_data_defects": sum(len(v) for v in data.values()),
        "ai_fixable_count": sum(len(v) for v in ai_fixable.values()),
        "operator_only_count": sum(len(v) for v in operator.values()),
    }


class Phase493I39CompletionLoopTests(unittest.TestCase):
    def test_defect_snapshot_separates_ai_data_from_operator_and_finalization(self):
        fake_state = {
            "stages": {
                "quick": {"missing_data": ["عنوان فارسی", "گروه سایت"]},
                "commerce": {"missing_data": ["حداقل یک پروفایل فروش ثبت‌شده"]},
                "images": {"missing_data": []},
                "content": {"missing_data": ["SEO Title فارسی", "SEO Description فارسی"]},
                "specs": {"missing_data": ["مجوز تجاری مجاز"]},
                "slider": {"missing_data": []},
                "publish": {"missing_data": ["تأیید برای فروش"]},
            }
        }
        app = SimpleNamespace(db=_DB())
        with patch(
            "app.phase49_3i39_completion_loop.readiness_module.evaluate_readiness",
            return_value=fake_state,
        ):
            result = defect_snapshot(app, 1)

        self.assertEqual(result["ai_fixable"]["quick"], ["عنوان فارسی"])
        self.assertEqual(
            result["ai_fixable"]["content"],
            ["SEO Title فارسی", "SEO Description فارسی"],
        )
        self.assertIn("گروه سایت", result["operator_only"]["quick"])
        self.assertIn("مجوز تجاری مجاز", result["operator_only"]["specs"])
        self.assertIn("تأیید برای فروش", result["operator_only"]["publish"])
        self.assertNotIn("تأیید نهایی اپراتور (ثبت مرحله)", result["ai_fixable_flat"])

    def test_repair_loop_rechecks_readiness_and_only_reaches_100_after_after_state(self):
        before = _snapshot(["SEO Title فارسی", "SEO Description فارسی"])
        after = _snapshot([])
        app = SimpleNamespace(db=_DB())
        dialog = _Dialog()

        with patch(
            "app.phase49_3i39_completion_loop.defect_snapshot",
            side_effect=[before, before, before, after, after],
        ), patch(
            "app.phase49_3i39_completion_loop.run_resilient_orchestrator",
            return_value={"changed_fields": ["seo_title_fa", "seo_description_fa"]},
        ) as runner:
            result = repair_until_stable(
                app,
                10,
                dialog,
                mode="data",
                max_passes=3,
            )

        self.assertEqual(result["final"]["ai_fixable_count"], 0)
        self.assertEqual(len(result["fixed_defects"]), 2)
        runner.assert_called_once()
        kwargs = runner.call_args.kwargs
        self.assertEqual(kwargs["target_stages"], {"content"})
        self.assertFalse(kwargs["finalize_progress"])
        self.assertEqual(dialog.progress[-1][0], 100)
        stages = [item[0] for item in dialog.events]
        self.assertIn("readiness_before", stages)
        self.assertIn("repair_pass_result", stages)
        self.assertIn("readiness_after", stages)

    def test_stage_scoped_repair_ignores_defects_owned_by_other_stages(self):
        before = _snapshot(
            ["SEO Title فارسی", "SEO Description فارسی"],
            quick_missing=["عنوان فارسی"],
        )
        after = _snapshot(
            ["SEO Title فارسی", "SEO Description فارسی"],
            quick_missing=[],
        )
        app = SimpleNamespace(db=_DB())
        dialog = _Dialog()

        with patch(
            "app.phase49_3i39_completion_loop.defect_snapshot",
            side_effect=[before, before, before, after, after],
        ), patch(
            "app.phase49_3i39_completion_loop.run_resilient_orchestrator",
            return_value={"changed_fields": ["title_fa"]},
        ) as runner:
            result = repair_until_stable(
                app,
                63,
                dialog,
                mode="data",
                target_stages={"quick"},
                refresh_existing=False,
                max_passes=3,
            )

        runner.assert_called_once()
        self.assertEqual(result["scoped_ai_fixable_count"], 0)
        self.assertEqual(result["final"]["ai_fixable_count"], 2)
        self.assertEqual(result["target_stages"], ["quick"])
        self.assertIn("این مرحله", _done_message(result))
        messages = [message for code, message, _payload in dialog.events if code == "repair_pass_result"]
        self.assertTrue(any("0 نقص AI-قابل‌اصلاح در Scope باقی" in message for message in messages))

    def test_post_ai_refresh_rehydrates_db_and_leaves_final_readiness_as_last_painter(self):
        calls = []

        class Workspace:
            product_id = 63

            def __init__(self):
                self.db = _DB({"id": 63, "title_fa": "گکو انعطاف‌پذیر"})
                self.row = None

            def reload(self):
                calls.append("reload")

            def _phase49_3i36_refresh_locks(self):
                calls.append("locks")

            def _phase49_3b_refresh_wizard(self):
                calls.append("wizard")

            def _phase49_refresh_readiness(self):
                calls.append("readiness")

        workspace = Workspace()
        _refresh_workspace_after_ai(workspace, reload_first=True)

        self.assertEqual(workspace.row["title_fa"], "گکو انعطاف‌پذیر")
        self.assertEqual(calls[0], "reload")
        self.assertEqual(calls[1:4], ["locks", "wizard", "readiness"])
        self.assertEqual(calls[-1], "readiness")

    def test_visible_confirm_finalizes_current_stage_before_advancing(self):
        calls = []

        class Workspace:
            def _phase49_3b_current_key(self, default="quick"):
                return "quick"

            def _phase49_3i36_finalize_stage(self, stage):
                calls.append(("finalize", stage))
                return True

            def _phase49_3b_refresh_wizard(self):
                calls.append(("refresh", None))

            def select_section(self, stage):
                calls.append(("select", stage))

        self.assertTrue(confirm_current_stage(Workspace()))
        self.assertEqual(
            calls,
            [
                ("finalize", "quick"),
                ("refresh", None),
                ("select", "commerce"),
            ],
        )

    def test_product_ai_runtime_lock_blocks_second_workspace(self):
        app = SimpleNamespace()
        first = SimpleNamespace(app=app, product_id=63)
        second = SimpleNamespace(app=app, product_id=295)
        token = _claim_ai_runtime(first, "quick")
        self.assertIsNotNone(token)
        self.assertIsNone(_claim_ai_runtime(second, "content"))
        _release_ai_runtime(first, token)
        second_token = _claim_ai_runtime(second, "content")
        self.assertIsNotNone(second_token)
        _release_ai_runtime(second, second_token)

    def test_operator_only_defects_do_not_spend_an_ai_request(self):
        snapshot = _snapshot([], {
            "commerce": ["حداقل یک پروفایل فروش ثبت‌شده"],
            "specs": ["مجوز تجاری مجاز"],
            "publish": ["تأیید برای فروش"],
        })
        app = SimpleNamespace(db=_DB())
        dialog = _Dialog()
        with patch(
            "app.phase49_3i39_completion_loop.defect_snapshot",
            return_value=snapshot,
        ), patch(
            "app.phase49_3i39_completion_loop.run_resilient_orchestrator",
            side_effect=AssertionError("AI provider must not be called"),
        ):
            result = repair_until_stable(app, 1, dialog, mode="data")
        self.assertEqual(result["final"]["ai_fixable_count"], 0)
        self.assertEqual(result["final"]["operator_only_count"], 3)
        self.assertEqual(dialog.progress[-1][0], 100)

    def test_live_pricing_summary_restores_exact_final_amount_for_formula_and_fixed_modes(self):
        filament = {
            "manufacturer": "Bambu Lab",
            "brand": "Bambu Lab",
            "material": "PLA",
            "color": "White",
            "roll_weight_grams": 1000,
            "sale_price_per_roll": 3_000_000,
            "print_hourly_rate": 120_000,
            "supervision_hourly_rate": 60_000,
            "preheat_hours": 2,
            "preheat_hourly_rate": 20_000,
        }
        production = [{
            "weight_grams": 100,
            "support_weight_grams": 10,
            "print_time_minutes": 60,
        }]
        dynamic = pricing_summary_range(
            [filament],
            production,
            "dynamic",
            support_multiplier=2,
            assembly_fee=50_000,
        )
        self.assertEqual(dynamic["min"], 630_000)
        self.assertEqual(dynamic["max"], 630_000)
        self.assertEqual(dynamic["count"], 1)

        fixed = pricing_summary_range(
            [
                {**filament, "fixed_product_price": 900_000},
                {**filament, "brand": "eSUN", "fixed_product_price": 950_000},
                {**filament, "brand": "Generic", "fixed_product_price": 0},
            ],
            production,
            "fixed",
        )
        self.assertEqual(fixed["min"], 900_000)
        self.assertEqual(fixed["max"], 950_000)
        self.assertEqual(fixed["count"], 2)
        self.assertEqual(fixed["incomplete"], 1)

    def test_operator_buttons_say_filament_not_offer(self):
        commerce = (ROOT / "app" / "phase49_3i39_professional_commerce.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("＋ تعریف Filament جدید", commerce)
        self.assertIn("✏ ویرایش Filament انتخابی", commerce)
        self.assertIn("✓ ثبت Filamentهای انتخابی روی محصول", commerce)
        self.assertIn("مبلغ نهایی محاسباتی", commerce)
        self.assertNotIn("＋ تعریف Offer جدید", commerce)

    def test_final_composition_keeps_historical_stage_layout_and_dedicated_confirm(self):
        source = (ROOT / "app" / "phase49_3i39_completion_loop.py").read_text(
            encoding="utf-8"
        )
        ownership = (ROOT / "app" / "phase49_3i36_stage_finalization.py").read_text(
            encoding="utf-8"
        )
        commerce = (ROOT / "app" / "phase49_3i39_professional_commerce.py").read_text(
            encoding="utf-8"
        )
        content = (ROOT / "app" / "epic49_product_studio.py").read_text(
            encoding="utf-8"
        )

        init_start = source.index("    def __init__(self, app, product_id):")
        init_end = source.index("\n    def add_quick_identity_panel", init_start)
        init_block = source[init_start:init_end]
        self.assertNotIn("_phase49_3i39_add_quick_identity_panel()", init_block)
        self.assertNotIn("_phase49_3i39_add_specs_contract_panel()", init_block)

        self.assertIn('"product_type", "dimensions", "use_case_class"', ownership)
        for token in ("ثبت Filamentهای انتخابی روی محصول", "قیمت‌گذاری", "وزن", "پروفایل"):
            self.assertIn(token, commerce)
        for token in ("SEO Title فارسی", "SEO Description فارسی", "کلمات کلیدی سایت"):
            self.assertIn(token, content)

        self.assertIn("✅ ثبت و تأیید مرحله →", source)
        self.assertIn("legacy_next.pack_forget()", source)
        self.assertIn("ترجمه فقط عنوان فارسی", source)
        self.assertIn('self._phase49_3i39_run_stage_ai("quick")', source)

    def test_single_bulk_and_stage_repair_share_one_engine(self):
        source = (ROOT / "app" / "phase49_3i39_completion_loop.py").read_text(encoding="utf-8")
        core = (ROOT / "app" / "phase49_3i37_seven_stage_ai.py").read_text(encoding="utf-8")
        self.assertIn("repair_until_stable(", source)
        self.assertIn('target_stages={"content"}', source)
        self.assertIn("run_resilient_orchestrator(", source)
        self.assertNotIn("AIProviderClient(", source)
        self.assertIn('"request_payload"', core)
        self.assertIn('"response_payload"', core)
        self.assertIn("finalize_progress", core)
        self.assertIn("workspace_class._phase49_3e_run_all_ai = run_all", source)
        self.assertIn("workspace_class._phase49_3i31_smart_ai = run_link_all", source)
        self.assertIn("workspace_class._phase49_3c_stage_ai = run_current_stage", source)
        self.assertIn("✅ ثبت و تأیید مرحله →", source)
        self.assertIn("✨ پرکردن ناقص‌ها با AI", source)
        self.assertIn("پیشنهاد AI برای موارد ناقص", source)
        self.assertIn("انجام وظایف ناقص AI", source)
        self.assertIn("root = self", source)
        self.assertIn("_phase49_3i39_bind_footer_refresh", source)
        self.assertIn("_phase49_3i39_sync_footer_actions", source)
        self.assertIn('state="normal"', source)
        self.assertIn("lambda message=error_text", source)
        self.assertIn("legacy_next.pack_forget()", source)
        self.assertIn("_phase49_3i39_footer_confirm", source)
        self.assertIn("self.after_idle(self._phase49_3i39_sync_footer_actions)", source)
        self.assertIn("_claim_ai_runtime", source)


if __name__ == "__main__":
    unittest.main()
