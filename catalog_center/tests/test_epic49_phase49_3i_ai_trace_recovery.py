from __future__ import annotations

import unittest
from pathlib import Path

from app.phase49_3i_ai_trace_recovery import (
    TITLE_WATCHDOG_MS,
    _freeze_exception_callback,
    _snapshot,
    _validate_title,
)


ROOT = Path(__file__).resolve().parents[2]


class Phase493I10AITraceRecoveryTests(unittest.TestCase):
    def test_title_watchdog_is_bounded_below_general_210_second_ai_limit(self):
        self.assertEqual(TITLE_WATCHDOG_MS, 90_000)
        self.assertLess(TITLE_WATCHDOG_MS, 210_000)

    def test_specific_persian_title_is_accepted(self):
        title = _validate_title(
            "جا شمعی وارمر LED طرح کدو تنبل هالووین سامهین",
            "Halloween Samhain Pumpkin LED goth Tealight Holder",
        )
        self.assertIn("کدو", title)
        self.assertIn("هالووین", title)

    def test_generic_title_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "عنوان عمومی"):
            _validate_title("محصول چاپ سه بعدی", "Halloween Pumpkin Tealight Holder")

    def test_exception_callback_freezes_except_target_before_python_clears_it(self):
        frozen = None
        try:
            raise RuntimeError("provider failed")
        except Exception as exc:
            callback = lambda: str(exc)
            frozen = _freeze_exception_callback(callback)
        self.assertIsNotNone(frozen)
        self.assertEqual(frozen(), "provider failed")

    def test_trace_snapshot_redacts_secret_keys(self):
        payload = _snapshot({
            "api_key": "secret-value",
            "Authorization": "Bearer secret-token",
            "messages": [{"content": "normal product text"}],
        })
        self.assertEqual(payload["api_key"], "***REDACTED***")
        self.assertEqual(payload["Authorization"], "***REDACTED***")
        self.assertIn("normal product text", str(payload))
        self.assertNotIn("secret-value", str(payload))
        self.assertNotIn("secret-token", str(payload))

    def test_runtime_composition_installs_trace_recovery_after_refresh_completion(self):
        source = (ROOT / "catalog_center/app/phase49_3i_local_qa_hotfix.py").read_text(encoding="utf-8")
        refresh_pos = source.index("install_ai_refresh_completion(workspace_class, task_center_module)")
        trace_pos = source.index("install_ai_trace_recovery(workspace_class, phase49_3f_workspace_module)")
        self.assertLess(refresh_pos, trace_pos)

    def test_trace_ui_has_vertical_and_horizontal_scrollbars_and_request_response_tabs(self):
        source = (ROOT / "catalog_center/app/phase49_3i_ai_trace_recovery.py").read_text(encoding="utf-8")
        self.assertIn('("request", "ارسالی")', source)
        self.assertIn('("response", "دریافتی")', source)
        self.assertIn('("error", "خطا / Diagnostics")', source)
        self.assertIn('orient="vertical"', source)
        self.assertIn('orient="horizontal"', source)
        self.assertIn("append_request", source)
        self.assertIn("append_response", source)
        self.assertIn("append_error", source)

    def test_http_trace_does_not_log_api_key_argument(self):
        source = (ROOT / "catalog_center/app/phase49_3i_ai_trace_recovery.py").read_text(encoding="utf-8")
        request_block = source[source.index("def _trace_request"):source.index("def _trace_response")]
        self.assertNotIn("api_key", request_block)
        self.assertNotIn("Authorization", request_block)
        self.assertIn('"payload": _snapshot(payload or {})', request_block)

    def test_title_worker_uses_bound_error_text_not_late_exception_lambda(self):
        source = (ROOT / "catalog_center/app/phase49_3i_ai_trace_recovery.py").read_text(encoding="utf-8")
        self.assertIn('error_text = f"{type(exc).__name__}: {exc}"', source)
        self.assertIn("lambda error_text=error_text: apply_error(error_text)", source)
        self.assertNotIn("lambda: apply_error(str(exc))", source)

    def test_title_cancel_and_timeout_are_stale_safe(self):
        source = (ROOT / "catalog_center/app/phase49_3i_ai_trace_recovery.py").read_text(encoding="utf-8")
        self.assertIn("_phase49_3i10_title_active_generation", source)
        self.assertIn("phase49-3i10-title-stale-result-discarded", source)
        self.assertIn("title_watchdog_timeout", source)
        self.assertIn("operator_cancel", (ROOT / "catalog_center/app/phase49_3i_ai_execution_recovery.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
