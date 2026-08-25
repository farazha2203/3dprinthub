from __future__ import annotations

import copy
import heapq
import itertools
import threading
import time
from typing import Any, Callable

from .phase49_diagnostics import audit_event


PHASE = "49.3I.22"
PUMP_INTERVAL_MS = 25
TOKEN_PREFIX = "phase49_3i22:"


def is_main_ui_thread(main_thread_id: int | None) -> bool:
    return bool(main_thread_id and threading.get_ident() == int(main_thread_id))


def install(workspace_class) -> None:
    """Keep every Tk call on the Tk/main thread.

    Several mature AI workers correctly move network work to daemon threads but
    historically used ``workspace.after(...)`` from those worker threads to hand
    results back to Tk. Tkinter can block while marshalling such cross-thread Tcl
    calls, especially while another modal/progress window is active. This bridge
    turns off-main ``after`` calls into plain Python heap entries. A pump that was
    itself scheduled by the main thread drains the heap and invokes callbacks on
    Tk's owning thread.

    The wrapper is deliberately installed at the final Product Workspace
    composition boundary so it also protects older AI entry points without
    rewriting each mature workflow.
    """

    if getattr(workspace_class, "_phase49_3i22_tk_thread_bridge_installed", False):
        return

    original_init = workspace_class.__init__
    original_after = workspace_class.after
    original_after_cancel = workspace_class.after_cancel
    original_source_for_ai = getattr(workspace_class, "_source_for_ai", None)
    original_link_refresh = getattr(workspace_class, "_phase49_3i21_link_refresh", None)

    def __init__(self, app, product_id):
        self._phase49_3i22_main_thread_id = threading.get_ident()
        self._phase49_3i22_heap: list[tuple[float, int, str, Callable, tuple[Any, ...]]] = []
        self._phase49_3i22_heap_lock = threading.RLock()
        self._phase49_3i22_cancelled_tokens: set[str] = set()
        self._phase49_3i22_counter = itertools.count(1)
        self._phase49_3i22_source_snapshot = None
        self._phase49_3i22_pump_id = None
        original_init(self, app, product_id)
        self._phase49_3i22_schedule_pump()
        audit_event(
            "ui",
            "tk_thread_bridge_ready",
            product_id=getattr(self, "product_id", None),
            source_file=__file__,
            message=f"main_thread={self._phase49_3i22_main_thread_id}",
        )

    def _schedule_pump(self):
        try:
            self._phase49_3i22_pump_id = original_after(
                self,
                PUMP_INTERVAL_MS,
                self._phase49_3i22_drain_ui_queue,
            )
        except Exception:
            self._phase49_3i22_pump_id = None

    def _drain_ui_queue(self):
        # This callback is created and rescheduled only from Tk's owning thread.
        if not is_main_ui_thread(getattr(self, "_phase49_3i22_main_thread_id", None)):
            return
        now = time.monotonic()
        ready: list[tuple[str, Callable, tuple[Any, ...]]] = []
        with self._phase49_3i22_heap_lock:
            while self._phase49_3i22_heap and self._phase49_3i22_heap[0][0] <= now:
                _due, _seq, token, callback, args = heapq.heappop(self._phase49_3i22_heap)
                if token in self._phase49_3i22_cancelled_tokens:
                    self._phase49_3i22_cancelled_tokens.discard(token)
                    continue
                ready.append((token, callback, args))
        for _token, callback, args in ready:
            try:
                callback(*args)
            except Exception as exc:
                try:
                    self.report_callback_exception(type(exc), exc, exc.__traceback__)
                except Exception:
                    audit_event(
                        "ui",
                        "deferred_callback_error",
                        status="error",
                        level="ERROR",
                        product_id=getattr(self, "product_id", None),
                        source_file=__file__,
                        message=str(exc),
                    )
        self._phase49_3i22_schedule_pump()

    def after(self, ms, func=None, *args):
        main_id = getattr(self, "_phase49_3i22_main_thread_id", None)
        if func is None or is_main_ui_thread(main_id):
            return original_after(self, ms, func, *args)

        # IMPORTANT: no Tk/Tcl call happens in this branch.
        try:
            delay_ms = max(0, int(ms or 0))
        except Exception:
            delay_ms = 0
        seq = next(self._phase49_3i22_counter)
        token = f"{TOKEN_PREFIX}{seq}"
        due = time.monotonic() + (delay_ms / 1000.0)
        with self._phase49_3i22_heap_lock:
            heapq.heappush(self._phase49_3i22_heap, (due, seq, token, func, args))
        return token

    def after_cancel(self, ident):
        token = str(ident or "")
        if token.startswith(TOKEN_PREFIX):
            with self._phase49_3i22_heap_lock:
                self._phase49_3i22_cancelled_tokens.add(token)
            return None
        return original_after_cancel(self, ident)

    def _source_for_ai(self):
        if not callable(original_source_for_ai):
            return {}
        main_id = getattr(self, "_phase49_3i22_main_thread_id", None)
        if not is_main_ui_thread(main_id):
            snapshot = getattr(self, "_phase49_3i22_source_snapshot", None)
            if snapshot is None:
                raise RuntimeError(
                    "AI worker requested Tk-backed source state off the UI thread before a safe snapshot existed."
                )
            return copy.deepcopy(snapshot)
        value = dict(original_source_for_ai(self) or {})
        self._phase49_3i22_source_snapshot = copy.deepcopy(value)
        return value

    def _link_refresh(self):
        # 49.3I.21 used _source_for_ai from its worker. Capture the Tk-backed
        # variables now on the main thread; the worker receives only a deep copy.
        if callable(original_source_for_ai):
            try:
                _source_for_ai(self)
            except Exception as exc:
                audit_event(
                    "ai_job",
                    "source_snapshot_error",
                    status="error",
                    level="ERROR",
                    product_id=getattr(self, "product_id", None),
                    source_file=__file__,
                    message=str(exc),
                )
                raise
        return original_link_refresh(self) if callable(original_link_refresh) else None

    workspace_class.__init__ = __init__
    workspace_class.after = after
    workspace_class.after_cancel = after_cancel
    workspace_class._phase49_3i22_schedule_pump = _schedule_pump
    workspace_class._phase49_3i22_drain_ui_queue = _drain_ui_queue
    if callable(original_source_for_ai):
        workspace_class._source_for_ai = _source_for_ai
    if callable(original_link_refresh):
        workspace_class._phase49_3i21_link_refresh = _link_refresh
    workspace_class._phase49_3i22_tk_thread_bridge_installed = True
