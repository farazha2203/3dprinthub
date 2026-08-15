from pathlib import Path

from django.test import TestCase
from django.urls import resolve


ROOT = Path(__file__).resolve().parents[1]


class Phase48OperationalReleaseTests(TestCase):
    def test_homepage_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_bridge_routes_are_registered(self):
        self.assertEqual(resolve("/api/catalog-bridge/v1/health/").view_name, "catalog_bridge:health")
        self.assertEqual(resolve("/api/catalog-bridge/v1/import/").view_name, "catalog_bridge:import")

    def test_importer_is_v85(self):
        source = (
            ROOT / "store" / "management" / "commands" / "phase37_import_catalog_center.py"
        ).read_text(encoding="utf-8")
        self.assertIn('expected 8.5', source)
        self.assertIn('"schema_version": "8.5"', source)
        self.assertIn("apply_phase43_product_details", source)
