from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .epic49_site_sync import BridgeConflictError, update_hero_slide

PRESENTATION = {
    "نمایش کامل محصول": "product_fit",
    "پر کردن کامل اسلایدر": "full_bleed",
    "کادر محصول": "framed",
    "سینمایی با پس‌زمینه": "cinematic",
}
PRESENTATION_LABEL = {value: key for key, value in PRESENTATION.items()}
BACKGROUND = {
    "رنگ ثابت": "solid",
    "Blur از خود تصویر": "blur",
    "گرادیان": "gradient",
    "خود تصویر": "image",
}
BACKGROUND_LABEL = {value: key for key, value in BACKGROUND.items()}


def _bounded(value, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(float(str(value if value not in (None, "") else default).replace(",", "")))
    except Exception:
        parsed = default
    return min(maximum, max(minimum, parsed))


def install(manager_class) -> None:
    if getattr(manager_class, "_phase49_3b_media_ui_installed", False):
        return
    original_build = manager_class._build_ui

    def _build_ui(self):
        original_build(self)
        # Add the entry point to the existing header instead of forking the manager.
        header = self.winfo_children()[0] if self.winfo_children() else None
        if isinstance(header, tk.Frame):
            ttk.Button(
                header,
                text="تنظیم قاب تصویر Hero",
                command=self.open_phase49_3b_media_editor,
                style="Primary.TButton",
            ).pack(side="right", padx=4)

    def open_phase49_3b_media_editor(self):
        if not getattr(self, "current_id", 0) or self.current_id not in self.rows:
            messagebox.showinfo("3DPrintHub", "ابتدا یک اسلاید را از لیست انتخاب کن.", parent=self)
            return
        row = self.rows[self.current_id]
        win = tk.Toplevel(self)
        win.title("تنظیم قاب تصویر Hero | 3DPrintHub")
        win.transient(self)
        win.grab_set()
        win.geometry("760x620")
        body = ttk.Frame(win, padding=14)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        presentation = tk.StringVar(value=PRESENTATION_LABEL.get(row.get("presentation_mode"), "نمایش کامل محصول"))
        fit = tk.StringVar(value=row.get("object_fit") or "contain")
        focal = tk.StringVar(value=row.get("focal_position") or "center")
        scale = tk.StringVar(value=str(row.get("image_scale_percent") or 100))
        pos_x = tk.StringVar(value=str(row.get("image_position_x_percent") or 50))
        pos_y = tk.StringVar(value=str(row.get("image_position_y_percent") or 50))
        background = tk.StringVar(value=BACKGROUND_LABEL.get(row.get("background_mode"), "Blur از خود تصویر"))
        color = tk.StringVar(value=row.get("background_color") or "#071827")
        blur = tk.StringVar(value=str(row.get("background_blur_px") or 18))
        desktop_w = tk.StringVar(value=str(row.get("desktop_max_width_percent") or 78))
        desktop_h = tk.StringVar(value=str(row.get("desktop_max_height_percent") or 88))
        mobile_w = tk.StringVar(value=str(row.get("mobile_max_width_percent") or 92))
        mobile_h = tk.StringVar(value=str(row.get("mobile_max_height_percent") or 72))

        fields = [
            ("حالت ارائه", ttk.Combobox(body, textvariable=presentation, values=list(PRESENTATION), state="readonly")),
            ("Object Fit", ttk.Combobox(body, textvariable=fit, values=["contain", "cover"], state="readonly")),
            ("نقطه تمرکز", ttk.Combobox(body, textvariable=focal, values=["center", "top", "bottom", "left", "right"], state="readonly")),
            ("مقیاس تصویر %", ttk.Entry(body, textvariable=scale)),
            ("موقعیت افقی X %", ttk.Entry(body, textvariable=pos_x)),
            ("موقعیت عمودی Y %", ttk.Entry(body, textvariable=pos_y)),
            ("حالت پس‌زمینه", ttk.Combobox(body, textvariable=background, values=list(BACKGROUND), state="readonly")),
            ("رنگ پس‌زمینه", ttk.Entry(body, textvariable=color)),
            ("Blur px", ttk.Entry(body, textvariable=blur)),
            ("Desktop max width %", ttk.Entry(body, textvariable=desktop_w)),
            ("Desktop max height %", ttk.Entry(body, textvariable=desktop_h)),
            ("Mobile max width %", ttk.Entry(body, textvariable=mobile_w)),
            ("Mobile max height %", ttk.Entry(body, textvariable=mobile_h)),
        ]
        for idx, (label, widget) in enumerate(fields):
            ttk.Label(body, text=label).grid(row=idx, column=0, sticky="w", padx=5, pady=5)
            widget.grid(row=idx, column=1, sticky="ew", padx=5, pady=5)

        status = tk.StringVar(value=f"Revision فعلی: {row.get('sync_revision') or 1}")
        ttk.Label(body, textvariable=status, style="SubHeader.TLabel").grid(row=len(fields), column=0, columnspan=2, sticky="w", padx=5, pady=8)

        def save_media():
            payload = {
                "presentation_mode": PRESENTATION.get(presentation.get(), "product_fit"),
                "object_fit": fit.get() if fit.get() in {"contain", "cover"} else "contain",
                "focal_position": focal.get() or "center",
                "image_scale_percent": _bounded(scale.get(), 100, 60, 140),
                "image_position_x_percent": _bounded(pos_x.get(), 50, 0, 100),
                "image_position_y_percent": _bounded(pos_y.get(), 50, 0, 100),
                "background_mode": BACKGROUND.get(background.get(), "blur"),
                "background_color": color.get().strip()[:24] or "#071827",
                "background_blur_px": _bounded(blur.get(), 18, 0, 60),
                "desktop_max_width_percent": _bounded(desktop_w.get(), 78, 30, 100),
                "desktop_max_height_percent": _bounded(desktop_h.get(), 88, 30, 100),
                "mobile_max_width_percent": _bounded(mobile_w.get(), 92, 30, 100),
                "mobile_max_height_percent": _bounded(mobile_h.get(), 72, 30, 100),
            }
            expected = int(row.get("sync_revision") or 1)
            status.set("در حال ذخیره روی سایت…")

            def work():
                return update_hero_slide(self.cfg, self.current_id, expected, payload)

            def done(result, error):
                if isinstance(error, BridgeConflictError):
                    current = error.payload.get("current") if isinstance(error.payload, dict) else None
                    if isinstance(current, dict):
                        self.rows[int(current["id"])] = current
                        self.current_id = int(current["id"])
                    status.set("Conflict: نسخه سایت جدیدتر است؛ پنجره را ببند و Refresh کن.")
                    messagebox.showwarning("3DPrintHub", str(error), parent=win)
                    return
                if error:
                    status.set(str(error))
                    messagebox.showerror("3DPrintHub", str(error), parent=win)
                    return
                slide = dict((result or {}).get("slide") or {})
                if slide:
                    self.rows[int(slide["id"])] = slide
                    self.current_id = int(slide["id"])
                status.set("✅ تنظیم قاب تصویر ذخیره شد")
                self.refresh()
                win.after(350, win.destroy)

            self._async(work, done)

        actions = ttk.Frame(body)
        actions.grid(row=len(fields) + 1, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(actions, text="بستن", command=win.destroy).pack(side="right", padx=3)
        ttk.Button(actions, text="ذخیره روی سایت", command=save_media, style="Success.TButton").pack(side="right", padx=3)

    manager_class._build_ui = _build_ui
    manager_class.open_phase49_3b_media_editor = open_phase49_3b_media_editor
    manager_class._phase49_3b_media_ui_installed = True
