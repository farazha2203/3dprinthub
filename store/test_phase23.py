from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from website.models import Material, Quote

from .catalog_site_adapters.common import CatalogCandidate
from .catalog_automation import homepage_catalog_assets
from .catalog_sync import public_catalog_queryset, sync_catalog_source
from .link_intelligence import (
    analyze_customer_link,
    create_order_from_analysis,
    normalize_public_url,
)
from .models import (
    CatalogAssetMetrics,
    CatalogSourcePolicy,
    CustomerLinkAnalysis,
    ImportedPrintAsset,
    PricingSetting,
    PrintCatalogSource,
)


class Phase23CatalogReferenceTests(TestCase):
    def setUp(self):
        self.source = PrintCatalogSource.objects.create(
            name="Reference Source",
            code="phase23-reference",
            base_url="https://models.example.com/",
            allowed_domains="models.example.com",
            download_preview_images=False,
        )
        self.policy = CatalogSourcePolicy.objects.create(
            source=self.source,
            source_kind="custom",
            public_display_policy="source_link_only",
            discovery_mode="public_html",
        )

    def create_asset(self, **overrides):
        defaults = {
            "source": self.source,
            "source_url": "https://models.example.com/model/gear-1",
            "external_id": "gear-1",
            "title": "Industrial Gear",
            "remote_image_url": "https://models.example.com/images/gear.jpg",
        }
        defaults.update(overrides)
        asset = ImportedPrintAsset.objects.create(**defaults)
        CatalogAssetMetrics.objects.create(
            asset=asset,
            source_kind="custom",
            commercial_use_allowed=None,
            license_review_status="manual",
            image_urls=[asset.remote_image_url] if asset.remote_image_url else [],
        )
        return asset

    def test_reference_item_is_public_without_license_or_model_file(self):
        asset = self.create_asset()
        self.assertTrue(public_catalog_queryset().filter(pk=asset.pk).exists())
        self.assertEqual(asset.public_display_mode, "reference")
        self.assertEqual(asset.catalog_image_url, asset.remote_image_url)

    def test_catalog_page_renders_remote_image_and_source(self):
        asset = self.create_asset()
        response = self.client.get(reverse("store:external_catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, asset.title)
        self.assertContains(response, asset.remote_image_url)
        self.assertContains(response, self.source.name)


    def test_policy_can_hide_reference_without_deleting_it(self):
        asset = self.create_asset(source_url="https://models.example.com/model/hidden")
        self.policy.public_reference_enabled = False
        self.policy.save(update_fields=["public_reference_enabled"])
        self.assertFalse(public_catalog_queryset().filter(pk=asset.pk).exists())

    def test_homepage_uses_remote_reference_image_without_manual_publication(self):
        asset = self.create_asset(source_url="https://models.example.com/model/home-reference")
        self.assertIn(asset, list(homepage_catalog_assets(slider=True, limit=5)))

    def test_sync_persists_candidate_when_detail_fetch_fails(self):
        class FakeAdapter:
            def discover(self, *, limit, sort_mode):
                return [CatalogCandidate(
                    url="https://models.example.com/model/partial-2",
                    external_id="partial-2",
                    summary={"title": "Partial Model", "images": ["https://models.example.com/partial.jpg"]},
                )]

            def fetch_record(self, candidate, *, hydrate_files=False):
                raise RuntimeError("detail endpoint blocked")

        with patch("store.catalog_sync.get_source_adapter", return_value=FakeAdapter()):
            run = sync_catalog_source(source=self.source, requested_limit=1)
        self.assertEqual(run.imported_count, 1)
        self.assertEqual(run.status, "partial")
        asset = ImportedPrintAsset.objects.get(source_url="https://models.example.com/model/partial-2")
        self.assertEqual(asset.title, "Partial Model")
        self.assertEqual(asset.remote_image_url, "https://models.example.com/partial.jpg")

    def test_sync_uses_generic_api_summary_when_detail_fetch_fails(self):
        class FakeAdapter:
            def discover(self, *, limit, sort_mode):
                return [CatalogCandidate(
                    url="https://models.example.com/model/api-summary",
                    external_id="api-summary",
                    summary={
                        "name": "API Summary Gear",
                        "thumbnail": "https://models.example.com/api-gear.jpg",
                        "creator": {"username": "gear-designer"},
                        "download_count": 420,
                        "tags": [{"name": "gear"}, {"name": "mechanical"}],
                    },
                )]

            def fetch_record(self, candidate, *, hydrate_files=False):
                raise RuntimeError("detail endpoint blocked")

        with patch("store.catalog_sync.get_source_adapter", return_value=FakeAdapter()):
            run = sync_catalog_source(source=self.source, requested_limit=1)
        self.assertEqual(run.imported_count, 1)
        asset = ImportedPrintAsset.objects.get(source_url="https://models.example.com/model/api-summary")
        self.assertEqual(asset.title, "API Summary Gear")
        self.assertEqual(asset.remote_image_url, "https://models.example.com/api-gear.jpg")
        self.assertEqual(asset.metrics.downloads_count, 420)


class Phase23LinkIntelligenceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="phase23-user",
            email="phase23@example.com",
            password="StrongPass123!",
            first_name="فراز",
            last_name="حراجی",
        )
        self.material = Material.objects.create(
            name="PETG",
            price_per_kg=1_000_000,
            sale_price_per_gram=1200,
            main_usage="قطعات کاربردی",
            sample_parts="چرخ‌دنده",
            is_active=True,
        )
        PricingSetting.objects.update_or_create(
            pk=1,
            defaults={
                "default_hourly_rate": 120_000,
                "default_labor_percent": Decimal("25"),
                "minimum_order_amount": 50_000,
                "packaging_fee": 20_000,
            },
        )

    def test_private_address_is_blocked(self):
        with self.assertRaises(ValidationError):
            normalize_public_url("http://127.0.0.1/internal")


    def test_direct_file_link_is_preserved_without_downloading_model(self):
        analysis = CustomerLinkAnalysis.objects.create(
            user=self.user,
            source_url="https://example.com/files/industrial-gear.step",
            normalized_url="https://example.com/files/industrial-gear.step",
            source_domain="example.com",
        )
        with patch("store.link_intelligence._assert_public_host"):
            analyze_customer_link(analysis)
        analysis.refresh_from_db()
        self.assertEqual(analysis.status, "needs_input")
        self.assertEqual(analysis.title, "industrial gear")
        self.assertEqual(analysis.file_formats, ["STEP"])
        self.assertEqual(analysis.file_links, ["https://example.com/files/industrial-gear.step"])

    def test_analyze_link_extracts_best_effort_and_estimates(self):
        html = b'''<!doctype html><html><head>
        <meta property="og:site_name" content="Model Lab">
        <meta property="og:title" content="PETG Functional Bracket">
        <meta property="og:description" content="Strong PETG bracket for industrial use">
        <meta property="og:image" content="https://cdn.example.com/bracket.jpg">
        <script type="application/ld+json">{
          "@type":"Product","name":"PETG Functional Bracket","description":"Strong PETG bracket",
          "image":"https://cdn.example.com/bracket.jpg",
          "additionalProperty":[
            {"name":"Filament weight","value":"84 g"},
            {"name":"Print time","value":"2 h 30 min"},
            {"name":"Material","value":"PETG"}
          ]
        }</script></head><body><a href="/downloads/bracket.stl">download</a></body></html>'''

        def fake_fetch(url, *, max_bytes, accept, timeout=20):
            if "image/" in accept:
                return b"GIF89a", "image/gif", "https://cdn.example.com/bracket.jpg"
            return html, "text/html", "https://public.example.com/models/bracket"

        analysis = CustomerLinkAnalysis.objects.create(
            user=self.user,
            source_url="https://public.example.com/models/bracket",
            normalized_url="https://public.example.com/models/bracket",
            source_domain="public.example.com",
        )
        # DNS validation is intentionally kept in production for SSRF protection.
        # The fetch layer is mocked in this unit test, so DNS must be mocked too;
        # otherwise reserved example domains correctly fail before the fake fetch runs.
        with (
            patch("store.link_intelligence._assert_public_host"),
            patch("store.link_intelligence._safe_fetch", side_effect=fake_fetch),
        ):
            analyze_customer_link(analysis)
        analysis.refresh_from_db()
        self.assertEqual(analysis.status, "ready")
        self.assertEqual(analysis.title, "PETG Functional Bracket")
        self.assertEqual(analysis.material, self.material)
        self.assertEqual(analysis.estimated_weight_grams, Decimal("84.00"))
        self.assertEqual(analysis.estimated_print_minutes, 150)
        self.assertIn("STL", analysis.file_formats)
        self.assertGreater(analysis.estimated_price, 0)
        self.assertGreater(analysis.estimated_price_max, analysis.estimated_price_min)

        order = create_order_from_analysis(
            analysis,
            user=self.user,
            full_name="فراز حراجی",
            phone="09120000000",
        )
        analysis.refresh_from_db()
        quote = Quote.objects.get(order=order)
        self.assertEqual(analysis.status, "converted")
        self.assertEqual(order.status, "quoted")
        self.assertEqual(quote.status, "sent")
        self.assertGreater(quote.total_price, 0)


class Phase23CustomerLinkHistoryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="phase23-history", email="history@example.com", password="pass12345"
        )

    def test_customer_can_view_own_link_analysis_history(self):
        own = CustomerLinkAnalysis.objects.create(
            user=self.user,
            source_url="https://example.com/own-model",
            normalized_url="https://example.com/own-model",
            source_domain="example.com",
            title="Own model",
            status="partial",
        )
        CustomerLinkAnalysis.objects.create(
            source_url="https://example.org/other-model",
            normalized_url="https://example.org/other-model",
            source_domain="example.org",
            title="Other model",
            status="partial",
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("store:customer_link_analyses"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, own.title)
        self.assertNotContains(response, "Other model")
