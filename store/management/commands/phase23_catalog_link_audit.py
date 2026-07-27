from django.core.management.base import BaseCommand
from django.db.models import Q

from store.catalog_sync import public_catalog_queryset
from store.models import (
    CatalogRefreshRequest,
    CatalogSourcePolicy,
    CustomerLinkAnalysis,
    ImportedPrintAsset,
)


class Command(BaseCommand):
    help = "گزارش سلامت نمایش کاتالوگ مرجع و سامانه تحلیل لینک مشتری."

    def handle(self, *args, **options):
        public_qs = public_catalog_queryset()
        all_assets = ImportedPrintAsset.objects.select_related("source")
        missing_image = public_qs.filter(
            Q(preview_image__isnull=True) | Q(preview_image=""),
            remote_image_url="",
            metrics__image_urls=[],
        ).count()
        missing_title = all_assets.filter(Q(title="") | Q(title__isnull=True)).count()
        hidden_policies = CatalogSourcePolicy.objects.filter(
            is_active=True,
            public_reference_enabled=False,
        ).count()

        rows = {
            "assets_total": all_assets.count(),
            "assets_public_reference": public_qs.count(),
            "assets_missing_title": missing_title,
            "assets_without_any_image": missing_image,
            "active_sources_hidden_from_reference": hidden_policies,
            "refresh_pending": CatalogRefreshRequest.objects.filter(status="pending").count(),
            "refresh_failed": CatalogRefreshRequest.objects.filter(status="failed").count(),
            "link_analysis_total": CustomerLinkAnalysis.objects.count(),
            "link_analysis_ready": CustomerLinkAnalysis.objects.filter(status="ready").count(),
            "link_analysis_needs_input": CustomerLinkAnalysis.objects.filter(status="needs_input").count(),
            "link_analysis_failed": CustomerLinkAnalysis.objects.filter(status="failed").count(),
            "link_analysis_converted": CustomerLinkAnalysis.objects.filter(status="converted").count(),
        }
        for key, value in rows.items():
            self.stdout.write(f"{key}={value}")

        if missing_title:
            self.stderr.write(self.style.ERROR("Some imported assets have no title."))
        if hidden_policies:
            self.stderr.write(self.style.WARNING("Some active sources are explicitly hidden from public reference display."))
        self.stdout.write(self.style.SUCCESS("Phase 23 audit completed."))
