from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.db import Database
from app import phase49_diagnostics as diagnostics
from app.phase49_3h_seo_execution import (
    _persist_result,
    format_result,
    get_result,
)


class Phase493HSEOExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp.name) / "catalog.sqlite3")
        diagnostics.configure(self.db)
        self.db.upsert_product({
            "source_code": "test",
            "external_id": "seo-1",
            "source_url": "https://example.test/product/seo-1",
            "source_title": "SEO Test",
            "title_fa": "محصول تست",
        })
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("test", "seo-1"),
        ).fetchone()
        self.assertIsNotNone(row)
        self.product_id = int(row["id"])

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_persistent_result_contains_steps_cost_and_changed_fields(self):
        before = {"title_fa": "محصول تست", "seo_title_fa": ""}
        diagnostics.ai_request_event(
            provider="openai", model="gpt-test", operation="structured_content",
            endpoint="https://api.example/responses", request_id="request-49h", status="ok",
            usage={"prompt_tokens": 40, "completion_tokens": 20, "total_tokens": 60},
            cost_usd=0.002, cost_source="provider_response", product_id=self.product_id,
        )
        self.db.update_product(self.product_id, {"seo_title_fa": "عنوان سئو تست فارسی"})
        context = {
            "product_id": self.product_id,
            "action_key": "product_ai",
            "scope": "content",
            "provider": "openai",
            "model": "gpt-test",
            "elapsed_ms": 321,
            "request_from_id": 0,
            "before": before,
            "steps": [
                {"at_ms": 10, "label": "اتصال", "detail": "موفق"},
                {"at_ms": 200, "label": "دریافت پاسخ", "detail": "JSON"},
            ],
        }
        result_id = _persist_result(
            self.db, context, status="success", label="انجام شد", detail="ثبت شد"
        )
        result = get_result(self.db, result_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["cost"]["total_tokens"], 60)
        self.assertIn("seo_title_fa", result["result"]["changed_fields"])
        rendered = format_result(result)
        self.assertIn("request-49h", rendered)
        self.assertIn("مراحل اجرا", rendered)

    def test_error_text_is_redacted_before_persistence_and_display(self):
        context = {
            "product_id": self.product_id,
            "action_key": "image_seo",
            "scope": "images",
            "provider": "avalai",
            "model": "gpt-test",
            "elapsed_ms": 100,
            "request_from_id": 0,
            "before": {},
            "steps": [{"at_ms": 50, "label": "ارسال", "detail": "failed"}],
        }
        secret = "very-secret-token-123"
        result_id = _persist_result(
            self.db,
            context,
            status="error",
            label="خطا",
            detail="اتصال ناموفق",
            error_text=f"Authorization: Bearer {secret}",
        )
        result = get_result(self.db, result_id)
        rendered = format_result(result)
        self.assertNotIn(secret, result["error_text"])
        self.assertNotIn(secret, rendered)
        self.assertIn("Bearer ***", rendered)

    def test_source_contract_has_result_drawer_and_error_keeps_progress_open(self):
        source = (Path(__file__).resolve().parents[1] / "app" / "phase49_3h_seo_execution.py").read_text(encoding="utf-8")
        self.assertIn("نتیجه / لاگ آخرین عملیات SEO و AI", source)
        self.assertIn("Error progress intentionally remains open", source)
        self.assertIn("باز کردن فولدر لاگ", source)
        self.assertIn("تلاش مجدد", source)
        self.assertIn("pre_publish_snapshot", source)


if __name__ == "__main__":
    unittest.main()
