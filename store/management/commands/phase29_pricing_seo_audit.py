from django.core.management.base import BaseCommand
from django.db.models import Q

from store.catalog_sync import public_catalog_queryset
from store.models import CatalogPricingReview, CustomerLinkAnalysis, ImportedPrintAsset, LinkAnalysisManualReview


class Command(BaseCommand):
    help = "Audit verified pricing, operator queues, source retention and catalog SEO state."

    def handle(self, *args, **options):
        false_prices = CustomerLinkAnalysis.objects.filter(estimated_price__gt=0).exclude(
            Q(technical_specs__weight_source_kind__in=["source_explicit", "source_profile", "operator_verified"])
            & Q(technical_specs__print_time_source_kind__in=["source_explicit", "source_profile", "operator_verified"])
        ).count()
        missing_reviews = ImportedPrintAsset.objects.filter(pricing_review__isnull=True).count()
        pending_catalog = CatalogPricingReview.objects.filter(status="pending").count()
        verified_catalog = CatalogPricingReview.objects.filter(status="verified").count()
        open_customer = LinkAnalysisManualReview.objects.filter(status__in=["pending", "in_progress"]).count()
        hidden_source_but_public = public_catalog_queryset().filter(
            source__is_active=False,
            keep_public_when_source_disabled=False,
            archive_status="none",
            archived_model_file__isnull=True,
        ).exclude(
            Q(product__model_file__isnull=False) & ~Q(product__model_file="")
        ).count()
        public_without_image = public_catalog_queryset().filter(
            Q(preview_image__isnull=True) | Q(preview_image=""), remote_image_url=""
        ).count()

        checks = {
            "false_automatic_prices": false_prices,
            "catalog_assets_without_operator_review": missing_reviews,
            "disabled_source_assets_leaking_publicly": hidden_source_but_public,
        }
        for key, count in checks.items():
            style = self.style.SUCCESS if count == 0 else self.style.ERROR
            self.stdout.write(style(f"{key}: {count}"))
        self.stdout.write(f"pending_catalog_reviews: {pending_catalog}")
        self.stdout.write(f"verified_catalog_reviews: {verified_catalog}")
        self.stdout.write(f"open_customer_reviews: {open_customer}")
        self.stdout.write(f"public_pages_without_image: {public_without_image}")
        if any(checks.values()):
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS("PHASE29_AUDIT=OK"))
