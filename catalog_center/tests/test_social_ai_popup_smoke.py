import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QBuffer
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox, QTabWidget

from app.db import Database
from qt6.social_ai_tab import SocialAICreativeTab
from app.social_ai_design import POST_STYLES, STORY_STYLES
from qt6.workers import Worker


class _Images:
    def __init__(self, path):
        self.path = str(path)

    def display_local_paths(self, _product):
        return [self.path]


class _Kernel:
    def __init__(self, path):
        self.images = _Images(path)


class _InlineTaskPool:
    """Run the normal Worker synchronously so popup wiring is deterministic in tests."""
    def start(self, worker):
        worker.run()


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
            send_calls = []
            db.set_setting("social_image_provider", "openrouter")
            db.set_setting("social_image_model", "vendor/cheap")

            dialog = QDialog()
            tabs = QTabWidget(dialog)
            story = SocialAICreativeTab(db, kernel, selected, kind="story", on_send=lambda *args: send_calls.append(args), parent=tabs)
            post = SocialAICreativeTab(db, kernel, selected, kind="post", on_send=lambda *args: send_calls.append(args), parent=tabs)
            tabs.addTab(story, "Story")
            tabs.addTab(post, "Post")
            self.assertEqual(len(story.styles), 6)
            self.assertEqual(len(post.styles), 6)
            self.assertFalse(story.send_button.isEnabled())
            self.assertFalse(post.send_button.isEnabled())
            self.assertIn("vendor/cheap", story.image_model_status.text())

            story.generate_mock()
            self.assertIsNotNone(story.preview.pixmap())
            self.assertEqual(len(db.social_ai_revisions(product_id, "story")), 1)
            # This fixture marks the persisted bytes as a real-generation result;
            # the separate mock-preview contract must never unlock sending.
            import hashlib, json
            source = db.social_ai_revisions(product_id, "story")[0]
            metadata = json.loads(source["metadata_json"])
            metadata["ai_generated"] = True
            metadata["mode"] = "provider"
            digest = hashlib.sha256(b"provider-confirmed-test-image").hexdigest()
            row = db.save_social_ai_revision(
                product_id, "story", STORY_STYLES[0].key, digest,
                source["image_blob"], metadata,
            )
            story.current_revision = row
            story._show_revision(row)
            story.approve_revision()
            self.assertEqual(story.current_revision["approved"], 1)
            story.prepare_for_send()
            self.assertEqual(story.current_revision["selected_for_publish"], 1)
            self.assertTrue(story.send_button.isEnabled())
            story.send_button.click()
            self.assertEqual(send_calls, [("story", product_id)])
            post.generate_mock()
            post_source = db.social_ai_revisions(product_id, "post")[0]
            post_metadata = json.loads(post_source["metadata_json"])
            post_metadata["ai_generated"] = True
            post_metadata["mode"] = "provider"
            post_digest = hashlib.sha256(b"provider-confirmed-test-post").hexdigest()
            post_row = db.save_social_ai_revision(
                product_id, "post", POST_STYLES[0].key, post_digest,
                post_source["image_blob"], post_metadata,
            )
            post.current_revision = post_row
            post._show_revision(post_row)
            post.approve_revision()
            post.prepare_for_send()
            self.assertTrue(post.send_button.isEnabled())
            post.send_button.click()
            self.assertEqual(send_calls, [("story", product_id), ("post", product_id)])
            dialog.close()

            reopened = SocialAICreativeTab(db, kernel, selected, kind="story")
            self.assertIsNotNone(reopened.preview.pixmap())
            self.assertEqual(reopened.current_revision["style_key"], STORY_STYLES[0].key)
            self.assertEqual(reopened.current_revision["approved"], 1)
            self.assertFalse(reopened.send_button.isEnabled(), "reopened tab is not wired to publisher in this isolated UI fixture")
            db.conn.close()

    def test_selected_style_reaches_image_provider_and_real_result_is_saved_idempotently(self):
        from unittest.mock import patch
        from app.social_ai_design import STORY_STYLES

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            image_path = root / "product.png"
            image_path.write_bytes(_png_bytes())
            generated = _png_bytes()
            db = Database(root / "catalog.sqlite3")
            product_id = db.upsert_product({
                "source_code": "smoke",
                "external_id": "2",
                "source_url": "https://example.test/product/2",
                "source_title": "Smoke Lamp",
                "source_description": "Orange lamp, source-confirmed",
                "local_dir": str(root),
            })
            db.set_setting("social_image_provider", "openrouter")
            db.set_setting("social_image_model", "vendor/cheap")
            db.set_setting("social_image_provider_tag", "cheap-provider")
            db.set_setting("social_image_supported_parameters_json", '{"input_references":{"max":2},"aspect_ratio":{"values":["9:16","4:5"]}}')
            db.set_setting("social_image_cost_usd", "0.03")
            db.set_setting("social_image_cost_unit", "image")
            db.set_setting("social_image_input_cost_usd", "0.003")
            db.set_setting("social_image_input_cost_unit", "image")
            tab = SocialAICreativeTab(db, _Kernel(image_path), lambda: [product_id], kind="story")
            tab._task_pool = _InlineTaskPool()
            tab._select(STORY_STYLES[1])
            try:
                with (
                    patch("qt6.social_ai_tab.get_provider_key", return_value="test-secret"),
                    patch("qt6.social_ai_tab.QMessageBox.question", return_value=QMessageBox.StandardButton.Yes) as confirmation,
                    patch("app.social_ai_design.generate_image_revision", return_value={
                        "bytes": generated,
                        "model": "vendor/cheap",
                        "usage": {"cost": 0},
                        "cost_usd": 0,
                    }) as provider,
                ):
                    tab.generate_image()
                    self.assertEqual(provider.call_count, 1)
                    args, kwargs = provider.call_args
                    self.assertEqual(args[0:2], ("test-secret", "vendor/cheap"))
                    self.assertIn("high-end vertical fashion-house campaign cover", args[2])
                    self.assertIn("Orange lamp", args[2])
                    self.assertEqual(kwargs["aspect_ratio"], "9:16")
                    self.assertEqual(kwargs["provider_tag"], "cheap-provider")
                    self.assertTrue(kwargs["brand_reference_bytes"])
                    self.assertIn("× 2 تصویر مرجع", confirmation.call_args.args[2])
                    self.assertIn("$0.036", confirmation.call_args.args[2])
                    rows = db.social_ai_revisions(product_id, "story")
                    self.assertEqual(len(rows), 1)
                    self.assertEqual(rows[0]["image_blob"], generated)
                    self.assertEqual(rows[0]["approved"], 0)
                    self.assertEqual(rows[0]["selected_for_publish"], 0)
                    tab.generate_image()
                    self.assertEqual(provider.call_count, 1, "identical generation request must not call provider twice")
                self.assertIn("تصویر تولیدشده با AI", tab.revision_status.text())
                self.assertIsNotNone(tab.preview.pixmap())
            finally:
                db.conn.close()


if __name__ == "__main__":
    unittest.main()
