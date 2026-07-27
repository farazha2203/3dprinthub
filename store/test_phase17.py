import base64
import tempfile
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from store.catalog_preview import extract_print_profiles, refresh_asset_metadata
from store.models import (
    CatalogSourcePolicy,
    ImportedPrintAsset,
    ImportedPrintAssetPrintProfile,
    PrintCatalogSource,
)


PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class _FakeClient:
    def fetch_bytes(self, url):
        return PNG_BYTES, "image/png"


class _FakeAdapter:
    def __init__(self, payload):
        self.payload = payload
        self.client = _FakeClient()

    def fetch_record(self, candidate, hydrate_files=False):
        return self.payload


class Phase17CatalogPreviewTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.override.enable()

        self.source = PrintCatalogSource.objects.create(
            name="Printables",
            code="printables-phase17",
            base_url="https://www.printables.com/",
            allowed_domains="printables.com, www.printables.com, example.com",
            adapter_key="custom",
            download_preview_images=True,
            store_private_download_url=True,
        )
        self.policy = CatalogSourcePolicy.objects.create(
            source=self.source,
            source_kind="printables",
            discovery_mode="public_html",
            public_display_policy="licensed_only",
            store_download_links=True,
        )
        self.asset = ImportedPrintAsset.objects.create(
            source=self.source,
            source_url="https://www.printables.com/model/17-preview",
            external_id="17",
            title="مدل اولیه",
            short_description="توضیح قدیمی",
        )

    def tearDown(self):
        self.override.disable()
        self.media_dir.cleanup()

    def payload(self):
        return {
            "source_url": self.asset.source_url,
            "external_id": self.asset.external_id,
            "title": "چرخ‌دنده صنعتی قابل چاپ",
            "short_description": "توضیح کوتاه دریافت‌شده از منبع",
            "description": "توضیحات کامل و قابل ویرایش مدل از صفحه اصلی منبع.",
            "author_name": "Designer",
            "creator_url": "https://www.printables.com/@designer",
            "license_name": "CC BY",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "tags": ["gear", "industrial"],
            "source_category": "Engineering",
            "images": [
                "https://example.com/image-1.png",
                "https://example.com/image-2.png",
                "https://example.com/image-3.png",
            ],
            "file_links": ["https://example.com/private-file.stl"],
            "file_formats": ["STL", "3MF"],
            "estimated_weight_grams": 42,
            "estimated_print_minutes": 95,
            "estimate_source": "source_profile",
            "commercial_use_allowed": True,
            "license_review_status": "allowed",
            "blocked_reason": "",
            "attribution_text": "Gear — Designer — Printables",
            "metrics": {"views_count": 12000, "downloads_count": 3400, "likes_count": 520},
            "raw_payload": {
                "json_blobs": [
                    {
                        "printProfiles": [
                            {
                                "profileName": "سبک",
                                "filamentWeight": "42 g",
                                "printTime": "1h 35m",
                                "material": "PLA",
                                "layerHeight": "0.20 mm",
                                "infillPercent": "15%",
                            },
                            {
                                "profileName": "مقاوم",
                                "filamentWeight": "68 g",
                                "printTime": "2h 20m",
                                "material": "PETG",
                                "layerHeight": "0.16 mm",
                                "infillPercent": "35%",
                            },
                        ]
                    }
                ]
            },
        }

    def test_extracts_multiple_weight_profiles(self):
        rows = extract_print_profiles(self.payload())
        weights = [row["weight_grams"] for row in rows if row["weight_grams"]]
        self.assertIn(Decimal("42.00"), weights)
        self.assertIn(Decimal("68.00"), weights)

    @patch("store.catalog_preview.get_source_adapter")
    def test_refresh_downloads_all_images_and_keeps_metadata_only(self, mocked_adapter):
        mocked_adapter.return_value = _FakeAdapter(self.payload())
        result = refresh_asset_metadata(self.asset, download_images=True, max_images=20)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.title, "چرخ‌دنده صنعتی قابل چاپ")
        self.assertIn("توضیحات کامل", self.asset.description)
        self.assertTrue(self.asset.preview_image)
        self.assertEqual(self.asset.images.filter(image__isnull=False).exclude(image="").count(), 3)
        self.assertEqual(self.asset.print_profiles.filter(is_manual=False).count(), result.profiles_found)
        self.assertEqual(self.asset.private_download_url, "")
        self.assertEqual(self.asset.metrics.file_links, [])
        self.assertTrue(self.asset.technical_specs.get("metadata_only"))

    @patch("store.catalog_preview.get_source_adapter")
    def test_manual_weight_profile_survives_refresh(self, mocked_adapter):
        ImportedPrintAssetPrintProfile.objects.create(
            asset=self.asset,
            profile_name="وزن دستی مشتری",
            weight_grams=Decimal("80.00"),
            is_manual=True,
        )
        mocked_adapter.return_value = _FakeAdapter(self.payload())
        refresh_asset_metadata(self.asset, download_images=False)
        self.assertTrue(
            self.asset.print_profiles.filter(profile_name="وزن دستی مشتری", is_manual=True).exists()
        )

    @patch("store.catalog_preview.get_source_adapter")
    def test_admin_list_shows_thumbnail_description_and_weights(self, mocked_adapter):
        mocked_adapter.return_value = _FakeAdapter(self.payload())
        refresh_asset_metadata(self.asset, download_images=True)
        user = User.objects.create_superuser("phase17-admin", "phase17@example.com", "pass12345")
        self.client.force_login(user)
        response = self.client.get(reverse("admin:store_importedprintasset_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "چرخ‌دنده صنعتی قابل چاپ")
        self.assertContains(response, "توضیح کوتاه دریافت‌شده")
        self.assertContains(response, "42 گرم")
        self.assertContains(response, "<img", html=False)

    @patch("store.catalog_preview.get_source_adapter")
    def test_admin_change_page_contains_gallery_and_profiles(self, mocked_adapter):
        mocked_adapter.return_value = _FakeAdapter(self.payload())
        refresh_asset_metadata(self.asset, download_images=True)
        user = User.objects.create_superuser("phase17-detail", "detail@example.com", "pass12345")
        self.client.force_login(user)
        response = self.client.get(reverse("admin:store_importedprintasset_change", args=[self.asset.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "گالری پیش‌نمایش")
        self.assertContains(response, "سبک")
        self.assertContains(response, "مقاوم")
        self.assertContains(response, "بازکردن صفحه منبع")
