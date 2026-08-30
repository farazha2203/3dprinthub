from __future__ import annotations

import asyncio
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from app.db import Database
from app.phase49_3i43_modern_acquisition_intelligence import (
    ModernHttpClient,
    RateLimitedError,
    RobotsDeniedError,
    acquisition_quality,
    build_provenance,
    discover_conditional_http,
    discover_sitemap_candidates,
    ensure_schema,
    record_endpoint_hints,
    robots_policy,
    sanitize_endpoint_url,
)


class _Handler(BaseHTTPRequestHandler):
    search_requests = 0

    def log_message(self, _format, *_args):
        return

    def do_GET(self):
        if self.path == "/robots.txt":
            body = (
                "User-agent: *\n"
                "Allow: /search\n"
                "Disallow: /private\n"
                "Crawl-delay: 1\n"
                f"Sitemap: http://127.0.0.1:{self.server.server_port}/sitemap.xml\n"
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/search":
            type(self).search_requests += 1
            if self.headers.get("If-None-Match") == '"search-v1"':
                self.send_response(304)
                self.send_header("ETag", '"search-v1"')
                self.end_headers()
                return
            base = f"http://127.0.0.1:{self.server.server_port}"
            body = (
                "<html><body>"
                f'<a href="{base}/models/101-alpha">A</a>'
                f'<a href="{base}/models/202-beta">B</a>'
                "</body></html>"
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("ETag", '"search-v1"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/sitemap.xml":
            base = f"http://127.0.0.1:{self.server.server_port}"
            body = (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                f'<url><loc>{base}/models/303-gamma</loc></url>'
                f'<url><loc>{base}/models/404-delta</loc></url>'
                '</urlset>'
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/xml")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/rate":
            self.send_response(429)
            self.send_header("Retry-After", "120")
            self.end_headers()
            return

        self.send_response(404)
        self.end_headers()


class Phase493I43ModernAcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

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

    def test_schema_adds_cache_telemetry_provenance_and_performance_indexes(self):
        tables = {
            row["name"]
            for row in self.db.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        self.assertTrue({
            "acquisition_http_cache",
            "acquisition_attempts",
            "source_endpoint_hints",
            "source_capabilities",
        }.issubset(tables))

        product_columns = {
            row["name"] for row in self.db.conn.execute("PRAGMA table_info(products)")
        }
        self.assertTrue({
            "source_provenance_json",
            "acquisition_method",
            "acquisition_quality",
            "source_last_http_status",
            "source_last_fetch_ms",
        }.issubset(product_columns))

        indexes = {
            row["name"]
            for row in self.db.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            )
        }
        self.assertIn("ix_discovered_source_status_updated", indexes)
        self.assertIn("ix_products_work_state", indexes)
        busy_timeout = self.db.conn.execute("PRAGMA busy_timeout").fetchone()[0]
        self.assertGreaterEqual(int(busy_timeout), 5000)

    def test_conditional_get_reuses_cached_body_after_304(self):
        async def run():
            async with ModernHttpClient(self.db, "test") as client:
                first = await client.fetch_text(self.base + "/search")
                second = await client.fetch_text(self.base + "/search")
            return first, second

        first, second = asyncio.run(run())
        self.assertEqual(first.status_code, 200)
        self.assertFalse(first.cache_hit)
        self.assertIn("/models/101-alpha", first.text)
        self.assertTrue(second.cache_hit)
        self.assertEqual(second.text, first.text)
        attempts = list(
            self.db.conn.execute(
                "SELECT status_code,cache_hit,outcome FROM acquisition_attempts "
                "WHERE normalized_url LIKE '%/search' ORDER BY id"
            )
        )
        self.assertEqual(attempts[-1]["status_code"], 304)
        self.assertEqual(attempts[-1]["cache_hit"], 1)
        self.assertEqual(attempts[-1]["outcome"], "not_modified_cache_hit")

    def test_robots_policy_allows_search_denies_private_and_exposes_sitemap(self):
        async def run():
            async with ModernHttpClient(self.db, "test") as client:
                allowed = await robots_policy(client, self.base + "/search")
                denied = await robots_policy(client, self.base + "/private")
            return allowed, denied

        allowed, denied = asyncio.run(run())
        self.assertTrue(allowed.known)
        self.assertTrue(allowed.allowed)
        self.assertFalse(denied.allowed)
        self.assertEqual(allowed.crawl_delay, 1.0)
        self.assertTrue(any("sitemap.xml" in item for item in allowed.sitemaps))

        row = self.db.conn.execute(
            "SELECT * FROM source_capabilities WHERE source_code='test'"
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertIn(row["robots_status"], {"allowed", "denied"})

    def test_discovery_uses_fast_public_http_and_honors_robots_gate(self):
        pattern = (
            self.base.replace(".", r"\.")
            + r"/models/(?P<external_id>\d+)[^\s\"'<>]*"
        )

        async def run_allowed():
            async with ModernHttpClient(self.db, "test") as client:
                return await discover_conditional_http(
                    client,
                    self.base + "/search",
                    source_code="test",
                    model_pattern=pattern,
                    requested=10,
                )

        rows = asyncio.run(run_allowed())
        self.assertEqual([row["external_id"] for row in rows], ["101", "202"])

        async def run_denied():
            async with ModernHttpClient(self.db, "test") as client:
                return await discover_conditional_http(
                    client,
                    self.base + "/private",
                    source_code="test",
                    model_pattern=pattern,
                    requested=10,
                )

        with self.assertRaises(RobotsDeniedError):
            asyncio.run(run_denied())

    def test_sitemap_intelligence_extracts_product_urls_without_browser(self):
        pattern = (
            self.base.replace(".", r"\.")
            + r"/models/(?P<external_id>\d+)[^\s\"'<>]*"
        )

        async def run():
            async with ModernHttpClient(self.db, "test") as client:
                return await discover_sitemap_candidates(
                    client,
                    [self.base + "/sitemap.xml"],
                    source_code="test",
                    model_pattern=pattern,
                    requested=10,
                )

        rows = asyncio.run(run())
        self.assertEqual([row["external_id"] for row in rows], ["303", "404"])
        attempts = list(
            self.db.conn.execute(
                "SELECT method,outcome FROM acquisition_attempts WHERE method='sitemap'"
            )
        )
        self.assertTrue(attempts)
        self.assertEqual(attempts[-1]["outcome"], "success")

    def test_retry_after_sets_source_cooldown_and_does_not_silently_retry(self):
        async def run():
            async with ModernHttpClient(self.db, "test") as client:
                return await client.fetch_text(self.base + "/rate")

        with self.assertRaises(RateLimitedError) as raised:
            asyncio.run(run())
        self.assertEqual(raised.exception.retry_after_seconds, 120)
        source = self.db.source("test")
        self.assertGreater(int(source["cooldown_until"] or 0), 0)
        self.assertIn("429", source["last_error"])

    def test_endpoint_provenance_redacts_credentials_and_keeps_same_site_json(self):
        raw = self.base + "/api/models?token=SUPERSECRET&page=2"
        snapshot = {
            "network_json": [
                {
                    "url": raw,
                    "status": 200,
                    "method": "GET",
                    "resource_type": "xhr",
                    "content_type": "application/json",
                    "data": {"ok": True},
                },
                {
                    "url": "https://analytics.example.net/event?token=NOPE",
                    "status": 200,
                    "method": "POST",
                    "resource_type": "fetch",
                    "content_type": "application/json",
                    "data": {"ok": True},
                },
            ]
        }
        hints = record_endpoint_hints(self.db, "test", self.base + "/models/101", snapshot)
        self.assertEqual(len(hints), 1)
        self.assertNotIn("SUPERSECRET", hints[0]["url"])
        query = parse_qs(urlsplit(hints[0]["url"]).query)
        self.assertEqual(query["token"], ["<redacted>"])
        self.assertEqual(query["page"], ["2"])

        stored = self.db.conn.execute(
            "SELECT endpoint_url FROM source_endpoint_hints WHERE source_code='test'"
        ).fetchone()["endpoint_url"]
        self.assertNotIn("SUPERSECRET", stored)

    def test_quality_and_provenance_are_bounded_and_exclude_raw_network_payloads(self):
        result = {
            "source_url": self.base + "/models/101",
            "source_title": "Strong Product",
            "source_description": "A" * 100,
            "images_json": json.dumps(["https://cdn.example/model.jpg"]),
            "source_specs_json": json.dumps({"material": "PLA"}),
            "author_name": "Designer",
            "license_name": "CC BY",
            "source_like_count": 25,
            "source_snapshot_json": json.dumps({
                "json_ld": ["{}"],
                "embedded_json": ["{}"],
                "network_json": [{"data": {"private_large_payload": "X" * 5000}}],
                "breadcrumbs": ["Models"],
                "spec_rows": [{"key": "material", "value": "PLA"}],
            }),
        }
        score = acquisition_quality(result)
        self.assertEqual(score, 100.0)
        provenance = build_provenance(result, [])
        encoded = json.dumps(provenance)
        self.assertNotIn("private_large_payload", encoded)
        self.assertTrue(provenance["policy"]["public_data_only"])
        self.assertFalse(provenance["policy"]["captcha_bypass"])


if __name__ == "__main__":
    unittest.main()
