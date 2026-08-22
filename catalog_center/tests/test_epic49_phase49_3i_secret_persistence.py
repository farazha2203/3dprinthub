from __future__ import annotations

import unittest
from unittest.mock import patch

from app.phase49_3i_secret_persistence import (
    _apply_model_catalog,
    install,
)


class _Var:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class _Box:
    def __init__(self):
        self.values = []

    def configure(self, **kwargs):
        if "values" in kwargs:
            self.values = list(kwargs["values"])


class _DummyApp:
    def _init_ux87_settings_state(self):
        self.ai_provider = _Var("openai")
        self.ai_key = _Var("")
        self.ftp_password = _Var("")
        self.bridge_token = _Var("")

    def _selected_ai_provider(self):
        return self.ai_provider.get()

    def _refresh_ai_key_source(self):
        self.refresh_count = getattr(self, "refresh_count", 0) + 1

    def save_openai_secret(self):
        self.ai_key.set("")
        self.ai_saved = True

    def save_connection_settings(self):
        self.ftp_password.set("")
        self.bridge_token.set("")
        self.connection_saved = True


class _ModernDummyApp(_DummyApp):
    def _init_ux87_settings_state(self):
        super()._init_ux87_settings_state()
        self._ai_hub_key_vars = {
            "avalai": _Var(""),
            "openrouter": _Var(""),
            "google": _Var(""),
            "openai": _Var(""),
        }
        self._ai_hub_model_vars = {
            provider: _Var("") for provider in self._ai_hub_key_vars
        }
        self._ai_hub_status_vars = {
            provider: _Var("") for provider in self._ai_hub_key_vars
        }
        self._ai_hub_model_boxes = {
            provider: _Box() for provider in self._ai_hub_key_vars
        }
        self._phase49_3d_model_cache = {
            provider: [] for provider in self._ai_hub_key_vars
        }
        self._openrouter_management_key_var = _Var("")
        self._openai_admin_key_var = _Var("")
        self._phase49_3d_active_provider = _Var("openrouter")
        self.after_callbacks = []

    def _build_ux87_ai_center(self):
        self.ai_center_built = True

    def after(self, _delay, callback):
        self.after_callbacks.append(callback)
        return len(self.after_callbacks)

    def _phase49_3f_save_card(self, provider):
        self._ai_hub_key_vars[provider].set("")
        self.provider_saved = provider

    def _phase49_3d_save_active_ai(self):
        provider = self._phase49_3d_active_provider.get()
        self._ai_hub_key_vars[provider].set("")
        self.active_saved = provider


class Phase493ISecretPersistenceTests(unittest.TestCase):
    def _class(self):
        class App(_DummyApp):
            pass

        install(App)
        return App

    def _modern_class(self):
        class App(_ModernDummyApp):
            pass

        install(App)
        return App

    def test_startup_hydrates_secure_fields_without_sqlite(self):
        App = self._class()
        with patch(
            "app.phase49_3i_secret_persistence.get_provider_key",
            side_effect=lambda provider: {"openai": "openai-secret"}.get(provider, ""),
        ), patch(
            "app.phase49_3i_secret_persistence.get_secret",
            side_effect=lambda name: {
                "ftp_password": "ftp-secret",
                "bridge_token": "bridge-secret",
            }.get(name, ""),
        ):
            app = App()
            app._init_ux87_settings_state()

        self.assertEqual(app.ai_key.get(), "openai-secret")
        self.assertEqual(app.ftp_password.get(), "ftp-secret")
        self.assertEqual(app.bridge_token.get(), "bridge-secret")
        self.assertFalse(hasattr(app, "db"))

    def test_successful_save_rehydrates_fields_cleared_by_mature_handlers(self):
        App = self._class()
        with patch(
            "app.phase49_3i_secret_persistence.get_provider_key",
            return_value="openai-secret",
        ), patch(
            "app.phase49_3i_secret_persistence.get_secret",
            side_effect=lambda name: {
                "ftp_password": "ftp-secret",
                "bridge_token": "bridge-secret",
            }.get(name, ""),
        ):
            app = App()
            app._init_ux87_settings_state()
            app.save_openai_secret()
            app.save_connection_settings()

        self.assertTrue(app.ai_saved)
        self.assertTrue(app.connection_saved)
        self.assertEqual(app.ai_key.get(), "openai-secret")
        self.assertEqual(app.ftp_password.get(), "ftp-secret")
        self.assertEqual(app.bridge_token.get(), "bridge-secret")

    def test_provider_change_loads_that_providers_secure_key(self):
        App = self._class()
        keys = {"openai": "openai-secret", "avalai": "avalai-secret"}
        with patch(
            "app.phase49_3i_secret_persistence.get_provider_key",
            side_effect=lambda provider: keys.get(provider, ""),
        ), patch(
            "app.phase49_3i_secret_persistence.get_secret",
            return_value="",
        ):
            app = App()
            app._init_ux87_settings_state()
            self.assertEqual(app.ai_key.get(), "openai-secret")
            app.ai_provider.set("avalai")
            app._refresh_ai_key_source()

        self.assertEqual(app.ai_key.get(), "avalai-secret")

    def test_regular_refresh_does_not_overwrite_unsaved_key_for_same_provider(self):
        App = self._class()
        with patch(
            "app.phase49_3i_secret_persistence.get_provider_key",
            return_value="stored-secret",
        ), patch(
            "app.phase49_3i_secret_persistence.get_secret",
            return_value="",
        ):
            app = App()
            app._init_ux87_settings_state()
            app.ai_key.set("new-unsaved-key")
            app._refresh_ai_key_source()

        self.assertEqual(app.ai_key.get(), "new-unsaved-key")

    def test_modern_provider_hub_hydrates_every_real_provider_field(self):
        App = self._modern_class()
        keys = {
            "avalai": "aval-secret",
            "openrouter": "router-secret",
            "google": "google-secret",
            "openai": "openai-secret",
        }
        connection = {
            "ftp_password": "ftp-secret",
            "bridge_token": "bridge-secret",
            "openrouter_management_key": "management-secret",
            "openai_admin_key": "admin-secret",
        }
        with patch(
            "app.phase49_3i_secret_persistence.get_provider_key",
            side_effect=lambda provider: keys.get(provider, ""),
        ), patch(
            "app.phase49_3i_secret_persistence.get_secret",
            side_effect=lambda name: connection.get(name, ""),
        ):
            app = App()
            app._init_ux87_settings_state()

        for provider, secret in keys.items():
            self.assertEqual(app._ai_hub_key_vars[provider].get(), secret)
        self.assertEqual(app._openrouter_management_key_var.get(), "management-secret")
        self.assertEqual(app._openai_admin_key_var.get(), "admin-secret")
        self.assertEqual(app.ftp_password.get(), "ftp-secret")
        self.assertEqual(app.bridge_token.get(), "bridge-secret")

    def test_modern_provider_save_rehydrates_field_after_mature_clear(self):
        App = self._modern_class()
        keys = {"openrouter": "router-secret", "openai": "openai-secret"}
        with patch(
            "app.phase49_3i_secret_persistence.get_provider_key",
            side_effect=lambda provider: keys.get(provider, ""),
        ), patch(
            "app.phase49_3i_secret_persistence.get_secret",
            return_value="",
        ), patch(
            "app.phase49_3i_secret_persistence._load_provider_models_async",
            return_value=None,
        ):
            app = App()
            app._init_ux87_settings_state()
            app._phase49_3f_save_card("openrouter")
            self.assertEqual(app._ai_hub_key_vars["openrouter"].get(), "router-secret")
            app._phase49_3d_save_active_ai()
            self.assertEqual(app._ai_hub_key_vars["openrouter"].get(), "router-secret")

        self.assertEqual(app.provider_saved, "openrouter")
        self.assertEqual(app.active_saved, "openrouter")

    def test_ai_center_schedules_model_catalogs_for_configured_providers(self):
        App = self._modern_class()
        keys = {"avalai": "aval-secret", "openrouter": "router-secret"}
        called = []
        with patch(
            "app.phase49_3i_secret_persistence.get_provider_key",
            side_effect=lambda provider: keys.get(provider, ""),
        ), patch(
            "app.phase49_3i_secret_persistence.get_secret",
            return_value="",
        ), patch(
            "app.phase49_3i_secret_persistence._load_provider_models_async",
            side_effect=lambda app, provider, force=False: called.append(provider),
        ):
            app = App()
            app._init_ux87_settings_state()
            app._build_ux87_ai_center()
            for callback in list(app.after_callbacks):
                callback()

        self.assertTrue(app.ai_center_built)
        self.assertEqual(called, ["avalai", "openrouter"])

    def test_model_catalog_populates_cache_combobox_and_status(self):
        app = _ModernDummyApp()
        app._init_ux87_settings_state()
        info = [
            {"id": "model-a", "name": "A"},
            {"id": "model-b", "name": "B"},
        ]
        _apply_model_catalog(app, "openrouter", info)
        self.assertEqual(app._phase49_3d_model_cache["openrouter"], info)
        self.assertEqual(app._ai_hub_model_boxes["openrouter"].values, ["model-a", "model-b"])
        self.assertIn("2", app._ai_hub_status_vars["openrouter"].get())

    def test_module_never_mentions_sqlite_logging_or_secret_persistence_files(self):
        from pathlib import Path

        source = (
            Path(__file__).resolve().parents[1]
            / "app"
            / "phase49_3i_secret_persistence.py"
        ).read_text(encoding="utf-8").lower()
        self.assertNotIn("set_setting(", source)
        self.assertNotIn("logger.", source)
        self.assertNotIn("write_text(", source)
        self.assertNotIn("open(", source)


if __name__ == "__main__":
    unittest.main()
