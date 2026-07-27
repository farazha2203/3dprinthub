from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from store.catalog_population import DEFAULT_SORT_MODES
from store.market_pricing import _phase16_record_bambu_price_history
from store.models import (
    BambuFilamentCatalogItem,
    BambuFilamentPriceHistory,
    CatalogAssetMetrics,
    ImportedPrintAsset,
    PrintCatalogSource,
)


class Phase16CatalogRankingAndPriceHistoryTests(TestCase):
    def create_bambu_item(self):
        return BambuFilamentCatalogItem.objects.create(
            external_id="bambu-pla-basic",
            handle="pla-basic",
            title="PLA Basic",
            product_url="https://us.store.bambulab.com/products/pla-basic",
            image_url="https://example.com/pla.jpg",
            vendor="Bambu Lab",
            product_type="Filament",
            min_price_usd=Decimal("19.99"),
            max_price_usd=Decimal("24.99"),
            conservative_price_usd=Decimal("24.99"),
            available=True,
            variants=[],
            raw_payload={},
        )

    def test_population_priority_is_views_then_downloads_likes_trending(self):
        self.assertEqual(
            DEFAULT_SORT_MODES,
            ("views", "downloads", "likes", "trending"),
        )

    def test_bambu_history_keeps_previous_and_new_price(self):
        item = self.create_bambu_item()
        now = timezone.now()
        _phase16_record_bambu_price_history(
            [{"handle": item.handle}],
            observed_at=now,
            source_mode="test",
        )
        item.conservative_price_usd = Decimal("27.50")
        item.max_price_usd = Decimal("27.50")
        item.save(update_fields=["conservative_price_usd", "max_price_usd", "updated_at"])
        _phase16_record_bambu_price_history(
            [{"handle": item.handle}],
            observed_at=timezone.now(),
            source_mode="test",
        )
        latest = BambuFilamentPriceHistory.objects.filter(item=item).first()
        self.assertEqual(latest.previous_conservative_price_usd, Decimal("24.99"))
        self.assertEqual(latest.conservative_price_usd, Decimal("27.50"))
        self.assertEqual(latest.delta_usd, Decimal("2.51"))
        self.assertTrue(latest.changed)

    def test_bambu_admin_shows_previous_new_and_history_link(self):
        item = self.create_bambu_item()
        _phase16_record_bambu_price_history([{"handle": item.handle}], source_mode="test")
        item.conservative_price_usd = Decimal("22.00")
        item.save(update_fields=["conservative_price_usd", "updated_at"])
        _phase16_record_bambu_price_history([{"handle": item.handle}], source_mode="test")
        user = User.objects.create_superuser("phase16-admin", "admin@example.com", "pass12345")
        self.client.force_login(user)
        response = self.client.get(reverse("admin:store_bambufilamentcatalogitem_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "قیمت قبلی")
        self.assertContains(response, "قیمت جدید")
        self.assertContains(response, "مشاهده همه تغییرات")

    def test_imported_assets_admin_shows_source_popularity_metrics(self):
        source = PrintCatalogSource.objects.create(
            name="Printables",
            code="printables-phase16",
            base_url="https://www.printables.com/",
            allowed_domains="printables.com",
            adapter_key="custom",
        )
        asset = ImportedPrintAsset.objects.create(
            source=source,
            source_url="https://www.printables.com/model/123-example",
            external_id="123",
            title="Popular Gear",
            file_format="STL",
        )
        CatalogAssetMetrics.objects.create(
            asset=asset,
            source_kind="printables",
            popularity_rank=1,
            views_count=120000,
            downloads_count=34000,
            likes_count=5600,
            commercial_use_allowed=True,
            license_review_status="allowed",
            public_approved=True,
        )
        user = User.objects.create_superuser("phase16-assets", "assets@example.com", "pass12345")
        self.client.force_login(user)
        response = self.client.get(reverse("admin:store_importedprintasset_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Popular Gear")
        self.assertContains(response, "120,000")
        self.assertContains(response, "34,000")
        self.assertContains(response, "5,600")
        self.assertContains(response, "مجاز تجاری")

    def test_dashboard_links_to_catalog_and_bambu_history(self):
        user = User.objects.create_superuser("phase16-dashboard", "dash@example.com", "pass12345")
        self.client.force_login(user)
        response = self.client.get(reverse("admin:store_catalogautomationdashboard_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "مدل‌های دریافت‌شده و رتبه محبوبیت")
        self.assertContains(response, "تاریخچه کامل قیمت Bambu")
