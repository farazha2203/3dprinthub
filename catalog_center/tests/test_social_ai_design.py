import base64
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.social_ai_design import (
    STORY_STYLES,
    build_product_prompt,
    decode_image_response,
    discover_image_endpoints,
    generate_image_revision,
    generation_request_fingerprint,
    materialize_selected_revision,
    persist_revision,
)


class SocialAIDesignTests(unittest.TestCase):
    def test_image_generation_adapter_uses_reference_and_returns_bytes_without_writing(self):
        calls = []
        raw = b"PNG-GENERATED" * 20

        class Response:
            status = 200
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps({
                    "model": "vendor/image",
                    "data": [{"b64_json": base64.b64encode(raw).decode()}],
                    "usage": {"cost": 0.01},
                }).encode()

        def opener(request, timeout=180):
            calls.append((request, timeout))
            return Response()

        result = generate_image_revision(
            "test-key", "vendor/image", "Keep the exact product geometry", b"PNG-SOURCE" * 20,
            aspect_ratio="9:16", opener=opener,
        )
        payload = json.loads(calls[0][0].data.decode())
        self.assertEqual(result["bytes"], raw)
        self.assertEqual(payload["model"], "vendor/image")
        self.assertEqual(payload["input_references"][0]["type"], "image_url")
        self.assertTrue(payload["input_references"][0]["image_url"]["url"].startswith("data:image/png;base64,"))

    def test_generation_request_fingerprint_is_idempotent_for_same_inputs(self):
        first = generation_request_fingerprint(9, "story", STORY_STYLES[0], "vendor/image", "prompt", b"source")
        second = generation_request_fingerprint(9, "story", STORY_STYLES[0], "vendor/image", "prompt", b"source")
        changed = generation_request_fingerprint(9, "story", STORY_STYLES[1], "vendor/image", "prompt", b"source")
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)

    def test_image_discovery_returns_cost_ordered_reference_capable_endpoints(self):
        class Response:
            def __init__(self, payload):
                self.payload = payload
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                import json
                return json.dumps(self.payload).encode()

        def opener(request, timeout=30):
            url = request.full_url
            if url.endswith("/images/models"):
                return Response({"data": [
                    {"id": "vendor/expensive", "architecture": {"input_modalities": ["text", "image"], "output_modalities": ["image"]}},
                    {"id": "vendor/cheap", "architecture": {"input_modalities": ["text", "image"], "output_modalities": ["image"]}},
                ]})
            if url.endswith("vendor/expensive/endpoints"):
                return Response({"endpoints": [{"provider_slug": "exp", "pricing": [{"cost_usd": 0.10}], "supported_parameters": {"input_references": {}}}]})
            return Response({"endpoints": [{"provider_slug": "cheap", "pricing": [{"cost_usd": 0.01}], "supported_parameters": {"input_references": {}, "aspect_ratio": {}}}]})

        result = discover_image_endpoints("test-key", opener=opener)
        self.assertEqual(result[0]["model"], "vendor/cheap")
        self.assertEqual(result[0]["cost_usd"], 0.01)

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

    def test_sqlite_generation_request_is_idempotently_reusable(self):
        from app.db import Database
        with tempfile.TemporaryDirectory() as temp:
            db = Database(Path(temp) / "catalog.sqlite3")
            try:
                row = db.save_social_ai_revision(
                    9, "story", STORY_STYLES[0].key, "digest-1", b"image-bytes",
                    {"request_fingerprint": "same-request", "ai_generated": True},
                )
                reused = db.social_ai_revision_by_request_fingerprint(9, "story", "same-request")
                missing = db.social_ai_revision_by_request_fingerprint(9, "story", "other-request")
                self.assertEqual(reused["id"], row["id"])
                self.assertIsNone(missing)
            finally:
                db.conn.close()

    def test_approved_selected_revision_is_the_send_handoff_source(self):
        from app.db import Database
        with tempfile.TemporaryDirectory() as temp:
            db = Database(Path(temp) / "catalog.sqlite3")
            try:
                raw = b"PNG-HANDOFF" * 20
                row = db.save_social_ai_revision(
                    9, "story", STORY_STYLES[0].key, "handoff-sha", raw,
                    {"ai_generated": True}, approved=True, selected_for_publish=True,
                )
                selected = materialize_selected_revision(db, 9, "story")
                self.assertEqual(selected["revision_id"], row["id"])
                self.assertEqual(Path(selected["local_path"]).read_bytes(), raw)
            finally:
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
