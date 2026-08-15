from __future__ import annotations

from unittest.mock import patch

from django.core.exceptions import ObjectDoesNotExist
from django.test import SimpleTestCase

from store.presentation import categorized_presentation


class _AssetWithoutMetrics:
    @property
    def metrics(self):
        raise ObjectDoesNotExist("ImportedPrintAsset has no metrics.")


class Phase48PresentationResilienceTests(SimpleTestCase):
    def test_asset_without_metrics_does_not_break_homepage_grouping(self):
        asset = _AssetWithoutMetrics()
        with patch("store.presentation.presentation_assets", return_value=[asset]):
            groups, flattened = categorized_presentation(limit=9, randomize=False)

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["key"], "other")
        self.assertEqual(groups[0]["count"], 1)
        self.assertEqual(groups[0]["items"], [asset])
        self.assertEqual(flattened, [asset])
