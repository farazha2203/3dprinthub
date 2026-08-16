from __future__ import annotations

from .secure_secrets import set_secret


NONSECRET_SETTINGS = (
    ("ftp_protocol", "FTP"),
    ("ftp_host", "ftp_host"),
    ("ftp_port", "ftp_port"),
    ("ftp_user", "ftp_user"),
    ("ftp_remote_root", "remote_root"),
    ("site_url", "site_url"),
)


def persist_connection_profile(app, cfg) -> None:
    """Persist a validated connection profile without writing secrets to SQLite."""
    for key, source in NONSECRET_SETTINGS:
        value = source if key == "ftp_protocol" else getattr(cfg, source)
        app.db.set_setting(key, str(value or ""))

    entered_password = app.ftp_password.get().strip() if hasattr(app, "ftp_password") else ""
    entered_token = app._entered_bridge_token() if hasattr(app, "_entered_bridge_token") else ""
    if entered_password:
        set_secret("ftp_password", entered_password)
    if entered_token:
        set_secret("bridge_token", entered_token)

    if hasattr(app, "_refresh_connection_secret_source"):
        app._refresh_connection_secret_source()


def install(app_main) -> None:
    """Patch App._site_connection once so successful Test/Publish also persists settings."""
    if getattr(app_main.App, "_epic49_persistent_connection_installed", False):
        return

    original = app_main.App._site_connection

    def _site_connection_with_persistence(self, require_bridge=True):
        cfg = original(self, require_bridge=require_bridge)
        persist_connection_profile(self, cfg)
        return cfg

    app_main.App._site_connection = _site_connection_with_persistence
    app_main.App._epic49_persistent_connection_installed = True
