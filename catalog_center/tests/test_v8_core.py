from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.db import Database, normalize_url
from app.openai_content import CONTENT_SCHEMA, response_output_text
from app.page_extractor import parse_page_snapshot
from app.v8_features import (
    diff_summary,
    parse_ack_lines,
    product_diff,
    product_fingerprint,
    source_payload_hash,
    merge_refetch,
)


class V8DatabaseTests(unittest.TestCase):
    def test_v8_schema_history_receipts_and_clean_close(self):
        with tempfile.TemporaryDirectory() as td:
            db = Database(Path(td) / "catalog.sqlite3")
            cols = {r["name"] for r in db.conn.execute("PRAGMA table_info(products)")}
            required = {
                "source_categories_json", "categories_fa_json", "specs_fa_json", "tags_fa_json",
                "seo_title_fa", "seo_description_fa", "sales_bullets_json", "social_caption_fa",
                "image_alt_texts_json", "content_pack_json", "fingerprint", "source_hash",
                "last_refetched_at", "server_id", "server_status", "server_ack_json", "last_synced_at",
            }
            self.assertTrue(required.issubset(cols))
            db.upsert_product({
                "source_code": "makerworld", "external_id": "123", "source_url": "https://makerworld.com/en/models/123",
                "source_title": "Thing", "images_json": "[]",
            })
            row = db.conn.execute("SELECT id FROM products").fetchone()
            db.save_history(row["id"], "test", {"a": 1}, {"a": 2}, "unit")
            self.assertEqual(len(db.history(row["id"])), 1)
            db.record_sync_receipt(row["id"], "b1", "updated", "42", {"status": "updated"})
            self.assertEqual(len(db.sync_receipts(row["id"])), 1)
            db.close()


class V8FeatureTests(unittest.TestCase):
    def test_fingerprint_and_source_hash_are_stable(self):
        a = product_fingerprint("makerworld", "123", "https://makerworld.com/en/models/123?utm_source=x")
        b = product_fingerprint("makerworld", "123", "https://makerworld.com/en/models/123")
        self.assertEqual(a, b)
        h1 = source_payload_hash({"source_url": "https://x.test/a", "source_title": "A", "images_json": '["x"]'})
        h2 = source_payload_hash({"images_json": '["x"]', "source_title": "A", "source_url": "https://x.test/a"})
        self.assertEqual(h1, h2)

    def test_ack_parser(self):
        ack = {"batch_uuid": "x", "items": [{"desktop_product_id": 1, "status": "updated", "server_id": 9}]}
        out = "hello\nCATALOG_ACK_JSON=" + json.dumps(ack) + "\nend"
        self.assertEqual(parse_ack_lines(out), ack)

    def test_diff_summary(self):
        old = {"source_title": "A", "images_json": '["1"]'}
        new = {"source_title": "B", "images_json": '["1","2"]'}
        diff = product_diff(old, new)
        self.assertIn("source_title", diff)
        self.assertIn("تصاویر", diff_summary(diff))

    def test_rich_categories_specs_and_network_images(self):
        snapshot = {
            "source_url": "https://example.com/p/1", "final_url": "https://example.com/p/1", "title": "T",
            "metas": {"keywords": "gear, automotive"},
            "json_ld": [json.dumps({"@type": "Product", "name": "Gear", "category": "Automotive", "image": "/hero.jpg"})],
            "breadcrumbs": ["Home", "Automotive", "Interior"],
            "spec_rows": [{"key": "Material", "value": "PA12"}],
            "dom_images": [], "picture_sources": [], "links": [], "body_text": "",
            "network_json": [{"url": "https://example.com/api/p/1", "data": {"gallery": ["https://cdn.example.com/real.webp"]}}],
        }
        page = parse_page_snapshot(snapshot)
        self.assertIn("Automotive", page.source_categories)
        self.assertIn("Interior", page.source_categories)
        self.assertIn("gear", page.tags)
        self.assertEqual(page.specs["Material"], "PA12")
        self.assertIn("https://cdn.example.com/real.webp", [x.url for x in page.images])

    def test_refetch_preserves_operator_owned_local_images(self):
        old = {
            "images_json": json.dumps([
                "local://04.webp",
                "local://05.webp",
                "local://manual_custom_part.png",
                "local://source-page-screenshot-20260918.png",
            ]),
            "selected_images_json": json.dumps([
                "local://04.webp",
                "local://manual_custom_part.png",
            ]),
            "primary_image_url": "local://manual_custom_part.png",
            "source_page_screenshot_path": r"D:\\catalog\\images\\source-page-screenshot-20260918.png",
            "image_metadata_json": json.dumps([{"source_url": "local://manual_custom_part.png"}]),
        }
        fresh = {
            "images_json": json.dumps(["https://cdn.example/new.webp"]),
            "selected_images_json": json.dumps(["https://cdn.example/new.webp"]),
        }
        merged = merge_refetch(old, fresh)
        self.assertEqual(
            json.loads(merged["images_json"]),
            [
                "https://cdn.example/new.webp",
                "local://04.webp",
                "local://manual_custom_part.png",
                "local://source-page-screenshot-20260918.png",
            ],
        )
        self.assertEqual(
            json.loads(merged["selected_images_json"]),
            ["local://04.webp", "local://manual_custom_part.png"],
        )
        self.assertEqual(merged["primary_image_url"], "local://manual_custom_part.png")
        self.assertEqual(merged["image_metadata_json"], old["image_metadata_json"])
        self.assertEqual(
            merged["source_page_screenshot_path"],
            old["source_page_screenshot_path"],
        )

    def test_refetch_replaces_unselected_numbered_source_cache_slots(self):
        old = {
            "images_json": json.dumps(["local://04.webp", "local://05.webp"]),
            "selected_images_json": json.dumps([]),
            "primary_image_url": "local://04.webp",
        }
        fresh = {
            "images_json": json.dumps(["https://cdn.example/current.webp"]),
            "selected_images_json": json.dumps(["https://cdn.example/current.webp"]),
        }
        merged = merge_refetch(old, fresh)
        self.assertEqual(json.loads(merged["images_json"]), ["https://cdn.example/current.webp"])
        self.assertEqual(json.loads(merged["selected_images_json"]), ["https://cdn.example/current.webp"])
        self.assertEqual(merged["primary_image_url"], "https://cdn.example/current.webp")

    def test_openai_schema_and_output_parser(self):
        required = set(CONTENT_SCHEMA["required"])
        self.assertIn("seo_title_fa", required)
        data = {"output": [{"content": [{"type": "output_text", "text": '{"ok":true}'}]}]}
        self.assertEqual(response_output_text(data), '{"ok":true}')


if __name__ == "__main__":
    unittest.main(verbosity=2)
