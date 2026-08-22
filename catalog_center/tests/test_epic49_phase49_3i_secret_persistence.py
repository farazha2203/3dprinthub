from __future__ import annotations

import unittest
from unittest.mock import patch

from app.phase49_3i_secret_persistence import install


class _Var:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


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


class Phase493ISecretPersistenceTests(unittest.TestCase):
    def _class(self):
        class App(_DummyApp):
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
