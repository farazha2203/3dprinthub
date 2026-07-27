from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .catalog_classification import classify_external_asset
from .catalog_site_adapters.common import CatalogCandidate, extract_file_formats, license_decision
from .catalog_site_adapters.printables import PrintablesAdapter
from .catalog_sync import public_catalog_queryset, save_external_record
from .models import (
    CatalogAssetMetrics,
    CatalogCategoryRule,
    CatalogSourcePolicy,
    Category,
    ImportedPrintAsset,
    PrintCatalogSource,
)


SAMPLE_PRINTABLES = '''
<html><head>
<meta property="og:title" content="Industrial Gear Holder">
<meta property="og:description" content="Functional holder for workshop use">
<meta property="og:image" content="https://media.printables.com/example.jpg">
<script type="application/ld+json">{
 "@type":"CreativeWork","name":"Industrial Gear Holder","description":"Functional holder",
 "author":{"name":"CAD Maker","url":"https://www.printables.com/@cadmaker"},
 "license":{"name":"CC BY 4.0","url":"https://creativecommons.org/licenses/by/4.0/"},
 "keywords":["gear","holder","industrial"],
 "downloadCount":15200,"likeCount":820,"viewCount":41000,
 "encoding":[{"contentUrl":"https://files.printables.com/gear-holder.stl"}],
 "additionalProperty":[{"name":"printTime","value":"2h 30m"},{"name":"filamentWeight","value":"84 g"}]
}</script></head><body></body></html>
'''


class Phase9Base(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="فایل‌های صنعتی",
            slug="phase9-industrial",
            section="industrial",
            is_active=True,
        )
        self.source = PrintCatalogSource.objects.create(
            name="Printables Test",
            code="printables-test",
            base_url="https://www.printables.com/",
            allowed_domains="printables.com,media.printables.com,files.printables.com",
            adapter_key="custom",
            default_category=self.category,
            download_preview_images=False,
            respect_robots_txt=False,
            store_private_download_url=True,
        )
        self.policy = CatalogSourcePolicy.objects.create(
            source=self.source,
            source_kind="printables",
            discovery_mode="public_html",
            public_display_policy="licensed_only",
            default_limit=200,
            maximum_limit=500,
            cache_images_after_approval=False,
        )
        CatalogCategoryRule.objects.create(
            segment="industrial",
            target_category=self.category,
            title_keywords="gear,industrial",
            priority=1,
        )


class LicenseTests(Phase9Base):
    def test_makerworld_standard_license_is_blocked(self):
        allowed, status, _ = license_decision("makerworld", "Standard Digital File License")
        self.assertIs(allowed, False)
        self.assertEqual(status, "blocked")

    def test_printables_cc_by_is_allowed(self):
        allowed, status, _ = license_decision("printables", "CC BY 4.0")
        self.assertIs(allowed, True)
        self.assertEqual(status, "allowed")

    def test_grabcad_is_always_admin_only(self):
        allowed, status, _ = license_decision("grabcad", "free")
        self.assertIs(allowed, False)
        self.assertEqual(status, "blocked")


class AdapterTests(Phase9Base):
    def test_printables_adapter_parses_metrics_files_and_estimates(self):
        adapter = PrintablesAdapter(self.source, self.policy)
        adapter.client.fetch_text = lambda url: SAMPLE_PRINTABLES
        record = adapter.fetch_record(CatalogCandidate("https://www.printables.com/model/123-industrial-gear-holder", "123"), hydrate_files=True)
        self.assertEqual(record["downloads_count"] if "downloads_count" in record else record["metrics"]["downloads_count"], 15200)
        self.assertIn("STL", record["file_formats"])
        self.assertEqual(record["estimated_print_minutes"], 150)
        self.assertEqual(record["estimated_weight_grams"], 84.0)
        self.assertIs(record["commercial_use_allowed"], True)

    def test_formats_are_deduplicated(self):
        self.assertEqual(extract_file_formats(["a.stl", "b.STL", "model.3mf"]), ["3MF", "STL"])


class ClassificationTests(Phase9Base):
    def test_industrial_rule_assigns_category(self):
        result = classify_external_asset(
            source_kind="printables",
            title="Gear fixture",
            description="workshop tool",
            tags=["mechanical"],
            source_category="Engineering",
        )
        self.assertEqual(result.segment, "industrial")
        self.assertEqual(result.category, self.category)


class PersistenceAndVisibilityTests(Phase9Base):
    def _record(self):
        return {
            "source_url": "https://www.printables.com/model/123-industrial-gear-holder",
            "external_id": "123",
            "title": "Industrial Gear Holder",
            "short_description": "Functional holder",
            "description": "Functional holder for workshop use",
            "author_name": "CAD Maker",
            "creator_url": "https://www.printables.com/@cadmaker",
            "license_name": "CC BY 4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "tags": ["gear", "industrial"],
            "source_category": "Engineering",
            "images": ["https://media.printables.com/example.jpg"],
            "file_links": ["https://files.printables.com/gear-holder.stl"],
            "file_formats": ["STL"],
            "estimated_weight_grams": 84,
            "estimated_print_minutes": 150,
            "estimate_source": "source_profile",
            "commercial_use_allowed": True,
            "license_review_status": "allowed",
            "blocked_reason": "",
            "attribution_text": "Industrial Gear Holder — CAD Maker — Printables",
            "metrics": {"downloads_count": 15200, "likes_count": 820, "views_count": 41000},
            "raw_payload": {},
        }

    def test_save_record_keeps_download_private(self):
        asset, metrics = save_external_record(source=self.source, policy=self.policy, parsed=self._record(), rank=1)
        self.assertEqual(asset.private_download_url, "https://files.printables.com/gear-holder.stl")
        self.assertEqual(metrics.file_links[0], asset.private_download_url)
        self.assertFalse(metrics.public_approved)

    def test_public_approval_requires_commercial_license(self):
        asset, metrics = save_external_record(source=self.source, policy=self.policy, parsed=self._record(), rank=1)
        metrics.commercial_use_allowed = False
        metrics.public_approved = True
        with self.assertRaises(ValidationError):
            metrics.full_clean()

    def test_public_queryset_returns_reference_before_commercial_approval(self):
        asset, metrics = save_external_record(source=self.source, policy=self.policy, parsed=self._record(), rank=1)
        self.assertTrue(public_catalog_queryset().filter(pk=asset.pk).exists())
        self.assertEqual(asset.public_display_mode, "reference")
        metrics.public_approved = True
        metrics.save(update_fields=["public_approved"])
        asset.refresh_from_db()
        self.assertEqual(asset.public_display_mode, "printable")

    def test_public_page_never_exposes_download_url(self):
        asset, metrics = save_external_record(source=self.source, policy=self.policy, parsed=self._record(), rank=1)
        asset.preview_image = SimpleUploadedFile("preview.jpg", b"fake-image", content_type="image/jpeg")
        asset.save(update_fields=["preview_image"])
        metrics.public_approved = True
        metrics.save(update_fields=["public_approved"])
        response = self.client.get(reverse("store:external_catalog_detail", args=[asset.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "https://files.printables.com/gear-holder.stl")
        self.assertContains(response, "Printables Test")


class PolicyTests(Phase9Base):
    def test_admin_can_increase_limit_within_cap(self):
        self.assertEqual(self.policy.clamp_limit(350), 350)
        self.assertEqual(self.policy.clamp_limit(900), 500)
