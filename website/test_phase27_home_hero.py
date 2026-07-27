from django.test import TestCase
from django.urls import reverse

from store.models import CatalogAssetMetrics, CatalogSourcePolicy, ImportedPrintAsset, PrintCatalogSource


class Phase27FullscreenHeroTests(TestCase):
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

    def test_home_hero_uses_newest_catalog_items_first(self):
        older = self.create_asset("older-model", "https://models.example.com/older.jpg")
        newer = self.create_asset("newer-model", "https://models.example.com/newer.jpg")
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        assets = list(response.context["hero_model_slider"])
        self.assertEqual(assets[:2], [newer, older])

    def test_home_renders_fullscreen_background_slider_and_product_links(self):
        asset = self.create_asset("hero-model", "https://models.example.com/hero.jpg")
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, "data-p27-home-hero")
        self.assertContains(response, "data-p27-hero-slide")
        self.assertContains(response, "data-p14-hero-slider")
        self.assertContains(response, "p27-home-hero__backdrop")
        self.assertContains(response, "p27-home-hero__subject-frame")
        self.assertContains(response, "p27-home-hero__subject")
        self.assertContains(response, reverse("store:external_catalog_detail", args=[asset.pk]))
        self.assertContains(response, asset.remote_image_url)
        self.assertContains(response, "phase27-home-hero.css")
        self.assertContains(response, "phase27-home-hero.js")

    def test_legacy_active_source_without_policy_remains_visible_as_reference(self):
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
        response = self.client.get(reverse("store:external_catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, asset.title)
        self.assertEqual(asset.public_display_mode, "reference")
