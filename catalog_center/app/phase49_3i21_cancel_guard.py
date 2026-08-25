from __future__ import annotations

from .phase49_3i21_observable_ai_link_refresh import ObservableJobDialog


def install() -> None:
    if getattr(ObservableJobDialog, "_phase49_3i21_cancel_guard", False):
        return
    original_cancel = ObservableJobDialog.cancel

    def cancel(self):
        original_cancel(self)
        try:
            setattr(self.workspace, "_phase49_3i21_busy", False)
            if hasattr(self.workspace, "footer_status"):
                self.workspace.footer_status.set(
                    "انتظار AI لغو شد؛ پاسخ دیررس روی محصول اعمال نمی‌شود"
                )
        except Exception:
            pass

    ObservableJobDialog.cancel = cancel
    ObservableJobDialog._phase49_3i21_cancel_guard = True
