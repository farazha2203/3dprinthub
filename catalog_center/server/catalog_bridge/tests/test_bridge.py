import json
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase, override_settings
from django.urls import reverse


TOKEN = "test-token-with-at-least-24-characters"


@override_settings(CATALOG_BRIDGE_TOKEN=TOKEN)
class CatalogBridgeSecurityTests(SimpleTestCase):
    def test_health_requires_bearer_token(self):
        response = self.client.get(reverse("catalog_bridge:health"))
        self.assertEqual(response.status_code, 401)

    def test_health_accepts_configured_token(self):
        response = self.client.get(reverse("catalog_bridge:health"), HTTP_AUTHORIZATION=f"Bearer {TOKEN}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["schema_version"], "8.5")

    def test_import_rejects_path_traversal(self):
        response = self.client.post(
            reverse("catalog_bridge:import"),
            data=json.dumps({"batch_name": "../escape", "batch_uuid": "x", "schema_version": "8.5"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {TOKEN}",
        )
        self.assertEqual(response.status_code, 400)

    def test_import_returns_structured_ack(self):
        with tempfile.TemporaryDirectory() as temp:
            pending = Path(temp)
            batch = pending / "desktop_catalog_v85_20260810_120000"
            batch.mkdir()
            (batch / "batch_manifest.json").write_text(
                json.dumps({"schema_version": "8.5", "batch_uuid": "uuid-1", "models": []}), encoding="utf-8"
            )
            ack = {"schema_version": "8.5", "batch_uuid": "uuid-1", "failed_count": 0, "items": []}
            with override_settings(CATALOG_BRIDGE_PENDING_ROOT=pending), mock.patch(
                "catalog_bridge.views.call_command",
                side_effect=lambda *a, **kw: kw["stdout"].write("CATALOG_ACK_JSON=" + json.dumps(ack) + "\n"),
            ):
                response = self.client.post(
                    reverse("catalog_bridge:import"),
                    data=json.dumps({"batch_name": batch.name, "batch_uuid": "uuid-1", "schema_version": "8.5"}),
                    content_type="application/json",
                    HTTP_AUTHORIZATION=f"Bearer {TOKEN}",
                )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["bridge_status"], "completed")
