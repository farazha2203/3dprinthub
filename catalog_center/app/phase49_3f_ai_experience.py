from __future__ import annotations

import os
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from .ai_providers import AIProviderClient
from . import secure_secrets
from .phase49_diagnostics import audit_event
from . import phase49_3f_runtime_trace as runtime_trace

PROVIDER_ORDER = ("avalai", "openrouter", "google", "openai")
PROVIDER_LABELS = {
    "avalai": "AvalAI — اعتبار و پرداخت ریالی",
    "openrouter": "OpenRouter — مدل‌های متعدد / Free",
    "google": "Google Gemini Direct — Google AI Studio",
    "openai": "OpenAI Direct — اتصال مستقیم",
}


def prepare_provider_modules() -> None:
    """Extend old module globals before their install functions create state/UI."""
    from . import phase49_ai_provider_hub as hub
    from . import phase49_3d_workflow_hardening as hardening

    hub.PROVIDER_ORDER = PROVIDER_ORDER
    hub.PROVIDER_LABELS.update(PROVIDER_LABELS)
    hardening.PROVIDER_ORDER = PROVIDER_ORDER
    try:
        aliases = hardening.MODEL_ALIASES
        aliases.setdefault("gimini", ("gemini", "google"))
        aliases.setdefault("gemini lite", ("gemini", "flash", "lite", "google"))
        aliases.setdefault("flash lite", ("gemini", "flash", "lite"))
    except Exception:
        pass
    secure_secrets.USERS.setdefault("google", "GOOGLE_GEMINI_API_KEY")
    secure_secrets.LEGACY_FILES.setdefault("google", [])


def _open_folder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    try:
        if os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as exc:
        raise RuntimeError(f"باز کردن فولدر لاگ ناموفق بود: {exc}") from exc


def install_shell(app_class, data_root) -> None:
    if getattr(app_class, "_phase49_3f_ai_experience_installed", False):
        return

    original_build = app_class._build_ux87_ai_center

    def _phase49_3f_key(self, provider: str) -> str:
        entered = ""
        try:
            entered = self._ai_hub_key_vars[provider].get().strip()
        except Exception:
            pass
        return entered or secure_secrets.get_provider_key(provider)

    def _phase49_3f_save_card(self, provider: str):
        try:
            entered = self._ai_hub_key_vars[provider].get().strip()
            if entered:
                secure_secrets.set_provider_key(provider, entered)
                self._ai_hub_key_vars[provider].set("")
            model = str(self._ai_hub_model_vars[provider].get() or "").split(" • ", 1)[0].strip()
            if model:
                self._ai_hub_model_vars[provider].set(model)
                self.db.set_setting(f"ai_model_{provider}", model)
            self._ai_hub_status_vars[provider].set("✅ کلید/مدل این Provider ذخیره شد")
            audit_event("settings", "phase49_3f_provider_card_saved", message=f"provider={provider} model={model}")
            runtime_trace.event("ai-settings", "provider-card-saved", provider=provider, model=model)
        except Exception as exc:
            self._ai_hub_status_vars[provider].set(f"❌ ذخیره ناموفق: {exc}")
            runtime_trace.event("ai-settings", "provider-card-save-error", status="error", provider=provider, message=str(exc))
            messagebox.showerror("3DPrintHub — ذخیره AI", str(exc), parent=self)

    def _phase49_3f_probe(self, provider: str, *, show_dialog=True):
        key = self._phase49_3f_key(provider)
        model = str(self._ai_hub_model_vars[provider].get() or "").split(" • ", 1)[0].strip()
        if not key:
            messagebox.showwarning("3DPrintHub", f"API Key برای {PROVIDER_LABELS.get(provider, provider)} تنظیم نشده است.", parent=self)
            return
        self._ai_hub_status_vars[provider].set("⏳ در حال اتصال… سقف انتظار ۳۰ ثانیه")
        runtime_trace.event("ai", "connection-probe-start", product_id=None, provider=provider, model=model)

        def worker():
            try:
                result = AIProviderClient(provider, key, model).probe_connection(timeout=30)
                self.after(0, lambda: done(result, None))
            except Exception as exc:
                self.after(0, lambda: done(None, exc))

        def done(result, exc):
            if exc is not None:
                self._ai_hub_status_vars[provider].set(f"❌ اتصال برقرار نشد: {exc}")
                runtime_trace.event("ai", "connection-probe-error", status="error", provider=provider, model=model, message=str(exc))
                if show_dialog:
                    messagebox.showerror("3DPrintHub — اتصال AI", f"اتصال برقرار نشد.\n\n{exc}", parent=self)
                return
            count = int((result or {}).get("models_count") or 0)
            self._ai_hub_status_vars[provider].set(f"✅ اتصال برقرار شد • {count:,} مدل قابل مشاهده")
            runtime_trace.event("ai", "connection-probe-ok", provider=provider, model=model, detail={"models_count": count})
            if show_dialog:
                messagebox.showinfo("3DPrintHub — اتصال AI", f"✅ اتصال برقرار شد.\nProvider: {PROVIDER_LABELS.get(provider, provider)}\nمدل‌های قابل مشاهده: {count:,}", parent=self)

        threading.Thread(target=worker, daemon=True).start()

    def _phase49_3f_test_active(self):
        provider = str(self._phase49_3d_active_provider.get() or "").strip().lower()
        if provider not in PROVIDER_ORDER:
            messagebox.showwarning("3DPrintHub", "ابتدا Provider فعال را انتخاب کن.", parent=self)
            return
        return self._phase49_3f_probe(provider)

    def _phase49_3f_balance(self, provider: str):
        key = self._phase49_3f_key(provider)
        model = str(self._ai_hub_model_vars[provider].get() or "").split(" • ", 1)[0].strip()
        if not key:
            messagebox.showwarning("3DPrintHub", "ابتدا API Key را وارد یا ذخیره کن.", parent=self)
            return
        self._ai_hub_balance_vars[provider].set("اعتبار/هزینه: در حال دریافت…")

        def worker():
            try:
                management = secure_secrets.get_secret("openrouter_management_key") if provider == "openrouter" else ""
                admin = secure_secrets.get_secret("openai_admin_key") if provider == "openai" else ""
                value = AIProviderClient(provider, key, model).balance_info(management_key=management, admin_key=admin)
                self.after(0, lambda: done(value, None))
            except Exception as exc:
                self.after(0, lambda: done(None, exc))

        def done(info, exc):
            if exc:
                self._ai_hub_balance_vars[provider].set(f"❌ {exc}")
                return
            if not info.get("available"):
                self._ai_hub_balance_vars[provider].set(str(info.get("reason") or "در دسترس نیست"))
                return
            if provider == "avalai":
                self._ai_hub_balance_vars[provider].set(f"{float(info.get('remaining_irt') or 0):,.0f} تومان")
            elif provider == "openrouter":
                self._ai_hub_balance_vars[provider].set(f"${float(info.get('remaining_usd') or 0):,.4f} مانده")
            else:
                self._ai_hub_balance_vars[provider].set(f"${float(info.get('spend_30d_usd') or 0):,.4f} هزینه ۳۰ روز")

        threading.Thread(target=worker, daemon=True).start()

    def _phase49_3f_open_logs(self):
        try:
            _open_folder(runtime_trace.log_folder())
        except Exception as exc:
            messagebox.showerror("3DPrintHub", str(exc), parent=self)

    def _build_ux87_ai_center(self):
        # Do not build then reparent the legacy cards: Tk widgets cannot be safely
        # reparented. Build the canonical 49.3F scroll surface directly.
        for child in self.ai_tab.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        self.ai_tab.columnconfigure(0, weight=1)
        self.ai_tab.rowconfigure(1, weight=1)

        sticky = ttk.LabelFrame(self.ai_tab, text="هوش مصنوعی فعال", padding=9, style="Card.TLabelframe")
        sticky.grid(row=0, column=0, sticky="ew", pady=(0, 7))
        sticky.columnconfigure(0, weight=1)
        self._phase49_3d_refresh_active_summary()
        ttk.Label(sticky, textvariable=self._phase49_3d_active_summary, font=("Tahoma", 10, "bold")).grid(row=0, column=0, sticky="w", padx=4)
        ttk.Button(sticky, text="💾 ذخیره Provider و مدل فعال", command=self._phase49_3d_save_active_ai, style="Success.TButton").grid(row=0, column=1, padx=3)
        ttk.Button(sticky, text="🔌 تست اتصال ۳۰ ثانیه", command=self._phase49_3f_test_active, style="Primary.TButton").grid(row=0, column=2, padx=3)
        ttk.Button(sticky, text="📂 فولدر لاگ", command=self._phase49_3f_open_logs).grid(row=0, column=3, padx=3)
        ttk.Checkbutton(sticky, text="آماده‌سازی خودکار AI هنگام بازکردن محصول", variable=self._phase49_3d_auto_prepare_var).grid(row=1, column=0, columnspan=4, sticky="w", padx=4, pady=(5, 0))

        shell = ttk.Frame(self.ai_tab)
        shell.grid(row=1, column=0, sticky="nsew")
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)
        canvas = tk.Canvas(shell, highlightthickness=0, bg="#f2f5f8")
        ybar = ttk.Scrollbar(shell, orient="vertical", command=canvas.yview)
        xbar = ttk.Scrollbar(shell, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        inner = ttk.Frame(canvas, padding=(3, 2, 8, 8))
        window = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.columnconfigure(0, weight=1)
        inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window, width=max(e.width, 920)))
        canvas.bind("<Enter>", lambda _e: canvas.bind_all("<MouseWheel>", lambda ev: canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")))
        canvas.bind("<Leave>", lambda _e: canvas.unbind_all("<MouseWheel>"))
        self._phase49_3f_ai_canvas = canvas

        intro = ttk.Frame(inner)
        intro.grid(row=0, column=0, sticky="ew", pady=(2, 7))
        ttk.Label(intro, text="مرکز Provider و مدل", style="UX87Title.TLabel").pack(side="left")
        ttk.Label(intro, text="مدل را از API همان Provider بگیر، انتخاب کن، سپس نوار بالایی را ذخیره کن.", style="UX87Muted.TLabel").pack(side="left", padx=10)

        row = 1
        for provider in PROVIDER_ORDER:
            card = ttk.LabelFrame(inner, text=PROVIDER_LABELS[provider], padding=10, style="Card.TLabelframe")
            card.grid(row=row, column=0, sticky="ew", pady=5)
            card.columnconfigure(1, weight=1)
            row += 1
            ttk.Radiobutton(card, text="استفاده از این Provider", value=provider, variable=self._phase49_3d_active_provider, command=self._phase49_3d_refresh_active_summary).grid(row=0, column=0, columnspan=3, sticky="w", padx=4, pady=(0, 5))
            ttk.Label(card, text="API Key").grid(row=1, column=0, sticky="w", padx=4, pady=4)
            ttk.Entry(card, textvariable=self._ai_hub_key_vars[provider], show="•").grid(row=1, column=1, sticky="ew", padx=4, pady=4)
            ttk.Label(card, text=f"منبع: {secure_secrets.provider_key_source(provider)}", style="SubHeader.TLabel").grid(row=1, column=2, sticky="w", padx=4)
            ttk.Label(card, text="Model ID").grid(row=2, column=0, sticky="w", padx=4, pady=4)
            box = ttk.Combobox(card, textvariable=self._ai_hub_model_vars[provider], width=74)
            box.grid(row=2, column=1, sticky="ew", padx=4, pady=4)
            self._ai_hub_model_boxes[provider] = box
            ttk.Button(card, text="🔎 جستجو و انتخاب مدل", command=lambda p=provider: self._phase49_3d_open_model_picker(p)).grid(row=2, column=2, padx=4)
            actions = ttk.Frame(card)
            actions.grid(row=3, column=0, columnspan=3, sticky="ew", padx=2, pady=(5, 2))
            ttk.Button(actions, text="ذخیره امن کلید/مدل", command=lambda p=provider: self._phase49_3f_save_card(p)).pack(side="left", padx=3)
            ttk.Button(actions, text="تست اتصال", command=lambda p=provider: self._phase49_3f_probe(p), style="Primary.TButton").pack(side="left", padx=3)
            ttk.Button(actions, text="اعتبار / هزینه", command=lambda p=provider: self._phase49_3f_balance(p)).pack(side="left", padx=3)
            ttk.Label(actions, textvariable=self._ai_hub_balance_vars[provider], style="SubHeader.TLabel").pack(side="right", padx=5)
            ttk.Label(card, textvariable=self._ai_hub_status_vars[provider], style="SubHeader.TLabel").grid(row=4, column=0, columnspan=3, sticky="w", padx=4, pady=(3, 0))

        footer = ttk.LabelFrame(inner, text="تنظیمات عمومی", padding=10, style="Card.TLabelframe")
        footer.grid(row=row, column=0, sticky="ew", pady=(7, 0))
        ttk.Label(footer, text="نرخ دلار برای گزارش هزینه AI به تومان").pack(side="left", padx=4)
        ttk.Entry(footer, textvariable=self._ai_usd_to_toman, width=16).pack(side="left", padx=4)
        ttk.Label(footer, text="موتور ترجمه").pack(side="left", padx=(18, 4))
        ttk.Combobox(footer, textvariable=self.translation_provider, values=["ai", "google"], state="readonly", width=15).pack(side="left", padx=4)
        runtime_trace.event("ui", "ai-center-built", detail={"providers": list(PROVIDER_ORDER)})

    app_class._phase49_3f_key = _phase49_3f_key
    app_class._phase49_3f_save_card = _phase49_3f_save_card
    app_class._phase49_3f_probe = _phase49_3f_probe
    app_class._phase49_3f_test_active = _phase49_3f_test_active
    app_class._phase49_3f_balance = _phase49_3f_balance
    app_class._phase49_3f_open_logs = _phase49_3f_open_logs
    app_class._build_ux87_ai_center = _build_ux87_ai_center
    app_class._phase49_3d_test_active_ai = _phase49_3f_test_active
    app_class._phase49_3f_ai_experience_installed = True


def configure_runtime(data_root) -> Path:
    return runtime_trace.configure(data_root)
