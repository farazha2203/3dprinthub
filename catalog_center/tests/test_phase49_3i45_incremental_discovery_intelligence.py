from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from app.db import Database
from app.phase49_3i45_incremental_discovery_intelligence import (
    OBSERVATION_TABLE,
    discover_sitemap_candidates_incremental,
    ensure_schema,
    observation_summary,
    parse_sitemap_document,
    record_discovery_observation,
)


class _FakeClient:
    def __init__(self, db, documents: dict[str, str]):
        self.db = db
        self.source_code = "test"
        self.documents = documents
        self.calls: list[str] = []

    async def fetch_text(self, url: str, **_kwargs):
        self.calls.append(url)
        if url not in self.documents:
            raise RuntimeError(f"missing fake document: {url}")
        return SimpleNamespace(text=self.documents[url], final_url=url)


class Phase493I45IncrementalDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp.name) / "catalog.sqlite3")
        ensure_schema(self.db)
        self.db.upsert_source({
            "code": "test",
            "name": "Test",
            "enabled": 1,
            "methods": [],
            "listing_urls": [],
            "model_url_pattern": "",
            "requires_login": False,
            "reference_only": False,
        })

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_schema_is_additive_and_keeps_discovery_metadata_only(self):
        columns = {
            row["name"]
            for row in self.db.conn.execute(f"PRAGMA table_info({OBSERVATION_TABLE})")
        }
        self.assertTrue({
            "source_code",
            "normalized_url",
            "source_url",
            "discovered_from",
            "sitemap_url",
            "sitemap_lastmod",
            "sitemap_changefreq",
            "sitemap_priority",
            "first_seen_at",
            "last_seen_at",
            "seen_count",
        }.issubset(columns))
        self.assertNotIn("body", columns)
        self.assertNotIn("html", columns)
        self.assertNotIn("payload", columns)

    def test_direct_child_parser_ignores_nested_image_loc_and_reads_metadata(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
          <url>
            <loc>https://example.test/models/101-alpha</loc>
            <lastmod>2026-08-30T10:30:00+00:00</lastmod>
            <changefreq>daily</changefreq>
            <priority>0.8</priority>
            <image:image>
              <image:loc>https://example.test/models/999-image-must-not-count</image:loc>
            </image:image>
          </url>
        </urlset>"""
        kind, entries = parse_sitemap_document(xml)
        self.assertEqual(kind, "urlset")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].loc, "https://example.test/models/101-alpha")
        self.assertEqual(entries[0].lastmod, "2026-08-30T10:30:00+00:00")
        self.assertEqual(entries[0].changefreq, "daily")
        self.assertEqual(entries[0].priority, 0.8)

    def test_observation_upsert_preserves_first_seen_and_increments_seen_count(self):
        first = record_discovery_observation(
            self.db,
            source_code="test",
            url="https://example.test/models/101-alpha",
            discovered_from="https://example.test/sitemap.xml",
            sitemap_url="https://example.test/sitemap.xml",
            lastmod="2026-08-29",
            changefreq="weekly",
            priority=0.7,
        )
        second = record_discovery_observation(
            self.db,
            source_code="test",
            url="https://example.test/models/101-alpha",
            discovered_from="https://example.test/sitemap.xml",
            sitemap_url="https://example.test/sitemap.xml",
            lastmod="2026-08-30",
            changefreq="daily",
            priority=0.9,
        )
        self.assertTrue(first)
        self.assertFalse(second)
        row = self.db.conn.execute(
            f"SELECT * FROM {OBSERVATION_TABLE} WHERE source_code='test'"
        ).fetchone()
        self.assertEqual(int(row["seen_count"]), 2)
        self.assertEqual(row["sitemap_lastmod"], "2026-08-30")
        self.assertEqual(row["sitemap_changefreq"], "daily")
        self.assertEqual(float(row["sitemap_priority"]), 0.9)
        self.assertLessEqual(row["first_seen_at"], row["last_seen_at"])

    def test_sitemap_index_prioritizes_newest_child_with_bounded_document_budget(self):
        root = "https://example.test/sitemap-index.xml"
        older = "https://example.test/sitemap-old.xml"
        newer = "https://example.test/sitemap-new.xml"
        documents = {
            root: f"""<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                <sitemap><loc>{older}</loc><lastmod>2026-01-01</lastmod></sitemap>
                <sitemap><loc>{newer}</loc><lastmod>2026-08-30</lastmod></sitemap>
            </sitemapindex>""",
            older: """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                <url><loc>https://example.test/models/101-old</loc><lastmod>2026-01-01</lastmod></url>
            </urlset>""",
            newer: """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                <url><loc>https://example.test/models/202-new</loc><lastmod>2026-08-30</lastmod></url>
            </urlset>""",
        }
        client = _FakeClient(self.db, documents)
        rows = asyncio.run(
            discover_sitemap_candidates_incremental(
                client,
                [root],
                source_code="test",
                model_pattern=r"https?://example\.test/models/(?P<external_id>\d+)[^\s\"'<>]*",
                requested=10,
                max_documents=2,
            )
        )
        self.assertEqual([row["external_id"] for row in rows], ["202"])
        self.assertEqual(client.calls, [root, newer])

    def test_unseen_product_is_ranked_before_known_even_if_known_is_newer(self):
        sitemap = "https://example.test/sitemap.xml"
        documents = {
            sitemap: """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                <url>
                  <loc>https://example.test/models/200-known</loc>
                  <lastmod>2026-08-30</lastmod>
                  <priority>1.0</priority>
                </url>
                <url>
                  <loc>https://example.test/models/100-unseen</loc>
                  <lastmod>2026-07-01</lastmod>
                  <priority>0.5</priority>
                </url>
            </urlset>"""
        }
        self.db.upsert_product({
            "source_code": "test",
            "external_id": "200",
            "source_url": "https://example.test/models/200-known",
            "source_title": "Known",
        })

        client = _FakeClient(self.db, documents)
        rows = asyncio.run(
            discover_sitemap_candidates_incremental(
                client,
                [sitemap],
                source_code="test",
                model_pattern=r"https?://example\.test/models/(?P<external_id>\d+)[^\s\"'<>]*",
                requested=2,
            )
        )
        self.assertEqual([row["external_id"] for row in rows], ["100", "200"])
        stats = observation_summary(self.db, "test")
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["with_lastmod"], 2)

    def test_custom_source_without_regex_uses_bounded_model_path_heuristic(self):
        sitemap = "https://example.test/sitemap.xml"
        documents = {
            sitemap: """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                <url><loc>https://example.test/blog/post-1</loc></url>
                <url><loc>https://example.test/3d-model/gearbox-cover</loc></url>
                <url><loc>https://example.test/products/not-a-model</loc></url>
            </urlset>"""
        }
        rows = asyncio.run(
            discover_sitemap_candidates_incremental(
                _FakeClient(self.db, documents),
                [sitemap],
                source_code="test",
                model_pattern="",
                requested=10,
            )
        )
        self.assertEqual(len(rows), 1)
        self.assertIn("/3d-model/gearbox-cover", rows[0]["source_url"])
        self.assertTrue(rows[0]["external_id"])


if __name__ == "__main__":
    unittest.main()
