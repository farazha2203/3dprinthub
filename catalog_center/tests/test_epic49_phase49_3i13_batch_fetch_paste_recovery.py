from __future__ import annotations

import unittest
from pathlib import Path

from app.phase49_3i13_batch_fetch_paste_recovery import _first_clipboard_line, install_app


class Phase493I13BatchFetchPasteRecoveryTests(unittest.TestCase):
    def test_clipboard_uses_first_non_empty_line_without_damaging_query(self):
        value = "\r\n  https://makerworld.com/en/search/models?keyword=cake+stand  \r\nignored"
        self.assertEqual(
            _first_clipboard_line(value),
            "https://makerworld.com/en/search/models?keyword=cake+stand",
        )

    def test_approved_batch_forces_background_browser_then_restores_direct_setting(self):
        class FakeApp:
            def _mount_phase49_3i12_operator_ui(self):
                return None

            def approve_discovery_candidates(self):
                self.seen_headed = self.config["direct_link"]["headed"]
                self.scan_running = False
                return "ok"

            def _selected_candidate_ids(self):
                return [11, 12]

        install_app(FakeApp)
        app = FakeApp()
        app.config = {"direct_link": {"headed": True}}
        app.scan_running = False
        app.after = lambda *_args, **_kwargs: None
        result = app.approve_discovery_candidates()
        self.assertEqual(result, "ok")
        self.assertFalse(app.seen_headed)
        self.assertTrue(app.config["direct_link"]["headed"])
        self.assertFalse(app._phase49_3i13_batch_headless_active)

    def test_recovery_source_exposes_windows_paste_and_error_controls(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "app"
            / "phase49_3i13_batch_fetch_paste_recovery.py"
        ).read_text(encoding="utf-8")
        self.assertIn('entry.bind("<Control-v>"', source)
        self.assertIn('entry.bind("<Control-V>"', source)
        self.assertIn('entry.bind("<Shift-Insert>"', source)
        self.assertIn('entry.bind("<Button-3>"', source)
        self.assertIn('text="چسباندن لینک"', source)
        self.assertIn('text="جزئیات خطای انتخابی"', source)
        self.assertIn('direct_cfg["headed"] = False', source)
        self.assertIn("_phase49_3i13_restore_batch_browser_mode", source)
        self.assertNotIn("extract_direct_link(", source)
        self.assertNotIn("async_playwright", source)

    def test_runtime_bridge_installs_3i13_after_3i12_contract(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "app"
            / "phase49_3i12_runtime_bridge.py"
        ).read_text(encoding="utf-8")
        self.assertIn("_install_phase49_3i13_app", source)
        self.assertIn("app_class._phase49_3i12_runtime_bridge_installed = True", source)
        self.assertIn("_install_phase49_3i13_app(app_class)", source)


if __name__ == "__main__":
    unittest.main()
