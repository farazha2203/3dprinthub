import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QBuffer
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QDialog, QTabWidget

from app.db import Database
from qt6.social_ai_tab import SocialAICreativeTab
from app.social_ai_design import POST_STYLES, STORY_STYLES


class _Images:
    def __init__(self, path):
        self.path = str(path)

    def display_local_paths(self, _product):
        return [self.path]


class _Kernel:
    def __init__(self, path):
        self.images = _Images(path)


def _png_bytes():
    image = QImage(96, 96, QImage.Format.Format_ARGB32)
    image.fill(0xFFCC66)
    buffer = QBuffer()
    buffer.open(QBuffer.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


class SocialAIPopupSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_story_post_popup_generate_approve_close_reopen(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            image_path = root / "product.png"
            image_path.write_bytes(_png_bytes())
            db = Database(root / "catalog.sqlite3")
            product_id = db.upsert_product({
                "source_code": "smoke",
                "external_id": "1",
                "source_url": "https://example.test/product/1",
                "source_title": "Smoke Lamp",
                "source_description": "A factual lamp preview",
                "local_dir": str(root),
            })
            kernel = _Kernel(image_path)
            selected = lambda: [product_id]
            db.set_setting("social_image_provider", "openrouter")
            db.set_setting("social_image_model", "vendor/cheap")

            dialog = QDialog()
            tabs = QTabWidget(dialog)
            story = SocialAICreativeTab(db, kernel, selected, kind="story", parent=tabs)
            post = SocialAICreativeTab(db, kernel, selected, kind="post", parent=tabs)
            tabs.addTab(story, "Story")
            tabs.addTab(post, "Post")
            self.assertEqual(len(story.styles), 6)
            self.assertEqual(len(post.styles), 6)
            self.assertIn("vendor/cheap", story.image_model_status.text())

            story.generate_mock()
            self.assertIsNotNone(story.preview.pixmap())
            self.assertEqual(len(db.social_ai_revisions(product_id, "story")), 1)
            story.approve_revision()
            self.assertEqual(story.current_revision["approved"], 1)
            story.prepare_for_send()
            self.assertEqual(story.current_revision["selected_for_publish"], 1)
            dialog.close()

            reopened = SocialAICreativeTab(db, kernel, selected, kind="story")
            self.assertIsNotNone(reopened.preview.pixmap())
            self.assertEqual(reopened.current_revision["style_key"], STORY_STYLES[0].key)
            self.assertEqual(reopened.current_revision["approved"], 1)
            db.conn.close()


if __name__ == "__main__":
    unittest.main()
