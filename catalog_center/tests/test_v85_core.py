import tempfile
import unittest
from pathlib import Path
from unittest import mock

from app.db import Database
from app.runtime_logging import close_logging, configure_logging, redact
from app.site_connection import SiteConnection


class BlockedProductLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp.name) / "catalog.sqlite3")
        self.db.upsert_product({
            "source_code": "makerworld",
            "external_id": "sample-1",
            "source_url": "https://example.com/model/sample-1",
        })
        self.product_id = self.db.products()[0]["id"]

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_blocked_product_is_excluded_and_cannot_be_reimported(self):
        self.db.block_product(self.product_id, "operator decision")
        self.assertEqual(self.db.products(), [])
        self.assertEqual(len(self.db.products("blocked")), 1)
        returned = self.db.upsert_product({
            "source_code": "makerworld",
            "external_id": "sample-1",
            "source_url": "https://example.com/model/sample-1",
            "source_title": "must not overwrite",
        })
        self.assertEqual(returned, self.product_id)
        self.assertEqual(self.db.product(self.product_id)["source_title"], "")

    def test_restore_returns_product_to_review_without_queueing(self):
        self.db.block_product(self.product_id)
        self.db.restore_product(self.product_id)
        row = self.db.product(self.product_id)
        self.assertEqual(row["is_blocked"], 0)
        self.assertEqual(row["workflow_status"], "review")
        self.assertEqual(row["upload_ready"], 0)


class V85ConnectionContractTests(unittest.TestCase):
    def test_logging_shutdown_releases_the_file_handler(self):
        with tempfile.TemporaryDirectory() as temp:
            logger, log_path = configure_logging(Path(temp))
            handler = logger.handlers[0]
            logger.info("LOG_RELEASE_TEST")
            close_logging(logger)
            self.assertEqual(logger.handlers, [])
            self.assertIsNone(handler.stream)
            renamed = log_path.with_name("catalog-intelligence.closed.log")
            log_path.replace(renamed)
            self.assertTrue(renamed.is_file())

    def test_site_connection_normalizes_remote_root(self):
        cfg = SiteConnection(" ftp.example.com ", 21, "user", "secret", "3dprinthub/", "https://example.com/", "token").normalized()
        self.assertEqual(cfg.ftp_host, "ftp.example.com")
        self.assertEqual(cfg.remote_root, "/3dprinthub")
        self.assertEqual(cfg.site_url, "https://example.com")

    def test_sensitive_values_are_redacted(self):
        text = redact("password=hello token:abc Authorization=BearerSecret Bearer another-secret")
        self.assertNotIn("hello", text)
        self.assertNotIn("abc", text)
        self.assertNotIn("another-secret", text)

    def test_main_has_ftp_https_bridge_and_no_paramiko(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "app" / "main.py").read_text(encoding="utf-8")
        self.assertIn("upload_batch(cfg", text)
        self.assertIn("import_batch(cfg", text)
        self.assertNotIn("paramiko", text.lower())
        self.assertNotIn("ssh_password", text.lower())
        self.assertTrue((root / "RUN_DEBUG.ps1").is_file())

    def test_product_fields_and_blocking_schema_exist(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Database(Path(temp) / "db.sqlite3")
            try:
                columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
                required = {
                    "product_type", "use_description", "dimensions", "materials_json", "colors_json",
                    "availability_status", "stock_quantity", "lead_time_min_days", "lead_time_max_days",
                    "has_3d_file", "source_name", "technical_features_json", "keywords_json",
                    "is_blocked", "blocked_at", "blocked_reason",
                }
                self.assertTrue(required.issubset(columns))
            finally:
                db.close()


if __name__ == "__main__":
    unittest.main()
