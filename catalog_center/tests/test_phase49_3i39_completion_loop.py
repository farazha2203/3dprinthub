from __future__ import annotations

import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.phase49_3i39_completion_loop import (
    _refresh_workspace_after_ai,
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


def _snapshot(content_missing=None, operator=None):
    content_missing = list(content_missing or [])
    operator = dict(operator or {})
    data = {
        "quick": [],
        "commerce": operator.get("commerce", []),
        "images": [],
        "content": content_missing,
        "specs": operator.get("specs", []),
        "slider": [],
        "publish": operator.get("publish", []),
    }
    return {
        "state": {},
        "data_missing": data,
        "ai_fixable": {"content": content_missing} if content_missing else {},
        "operator_only": operator,
        "ai_fixable_flat": [f"content:{x}" for x in content_missing],
        "operator_only_flat": [],
        "finalization_pending": [],
        "total_data_defects": sum(len(v) for v in data.values()),
        "ai_fixable_count": len(content_missing),
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
        self.assertIn("✅ تأیید و مرحله بعد →", source)
        self.assertIn("✨ پرکردن ناقص‌ها با AI", source)
        self.assertIn("پیشنهاد AI برای موارد ناقص", source)
        self.assertIn("انجام وظایف ناقص AI", source)
        self.assertIn("root = self", source)
        self.assertIn("lambda message=error_text", source)


if __name__ == "__main__":
    unittest.main()
