from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from qt6.image_gallery import ImageCard, ImagePreviewDialog, ProductImageGrid


class Phase50ResponsiveImageWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.paths = []
        for index, size in enumerate(((1600, 900), (900, 1600), (1200, 1200), (1800, 1200)), 1):
            path = self.root / f"image-{index}.png"
            Image.new("RGB", size, "white").save(path)
            self.paths.append(path)

    def tearDown(self):
        self.temp.cleanup()

    def _items(self):
        output = []
        for index, path in enumerate(self.paths, 1):
            with Image.open(path) as image:
                width, height = image.size
            output.append(
                {
                    "url": f"https://example.invalid/image-{index}.png",
                    "path": str(path),
                    "filename": path.name,
                    "downloaded": True,
                    "selected": True,
                    "primary": index == 1,
                    "slider": index == 2,
                    "width": width,
                    "height": height,
                    "bytes": path.stat().st_size,
                    "alt_text": f"image {index}",
                }
            )
        return output

    def test_card_uses_large_uniform_preview_surface(self):
        card = ImageCard(self._items()[0])
        self.assertGreaterEqual(card.minimumWidth(), 280)
        self.assertGreaterEqual(card.minimumHeight(), 500)
        self.assertGreaterEqual(card.preview.minimumWidth(), 250)
        self.assertGreaterEqual(card.preview.minimumHeight(), 250)
        self.assertLessEqual(card.preview.maximumHeight(), 320)
        self.assertIsNotNone(card.preview.pixmap())

    def test_grid_reflows_from_one_to_four_columns_without_changing_desktop_max(self):
        grid = ProductImageGrid(columns=4)
        self.assertEqual(grid.columns, 4)
        self.assertEqual(grid._responsive_columns(350), 1)
        self.assertEqual(grid._responsive_columns(650), 2)
        self.assertEqual(grid._responsive_columns(980), 3)
        self.assertEqual(grid._responsive_columns(1320), 4)
        grid.resize(700, 800)
        grid.set_items(self._items())
        self.assertIn(grid._active_columns, {1, 2})
        self.assertEqual(len(grid.cards), 4)
        self.assertGreaterEqual(grid.host.minimumHeight(), 535)

    def test_large_preview_accepts_portrait_square_and_landscape(self):
        for path in self.paths[:3]:
            dialog = ImagePreviewDialog(str(path))
            self.assertGreaterEqual(dialog.width(), 1000)
            self.assertGreaterEqual(dialog.height(), 760)
            dialog.close()


if __name__ == "__main__":
    unittest.main()
