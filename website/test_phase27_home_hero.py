from django.test import TestCase
from django.urls import NoReverseMatch, reverse

from store.models import CatalogAssetMetrics, CatalogSourcePolicy, ImportedPrintAsset, PrintCatalogSource


class Phase27HistoricalHeroCompatibilityTests(TestCase):
    """Keep the useful Phase 27 data contracts without resurrecting retired public UI."""

    def setUp(self):
        self.source = PrintCatalogSource.objects.create(
            name="Phase 27 Source",
            code="phase27-source",
            base_url="https://models.example.com/",
            allowed_domains="models.example.com",
        )
        CatalogSourcePolicy.objects.create(
            source=self.source,
            source_kind="custom",
            discovery_mode="public_html",
            public_reference_enabled=True,
        )

    def create_asset(self, title, image):
        asset = ImportedPrintAsset.objects.create(
            source=self.source,
            source_url=f"https://models.example.com/{title}",
            external_id=title,
            title=title,
            remote_image_url=image,
        )
        CatalogAssetMetrics.objects.create(
            asset=asset,
            source_kind="custom",
            image_urls=[image],
            commercial_use_allowed=None,
            license_review_status="manual",
        )
        return asset

    def test_historical_home_context_keeps_newest_catalog_items_first(self):
        older = self.create_asset("older-model", "https://models.example.com/older.jpg")
        newer = self.create_asset("newer-model", "https://models.example.com/newer.jpg")
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        assets = list(response.context["hero_model_slider"])
        self.assertEqual(assets[:2], [newer, older])

    def test_home_uses_current_managed_hero_not_retired_phase27_markup(self):
        self.create_asset("hero-model", "https://models.example.com/hero.jpg")
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-p45-hero")
        self.assertContains(response, "phase45-home-hero.css")
        self.assertNotContains(response, "data-p27-home-hero")
        self.assertNotContains(response, "phase27-home-hero.js")
        self.assertNotContains(response, "/store/ready-models/")

    def test_legacy_reference_record_is_preserved_without_public_catalog_route(self):
        source = PrintCatalogSource.objects.create(
            name="Legacy Source",
            code="phase27-legacy-source",
            base_url="https://legacy.example.com/",
            allowed_domains="legacy.example.com",
        )
        asset = ImportedPrintAsset.objects.create(
            source=source,
            source_url="https://legacy.example.com/model/1",
            external_id="legacy-1",
            title="مدل مرجع قدیمی",
            remote_image_url="https://legacy.example.com/model.jpg",
        )
        CatalogAssetMetrics.objects.create(
            asset=asset,
            source_kind="custom",
            image_urls=[asset.remote_image_url],
        )
        asset.refresh_from_db()
        self.assertEqual(asset.public_display_mode, "reference")
        with self.assertRaises(NoReverseMatch):
            reverse("store:external_catalog")
