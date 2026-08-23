from __future__ import annotations

import time
from tkinter import messagebox, ttk

from .phase49_3i12_discovery_image_recovery import classify_manual_url


LEGACY_ACTION_TEXTS = (
    "شروع اسکن",
    "توقف محترمانه",
    "دریافت هوشمند از لینک",
    "🔎 کشف جدیدها",
    "کشف جدیدها",
)


def _walk(root):
    try:
        children = root.winfo_children()
    except Exception:
        children = []
    for child in children:
        yield child
        yield from _walk(child)


def _resolve_legacy_start_scan(app_class):
    """Return the mature BaseApp start_scan hidden by the 49.3I preview wrapper."""
    for parent in app_class.__mro__[1:]:
        candidate = parent.__dict__.get("start_scan")
        if callable(candidate):
            return candidate
    return None


def install_app(app_class) -> None:
    """Restore the mature top scan workflow without removing newer 49.3I controls.

    Phase49.3I.12 hid several healthy buttons and the earlier 49.3I preview layer
    replaced ``App87.start_scan`` with Preview discovery.  This recovery keeps the
    Preview/Approve panel intact but restores the original top controls and binds
    the visible ``شروع اسکن`` button back to the mature BaseApp scan worker.

    The separate manual single-product action also uses that mature scan worker.
    This intentionally avoids the newer RichPageExtractor direct-intake route that
    returned HTTP 403 in real Windows QA while preserving the explicit
    ``دریافت هوشمند از لینک`` button as an optional independent tool.
    """
    if getattr(app_class, "_phase49_3i14_legacy_scan_restore_installed", False):
        return

    original_mount = app_class._mount_phase49_3i12_operator_ui
    legacy_start_scan = _resolve_legacy_start_scan(app_class)
    if legacy_start_scan is None:
        raise RuntimeError("Mature BaseApp start_scan was not found; refusing to replace scan behavior.")

    def start_legacy_scan(self):
        if bool(getattr(self, "scan_running", False)):
            detail = getattr(self, "_phase49_3i12_detail", None)
            if detail is not None:
                try:
                    detail.set("یک عملیات دریافت در حال اجرا است؛ ابتدا همان عملیات را تمام یا متوقف کنید.")
                except Exception:
                    pass
            return None
        return legacy_start_scan(self)

    def _begin_single_monitor(self, url: str):
        token = int(getattr(self, "_phase49_3i12_run_token", 0) or 0) + 1
        self._phase49_3i12_run_token = token
        self._phase49_3i12_run_kind = "single"
        self._phase49_3i12_run_url = url
        self._phase49_3i12_started = time.monotonic()
        self._phase49_3i12_stop_requested = False
        elapsed = getattr(self, "_phase49_3i12_elapsed", None)
        if elapsed is not None:
            try:
                elapsed.set("زمان: 0s")
            except Exception:
                pass
        setter = getattr(self, "_phase49_3i12_set_state", None)
        if callable(setter):
            setter(
                "active",
                "● شروع دریافت محصول تکی",
                "مسیر بالغ اسکن بالای برنامه اجرا می‌شود؛ Rich Direct Intake اجباری نیست.",
            )
        monitor = getattr(self, "_phase49_3i12_monitor_run", None)
        if callable(monitor):
            try:
                self.after(150, lambda t=token: monitor(t))
            except Exception:
                pass
        return token

    def start_single_product_manual(self):
        if bool(getattr(self, "scan_running", False)):
            detail = getattr(self, "_phase49_3i12_detail", None)
            if detail is not None:
                try:
                    detail.set("یک عملیات در حال اجرا است؛ ابتدا همان عملیات را تمام یا متوقف کنید.")
                except Exception:
                    pass
            return None

        url = self.seed_var.get().strip()
        selected_label = self.source_var.get().strip()
        code = self.source_map.get(selected_label, selected_label)
        src = self.db.source(code)
        pattern = str(src["model_url_pattern"] or "") if src is not None else ""
        if src is None:
            messagebox.showwarning("3DPrintHub", "ابتدا یک منبع معتبر انتخاب کنید.", parent=self)
            return None

        kind = classify_manual_url(url, pattern)
        if kind == "invalid":
            messagebox.showwarning("3DPrintHub", "یک URL کامل http/https وارد کنید.", parent=self)
            return None
        if kind == "invalid_pattern":
            messagebox.showerror("3DPrintHub", "Regex تشخیص Product URL برای این منبع معتبر نیست.", parent=self)
            return None
        if kind != "product":
            messagebox.showwarning(
                "3DPrintHub",
                "این URL محصول تکی این منبع نیست. برای Search/Listing/Category از کشف لینک‌های همین صفحه استفاده کنید.",
                parent=self,
            )
            return None

        self.mode_var.set("single")
        if not str(self.method_var.get() or "").strip():
            self.method_var.set("auto")
        self._phase49_3i12_source_code = code
        token = _begin_single_monitor(self, url)
        result = start_legacy_scan(self)
        if not bool(getattr(self, "scan_running", False)):
            monitor = getattr(self, "_phase49_3i12_monitor_run", None)
            if callable(monitor):
                try:
                    self.after(0, lambda t=token: monitor(t))
                except Exception:
                    pass
        return result

    def _restore_legacy_buttons(self):
        scan_tab = getattr(self, "scan_tab", None)
        if scan_tab is None:
            return 0
        restored = 0
        for widget in _walk(scan_tab):
            if not isinstance(widget, ttk.Button):
                continue
            try:
                text = str(widget.cget("text") or "")
            except Exception:
                continue
            if text not in LEGACY_ACTION_TEXTS:
                continue
            if text == "شروع اسکن":
                try:
                    widget.configure(command=self.start_legacy_scan)
                except Exception:
                    pass
            try:
                manager = widget.winfo_manager()
            except Exception:
                manager = ""
            if manager:
                continue
            try:
                widget.pack(side="left", padx=4)
                restored += 1
            except Exception:
                pass
        return restored

    def _mount_phase49_3i12_operator_ui(self):
        result = original_mount(self)
        restored = _restore_legacy_buttons(self)
        self._phase49_3i14_legacy_buttons_restored = True
        self._phase49_3i14_legacy_buttons_restored_count = restored
        return result

    app_class.start_legacy_scan = start_legacy_scan
    app_class.start_single_product_manual = start_single_product_manual
    app_class._phase49_3i14_restore_legacy_buttons = _restore_legacy_buttons
    app_class._mount_phase49_3i12_operator_ui = _mount_phase49_3i12_operator_ui
    app_class._phase49_3i14_legacy_scan_restore_installed = True
