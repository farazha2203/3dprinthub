from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase

from catalog_bridge.diagnostics import write_import_diagnostic


class Phase49BridgeDiagnosticTests(SimpleTestCase):
    def test_diagnostic_is_written_outside_pending_and_contains_ack(self):
        with TemporaryDirectory() as tmp:
            pending = Path(tmp) / "pending"
            pending.mkdir()
            path = write_import_diagnostic(
                pending,
                "desktop_catalog_v85_20260815_140000",
                batch_uuid="abc",
                status="completed",
                ack={"failed_count": 0, "items": [{"visible_on_store": True}]},
                stdout="ok",
                stderr="",
            )
            self.assertEqual(path.parent.name, "diagnostics")
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["batch_uuid"], "abc")
            self.assertEqual(payload["status"], "completed")
            self.assertTrue(payload["ack"]["items"][0]["visible_on_store"])

    def test_bridge_source_attaches_diagnostic_id(self):
        source = (Path(__file__).resolve().parents[1] / "views.py").read_text(encoding="utf-8")
        self.assertIn('ack["diagnostic_id"] = batch_name', source)
        self.assertIn("write_import_diagnostic", source)

    def test_bridge_url_contract_exposes_authenticated_diagnostic(self):
        urls_source = (Path(__file__).resolve().parents[1] / "urls.py").read_text(encoding="utf-8")
        views_source = (Path(__file__).resolve().parents[1] / "views.py").read_text(encoding="utf-8")
        self.assertIn('diagnostics/<str:batch_name>/', urls_source)
        self.assertIn("def diagnostic_view", views_source)
        self.assertIn("if not _authorized(request)", views_source)
