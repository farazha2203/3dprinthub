from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .epic49_site_sync import BridgeConflictError, list_hero_slides, update_hero_slide


EFFECTS = [
    ("cinematic_fade", "Cinematic Fade"),
    ("wedding_dissolve", "Wedding Dissolve"),
    ("cinematic_zoom", "Cinematic Zoom"),
    ("ken_burns", "Ken Burns Fade"),
    ("soft_blur", "Soft Blur Dissolve"),
    ("cinematic_reveal", "Cinematic Reveal"),
]
EFFECT_LABEL = dict(EFFECTS)
EFFECT_CODE = {label: code for code, label in EFFECTS}


class ServerSliderManager(tk.Toplevel):
    def __init__(self, app, parent=None):
        super().__init__(parent or app)
        self.app = app
        self.cfg = app._site_connection(require_bridge=True)
        self.title("اسلایدرهای سایت | 3DPrintHub")
        self.geometry("1380x820")
        self.minsize(1080, 680)
        self.rows: dict[int, dict] = {}
        self.current_id = 0
        self.image_map: dict[str, int | None] = {}
        self._build_ui()
        if self.cfg:
            self.refresh()
        else:
            self.status.set("تنظیمات اتصال سایت/Bridge کامل نیست")

    def _build_ui(self):
        header = tk.Frame(self, bg="#071827", padx=14, pady=10)
        header.pack(fill="x")
        tk.Label(header, text="مدیریت اسلایدرهای سایت", bg="#071827", fg="white", font=("Tahoma", 15, "bold")).pack(side="left")
        ttk.Button(header, text="تازه‌سازی از سایت", command=self.refresh).pack(side="right")

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=10, pady=10)
        left = ttk.Frame(body, padding=6)
        right = ttk.Frame(body, padding=10)
        body.add(left, weight=2)
        body.add(right, weight=3)

        self.tree = ttk.Treeview(left, columns=("id", "title", "effect", "active", "revision"), show="headings", height=24)
        for key, text, width in [
            ("id", "ID", 60), ("title", "عنوان", 280), ("effect", "افکت", 130),
            ("active", "فعال", 70), ("revision", "Revision", 80),
        ]:
            self.tree.heading(key, text=text)
            self.tree.column(key, width=width, anchor="center" if key != "title" else "e")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._select)

        right.columnconfigure(1, weight=1)
        self.title_var = tk.StringVar()
        self.alt_var = tk.StringVar()
        self.button_var = tk.StringVar(value="مشاهده محصول")
        self.focus_var = tk.StringVar()
        self.effect_var = tk.StringVar(value="Cinematic Fade")
        self.transition_var = tk.StringVar(value="1400")
        self.display_var = tk.StringVar(value="7000")
        self.sort_var = tk.StringVar(value="100")
        self.active_var = tk.IntVar(value=1)
        self.image_var = tk.StringVar()
        self.revision_var = tk.StringVar(value="Revision: —")

        ttk.Label(right, text="عنوان اختصاصی اسلایدر").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(right, textvariable=self.title_var).grid(row=0, column=1, sticky="ew", padx=6, pady=5)
        ttk.Label(right, text="توضیح اسلایدر").grid(row=1, column=0, sticky="nw", pady=5)
        self.description = tk.Text(right, height=5, wrap="word", undo=True)
        self.description.grid(row=1, column=1, sticky="ew", padx=6, pady=5)
        ttk.Label(right, text="Alt تصویر Hero").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(right, textvariable=self.alt_var).grid(row=2, column=1, sticky="ew", padx=6, pady=5)
        ttk.Label(right, text="Focus Keyword").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(right, textvariable=self.focus_var).grid(row=3, column=1, sticky="ew", padx=6, pady=5)
        ttk.Label(right, text="متن دکمه").grid(row=4, column=0, sticky="w", pady=5)
        ttk.Entry(right, textvariable=self.button_var).grid(row=4, column=1, sticky="ew", padx=6, pady=5)

        ttk.Label(right, text="عکس اسلایدر").grid(row=5, column=0, sticky="w", pady=5)
        self.image_box = ttk.Combobox(right, textvariable=self.image_var, state="readonly")
        self.image_box.grid(row=5, column=1, sticky="ew", padx=6, pady=5)

        settings = ttk.LabelFrame(right, text="افکت و زمان‌بندی", padding=8)
        settings.grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(settings, text="افکت").grid(row=0, column=0, padx=4, pady=4)
        ttk.Combobox(settings, textvariable=self.effect_var, values=[label for _, label in EFFECTS], state="readonly", width=24).grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(settings, text="Transition ms").grid(row=0, column=2, padx=4, pady=4)
        ttk.Spinbox(settings, from_=300, to=4000, increment=100, textvariable=self.transition_var, width=9).grid(row=0, column=3, padx=4, pady=4)
        ttk.Label(settings, text="Display ms").grid(row=0, column=4, padx=4, pady=4)
        ttk.Spinbox(settings, from_=2000, to=30000, increment=500, textvariable=self.display_var, width=9).grid(row=0, column=5, padx=4, pady=4)
        ttk.Label(settings, text="ترتیب").grid(row=0, column=6, padx=4, pady=4)
        ttk.Spinbox(settings, from_=0, to=10000, textvariable=self.sort_var, width=8).grid(row=0, column=7, padx=4, pady=4)
        ttk.Checkbutton(settings, text="فعال", variable=self.active_var).grid(row=0, column=8, padx=8, pady=4)

        actions = ttk.Frame(right)
        actions.grid(row=7, column=0, columnspan=2, sticky="ew", pady=8)
        ttk.Label(actions, textvariable=self.revision_var).pack(side="left")
        ttk.Button(actions, text="ذخیره روی سایت", command=self.save, style="Success.TButton").pack(side="right", padx=4)
        self.status = tk.StringVar(value="آماده")
        ttk.Label(right, textvariable=self.status).grid(row=8, column=0, columnspan=2, sticky="ew", pady=4)

    def _async(self, work, done):
        def runner():
            try:
                result = work()
                self.after(0, lambda: done(result, None))
            except Exception as exc:
                self.after(0, lambda: done(None, exc))
        threading.Thread(target=runner, daemon=True).start()

    def refresh(self):
        if not self.cfg:
            return
        self.status.set("در حال دریافت اسلایدرهای سایت…")
        self._async(lambda: list_hero_slides(self.cfg), self._refresh_done)

    def _refresh_done(self, items, error):
        if error:
            self.status.set(str(error))
            messagebox.showerror("3DPrintHub", str(error), parent=self)
            return
        self.rows = {int(row["id"]): row for row in items or []}
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for row in items or []:
            self.tree.insert("", "end", iid=str(row["id"]), values=(
                row["id"], row.get("product_title") or row.get("title_override") or "—",
                EFFECT_LABEL.get(row.get("transition_effect"), row.get("transition_effect")),
                "بله" if row.get("is_active") else "خیر", row.get("sync_revision") or 0,
            ))
        self.status.set(f"{len(items or [])} اسلاید از سایت دریافت شد")
        if self.current_id in self.rows:
            self._load(self.rows[self.current_id])

    def _select(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        self.current_id = int(selection[0])
        self._load(self.rows[self.current_id])

    def _load(self, row):
        self.title_var.set(row.get("title_override") or "")
        self.description.delete("1.0", "end")
        self.description.insert("1.0", row.get("description") or "")
        self.alt_var.set(row.get("image_alt_text") or "")
        self.button_var.set(row.get("button_text") or "مشاهده محصول")
        self.focus_var.set(row.get("focus_keyword") or "")
        self.effect_var.set(EFFECT_LABEL.get(row.get("transition_effect"), "Cinematic Fade"))
        self.transition_var.set(str(row.get("transition_duration_ms") or 1400))
        self.display_var.set(str(row.get("display_duration_ms") or 7000))
        self.sort_var.set(str(row.get("sort_order") or 0))
        self.active_var.set(1 if row.get("is_active") else 0)
        self.revision_var.set(f"Revision: {row.get('sync_revision') or 0} • {row.get('last_modified_source') or '-'} / {row.get('last_modified_by') or '-'}")
        mapping = {"تصویر پیش‌فرض / بدون انتخاب Relation": None}
        for index, image in enumerate(row.get("images") or [], 1):
            label = f"{index:02d} — #{image.get('id')} — {(image.get('alt') or image.get('url') or '')[:70]}"
            mapping[label] = image.get("id")
        self.image_map = mapping
        self.image_box.configure(values=list(mapping))
        wanted = row.get("selected_asset_image_id")
        chosen = next((label for label, image_id in mapping.items() if image_id == wanted), list(mapping)[0])
        self.image_var.set(chosen)

    def save(self):
        if not self.current_id or self.current_id not in self.rows:
            messagebox.showinfo("3DPrintHub", "ابتدا یک اسلاید را انتخاب کنید.", parent=self)
            return
        row = self.rows[self.current_id]
        try:
            transition = max(300, min(4000, int(self.transition_var.get() or 1400)))
            display = max(2000, min(30000, int(self.display_var.get() or 7000)))
            order = max(0, int(self.sort_var.get() or 0))
        except ValueError:
            messagebox.showerror("3DPrintHub", "مقادیر زمان/ترتیب معتبر نیست.", parent=self)
            return
        payload = {
            "title_override": self.title_var.get().strip(),
            "description": self.description.get("1.0", "end").strip(),
            "image_alt_text": self.alt_var.get().strip(),
            "button_text": self.button_var.get().strip() or "مشاهده محصول",
            "focus_keyword": self.focus_var.get().strip(),
            "selected_asset_image_id": self.image_map.get(self.image_var.get()),
            "transition_effect": EFFECT_CODE.get(self.effect_var.get(), "cinematic_fade"),
            "transition_duration_ms": transition,
            "display_duration_ms": display,
            "sort_order": order,
            "is_active": bool(self.active_var.get()),
        }
        expected = int(row.get("sync_revision") or 1)
        self.status.set("در حال ذخیره روی سایت…")
        self._async(
            lambda: update_hero_slide(self.cfg, self.current_id, expected, payload),
            self._save_done,
        )

    def _save_done(self, result, error):
        if isinstance(error, BridgeConflictError):
            current = error.payload.get("current") if isinstance(error.payload, dict) else None
            if isinstance(current, dict):
                self.rows[int(current["id"])] = current
                self.current_id = int(current["id"])
                self._load(current)
            self.status.set("Conflict: نسخه جدید سایت بارگذاری شد")
            messagebox.showwarning("3DPrintHub", str(error) + "\nنسخه جدید سایت بارگذاری شد؛ تغییرات را دوباره بررسی کنید.", parent=self)
            return
        if error:
            self.status.set(str(error))
            messagebox.showerror("3DPrintHub", str(error), parent=self)
            return
        slide = dict((result or {}).get("slide") or {})
        if slide:
            self.rows[int(slide["id"])] = slide
            self.current_id = int(slide["id"])
            self._load(slide)
        self.status.set("اسلایدر روی سایت ذخیره شد")
        self.refresh()


def open_server_slider_manager(app, parent=None):
    return ServerSliderManager(app, parent=parent)
