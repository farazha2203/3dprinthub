from __future__ import annotations

import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .ai_providers import AIProviderClient, PROVIDERS
from .env_settings import env_value
from .phase49_diagnostics import audit_event
from . import secure_secrets

PROVIDER_ORDER = ("avalai", "openrouter", "openai")
PROVIDER_LABELS = {
    "avalai": "AvalAI — پرداخت و اعتبار ریالی",
    "openrouter": "OpenRouter — مدل‌های متعدد و Free Router",
    "openai": "OpenAI Direct — اتصال مستقیم",
}


def _prepare_secret_registry() -> None:
    secure_secrets.USERS.setdefault("openrouter", "OPENROUTER_API_KEY")
    secure_secrets.CONNECTION_USERS.setdefault("openrouter_management_key", "OPENROUTER_MANAGEMENT_KEY")
    secure_secrets.CONNECTION_USERS.setdefault("openai_admin_key", "OPENAI_ADMIN_KEY")


def install_base_app(app_class) -> None:
    if getattr(app_class, "_phase49_ai_base_installed", False):
        return
    _prepare_secret_registry()

    def _provider_candidates(self):
        selected = (self.ai_provider.get() or "auto").strip().lower()
        if selected in PROVIDER_ORDER:
            return [selected]
        return list(PROVIDER_ORDER)

    def _selected_ai_provider(self):
        selected = (self.ai_provider.get() or "auto").strip().lower()
        if selected in PROVIDER_ORDER:
            return selected
        for provider in PROVIDER_ORDER:
            env_name = secure_secrets.USERS.get(provider, "")
            if (env_value(env_name, "") if env_name else "") or secure_secrets.get_provider_key(provider):
                return provider
        return "avalai"

    def _ai_key(self, provider=None):
        provider = (provider or self._selected_ai_provider()).strip().lower()
        env_name = secure_secrets.USERS.get(provider, "OPENAI_API_KEY")
        # The old single ai_key widget is still honored only for the currently
        # selected provider. Provider Hub has independent key widgets.
        entered = ""
        if getattr(self, "ai_provider", None) is not None and self.ai_provider.get() == provider:
            entered = getattr(self, "ai_key", tk.StringVar(value="")).get().strip()
        return entered or env_value(env_name, "") or secure_secrets.get_provider_key(provider)

    app_class._provider_candidates = _provider_candidates
    app_class._selected_ai_provider = _selected_ai_provider
    app_class._ai_key = _ai_key
    app_class._openai_key = lambda self: self._ai_key()
    app_class._phase49_ai_base_installed = True


def install_shell(app_class) -> None:
    if getattr(app_class, "_phase49_ai_hub_installed", False):
        return
    _prepare_secret_registry()

    original_init_state = app_class._init_ux87_settings_state
    original_refresh_status = app_class._refresh_ux87_status

    def _init_ux87_settings_state(self):
        original_init_state(self)
        stored = str(self.db.setting("ai_provider", "auto") or "auto").strip().lower()
        if stored in {"auto", *PROVIDER_ORDER}:
            self.ai_provider.set(stored)
        self._ai_hub_model_vars = {
            provider: tk.StringVar(value=str(self.db.setting(f"ai_model_{provider}", "") or ""))
            for provider in PROVIDER_ORDER
        }
        current = self.ai_provider.get()
        if current in PROVIDER_ORDER and self._ai_hub_model_vars[current].get():
            self.ai_model.set(self._ai_hub_model_vars[current].get())
        self._ai_hub_key_vars = {provider: tk.StringVar(value="") for provider in PROVIDER_ORDER}
        self._ai_hub_status_vars = {provider: tk.StringVar(value="آماده بررسی") for provider in PROVIDER_ORDER}
        self._ai_hub_balance_vars = {provider: tk.StringVar(value="اعتبار: —") for provider in PROVIDER_ORDER}
        self._ai_hub_model_boxes = {}
        self._ai_hub_model_info = {provider: {} for provider in PROVIDER_ORDER}
        self._ai_hub_last_request = {provider: "" for provider in PROVIDER_ORDER}
        self._ai_usd_to_toman = tk.StringVar(value=str(self.db.setting("ai_usd_to_toman", "") or ""))
        self._openrouter_management_key_var = tk.StringVar(value="")
        self._openai_admin_key_var = tk.StringVar(value="")

    def _provider_key(provider: str, self):
        entered = self._ai_hub_key_vars[provider].get().strip()
        return entered or secure_secrets.get_provider_key(provider)

    def _thread(self, work, done):
        def runner():
            try:
                value = work()
                self.after(0, lambda: done(value, None))
            except Exception as exc:
                self.after(0, lambda: done(None, exc))
        threading.Thread(target=runner, daemon=True).start()

    def _activate_provider(self, provider: str):
        model = self._ai_hub_model_vars[provider].get().strip()
        self.ai_provider.set(provider)
        self.ai_model.set(model)
        self.db.set_setting("ai_provider", provider)
        self.db.set_setting("ai_model", model)
        self.db.set_setting(f"ai_model_{provider}", model)
        audit_event("settings", "activate_ai_provider", message=f"provider={provider} model={model}")
        self._refresh_ux87_status()
        self._ai_hub_status_vars[provider].set("✅ Provider فعال برای درخواست‌های بعدی")

    def _save_provider(self, provider: str):
        key = self._ai_hub_key_vars[provider].get().strip()
        try:
            if key:
                secure_secrets.set_provider_key(provider, key)
                self._ai_hub_key_vars[provider].set("")
            model = self._ai_hub_model_vars[provider].get().strip()
            self.db.set_setting(f"ai_model_{provider}", model)
            if provider == "openrouter" and self._openrouter_management_key_var.get().strip():
                secure_secrets.set_secret("openrouter_management_key", self._openrouter_management_key_var.get().strip())
                self._openrouter_management_key_var.set("")
            if provider == "openai" and self._openai_admin_key_var.get().strip():
                secure_secrets.set_secret("openai_admin_key", self._openai_admin_key_var.get().strip())
                self._openai_admin_key_var.set("")
            self.db.set_setting("ai_usd_to_toman", self._ai_usd_to_toman.get().strip())
            audit_event("settings", "save_ai_provider", message=f"provider={provider} model={model}")
            self._ai_hub_status_vars[provider].set("✅ تنظیمات امن ذخیره شد")
        except Exception as exc:
            self._ai_hub_status_vars[provider].set(f"❌ {exc}")
            messagebox.showerror("3DPrintHub", str(exc), parent=self)

    def _load_models(self, provider: str):
        key = _provider_key(provider, self)
        if not key:
            messagebox.showwarning("3DPrintHub", f"API Key برای {provider} تنظیم نشده است.", parent=self)
            return
        self._ai_hub_status_vars[provider].set("در حال دریافت مدل‌ها…")
        preferred = self._ai_hub_model_vars[provider].get().strip()

        def work():
            client = AIProviderClient(provider, key, preferred)
            return client.list_model_info()

        def done(info, exc):
            if exc:
                self._ai_hub_status_vars[provider].set(f"❌ دریافت مدل‌ها: {exc}")
                return
            mapping = {}
            labels = []
            for item in info:
                model_id = item["id"]
                pricing = item.get("pricing") or {}
                free = bool(item.get("free"))
                suffix = " • رایگان" if free else ""
                if provider == "openrouter" and not free:
                    try:
                        prompt = float(pricing.get("prompt") or 0) * 1_000_000
                        completion = float(pricing.get("completion") or 0) * 1_000_000
                        suffix = f" • ${prompt:.3f}/${completion:.3f} per 1M"
                    except Exception:
                        pass
                label = f"{model_id}{suffix}"
                labels.append(label)
                mapping[label] = model_id
                mapping[model_id] = model_id
            self._ai_hub_model_info[provider] = {item["id"]: item for item in info}
            box = self._ai_hub_model_boxes.get(provider)
            if box is not None:
                box.configure(values=labels)
            if not preferred and info:
                chosen = next((item["id"] for item in info if item.get("free")), info[0]["id"])
                self._ai_hub_model_vars[provider].set(chosen)
            self._ai_hub_status_vars[provider].set(f"✅ {len(info)} مدل دریافت شد")

        _thread(self, work, done)

    def _normalize_model_value(self, provider: str):
        value = self._ai_hub_model_vars[provider].get().strip()
        if " • " in value:
            value = value.split(" • ", 1)[0].strip()
            self._ai_hub_model_vars[provider].set(value)
        return value

    def _test_provider(self, provider: str):
        key = _provider_key(provider, self)
        if not key:
            messagebox.showwarning("3DPrintHub", f"API Key برای {provider} تنظیم نشده است.", parent=self)
            return
        model = _normalize_model_value(self, provider)
        self._ai_hub_status_vars[provider].set("در حال تست زنده…")

        def work():
            return AIProviderClient(provider, key, model).test_connection(model)

        def done(result, exc):
            if exc:
                self._ai_hub_status_vars[provider].set(f"❌ {provider}: {exc}")
                audit_event("ai", "provider_test", status="error", level="ERROR", message=f"{provider}: {exc}")
                return
            self._ai_hub_last_request[provider] = str(result.get("request_id") or "")
            usage = result.get("usage") or {}
            cost = usage.get("cost")
            free = " • رایگان" if result.get("free") else ""
            cost_text = f" • cost=${float(cost):.6f}" if cost is not None else ""
            self._ai_hub_status_vars[provider].set(
                f"✅ اتصال موفق • {result.get('model')}{free}{cost_text} • {result.get('sample','')[:60]}"
            )

        _thread(self, work, done)

    def _balance_provider(self, provider: str):
        key = _provider_key(provider, self)
        if not key:
            messagebox.showwarning("3DPrintHub", f"API Key برای {provider} تنظیم نشده است.", parent=self)
            return
        model = _normalize_model_value(self, provider)
        self._ai_hub_balance_vars[provider].set("اعتبار: در حال دریافت…")

        def work():
            management = self._openrouter_management_key_var.get().strip() or secure_secrets.get_secret("openrouter_management_key")
            admin = self._openai_admin_key_var.get().strip() or secure_secrets.get_secret("openai_admin_key")
            return AIProviderClient(provider, key, model).balance_info(management_key=management, admin_key=admin)

        def done(info, exc):
            if exc:
                self._ai_hub_balance_vars[provider].set(f"اعتبار: ❌ {exc}")
                return
            if not info.get("available"):
                self._ai_hub_balance_vars[provider].set(f"اعتبار: {info.get('reason','در دسترس نیست')}")
                return
            rate = 0.0
            try:
                rate = float(self._ai_usd_to_toman.get().replace(",", "") or 0)
            except Exception:
                rate = 0.0
            if provider == "avalai":
                toman = float(info.get("remaining_irt") or 0)
                usd = float(info.get("remaining_usd") or 0)
                if info.get("exchange_rate"):
                    self._ai_usd_to_toman.set(str(int(float(info["exchange_rate"]))))
                    self.db.set_setting("ai_usd_to_toman", self._ai_usd_to_toman.get())
                self._ai_hub_balance_vars[provider].set(f"اعتبار: {toman:,.0f} تومان • ${usd:,.4f} • Tier {info.get('account_tier','—')}")
            elif provider == "openrouter":
                usd = float(info.get("remaining_usd") or 0)
                toman = usd * rate if rate else 0
                suffix = f" • ≈ {toman:,.0f} تومان" if rate else ""
                self._ai_hub_balance_vars[provider].set(f"اعتبار: ${usd:,.4f}{suffix} • مصرف ${float(info.get('total_usage') or 0):,.4f}")
            else:
                usd = float(info.get("spend_30d_usd") or 0)
                toman = usd * rate if rate else 0
                suffix = f" • ≈ {toman:,.0f} تومان" if rate else ""
                self._ai_hub_balance_vars[provider].set(f"هزینه ۳۰ روز اخیر: ${usd:,.4f}{suffix} (مانده اعتبار نیست)")

        _thread(self, work, done)

    def _build_ux87_ai_center(self):
        self.ai_tab.columnconfigure(0, weight=1)
        ttk.Label(self.ai_tab, text="مرکز هوش مصنوعی و هزینه", style="UX87Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.ai_tab,
            text="هر Provider تنظیمات، مدل، کلید، اعتبار و تست مستقل دارد. Provider فعال برای درخواست‌های Product Workspace با دکمه «فعال کن» انتخاب می‌شود.",
            style="UX87Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 8))

        tools = ttk.LabelFrame(self.ai_tab, text="گزارش هزینه", padding=10, style="Card.TLabelframe")
        tools.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(tools, text="نرخ دلار برای تبدیل هزینه Providerهای دلاری به تومان").pack(side="left", padx=4)
        ttk.Entry(tools, textvariable=self._ai_usd_to_toman, width=16).pack(side="left", padx=4)
        ttk.Label(tools, text="AvalAI نرخ IRT را از API خودش بروزرسانی می‌کند.", style="SubHeader.TLabel").pack(side="left", padx=8)

        row = 3
        for provider in PROVIDER_ORDER:
            card = ttk.LabelFrame(self.ai_tab, text=PROVIDER_LABELS[provider], padding=12, style="Card.TLabelframe")
            card.grid(row=row, column=0, sticky="ew", pady=5)
            card.columnconfigure(1, weight=1)
            row += 1

            ttk.Label(card, text="API Key").grid(row=0, column=0, sticky="w", padx=4, pady=4)
            ttk.Entry(card, textvariable=self._ai_hub_key_vars[provider], show="•").grid(row=0, column=1, sticky="ew", padx=4, pady=4)
            source = secure_secrets.provider_key_source(provider)
            ttk.Label(card, text=f"منبع فعلی: {source}", style="SubHeader.TLabel").grid(row=0, column=2, sticky="w", padx=4)

            ttk.Label(card, text="Model").grid(row=1, column=0, sticky="w", padx=4, pady=4)
            box = ttk.Combobox(card, textvariable=self._ai_hub_model_vars[provider], width=70)
            box.grid(row=1, column=1, sticky="ew", padx=4, pady=4)
            self._ai_hub_model_boxes[provider] = box
            ttk.Button(card, text="دریافت مدل‌ها", command=lambda p=provider: _load_models(self, p)).grid(row=1, column=2, padx=4)

            extra_row = 2
            if provider == "openrouter":
                ttk.Label(card, text="Management Key (اختیاری برای Balance)").grid(row=extra_row, column=0, sticky="w", padx=4, pady=4)
                ttk.Entry(card, textvariable=self._openrouter_management_key_var, show="•").grid(row=extra_row, column=1, sticky="ew", padx=4, pady=4)
                extra_row += 1
            elif provider == "openai":
                ttk.Label(card, text="Admin Key (اختیاری برای Costs)").grid(row=extra_row, column=0, sticky="w", padx=4, pady=4)
                ttk.Entry(card, textvariable=self._openai_admin_key_var, show="•").grid(row=extra_row, column=1, sticky="ew", padx=4, pady=4)
                extra_row += 1

            actions = ttk.Frame(card)
            actions.grid(row=extra_row, column=0, columnspan=3, sticky="ew", pady=(5, 2))
            ttk.Button(actions, text="ذخیره امن", command=lambda p=provider: _save_provider(self, p)).pack(side="left", padx=3)
            ttk.Button(actions, text="تست زنده", command=lambda p=provider: _test_provider(self, p), style="Success.TButton").pack(side="left", padx=3)
            ttk.Button(actions, text="اعتبار / هزینه", command=lambda p=provider: _balance_provider(self, p)).pack(side="left", padx=3)
            ttk.Button(actions, text="فعال کن", command=lambda p=provider: _activate_provider(self, p), style="Primary.TButton").pack(side="left", padx=3)
            ttk.Label(actions, textvariable=self._ai_hub_balance_vars[provider], style="SubHeader.TLabel").pack(side="right", padx=5)
            ttk.Label(card, textvariable=self._ai_hub_status_vars[provider], style="SubHeader.TLabel").grid(row=extra_row + 1, column=0, columnspan=3, sticky="w", padx=4, pady=(3, 0))

        translation = ttk.LabelFrame(self.ai_tab, text="ترجمه", padding=10, style="Card.TLabelframe")
        translation.grid(row=row, column=0, sticky="ew", pady=(8, 0))
        ttk.Label(translation, text="موتور ترجمه").pack(side="left", padx=4)
        ttk.Combobox(translation, textvariable=self.translation_provider, values=["ai", "google"], state="readonly", width=16).pack(side="left", padx=4)
        ttk.Label(translation, text="AI از Provider فعال بالا استفاده می‌کند؛ Google Translation مستقل است.", style="SubHeader.TLabel").pack(side="left", padx=8)

    def _refresh_ux87_status(self):
        original_refresh_status(self)
        provider = self.ai_provider.get() if hasattr(self, "ai_provider") else "auto"
        if provider in PROVIDER_ORDER:
            ready = bool(secure_secrets.get_provider_key(provider))
            if hasattr(self, "ux87_ai_status"):
                self.ux87_ai_status.set(f"AI: {provider} {'آماده' if ready else 'بدون کلید'}")

    app_class._init_ux87_settings_state = _init_ux87_settings_state
    app_class._build_ux87_ai_center = _build_ux87_ai_center
    app_class._refresh_ux87_status = _refresh_ux87_status
    app_class._phase49_ai_hub_installed = True
