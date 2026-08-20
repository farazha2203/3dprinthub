from __future__ import annotations

import json
import math
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from .openai_content import AIContentService
from .phase49_diagnostics import audit_event
from . import phase49_3c_image_pipeline as image_pipeline
from .phase49_3f_selected_image_ai import (
    generate_selected_image_text,
    install_image_pipeline_override,
    merge_selected_metadata,
)
from .phase49_3f_product_intelligence import generate_technical_intelligence
from . import phase49_3f_runtime_trace as runtime_trace

DESKTOP_COLUMNS = {
    "pricing_strategy": "TEXT NOT NULL DEFAULT 'legacy'",
    "fixed_price_material_name": "TEXT NOT NULL DEFAULT ''",
    "fixed_price_color_name": "TEXT NOT NULL DEFAULT ''",
    "pricing_inputs_json": "TEXT NOT NULL DEFAULT '{}'",
    "technical_summary_fa": "TEXT NOT NULL DEFAULT ''",
}


def _json_list(value):
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def _json_dict(value):
    if isinstance(value, dict):
        return dict(value)
    try:
        parsed = json.loads(value or "{}")
    except Exception:
        return {}
    return dict(parsed) if isinstance(parsed, dict) else {}


def _row_value(row, key, default=""):
    if row is None:
        return default
    if isinstance(row, dict):
        return row.get(key, default)
    try:
        return row[key]
    except Exception:
        return default


def _number(value, default=0.0):
    try:
        return max(0.0, float(str(value if value not in (None, "") else default).replace(",", "").strip() or default))
    except Exception:
        return float(default)


def _money(value) -> int:
    return max(0, int(round(_number(value, 0))))


def ensure_schema(db) -> None:
    columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
    for name, ddl in DESKTOP_COLUMNS.items():
        if name not in columns:
            db.conn.execute(f"ALTER TABLE products ADD COLUMN {name} {ddl}")
    db.conn.execute(
        """
        CREATE TABLE IF NOT EXISTS material_pricing_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            price_per_kg INTEGER NOT NULL DEFAULT 0,
            print_hourly_rate INTEGER NOT NULL DEFAULT 0,
            supervision_hourly_rate INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.conn.commit()


def _rate_map(db) -> dict[str, dict]:
    ensure_schema(db)
    output = {}
    for row in db.conn.execute(
        "SELECT material_name, price_per_kg, print_hourly_rate, supervision_hourly_rate, updated_at FROM material_pricing_rates ORDER BY material_name COLLATE NOCASE"
    ).fetchall():
        output[str(row["material_name"]).casefold()] = dict(row)
    return output


def _save_rate(db, material: str, price_per_kg: int, print_hourly: int, supervision_hourly: int) -> None:
    ensure_schema(db)
    existing = db.conn.execute(
        "SELECT id FROM material_pricing_rates WHERE material_name = ? COLLATE NOCASE",
        (material,),
    ).fetchone()
    if existing:
        db.conn.execute(
            "UPDATE material_pricing_rates SET price_per_kg=?, print_hourly_rate=?, supervision_hourly_rate=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (price_per_kg, print_hourly, supervision_hourly, existing["id"]),
        )
    else:
        db.conn.execute(
            "INSERT INTO material_pricing_rates(material_name,price_per_kg,print_hourly_rate,supervision_hourly_rate) VALUES(?,?,?,?)",
            (material, price_per_kg, print_hourly, supervision_hourly),
        )
    db.conn.commit()


class AIProgress:
    def __init__(self, parent, title: str, product_id: int | None = None):
        self.parent = parent
        self.product_id = product_id
        self.win = tk.Toplevel(parent)
        self.win.title(title)
        self.win.geometry("610x300")
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None)
        body = ttk.Frame(self.win, padding=16)
        body.pack(fill="both", expand=True)
        self.title_var = tk.StringVar(value=title)
        self.status_var = tk.StringVar(value="آماده شروع")
        self.detail_var = tk.StringVar(value="")
        ttk.Label(body, textvariable=self.title_var, font=("Tahoma", 13, "bold")).pack(anchor="w")
        ttk.Label(body, textvariable=self.status_var, font=("Tahoma", 10, "bold")).pack(anchor="w", pady=(12, 4))
        ttk.Label(body, textvariable=self.detail_var, style="SubHeader.TLabel", wraplength=560, justify="left").pack(anchor="w", fill="x")
        self.bar = ttk.Progressbar(body, mode="indeterminate")
        self.bar.pack(fill="x", pady=14)
        self.bar.start(12)
        self.steps = tk.Listbox(body, height=6, font=("Tahoma", 9), bd=0, highlightthickness=0)
        self.steps.pack(fill="both", expand=True)
        self.close_button = ttk.Button(body, text="بستن", command=self.close, state="disabled")
        self.close_button.pack(anchor="e", pady=(8, 0))

    def step(self, label: str, detail: str = ""):
        if not self.win.winfo_exists():
            return
        self.status_var.set(label)
        self.detail_var.set(detail)
        self.steps.insert("end", label)
        self.steps.see("end")
        self.win.update_idletasks()

    def done(self, label="✅ عملیات کامل شد", detail=""):
        if not self.win.winfo_exists():
            return
        self.bar.stop()
        self.status_var.set(label)
        self.detail_var.set(detail)
        self.steps.insert("end", label)
        self.steps.see("end")
        self.close_button.configure(state="normal")
        self.win.protocol("WM_DELETE_WINDOW", self.close)

    def fail(self, message: str):
        self.done("❌ عملیات متوقف شد", message)

    def close(self):
        try:
            self.win.destroy()
        except Exception:
            pass


def install(workspace_class, readiness_module=None) -> None:
    if getattr(workspace_class, "_phase49_3f_workspace_installed", False):
        return

    install_image_pipeline_override(image_pipeline)
    original_init = workspace_class.__init__
    original_commerce_ui = workspace_class._commerce_ui
    original_specs_ui = workspace_class._specs_ui
    original_reload = workspace_class.reload
    original_save = workspace_class.save

    def __init__(self, app, product_id: int):
        ensure_schema(app.db)
        self._phase49_3f_source_busy = False
        original_init(self, app, product_id)
        runtime_trace.event("workspace", "product-open", product_id=self.product_id)

    def _commerce_ui(self):
        original_commerce_ui(self)
        ensure_schema(self.db)
        self.pricing_strategy_var = tk.StringVar(value="dynamic")
        self.fixed_price_material_var = tk.StringVar(value="")
        self.fixed_price_color_var = tk.StringVar(value="")
        self.part_weight_grams_var = tk.StringVar(value="0")
        self.support_weight_grams_var = tk.StringVar(value="0")
        self.support_cost_multiplier_var = tk.StringVar(value="1")
        self.assembly_fee_var = tk.StringVar(value="0")
        self.standard_print_minutes_var = tk.StringVar(value="180")
        self.fine_print_minutes_var = tk.StringVar(value="360")

        used_rows = [int(child.grid_info().get("row", 0)) for child in self.commerce_tab.grid_slaves() if child.grid_info()]
        row = (max(used_rows) + 1) if used_rows else 10
        panel = ttk.LabelFrame(
            self.commerce_tab,
            text="قیمت‌گذاری حرفه‌ای — قطعی یا محاسباتی",
            padding=10,
            style="Card.TLabelframe",
        )
        panel.grid(row=row, column=0, columnspan=4, sticky="nsew", pady=(12, 0))
        panel.columnconfigure(1, weight=1)
        panel.columnconfigure(3, weight=1)
        self._phase49_3f_pricing_panel = panel

        mode = ttk.Frame(panel)
        mode.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 8))
        ttk.Label(mode, text="روش اعلام قیمت:", font=("Tahoma", 10, "bold")).pack(side="left", padx=4)
        ttk.Radiobutton(mode, text="● قیمت قطعی", variable=self.pricing_strategy_var, value="fixed", command=self._phase49_3f_refresh_pricing_state).pack(side="left", padx=8)
        ttk.Radiobutton(mode, text="● قیمت محاسباتی / محدوده", variable=self.pricing_strategy_var, value="dynamic", command=self._phase49_3f_refresh_pricing_state).pack(side="left", padx=8)
        ttk.Label(mode, text="قیمت ارسال در Checkout جدا محاسبه می‌شود.", style="SubHeader.TLabel").pack(side="right", padx=5)

        ttk.Label(panel, text="متریال قیمت قطعی").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.fixed_material_box = ttk.Combobox(panel, textvariable=self.fixed_price_material_var, state="readonly")
        self.fixed_material_box.grid(row=1, column=1, sticky="ew", padx=4, pady=4)
        ttk.Label(panel, text="رنگ قیمت قطعی").grid(row=1, column=2, sticky="w", padx=4, pady=4)
        self.fixed_color_box = ttk.Combobox(panel, textvariable=self.fixed_price_color_var, state="readonly")
        self.fixed_color_box.grid(row=1, column=3, sticky="ew", padx=4, pady=4)

        fields = [
            ("وزن خود قطعه (گرم)", self.part_weight_grams_var, "وزن واقعی قطعه بدون ساپورت"),
            ("وزن ساپورت (گرم)", self.support_weight_grams_var, "فیلامنت مصرفی ساپورت"),
            ("ضریب هزینه ساپورت", self.support_cost_multiplier_var, "مثلاً 2 یعنی هر گرم ساپورت دو برابر در هزینه متریال حساب شود"),
            ("هزینه اسمبلی (تومان)", self.assembly_fee_var, "پیش‌فرض صفر؛ اپراتور برای محصول وارد می‌کند"),
            ("زمان چاپ استاندارد (دقیقه)", self.standard_print_minutes_var, "برای کیفیت/صافی معمولی"),
            ("زمان چاپ سطح ظریف (دقیقه)", self.fine_print_minutes_var, "مثلاً 360 دقیقه به‌جای 180 دقیقه"),
        ]
        start = 2
        for index, (label, var, hint) in enumerate(fields):
            r = start + index // 2
            c = 0 if index % 2 == 0 else 2
            ttk.Label(panel, text=label).grid(row=r, column=c, sticky="w", padx=4, pady=4)
            holder = ttk.Frame(panel)
            holder.grid(row=r, column=c + 1, sticky="ew", padx=4, pady=4)
            ttk.Entry(holder, textvariable=var, width=16).pack(side="left")
            ttk.Label(holder, text=hint, style="SubHeader.TLabel", wraplength=280).pack(side="left", padx=6)

        rates_frame = ttk.LabelFrame(panel, text="نرخ متریال‌های انتخاب‌شده", padding=7)
        rates_frame.grid(row=5, column=0, columnspan=4, sticky="nsew", pady=(8, 4))
        rates_frame.columnconfigure(0, weight=1)
        rates_frame.rowconfigure(0, weight=1)
        self.material_rate_tree = ttk.Treeview(
            rates_frame,
            columns=("material", "kg", "print", "supervision", "updated"),
            show="headings",
            height=5,
        )
        for col, title, width in (
            ("material", "متریال", 150),
            ("kg", "قیمت هر کیلو (تومان)", 150),
            ("print", "نرخ ساعت چاپ", 130),
            ("supervision", "نرخ ساعت نظارت", 130),
            ("updated", "آخرین بروزرسانی", 150),
        ):
            self.material_rate_tree.heading(col, text=title)
            self.material_rate_tree.column(col, width=width, anchor="center")
        self.material_rate_tree.grid(row=0, column=0, sticky="nsew")
        ybar = ttk.Scrollbar(rates_frame, orient="vertical", command=self.material_rate_tree.yview)
        ybar.grid(row=0, column=1, sticky="ns")
        self.material_rate_tree.configure(yscrollcommand=ybar.set)
        rate_actions = ttk.Frame(rates_frame)
        rate_actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(rate_actions, text="✏ ویرایش نرخ متریال", command=self._phase49_3f_edit_material_rate, style="Primary.TButton").pack(side="left", padx=3)
        ttk.Button(rate_actions, text="↻ تازه‌سازی نرخ‌ها", command=self._phase49_3f_refresh_pricing_choices).pack(side="left", padx=3)
        ttk.Button(rate_actions, text="🧮 پیش‌نمایش قیمت‌ها", command=self._phase49_3f_price_preview, style="Success.TButton").pack(side="left", padx=3)
        self.pricing_preview_var = tk.StringVar(value="")
        ttk.Label(rate_actions, textvariable=self.pricing_preview_var, style="SubHeader.TLabel").pack(side="right", padx=5)
        self.commerce_tab.rowconfigure(row, weight=1)

    def _specs_ui(self):
        original_specs_ui(self)
        panel = ttk.LabelFrame(
            self.specs_tab,
            text="توضیحات فنی قابل فهم برای مشتری",
            padding=9,
            style="Card.TLabelframe",
        )
        panel.pack(fill="x", pady=(10, 0))
        self.technical_summary_text = tk.Text(panel, height=5, wrap="word")
        self.technical_summary_text.pack(fill="x")
        actions = ttk.Frame(panel)
        actions.pack(fill="x", pady=(6, 0))
        ttk.Button(
            actions,
            text="♻ بازخوانی منبع + ✨ ساخت توضیحات فنی با AI",
            command=self._phase49_3f_refresh_source_and_generate,
            style="Success.TButton",
        ).pack(side="left", padx=3)
        ttk.Label(
            actions,
            text="اول صفحه منبع دوباره استخراج می‌شود؛ سپس فقط متن و مشخصات واقعی برای AI ارسال می‌شود.",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=8)

    def _phase49_3f_selected_materials(self):
        if hasattr(self, "_selected_materials"):
            return list(self._selected_materials())
        row = self.db.product(self.product_id)
        return [str(x or "").strip() for x in _json_list(_row_value(row, "material_options_json", "[]")) if str(x or "").strip()]

    def _phase49_3f_selected_colors(self):
        if hasattr(self, "_selected_colors"):
            return [str(item.get("name") or "").strip() for item in self._selected_colors() if str(item.get("name") or "").strip()]
        row = self.db.product(self.product_id)
        output = []
        for item in _json_list(_row_value(row, "color_options_json", "[]")):
            if isinstance(item, dict):
                value = str(item.get("name") or "").strip()
            else:
                value = str(item or "").strip()
            if value:
                output.append(value)
        return output

    def _phase49_3f_refresh_pricing_choices(self):
        if not hasattr(self, "fixed_material_box"):
            return
        materials = self._phase49_3f_selected_materials()
        colors = self._phase49_3f_selected_colors()
        self.fixed_material_box.configure(values=materials)
        self.fixed_color_box.configure(values=colors)
        if materials and self.fixed_price_material_var.get() not in materials:
            self.fixed_price_material_var.set(materials[0])
        if colors and self.fixed_price_color_var.get() not in colors:
            self.fixed_price_color_var.set(colors[0])
        rates = _rate_map(self.db)
        for iid in self.material_rate_tree.get_children():
            self.material_rate_tree.delete(iid)
        for material in materials:
            rate = rates.get(material.casefold(), {})
            self.material_rate_tree.insert(
                "",
                "end",
                iid=material,
                values=(
                    material,
                    f"{int(rate.get('price_per_kg') or 0):,}",
                    f"{int(rate.get('print_hourly_rate') or 0):,}",
                    f"{int(rate.get('supervision_hourly_rate') or 0):,}",
                    str(rate.get("updated_at") or "—")[:19],
                ),
            )
        self._phase49_3f_refresh_pricing_state()

    def _phase49_3f_refresh_pricing_state(self):
        fixed = self.pricing_strategy_var.get() == "fixed"
        try:
            self.fixed_material_box.configure(state="readonly" if fixed else "disabled")
            self.fixed_color_box.configure(state="readonly" if fixed else "disabled")
        except Exception:
            pass
        self.pricing_preview_var.set(
            "قیمت قطعی: حداقل و حداکثر برابر می‌شوند." if fixed else "قیمت محاسباتی: مشتری متریال/رنگ/کیفیت را انتخاب می‌کند."
        )

    def _phase49_3f_edit_material_rate(self):
        materials = self._phase49_3f_selected_materials()
        if not materials:
            messagebox.showwarning("3DPrintHub", "ابتدا حداقل یک متریال را تیک بزن.", parent=self)
            return
        selected = self.material_rate_tree.selection() if hasattr(self, "material_rate_tree") else ()
        material = str(selected[0]) if selected else materials[0]
        current = _rate_map(self.db).get(material.casefold(), {})
        win = tk.Toplevel(self)
        win.title(f"نرخ قیمت — {material}")
        win.geometry("520x300")
        win.transient(self)
        win.grab_set()
        body = ttk.Frame(win, padding=14)
        body.pack(fill="both", expand=True)
        kg = tk.StringVar(value=str(int(current.get("price_per_kg") or 0)))
        hourly = tk.StringVar(value=str(int(current.get("print_hourly_rate") or 0)))
        supervision = tk.StringVar(value=str(int(current.get("supervision_hourly_rate") or 0)))
        ttk.Label(body, text=f"متریال: {material}", font=("Tahoma", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        for row_index, (label, var, hint) in enumerate((
            ("قیمت هر کیلو (تومان)", kg, "مثال: 2600000"),
            ("نرخ ساعت چاپ", hourly, "مثال PLA: 150000"),
            ("نرخ ساعت نظارت اپراتور", supervision, "مثال: 50000"),
        ), start=1):
            ttk.Label(body, text=label).grid(row=row_index, column=0, sticky="w", pady=6)
            holder = ttk.Frame(body)
            holder.grid(row=row_index, column=1, sticky="ew", pady=6)
            ttk.Entry(holder, textvariable=var, width=20).pack(side="left")
            ttk.Label(holder, text=hint, style="SubHeader.TLabel").pack(side="left", padx=6)
        body.columnconfigure(1, weight=1)

        def save_rate():
            try:
                _save_rate(self.db, material, _money(kg.get()), _money(hourly.get()), _money(supervision.get()))
            except Exception as exc:
                messagebox.showerror("3DPrintHub", str(exc), parent=win)
                return
            runtime_trace.event("pricing", "material-rate-save", product_id=self.product_id, detail={"material": material, "price_per_kg": _money(kg.get()), "print_hourly": _money(hourly.get()), "supervision_hourly": _money(supervision.get())})
            win.destroy()
            self._phase49_3f_refresh_pricing_choices()

        buttons = ttk.Frame(body)
        buttons.grid(row=4, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="انصراف", command=win.destroy).pack(side="right", padx=3)
        ttk.Button(buttons, text="ذخیره نرخ", command=save_rate, style="Success.TButton").pack(side="right", padx=3)

    def _phase49_3f_pricing_inputs(self):
        rates = _rate_map(self.db)
        materials = self._phase49_3f_selected_materials()
        material_rates = []
        for material in materials:
            rate = rates.get(material.casefold(), {})
            material_rates.append({
                "material": material,
                "price_per_kg": int(rate.get("price_per_kg") or 0),
                "print_hourly_rate": int(rate.get("print_hourly_rate") or 0),
                "supervision_hourly_rate": int(rate.get("supervision_hourly_rate") or 0),
            })
        profiles = [{"name": "استاندارد", "print_minutes": max(1, _money(self.standard_print_minutes_var.get()))}]
        fine = _money(self.fine_print_minutes_var.get())
        if fine:
            profiles.append({"name": "سطح ظریف", "print_minutes": fine})
        return {
            "part_weight_grams": _number(self.part_weight_grams_var.get()),
            "support_weight_grams": _number(self.support_weight_grams_var.get()),
            "support_cost_multiplier": max(0.01, _number(self.support_cost_multiplier_var.get(), 1)),
            "assembly_fee": _money(self.assembly_fee_var.get()),
            "fixed_material": self.fixed_price_material_var.get().strip(),
            "fixed_color": self.fixed_price_color_var.get().strip(),
            "material_rates": material_rates,
            "quality_profiles": profiles,
            "shipping_separate": True,
        }

    def _phase49_3f_price_preview(self):
        self._phase49_3f_refresh_pricing_choices()
        inputs = self._phase49_3f_pricing_inputs()
        part = float(inputs["part_weight_grams"])
        support = float(inputs["support_weight_grams"])
        multiplier = float(inputs["support_cost_multiplier"])
        assembly = int(inputs["assembly_fee"])
        charged = part + support * multiplier
        rows = []
        for rate in inputs["material_rates"]:
            for quality in inputs["quality_profiles"]:
                minutes = int(quality["print_minutes"])
                material_cost = round((float(rate["price_per_kg"]) / 1000.0) * charged)
                print_cost = round((float(rate["print_hourly_rate"]) * minutes) / 60.0)
                supervision_cost = round((float(rate["supervision_hourly_rate"]) * minutes) / 60.0)
                total = int(material_cost + print_cost + supervision_cost + assembly)
                rows.append((rate["material"], quality["name"], minutes, material_cost, print_cost, supervision_cost, assembly, total))
        if not rows:
            messagebox.showwarning("3DPrintHub", "برای پیش‌نمایش، متریال و نرخ‌های آن را مشخص کن.", parent=self)
            return
        win = tk.Toplevel(self)
        win.title("پیش‌نمایش فرمول قیمت")
        win.geometry("1120x520")
        win.transient(self)
        body = ttk.Frame(win, padding=12)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=f"گرم قابل محاسبه = {part:g} وزن قطعه + ({support:g} ساپورت × {multiplier:g}) = {charged:g} گرم", font=("Tahoma", 10, "bold")).pack(anchor="w", pady=(0, 8))
        tree = ttk.Treeview(body, columns=("m", "q", "t", "mat", "machine", "sup", "assembly", "total"), show="headings")
        headings = (("m", "متریال"), ("q", "کیفیت"), ("t", "دقیقه"), ("mat", "متریال"), ("machine", "چاپ"), ("sup", "نظارت"), ("assembly", "اسمبلی"), ("total", "جمع قبل از ارسال"))
        for key, title in headings:
            tree.heading(key, text=title)
            tree.column(key, width=125, anchor="center")
        tree.pack(fill="both", expand=True)
        for row in rows:
            tree.insert("", "end", values=(row[0], row[1], row[2], f"{row[3]:,}", f"{row[4]:,}", f"{row[5]:,}", f"{row[6]:,}", f"{row[7]:,}"))
        ttk.Label(body, text="هزینه ارسال/بسته‌بندی در Checkout جداست. سرور قوانین حداقل سفارش و تخفیف فعال را نیز اعمال می‌کند.", style="SubHeader.TLabel").pack(anchor="w", pady=(8, 0))
        runtime_trace.event("pricing", "preview", product_id=self.product_id, detail={"rows": len(rows), "chargeable_grams": charged})

    def reload(self):
        original_reload(self)
        ensure_schema(self.db)
        row = self.db.product(self.product_id)
        if row is None:
            return
        if hasattr(self, "pricing_strategy_var"):
            strategy = str(_row_value(row, "pricing_strategy", "legacy") or "legacy")
            if strategy not in {"fixed", "dynamic"}:
                minimum = _money(_row_value(row, "price_min", 0))
                maximum = _money(_row_value(row, "price_max", 0))
                strategy = "fixed" if int(_row_value(row, "price_is_final", 0) or 0) and minimum and minimum == maximum else "dynamic"
            self.pricing_strategy_var.set(strategy)
            self.fixed_price_material_var.set(str(_row_value(row, "fixed_price_material_name", "") or ""))
            self.fixed_price_color_var.set(str(_row_value(row, "fixed_price_color_name", "") or ""))
            inputs = _json_dict(_row_value(row, "pricing_inputs_json", "{}"))
            self.part_weight_grams_var.set(str(inputs.get("part_weight_grams", 0)))
            self.support_weight_grams_var.set(str(inputs.get("support_weight_grams", 0)))
            self.support_cost_multiplier_var.set(str(inputs.get("support_cost_multiplier", 1)))
            self.assembly_fee_var.set(str(inputs.get("assembly_fee", 0)))
            profiles = [x for x in (inputs.get("quality_profiles") or []) if isinstance(x, dict)]
            standard = next((x for x in profiles if str(x.get("name") or "") == "استاندارد"), profiles[0] if profiles else {})
            fine = next((x for x in profiles if str(x.get("name") or "") == "سطح ظریف"), {})
            self.standard_print_minutes_var.set(str(standard.get("print_minutes") or 180))
            self.fine_print_minutes_var.set(str(fine.get("print_minutes") or 360))
            self._phase49_3f_refresh_pricing_choices()
        if hasattr(self, "technical_summary_text"):
            self.technical_summary_text.delete("1.0", "end")
            self.technical_summary_text.insert("1.0", str(_row_value(row, "technical_summary_fa", "") or ""))

    def save(self, silent=False):
        ok = original_save(self, silent=True)
        if not ok:
            return False
        ensure_schema(self.db)
        strategy = self.pricing_strategy_var.get() if hasattr(self, "pricing_strategy_var") else "legacy"
        inputs = self._phase49_3f_pricing_inputs() if hasattr(self, "pricing_strategy_var") else {}
        values = {
            "pricing_strategy": strategy,
            "fixed_price_material_name": self.fixed_price_material_var.get().strip() if hasattr(self, "fixed_price_material_var") else "",
            "fixed_price_color_name": self.fixed_price_color_var.get().strip() if hasattr(self, "fixed_price_color_var") else "",
            "pricing_inputs_json": json.dumps(inputs, ensure_ascii=False),
            "technical_summary_fa": self.technical_summary_text.get("1.0", "end").strip() if hasattr(self, "technical_summary_text") else str(_row_value(self.db.product(self.product_id), "technical_summary_fa", "") or ""),
        }
        if strategy == "fixed" and hasattr(self, "price_min_var"):
            fixed = _money(self.price_min_var.get())
            values.update({"price_min": fixed, "price_max": fixed, "final_price": fixed, "price_is_final": 1})
            self.price_max_var.set(str(fixed))
        elif strategy == "dynamic":
            values["price_is_final"] = 0
        self.db.update_product(self.product_id, values)
        self.row = self.db.product(self.product_id)
        runtime_trace.event("pricing", "product-pricing-save", product_id=self.product_id, detail={"strategy": strategy, "inputs": inputs})
        if not silent:
            self.footer_status.set("قیمت‌گذاری، نرخ‌ها و مشخصات فنی ذخیره شد")
        return True

    def _phase49_3f_progress_step(self, progress, label, detail=""):
        self.after(0, lambda: progress.step(label, detail))

    def _phase49_3e_run_ai(self, scope: str):
        if self._phase49_3e_busy or getattr(self, "_ai_busy", False):
            self.footer_status.set("یک درخواست هوش مصنوعی در حال اجرا است.")
            return
        provider, key, model = self._phase49_3e_provider()
        if not key:
            messagebox.showwarning("3DPrintHub", f"API Key برای {provider} تنظیم نشده است. از بخش هوش مصنوعی Provider/Model را انتخاب و ذخیره کن.", parent=self)
            return
        try:
            self.save(silent=True)
        except Exception:
            pass
        row = self.db.product(self.product_id)
        selected = image_pipeline.cap_unique_urls(_json_list(_row_value(row, "selected_images_json", "[]")))
        source = dict(self._source_for_ai() or {})
        if hasattr(self, "_selected_materials"):
            source["selected_materials"] = list(self._selected_materials())
        if hasattr(self, "_selected_colors"):
            source["selected_colors"] = [str(item.get("name") or "") for item in self._selected_colors()]
        categories = self.app.get_all_categories()
        progress = AIProgress(self, "سئو تصاویر منتخب" if scope == "images" else "تکمیل هوشمند محصول", self.product_id)
        self._phase49_3e_busy = True
        started = time.perf_counter()
        runtime_trace.event("ai", "task-start", product_id=self.product_id, provider=provider, model=model, detail={"scope": scope, "selected_count": len(selected), "image_payload": False})
        self._phase49_3f_progress_step(progress, "🔌 در حال اتصال به هوش مصنوعی…", "اگر اتصال تا ۳۰ ثانیه برقرار نشود، عملیات متوقف می‌شود.")

        def worker():
            try:
                service = AIContentService(key, model, provider, product_id=self.product_id)
                probe = service.client.probe_connection(timeout=30)
                self._phase49_3f_progress_step(progress, "✅ اتصال برقرار شد", f"Provider={provider} • models={int(probe.get('models_count') or 0):,}")
                if scope == "images":
                    if not selected:
                        raise RuntimeError("هیچ تصویر منتخبی برای سایت وجود ندارد.")
                    self._phase49_3f_progress_step(progress, "📤 داده متنی تصاویر منتخب ارسال شد", f"{len(selected)} slot منتخب • بدون ارسال URL/فایل/پیکسل عکس")
                    pack = generate_selected_image_text(service, row, selected)
                    self._phase49_3f_progress_step(progress, "📥 پاسخ هوش مصنوعی دریافت شد", f"{len(pack.get('items') or [])} رکورد Metadata")
                    self.after(0, lambda: self._phase49_3f_apply_selected_image_ai(pack, selected, progress, provider, model, started))
                else:
                    self._phase49_3f_progress_step(progress, "📤 دیتای محصول ارسال شد", "فقط متن/مشخصات؛ تصویر برای این Task Center ارسال نمی‌شود.")
                    pack = service.enrich_product(source, categories, image_count=len(selected), image_urls=[], mode="commerce")
                    self._phase49_3f_progress_step(progress, "📥 پاسخ هوش مصنوعی دریافت شد", "در حال اعتبارسنجی و ثبت خروجی")
                    self.after(0, lambda: self._phase49_3f_apply_full_ai(pack, scope, progress, provider, model, started))
            except Exception as exc:
                elapsed = int((time.perf_counter() - started) * 1000)
                runtime_trace.event("ai", "task-error", status="error", product_id=self.product_id, provider=provider, model=model, elapsed_ms=elapsed, message=str(exc), detail={"scope": scope})
                audit_event("ai", "phase49_3f_task_error", product_id=self.product_id, status="error", level="ERROR", message=f"scope={scope} provider={provider} model={model}: {exc}", source_file="catalog_center/app/phase49_3f_workspace.py")
                self.after(0, lambda: progress.fail(str(exc)))
                self.after(0, lambda: setattr(self, "_phase49_3e_busy", False))

        threading.Thread(target=worker, daemon=True).start()

    def _phase49_3f_apply_selected_image_ai(self, pack, selected, progress, provider, model, started):
        try:
            current = self.db.product(self.product_id)
            existing = _json_list(_row_value(current, image_pipeline.IMAGE_METADATA_COLUMN, "[]"))
            merged = merge_selected_metadata(existing, selected, pack)
            result_by_slot = {int(item.get("slot") or 0): item for item in (pack.get("items") or []) if isinstance(item, dict)}
            old_alts = [str(x or "").strip() for x in _json_list(_row_value(current, "image_alt_texts_json", "[]"))]
            alts = []
            for slot, _url in enumerate(selected, 1):
                generated = str((result_by_slot.get(slot) or {}).get("alt_text") or "").strip()
                old = old_alts[slot - 1] if slot - 1 < len(old_alts) else ""
                alts.append(generated or old)
            self.db.update_product(self.product_id, {
                image_pipeline.IMAGE_METADATA_COLUMN: json.dumps(merged, ensure_ascii=False),
                "image_alt_texts_json": json.dumps(alts, ensure_ascii=False),
            })
            self._phase49_3f_progress_step(progress, "💾 Metadata فقط برای تصاویر منتخب ثبت شد", f"تصاویر خارج از انتخاب: دست‌نخورده")
            finalized = image_pipeline.finalize_selected_images(self.db, self.product_id)
            self._phase49_3f_progress_step(progress, "🖼 فایل‌های SEO منتخب نهایی شدند", f"kept={finalized.get('kept')} • preserved_unselected={finalized.get('preserved_unselected_metadata', 0)}")
            try:
                self.reload()
            except Exception:
                pass
            try:
                self._phase49_3e_refresh_tasks()
            except Exception:
                pass
            elapsed = int((time.perf_counter() - started) * 1000)
            runtime_trace.event("ai", "selected-image-seo-done", product_id=self.product_id, provider=provider, model=model, elapsed_ms=elapsed, detail={"selected_count": len(selected), "generated_count": len(pack.get("items") or []), "no_image_payload": True})
            progress.done("✅ سئو تصاویر منتخب کامل شد", "هیچ تصویر، URL تصویر یا فایل عکس برای AI ارسال نشد.")
        except Exception as exc:
            runtime_trace.event("ai", "selected-image-seo-apply-error", status="error", product_id=self.product_id, provider=provider, model=model, message=str(exc))
            progress.fail(str(exc))
        finally:
            self._phase49_3e_busy = False

    def _phase49_3f_apply_full_ai(self, pack, scope, progress, provider, model, started):
        try:
            self._phase49_3e_apply_ai_result(pack, scope)
            elapsed = int((time.perf_counter() - started) * 1000)
            runtime_trace.event("ai", "task-done", product_id=self.product_id, provider=provider, model=model, elapsed_ms=elapsed, detail={"scope": scope, "image_payload": False})
            progress.done("✅ داده AI اعتبارسنجی و ثبت شد")
        except Exception as exc:
            progress.fail(str(exc))
            runtime_trace.event("ai", "task-apply-error", status="error", product_id=self.product_id, provider=provider, model=model, message=str(exc))
        finally:
            self._phase49_3e_busy = False

    def _phase49_3e_open_image_editor(self):
        row = self.db.product(self.product_id)
        selected = image_pipeline.cap_unique_urls(_json_list(_row_value(row, "selected_images_json", "[]")))
        if not selected:
            messagebox.showwarning("3DPrintHub", "هیچ تصویر منتخبی وجود ندارد.", parent=self)
            return
        original_items = [dict(x) for x in _json_list(_row_value(row, image_pipeline.IMAGE_METADATA_COLUMN, "[]")) if isinstance(x, dict)]
        by_url = {str(item.get("source_url") or ""): item for item in original_items if item.get("source_url")}
        working = {url: dict(by_url.get(url) or {"source_url": url}) for url in selected}

        win = tk.Toplevel(self)
        win.title("ویرایش Metadata تصاویر منتخب")
        win.geometry("1120x720")
        win.transient(self)
        body = ttk.Frame(win, padding=10)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        listing = tk.Listbox(left, width=27, exportselection=False)
        listing.pack(fill="y", expand=True)
        for index, _url in enumerate(selected, 1):
            listing.insert("end", f"تصویر منتخب {index}")
        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(1, weight=1)
        vars_map = {key: tk.StringVar() for key in ("seo_filename", "alt_text", "title", "creator", "source_page_url", "license_name", "license_url")}
        caption = tk.Text(right, height=5, wrap="word")
        keywords = tk.Text(right, height=4, wrap="word")
        labels = (
            ("نام فایل SEO", "seo_filename"), ("Alt فارسی", "alt_text"), ("Title تصویر", "title"),
            ("Creator/Designer", "creator"), ("صفحه منبع", "source_page_url"), ("نام مجوز", "license_name"), ("URL مجوز", "license_url"),
        )
        for r, (label, key) in enumerate(labels):
            ttk.Label(right, text=label).grid(row=r, column=0, sticky="w", padx=4, pady=4)
            ttk.Entry(right, textvariable=vars_map[key]).grid(row=r, column=1, sticky="ew", padx=4, pady=4)
        ttk.Label(right, text="Caption").grid(row=7, column=0, sticky="nw", padx=4, pady=4)
        caption.grid(row=7, column=1, sticky="ew", padx=4, pady=4)
        ttk.Label(right, text="Keywords (هر خط یک مورد)").grid(row=8, column=0, sticky="nw", padx=4, pady=4)
        keywords.grid(row=8, column=1, sticky="ew", padx=4, pady=4)
        current_index = {"value": 0}

        def save_current():
            index = current_index["value"]
            if index < 0 or index >= len(selected):
                return
            url = selected[index]
            item = working[url]
            override_fields = set(item.get("_operator_override_fields") or [])
            for key, var in vars_map.items():
                value = var.get().strip()
                if key == "seo_filename" and value:
                    value = Path(value).name.replace("/", "-").replace("\\", "-")
                    if not value.lower().endswith(".webp"):
                        value = Path(value).stem + ".webp"
                item[key] = value
                if value:
                    override_fields.add(key)
            item["caption"] = caption.get("1.0", "end").strip()
            item["keywords"] = [x.strip().lstrip("#") for x in keywords.get("1.0", "end").splitlines() if x.strip()]
            if item["caption"]:
                override_fields.add("caption")
            if item["keywords"]:
                override_fields.add("keywords")
            item["_operator_override_fields"] = sorted(override_fields)

        def load_index(index):
            save_current()
            current_index["value"] = index
            item = working[selected[index]]
            for key, var in vars_map.items():
                var.set(str(item.get(key) or ""))
            caption.delete("1.0", "end"); caption.insert("1.0", str(item.get("caption") or ""))
            keywords.delete("1.0", "end"); keywords.insert("1.0", "\n".join(str(x) for x in (item.get("keywords") or [])))

        def on_select(_event=None):
            sel = listing.curselection()
            if sel:
                load_index(int(sel[0]))

        def save_all():
            save_current()
            # Preserve every unselected metadata record. Only selected records are replaced.
            unselected = [item for item in original_items if str(item.get("source_url") or "") not in set(selected)]
            merged = [*unselected, *[working[url] for url in selected]]
            self.db.update_product(self.product_id, {image_pipeline.IMAGE_METADATA_COLUMN: json.dumps(merged, ensure_ascii=False)})
            try:
                result = image_pipeline.finalize_selected_images(self.db, self.product_id)
            except Exception as exc:
                messagebox.showerror("3DPrintHub", f"Metadata ذخیره شد اما ساخت فایل SEO کامل نشد:\n{exc}", parent=win)
                return
            runtime_trace.event("images", "manual-metadata-save", product_id=self.product_id, detail={"selected": len(selected), "preserved_unselected": len(unselected)})
            win.destroy()
            self.reload()
            self._phase49_3e_refresh_tasks()
            messagebox.showinfo("3DPrintHub", f"✅ Metadata {len(selected)} تصویر منتخب ثبت شد.\n{result.get('preserved_unselected_metadata', 0)} رکورد خارج از انتخاب حفظ شد.", parent=self)

        listing.bind("<<ListboxSelect>>", on_select)
        buttons = ttk.Frame(body)
        buttons.grid(row=1, column=0, columnspan=2, sticky="e", pady=(8, 0))
        ttk.Button(buttons, text="انصراف", command=win.destroy).pack(side="right", padx=3)
        ttk.Button(buttons, text="ذخیره و بازسازی SEO منتخب‌ها", command=save_all, style="Success.TButton").pack(side="right", padx=3)
        listing.selection_set(0)
        current_index["value"] = -1
        load_index(0)

    def _phase49_3f_refresh_source_and_generate(self):
        if self._phase49_3f_source_busy:
            self.footer_status.set("بازخوانی/تحلیل منبع در حال اجرا است.")
            return
        self.save(silent=True)
        before = self.db.product(self.product_id)
        marker = str(_row_value(before, "last_refetched_at", "") or _row_value(before, "updated_at", "") or "")
        progress = AIProgress(self, "بازخوانی منبع و ساخت توضیحات فنی", self.product_id)
        progress.step("🌐 بازخوانی صفحه منبع شروع شد", str(_row_value(before, "source_url", "") or ""))
        runtime_trace.event("source", "refresh-start", product_id=self.product_id, detail={"source_url": str(_row_value(before, "source_url", "") or "")})
        self._phase49_3f_source_busy = True
        try:
            self.refetch()
        except Exception as exc:
            self._phase49_3f_source_busy = False
            progress.fail(str(exc))
            return
        started = time.perf_counter()

        def poll():
            row = self.db.product(self.product_id)
            current = str(_row_value(row, "last_refetched_at", "") or _row_value(row, "updated_at", "") or "")
            if current and current != marker:
                progress.step("✅ اطلاعات منبع بروزرسانی شد", "در حال اتصال به AI برای تبدیل داده خام به توضیح فنی قابل فهم")
                return self._phase49_3f_generate_technical(progress)
            if time.perf_counter() - started >= 60:
                self._phase49_3f_source_busy = False
                progress.fail("بازخوانی منبع تا ۶۰ ثانیه کامل نشد. درخواست AI ارسال نشد؛ جزئیات را در فولدر لاگ بررسی کن.")
                runtime_trace.event("source", "refresh-timeout", status="error", product_id=self.product_id, elapsed_ms=int((time.perf_counter() - started) * 1000))
                return
            self.after(750, poll)

        self.after(750, poll)

    def _phase49_3f_generate_technical(self, progress):
        provider, key, model = self._phase49_3e_provider()
        if not key:
            self._phase49_3f_source_busy = False
            progress.fail(f"API Key برای {provider} تنظیم نشده است.")
            return
        row = self.db.product(self.product_id)
        source = dict(self._source_for_ai() or {})
        progress.step("🔌 در حال اتصال به هوش مصنوعی…", "Timeout اتصال: ۳۰ ثانیه")
        started = time.perf_counter()

        def worker():
            try:
                service = AIContentService(key, model, provider, product_id=self.product_id)
                service.client.probe_connection(timeout=30)
                self._phase49_3f_progress_step(progress, "✅ اتصال برقرار شد")
                self._phase49_3f_progress_step(progress, "📤 متن و مشخصات استخراج‌شده منبع ارسال شد", "هیچ تصویر یا فایل محصول برای AI ارسال نمی‌شود.")
                result = generate_technical_intelligence(service, row, source)
                self._phase49_3f_progress_step(progress, "📥 توضیحات فنی دریافت شد", "قبل از ثبت، اپراتور آن را بازبینی می‌کند.")
                self.after(0, lambda: self._phase49_3f_review_technical(result, progress, provider, model, started))
            except Exception as exc:
                self._phase49_3f_source_busy = False
                runtime_trace.event("source-ai", "technical-error", status="error", product_id=self.product_id, provider=provider, model=model, message=str(exc))
                self.after(0, lambda: progress.fail(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _phase49_3f_review_technical(self, result, progress, provider, model, started):
        win = tk.Toplevel(self)
        win.title("بازبینی توضیحات فنی AI")
        win.geometry("980x720")
        win.transient(self)
        body = ttk.Frame(win, padding=12)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="این خروجی از داده استخراج‌شده منبع ساخته شده است. قبل از ثبت می‌توانی آن را ویرایش کنی.", font=("Tahoma", 10, "bold")).pack(anchor="w", pady=(0, 8))
        ttk.Label(body, text="خلاصه فنی برای صفحه محصول").pack(anchor="w")
        summary = tk.Text(body, height=8, wrap="word"); summary.pack(fill="x", pady=(2, 8)); summary.insert("1.0", result.get("technical_summary_fa") or "")
        ttk.Label(body, text="کاربرد محصول").pack(anchor="w")
        use = tk.Text(body, height=5, wrap="word"); use.pack(fill="x", pady=(2, 8)); use.insert("1.0", result.get("use_description_fa") or "")
        ttk.Label(body, text="ویژگی‌های فنی — هر خط: عنوان = مقدار").pack(anchor="w")
        features = tk.Text(body, height=10, wrap="word"); features.pack(fill="both", expand=True, pady=(2, 8))
        features.insert("1.0", "\n".join(f"{item['key']} = {item['value']}" for item in result.get("technical_features") or []))
        notes = result.get("operator_notes") or []
        if notes:
            ttk.Label(body, text="نیازمند بررسی اپراتور: " + " | ".join(notes[:4]), style="SubHeader.TLabel", wraplength=900).pack(anchor="w", pady=4)

        def apply():
            feature_dict = {}
            for raw in features.get("1.0", "end").splitlines():
                if "=" not in raw:
                    continue
                key, value = raw.split("=", 1)
                if key.strip() and value.strip():
                    feature_dict[key.strip()] = value.strip()
            values = {
                "technical_summary_fa": summary.get("1.0", "end").strip(),
                "use_description": use.get("1.0", "end").strip(),
                "technical_features_json": json.dumps(feature_dict, ensure_ascii=False),
            }
            self.db.update_product(self.product_id, values)
            runtime_trace.event("source-ai", "technical-applied", product_id=self.product_id, provider=provider, model=model, elapsed_ms=int((time.perf_counter() - started) * 1000), detail={"feature_count": len(feature_dict)})
            self._phase49_3f_source_busy = False
            win.destroy()
            self.reload()
            progress.done("✅ توضیحات فنی بازبینی و ثبت شد")

        actions = ttk.Frame(body); actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="رد کردن", command=lambda: (setattr(self, "_phase49_3f_source_busy", False), win.destroy(), progress.done("خروجی AI ثبت نشد"))).pack(side="right", padx=3)
        ttk.Button(actions, text="تأیید و ثبت", command=apply, style="Success.TButton").pack(side="right", padx=3)

    workspace_class.__init__ = __init__
    workspace_class._commerce_ui = _commerce_ui
    workspace_class._specs_ui = _specs_ui
    workspace_class.reload = reload
    workspace_class.save = save
    workspace_class._phase49_3f_selected_materials = _phase49_3f_selected_materials
    workspace_class._phase49_3f_selected_colors = _phase49_3f_selected_colors
    workspace_class._phase49_3f_refresh_pricing_choices = _phase49_3f_refresh_pricing_choices
    workspace_class._phase49_3f_refresh_pricing_state = _phase49_3f_refresh_pricing_state
    workspace_class._phase49_3f_edit_material_rate = _phase49_3f_edit_material_rate
    workspace_class._phase49_3f_pricing_inputs = _phase49_3f_pricing_inputs
    workspace_class._phase49_3f_price_preview = _phase49_3f_price_preview
    workspace_class._phase49_3f_progress_step = _phase49_3f_progress_step
    workspace_class._phase49_3e_run_ai = _phase49_3e_run_ai
    workspace_class._phase49_3f_apply_selected_image_ai = _phase49_3f_apply_selected_image_ai
    workspace_class._phase49_3f_apply_full_ai = _phase49_3f_apply_full_ai
    workspace_class._phase49_3e_open_image_editor = _phase49_3e_open_image_editor
    workspace_class._phase49_3f_refresh_source_and_generate = _phase49_3f_refresh_source_and_generate
    workspace_class._phase49_3f_generate_technical = _phase49_3f_generate_technical
    workspace_class._phase49_3f_review_technical = _phase49_3f_review_technical
    workspace_class._phase49_3f_workspace_installed = True
