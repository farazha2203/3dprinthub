from __future__ import annotations

from django.apps import AppConfig


class SmartBaseAdminBridgeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "smartbase_admin_bridge"
    verbose_name = "مدیریت هوشمند 3DPrintHub"

    def ready(self) -> None:
        # SmartBase autodiscovers ``sb_admin.py`` before this hook. Signals are
        # connected afterwards so all project models are already loaded.
        from . import signals  # noqa: F401
