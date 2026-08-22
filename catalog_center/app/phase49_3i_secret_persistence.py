from __future__ import annotations

import threading

from .ai_providers import AIProviderClient
from .secure_secrets import get_provider_key, get_secret


PROVIDER_ORDER = ("avalai", "openrouter", "google", "openai")


def _selected_provider(app) -> str:
    try:
        return str(app._selected_ai_provider() or "").strip().lower()
    except Exception:
        try:
            return str(app.ai_provider.get() or "").strip().lower()
        except Exception:
            return ""


def _hydrate_connection_fields(app, *, only_empty: bool = True) -> None:
    pairs = (
        ("ftp_password", "ftp_password"),
        ("bridge_token", "bridge_token"),
    )
    for attr_name, secret_name in pairs:
        variable = getattr(app, attr_name, None)
        if variable is None:
            continue
        try:
            current = str(variable.get() or "").strip()
        except Exception:
            current = ""
        if only_empty and current:
            continue
        try:
            value = str(get_secret(secret_name) or "").strip()
        except Exception:
            value = ""
        if value:
            variable.set(value)


def _hydrate_provider_hub_fields(app, *, only_empty: bool = True) -> None:
    """Hydrate the real Phase49.3F provider-card variables from secure storage."""
    variables = getattr(app, "_ai_hub_key_vars", {}) or {}
    for provider, variable in variables.items():
        if provider not in PROVIDER_ORDER:
            continue
        try:
            current = str(variable.get() or "").strip()
        except Exception:
            current = ""
        if only_empty and current:
            continue
        try:
            value = str(get_provider_key(provider) or "").strip()
        except Exception:
            value = ""
        if value:
            variable.set(value)

    admin_pairs = (
        ("_openrouter_management_key_var", "openrouter_management_key"),
        ("_openai_admin_key_var", "openai_admin_key"),
    )
    for attr_name, secret_name in admin_pairs:
        variable = getattr(app, attr_name, None)
        if variable is None:
            continue
        try:
            current = str(variable.get() or "").strip()
        except Exception:
            current = ""
        if only_empty and current:
            continue
        try:
            value = str(get_secret(secret_name) or "").strip()
        except Exception:
            value = ""
        if value:
            variable.set(value)


def _hydrate_ai_field(app, *, force: bool = False) -> None:
    """Keep the legacy single-key field compatible with the active provider."""
    variable = getattr(app, "ai_key", None)
    if variable is None:
        return

    provider = _selected_provider(app)
    if not provider or provider == "auto":
        return

    previous_provider = str(
        getattr(app, "_phase49_3i_secret_loaded_provider", "") or ""
    ).strip().lower()
    try:
        current = str(variable.get() or "").strip()
    except Exception:
        current = ""

    provider_changed = provider != previous_provider
    if not force and current and not provider_changed:
        return

    try:
        value = str(get_provider_key(provider) or "").strip()
    except Exception:
        value = ""

    variable.set(value)
    app._phase49_3i_secret_loaded_provider = provider


def _apply_model_catalog(app, provider: str, info) -> None:
    info = list(info or [])
    cache = getattr(app, "_phase49_3d_model_cache", None)
    if isinstance(cache, dict):
        cache[provider] = info

    raw_ids = [str(item.get("id") or "") for item in info if isinstance(item, dict) and item.get("id")]
    boxes = getattr(app, "_ai_hub_model_boxes", {}) or {}
    box = boxes.get(provider)
    if box is not None:
        try:
            box.configure(values=raw_ids)
        except Exception:
            pass

    statuses = getattr(app, "_ai_hub_status_vars", {}) or {}
    status = statuses.get(provider)
    if status is not None:
        try:
            status.set(f"✅ {len(raw_ids):,} مدل از API لود شد؛ از Model ID یا جستجوی مدل انتخاب کن")
        except Exception:
            pass


def _load_provider_models_async(app, provider: str, *, force: bool = False) -> None:
    provider = str(provider or "").strip().lower()
    if provider not in PROVIDER_ORDER:
        return

    cache = getattr(app, "_phase49_3d_model_cache", {}) or {}
    if cache.get(provider) and not force:
        _apply_model_catalog(app, provider, cache.get(provider))
        return

    variables = getattr(app, "_ai_hub_key_vars", {}) or {}
    variable = variables.get(provider)
    try:
        entered = str(variable.get() or "").strip() if variable is not None else ""
    except Exception:
        entered = ""
    key = entered or str(get_provider_key(provider) or "").strip()
    if not key:
        return

    model_vars = getattr(app, "_ai_hub_model_vars", {}) or {}
    model_var = model_vars.get(provider)
    try:
        preferred = str(model_var.get() or "").split(" • ", 1)[0].strip() if model_var is not None else ""
    except Exception:
        preferred = ""

    loading = getattr(app, "_phase49_3i_model_catalog_loading", None)
    if not isinstance(loading, set):
        loading = set()
        app._phase49_3i_model_catalog_loading = loading
    if provider in loading:
        return
    loading.add(provider)

    statuses = getattr(app, "_ai_hub_status_vars", {}) or {}
    status = statuses.get(provider)
    if status is not None:
        try:
            status.set("در حال لود فهرست مدل‌ها از API…")
        except Exception:
            pass

    def worker():
        try:
            value = AIProviderClient(provider, key, preferred).list_model_info()
            app.after(0, lambda value=value: done(value, None))
        except Exception as exc:
            app.after(0, lambda exc=exc: done(None, exc))

    def done(value, error):
        loading.discard(provider)
        if error is not None:
            if status is not None:
                try:
                    status.set(f"❌ دریافت مدل‌ها از API: {error}")
                except Exception:
                    pass
            return
        _apply_model_catalog(app, provider, value)

    threading.Thread(target=worker, daemon=True).start()


def _schedule_provider_model_catalogs(app) -> None:
    """Background-load model catalogs for every provider that already has a key."""
    variables = getattr(app, "_ai_hub_key_vars", {}) or {}
    for index, provider in enumerate(PROVIDER_ORDER):
        if provider not in variables:
            continue
        try:
            has_key = bool(str(variables[provider].get() or "").strip() or get_provider_key(provider))
        except Exception:
            has_key = False
        if not has_key:
            continue
        try:
            app.after(
                250 + (index * 180),
                lambda provider=provider: _load_provider_models_async(app, provider),
            )
        except Exception:
            pass


def install(app_class) -> None:
    """Keep secure credentials visible and restore provider model visibility.

    The source of truth remains Windows Credential Store/environment. Nothing here
    writes secrets to SQLite, source files, diagnostics or logs.
    """
    if getattr(app_class, "_phase49_3i_secret_persistence_installed", False):
        return

    # Install the Stage-1 Preview recovery at the same late composition boundary.
    # It replaces only the broken listing-card JS evaluator; mature full fetch is
    # intentionally left untouched.
    from .phase49_3i_preview_recovery import install as install_preview_recovery

    install_preview_recovery()

    original_init = app_class._init_ux87_settings_state
    original_build_ai = getattr(app_class, "_build_ux87_ai_center", None)
    original_refresh_ai_source = app_class._refresh_ai_key_source
    original_save_ai = app_class.save_openai_secret
    original_save_connection = app_class.save_connection_settings
    original_provider_save = getattr(app_class, "_phase49_3f_save_card", None)
    original_active_save = getattr(app_class, "_phase49_3d_save_active_ai", None)

    def _init_ux87_settings_state(self):
        result = original_init(self)
        _hydrate_connection_fields(self, only_empty=True)
        _hydrate_provider_hub_fields(self, only_empty=True)
        _hydrate_ai_field(self, force=True)
        return result

    def _build_ux87_ai_center(self):
        result = original_build_ai(self) if callable(original_build_ai) else None
        _hydrate_provider_hub_fields(self, only_empty=True)
        _schedule_provider_model_catalogs(self)
        return result

    def _refresh_ai_key_source(self):
        result = original_refresh_ai_source(self)
        provider = _selected_provider(self)
        previous = str(
            getattr(self, "_phase49_3i_secret_loaded_provider", "") or ""
        ).strip().lower()
        if provider and provider != "auto" and provider != previous:
            _hydrate_ai_field(self, force=True)
        return result

    def save_openai_secret(self):
        result = original_save_ai(self)
        variable = getattr(self, "ai_key", None)
        try:
            empty_after_save = variable is not None and not str(variable.get() or "").strip()
        except Exception:
            empty_after_save = False
        if empty_after_save:
            _hydrate_ai_field(self, force=True)
        _hydrate_provider_hub_fields(self, only_empty=True)
        return result

    def save_connection_settings(self):
        result = original_save_connection(self)
        _hydrate_connection_fields(self, only_empty=True)
        return result

    def _phase49_3f_save_card(self, provider: str):
        result = original_provider_save(self, provider)
        _hydrate_provider_hub_fields(self, only_empty=True)
        _load_provider_models_async(self, provider, force=True)
        return result

    def _phase49_3d_save_active_ai(self):
        result = original_active_save(self)
        _hydrate_provider_hub_fields(self, only_empty=True)
        provider = ""
        try:
            provider = str(self._phase49_3d_active_provider.get() or "").strip().lower()
        except Exception:
            provider = ""
        if provider in PROVIDER_ORDER:
            _load_provider_models_async(self, provider, force=True)
        return result

    app_class._init_ux87_settings_state = _init_ux87_settings_state
    if callable(original_build_ai):
        app_class._build_ux87_ai_center = _build_ux87_ai_center
    app_class._refresh_ai_key_source = _refresh_ai_key_source
    app_class.save_openai_secret = save_openai_secret
    app_class.save_connection_settings = save_connection_settings
    if callable(original_provider_save):
        app_class._phase49_3f_save_card = _phase49_3f_save_card
    if callable(original_active_save):
        app_class._phase49_3d_save_active_ai = _phase49_3d_save_active_ai
    app_class._phase49_3i_refresh_provider_models = _load_provider_models_async
    app_class._phase49_3i_secret_persistence_installed = True
