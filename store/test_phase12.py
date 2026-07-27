from __future__ import annotations

from io import StringIO
from urllib.error import HTTPError
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .catalog_site_adapters.makerworld import MakerWorldAdapter
from .market_pricing import fetch_bambu_collection
from .models import (
    CatalogSeedURL,
    CatalogSourcePolicy,
    ExternalSourceFetchLog,
    PrintCatalogSource,
)
from .source_probes import test_catalog_source


class Phase12BambuFallbackTests(TestCase):
    def test_collection_html_and_product_js_fallback(self):
        collection_html = '''
        <a href="/products/pla-basic-filament">PLA Basic</a>
        <a href="/products/petg-cf">PETG-CF</a>
        '''

        def fake_json(url, *, timeout):
            if url.endswith("products.json?limit=250"):
                raise HTTPError(url, 404, "Not Found", None, None)
            if url.endswith("pla-basic-filament.js"):
                return ({
                    "id": 1,
                    "handle": "pla-basic-filament",
                    "title": "PLA Basic",
                    "vendor": "Bambu Lab",
                    "type": "Filament",
                    "variants": [
                        {"id": 1, "title": "Refill", "price": 1999, "available": True},
                        {"id": 2, "title": "With spool", "price": 2499, "available": True},
                    ],
                }, {"http_status": 200, "final_url": url})
            if url.endswith("petg-cf.js"):
                return ({
                    "id": 2,
                    "handle": "petg-cf",
                    "title": "PETG-CF",
                    "vendor": "Bambu Lab",
                    "type": "Filament",
                    "variants": [{"id": 3, "title": "1kg", "price": 3199, "available": True}],
                }, {"http_status": 200, "final_url": url})
            raise AssertionError(url)

        def fake_html(url, *, timeout):
            return collection_html, {"http_status": 200, "final_url": url}

        with patch("store.market_pricing._request_json", side_effect=fake_json), patch(
            "store.market_pricing._request_html", side_effect=fake_html
        ):
            records, meta = fetch_bambu_collection(
                "https://us.store.bambulab.com/collections/bambu-lab-3d-printer-filament",
                max_products=2,
            )

        self.assertEqual(meta["mode"], "collection_html_product_js")
        self.assertEqual(len(records), 2)
        self.assertEqual(str(records[0]["max_price_usd"]), "24.99")
        self.assertEqual(str(records[1]["max_price_usd"]), "31.99")


class Phase12SourceStateTests(TestCase):
    def make_source(self, key, base_url, allowed_domains, mode="public_html"):
        source = PrintCatalogSource.objects.create(
            name=key.title(),
            code=f"{key}-phase12",
            base_url=base_url,
            allowed_domains=allowed_domains,
            adapter_key=key,
        )
        policy = CatalogSourcePolicy.objects.create(
            source=source,
            source_kind=key,
            discovery_mode=mode,
            public_display_policy="admin_only" if key == "grabcad" else "licensed_only",
            api_token_env="THINGIVERSE_ACCESS_TOKEN" if key == "thingiverse" else "",
        )
        return source, policy

    def test_thingiverse_without_token_is_configuration_warning(self):
        _source, policy = self.make_source(
            "thingiverse", "https://www.thingiverse.com/", "thingiverse.com,api.thingiverse.com", "official_api"
        )
        with patch.dict("os.environ", {}, clear=True):
            record, log = test_catalog_source(policy)
        self.assertEqual(record["_probe_status"], "configuration_required")
        self.assertEqual(log.status, "partial")
        self.assertIn("THINGIVERSE_ACCESS_TOKEN", log.message)

    def test_grabcad_without_seed_is_manual_only(self):
        _source, policy = self.make_source("grabcad", "https://grabcad.com/", "grabcad.com", "admin_reference")
        record, log = test_catalog_source(policy)
        self.assertEqual(record["_probe_status"], "manual_only")
        self.assertEqual(log.status, "partial")

    def test_thingiverse_command_does_not_fail_for_missing_token(self):
        self.make_source(
            "thingiverse", "https://www.thingiverse.com/", "thingiverse.com,api.thingiverse.com", "official_api"
        )
        output = StringIO()
        with patch.dict("os.environ", {}, clear=True):
            call_command("test_external_sources", source="thingiverse", stdout=output)
        self.assertIn("configuration_required", output.getvalue())


class Phase12MakerWorldTests(TestCase):
    def setUp(self):
        self.source = PrintCatalogSource.objects.create(
            name="MakerWorld",
            code="makerworld-phase12",
            base_url="https://makerworld.com/",
            allowed_domains="makerworld.com,makerworld.bblmw.com",
            adapter_key="makerworld",
        )
        self.policy = CatalogSourcePolicy.objects.create(
            source=self.source,
            source_kind="makerworld",
            discovery_mode="public_html",
            public_display_policy="licensed_only",
        )

    def test_sitemap_is_used_when_listing_returns_403(self):
        adapter = MakerWorldAdapter(self.source, self.policy)

        def fake_fetch(url):
            if "/3d-models" in url:
                raise HTTPError(url, 403, "Forbidden", None, None)
            if url.endswith("/sitemap.xml"):
                return "https://makerworld.com/sitemap-0.xml"
            if url.endswith("/sitemaps/index.xml"):
                return ""
            if url.endswith("/sitemap-0.xml"):
                return "<loc>https://makerworld.com/en/models/526005-my-sign</loc>"
            raise AssertionError(url)

        with patch.object(adapter.client, "fetch_text", side_effect=fake_fetch):
            records = adapter.discover(limit=1, sort_mode="downloads")
        self.assertEqual(records[0].external_id, "526005")

    def test_admin_seed_url_can_be_registered(self):
        seed = CatalogSeedURL.objects.create(
            source=self.source,
            url="https://makerworld.com/en/models/526005-my-sign",
            label="نمونه تست",
        )
        self.assertTrue(seed.is_active)


class Phase12AdminTests(TestCase):
    def test_dashboard_has_seed_url_management(self):
        User = get_user_model()
        user = User.objects.create_superuser("phase12-admin", "admin@example.com", "StrongPass123!")
        self.client.force_login(user)
        response = self.client.get(reverse("admin:store_catalogautomationdashboard_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "لینک‌های بذر")
        self.assertContains(response, "product.js")

    def test_source_logs_keep_expected_state(self):
        log = ExternalSourceFetchLog.objects.create(
            source_key="makerworld",
            action="catalog_probe",
            status="partial",
            message="blocked_by_source",
        )
        self.assertEqual(log.status, "partial")
