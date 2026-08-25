from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V854LauncherTests(unittest.TestCase):
    def test_absolute_launcher_ignores_stale_app_in_callers_working_directory(self):
        from app.version import APP_VERSION

        with tempfile.TemporaryDirectory() as temporary:
            shadow = Path(temporary)
            (shadow / "app").mkdir()
            (shadow / "app" / "__init__.py").write_text("", encoding="utf-8")
            (shadow / "app" / "version.py").write_text(
                'APP_VERSION = "8.5.1"\nBUILD_ID = "stale"\nSOURCE_ROOT = "wrong"\n',
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(ROOT / "launch.py"), "--verify-only"],
                cwd=shadow,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"ACTIVE_VERSION={APP_VERSION}", result.stdout)
        self.assertIn("UX87_SHELL=ENABLED", result.stdout)
        self.assertIn("PRODUCT_WORKSPACE_V87=ENABLED", result.stdout)
        self.assertIn("PRODUCT_WORKSPACE_V871=ENABLED", result.stdout)
        self.assertIn("HOMEPAGE_SLIDER_SEO_V871=ENABLED", result.stdout)
        self.assertIn("AI_PROFILE_MIGRATION=PRESERVED", result.stdout)
        self.assertIn("HOST_PROFILE_MIGRATION=PRESERVED", result.stdout)
        self.assertIn(f"ACTIVE_SOURCE={ROOT}", result.stdout)
        self.assertNotIn("ACTIVE_VERSION=8.5.1", result.stdout)

    def test_manifest_app_launcher_and_config_versions_match(self):
        manifest = json.loads((ROOT / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
        config = json.loads((ROOT / "config.example.json").read_text(encoding="utf-8"))
        from app.version import APP_VERSION
        from launch import EXPECTED_VERSION

        self.assertEqual(
            {manifest["version"], config["package_version"], APP_VERSION, EXPECTED_VERSION},
            {APP_VERSION},
        )

    def test_every_manifest_file_exists(self):
        manifest = json.loads((ROOT / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
        missing = [name for name in manifest["files"] if not (ROOT / name).is_file()]
        self.assertEqual(missing, [])

    def test_run_scripts_do_not_launch_app_main_as_an_ambient_module(self):
        run_text = (ROOT / "RUN.ps1").read_text(encoding="utf-8")
        debug_text = (ROOT / "RUN_DEBUG.ps1").read_text(encoding="utf-8")
        self.assertIn('"$Root\\launch.py"', run_text)
        self.assertIn('"$Root\\launch.py"', debug_text)
        self.assertNotIn("-m app.main", run_text)
        self.assertNotIn("-m app.main", debug_text)


if __name__ == "__main__":
    unittest.main()
