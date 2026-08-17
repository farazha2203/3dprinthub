from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from store.catalog_population import (
    _mark_source_file_availability,
    catalog_population_counts,
    configure_population_schedule,
    discover_population_candidates,
)
from store.catalog_site_adapters.common import CatalogCandidate, license_decision
from store.models import (
    CatalogAssetMetrics,
    CatalogSourcePolicy,
    CatalogSyncRun,
    ImportedPrintAsset,
    PrintCatalogSource,
)


class _FakeAdapter:
    source = type("Source", (), {"base_url": "https://example.com"})()

    def discover(self, *, limit, sort_mode):
        return [CatalogCandidate(url=f"https://example.com/model/{sort_mode}", external_id=sort_mode)]


class Phase15PopulationTests(TestCase):
    def setUp(self):
        self.source = PrintCatalogSource.objects.create(
            name="MakerWorld Test",
            code="makerworld-test",
            base_url="https://makerworld.com/en",
            adapter_key="makerworld",
        )
        self.policy = CatalogSourcePolicy.objects.create(
            source=self.source,
            source_kind="makerworld",
            default_limit=20,
            maximum_limit=100,
        )

    def test_schedule_configuration_remains_readable_for_historical_records(self):
        schedule = configure_population_schedule(self.policy, requested_limit=50)
        self.assertTrue(schedule.enabled)
        self.assertTrue(schedule.hydrate_files)
        self.assertTrue(schedule.auto_approve_commercial)
        self.assertTrue(schedule.cache_images_after_approval)
        self.assertTrue(schedule.show_approved_on_homepage)
        self.assertEqual(schedule.requested_limit, 50)

    @patch("store.catalog_population._discover_from_url", return_value=[])
    def test_discovery_parser_combines_multiple_sort_modes(self, _mock):
        candidates, errors = discover_population_candidates(
            _FakeAdapter(),
            source_key="makerworld",
            limit=3,
            sort_modes=("downloads", "trending", "newest"),
        )
        self.assertEqual(len(candidates), 3)
        self.assertFalse(errors)

    def test_cc_by_nd_is_commercial_when_unmodified(self):
        allowed, status, reason = license_decision(
            "makerworld",
            "Creative Commons Attribution-NoDerivatives",
            "",
        )
        self.assertTrue(allowed)
        self.assertEqual(status, "allowed")

    def test_standard_makerworld_license_stays_blocked(self):
        allowed, status, reason = license_decision(
            "makerworld",
            "Standard Digital File License",
            "free commercial use written in description",
        )
        self.assertFalse(allowed)
        self.assertEqual(status, "blocked")

    def test_source_page_marks_file_availability(self):
        asset = ImportedPrintAsset.objects.create(
            source=self.source,
            source_url="https://makerworld.com/en/models/1-test",
            title="مدل تست",
        )
        _mark_source_file_availability(asset, {"images": ["https://example.com/a.jpg"]})
        asset.refresh_from_db()
        self.assertTrue(asset.technical_specs["source_file_available"])

    def test_admin_dashboard_still_exposes_pricing_and_historical_catalog_status(self):
        admin_user = User.objects.create_superuser(
            username="phase15-admin",
            email="phase15@example.com",
            password="StrongPass123!",
        )
        self.client.force_login(admin_user)
        response = self.client.get(
            reverse("admin:store_catalogautomationdashboard_changelist")
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "داشبورد همگام‌سازی")

    def test_admin_prepare_population_does_not_queue_external_sources_in_phase49_2a(self):
        printables_source = PrintCatalogSource.objects.create(
            name="Printables Test",
            code="printables-phase15",
            base_url="https://www.printables.com/",
            adapter_key="printables",
        )
        CatalogSourcePolicy.objects.create(
            source=printables_source,
            source_kind="printables",
            default_limit=20,
            maximum_limit=100,
        )
        admin_user = User.objects.create_superuser(
            username="phase15-queue-admin",
            email="phase15q@example.com",
            password="StrongPass123!",
        )
        self.client.force_login(admin_user)
        response = self.client.post(
            reverse("admin:store_catalogautomationdashboard_prepare_population"),
            {"limit": 30},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CatalogSyncRun.objects.filter(status="queued").count(), 0)

    def test_counts_report_historical_public_assets(self):
        asset = ImportedPrintAsset.objects.create(
            source=self.source,
            source_url="https://makerworld.com/en/models/2-test",
            title="مدل عمومی",
            preview_image="previews/test.jpg",
        )
        CatalogAssetMetrics.objects.create(
            asset=asset,
            source_kind="makerworld",
            commercial_use_allowed=True,
            license_review_status="allowed",
            public_approved=True,
        )
        counts = catalog_population_counts()
        self.assertEqual(counts["all_imported"], 1)
        self.assertEqual(counts["public_with_image"], 1)
