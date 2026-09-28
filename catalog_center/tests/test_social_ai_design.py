import base64
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.social_ai_design import (
    STORY_STYLES,
    build_product_prompt,
    decode_image_response,
    persist_revision,
)


class SocialAIDesignTests(unittest.TestCase):
    def test_sqlite_revision_round_trip(self):
        from app.db import Database
        with tempfile.TemporaryDirectory() as temp:
            db = Database(Path(temp) / "catalog.sqlite3")
            row = db.save_social_ai_revision(9, "story", STORY_STYLES[0].key, "abc", b"image-bytes", {"published": False})
            self.assertEqual(row["image_blob"], b"image-bytes")
            loaded = db.social_ai_revisions(9, "story")
            self.assertEqual(loaded[0]["image_blob"], b"image-bytes")
            db.update_social_ai_revision_state(row["id"], approved=True, selected_for_publish=True)
            self.assertEqual(db.social_ai_revisions(9, "story")[0]["approved"], 1)
            self.assertEqual(db.social_ai_revisions(9, "story")[0]["selected_for_publish"], 1)
            db.conn.close()

    def test_prompt_does_not_invent_commerce_facts(self):
        prompt = build_product_prompt({"source_title": "Lamp", "source_description": "Orange lamp"}, STORY_STYLES[0])
        self.assertIn("Preserve the exact product geometry", prompt)
        self.assertIn("do not invent accessories, dimensions, price", prompt)
        self.assertIn("Persian typography", prompt)

    def test_decode_mock_image_response(self):
        raw = b"PNG-MOCK" * 20
        decoded = decode_image_response({"data": [{"b64_json": base64.b64encode(raw).decode()}]})
        self.assertEqual(decoded, raw)
        with self.assertRaises(ValueError):
            decode_image_response({"data": [{"b64_json": "not-base64"}]})

    def test_persist_revision_is_immutable_and_reusable(self):
        raw = b"PNG-MOCK" * 20
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict("os.environ", {"CATALOG_DATA_ROOT": temp}, clear=False):
                first = persist_revision(9, "story", STORY_STYLES[0], raw, {"link_mode": "provider_metadata", "mention": "@demo"})
                second = persist_revision(9, "story", STORY_STYLES[0], raw, {"link_mode": "provider_metadata", "mention": "@demo"})
            self.assertEqual(first["path"], second["path"])
            self.assertTrue(Path(first["path"]).is_file())
            self.assertTrue(first["immutable_revision"])
            self.assertFalse(first["published"])
            self.assertEqual(first["mention"], "@demo")


if __name__ == "__main__":
    unittest.main()
