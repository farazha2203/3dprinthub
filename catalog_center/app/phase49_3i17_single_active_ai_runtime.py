from __future__ import annotations

import types
import tkinter as tk

from . import phase49_3f_gemini_provider as gemini_provider
from . import phase49_3f_runtime_trace as runtime_trace
from . import secure_secrets
from .ai_providers import AIProviderClient


ALLOWED_PROVIDERS = ("avalai", "openrouter", "google", "openai")
BUSY_FLAGS = (
    "_phase49_3e_busy",
    "_ai_busy",
    "_phase49_3f_source_busy",
    "_phase49_3i_ai_starting",
    "_phase49_3i10_title_busy",
)


def _clean_model(value: str) -> str:
    model = str(value or "").strip()
    if " • " in model:
        model = model.split(" • ", 1)[0].strip()
    if " — " in model:
        # Model picker labels may contain "Name — raw-id". The raw ID is always
        # the last segment and is what was persisted by the mature save action.
        model = model.rsplit(" — ", 1)[-1].strip()
    return model.replace("models/", "", 1) if model.startswith("models/") else model


def active_ai_config(app, *, require_key: bool = True) -> tuple[str, str, str]:
    """Return exactly the provider/model explicitly saved by the operator.

    No provider discovery, environment-key priority scan, auto mode, or alternate
    provider fallback is allowed here. The database settings written by the real
    "save active Provider/model" action are the runtime identity source; the key
    is read only from that provider's secure secret slot.
    """
    db = getattr(app, "db", None)
    if db is None:
        raise RuntimeError("AI runtime database is unavailable.")
    provider = str(db.setting("ai_provider", "") or "").strip().lower()
    if provider not in ALLOWED_PROVIDERS:
        raise RuntimeError("ابتدا در بخش هوش مصنوعی یک Provider را انتخاب و «Provider و مدل فعال» را ذخیره کن.")
    model = _clean_model(
        db.setting(f"ai_model_{provider}", "")
        or db.setting("ai_model", "")
    )
    if not model:
        raise RuntimeError("برای Provider فعال هیچ Model ذخیره نشده است؛ مدل را انتخاب و ذخیره کن.")
    key = str(secure_secrets.get_provider_key(provider) or "").strip()
    if require_key and not key:
        raise RuntimeError(f"API Key ذخیره‌شده برای Provider فعال {provider} پیدا نشد.")
    return provider, key, model


def _sync_compatibility_vars(app, provider: str, model: str) -> None:
    """Keep legacy read-only call sites pointed at the canonical active identity."""
    for attr, value in (("ai_provider", provider), ("ai_model", model), ("openai_model", model)):
        variable = getattr(app, attr, None)
        if variable is None:
            continue
        try:
            variable.set(value)
        except Exception:
            pass
    active = getattr(app, "_phase49_3d_active_provider", None)
    if active is not None:
        try:
            active.set(provider)
        except Exception:
            pass


def _release_busy(parent) -> None:
    if parent is None:
        return
    for attr in BUSY_FLAGS:
        if hasattr(parent, attr):
            try:
                setattr(parent, attr, False)
            except Exception:
                pass


def _install_exact_google_model_shortcut() -> None:
    if getattr(gemini_provider, "_phase49_3i17_exact_model_shortcut", False):
        return
    original_model_info = gemini_provider._google_model_info

    def _google_model_info(client: AIProviderClient, timeout=30):
        # Product-bound AI already has the exact operator-saved model. Do not
        # download Google's complete model catalog before every content request.
        # Explicit Settings > Search/Test clients have product_id=None and retain
        # the mature live model-list behavior.
        exact = _clean_model(getattr(client, "model", ""))
        if getattr(client, "product_id", None) is not None and exact:
            return [{
                "id": exact,
                "name": exact,
                "pricing": {},
                "supported_parameters": ["generateContent"],
                "context_length": None,
                "free": False,
            }]
        return original_model_info(client, timeout=timeout)

    gemini_provider._google_model_info = _google_model_info
    gemini_provider._phase49_3i17_exact_model_shortcut = True


def _install_product_probe_shortcut() -> None:
    if getattr(AIProviderClient, "_phase49_3i17_product_probe_shortcut", False):
        return
    original_probe = getattr(AIProviderClient, "probe_connection", None)
    if not callable(original_probe):
        return

    def probe_connection(self, timeout=30):
        exact = _clean_model(getattr(self, "model", ""))
        if getattr(self, "product_id", None) is not None and exact:
            # The actual content request is the network test. A preliminary
            # /models request added latency and could hang the UI before useful
            # work started. Explicit Settings connection tests remain live.
            return {
                "provider": self.provider,
                "model": exact,
                "models_count": 1,
                "connected": True,
                "network_probe": False,
                "exact_saved_model": True,
            }
        return original_probe(self, timeout=timeout)

    AIProviderClient.probe_connection = probe_connection
    AIProviderClient._phase49_3i17_product_probe_shortcut = True


def _install_progress_stale_widget_guard(phase49_3f_workspace_module) -> None:
    Progress = phase49_3f_workspace_module.AIProgress
    if getattr(Progress, "_phase49_3i17_stale_widget_guard", False):
        return

    def wrap(name: str):
        original = getattr(Progress, name, None)
        if not callable(original):
            return

        def guarded(self, *args, **kwargs):
            try:
                return original(self, *args, **kwargs)
            except tk.TclError as exc:
                if "invalid command name" not in str(exc).lower():
                    raise
                parent = getattr(self, "parent", None)
                _release_busy(parent)
                runtime_trace.event(
                    "ai-ui",
                    "stale-widget-callback",
                    status="error",
                    product_id=getattr(self, "product_id", None),
                    message=str(exc),
                )
                return None

        setattr(Progress, name, guarded)

    for method in ("step", "done", "fail", "close"):
        wrap(method)
    Progress._phase49_3i17_stale_widget_guard = True


def _patch_app_instance(app) -> None:
    if getattr(app, "_phase49_3i17_single_active_ai_instance", False):
        return

    def selected_ai_provider(_self):
        provider, _key, model = active_ai_config(_self, require_key=False)
        _sync_compatibility_vars(_self, provider, model)
        return provider

    def ai_key(_self, provider=None):
        active_provider, key, model = active_ai_config(_self, require_key=True)
        requested = str(provider or active_provider).strip().lower()
        if requested != active_provider:
            raise RuntimeError(
                f"Provider فعال {active_provider} است؛ استفاده خودکار از {requested} مجاز نیست."
            )
        _sync_compatibility_vars(_self, active_provider, model)
        return key

    app._selected_ai_provider = types.MethodType(selected_ai_provider, app)
    app._ai_key = types.MethodType(ai_key, app)
    app._openai_key = types.MethodType(lambda self: self._ai_key(), app)

    original_report = getattr(app, "report_callback_exception", None)
    if callable(original_report):
        def report_callback_exception(_self, exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, tk.TclError) and "invalid command name" in str(exc_value).lower():
                try:
                    _self.logger.warning("STALE_TK_CALLBACK_SUPPRESSED %s", exc_value)
                except Exception:
                    pass
                runtime_trace.event(
                    "ai-ui",
                    "stale-tk-callback-suppressed",
                    status="error",
                    message=str(exc_value),
                )
                return None
            return original_report(exc_type, exc_value, exc_traceback)

        app.report_callback_exception = types.MethodType(report_callback_exception, app)

    try:
        provider, _key, model = active_ai_config(app, require_key=False)
        _sync_compatibility_vars(app, provider, model)
    except Exception:
        pass

    # Hidden AI-on-open is intentionally disabled. Product AI is operator driven.
    try:
        app.db.set_setting("ai_auto_prepare_on_open", "0")
    except Exception:
        pass
    auto_var = getattr(app, "_phase49_3d_auto_prepare_var", None)
    if auto_var is not None:
        try:
            auto_var.set(0)
        except Exception:
            pass

    app._phase49_3i17_single_active_ai_instance = True


def install(workspace_class, phase49_3f_workspace_module) -> None:
    """Enforce one explicit active Provider/Model for every Product AI action."""
    if getattr(workspace_class, "_phase49_3i17_single_active_ai_runtime", False):
        return

    _install_exact_google_model_shortcut()
    _install_product_probe_shortcut()
    _install_progress_stale_widget_guard(phase49_3f_workspace_module)

    original_init = workspace_class.__init__

    def __init__(self, app, product_id: int):
        _patch_app_instance(app)
        original_init(self, app, product_id)

    def _phase49_3e_provider(self):
        provider, key, model = active_ai_config(self.app, require_key=True)
        _sync_compatibility_vars(self.app, provider, model)
        return provider, key, model

    def _phase49_3d_auto_prepare_on_open(self):
        # No network request may be started merely by opening a ProductWorkspace.
        try:
            self.footer_status.set(
                "AI خودکار هنگام بازکردن محصول غیرفعال است؛ برای اجرا از دکمه هوش مصنوعی استفاده کن."
            )
        except Exception:
            pass
        return None

    workspace_class.__init__ = __init__
    workspace_class._phase49_3e_provider = _phase49_3e_provider
    workspace_class._phase49_3d_auto_prepare_on_open = _phase49_3d_auto_prepare_on_open
    workspace_class._phase49_3i17_single_active_ai_runtime = True
