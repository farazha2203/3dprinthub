from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.db import Database
from app.phase49_diagnostics import ai_request_event, audit_event, configure, recent_ai_requests, recent_app_events
from app.phase49_diagnostics_identity import install, session_snapshot


class Phase493BDiagnosticIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = Database(self.root / "catalog.sqlite3")
        configure(self.db)
        self.db.set_setting("operator_name", "کارمند تست")
        self.db.set_setting("ai_usd_to_toman", "100000")
        install(self.db)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_identity_columns_are_populated_for_app_and_ai_rows(self):
        audit_event("product", "update", product_id=17, source_file="product_workspace.py", message="changed title")
        ai_request_event(
            provider="openrouter",
            model="vendor/model",
            operation="structured_content",
            endpoint="https://openrouter.ai/api/v1/chat/completions",
            request_id="req-cost-1",
            http_status=200,
            status="ok",
            usage={"prompt_tokens": 100, "completion_tokens": 40, "total_tokens": 140, "cost": 0.0025},
            cost_usd=0.0025,
            cost_source="provider_response",
            product_id=17,
        )
        app_row = recent_app_events(1)[0]
        ai_row = recent_ai_requests(1)[0]
        self.assertEqual(app_row["operator"], "کارمند تست")
        self.assertTrue(app_row["workstation"])
        self.assertTrue(app_row["session_id"])
        self.assertEqual(ai_row["operator"], "کارمند تست")
        self.assertEqual(ai_row["session_id"], app_row["session_id"])
        self.assertAlmostEqual(float(ai_row["cost_irt"]), 250.0, places=3)
        self.assertIn("usd_to_toman_rate", ai_row["cost_source"])

    def test_session_snapshot_is_shareable_without_secret(self):
        snap = session_snapshot(self.db)
        self.assertEqual(snap["operator"], "کارمند تست")
        self.assertTrue(snap["workstation"])
        self.assertTrue(snap["session_id"])
        self.assertEqual(snap["usd_to_toman"], 100000.0)

    def test_launch_contract_exposes_identity_markers(self):
        launch = (Path(__file__).resolve().parents[1] / "launch.py").read_text(encoding="utf-8")
        self.assertIn("EPIC49_AUDIT_IDENTITY=ENABLED", launch)
        self.assertIn("EPIC49_AI_COST_PERSISTENCE=ENABLED", launch)


if __name__ == "__main__":
    unittest.main()
