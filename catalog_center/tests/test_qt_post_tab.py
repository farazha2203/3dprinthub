"""Qt6 structural regression for the operator-visible Post tab."""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
CATALOG_ROOT = Path(__file__).resolve().parents[1]
if str(CATALOG_ROOT) not in sys.path:
    sys.path.insert(0, str(CATALOG_ROOT))

from PySide6.QtWidgets import QApplication  # noqa: E402

from catalog_center.app.post_composer import POST_STYLES  # noqa: E402
from catalog_center.qt6.product_wizard import ProductWizardPage  # noqa: E402


class QtPostTabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_active_qt_wizard_exposes_safe_post_controls(self):
        kernel = SimpleNamespace(
            providers=SimpleNamespace(source_modes=lambda: []),
        )
        wizard = ProductWizardPage(None, kernel=kernel)
        self.addCleanup(wizard.deleteLater)

        self.assertEqual(wizard.content_tabs.tabText(2), "Post")
        self.assertEqual(set(wizard.post_style_buttons), {key for key, _ in POST_STYLES})
        self.assertEqual(len(wizard.post_style_buttons), 12)
        self.assertEqual(wizard.post_mock_btn.objectName(), "post_mock_button")
        self.assertFalse(hasattr(wizard, "post_send_btn"))


if __name__ == "__main__":
    unittest.main()
