from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from qt6.image_gallery import ProductImageGrid


class Phase50O6A1MediaDisplayHotfixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def _item(path: Path, name: str) -> dict:
        return {
            "url": f"local://{name}",
            "path": str(path),
            "filename": name,
            "downloaded": True,
            "selected": True,
        }

    def test_refresh_detaches_stale_cards_before_rebuild(self):
        first = self.root / "first.webp"
        second = self.root / "second.webp"
        Image.new("RGB", (64, 64), (220, 20, 20)).save(first, "WEBP")
        Image.new("RGB", (64, 64), (20, 20, 220)).save(second, "WEBP")

        grid = ProductImageGrid(columns=3, large_cards=True)
        try:
            grid.show()
            grid.set_items([self._item(first, first.name)])
            old_card = grid.cards[0]
            self.assertIsNotNone(old_card.parent())

            grid.set_items([self._item(second, second.name)])

            self.assertTrue(old_card.isHidden())
            self.assertIsNone(old_card.parent())
            self.assertEqual(len(grid.cards), 1)
            self.assertEqual(grid.cards[0].item["filename"], second.name)
        finally:
            grid.close()

    def test_reload_decodes_current_bytes_from_same_filename(self):
        path = self.root / "same-final.webp"
        Image.new("RGB", (72, 72), (230, 15, 15)).save(path, "WEBP")

        grid = ProductImageGrid(columns=3, large_cards=True)
        try:
            payload = [self._item(path, path.name)]
            grid.set_items(payload)
            first_image = grid.cards[0].preview.pixmap().toImage()
            first_color = first_image.pixelColor(
                max(0, first_image.width() // 2),
                max(0, first_image.height() // 2),
            )
            self.assertGreater(first_color.red(), first_color.blue())

            Image.new("RGB", (72, 72), (15, 15, 230)).save(path, "WEBP")
            grid.set_items(payload)
            second_image = grid.cards[0].preview.pixmap().toImage()
            second_color = second_image.pixelColor(
                max(0, second_image.width() // 2),
                max(0, second_image.height() // 2),
            )
            self.assertGreater(second_color.blue(), second_color.red())
        finally:
            grid.close()


if __name__ == "__main__":
    unittest.main()
