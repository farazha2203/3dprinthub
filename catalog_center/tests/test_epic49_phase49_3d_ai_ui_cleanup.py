from __future__ import annotations

import unittest
from pathlib import Path


class Phase493DAIUiCleanupContractTests(unittest.TestCase):
    def test_legacy_activation_path_is_hidden_and_radio_save_is_canonical(self):
        root = Path(__file__).resolve().parents[1]
        cleanup = (root / "app" / "phase49_3d_ai_ui_cleanup.py").read_text(encoding="utf-8")
        hardening = (root / "app" / "phase49_3d_workflow_hardening.py").read_text(encoding="utf-8")
        launch = (root / "launch.py").read_text(encoding="utf-8")

        self.assertIn('LEGACY_ACTIVATE_TEXT = "فعال کن"', cleanup)
        self.assertIn("pack_forget", cleanup)
        self.assertIn("Provider فعال را با Radio انتخاب کن", cleanup)
        self.assertIn("ttk.Radiobutton", hardening)
        self.assertIn("ذخیره Provider و مدل فعال", hardening)
        self.assertIn("install_phase49_3d_ai_ui_cleanup(App87)", launch)
        self.assertIn("EPIC49_3D_AI_LEGACY_ACTIVATE_REMOVED=ENABLED", launch)


if __name__ == "__main__":
    unittest.main()
