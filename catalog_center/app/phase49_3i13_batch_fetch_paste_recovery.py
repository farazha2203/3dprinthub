from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .phase49_3i_discovery_review import candidate_row


def _first_clipboard_line(value: str) -> str:
    """Return the first non-empty clipboard line without changing URL query text."""
    for line in str(value or "").replace("\r", "\n").split("\n"):
        candidate = line.strip()
        if candidate:
            return candidate
    return ""


def install_app(app_class) -> None:
    """Install the 49.3I.13 Windows operator recovery.

    This hotfix intentionally leaves discovery, direct single-product intake and
    the mature RichPageExtractor untouched. It changes only the final operator
    surface and the browser visibility policy used while an *approved batch*
    Full Fetch is running.
    """
    if getattr(app_class, "_phase49_3i13_recovery_installed", False):
        return

    original_mount = app_class._mount_phase49_3i12_operator_ui
    original_approve = app_class.approve_discovery_candidates

    def _phase49_3i13_paste_url(self, event=None):
        entry = getattr(self, "_phase49_3i13_url_entry", None)
        if entry is None:
            return "break" if event is not None else None
        try:
            value = _first_clipboard_line(self.clipboard_get())
        except Exception:
            value = ""
        if not value:
            messagebox.showwarning("3DPrintHub", "کلیپ‌بورد متن قابل چسباندن ندارد.", parent=self)
            return "break" if event is not None else None
        try:
            entry.delete(0, tk.END)
            entry.insert(0, value)
            entry.icursor(tk.END)
            entry.focus_set()
        except Exception:
            try:
                self.seed_var.set(value)
            except Exception:
                pass
        detail = getattr(self, "_phase49_3i12_detail", None)
        if detail is not None:
            try:
                detail.set("URL از کلیپ‌بورد چسبانده شد؛ نوع لینک قبل از اجرا بررسی می‌شود.")
            except Exception:
                pass
        return "break" if event is not None else None

    def _phase49_3i13_open_url_menu(self, event):
        menu = getattr(self, "_phase49_3i13_url_menu", None)
        if menu is None:
            return "break"
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass
        return "break"

    def _phase49_3i13_show_selected_error(self):
        ids = self._selected_candidate_ids() if hasattr(self, "_selected_candidate_ids") else []
        if not ids:
            messagebox.showinfo("خطای کاندیدا", "ابتدا یک یا چند کاندیدا را انتخاب کنید.", parent=self)
            return
        lines = []
        for candidate_id in ids[:8]:
            row = candidate_row(self.db, candidate_id)
            if row is None:
                continue
            title = str(row["source_title"] or row["external_id"] or candidate_id)
            status = str(row["status"] or "")
            error = str(row["last_error"] or "").strip()
            lines.append(f"#{candidate_id} | {status} | {title}\n{error or 'خطای فنی برای این مورد ثبت نشده است.'}")
        if len(ids) > 8:
            lines.append(f"... و {len(ids) - 8} مورد دیگر")
        messagebox.showinfo("جزئیات دریافت کاندیدا", "\n\n".join(lines) or "جزئیاتی ثبت نشده است.", parent=self)

    def _phase49_3i13_restore_batch_browser_mode(self, token: int):
        if int(getattr(self, "_phase49_3i13_batch_token", 0) or 0) != int(token):
            return
        if bool(getattr(self, "scan_running", False)):
            self.after(350, lambda t=token: _phase49_3i13_restore_batch_browser_mode(self, t))
            return
        direct_cfg = self.config.setdefault("direct_link", {})
        had_key = bool(getattr(self, "_phase49_3i13_had_headed_key", False))
        old_value = getattr(self, "_phase49_3i13_old_headed_value", True)
        if had_key:
            direct_cfg["headed"] = old_value
        else:
            direct_cfg.pop("headed", None)
        self._phase49_3i13_batch_headless_active = False

    def approve_discovery_candidates(self):
        ids = self._selected_candidate_ids() if hasattr(self, "_selected_candidate_ids") else []
        if not ids:
            return original_approve(self)
        if bool(getattr(self, "scan_running", False)):
            return original_approve(self)

        # The direct single-product workflow intentionally keeps its configured
        # headed behavior for CAPTCHA/login recovery. Approved multi-candidate
        # intake is different: it must run in the background and must not flash
        # one Chrome/Edge window per selected row.
        direct_cfg = self.config.setdefault("direct_link", {})
        self._phase49_3i13_had_headed_key = "headed" in direct_cfg
        self._phase49_3i13_old_headed_value = direct_cfg.get("headed", True)
        direct_cfg["headed"] = False
        self._phase49_3i13_batch_headless_active = True
        token = int(getattr(self, "_phase49_3i13_batch_token", 0) or 0) + 1
        self._phase49_3i13_batch_token = token

        try:
            result = original_approve(self)
        except Exception:
            _phase49_3i13_restore_batch_browser_mode(self, token)
            raise

        if bool(getattr(self, "scan_running", False)):
            detail = getattr(self, "_phase49_3i12_detail", None)
            if detail is not None:
                try:
                    detail.set(
                        f"دریافت کامل {len(ids)} مورد در پس‌زمینه اجرا می‌شود؛ پنجره مرورگر برای هر محصول باز نمی‌شود."
                    )
                except Exception:
                    pass
            self.after(350, lambda t=token: _phase49_3i13_restore_batch_browser_mode(self, t))
        else:
            # User cancelled the confirmation dialog or the mature path returned
            # before starting a worker; restore immediately.
            _phase49_3i13_restore_batch_browser_mode(self, token)
        return result

    def _mount_phase49_3i12_operator_ui(self):
        result = original_mount(self)
        if bool(getattr(self, "_phase49_3i13_operator_controls_ready", False)):
            return result
        operator = getattr(self, "_phase49_3i12_operator_frame", None)
        if operator is None:
            return result

        entry = next((widget for widget in operator.winfo_children() if isinstance(widget, ttk.Entry)), None)
        if entry is None:
            # The Entry may live one level down in a future shell composition.
            for child in operator.winfo_children():
                try:
                    nested = next((widget for widget in child.winfo_children() if isinstance(widget, ttk.Entry)), None)
                except Exception:
                    nested = None
                if nested is not None:
                    entry = nested
                    break
        if entry is not None:
            self._phase49_3i13_url_entry = entry
            entry.bind("<Control-v>", self._phase49_3i13_paste_url)
            entry.bind("<Control-V>", self._phase49_3i13_paste_url)
            entry.bind("<Shift-Insert>", self._phase49_3i13_paste_url)
            entry.bind("<Button-3>", self._phase49_3i13_open_url_menu)
            menu = tk.Menu(entry, tearoff=False)
            menu.add_command(label="چسباندن", command=self._phase49_3i13_paste_url)
            menu.add_command(label="انتخاب همه", command=lambda: (entry.selection_range(0, tk.END), entry.icursor(tk.END)))
            self._phase49_3i13_url_menu = menu

        actions = None
        for child in operator.winfo_children():
            if not isinstance(child, ttk.Frame):
                continue
            try:
                info = child.grid_info()
                if int(info.get("row", -1)) == 0 and int(info.get("column", -1)) == 2:
                    actions = child
                    break
            except Exception:
                continue
        if actions is not None:
            ttk.Button(actions, text="چسباندن لینک", command=self._phase49_3i13_paste_url).pack(side="left", padx=2)
            ttk.Button(actions, text="جزئیات خطای انتخابی", command=self._phase49_3i13_show_selected_error).pack(side="left", padx=2)

        self._phase49_3i13_operator_controls_ready = True
        return result

    app_class._phase49_3i13_paste_url = _phase49_3i13_paste_url
    app_class._phase49_3i13_open_url_menu = _phase49_3i13_open_url_menu
    app_class._phase49_3i13_show_selected_error = _phase49_3i13_show_selected_error
    app_class._phase49_3i13_restore_batch_browser_mode = _phase49_3i13_restore_batch_browser_mode
    app_class.approve_discovery_candidates = approve_discovery_candidates
    app_class._mount_phase49_3i12_operator_ui = _mount_phase49_3i12_operator_ui
    app_class._phase49_3i13_recovery_installed = True
