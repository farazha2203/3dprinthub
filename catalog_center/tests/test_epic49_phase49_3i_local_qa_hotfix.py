from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Phase493ILocalQAHotfixContractTests(unittest.TestCase):
    def test_ai_first_paint_yields_before_existing_flow(self):
        source = (ROOT / "app" / "phase49_3i_local_qa_hotfix.py").read_text(encoding="utf-8")
        self.assertIn("STARTUP_DELAY_MS = 80", source)
        self.assertIn("self._phase49_3i_show_ai_startup(scope)", source)
        self.assertIn("self.after(STARTUP_DELAY_MS, invoke_existing_flow)", source)
        self.assertIn("original_run_ai(self, scope)", source)

    def test_hotfix_hands_off_to_existing_49_3h_progress_class(self):
        source = (ROOT / "app" / "phase49_3i_local_qa_hotfix.py").read_text(encoding="utf-8")
        self.assertIn("BaseProgress = phase49_3f_workspace_module.AIProgress", source)
        self.assertIn("class AIProgressHandoff(BaseProgress)", source)
        self.assertIn("phase49_3f_workspace_module.AIProgress = AIProgressHandoff", source)
        self.assertNotIn("AIContentService", source)
        self.assertNotIn("probe_connection", source)

    def test_no_second_ai_network_worker_is_created(self):
        source = (ROOT / "app" / "phase49_3i_local_qa_hotfix.py").read_text(encoding="utf-8")
        self.assertNotIn("threading.Thread", source)
        self.assertNotIn("enrich_product", source)
        self.assertIn("_phase49_3i_ai_starting", source)

    def test_launch_composes_hotfix_after_49_3h_execution(self):
        launch = (ROOT / "launch.py").read_text(encoding="utf-8")
        import_token = "from app.phase49_3i_local_qa_hotfix import install as install_phase49_3i_local_qa_hotfix"
        self.assertIn(import_token, launch)
        execution = launch.index("install_phase49_3h_execution_workspace(ProductWorkspace)")
        hotfix = launch.index("install_phase49_3i_local_qa_hotfix(ProductWorkspace, phase49_3f_workspace_module)")
        pricing = launch.index("install_phase49_3i_pricing_workspace(ProductWorkspace)")
        self.assertLess(execution, hotfix)
        self.assertLess(hotfix, pricing)


if __name__ == "__main__":
    unittest.main()
