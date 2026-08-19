from __future__ import annotations

from tkinter import ttk


LEGACY_ACTIVATE_TEXT = "فعال کن"
OLD_HELP_FRAGMENT = "Provider فعال برای درخواست‌های Product Workspace با دکمه «فعال کن» انتخاب می‌شود."
NEW_HELP_TEXT = (
    "هر Provider تنظیمات، کلید، اعتبار و تست مستقل دارد. "
    "Provider فعال را با Radio انتخاب کن، مدل را از «جستجو و انتخاب مدل» بردار و سپس "
    "«ذخیره Provider و مدل فعال» را بزن."
)


def _walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from _walk(child)


def install(app_class) -> None:
    """Remove the obsolete per-card activation button after Phase49.3D adds radio state.

    The old secure-save, live-test and balance buttons remain available. Only the
    duplicated activation path and its stale help sentence are removed so there is
    one unambiguous source of truth for the active Provider/Model.
    """
    if getattr(app_class, "_phase49_3d_ai_ui_cleanup_installed", False):
        return
    original_build = app_class._build_ux87_ai_center

    def _build_ux87_ai_center(self):
        original_build(self)
        removed = 0
        for child in _walk(self.ai_tab):
            if isinstance(child, ttk.Button):
                try:
                    if str(child.cget("text") or "").strip() == LEGACY_ACTIVATE_TEXT:
                        manager = child.winfo_manager()
                        if manager == "pack":
                            child.pack_forget()
                        elif manager == "grid":
                            child.grid_remove()
                        elif manager == "place":
                            child.place_forget()
                        removed += 1
                except Exception:
                    pass
            elif isinstance(child, ttk.Label):
                try:
                    text = str(child.cget("text") or "")
                    if OLD_HELP_FRAGMENT in text:
                        child.configure(text=NEW_HELP_TEXT)
                except Exception:
                    pass
        self._phase49_3d_legacy_activate_buttons_removed = removed

    app_class._build_ux87_ai_center = _build_ux87_ai_center
    app_class._phase49_3d_ai_ui_cleanup_installed = True
