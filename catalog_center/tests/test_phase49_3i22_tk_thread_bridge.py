from __future__ import annotations

import threading
import unittest
from pathlib import Path

from app.phase49_3i22_tk_thread_bridge import TOKEN_PREFIX, install, is_main_ui_thread


class FakeWorkspace:
    def __init__(self, app, product_id):
        self.app = app
        self.product_id = product_id
        self.scheduled = []
        self.cancelled = []
        self.callback_errors = []

    def after(self, ms, func=None, *args):
        token = f"native:{len(self.scheduled) + 1}"
        self.scheduled.append((token, ms, func, args))
        return token

    def after_cancel(self, ident):
        self.cancelled.append(ident)

    def _source_for_ai(self):
        return {"source_title": "Cake Stand", "source_url": "https://example.test/product"}

    def report_callback_exception(self, exc_type, exc_value, exc_traceback):
        self.callback_errors.append((exc_type, exc_value))


class Phase493I22ThreadBridgeTests(unittest.TestCase):
    def test_main_thread_detection(self):
        self.assertTrue(is_main_ui_thread(threading.get_ident()))
        self.assertFalse(is_main_ui_thread(None))

    def test_worker_after_never_calls_native_tk_after(self):
        class Workspace(FakeWorkspace):
            pass

        install(Workspace)
        ws = Workspace(object(), 12)
        native_before = len(ws.scheduled)
        result = []

        def worker():
            token = ws.after(0, lambda: result.append("done"))
            result.append(token)

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        self.assertEqual(len(ws.scheduled), native_before)
        self.assertTrue(str(result[0]).startswith(TOKEN_PREFIX))

        # Execute the already-main-thread-scheduled pump manually.
        _token, _ms, pump, args = ws.scheduled[0]
        pump(*args)
        self.assertIn("done", result)

    def test_off_thread_source_uses_main_thread_snapshot(self):
        class Workspace(FakeWorkspace):
            pass

        install(Workspace)
        ws = Workspace(object(), 13)
        main_value = ws._source_for_ai()
        worker_values = []

        thread = threading.Thread(target=lambda: worker_values.append(ws._source_for_ai()))
        thread.start()
        thread.join(timeout=2)
        self.assertEqual(worker_values[0], main_value)
        self.assertIsNot(worker_values[0], main_value)

    def test_product_workspace_has_real_scrollable_stage_rail(self):
        source = Path(__file__).resolve().parents[1] / "app" / "product_workspace_v87.py"
        text = source.read_text(encoding="utf-8")
        self.assertIn("rail_canvas = tk.Canvas", text)
        self.assertIn("ttk.Scrollbar(rail_host, orient=\"vertical\"", text)
        self.assertIn("scrollregion=rail_canvas.bbox(\"all\")", text)
        self.assertIn("self._workspace_rail_scrollbar", text)


if __name__ == "__main__":
    unittest.main()
