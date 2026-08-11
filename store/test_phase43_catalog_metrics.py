from __future__ import annotations

from django.test import SimpleTestCase

from store.catalog_site_adapters.makerworld import _makerworld_print_time_minutes
from store.management.commands.phase43_fix_catalog_metrics import (
    extract_raw_print_seconds,
    seconds_to_minutes,
)


class Phase43CatalogMetricsUnitTests(SimpleTestCase):
    def test_seconds_to_minutes_rounds_up(self):
        cases = {
            60: 1,
            61: 2,
            1088: 19,
            3227: 54,
            71102: 1186,
        }
        for seconds, expected in cases.items():
            with self.subTest(seconds=seconds):
                self.assertEqual(seconds_to_minutes(seconds), expected)
                self.assertEqual(_makerworld_print_time_minutes(seconds), expected)

    def test_invalid_values_are_none(self):
        for value in (None, "", 0, -1, "bad"):
            with self.subTest(value=value):
                self.assertIsNone(seconds_to_minutes(value))
                self.assertIsNone(_makerworld_print_time_minutes(value))

    def test_extract_raw_print_seconds(self):
        payload = {
            "instances": [
                {"print_time": 1088, "weight": 10},
                {"printTimeSeconds": 3227},
            ],
            "other": {
                "prediction": 71102,
                "estimated_print_minutes": 999,
            },
        }
        self.assertEqual(
            extract_raw_print_seconds(payload),
            {1088, 3227, 71102},
        )
