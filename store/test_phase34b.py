from __future__ import annotations

import json
from django.test import TestCase

from store.makerworld_next_data import extract_record
from store.models import Category, ImportedPrintAsset, PrintCatalogSource
from store.phase34b_publishing import ensure_persian_draft
from store.phase34b_translation import expand_persian_query


class MakerWorldNextDataTests(TestCase):
    def test_extracts_structured_public_model(self):
        payload = {"props": {"pageProps": {"design": {
            "id": 3098133,
            "modelId": "US101fa1c3a46dc1",
            "title": "Car Gear Holder",
            "summary": "<p>Public description</p>",
            "coverUrl": "https://makerworld.bblmw.com/cover.png",
            "tags": ["car", "gear"],
            "categories": [{"name": "Automotive"}],
            "designCreator": {"name": "Designer"},
            "downloadCount": 10,
            "license": "Standard Digital File License",
            "licenseDescriptionInfo": {"content": "No commercial use"},
            "designExtension": {"design_pictures": [{"name": "cover", "url": "https://makerworld.bblmw.com/cover.png"}]},
            "instances": [],
        }}}}
        html = '<script id="__NEXT_DATA__" type="application/json">' + json.dumps(payload) + '</script>'
        record = extract_record(html, "https://makerworld.com/en/models/3098133")
        self.assertEqual(record["external_id"], "3098133")
        self.assertEqual(record["image_count"], 1)
        self.assertEqual(record["creator"]["name"], "Designer")

    def test_persian_query_expansion(self):
        values = expand_persian_query("چرخ‌دنده خودرو")
        self.assertTrue(any("gear" in value.lower() for value in values))


class ImportedAssetEditorialTests(TestCase):
    def setUp(self):
        category, _ = Category.objects.get_or_create(
            slug="models",
            defaults={
                "name": "Models",
                "section": "general",
                "is_active": True,
            },
        )
        self.source, _ = PrintCatalogSource.objects.update_or_create(
            code="makerworld",
            defaults={
                "name": "MakerWorld",
                "base_url": "https://makerworld.com",
                "adapter_key": "makerworld",
                "default_category": category,
                "is_active": True,
            },
        )

    def test_persian_draft_keeps_source_text(self):
        asset = ImportedPrintAsset.objects.create(
            source=self.source,
            source_url="https://makerworld.com/en/models/1",
            title="Car Gear Holder",
            description="Original English description",
        )
        ensure_persian_draft(asset)
        asset.refresh_from_db()
        self.assertEqual(asset.source_title, "Car Gear Holder")
        self.assertIn("چرخ", asset.persian_title)
        self.assertIn("Original English description", asset.persian_description)

    def test_commercial_guard_requires_price_and_license(self):
        asset = ImportedPrintAsset.objects.create(
            source=self.source,
            source_url="https://makerworld.com/en/models/2",
            title="Model",
            commercial_license_status="review",
            fixed_print_price=0,
        )
        self.assertFalse(asset.can_convert_to_fixed_product)
        asset.commercial_license_status = "allowed"
        asset.fixed_print_price = 100000
        asset.save()
        self.assertTrue(asset.can_convert_to_fixed_product)
