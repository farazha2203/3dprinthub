from __future__ import annotations

import ast
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Phase493I53HostAIImportSafetyTests(unittest.TestCase):
    def _top_level_import_modules(self, relative: str) -> set[str]:
        tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
        modules: set[str] = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                modules.add(str(node.module or ""))
        return modules

    def test_site_ai_modules_do_not_eagerly_import_transport_clients(self):
        model_imports = self._top_level_import_modules("ai/model_policy.py")
        content_imports = self._top_level_import_modules("ai/product_content.py")

        self.assertNotIn("catalog_center.app.ai_providers", model_imports)
        self.assertNotIn("catalog_center.app.openai_content", content_imports)

    def test_django_setup_does_not_require_httpx_import(self):
        code = r"""
import os
import sys
sys.modules["httpx"] = None
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
print("DJANGO_SETUP_WITHOUT_HTTPX_IMPORT=PASS")
"""
        env = dict(os.environ)
        env.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
        proc = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + "\n" + proc.stderr)
        self.assertIn("DJANGO_SETUP_WITHOUT_HTTPX_IMPORT=PASS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
