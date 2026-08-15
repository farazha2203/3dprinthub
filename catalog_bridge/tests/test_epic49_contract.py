import json
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from catalog_bridge.views import PUBLISH_CONTRACT, VERSION


TOKEN = "epic49-test-token-with-at-least-24-characters"


@override_settings(CATALOG_BRIDGE_TOKEN=TOKEN)
class Epic49BridgeContractTests(SimpleTestCase):
    def test_health_exposes_final_publish_contract(self):
        response = self.client.get(
            reverse("catalog_bridge:health"),
            HTTP_AUTHORIZATION=f"Bearer {TOKEN}",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(VERSION, "1.2.0")
        self.assertEqual(PUBLISH_CONTRACT, "epic49-final")
        self.assertEqual(payload["version"], "1.2.0")
        self.assertEqual(payload["schema_version"], "8.5")
        self.assertEqual(payload["publish_contract"], "epic49-final")

    def test_import_ack_exposes_final_publish_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            pending = Path(temp)
            batch = pending / "desktop_catalog_v85_20260815_193000"
            batch.mkdir()
            (batch / "batch_manifest.json").write_text(
                json.dumps({
                    "schema_version": "8.5",
                    "batch_uuid": "epic49-uuid",
                    "batch_name": batch.name,
                    "models": [],
                }),
                encoding="utf-8",
            )
            ack = {
                "schema_version": "8.5",
                "batch_uuid": "epic49-uuid",
                "failed_count": 0,
                "items": [],
            }
            with override_settings(CATALOG_BRIDGE_PENDING_ROOT=pending), mock.patch(
                "catalog_bridge.views.call_command",
                side_effect=lambda *a, **kw: kw["stdout"].write(
                    "CATALOG_ACK_JSON=" + json.dumps(ack) + "\n"
                ),
            ):
                response = self.client.post(
                    reverse("catalog_bridge:import"),
                    data=json.dumps({
                        "batch_name": batch.name,
                        "batch_uuid": "epic49-uuid",
                        "schema_version": "8.5",
                    }),
                    content_type="application/json",
                    HTTP_AUTHORIZATION=f"Bearer {TOKEN}",
                )
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["bridge_status"], "completed")
            self.assertEqual(payload["publish_contract"], "epic49-final")
            self.assertEqual(payload["diagnostic_id"], batch.name)


if __name__ == "__main__":
    import unittest
    unittest.main()
