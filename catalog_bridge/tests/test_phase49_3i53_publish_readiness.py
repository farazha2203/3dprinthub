from __future__ import annotations

import tempfile
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse

from store.models import PrintQuality
from website.models import Material


TOKEN = "phase49-3i53-publish-readiness-token-1234567890"


class Phase493I53PublishReadinessTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pending = self.root / "imports" / "desktop_catalog" / "pending"
        self.media = self.root / "media"
        self.pending.mkdir(parents=True)
        self.media.mkdir(parents=True)
        self.settings_override = override_settings(
            CATALOG_BRIDGE_TOKEN=TOKEN,
            CATALOG_BRIDGE_PENDING_ROOT=self.pending,
            MEDIA_ROOT=self.media,
        )
        self.settings_override.enable()

        Material.objects.create(
            name="PLA readiness",
            price_per_kg=800000,
            main_usage="عمومی",
            sample_parts="تست",
            is_active=True,
        )
        PrintQuality.objects.create(
            code="readiness-standard",
            name="استاندارد readiness",
            is_active=True,
        )

    def tearDown(self):
        self.settings_override.disable()
        self.temp.cleanup()

    def _get(self):
        return self.client.get(
            reverse("catalog_bridge:publish_readiness"),
            HTTP_AUTHORIZATION=f"Bearer {TOKEN}",
        )

    def test_publish_readiness_reports_current_receiver_ready(self):
        response = self._get()
        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertTrue(payload["ready"], payload)
        self.assertEqual(
            payload["contract"],
            "epic49-site-publish-readiness-v1",
        )
        self.assertEqual(payload["blockers"], [])
        self.assertGreater(
            payload["prerequisites"]["active_materials"],
            0,
        )
        self.assertGreater(
            payload["prerequisites"]["active_print_qualities"],
            0,
        )
        migration_map = {
            f"{item['app']}.{item['name']}": item["applied"]
            for item in payload["migrations"]
        }
        self.assertTrue(
            migration_map[
                "store.0042_phase49_3i51_filament_registry_descriptions"
            ]
        )
        self.assertTrue(
            migration_map[
                "website.0024_phase49_3i51_material_catalog_description"
            ]
        )

    def test_no_active_material_blocks_publish_without_mutation(self):
        Material.objects.update(is_active=False)
        response = self._get()
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(payload["ready"])
        self.assertIn("active_materials:none", payload["blockers"])

    def test_endpoint_requires_bridge_token(self):
        response = self.client.get(reverse("catalog_bridge:publish_readiness"))
        self.assertEqual(response.status_code, 401)
