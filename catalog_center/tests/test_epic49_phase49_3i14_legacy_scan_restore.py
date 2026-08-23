from __future__ import annotations

import unittest

from app.phase49_3i14_legacy_scan_restore import (
    LEGACY_ACTION_TEXTS,
    _resolve_legacy_start_scan,
    install_app,
)


class _Var:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class _DB:
    def source(self, code):
        if code != "makerworld":
            return None
        return {
            "model_url_pattern": r"https?://(?:www\.)?makerworld\.com/(?:[a-z]{2}/)?models/(?P<external_id>\d+)[^\s\"'<>]*"
        }


class _BaseApp:
    def start_scan(self):
        self.calls.append(("legacy", self.mode_var.get(), self.method_var.get()))
        self.scan_running = True
        return "legacy-started"


class _App87(_BaseApp):
    def __init__(self):
        self.calls = []
        self.scan_running = False
        self.source_map = {"MakerWorld": "makerworld"}
        self.source_var = _Var("MakerWorld")
        self.seed_var = _Var("https://makerworld.com/en/models/400767-3-tier-cake-stand?from=search#profileId-302300")
        self.mode_var = _Var("automatic")
        self.method_var = _Var("auto")
        self.db = _DB()
        self._phase49_3i12_run_token = 0
        self._phase49_3i12_elapsed = _Var("")
        self.state_calls = []
        self.after_calls = []

    # This mimics the 49.3I Preview override that shadowed BaseApp.start_scan.
    def start_scan(self):
        self.calls.append(("preview", self.mode_var.get(), self.method_var.get()))
        return "preview-started"

    def _mount_phase49_3i12_operator_ui(self):
        return "mounted"

    def _phase49_3i12_set_state(self, *args):
        self.state_calls.append(args)

    def _phase49_3i12_monitor_run(self, token):
        self.state_calls.append(("monitor", token))

    def after(self, delay, callback):
        self.after_calls.append((delay, callback))
        return len(self.after_calls)


class Phase493I14LegacyScanRestoreTests(unittest.TestCase):
    def test_resolves_base_mature_scan_not_preview_override(self):
        resolved = _resolve_legacy_start_scan(_App87)
        self.assertIs(resolved, _BaseApp.__dict__["start_scan"])

    def test_single_product_uses_mature_legacy_scan_route(self):
        class App(_App87):
            pass

        install_app(App)
        app = App()
        result = app.start_single_product_manual()

        self.assertEqual(result, "legacy-started")
        self.assertEqual(app.mode_var.get(), "single")
        self.assertEqual(app.method_var.get(), "auto")
        self.assertEqual(app.calls, [("legacy", "single", "auto")])
        self.assertTrue(app.scan_running)

    def test_legacy_operator_actions_are_preserved_contract(self):
        self.assertIn("شروع اسکن", LEGACY_ACTION_TEXTS)
        self.assertIn("توقف محترمانه", LEGACY_ACTION_TEXTS)
        self.assertIn("دریافت هوشمند از لینک", LEGACY_ACTION_TEXTS)
        self.assertIn("🔎 کشف جدیدها", LEGACY_ACTION_TEXTS)


if __name__ == "__main__":
    unittest.main()
