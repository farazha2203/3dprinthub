from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace

from app.main import App, normalize_bridge_token_input


ROOT = Path(__file__).resolve().parents[1]


class _Variable:
    def __init__(self, value: str):
        self.value = value

    def get(self) -> str:
        return self.value

    def set(self, value: str) -> None:
        self.value = value


class _Entry:
    def __init__(self):
        self.show = "•"

    def configure(self, *, show: str) -> None:
        self.show = show


class V854BridgeTokenTests(unittest.TestCase):
    def test_plain_token_is_trimmed(self):
        self.assertEqual(normalize_bridge_token_input("  unit-test-token  \r\n"), "unit-test-token")

    def test_dotenv_assignment_returns_only_the_value(self):
        self.assertEqual(
            normalize_bridge_token_input("CATALOG_BRIDGE_TOKEN=unit-test-token"),
            "unit-test-token",
        )

    def test_exported_quoted_assignment_is_supported(self):
        self.assertEqual(
            normalize_bridge_token_input("export catalog_bridge_token='unit-test-token'"),
            "unit-test-token",
        )

    def test_matching_assignment_is_found_in_multiline_clipboard_text(self):
        copied = "command output\nCATALOG_BRIDGE_TOKEN=unit-test-token\nnext line"
        self.assertEqual(normalize_bridge_token_input(copied), "unit-test-token")

    def test_unrelated_multiline_text_is_rejected(self):
        self.assertEqual(normalize_bridge_token_input("first line\nsecond line"), "")

    def test_app_connection_path_uses_the_same_normalizer(self):
        holder = SimpleNamespace(bridge_token=_Variable("CATALOG_BRIDGE_TOKEN=unit-test-token"))
        self.assertEqual(App._entered_bridge_token(holder), "unit-test-token")
        holder.bridge_token = _Variable("first line\nsecond line")
        with self.assertRaises(ValueError):
            App._entered_bridge_token(holder)

    def test_bridge_token_is_not_written_to_sqlite_settings(self):
        main_text = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
        self.assertNotIn('set_setting("bridge_token"', main_text)
        self.assertIn('set_secret("bridge_token",entered_token)', main_text)

    def test_paste_action_extracts_assignment_without_exposing_it_in_status(self):
        holder = SimpleNamespace(
            clipboard_get=lambda: "CATALOG_BRIDGE_TOKEN=unit-test-token\r\n",
            bridge_token=_Variable(""),
            status=_Variable(""),
        )
        self.assertEqual(App.paste_bridge_token(holder), "break")
        self.assertEqual(holder.bridge_token.get(), "unit-test-token")
        self.assertNotIn("unit-test-token", holder.status.get())

    def test_visibility_action_toggles_mask_without_changing_token(self):
        holder = SimpleNamespace(
            bridge_token_visible=False,
            bridge_token_entry=_Entry(),
            bridge_token=_Variable("unit-test-token"),
        )
        App.toggle_bridge_token_visibility(holder)
        self.assertEqual(holder.bridge_token_entry.show, "")
        App.toggle_bridge_token_visibility(holder)
        self.assertEqual(holder.bridge_token_entry.show, "•")
        self.assertEqual(holder.bridge_token.get(), "unit-test-token")

    def test_ui_source_wires_all_required_paste_paths(self):
        main_text = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
        for marker in (
            'self.bridge_token_entry=ttk.Entry',
            'bind("<Control-v>",self.paste_bridge_token)',
            'bind("<Control-V>",self.paste_bridge_token)',
            'bind("<Shift-Insert>",self.paste_bridge_token)',
            'bind("<Button-3>",self.open_bridge_token_menu)',
            'text="چسباندن توکن"',
            'text="نمایش/مخفی"',
        ):
            self.assertIn(marker, main_text)


if __name__ == "__main__":
    unittest.main()
