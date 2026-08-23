from __future__ import annotations

import time
import tkinter as tk
from tkinter import ttk

from . import phase49_3f_runtime_trace as runtime_trace


AI_TOTAL_WATCHDOG_MS = 210_000
AI_HEARTBEAT_MS = 1_000


def _safe_exists(widget) -> bool:
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def _format_elapsed(seconds: float) -> str:
    value = max(0, int(seconds))
    return f"{value // 60:02d}:{value % 60:02d}"


def install(workspace_class, phase49_3f_workspace_module) -> None:
    """Recover the real operator AI buttons and make long waits observable.

    The old Phase49.3C bottom assistant still called ProductStudio.generate_ai(),
    bypassing the mature Phase49.3E/3F/3H task center and therefore bypassing the
    Phase49.3I first-paint progress handoff. Route those operator actions into the
    mature task center instead of creating another AI client.

    The progress wrapper adds an elapsed heartbeat, a bounded operator wait and
    stale-result protection. Cancelling/timing out cannot kill a blocking urllib
    worker safely, so the worker is allowed to finish in the background while its
    late result is explicitly prevented from mutating the product.
    """
    if getattr(workspace_class, "_phase49_3i8_ai_execution_recovery_installed", False):
        return

    original_all_ai = getattr(workspace_class, "_phase49_3c_all_ai", None)
    original_stage_ai = getattr(workspace_class, "_phase49_3c_stage_ai", None)
    original_apply_full = getattr(workspace_class, "_phase49_3f_apply_full_ai", None)
    original_apply_images = getattr(workspace_class, "_phase49_3f_apply_selected_image_ai", None)
    BaseProgress = phase49_3f_workspace_module.AIProgress

    class ObservableAIProgress(BaseProgress):
        def __init__(self, parent, title: str, product_id: int | None = None):
            super().__init__(parent, title, product_id)
            self._phase49_3i8_parent = parent
            self._phase49_3i8_started = time.monotonic()
            self._phase49_3i8_finished = False
            self._phase49_3i8_cancelled = False
            counter = int(getattr(parent, "_phase49_3i8_generation_counter", 0) or 0) + 1
            parent._phase49_3i8_generation_counter = counter
            parent._phase49_3i8_active_generation = counter
            self._phase49_3i8_generation = counter
            self._phase49_3i8_tick_id = None
            self._phase49_3i8_timeout_id = None
            self._phase49_3i8_elapsed_var = tk.StringVar(value="زمان سپری‌شده: 00:00 • سقف انتظار این عملیات: 03:30")
            self._phase49_3i8_add_controls()
            self._phase49_3i8_tick()
            try:
                self._phase49_3i8_timeout_id = parent.after(
                    AI_TOTAL_WATCHDOG_MS,
                    self._phase49_3i8_timeout,
                )
            except Exception:
                self._phase49_3i8_timeout_id = None

        def _phase49_3i8_add_controls(self):
            win = getattr(self, "win", None)
            if not _safe_exists(win):
                return
            try:
                controls = ttk.Frame(win, padding=(16, 0, 16, 10))
                controls.pack(side="bottom", fill="x")
                ttk.Label(
                    controls,
                    textvariable=self._phase49_3i8_elapsed_var,
                    style="SubHeader.TLabel",
                ).pack(side="left", fill="x", expand=True)
                self._phase49_3i8_cancel_button = ttk.Button(
                    controls,
                    text="توقف انتظار",
                    command=self._phase49_3i8_cancel,
                )
                self._phase49_3i8_cancel_button.pack(side="right", padx=(8, 0))
                win.update_idletasks()
                width = max(610, int(win.winfo_width() or 610))
                height = max(330, int(win.winfo_height() or 330))
                px = int(getattr(self._phase49_3i8_parent, "winfo_rootx", lambda: 0)())
                py = int(getattr(self._phase49_3i8_parent, "winfo_rooty", lambda: 0)())
                pw = int(getattr(self._phase49_3i8_parent, "winfo_width", lambda: width)() or width)
                ph = int(getattr(self._phase49_3i8_parent, "winfo_height", lambda: height)() or height)
                x = max(0, px + (pw - width) // 2)
                y = max(0, py + (ph - height) // 2)
                win.geometry(f"{width}x{height}+{x}+{y}")
                win.lift()
                try:
                    win.attributes("-topmost", True)
                    win.after(700, lambda: _safe_exists(win) and win.attributes("-topmost", False))
                except Exception:
                    pass
            except Exception:
                pass

        def _phase49_3i8_cancel_timers(self):
            parent = self._phase49_3i8_parent
            for attr in ("_phase49_3i8_tick_id", "_phase49_3i8_timeout_id"):
                ident = getattr(self, attr, None)
                if ident is not None:
                    try:
                        parent.after_cancel(ident)
                    except Exception:
                        pass
                    setattr(self, attr, None)

        def _phase49_3i8_tick(self):
            if self._phase49_3i8_finished:
                return
            elapsed = time.monotonic() - self._phase49_3i8_started
            try:
                self._phase49_3i8_elapsed_var.set(
                    f"زمان سپری‌شده: {_format_elapsed(elapsed)} • سقف انتظار این عملیات: 03:30"
                )
            except Exception:
                pass
            try:
                self._phase49_3i8_tick_id = self._phase49_3i8_parent.after(
                    AI_HEARTBEAT_MS,
                    self._phase49_3i8_tick,
                )
            except Exception:
                self._phase49_3i8_tick_id = None

        def _phase49_3i8_abort(self, message: str, *, reason: str):
            if self._phase49_3i8_finished:
                return
            self._phase49_3i8_finished = True
            self._phase49_3i8_cancelled = True
            self._phase49_3i8_cancel_timers()
            parent = self._phase49_3i8_parent
            if int(getattr(parent, "_phase49_3i8_active_generation", 0) or 0) == self._phase49_3i8_generation:
                parent._phase49_3i8_active_generation = 0
            try:
                if hasattr(self, "_phase49_3i8_cancel_button"):
                    self._phase49_3i8_cancel_button.configure(state="disabled")
            except Exception:
                pass
            runtime_trace.event(
                "ai",
                "phase49-3i8-execution-abort",
                status="error",
                product_id=getattr(parent, "product_id", None),
                message=message,
                detail={"reason": reason, "generation": self._phase49_3i8_generation},
            )
            try:
                BaseProgress.fail(self, message)
            except Exception:
                pass
            try:
                parent.footer_status.set(message)
            except Exception:
                pass

        def _phase49_3i8_cancel(self):
            self._phase49_3i8_abort(
                "انتظار توسط اپراتور متوقف شد. اگر پاسخ شبکه دیرتر برسد روی محصول اعمال نمی‌شود.",
                reason="operator_cancel",
            )

        def _phase49_3i8_timeout(self):
            self._phase49_3i8_timeout_id = None
            self._phase49_3i8_abort(
                "هوش مصنوعی تا سقف ۲۱۰ ثانیه نتیجه نداد. عملیات برای این محصول متوقف شد و هر پاسخ دیرهنگام نادیده گرفته می‌شود.",
                reason="watchdog_timeout",
            )

        def step(self, label: str, detail: str = ""):
            if self._phase49_3i8_finished:
                return
            return super().step(label, detail)

        def done(self, label="✅ عملیات کامل شد", detail=""):
            if self._phase49_3i8_finished:
                return
            self._phase49_3i8_finished = True
            self._phase49_3i8_cancel_timers()
            try:
                if hasattr(self, "_phase49_3i8_cancel_button"):
                    self._phase49_3i8_cancel_button.configure(state="disabled")
            except Exception:
                pass
            return super().done(label, detail)

        def fail(self, message: str):
            if self._phase49_3i8_finished:
                return
            self._phase49_3i8_finished = True
            self._phase49_3i8_cancel_timers()
            try:
                if hasattr(self, "_phase49_3i8_cancel_button"):
                    self._phase49_3i8_cancel_button.configure(state="disabled")
            except Exception:
                pass
            return super().fail(message)

        def close(self):
            self._phase49_3i8_cancel_timers()
            return super().close()

    phase49_3f_workspace_module.AIProgress = ObservableAIProgress

    def _phase49_3c_all_ai(self):
        if hasattr(self, "_phase49_3e_run_ai"):
            try:
                self.footer_status.set("تکمیل هوشمند از Task Center شروع شد؛ روند اتصال/ارسال/دریافت در پنجره پیشرفت نمایش داده می‌شود.")
            except Exception:
                pass
            return self._phase49_3e_run_ai("all")
        return original_all_ai(self) if callable(original_all_ai) else None

    def _phase49_3c_stage_ai(self):
        current = ""
        try:
            current = self._phase49_3b_current_key(default="quick")
        except Exception:
            current = ""
        if current == "quick":
            return original_stage_ai(self) if callable(original_stage_ai) else None
        if hasattr(self, "_phase49_3e_run_ai"):
            scope = "images" if current == "images" else "all"
            return self._phase49_3e_run_ai(scope)
        return original_stage_ai(self) if callable(original_stage_ai) else None

    def _progress_is_current(self, progress) -> bool:
        generation = getattr(progress, "_phase49_3i8_generation", None)
        if generation is None:
            return True
        active = int(getattr(self, "_phase49_3i8_active_generation", 0) or 0)
        return bool(not getattr(progress, "_phase49_3i8_cancelled", False) and int(generation) == active)

    def _phase49_3f_apply_full_ai(self, pack, scope, progress, provider, model, started):
        if not _progress_is_current(self, progress):
            runtime_trace.event(
                "ai",
                "phase49-3i8-stale-full-result-discarded",
                status="blocked",
                product_id=getattr(self, "product_id", None),
                provider=provider,
                model=model,
                detail={"scope": scope},
            )
            return None
        return original_apply_full(self, pack, scope, progress, provider, model, started) if callable(original_apply_full) else None

    def _phase49_3f_apply_selected_image_ai(self, pack, selected, progress, provider, model, started):
        if not _progress_is_current(self, progress):
            runtime_trace.event(
                "ai",
                "phase49-3i8-stale-image-result-discarded",
                status="blocked",
                product_id=getattr(self, "product_id", None),
                provider=provider,
                model=model,
                detail={"selected_count": len(selected or [])},
            )
            return None
        return original_apply_images(self, pack, selected, progress, provider, model, started) if callable(original_apply_images) else None

    workspace_class._phase49_3c_all_ai = _phase49_3c_all_ai
    workspace_class._phase49_3c_stage_ai = _phase49_3c_stage_ai
    workspace_class._phase49_3i8_progress_is_current = _progress_is_current
    if callable(original_apply_full):
        workspace_class._phase49_3f_apply_full_ai = _phase49_3f_apply_full_ai
    if callable(original_apply_images):
        workspace_class._phase49_3f_apply_selected_image_ai = _phase49_3f_apply_selected_image_ai
    workspace_class._phase49_3i8_ai_execution_recovery_installed = True
