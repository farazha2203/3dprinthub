from __future__ import annotations

from .secure_secrets import get_provider_key, get_secret


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


def _hydrate_ai_field(app, *, force: bool = False) -> None:
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


def install(app_class) -> None:
    """Keep secure credentials visible as masked fields across restarts/releases.

    The source of truth remains Windows Credential Store/environment. Nothing here
    writes secrets to SQLite, source files, diagnostics or logs.
    """
    if getattr(app_class, "_phase49_3i_secret_persistence_installed", False):
        return

    original_init = app_class._init_ux87_settings_state
    original_refresh_ai_source = app_class._refresh_ai_key_source
    original_save_ai = app_class.save_openai_secret
    original_save_connection = app_class.save_connection_settings

    def _init_ux87_settings_state(self):
        result = original_init(self)
        _hydrate_connection_fields(self, only_empty=True)
        _hydrate_ai_field(self, force=True)
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
        return result

    def save_connection_settings(self):
        result = original_save_connection(self)
        _hydrate_connection_fields(self, only_empty=True)
        return result

    app_class._init_ux87_settings_state = _init_ux87_settings_state
    app_class._refresh_ai_key_source = _refresh_ai_key_source
    app_class.save_openai_secret = save_openai_secret
    app_class.save_connection_settings = save_connection_settings
    app_class._phase49_3i_secret_persistence_installed = True
