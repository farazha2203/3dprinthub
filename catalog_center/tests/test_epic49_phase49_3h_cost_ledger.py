from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.db import Database
from app import phase49_diagnostics as diagnostics
from app.phase49_3h_cost_ledger import (
    aggregate_product,
    extract_verified_avalai_cost,
    freeze_receipt,
    latest_receipt,
)


class Phase493HCostLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp.name) / "catalog.sqlite3")
        diagnostics.configure(self.db)
        self.db.upsert_product({
            "source_code": "test",
            "external_id": "p-1",
            "source_url": "https://example.test/product/1",
            "source_title": "Test product",
        })
        row = self.db.conn.execute(
            "SELECT id FROM products WHERE source_code=? AND external_id=?",
            ("test", "p-1"),
        ).fetchone()
        self.assertIsNotNone(row)
        self.product_id = int(row["id"])

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_aggregate_known_unknown_and_nonbillable_requests(self):
        diagnostics.ai_request_event(
            provider="avalai", model="gpt-test", operation="list_models",
            endpoint="https://api.example/models", status="ok", product_id=self.product_id,
        )
        diagnostics.ai_request_event(
            provider="avalai", model="gpt-test", operation="structured_content",
            endpoint="https://api.example/chat", request_id="req-known", status="ok",
            usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            cost_usd=0.0125, cost_source="provider_response", product_id=self.product_id,
        )
        diagnostics.ai_request_event(
            provider="avalai", model="gpt-test", operation="structured_content",
            endpoint="https://api.example/chat", request_id="req-unknown", status="ok",
            usage={"prompt_tokens": 200, "completion_tokens": 70, "total_tokens": 270},
            product_id=self.product_id,
        )
        summary = aggregate_product(self.db, self.product_id)
        self.assertEqual(summary["request_count"], 3)
        self.assertEqual(summary["billable_request_count"], 2)
        self.assertEqual(summary["unknown_cost_request_count"], 1)
        self.assertEqual(summary["total_tokens"], 420)
        self.assertAlmostEqual(summary["known_cost_usd"], 0.0125)

    def test_avalai_cost_parser_requires_explicit_currency_semantics(self):
        self.assertEqual(extract_verified_avalai_cost({"amount": 12345}), {})
        self.assertEqual(
            extract_verified_avalai_cost({"amount_irt": 1250}),
            {"cost_irt": 1250.0, "cost_source": "avalai_lookup:amount_irt"},
        )
        self.assertEqual(
            extract_verified_avalai_cost({"amount": {"value": 0.004, "currency": "USD"}}),
            {"cost_usd": 0.004, "cost_source": "avalai_lookup:amount_usd"},
        )

    def test_publish_receipt_freezes_internal_product_cost_snapshot(self):
        diagnostics.ai_request_event(
            provider="openai", model="gpt-test", operation="structured_content",
            endpoint="https://api.example/responses", request_id="req-1", status="ok",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            cost_usd=0.001, cost_source="provider_response", product_id=self.product_id,
        )
        receipt = freeze_receipt(self.db, self.product_id, "local_django")
        self.assertEqual(receipt["product_id"], self.product_id)
        self.assertEqual(receipt["target"], "local_django")
        self.assertEqual(receipt["summary"]["billable_request_count"], 1)
        stored = latest_receipt(self.db, self.product_id)
        self.assertIsNotNone(stored)
        self.assertEqual(stored["target"], "local_django")
        self.assertEqual(stored["summary"]["known_cost_usd"], 0.001)


if __name__ == "__main__":
    unittest.main()
