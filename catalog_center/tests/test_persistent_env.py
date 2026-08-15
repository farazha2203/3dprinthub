from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from app.env_settings import load_project_env, parse_env_file


class PersistentEnvTests(unittest.TestCase):
    def test_parser_and_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text(
                'CATALOG_AI_PROVIDER="avalai"\n'
                'AVALAI_API_KEY="test-value"\n'
                'CATALOG_FTP_PORT=21\n',
                encoding="utf-8",
            )
            values = parse_env_file(path)
            self.assertEqual(values["CATALOG_AI_PROVIDER"], "avalai")
            self.assertEqual(values["AVALAI_API_KEY"], "test-value")
            old = os.environ.get("CATALOG_AI_PROVIDER")
            try:
                load_project_env(path, override=True)
                self.assertEqual(os.environ["CATALOG_AI_PROVIDER"], "avalai")
            finally:
                if old is None:
                    os.environ.pop("CATALOG_AI_PROVIDER", None)
                else:
                    os.environ["CATALOG_AI_PROVIDER"] = old

    def test_upgrade_preserves_env_contract(self):
        upgrade = (Path(__file__).resolve().parents[1] / "app" / "upgrade.py").read_text(
            encoding="utf-8", errors="replace"
        )
        self.assertIn('".env"', upgrade)
        self.assertIn("persistent_name", upgrade)
        self.assertIn("shutil.copy2(current_file, staged_file)", upgrade)
