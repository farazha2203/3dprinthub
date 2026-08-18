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
    def test_health_exposes_unified_publish_contract(self):
        response = self.client.get(
            reverse("catalog_bridge:health"),
            HTTP_AUTHORIZATION=f"Bearer {TOKEN}",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(VERSION, "1.3.0")
        self.assertEqual(PUBLISH_CONTRACT, "epic49-unified-v1")
        self.assertEqual(payload["version"], "1.3.0")
        self.assertEqual(payload["schema_version"], "8.5")
        self.assertEqual(payload["publish_contract"], "epic49-unified-v1")

    def test_legacy_import_and_diagnostics_routes_remain_available(self):
        self.assertEqual(reverse("catalog_bridge:health"), "/api/catalog-bridge/v1/health/")
        self.assertEqual(reverse("catalog_bridge:import"), "/api/catalog-bridge/v1/import/")
        self.assertEqual(
            reverse("catalog_bridge:diagnostic", kwargs={"batch_name": "desktop_catalog_v85_20260815_193000"}),
            "/api/catalog-bridge/v1/diagnostics/desktop_catalog_v85_20260815_193000/",
        )

    def test_unified_management_routes_are_registered_without_replacing_import(self):
        self.assertEqual(reverse("catalog_bridge:products"), "/api/catalog-bridge/v1/products/")
        self.assertEqual(reverse("catalog_bridge:product_detail", kwargs={"product_id": 7}), "/api/catalog-bridge/v1/products/7/")
        self.assertEqual(reverse("catalog_bridge:product_sync", kwargs={"product_id": 7}), "/api/catalog-bridge/v1/products/7/sync/")
        self.assertEqual(reverse("catalog_bridge:hero_slides"), "/api/catalog-bridge/v1/hero-slides/")
        self.assertEqual(reverse("catalog_bridge:hero_slide_detail", kwargs={"slide_id": 9}), "/api/catalog-bridge/v1/hero-slides/9/")
        self.assertEqual(reverse("catalog_bridge:hero_slide_sync", kwargs={"slide_id": 9}), "/api/catalog-bridge/v1/hero-slides/9/sync/")

    def test_import_ack_exposes_unified_publish_contract_and_sync_marker(self):
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
            self.assertEqual(payload["publish_contract"], "epic49-unified-v1")
            self.assertEqual(payload["sync_contract"], "epic49-unified-v1")
            self.assertEqual(payload["diagnostic_id"], batch.name)


if __name__ == "__main__":
    import unittest
    unittest.main()
