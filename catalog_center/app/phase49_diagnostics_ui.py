from __future__ import annotations

import getpass
import json
import os
import traceback
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from .phase49_diagnostics import (
    audit_event,
    export_diagnostic_bundle,
    recent_ai_requests,
    recent_app_events,
    update_ai_cost,
)
from .secure_secrets import get_provider_key
from .ai_providers import AIProviderClient


def install_database(database_class) -> None:
    if getattr(database_class, "_phase49_diagnostics_installed", False):
        return
    original_update = database_class.update_product
    original_history = database_class.save_history

    def update_product(self, product_id, values):
        keys = sorted(str(key) for key in (values or {}).keys() if str(key) != "updated_at")
        result = original_update(self, product_id, values)
        if keys:
            audit_event(
                "product",
                "update",
                product_id=int(product_id),
                source_file="catalog_center/app/db.py",
                message=f"user={getpass.getuser()} changed_fields={','.join(keys)}",
                detail={"changed_fields": keys, "operator": getpass.getuser()},
            )
        return result

    def save_history(self, product_id, event_type, before=None, after=None, note=""):
        result = original_history(self, product_id, event_type, before, after, note)
        audit_event(
            "product_history",
            str(event_type),
            product_id=int(product_id),
            source_file="catalog_center/app/db.py",
            message=f"user={getpass.getuser()} note={str(note or '')[:500]}",
            detail={"operator": getpass.getuser()},
        )
        return result

    database_class.update_product = update_product
    database_class.save_history = save_history
    database_class._phase49_diagnostics_installed = True


def install_base_app(app_class, data_root: str | Path) -> None:
    if getattr(app_class, "_phase49_diagnostics_ui_installed", False):
        return
    original_runs_ui = app_class._runs_ui
    original_callback_error = app_class.report_callback_exception

    def _runs_ui(self):
        original_runs_ui(self)
        bar = ttk.LabelFrame(self.runs_tab, text="لاگ برنامه و عیب‌یابی Phase49", padding=10, style="Card.TLabelframe")
        bar.pack(fill="x", pady=(8, 0))
        ttk.Button(bar, text="لاگ دیتابیسی برنامه", command=self.open_phase49_app_log, style="Primary.TButton").pack(side="left", padx=3)
        ttk.Button(bar, text="درخواست‌های AI", command=self.open_phase49_ai_log, style="Primary.TButton").pack(side="left", padx=3)
        ttk.Button(bar, text="تکمیل هزینه AvalAI", command=self.refresh_phase49_avalai_costs).pack(side="left", padx=3)
        ttk.Button(bar, text="خروجی گزارش عیب‌یابی", command=self.export_phase49_diagnostics, style="Success.TButton").pack(side="left", padx=3)
        ttk.Label(
            bar,
            text="API Key/Password/Token در خروجی ذخیره نمی‌شود. Request ID، Provider، Model، HTTP، Token، Cost و خطا نگه‌داری می‌شود.",
            style="SubHeader.TLabel",
        ).pack(side="right", padx=5)

    def _copy_to_clipboard(self, value: str):
        self.clipboard_clear()
        self.clipboard_append(str(value or ""))
        self.update_idletasks()

    def open_phase49_app_log(self):
        win = tk.Toplevel(self)
        win.title("لاگ دیتابیسی برنامه | 3DPrintHub")
        win.geometry("1380x760")
        cols = ("id", "time", "level", "area", "action", "status", "product", "message")
        tree = ttk.Treeview(win, columns=cols, show="headings", selectmode="browse")
        specs = [
            ("id", "ID", 65), ("time", "زمان", 155), ("level", "Level", 70),
            ("area", "بخش", 110), ("action", "عملیات", 140), ("status", "وضعیت", 85),
            ("product", "Product", 80), ("message", "پیام", 620),
        ]
        for key, title, width in specs:
            tree.heading(key, text=title)
            tree.column(key, width=width, anchor="center" if key != "message" else "w")
        tree.pack(fill="both", expand=True, padx=10, pady=(10, 4))
        details = tk.Text(win, height=9, wrap="word", font=("Consolas", 9))
        details.pack(fill="x", padx=10, pady=(0, 4))
        rows_by_id = {}

        def refresh():
            tree.delete(*tree.get_children())
            rows_by_id.clear()
            for row in recent_app_events(1000):
                iid = str(row["id"])
                rows_by_id[iid] = row
                tree.insert("", "end", iid=iid, values=(
                    row["id"], row["created_at"], row["level"], row["area"], row["action"],
                    row["status"], row.get("product_id") or "", row["message"],
                ))

        def selected(_event=None):
            items = tree.selection()
            if not items:
                return
            row = rows_by_id.get(items[0]) or {}
            details.delete("1.0", "end")
            details.insert("1.0", json.dumps(row, ensure_ascii=False, indent=2, default=str))

        tree.bind("<<TreeviewSelect>>", selected)
        actions = ttk.Frame(win, padding=8)
        actions.pack(fill="x")
        ttk.Button(actions, text="بروزرسانی", command=refresh).pack(side="left", padx=3)
        ttk.Button(actions, text="کپی جزئیات", command=lambda: _copy_to_clipboard(self, details.get("1.0", "end").strip())).pack(side="left", padx=3)
        ttk.Button(actions, text="بستن", command=win.destroy).pack(side="right", padx=3)
        refresh()

    def open_phase49_ai_log(self):
        win = tk.Toplevel(self)
        win.title("لاگ درخواست‌های هوش مصنوعی | 3DPrintHub")
        win.geometry("1480x800")
        cols = ("id", "time", "provider", "model", "operation", "http", "status", "tokens", "cost", "request")
        tree = ttk.Treeview(win, columns=cols, show="headings", selectmode="browse")
        specs = [
            ("id", "ID", 55), ("time", "زمان", 150), ("provider", "Provider", 90),
            ("model", "Model", 240), ("operation", "عملیات", 155), ("http", "HTTP", 65),
            ("status", "وضعیت", 80), ("tokens", "Tokens", 75), ("cost", "Cost", 150),
            ("request", "Request ID", 310),
        ]
        for key, title, width in specs:
            tree.heading(key, text=title)
            tree.column(key, width=width, anchor="center" if key not in {"model", "request"} else "w")
        tree.pack(fill="both", expand=True, padx=10, pady=(10, 4))
        details = tk.Text(win, height=10, wrap="word", font=("Consolas", 9))
        details.pack(fill="x", padx=10, pady=(0, 4))
        rows_by_id = {}

        def refresh():
            tree.delete(*tree.get_children())
            rows_by_id.clear()
            for row in recent_ai_requests(1000):
                iid = str(row["id"])
                rows_by_id[iid] = row
                if row.get("cost_irt") is not None:
                    cost = f"{float(row['cost_irt']):,.0f} تومان"
                elif row.get("cost_usd") is not None:
                    cost = f"${float(row['cost_usd']):.6f}"
                else:
                    cost = "—"
                tree.insert("", "end", iid=iid, values=(
                    row["id"], row["created_at"], row["provider"], row["model"], row["operation"],
                    row.get("http_status") or "", row["status"], row["total_tokens"], cost, row["request_id"],
                ))

        def selected(_event=None):
            items = tree.selection()
            if not items:
                return
            row = rows_by_id.get(items[0]) or {}
            details.delete("1.0", "end")
            details.insert("1.0", json.dumps(row, ensure_ascii=False, indent=2, default=str))

        tree.bind("<<TreeviewSelect>>", selected)
        actions = ttk.Frame(win, padding=8)
        actions.pack(fill="x")
        ttk.Button(actions, text="بروزرسانی", command=refresh).pack(side="left", padx=3)
        ttk.Button(actions, text="کپی Request ID", command=lambda: _copy_to_clipboard(self, (rows_by_id.get(tree.selection()[0]) or {}).get("request_id", "") if tree.selection() else "")).pack(side="left", padx=3)
        ttk.Button(actions, text="بستن", command=win.destroy).pack(side="right", padx=3)
        refresh()

    def refresh_phase49_avalai_costs(self):
        key = get_provider_key("avalai")
        if not key:
            messagebox.showwarning("3DPrintHub", "AvalAI API Key تنظیم نشده است.", parent=self)
            return
        pending = [row for row in recent_ai_requests(200) if row.get("provider") == "avalai" and row.get("request_id") and row.get("cost_irt") is None]
        if not pending:
            messagebox.showinfo("3DPrintHub", "درخواست AvalAI بدون هزینه ثبت‌شده پیدا نشد.", parent=self)
            return
        self.status.set(f"در حال تکمیل هزینه {len(pending)} درخواست AvalAI…")

        def work():
            client = AIProviderClient("avalai", key)
            changed = 0
            for row in pending:
                try:
                    tx = client.lookup_avalai_cost(str(row["request_id"]))
                    if not tx:
                        continue
                    cost_usd = tx.get("cost")
                    cost_irt = tx.get("cost_irt")
                    try:
                        cost_usd = float(cost_usd) if cost_usd is not None else None
                    except Exception:
                        cost_usd = None
                    try:
                        cost_irt = float(cost_irt) if cost_irt is not None else None
                    except Exception:
                        cost_irt = None
                    changed += update_ai_cost(str(row["request_id"]), cost_usd=cost_usd, cost_irt=cost_irt, cost_source="avalai_transaction_lookup")
                except Exception:
                    continue
            return changed

        def runner():
            try:
                changed = work()
                self.after(0, lambda: messagebox.showinfo("3DPrintHub", f"هزینه {changed} درخواست بروزرسانی شد.\nممکن است ثبت هزینه AvalAI تا چند ثانیه تأخیر داشته باشد.", parent=self))
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("3DPrintHub", str(exc), parent=self))

        import threading
        threading.Thread(target=runner, daemon=True).start()

    def export_phase49_diagnostics(self):
        product_id = getattr(self, "current_product", None)
        try:
            path = export_diagnostic_bundle(data_root, product_id=product_id)
            messagebox.showinfo("3DPrintHub", f"گزارش ساخته شد:\n{path}\n\nاین فایل Secret ندارد و می‌توانی برای عیب‌یابی ارسالش کنی.", parent=self)
            try:
                os.startfile(path.parent)
            except Exception:
                pass
        except Exception as exc:
            messagebox.showerror("3DPrintHub", str(exc), parent=self)

    def report_callback_exception(self, exc_type, exc_value, exc_traceback):
        detail = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        audit_event(
            "runtime",
            "tk_callback_exception",
            status="error",
            level="ERROR",
            source_file="tkinter_callback",
            message=f"{exc_type.__name__}: {exc_value}",
            detail={"traceback": detail},
        )
        return original_callback_error(self, exc_type, exc_value, exc_traceback)

    app_class._runs_ui = _runs_ui
    app_class.open_phase49_app_log = open_phase49_app_log
    app_class.open_phase49_ai_log = open_phase49_ai_log
    app_class.refresh_phase49_avalai_costs = refresh_phase49_avalai_costs
    app_class.export_phase49_diagnostics = export_phase49_diagnostics
    app_class.report_callback_exception = report_callback_exception
    app_class._phase49_diagnostics_ui_installed = True
