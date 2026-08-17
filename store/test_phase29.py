from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from website.models import Material

from .catalog_sync import public_catalog_queryset
from .link_intelligence import analyze_customer_link, billable_print_minutes, normalize_public_url
from .manual_pricing import apply_manual_review_pricing
from .models import (
    CatalogAssetMetrics,
    CatalogSourcePolicy,
    CustomerLinkAnalysis,
    ImportedPrintAsset,
    LinkAnalysisManualReview,
    PricingSetting,
    PrintCatalogSource,
)


class Phase29VerifiedPricingTests(TestCase):
    """Pricing/parser rules remain valid for historical review data."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="phase29-user", email="p29@example.com", password="StrongPass123!"
        )
        self.operator = get_user_model().objects.create_superuser(
            username="phase29-operator", email="operator@example.com", password="StrongPass123!"
        )
        self.material = Material.objects.create(
            name="PETG", price_per_kg=1_000_000, sale_price_per_gram=1_200,
            main_usage="قطعات کاربردی", sample_parts="براکت", is_active=True,
        )
        PricingSetting.objects.update_or_create(
            pk=1,
            defaults={
                "default_hourly_rate": 120_000,
                "minimum_billable_minutes": 60,
                "billing_increment_minutes": 60,
                "default_labor_percent": Decimal("25"),
                "minimum_order_amount": 0,
                "packaging_fee": 0,
            },
        )

    def create_analysis(self, url="https://www.printables.com/model/133384-better-ventilated-funnel-parametric/related"):
        return CustomerLinkAnalysis.objects.create(
            user=self.user,
            source_url=url,
            normalized_url=url,
            source_domain="www.printables.com",
        )

    def test_printables_related_url_is_canonicalized(self):
        self.assertEqual(
            normalize_public_url("https://www.printables.com/model/133384-better-ventilated-funnel-parametric/related"),
            "https://www.printables.com/model/133384-better-ventilated-funnel-parametric",
        )

    def test_unlabeled_page_numbers_never_become_weight_or_print_time(self):
        html = b'''<!doctype html><html><head>
        <meta property="og:site_name" content="Printables">
        <meta property="og:title" content="Better ventilated funnel parametric">
        <meta property="og:description" content="Parametric funnel model">
        <meta property="og:image" content="https://media.example.com/funnel.jpg">
        <script type="application/ld+json">{
          "@type":"Product","name":"Better ventilated funnel parametric",
          "duration":8,"weight":8,"interactionStatistic":{"userInteractionCount":8}
        }</script></head><body>8 downloads, 8 likes, updated 8 days ago</body></html>'''

        def fake_fetch(url, *, max_bytes, accept, timeout=20):
            return html, "text/html", "https://www.printables.com/model/133384-better-ventilated-funnel-parametric"

        analysis = self.create_analysis()
        with (
            patch("store.link_intelligence._assert_public_host"),
            patch("store.link_intelligence._safe_fetch", side_effect=fake_fetch),
            patch("store.operator_notifications.notify_manual_review") as notify,
        ):
            analyze_customer_link(analysis, cache_remote_images=False)
        analysis.refresh_from_db()
        self.assertEqual(analysis.status, "needs_input")
        self.assertIsNone(analysis.estimated_weight_grams)
        self.assertIsNone(analysis.estimated_print_minutes)
        self.assertEqual(analysis.estimated_price, 0)
        self.assertFalse(analysis.has_authoritative_pricing_inputs)
        self.assertTrue(LinkAnalysisManualReview.objects.filter(analysis=analysis, status="pending").exists())
        notify.assert_called_once()

    def test_explicit_labeled_specs_are_accepted_and_hourly_rounded(self):
        html = b'''<!doctype html><html><head>
        <meta property="og:title" content="PETG bracket">
        <script type="application/ld+json">{
          "@type":"Product","name":"PETG bracket",
          "additionalProperty":[
            {"name":"Filament weight","value":"84 g"},
            {"name":"Print time","value":"1 h 30 min"},
            {"name":"Material","value":"PETG"}
          ]
        }</script></head><body></body></html>'''

        def fake_fetch(url, *, max_bytes, accept, timeout=20):
            return html, "text/html", "https://public.example.com/model/bracket"

        analysis = self.create_analysis("https://public.example.com/model/bracket")
        with (
            patch("store.link_intelligence._assert_public_host"),
            patch("store.link_intelligence._safe_fetch", side_effect=fake_fetch),
        ):
            analyze_customer_link(analysis, cache_remote_images=False)
        analysis.refresh_from_db()
        self.assertEqual(analysis.status, "ready")
        self.assertEqual(analysis.estimated_weight_grams, Decimal("84.00"))
        self.assertEqual(analysis.estimated_print_minutes, 90)
        self.assertEqual(analysis.estimate_breakdown["billable_print_minutes"], 120)
        self.assertGreater(analysis.estimated_price, 0)

    def test_billing_rounds_up_to_configured_hour_blocks(self):
        self.assertEqual(billable_print_minutes(8), 60)
        self.assertEqual(billable_print_minutes(60), 60)
        self.assertEqual(billable_print_minutes(61), 120)
        self.assertEqual(billable_print_minutes(90), 120)

    def test_operator_verification_locks_exact_price_and_finishes_review(self):
        analysis = self.create_analysis()
        analysis.title = "فانل پارامتریک"
        analysis.status = "needs_input"
        analysis.save(update_fields=["title", "status", "updated_at"])
        review = LinkAnalysisManualReview.objects.create(
            analysis=analysis,
            requested_by=self.user,
            operator_material=self.material,
            operator_weight_grams=Decimal("42.50"),
            operator_print_minutes=90,
            resolution_action="data_completed",
        )
        apply_manual_review_pricing(review, operator=self.operator)
        analysis.refresh_from_db()
        review.refresh_from_db()
        self.assertTrue(analysis.pricing_locked)
        self.assertEqual(analysis.estimate_breakdown["billable_print_minutes"], 120)
        self.assertEqual(analysis.estimated_price_min, analysis.estimated_price)
        self.assertEqual(analysis.estimated_price_max, analysis.estimated_price)
        self.assertEqual(analysis.estimate_confidence, Decimal("100"))
        self.assertEqual(review.status, "resolved")


class Phase29SourceLifecycleTests(TestCase):
    def create_source(self, code, kind, priority):
        source = PrintCatalogSource.objects.create(
            name=code.title(), code=code, base_url=f"https://{code}.example.com/",
            allowed_domains=f"{code}.example.com", is_active=True,
        )
        CatalogSourcePolicy.objects.create(
            source=source, source_kind=kind, public_display_policy="source_link_only",
            discovery_mode="public_html", source_priority=priority,
        )
        return source

    def create_asset(self, source, suffix):
        asset = ImportedPrintAsset.objects.create(
            source=source, source_url=f"{source.base_url}model/{suffix}", title=f"Model {suffix}"
        )
        CatalogAssetMetrics.objects.create(asset=asset, source_kind=source.sync_policy.source_kind)
        return asset

    def test_source_disable_hides_normal_asset_but_keeps_archive(self):
        source = self.create_source("printables-p29", "printables", 30)
        normal = self.create_asset(source, "normal")
        archived = self.create_asset(source, "archived")
        archived.archive_status = "archived"
        archived.save(update_fields=["archive_status", "keep_public_when_source_disabled", "updated_at"])
        source.is_active = False
        source.save(update_fields=["is_active"])
        archived.refresh_from_db()
        self.assertFalse(public_catalog_queryset().filter(pk=normal.pk).exists())
        self.assertTrue(public_catalog_queryset().filter(pk=archived.pk).exists())
        self.assertNotEqual(archived.public_display_mode, "hidden")

    def test_makerworld_priority_precedes_printables_for_historical_queryset(self):
        printables = self.create_source("printables-order", "printables", 30)
        makerworld = self.create_source("makerworld-order", "makerworld", 10)
        print_asset = self.create_asset(printables, "newer")
        maker_asset = self.create_asset(makerworld, "preferred")
        ids = list(public_catalog_queryset().filter(pk__in=[print_asset.pk, maker_asset.pk]).values_list("pk", flat=True))
        self.assertEqual(ids[0], maker_asset.pk)
