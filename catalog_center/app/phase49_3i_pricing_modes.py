from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from . import phase49_3i_product_list as _phase49_3i_product_list_module
from .phase49_3i12_runtime_bridge import (
    install_app as _install_phase49_3i12_app,
    install_workspace as _install_phase49_3i12_workspace,
)


PRICING_MODES = {"fixed", "range", "dynamic"}


# launch.py imports this same-phase pricing module before importing
# phase49_3i_product_list.install. Wrap that later same-phase composition point so
# 49.3I.12 mounts *after* the mature Product Explorer while leaving prior phases
# independently testable (ERR-49-009 prevention rule).
if not getattr(_phase49_3i_product_list_module, "_phase49_3i12_composition_bridge", False):
    _phase49_3i_product_list_install = _phase49_3i_product_list_module.install

    def _phase49_3i12_product_list_install(app_class):
        _phase49_3i_product_list_install(app_class)
        _install_phase49_3i12_app(app_class, None)

    _phase49_3i_product_list_module.install = _phase49_3i12_product_list_install
    _phase49_3i_product_list_module._phase49_3i12_composition_bridge = True


def _money(value) -> int:
    try:
        return max(0, int(float(str(value if value not in (None, "") else 0).replace(",", "").strip() or 0)))
    except Exception:
        return 0


def normalize_range(minimum, maximum) -> tuple[int, int]:
    low = _money(minimum)
    high = _money(maximum)
    if low and high and high < low:
        low, high = high, low
    return low, high


def install(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3i_pricing_modes_installed", False):
        return

    original_commerce_ui = workspace_class._commerce_ui
    original_reload = workspace_class.reload
    original_save = workspace_class.save
    original_refresh_state = getattr(workspace_class, "_phase49_3f_refresh_pricing_state", None)

    def _commerce_ui(self):
        original_commerce_ui(self)
        panel = getattr(self, "_phase49_3f_pricing_panel", None)
        if panel is None or not hasattr(self, "pricing_strategy_var"):
            return
        try:
            panel.configure(text="قیمت‌گذاری حرفه‌ای — قطعی / بازه‌ای / فرمولی")
        except Exception:
            pass
        # Remove only the old two-choice visual row. The underlying 49.3F
        # pricing engine remains intact.
        for child in panel.grid_slaves(row=0):
            try:
                texts = [str(grand.cget("text") or "") for grand in child.winfo_children() if isinstance(grand, ttk.Radiobutton)]
            except Exception:
                texts = []
            if any("قیمت قطعی" in text or "محاسباتی / محدوده" in text for text in texts):
                try:
                    child.grid_remove()
                except Exception:
                    pass

        mode = ttk.Frame(panel)
        mode.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 8))
        ttk.Label(mode, text="روش اعلام قیمت:", font=("Tahoma", 10, "bold")).pack(side="left", padx=4)
        ttk.Radiobutton(
            mode,
            text="● قیمت قطعی",
            variable=self.pricing_strategy_var,
            value="fixed",
            command=self._phase49_3f_refresh_pricing_state,
        ).pack(side="left", padx=8)
        ttk.Radiobutton(
            mode,
            text="● بازه قیمت",
            variable=self.pricing_strategy_var,
            value="range",
            command=self._phase49_3f_refresh_pricing_state,
        ).pack(side="left", padx=8)
        ttk.Radiobutton(
            mode,
            text="● قیمت فرمولی",
            variable=self.pricing_strategy_var,
            value="dynamic",
            command=self._phase49_3f_refresh_pricing_state,
        ).pack(side="left", padx=8)
        self.phase49_3i_pricing_hint = tk.StringVar(value="")
        ttk.Label(mode, textvariable=self.phase49_3i_pricing_hint, style="SubHeader.TLabel").pack(side="right", padx=5)
        self._phase49_3i_pricing_mode_frame = mode
        self._phase49_3f_refresh_pricing_state()

    def _phase49_3f_refresh_pricing_state(self):
        if original_refresh_state is not None:
            original_refresh_state(self)
        mode = str(self.pricing_strategy_var.get() or "dynamic") if hasattr(self, "pricing_strategy_var") else "dynamic"
        fixed = mode == "fixed"
        try:
            self.fixed_material_box.configure(state="readonly" if fixed else "disabled")
            self.fixed_color_box.configure(state="readonly" if fixed else "disabled")
        except Exception:
            pass
        hint = {
            "fixed": "یک مبلغ قطعی؛ حداقل و حداکثر برابر می‌شوند.",
            "range": "حداقل و حداکثر را بالا وارد کن؛ این حالت فرمولی نیست.",
            "dynamic": "قیمت از وزن/متریال/زمان چاپ/نظارت محاسبه می‌شود.",
        }.get(mode, "")
        if hasattr(self, "phase49_3i_pricing_hint"):
            self.phase49_3i_pricing_hint.set(hint)

    def reload(self):
        raw = ""
        try:
            row = self.db.product(self.product_id)
            raw = str(row["pricing_strategy"] or "") if row is not None and "pricing_strategy" in row.keys() else ""
        except Exception:
            raw = ""
        result = original_reload(self)
        if raw == "range" and hasattr(self, "pricing_strategy_var"):
            self.pricing_strategy_var.set("range")
            self._phase49_3f_refresh_pricing_state()
        return result

    def save(self, silent=False):
        mode = str(self.pricing_strategy_var.get() or "dynamic") if hasattr(self, "pricing_strategy_var") else "dynamic"
        if mode == "range" and hasattr(self, "price_min_var") and hasattr(self, "price_max_var"):
            minimum, maximum = normalize_range(self.price_min_var.get(), self.price_max_var.get())
            if minimum <= 0 or maximum <= minimum:
                if not silent:
                    messagebox.showwarning(
                        "3DPrintHub — بازه قیمت",
                        "برای حالت بازه‌ای، حداقل باید بیشتر از صفر و حداکثر باید بزرگ‌تر از حداقل باشد.",
                        parent=self,
                    )
                if hasattr(self, "footer_status"):
                    self.footer_status.set("بازه قیمت معتبر نیست")
                return False
            self.price_min_var.set(str(minimum))
            self.price_max_var.set(str(maximum))
        ok = original_save(self, silent=silent)
        if not ok:
            return False
        if mode == "range":
            minimum, maximum = normalize_range(self.price_min_var.get(), self.price_max_var.get())
            self.db.update_product(
                self.product_id,
                {
                    "pricing_strategy": "range",
                    "price_min": minimum,
                    "price_max": maximum,
                    "final_price": 0,
                    "price_is_final": 0,
                },
            )
            self.row = self.db.product(self.product_id)
            if not silent and hasattr(self, "footer_status"):
                self.footer_status.set(f"بازه قیمت {minimum:,} تا {maximum:,} تومان ذخیره شد")
        return True

    workspace_class._commerce_ui = _commerce_ui
    workspace_class._phase49_3f_refresh_pricing_state = _phase49_3f_refresh_pricing_state
    workspace_class.reload = reload
    workspace_class.save = save
    workspace_class._phase49_3i_pricing_modes_installed = True

    # Same-phase final workspace boundary: keep the mature gallery/network logic,
    # replace only its pixel rendering contract with fixed contain/letterbox cards.
    _install_phase49_3i12_workspace(workspace_class)
