from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from website.models import Material

from .market_pricing import (
    _normalize_bambu_product,
    effective_fx_rates,
    parse_tgju_dollar_html,
    refresh_material_market_prices,
    sync_bambu_collection,
)
from .models import (
    BambuFilamentCatalogItem,
    ExchangeRateProvider,
    ExchangeRateSnapshot,
    ExternalSourceFetchLog,
    MarketPricingSetting,
)
from .source_monitoring import source_log, update_log


class Phase11TGJUTests(TestCase):
    def test_tgju_parser_reads_current_and_daily_high_in_rial(self):
        html = """
        <div>نرخ فعلی: 1,893,000</div>
        <table><tr><td>بالاترین قیمت روز</td><td>1,895,200</td></tr></table>
        <div>واحد پولی : ریال</div>
        """
        data = parse_tgju_dollar_html(html)
        self.assertEqual(data["current_toman"], Decimal("189300.00"))
        self.assertEqual(data["daily_high_toman"], Decimal("189520.00"))

    def test_tgju_parser_accepts_persian_digits(self):
        html = "<div>نرخ فعلی: ۱,۹۰۰,۰۰۰</div><div>بالاترین قیمت روز ۱,۹۵۰,۰۰۰</div>"
        data = parse_tgju_dollar_html(html)
        self.assertEqual(data["current_toman"], Decimal("190000.00"))
        self.assertEqual(data["daily_high_toman"], Decimal("195000.00"))

    def test_effective_rate_uses_raw_tgju_daily_high(self):
        provider = ExchangeRateProvider.objects.get(code="tgju-dollar")
        now = timezone.now()
        ExchangeRateSnapshot.objects.create(
            provider=provider,
            sell_rate_toman=Decimal("187000"),
            observed_at=now,
            local_date=timezone.localdate(now),
            raw_payload={"daily_high_toman": "195000"},
        )
        current, high = effective_fx_rates(now=now)
        self.assertEqual(current, Decimal("187000"))
        self.assertEqual(high, Decimal("195000"))

    def test_phase11_migration_seeds_tgju_provider(self):
        provider = ExchangeRateProvider.objects.get(code="tgju-dollar")
        self.assertEqual(provider.provider_type, "tgju_html")
        self.assertTrue(provider.is_active)
        self.assertIn("tgju.org", provider.endpoint_url)


class Phase11BambuTests(TestCase):
    def sample_product(self):
        return {
            "id": 101,
            "handle": "pla-basic-filament",
            "title": "PLA Basic",
            "vendor": "Bambu Lab",
            "product_type": "Filament",
            "tags": ["PLA"],
            "images": [{"src": "https://cdn.example/pla.jpg"}],
            "variants": [
                {"id": 1, "title": "Refill", "price": "19.99", "available": True},
                {"id": 2, "title": "With spool", "price": "24.99", "available": True},
            ],
        }

    def test_bambu_product_uses_highest_variant_price(self):
        record = _normalize_bambu_product(self.sample_product(), "https://us.store.bambulab.com")
        self.assertEqual(record["min_price_usd"], Decimal("19.99"))
        self.assertEqual(record["max_price_usd"], Decimal("24.99"))
        self.assertEqual(record["conservative_price_usd"], Decimal("24.99"))

    @patch("store.market_pricing.fetch_bambu_collection")
    def test_bambu_sync_saves_catalog_and_log(self, mocked):
        record = _normalize_bambu_product(self.sample_product(), "https://us.store.bambulab.com")
        mocked.return_value = ([record], {"mode": "shopify_products_json", "http": {"http_status": 200}})
        records, log = sync_bambu_collection()
        self.assertEqual(len(records), 1)
        self.assertEqual(log.status, "success")
        item = BambuFilamentCatalogItem.objects.get(handle="pla-basic-filament")
        self.assertEqual(item.conservative_price_usd, Decimal("24.99"))

    @patch("store.market_pricing.fetch_bambu_collection")
    def test_material_refresh_matches_cached_bambu_handle(self, mocked):
        record = _normalize_bambu_product(self.sample_product(), "https://us.store.bambulab.com")
        mocked.return_value = ([record], {"mode": "shopify_products_json", "http": {"http_status": 200}})
        provider = ExchangeRateProvider.objects.get(code="tgju-dollar")
        now = timezone.now()
        ExchangeRateSnapshot.objects.create(
            provider=provider,
            sell_rate_toman=Decimal("187000"),
            observed_at=now,
            local_date=timezone.localdate(now),
            raw_payload={"daily_high_toman": "195000"},
        )
        material = Material.objects.create(
            name="PLA Basic",
            main_usage="عمومی",
            sample_parts="نمونه",
            market_pricing_enabled=True,
            bambu_product_url="https://us.store.bambulab.com/products/pla-basic-filament",
            bambu_reference_weight_grams=1000,
            market_import_cost_percent=0,
            market_margin_percent=100,
        )
        setting = MarketPricingSetting.load()
        setting.enabled = True
        setting.save(update_fields=["enabled"])
        results, errors = refresh_material_market_prices(refresh_bambu=True, now=now)
        self.assertFalse(errors)
        self.assertEqual(len(results), 1)
        material.refresh_from_db()
        self.assertEqual(material.market_bambu_usd_price, Decimal("24.99"))
        self.assertGreater(material.market_sale_price_per_gram, 0)


class Phase11MonitoringTests(TestCase):
    def test_source_log_records_failure_details(self):
        with self.assertRaisesMessage(ValueError, "sample failure"):
            with source_log(source_key="tgju", action="test") as log:
                update_log(log, stage="پارسر", progress=50)
                raise ValueError("sample failure")
        log.refresh_from_db()
        self.assertEqual(log.status, "failed")
        self.assertEqual(log.progress_percent, 100)
        self.assertIn("sample failure", log.error)

    def test_admin_dashboard_renders_phase11_controls(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser("phase11-admin", "admin@example.com", "StrongPass123!")
        self.client.force_login(admin_user)
        response = self.client.get(reverse("admin:store_catalogautomationdashboard_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "تست اتصال")
        self.assertContains(response, "TGJU")
        self.assertContains(response, "Bambu Lab")

    @patch("store.admin._phase11_test_exchange_provider")
    def test_admin_tgju_test_button_is_post_only_and_reports_success(self, mocked):
        provider = ExchangeRateProvider.objects.get(code="tgju-dollar")
        log = ExternalSourceFetchLog.objects.create(source_key="tgju", action="test", status="success")
        mocked.return_value = (Decimal("189300"), {"daily_high_toman": "189520"}, log)
        User = get_user_model()
        admin_user = User.objects.create_superuser("phase11-button", "button@example.com", "StrongPass123!")
        self.client.force_login(admin_user)
        url = reverse("admin:store_catalogautomationdashboard_test_tgju")
        self.assertEqual(self.client.get(url).status_code, 302)
        self.assertEqual(self.client.post(url).status_code, 302)
        mocked.assert_called_once()
