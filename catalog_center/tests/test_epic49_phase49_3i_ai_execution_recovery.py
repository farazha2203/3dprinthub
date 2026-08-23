from __future__ import annotations

import types
import unittest
from pathlib import Path
from unittest.mock import patch

from app.phase49_3i_ai_execution_recovery import AI_TOTAL_WATCHDOG_MS, install


class _BaseProgress:
    pass


class _WorkspaceBase:
    def __init__(self):
        self.calls = []
        self.product_id = 99
        self._phase49_3i8_active_generation = 2
        self.current_stage = "content"

    def _phase49_3c_all_ai(self):
        self.calls.append(("legacy_all", None))
        return "legacy-all"

    def _phase49_3c_stage_ai(self):
        self.calls.append(("legacy_stage", self.current_stage))
        return "legacy-stage"

    def _phase49_3e_run_ai(self, scope):
        self.calls.append(("task_center", scope))
        return scope

    def _phase49_3b_current_key(self, default="quick"):
        return self.current_stage or default

    def _phase49_3f_apply_full_ai(self, *args):
        self.calls.append(("apply_full", args[1]))
        return "applied-full"

    def _phase49_3f_apply_selected_image_ai(self, *args):
        self.calls.append(("apply_images", len(args[1])))
        return "applied-images"


class Phase493IAIExecutionRecoveryTests(unittest.TestCase):
    def _class(self):
        class Workspace(_WorkspaceBase):
            pass

        module = types.SimpleNamespace(AIProgress=_BaseProgress)
        install(Workspace, module)
        return Workspace, module

    def test_all_fields_button_routes_to_mature_task_center(self):
        Workspace, _module = self._class()
        workspace = Workspace()
        with patch("app.phase49_3i_ai_execution_recovery.runtime_trace.event"):
            result = workspace._phase49_3c_all_ai()
        self.assertEqual(result, "all")
        self.assertIn(("task_center", "all"), workspace.calls)
        self.assertNotIn(("legacy_all", None), workspace.calls)

    def test_non_quick_stage_routes_to_task_center_and_images_keep_image_scope(self):
        Workspace, _module = self._class()
        workspace = Workspace()
        workspace.current_stage = "images"
        self.assertEqual(workspace._phase49_3c_stage_ai(), "images")
        workspace.current_stage = "content"
        self.assertEqual(workspace._phase49_3c_stage_ai(), "all")
        self.assertEqual(
            [item for item in workspace.calls if item[0] == "task_center"],
            [("task_center", "images"), ("task_center", "all")],
        )

    def test_quick_stage_preserves_mature_title_only_path(self):
        Workspace, _module = self._class()
        workspace = Workspace()
        workspace.current_stage = "quick"
        self.assertEqual(workspace._phase49_3c_stage_ai(), "legacy-stage")
        self.assertIn(("legacy_stage", "quick"), workspace.calls)

    def test_stale_or_cancelled_full_result_cannot_mutate_product(self):
        Workspace, _module = self._class()
        workspace = Workspace()
        stale = types.SimpleNamespace(_phase49_3i8_generation=1, _phase49_3i8_cancelled=False)
        current = types.SimpleNamespace(_phase49_3i8_generation=2, _phase49_3i8_cancelled=False)
        with patch("app.phase49_3i_ai_execution_recovery.runtime_trace.event"):
            self.assertIsNone(workspace._phase49_3f_apply_full_ai({}, "all", stale, "avalai", "model", 0))
            self.assertEqual(workspace._phase49_3f_apply_full_ai({}, "all", current, "avalai", "model", 0), "applied-full")
        self.assertEqual([item for item in workspace.calls if item[0] == "apply_full"], [("apply_full", "all")])

    def test_stale_image_result_is_discarded_too(self):
        Workspace, _module = self._class()
        workspace = Workspace()
        stale = types.SimpleNamespace(_phase49_3i8_generation=1, _phase49_3i8_cancelled=True)
        with patch("app.phase49_3i_ai_execution_recovery.runtime_trace.event"):
            self.assertIsNone(workspace._phase49_3f_apply_selected_image_ai({}, ["a"], stale, "avalai", "model", 0))
        self.assertFalse(any(item[0] == "apply_images" for item in workspace.calls))

    def test_watchdog_matches_existing_single_request_upper_bound(self):
        self.assertEqual(AI_TOTAL_WATCHDOG_MS, 210_000)

    def test_recovery_adds_observable_controls_without_new_network_worker(self):
        source = (Path(__file__).resolve().parents[1] / "app" / "phase49_3i_ai_execution_recovery.py").read_text(encoding="utf-8")
        self.assertIn("توقف انتظار", source)
        self.assertIn("زمان سپری‌شده", source)
        self.assertIn("stale-full-result-discarded", source)
        self.assertNotIn("threading.Thread", source)
        self.assertNotIn("AIContentService", source)
        self.assertNotIn("enrich_product(", source)

    def test_active_local_qa_boundary_composes_both_runtime_recoveries(self):
        root = Path(__file__).resolve().parents[1]
        hotfix = (root / "app" / "phase49_3i_local_qa_hotfix.py").read_text(encoding="utf-8")
        launch = (root / "launch.py").read_text(encoding="utf-8")
        self.assertIn("install_preview_recovery()", hotfix)
        self.assertIn("install_ai_execution_recovery(workspace_class, phase49_3f_workspace_module)", hotfix)
        self.assertIn("install_phase49_3i_local_qa_hotfix(ProductWorkspace, phase49_3f_workspace_module)", launch)
        self.assertLess(
            hotfix.index("workspace_class._phase49_3i_ai_first_paint_installed = True"),
            hotfix.index("install_ai_execution_recovery(workspace_class, phase49_3f_workspace_module)"),
        )


if __name__ == "__main__":
    unittest.main()
