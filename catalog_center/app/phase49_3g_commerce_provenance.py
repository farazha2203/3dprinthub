from __future__ import annotations

import tkinter as tk
from tkinter import ttk


MATERIAL_GROUP = "materials"


def install(workspace_class) -> None:
    """Add a compact ownership row to the mature commerce page.

    This is presentation-only. Pricing inputs, price strategy, approval flags and
    publish controls remain operator-owned and are not changed here.
    """
    if getattr(workspace_class, "_phase49_3g_commerce_provenance_installed", False):
        return

    original_init = workspace_class.__init__

    def __init__(self, app, product_id: int):
        original_init(self, app, product_id)
        self._phase49_3g_add_commerce_provenance_panel()
        self.after_idle(self._phase49_3g_refresh_provenance)
        self.after_idle(self._phase49_3g_refresh_workspace_scroll)

    def _phase49_3g_add_commerce_provenance_panel(self):
        parent = getattr(self, "commerce_tab", None)
        if parent is None or getattr(self, "_phase49_3g_commerce_provenance_panel", None) is not None:
            return

        rows = []
        for child in parent.grid_slaves():
            try:
                rows.append(int(child.grid_info().get("row", 0)))
            except Exception:
                continue
        row_index = (max(rows) + 1) if rows else 20

        frame = ttk.LabelFrame(
            parent,
            text="مالکیت AI در سفارش و قیمت",
            padding=6,
            style="Card.TLabelframe",
        )
        frame.grid(row=row_index, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        self._phase49_3g_commerce_provenance_panel = frame

        ownership = ttk.Frame(frame)
        ownership.pack(fill="x", pady=2)
        var = tk.StringVar(value="")
        self._phase49_3g_provenance_vars[MATERIAL_GROUP] = var
        ttk.Label(
            ownership,
            textvariable=var,
            style="SubHeader.TLabel",
        ).pack(side="right", fill="x", expand=True, padx=5)
        ttk.Button(
            ownership,
            text="خاموش/روشن AI",
            command=lambda: self._phase49_3g_toggle_group(MATERIAL_GROUP),
        ).pack(side="left", padx=3)
        ttk.Button(
            ownership,
            text="اجازه بازنویسی AI",
            command=lambda: self._phase49_3g_allow_rewrite(MATERIAL_GROUP),
        ).pack(side="left", padx=3)

        ttk.Label(
            frame,
            text=(
                "🔒 قیمت قطعی، تأیید فروش، موجودی، مجوز و انتشار Production همیشه اپراتوری می‌مانند؛ "
                "AI فقط پیشنهاد متریال و داده‌های مجاز را تکمیل می‌کند."
            ),
            style="SubHeader.TLabel",
            wraplength=1050,
        ).pack(fill="x", padx=5, pady=(3, 0))

    workspace_class.__init__ = __init__
    workspace_class._phase49_3g_add_commerce_provenance_panel = _phase49_3g_add_commerce_provenance_panel
    workspace_class._phase49_3g_commerce_provenance_installed = True
