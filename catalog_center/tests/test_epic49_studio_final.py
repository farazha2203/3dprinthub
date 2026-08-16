from __future__ import annotations

import inspect
import unittest
from pathlib import Path

from app.epic49_product_studio_final import ProductStudio


ROOT = Path(__file__).resolve().parents[1]


class Epic49FinalStudioTests(unittest.TestCase):
    def test_final_studio_preserves_legacy_seo_entry(self):
        source = inspect.getsource(ProductStudio._content_ui)
        self.assertIn("باز کردن استودیوی کامل SEO", source)
        self.assertIn("open_content_studio", source)

    def test_license_controls_are_reconciled_before_save(self):
        reconcile = inspect.getsource(ProductStudio._reconcile_license_controls)
        save = inspect.getsource(ProductStudio.save)
        self.assertIn("quick_code", reconcile)
        self.assertIn("publish_code", reconcile)
        self.assertIn("database_code", reconcile)
        self.assertIn("self._reconcile_license_controls()", save)

    def test_launchers_use_final_studio_class(self):
        launch = (ROOT / "launch.py").read_text(encoding="utf-8")
        portable = (ROOT / "portable_entry.py").read_text(encoding="utf-8")
        self.assertIn("app.epic49_product_studio_final", launch)
        self.assertIn("app.epic49_product_studio_final", portable)
        self.assertIn("ProductStudio = Epic49ProductStudio", launch)
        self.assertIn("ProductStudio = Epic49ProductStudio", portable)


if __name__ == "__main__":
    unittest.main()
