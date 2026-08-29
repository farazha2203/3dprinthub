from __future__ import annotations

import json

from django.test import TestCase, override_settings
from django.urls import reverse

from store.phase39_models import MaterialColorOption
from website.models import Material


TOKEN = "phase49-filament-library-test-token-123456789"
HEADERS = {"HTTP_AUTHORIZATION": f"Bearer {TOKEN}"}


@override_settings(CATALOG_BRIDGE_TOKEN=TOKEN)
class Phase493I41FilamentBridgeTests(TestCase):
    def _post(self, payload):
        return self.client.post(
            reverse("catalog_bridge:filament_sync"),
            data=json.dumps(payload),
            content_type="application/json",
            **HEADERS,
        )

    def test_filament_routes_require_bridge_auth_and_are_registered(self):
        self.assertEqual(reverse("catalog_bridge:filaments"), "/api/catalog-bridge/v1/filaments/")
        self.assertEqual(reverse("catalog_bridge:filament_sync"), "/api/catalog-bridge/v1/filaments/sync/")
        self.assertEqual(self.client.get(reverse("catalog_bridge:filaments")).status_code, 401)

    def test_sync_creates_global_filament_with_weight_stock_rates_and_preheat(self):
        response = self._post({
            "operator": "catalog-center",
            "filament": {
                "material": "PLA",
                "brand": "Bambu Lab",
                "manufacturer": "Bambu Lab",
                "color": "صورتی پاستلی",
                "hex": "#F5D4ED",
                "roll_weight_grams": 1000,
                "stock_roll_count": 2.5,
                "purchase_price_per_roll": 3_600_000,
                "sale_price_per_roll": 4_200_000,
                "usd_price_per_roll": 18,
                "usd_fx_rate_toman": 220_000,
                "print_hourly_rate": 160_000,
                "supervision_hourly_rate": 50_000,
                "preheat_hours": 8,
                "preheat_temperature_c": 45,
                "preheat_hourly_rate": 30_000,
                "filament_image_url": "https://example.com/bambu-pink.webp",
            },
        })
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["created"])
        self.assertEqual(payload["contract"], "phase49-filament-library-v1")

        material = Material.objects.get(name="PLA")
        option = MaterialColorOption.objects.get(
            material=material,
            name="صورتی پاستلی",
            brand_name="Bambu Lab",
        )
        self.assertEqual(str(option.roll_weight_grams), "1000.00")
        self.assertEqual(str(option.stock_roll_count_snapshot), "2.50")
        self.assertEqual(option.sale_price_per_roll, 4_200_000)
        self.assertEqual(option.print_hourly_rate, 160_000)
        self.assertEqual(option.supervision_hourly_rate, 50_000)
        self.assertEqual(str(option.preheat_hours), "8.00")
        self.assertEqual(str(option.preheat_temperature_c), "45.00")
        self.assertEqual(option.preheat_hourly_rate, 30_000)

        listing = self.client.get(
            reverse("catalog_bridge:filaments"),
            {"material": "PLA"},
            **HEADERS,
        )
        self.assertEqual(listing.status_code, 200)
        rows = listing.json()["items"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["brand"], "Bambu Lab")
        self.assertEqual(rows[0]["current_stock_grams"], "2500.0000")

    def test_sync_updates_same_material_brand_color_instead_of_duplicating(self):
        first = self._post({
            "filament": {
                "material": "PETG",
                "brand": "eSUN",
                "manufacturer": "eSUN",
                "color": "شفاف",
                "roll_weight_grams": 1000,
                "stock_roll_count": 1,
                "sale_price_per_roll": 3_000_000,
            },
        })
        self.assertEqual(first.status_code, 200)
        first_id = first.json()["filament"]["id"]

        second = self._post({
            "filament": {
                "material": "PETG",
                "brand": "eSUN",
                "manufacturer": "eSUN",
                "color": "شفاف",
                "roll_weight_grams": 1000,
                "stock_roll_count": 3,
                "sale_price_per_roll": 4_500_000,
                "print_hourly_rate": 170_000,
            },
        })
        self.assertEqual(second.status_code, 200)
        self.assertFalse(second.json()["created"])
        self.assertEqual(second.json()["filament"]["id"], first_id)
        self.assertEqual(
            MaterialColorOption.objects.filter(
                material__name="PETG",
                brand_name="eSUN",
                name="شفاف",
            ).count(),
            1,
        )
        option = MaterialColorOption.objects.get(pk=first_id)
        self.assertEqual(str(option.stock_roll_count_snapshot), "3.00")
        self.assertEqual(option.sale_price_per_roll, 4_500_000)
        self.assertEqual(option.print_hourly_rate, 170_000)


    def test_invalid_color_type_is_normalized_and_inactive_sync_updates_same_row(self):
        created = self._post({
            "filament": {
                "material": "PLA",
                "brand": "Bambu Lab",
                "manufacturer": "Bambu Lab",
                "color": "دو رنگ",
                "color_type": "not-a-real-type",
                "secondary_hex": "#112233",
                "tertiary_hex": "#445566",
                "roll_weight_grams": 1000,
                "stock_roll_count": 1,
                "sale_price_per_roll": 4_000_000,
            },
        })
        self.assertEqual(created.status_code, 200)
        row_id = created.json()["filament"]["id"]
        option = MaterialColorOption.objects.get(pk=row_id)
        self.assertEqual(option.color_type, "solid")
        self.assertEqual(option.secondary_hex, "#112233")
        self.assertEqual(option.tertiary_hex, "#445566")

        disabled = self._post({
            "filament": {
                "material": "PLA",
                "brand": "Bambu Lab",
                "manufacturer": "Bambu Lab",
                "color": "دو رنگ",
                "color_type": "dual",
                "secondary_hex": "#112233",
                "tertiary_hex": "#445566",
                "roll_weight_grams": 1000,
                "stock_roll_count": 1,
                "sale_price_per_roll": 4_000_000,
                "is_active": False,
            },
        })
        self.assertEqual(disabled.status_code, 200)
        self.assertFalse(disabled.json()["created"])
        self.assertEqual(disabled.json()["filament"]["id"], row_id)
        option.refresh_from_db()
        self.assertFalse(option.is_active)
        self.assertEqual(option.color_type, "dual")

        listing = self.client.get(reverse("catalog_bridge:filaments"), **HEADERS)
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.json()["count"], 0)
