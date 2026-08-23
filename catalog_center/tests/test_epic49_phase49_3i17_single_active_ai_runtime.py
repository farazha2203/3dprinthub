from __future__ import annotations

import types
import unittest
from unittest.mock import patch

from app.ai_providers import AIProviderClient
from app import phase49_3f_gemini_provider as gemini_provider
from app.phase49_3i17_single_active_ai_runtime import (
    _install_exact_google_model_shortcut,
    _install_product_probe_shortcut,
    _patch_app_instance,
    active_ai_config,
    install,
)


class _Var:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class _DB:
    def __init__(self, values=None):
        self.values = dict(values or {})

    def setting(self, key, default=""):
        return self.values.get(key, default)

    def set_setting(self, key, value):
        self.values[key] = value


class _App:
    def __init__(self, values=None):
        self.db = _DB(values)
        self.ai_provider = _Var("auto")
        self.ai_model = _Var("")
        self.openai_model = self.ai_model
        self._phase49_3d_active_provider = _Var("avalai")
        self._phase49_3d_auto_prepare_var = _Var(1)
        self.reported = []
        self.logger = types.SimpleNamespace(warning=lambda *args, **kwargs: None)

    def report_callback_exception(self, exc_type, exc_value, exc_traceback):
        self.reported.append((exc_type, exc_value, exc_traceback))


class _Progress:
    def step(self, *args, **kwargs):
        return None

    def done(self, *args, **kwargs):
        return None

    def fail(self, *args, **kwargs):
        return None

    def close(self, *args, **kwargs):
        return None


class _WorkspaceModule:
    AIProgress = _Progress


class _Workspace:
    def __init__(self, app, product_id):
        self.app = app
        self.db = app.db
        self.product_id = product_id
        self.footer_status = _Var("")

    def _phase49_3e_provider(self):
        return "legacy", "legacy-key", "legacy-model"

    def _phase49_3d_auto_prepare_on_open(self):
        raise AssertionError("hidden AI-on-open must not execute")


class Phase493I17SingleActiveAIRuntimeTests(unittest.TestCase):
    def test_saved_provider_and_model_are_the_only_runtime_identity(self):
        app = _App({
            "ai_provider": "openrouter",
            "ai_model": "wrong-global-model",
            "ai_model_openrouter": "openai/gpt-5.4-mini",
        })
        with patch(
            "app.phase49_3i17_single_active_ai_runtime.secure_secrets.get_provider_key",
            side_effect=lambda provider: {
                "avalai": "aval-key-that-must-never-win",
                "openrouter": "router-key",
            }.get(provider, ""),
        ) as get_key:
            provider, key, model = active_ai_config(app)
        self.assertEqual((provider, key, model), ("openrouter", "router-key", "openai/gpt-5.4-mini"))
        get_key.assert_called_once_with("openrouter")

    def test_auto_mode_or_unsaved_provider_fails_closed_instead_of_falling_back(self):
        app = _App({"ai_provider": "auto", "ai_model": "gpt-5.4-mini"})
        with patch(
            "app.phase49_3i17_single_active_ai_runtime.secure_secrets.get_provider_key",
            return_value="aval-key",
        ) as get_key:
            with self.assertRaises(RuntimeError):
                active_ai_config(app)
        get_key.assert_not_called()

    def test_app_instance_rejects_cross_provider_key_requests(self):
        app = _App({
            "ai_provider": "google",
            "ai_model_google": "gemini-2.5-flash-lite",
        })
        with patch(
            "app.phase49_3i17_single_active_ai_runtime.secure_secrets.get_provider_key",
            return_value="google-key",
        ):
            _patch_app_instance(app)
            self.assertEqual(app._selected_ai_provider(), "google")
            self.assertEqual(app._ai_key("google"), "google-key")
            with self.assertRaises(RuntimeError):
                app._ai_key("avalai")
        self.assertEqual(app.db.setting("ai_auto_prepare_on_open"), "0")
        self.assertEqual(app._phase49_3d_auto_prepare_var.get(), 0)

    def test_workspace_uses_saved_identity_and_disables_hidden_auto_ai(self):
        class Workspace(_Workspace):
            pass

        class WorkspaceModule:
            class AIProgress(_Progress):
                pass

        install(Workspace, WorkspaceModule)
        app = _App({
            "ai_provider": "avalai",
            "ai_model_avalai": "gpt-5.4-mini",
        })
        with patch(
            "app.phase49_3i17_single_active_ai_runtime.secure_secrets.get_provider_key",
            return_value="aval-key",
        ):
            workspace = Workspace(app, 117)
            self.assertEqual(workspace._phase49_3e_provider(), ("avalai", "aval-key", "gpt-5.4-mini"))
            self.assertIsNone(workspace._phase49_3d_auto_prepare_on_open())
        self.assertIn("غیرفعال", workspace.footer_status.get())

    def test_product_probe_does_not_download_model_catalog(self):
        original_probe = getattr(AIProviderClient, "probe_connection", None)
        original_marker = getattr(AIProviderClient, "_phase49_3i17_product_probe_shortcut", None)
        try:
            calls = []

            def base_probe(self, timeout=30):
                calls.append((self.provider, timeout))
                return {"connected": True, "models_count": 99}

            AIProviderClient.probe_connection = base_probe
            if hasattr(AIProviderClient, "_phase49_3i17_product_probe_shortcut"):
                delattr(AIProviderClient, "_phase49_3i17_product_probe_shortcut")
            _install_product_probe_shortcut()
            product_client = AIProviderClient("avalai", "key", "gpt-5.4-mini", product_id=117)
            result = product_client.probe_connection(timeout=30)
            self.assertEqual(result["models_count"], 1)
            self.assertFalse(result["network_probe"])
            self.assertEqual(calls, [])

            settings_client = AIProviderClient("avalai", "key", "gpt-5.4-mini", product_id=None)
            self.assertEqual(settings_client.probe_connection(timeout=12)["models_count"], 99)
            self.assertEqual(calls, [("avalai", 12)])
        finally:
            if original_probe is None:
                try:
                    delattr(AIProviderClient, "probe_connection")
                except AttributeError:
                    pass
            else:
                AIProviderClient.probe_connection = original_probe
            if original_marker is None:
                try:
                    delattr(AIProviderClient, "_phase49_3i17_product_probe_shortcut")
                except AttributeError:
                    pass
            else:
                AIProviderClient._phase49_3i17_product_probe_shortcut = original_marker

    def test_google_product_request_uses_exact_model_without_listing_models(self):
        original_info = gemini_provider._google_model_info
        original_marker = getattr(gemini_provider, "_phase49_3i17_exact_model_shortcut", None)
        try:
            calls = []

            def network_model_info(client, timeout=30):
                calls.append(timeout)
                return [{"id": "network-model"}]

            gemini_provider._google_model_info = network_model_info
            if hasattr(gemini_provider, "_phase49_3i17_exact_model_shortcut"):
                delattr(gemini_provider, "_phase49_3i17_exact_model_shortcut")
            _install_exact_google_model_shortcut()

            product_client = types.SimpleNamespace(
                product_id=117,
                model="gemini-2.5-flash-lite",
            )
            info = gemini_provider._google_model_info(product_client, timeout=30)
            self.assertEqual(info[0]["id"], "gemini-2.5-flash-lite")
            self.assertEqual(calls, [])

            settings_client = types.SimpleNamespace(product_id=None, model="gemini-2.5-flash-lite")
            info = gemini_provider._google_model_info(settings_client, timeout=17)
            self.assertEqual(info[0]["id"], "network-model")
            self.assertEqual(calls, [17])
        finally:
            gemini_provider._google_model_info = original_info
            if original_marker is None:
                try:
                    delattr(gemini_provider, "_phase49_3i17_exact_model_shortcut")
                except AttributeError:
                    pass
            else:
                gemini_provider._phase49_3i17_exact_model_shortcut = original_marker

    def test_stale_tk_invalid_command_callback_is_not_promoted_to_fatal_dialog(self):
        app = _App({
            "ai_provider": "avalai",
            "ai_model_avalai": "gpt-5.4-mini",
        })
        with patch(
            "app.phase49_3i17_single_active_ai_runtime.secure_secrets.get_provider_key",
            return_value="aval-key",
        ):
            _patch_app_instance(app)
        app.report_callback_exception(
            __import__("tkinter").TclError,
            __import__("tkinter").TclError('invalid command name ".!productworkspace.!listbox"'),
            None,
        )
        self.assertEqual(app.reported, [])


if __name__ == "__main__":
    unittest.main()
