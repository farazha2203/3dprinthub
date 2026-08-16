from __future__ import annotations

import inspect
import unittest
from pathlib import Path

from app.epic49_product_studio_final import ProductStudio as Epic49ProductStudio
from app.product_workspace_v87 import ProductWorkspace


ROOT = Path(__file__).resolve().parents[1]


class Epic49FinalStudioTests(unittest.TestCase):
    def test_v87_workspace_hides_duplicate_legacy_seo_entry(self):
        legacy = inspect.getsource(Epic49ProductStudio._content_ui)
        workspace = inspect.getsource(ProductWorkspace._remove_duplicate_legacy_actions)
        self.assertIn("باز کردن استودیوی کامل SEO", legacy)
        self.assertIn("استودیوی کامل SEO", workspace)
        self.assertIn("pack_forget", workspace)

    def test_license_controls_are_reconciled_before_save(self):
        reconcile = inspect.getsource(Epic49ProductStudio._reconcile_license_controls)
        save = inspect.getsource(Epic49ProductStudio.save)
        self.assertIn("quick_code", reconcile)
        self.assertIn("publish_code", reconcile)
        self.assertIn("database_code", reconcile)
        self.assertIn("self._reconcile_license_controls()", save)

    def test_launchers_use_v87_workspace_and_shell(self):
        launch = (ROOT / "launch.py").read_text(encoding="utf-8")
        portable = (ROOT / "portable_entry.py").read_text(encoding="utf-8")
        for source in (launch, portable):
            self.assertIn("app.product_workspace_v87", source)
            self.assertIn("app.ux87_shell", source)
            self.assertIn("ProductWorkspace", source)
            self.assertIn("build_app_class", source)
        self.assertNotIn("ProductStudio as Epic49ProductStudio", launch)
        self.assertNotIn("ProductStudio as Epic49ProductStudio", portable)


if __name__ == "__main__":
    unittest.main()
