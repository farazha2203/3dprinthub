from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.db import Database
from app.epic49_desktop_schema import ensure_epic49_desktop_schema
from app.phase49_3i_discovery_review import (
    archive_candidate,
    candidate_row,
    candidates_from_dom_rows,
    ensure_schema,
    resolve_discovery_targets,
    sanitize_source_payload,
    sanitize_source_text,
    upsert_candidate,
)


MAKERWORLD_PATTERN = r"https?://(?:www\.)?makerworld\.com/(?:[a-z]{2}/)?models/(?P<external_id>\d+)[^\s\"'<>]*"
SEARCH_URL = "https://makerworld.com/en/search/models?keyword=cake+stand"
MODEL_A = "https://makerworld.com/en/models/2834255-cake-stand-small-table-great-for-cakes-cupcakes?from=search#profileId-3158565"
MODEL_B = "https://makerworld.com/en/models/2845731-cake-stand?from=search#profileId-3173184"


class Phase493IDiscoveryPureTests(unittest.TestCase):
    def test_explicit_search_seed_is_authoritative(self):
        targets, max_pages = resolve_discovery_targets(
            "search",
            SEARCH_URL,
            ["https://makerworld.com/en/3d-models?orderBy=downloadCount&page={page}"],
            "cake+stand",
        )
        self.assertEqual(targets, [SEARCH_URL])
        self.assertEqual(max_pages, 1)

    def test_makerworld_candidate_cards_keep_expected_models_and_dedupe_identity(self):
        rows = [
            {"href": MODEL_A, "text": "Cake Stand Small Table\nBy designer", "image": "https://img.test/a.jpg"},
            {"href": MODEL_A.replace("#profileId-3158565", "#other"), "text": "duplicate", "image": "https://img.test/a2.jpg"},
            {"href": MODEL_B, "text": "Cake Stand", "image": "https://img.test/b.jpg"},
            {"href": "https://makerworld.com/en/models/not-a-number", "text": "bad", "image": ""},
        ]
        result = candidates_from_dom_rows(rows, MAKERWORLD_PATTERN, SEARCH_URL, "makerworld", 20)
        self.assertEqual([row["external_id"] for row in result], ["2834255", "2845731"])
        self.assertEqual(result[0]["thumbnail_url"], "https://img.test/a.jpg")
        self.assertEqual(result[1]["source_title"], "Cake Stand")

    def test_source_text_sanitizer_removes_unexpected_scripts_and_emoji(self):
        cleaned = sanitize_source_text("Cake Stand 蛋糕架 Привет 🐶 25mm – PLA")
        self.assertIn("Cake Stand", cleaned)
        self.assertIn("25mm", cleaned)
        self.assertIn("PLA", cleaned)
        self.assertNotIn("蛋", cleaned)
        self.assertNotIn("Привет", cleaned)
        self.assertNotIn("🐶", cleaned)

    def test_source_payload_sanitizes_source_json_but_preserves_urls_and_persian_editorial(self):
        source_url = MODEL_A
        payload = sanitize_source_payload({
            "source_title": "Cake Stand 蛋糕架 🧁",
            "source_url": source_url,
            "title_fa": "استند کیک کوچک",
            "tags_json": json.dumps(["cake", "蛋糕", "🧁", "stand"]),
            "source_specs_json": json.dumps({"note": "PLA 材料", "manual_url": "https://example.test/说明"}),
            "source_snapshot_json": json.dumps({"title": "Cake 蛋糕", "url": source_url}),
        })
        self.assertEqual(payload["source_url"], source_url)
        self.assertEqual(payload["title_fa"], "استند کیک کوچک")
        self.assertNotIn("蛋", payload["source_title"])
        self.assertNotIn("🧁", payload["tags_json"])
        specs = json.loads(payload["source_specs_json"])
        self.assertEqual(specs["manual_url"], "https://example.test/说明")
        self.assertEqual(specs["note"], "PLA")

    def test_preview_module_has_no_full_extractor_call(self):
        source = (Path(__file__).resolve().parents[1] / "app" / "phase49_3i_discovery_review.py").read_text(encoding="utf-8")
        start = source.index("async def discover_preview_candidates")
        end = source.index("def _source_defaults", start)
        preview_method = source[start:end]
        self.assertNotIn("extract_direct_link", preview_method)
        self.assertNotIn("collect_classic_exact", preview_method)


class Phase493IDiscoveryDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp.name) / "catalog.sqlite3")
        ensure_epic49_desktop_schema(self.db)
        ensure_schema(self.db)

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def _candidate(self):
        candidate_id = upsert_candidate(self.db, {
            "source_code": "makerworld",
            "external_id": "2834255",
            "source_url": MODEL_A,
            "source_title": "Cake Stand Small Table",
            "thumbnail_url": "https://img.test/cake.jpg",
            "discovered_from": SEARCH_URL,
        })
        return candidate_id

    def test_archive_blocks_identity_without_full_product_payload(self):
        candidate_id = self._candidate()
        product_id = archive_candidate(self.db, candidate_id)
        self.assertIsNotNone(product_id)
        product = self.db.product(product_id)
        self.assertEqual(product["is_blocked"], 1)
        self.assertEqual(product["workflow_status"], "blocked")
        self.assertEqual(candidate_row(self.db, candidate_id)["status"], "blocked")
        # Existing Database discovery guard must reject the same blocked identity.
        added = self.db.add_discovered("makerworld", "2834255", MODEL_A, SEARCH_URL)
        self.assertFalse(added)

    def test_existing_product_marks_candidate_existing_and_prevents_duplicate_review_reset(self):
        self.db.upsert_product({
            "source_code": "makerworld",
            "external_id": "2834255",
            "source_url": MODEL_A,
            "source_title": "Existing Cake Stand",
        })
        candidate_id = self._candidate()
        row = candidate_row(self.db, candidate_id)
        self.assertEqual(row["status"], "existing")
        product_count = self.db.conn.execute(
            "SELECT COUNT(*) total FROM products WHERE source_code='makerworld' AND external_id='2834255'"
        ).fetchone()["total"]
        self.assertEqual(product_count, 1)


if __name__ == "__main__":
    unittest.main()
