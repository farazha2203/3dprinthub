from __future__ import annotations

import unittest
from pathlib import Path


class Phase493CPersianTranslateGuardContractTests(unittest.TestCase):
    def test_translate_guard_is_loaded_by_launcher(self):
        root = Path(__file__).resolve().parents[1]
        launcher = (root / "launch.py").read_text(encoding="utf-8")
        self.assertIn("phase49_3c_persian_translate_guard", launcher)
        self.assertIn("EPIC49_3C_PERSIAN_TRANSLATE_GUARD=ENABLED", launcher)

    def test_translate_guard_contains_strict_persian_repair_path(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "app" / "phase49_3c_persian_translate_guard.py").read_text(encoding="utf-8")
        for token in (
            "_language_invalid_fields",
            "_repair_with_provider",
            "_generic_persian_pack",
            "AI_PERSIAN_TRANSLATE_REPAIR_FAILED",
            "_phase49_3c_persian_translate_guard_installed",
        ):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
