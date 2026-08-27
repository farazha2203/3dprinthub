from __future__ import annotations

import threading

import tkinter as tk
from tkinter import messagebox, ttk

from .ai_providers import AIProviderClient
from .phase49_3i17_single_active_ai_runtime import (
    ALLOWED_PROVIDERS,
    active_ai_config,
)
from .phase49_3i21_observable_ai_link_refresh import ObservableJobDialog
from .phase49_3i24_runtime_observability import redact
from .phase49_3i33_ai_core import OperationTelemetry, run_ai_mode
from .phase49_3i33_operator_workflow import AI_MODE_BY_LABEL, AI_MODES
from .secure_secrets import get_provider_key

PHASE = "49.3I.35"


def _bool_setting(app, key: str, default: bool) -> bool:
    raw = str(app.db.setting(key, "1" if default else "0") or "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def retry_attempts(app) -> int:
    try:
        value = int(float(str(app.db.setting("ai_retry_attempts", "3") or "3")))
    except Exception:
        value = 3
    return min(3, max(1, value))


def configured_ai_candidates(app, *, require_key=True) -> list[tuple[str, str, str, str]]:
    """Return explicit mother-settings candidates.

    The primary provider/model stays authoritative. Fallback is enabled only by
    the mother AI settings and never scans arbitrary providers/models.
    """
    primary_provider, primary_key, primary_model = active_ai_config(app, require_key=require_key)
    output = [(primary_provider, primary_key, primary_model, "primary")]
    if not _bool_setting(app, "ai_fallback_enabled", True):
        return output

    raw_order = str(
        app.db.setting("ai_fallback_order", "openrouter,avalai,google,openai")
        or "openrouter,avalai,google,openai"
    )
    order = []
    for token in raw_order.split(","):
        provider = token.strip().lower()
        if provider in ALLOWED_PROVIDERS and provider not in order:
            order.append(provider)

    use_openrouter_free = _bool_setting(app, "ai_fallback_openrouter_free", True)
    for provider in order:
        if provider == primary_provider:
            continue
        key = get_provider_key(provider)
        if require_key and not key:
            continue
        if provider == "openrouter" and use_openrouter_free:
            model = "openrouter/free"
            source = "fallback-free"
        else:
            model = str(
                app.db.setting(f"ai_model_{provider}", "")
                or app.db.setting("ai_model", "")
                or ""
            ).strip()
            source = "fallback"
            if not model:
                continue
        output.append((provider, key, model, source))
        if len(output) >= 3:
            break
    return output


def _set_progress(self, percent: float, message: str = ""):
    value = min(100.0, max(0.0, float(percent)))
    def render():
        if not self.top.winfo_exists():
            return
        try:
            self.progress.stop()
            self.progress.configure(mode="determinate", maximum=100, value=value)
        except Exception:
            pass
        if message:
            self.status.set(f"{value:.0f}% • {message}")
    self.workspace.after(0, render)


def install_progress_dialog() -> None:
    if not hasattr(ObservableJobDialog, "set_progress"):
        ObservableJobDialog.set_progress = _set_progress


def _preflight(dialog, provider: str, key: str, model: str, source: str, health_cache: dict):
    cache_key = (provider, model)
    if cache_key in health_cache:
        cached = health_cache[cache_key]
        if isinstance(cached, Exception):
            raise cached
        dialog.event(
            "preflight_cached",
            f"تست قبلی سالم است • {provider} / {model}",
            {"provider": provider, "model": model, "source": source},
        )
        return cached

    dialog.event(
        "preflight",
        f"تست زنده پاسخ‌گویی {provider} قبل از پردازش…",
        {"provider": provider, "model": model, "source": source},
    )
    try:
        result = AIProviderClient(provider, key, model, product_id=None).test_connection(model)
    except Exception as exc:
        health_cache[cache_key] = exc
        dialog.event(
            "preflight_failed",
            f"{provider} پاسخ‌گو نیست: {redact(exc)}",
            {"provider": provider, "model": model},
        )
        raise
    health_cache[cache_key] = result
    dialog.event(
        "preflight_ok",
        f"{provider} پاسخ داد • مدل آماده است",
        {
            "provider": provider,
            "model": result.get("model") or model,
            "free": bool(result.get("free")),
        },
    )
    return result


def run_resilient_ai(
    app,
    product_id: int,
    mode: str,
    dialog,
    *,
    health_cache: dict | None = None,
    progress_start: float = 0,
    progress_end: float = 100,
):
    candidates = configured_ai_candidates(app, require_key=True)
    attempts = retry_attempts(app)
    health_cache = health_cache if health_cache is not None else {}
    failures = []
    span = max(1.0, progress_end - progress_start)

    for provider_index, (provider, key, model, source) in enumerate(candidates, 1):
        if dialog.cancelled.is_set():
            raise RuntimeError("عملیات توسط اپراتور لغو شد.")
        candidate_base = progress_start + span * ((provider_index - 1) / max(1, len(candidates)))
        dialog.set_progress(candidate_base, f"تست {provider}")
        try:
            probe = _preflight(dialog, provider, key, model, source, health_cache)
            model = str(probe.get("model") or model)
        except Exception as exc:
            failures.append(f"{provider}/preflight: {redact(exc)}")
            if provider_index < len(candidates):
                dialog.event("fallback", f"رفتن سراغ هوش جایگزین {provider_index + 1}/{len(candidates)}")
            continue

        for attempt in range(1, attempts + 1):
            if dialog.cancelled.is_set():
                raise RuntimeError("عملیات توسط اپراتور لغو شد.")
            fraction = ((provider_index - 1) + (attempt / (attempts + 1))) / max(1, len(candidates))
            dialog.set_progress(progress_start + span * fraction, f"{provider} • تلاش {attempt}/{attempts}")
            dialog.event(
                "send",
                f"محصول #{product_id}: ارسال درخواست به {provider} • تلاش {attempt}/{attempts}",
                {"provider": provider, "model": model, "attempt": attempt, "mode": mode},
            )
            dialog.event("waiting", f"محصول #{product_id}: درخواست دریافت شد؛ منتظر پاسخ {provider}…")
            try:
                result = run_ai_mode(app, int(product_id), mode, provider, key, model)
            except Exception as exc:
                failures.append(f"{provider}/attempt-{attempt}: {redact(exc)}")
                if attempt < attempts:
                    dialog.event(
                        "retry",
                        f"محصول #{product_id}: پاسخ معتبر نگرفتیم؛ تلاش {attempt + 1}/{attempts}",
                        {"error": redact(exc), "provider": provider},
                    )
                    continue
                dialog.event(
                    "provider_failed",
                    f"محصول #{product_id}: سه تلاش {provider} تمام شد؛ {redact(exc)}",
                )
                break

            dialog.event(
                "reply",
                f"محصول #{product_id}: پاسخ {provider} دریافت شد",
                {"provider": provider, "model": model},
            )
            dialog.event(
                "apply",
                f"محصول #{product_id}: اطلاعات فارسی/SEO در دیتابیس محلی به‌روزرسانی شد",
                {"changed_fields": result.get("changed_fields") or []},
            )
            dialog.set_progress(progress_end, f"محصول #{product_id} تکمیل شد")
            return result

        if provider_index < len(candidates):
            dialog.event(
                "fallback",
                f"محصول #{product_id}: Provider بعدی امتحان می‌شود",
                {"next_index": provider_index + 1, "providers": len(candidates)},
            )

    raise RuntimeError(
        "هیچ Provider تنظیم‌شده پس از تست/Retry پاسخ معتبر نداد. "
        + " | ".join(failures[-6:])
    )


def install_app(app_class) -> None:
    install_progress_dialog()
    if getattr(app_class, "_phase49_3i35_resilient_ai", False):
        return
    original_init = app_class.__init__

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self._phase49_3i35_build_ai_resilience_settings()

    def build_settings(self):
        if getattr(self, "_phase49_3i35_ai_settings_panel", None) is not None:
            return
        panel = ttk.LabelFrame(
            self.settings_tab,
            text="پایداری AI گروهی — تنظیمات مادر",
            padding=10,
            style="Card.TLabelframe",
        )
        # settings_tab is pack-managed by UX87. Keep one geometry manager per parent.\n        panel.pack(fill="x", padx=8, pady=8)
        self._phase49_3i35_retry_var = tk.StringVar(
            value=str(retry_attempts(self))
        )
        self._phase49_3i35_fallback_var = tk.IntVar(
            value=int(_bool_setting(self, "ai_fallback_enabled", True))
        )
        self._phase49_3i35_free_var = tk.IntVar(
            value=int(_bool_setting(self, "ai_fallback_openrouter_free", True))
        )
        self._phase49_3i35_order_var = tk.StringVar(
            value=str(self.db.setting("ai_fallback_order", "openrouter,avalai,google,openai"))
        )
        ttk.Label(panel, text="تلاش برای هر Provider").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        ttk.Combobox(
            panel, textvariable=self._phase49_3i35_retry_var,
            values=["1", "2", "3"], state="readonly", width=6,
        ).grid(row=0, column=1, sticky="w", padx=4)
        ttk.Checkbutton(
            panel, text="Fallback فعال باشد",
            variable=self._phase49_3i35_fallback_var,
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=4, pady=4)
        ttk.Checkbutton(
            panel,
            text="برای OpenRouter جایگزین از openrouter/free استفاده شود",
            variable=self._phase49_3i35_free_var,
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=4, pady=4)
        ttk.Label(panel, text="ترتیب Providerهای جایگزین").grid(row=3, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(panel, textvariable=self._phase49_3i35_order_var).grid(row=3, column=1, sticky="ew", padx=4)
        ttk.Button(
            panel,
            text="ذخیره تنظیمات پایداری AI",
            command=self._phase49_3i35_save_ai_resilience_settings,
            style="Primary.TButton",
        ).grid(row=4, column=1, sticky="e", padx=4, pady=(7, 2))
        ttk.Label(
            panel,
            text=(
                "Primary همان Provider/Model مادر است. جایگزین‌ها فقط از کلیدهای امن و مدل‌های ذخیره‌شده مادر "
                "استفاده می‌کنند؛ مدل تصادفی اسکن نمی‌شود. openrouter/free یک Router رایگان رسمی در Provider Hub همین برنامه است."
            ),
            style="SubHeader.TLabel",
            wraplength=1050,
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=4, pady=4)
        panel.columnconfigure(1, weight=1)
        self._phase49_3i35_ai_settings_panel = panel

    def save_settings(self):
        attempts = min(3, max(1, int(self._phase49_3i35_retry_var.get() or 3)))
        order = []
        for token in self._phase49_3i35_order_var.get().split(","):
            provider = token.strip().lower()
            if provider in ALLOWED_PROVIDERS and provider not in order:
                order.append(provider)
        if not order:
            order = ["openrouter", "avalai", "google", "openai"]
        self.db.set_setting("ai_retry_attempts", str(attempts))
        self.db.set_setting("ai_fallback_enabled", "1" if self._phase49_3i35_fallback_var.get() else "0")
        self.db.set_setting("ai_fallback_openrouter_free", "1" if self._phase49_3i35_free_var.get() else "0")
        self.db.set_setting("ai_fallback_order", ",".join(order))
        self.status.set("تنظیمات پایداری AI در تنظیمات مادر ذخیره شد؛ API Key در SQLite ذخیره نشد")
        return True

    def bulk_run(self):
        if getattr(self, "_phase49_3i33_bulk_busy", False):
            return
        ids = []
        for name in ("_phase49_3i26_product_selection", "_phase49_3i_selected_products"):
            for raw in getattr(self, name, set()) or set():
                try:
                    value = int(raw)
                except Exception:
                    continue
                if value not in ids:
                    ids.append(value)
        ids.sort()
        if not ids:
            messagebox.showwarning("3DPrintHub", "ابتدا چند محصول را از لیست انتخاب کن.", parent=self)
            return
        mode = AI_MODE_BY_LABEL.get(str(self._phase49_3i33_bulk_mode.get() or ""), "link")

        try:
            candidates = configured_ai_candidates(self, require_key=True)
        except Exception as exc:
            messagebox.showerror("تنظیمات هوش مصنوعی", str(exc), parent=self)
            return

        self._phase49_3i33_bulk_busy = True
        dialog = ObservableJobDialog(self, f"{AI_MODES[mode]} — {len(ids)} محصول")
        dialog.event(
            "queue",
            f"{len(ids)} محصول در صف • {len(candidates)} Provider قابل امتحان • Retry={retry_attempts(self)}",
            {"providers": [item[0] for item in candidates]},
        )
        span = OperationTelemetry(f"bulk-ai-resilient-{mode}")
        health_cache = {}

        def worker():
            success = 0
            failed = 0
            try:
                for index, product_id in enumerate(ids, 1):
                    if dialog.cancelled.is_set():
                        break
                    start = ((index - 1) / len(ids)) * 100
                    end = (index / len(ids)) * 100
                    dialog.set_progress(start, f"شروع محصول {index}/{len(ids)}")
                    dialog.event("product_start", f"محصول {index}/{len(ids)} • #{product_id}")
                    try:
                        result = run_resilient_ai(
                            self,
                            product_id,
                            mode,
                            dialog,
                            health_cache=health_cache,
                            progress_start=start,
                            progress_end=end,
                        )
                    except Exception as exc:
                        failed += 1
                        dialog.event(
                            "product_failed",
                            f"محصول #{product_id} پس از Retry/Fallback ناموفق ماند: {redact(exc)}",
                        )
                        dialog.set_progress(end, f"محصول {index}/{len(ids)} با خطا عبور داده شد")
                        continue
                    success += 1
                    post = getattr(self, "_phase49_3i33_post_ui", None)
                    updater = getattr(self, "_phase49_3i33_update_product_card", None)
                    if callable(post) and callable(updater):
                        post(lambda pid=product_id: updater(pid))
                    dialog.event(
                        "product_done",
                        f"محصول #{product_id} تکمیل شد • {result.get('title_fa') or 'بدون عنوان'}",
                    )
                dialog.set_progress(100, "پایان عملیات گروهی")
                dialog.done(
                    f"پایان — {success} موفق • {failed} خطا • کل لیست محصولات Refresh نشد"
                )
                span.finish(
                    "ok" if failed == 0 else "partial",
                    {"success": success, "failed": failed, "count": len(ids)},
                )
            except Exception as exc:
                span.finish("error", {"error": redact(exc)})
                dialog.fail(exc)
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i33_bulk_busy", False))

        threading.Thread(target=worker, daemon=True, name="catalog-3i35-bulk-ai").start()

    app_class.__init__ = __init__
    app_class._phase49_3i35_build_ai_resilience_settings = build_settings
    app_class._phase49_3i35_save_ai_resilience_settings = save_settings
    app_class._phase49_3i33_bulk_run = bulk_run
    app_class._phase49_3i35_resilient_ai = True


def install_workspace(workspace_class) -> None:
    install_progress_dialog()
    if getattr(workspace_class, "_phase49_3i35_resilient_ai", False):
        return

    def run_ai_ui(self, mode: str):
        if getattr(self, "_phase49_3i33_ai_busy", False):
            self.footer_status.set("یک عملیات هوش مصنوعی در حال اجرا است.")
            return
        try:
            candidates = configured_ai_candidates(self.app, require_key=True)
        except Exception as exc:
            messagebox.showerror("تنظیمات هوش مصنوعی", str(exc), parent=self)
            return

        self._phase49_3i33_ai_busy = True
        dialog = ObservableJobDialog(self, AI_MODES.get(mode, "هوش مصنوعی"))
        dialog.event(
            "queue",
            f"Primary + Fallback آماده بررسی • Retry={retry_attempts(self.app)}",
            {"providers": [item[0] for item in candidates]},
        )
        span = OperationTelemetry(f"product-ai-resilient-{mode}", int(self.product_id))

        def worker():
            try:
                result = run_resilient_ai(
                    self.app,
                    int(self.product_id),
                    mode,
                    dialog,
                    health_cache={},
                    progress_start=0,
                    progress_end=100,
                )
                dialog.done(f"انجام شد: {result.get('title_fa') or ''}")
                span.finish("ok", {"mode": mode, "changed_fields": result.get("changed_fields")})

                def complete_ui():
                    self.reload()
                    updater = getattr(self.app, "_phase49_3i33_update_product_card", None)
                    if callable(updater):
                        updater(int(self.product_id))

                self.after(0, complete_ui)
            except Exception as exc:
                span.finish("error", {"mode": mode, "error": redact(exc)})
                dialog.fail(exc)
                self.after(
                    0,
                    lambda error=exc: self.footer_status.set(
                        f"AI پس از Retry/Fallback ناموفق: {redact(error)}"
                    ),
                )
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i33_ai_busy", False))

        threading.Thread(target=worker, daemon=True, name=f"catalog-3i35-ai-{mode}").start()

    workspace_class._phase49_3i33_run_ai = run_ai_ui
    workspace_class._phase49_3i35_resilient_ai = True
