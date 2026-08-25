from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.phase49_3i24_runtime_observability import _tail


class Phase493I24RuntimeObservabilityTests(unittest.TestCase):
    def test_runtime_tail_redacts_bearer_and_api_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.log"
            path.write_text(
                "Authorization: Bearer secret-token-123\napi_key=super-secret\nlast-line\n",
                encoding="utf-8",
            )
            value = _tail(path)
        self.assertNotIn("secret-token-123", value)
        self.assertNotIn("super-secret", value)
        self.assertIn("last-line", value)

    def test_runtime_module_contains_startup_no_network_and_hang_dump_contract(self):
        source = Path(__file__).resolve().parents[1] / "app" / "phase49_3i24_runtime_observability.py"
        text = source.read_text(encoding="utf-8")
        self.assertIn("_phase49_3i24_startup_guard", text)
        self.assertIn("blocked_hidden_model_scans", text)
        self.assertIn("faulthandler.dump_traceback", text)
        self.assertIn("ui_hang_detected", text)
        self.assertIn("ساخت گزارش امن برای GitHub", text)
        self.assertIn("catalog_runtime_session_tail", text)
        self.assertIn("catalog_hang_thread_dump_tail", text)

    def test_runtime_bridge_mounts_observability_on_real_app_shell(self):
        source = Path(__file__).resolve().parents[1] / "app" / "phase49_3i12_runtime_bridge.py"
        text = source.read_text(encoding="utf-8")
        self.assertIn("_install_phase49_3i24_runtime_observability", text)
        self.assertIn("_main_module.DATA", text)


if __name__ == "__main__":
    unittest.main()
