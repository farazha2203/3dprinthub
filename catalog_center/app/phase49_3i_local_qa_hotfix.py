from __future__ import annotations

import tkinter as tk
from tkinter import ttk


STARTUP_DELAY_MS = 80


def _safe_exists(widget) -> bool:
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def install(workspace_class, phase49_3f_workspace_module) -> None:
    """Make AI progress visible before legacy synchronous save/preflight work.

    The mature 49.3F/49.3H AI request, threading, provider/model, result drawer,
    cost ledger and error handling remain the source of truth. This hotfix only
    inserts a first-paint handoff before calling that existing workflow.

    Same-phase Windows QA recoveries are composed here because this installer is
    already the verified ProductWorkspace runtime boundary in launch.py. This
    keeps Preview recovery and the operator-AI bridge active without creating a
    second network/extraction implementation.
    """
    if getattr(workspace_class, "_phase49_3i_ai_first_paint_installed", False):
        return

    # The Preview patch is independent of ProductWorkspace, but must be installed
    # in the real runtime. The previous 49.3I.7 regression test exercised install()
    # directly while launch never invoked it, so Windows could still execute the
    # broken original evaluate_all expression.
    from .phase49_3i_preview_recovery import install as install_preview_recovery

    install_preview_recovery()

    original_run_ai = getattr(workspace_class, "_phase49_3e_run_ai", None)
    if original_run_ai is None:
        return

    BaseProgress = phase49_3f_workspace_module.AIProgress

    class AIProgressHandoff(BaseProgress):
        def __init__(self, parent, title: str, product_id: int | None = None):
            parent._phase49_3i_close_ai_startup()
            super().__init__(parent, title, product_id)
            try:
                self.win.update_idletasks()
                self.win.lift()
            except Exception:
                pass

    phase49_3f_workspace_module.AIProgress = AIProgressHandoff

    def _phase49_3i_close_ai_startup(self):
        win = getattr(self, "_phase49_3i_ai_startup_win", None)
        bar = getattr(self, "_phase49_3i_ai_startup_bar", None)
        if bar is not None:
            try:
                bar.stop()
            except Exception:
                pass
        if _safe_exists(win):
            try:
                win.destroy()
            except Exception:
                pass
        self._phase49_3i_ai_startup_win = None
        self._phase49_3i_ai_startup_bar = None

    def _phase49_3i_show_ai_startup(self, scope: str):
        self._phase49_3i_close_ai_startup()
        win = tk.Toplevel(self)
        win.title("3DPrintHub AI")
        win.geometry("560x190")
        win.resizable(False, False)
        win.transient(self)
        win.protocol("WM_DELETE_WINDOW", lambda: None)
        body = ttk.Frame(win, padding=16)
        body.pack(fill="both", expand=True)
        title = "آماده‌سازی SEO تصاویر" if scope == "images" else "آماده‌سازی تکمیل هوشمند محصول"
        ttk.Label(body, text=title, font=("Tahoma", 12, "bold")).pack(anchor="w")
        ttk.Label(
            body,
            text="در حال ذخیره وضعیت فعلی، بررسی Provider/Model و آماده‌سازی داده‌ها...",
            wraplength=510,
        ).pack(anchor="w", pady=(12, 8))
        bar = ttk.Progressbar(body, mode="indeterminate")
        bar.pack(fill="x", pady=8)
        bar.start(10)
        ttk.Label(
            body,
            text="پس از آماده‌سازی، پنجره پیشرفت اصلی اتصال/ارسال/دریافت جایگزین این صفحه می‌شود.",
            style="SubHeader.TLabel",
            wraplength=510,
        ).pack(anchor="w")
        self._phase49_3i_ai_startup_win = win
        self._phase49_3i_ai_startup_bar = bar
        try:
            win.update_idletasks()
            win.lift()
        except Exception:
            pass
        return win

    def _phase49_3e_run_ai(self, scope: str):
        if getattr(self, "_phase49_3i_ai_starting", False):
            try:
                self.footer_status.set("آماده‌سازی درخواست هوش مصنوعی در حال انجام است.")
            except Exception:
                pass
            return None
        if getattr(self, "_phase49_3e_busy", False) or getattr(self, "_ai_busy", False):
            return original_run_ai(self, scope)

        self._phase49_3i_ai_starting = True
        self._phase49_3i_show_ai_startup(scope)

        def invoke_existing_flow():
            try:
                original_run_ai(self, scope)
            finally:
                self._phase49_3i_ai_starting = False
                # If the existing flow exited before creating its real AIProgress
                # (for example missing API key), remove the startup handoff.
                if _safe_exists(getattr(self, "_phase49_3i_ai_startup_win", None)):
                    self._phase49_3i_close_ai_startup()

        # Yield to Tk first. This guarantees the operator sees immediate feedback
        # before the existing synchronous save/preflight block runs.
        self.after(STARTUP_DELAY_MS, invoke_existing_flow)
        return None

    workspace_class._phase49_3i_close_ai_startup = _phase49_3i_close_ai_startup
    workspace_class._phase49_3i_show_ai_startup = _phase49_3i_show_ai_startup
    workspace_class._phase49_3e_run_ai = _phase49_3e_run_ai
    workspace_class._phase49_3i_ai_first_paint_installed = True

    # Compose after first-paint so the real operator buttons enter this wrapper,
    # then hand off to the mature 49.3H progress/result/error/cost stack.
    from .phase49_3i_ai_execution_recovery import install as install_ai_execution_recovery

    install_ai_execution_recovery(workspace_class, phase49_3f_workspace_module)

    # 49.3I.9 extends the *real* all-fields button after 49.3I.8 routing exists:
    # optional source-image preflight, repeatable AI-owned refresh, readiness
    # defaults and operator-only final confirmations. No second AI/source client.
    from . import phase49_3e_ai_task_center as task_center_module
    from .phase49_3i_ai_refresh_completion import install as install_ai_refresh_completion

    install_ai_refresh_completion(workspace_class, task_center_module)
