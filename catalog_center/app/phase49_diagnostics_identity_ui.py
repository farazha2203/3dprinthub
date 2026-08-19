from __future__ import annotations

import getpass
import json
import tkinter as tk
from tkinter import messagebox, ttk

from .phase49_diagnostics import recent_ai_requests, recent_app_events
from .phase49_diagnostics_identity import session_snapshot


def install(app_class) -> None:
    if getattr(app_class, "_phase49_diagnostics_identity_ui_installed", False):
        return
    original_runs_ui = app_class._runs_ui

    def _runs_ui(self):
        original_runs_ui(self)
        box = ttk.LabelFrame(self.runs_tab, text="هویت اپراتور و Session", padding=8, style="Card.TLabelframe")
        box.pack(fill="x", pady=(7, 0))
        self._phase49_operator_name = tk.StringVar(
            value=str(self.db.setting("operator_name", "") or getpass.getuser() or "")
        )
        ttk.Label(box, text="نام اپراتور").pack(side="left", padx=4)
        ttk.Entry(box, textvariable=self._phase49_operator_name, width=28).pack(side="left", padx=4)

        def save_operator():
            name = self._phase49_operator_name.get().strip()[:120]
            self.db.set_setting("operator_name", name)
            snap = session_snapshot(self.db)
            messagebox.showinfo(
                "3DPrintHub",
                f"اپراتور ذخیره شد: {snap['operator']}\nسیستم: {snap['workstation']}\nSession: {snap['session_id']}",
                parent=self,
            )

        ttk.Button(box, text="ذخیره اپراتور", command=save_operator, style="Primary.TButton").pack(side="left", padx=4)
        snap = session_snapshot(self.db)
        ttk.Label(
            box,
            text=f"سیستم: {snap['workstation']}  |  Session: {snap['session_id'][:12]}…",
            style="SubHeader.TLabel",
        ).pack(side="right", padx=6)

    def _copy(self, value: str):
        self.clipboard_clear()
        self.clipboard_append(str(value or ""))
        self.update_idletasks()

    def open_phase49_app_log(self):
        win = tk.Toplevel(self)
        win.title("لاگ برنامه و تغییرات | 3DPrintHub")
        win.geometry("1540x800")
        cols = ("id", "time", "operator", "workstation", "level", "area", "action", "status", "product", "source", "message")
        tree = ttk.Treeview(win, columns=cols, show="headings", selectmode="browse")
        specs = [
            ("id", "ID", 55), ("time", "زمان", 145), ("operator", "اپراتور", 115),
            ("workstation", "سیستم", 120), ("level", "Level", 65), ("area", "بخش", 90),
            ("action", "عملیات", 120), ("status", "وضعیت", 75), ("product", "Product", 70),
            ("source", "فایل/منبع", 220), ("message", "پیام", 440),
        ]
        for key, title, width in specs:
            tree.heading(key, text=title)
            tree.column(key, width=width, anchor="w" if key in {"source", "message"} else "center")
        tree.pack(fill="both", expand=True, padx=10, pady=(10, 4))
        details = tk.Text(win, height=10, wrap="word", font=("Consolas", 9))
        details.pack(fill="x", padx=10, pady=(0, 4))
        rows = {}

        def refresh():
            tree.delete(*tree.get_children())
            rows.clear()
            for row in recent_app_events(1500):
                iid = str(row["id"])
                rows[iid] = row
                tree.insert("", "end", iid=iid, values=(
                    row.get("id"), row.get("created_at"), row.get("operator") or "",
                    row.get("workstation") or "", row.get("level"), row.get("area"),
                    row.get("action"), row.get("status"), row.get("product_id") or "",
                    row.get("source_file") or "", row.get("message") or "",
                ))

        def selected(_event=None):
            if not tree.selection():
                return
            row = rows.get(tree.selection()[0]) or {}
            details.delete("1.0", "end")
            details.insert("1.0", json.dumps(row, ensure_ascii=False, indent=2, default=str))

        tree.bind("<<TreeviewSelect>>", selected)
        actions = ttk.Frame(win, padding=8); actions.pack(fill="x")
        ttk.Button(actions, text="بروزرسانی", command=refresh).pack(side="left", padx=3)
        ttk.Button(actions, text="کپی جزئیات", command=lambda: _copy(self, details.get("1.0", "end").strip())).pack(side="left", padx=3)
        ttk.Button(actions, text="بستن", command=win.destroy).pack(side="right", padx=3)
        refresh()

    def open_phase49_ai_log(self):
        win = tk.Toplevel(self)
        win.title("لاگ درخواست‌های AI | 3DPrintHub")
        win.geometry("1580x820")
        cols = ("id", "time", "operator", "provider", "model", "operation", "http", "status", "tokens", "cost", "request")
        tree = ttk.Treeview(win, columns=cols, show="headings", selectmode="browse")
        specs = [
            ("id", "ID", 50), ("time", "زمان", 145), ("operator", "اپراتور", 110),
            ("provider", "Provider", 85), ("model", "Model", 220), ("operation", "عملیات", 145),
            ("http", "HTTP", 60), ("status", "وضعیت", 75), ("tokens", "Tokens", 75),
            ("cost", "هزینه", 150), ("request", "Request ID", 300),
        ]
        for key, title, width in specs:
            tree.heading(key, text=title)
            tree.column(key, width=width, anchor="w" if key in {"model", "request"} else "center")
        tree.pack(fill="both", expand=True, padx=10, pady=(10, 4))
        details = tk.Text(win, height=11, wrap="word", font=("Consolas", 9))
        details.pack(fill="x", padx=10, pady=(0, 4))
        rows = {}

        def refresh():
            tree.delete(*tree.get_children())
            rows.clear()
            for row in recent_ai_requests(1500):
                iid = str(row["id"]); rows[iid] = row
                if row.get("cost_irt") is not None:
                    cost = f"{float(row['cost_irt']):,.0f} تومان"
                elif row.get("cost_usd") is not None:
                    cost = f"${float(row['cost_usd']):.6f}"
                else:
                    cost = "—"
                tree.insert("", "end", iid=iid, values=(
                    row.get("id"), row.get("created_at"), row.get("operator") or "",
                    row.get("provider"), row.get("model"), row.get("operation"),
                    row.get("http_status") or "", row.get("status"), row.get("total_tokens") or 0,
                    cost, row.get("request_id") or "",
                ))

        def selected(_event=None):
            if not tree.selection():
                return
            row = rows.get(tree.selection()[0]) or {}
            details.delete("1.0", "end")
            details.insert("1.0", json.dumps(row, ensure_ascii=False, indent=2, default=str))

        tree.bind("<<TreeviewSelect>>", selected)
        actions = ttk.Frame(win, padding=8); actions.pack(fill="x")
        ttk.Button(actions, text="بروزرسانی", command=refresh).pack(side="left", padx=3)
        ttk.Button(actions, text="کپی Request ID", command=lambda: _copy(self, (rows.get(tree.selection()[0]) or {}).get("request_id", "") if tree.selection() else "")).pack(side="left", padx=3)
        ttk.Button(actions, text="کپی جزئیات", command=lambda: _copy(self, details.get("1.0", "end").strip())).pack(side="left", padx=3)
        ttk.Button(actions, text="بستن", command=win.destroy).pack(side="right", padx=3)
        refresh()

    app_class._runs_ui = _runs_ui
    app_class.open_phase49_app_log = open_phase49_app_log
    app_class.open_phase49_ai_log = open_phase49_ai_log
    app_class._phase49_diagnostics_identity_ui_installed = True
