from __future__ import annotations

import tempfile
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from store.models import (
    CatalogAssetMetrics,
    CatalogAssetPublication,
    CatalogSourcePolicy,
    ImportedPrintAsset,
    PrintCatalogSource,
)
from store.presentation import categorized_presentation, presentation_assets


def _image(name: str):
    buffer = BytesIO()
    Image.new("RGB", (48, 48), "white").save(buffer, format="JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


class Phase18HistoricalPresentationHelpersTests(TestCase):
    """Keep deterministic helper coverage for historical catalog records.

    The Phase 18 public external catalog list/sort routes were retired by
    Phase 49.2A; only the reusable presentation grouping helpers remain under
    regression coverage until their historical data models are archived.
    """

    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.media_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.media_override.enable()
        self.source = PrintCatalogSource.objects.create(
            name="Printables Phase18",
            code="printables-phase18",
            base_url="https://www.printables.com/",
            allowed_domains="printables.com,www.printables.com",
            adapter_key="printables",
        )
        CatalogSourcePolicy.objects.create(
            source=self.source,
            source_kind="printables",
            discovery_mode="public_html",
            public_display_policy="licensed_only",
        )

    def tearDown(self):
        self.media_override.disable()
        self.media_dir.cleanup()

    def make_asset(self, number: int, *, title_prefix="مدل"):
        asset = ImportedPrintAsset.objects.create(
            source=self.source,
            source_url=f"https://www.printables.com/model/{18000 + number}",
            external_id=str(18000 + number),
            title=f"{title_prefix} {number:02d}",
            short_description="نمونه تاریخی",
            preview_image=_image(f"phase18-{number}.jpg"),
            technical_specs={"source_file_available": True},
            private_download_url=f"https://private.example/{number}.zip",
        )
        metrics = CatalogAssetMetrics.objects.create(
            asset=asset,
            source_kind="printables",
            segment="industrial",
            commercial_use_allowed=True,
            license_review_status="allowed",
            public_approved=True,
            views_count=number * 100,
            downloads_count=number * 10,
            likes_count=number,
            popularity_rank=number,
        )
        CatalogAssetPublication.objects.create(
            metrics=metrics,
            show_on_homepage=True,
            image_alt_text=asset.title,
        )
        return asset

    def test_presentation_helper_respects_limit_fifteen(self):
        for number in range(1, 19):
            self.make_asset(number)
        assets = presentation_assets(limit=15, randomize=False)
        self.assertEqual(len(assets), 15)

    @patch("store.presentation.random.SystemRandom.shuffle")
    def test_grouping_helper_returns_nine_and_randomizes(self, mocked_shuffle):
        for number in range(1, 13):
            self.make_asset(number)
        groups, assets = categorized_presentation(limit=9, randomize=True)
        self.assertTrue(groups)
        self.assertEqual(len(assets), 9)
        mocked_shuffle.assert_called()
