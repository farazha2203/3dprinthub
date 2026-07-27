from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from store.models import CatalogAssetMetrics


class Command(BaseCommand):
    help = "بررسی عدم انتشار فایل بدون مجوز تجاری معتبر"

    def handle(self, *args, **options):
        invalid = CatalogAssetMetrics.objects.filter(public_approved=True).filter(
            Q(commercial_use_allowed__isnull=True)
            | Q(commercial_use_allowed=False)
            | ~Q(license_review_status="allowed")
            | Q(source_kind="grabcad")
        )
        if invalid.exists():
            for item in invalid.select_related("asset")[:100]:
                self.stderr.write(f"{item.asset_id}: {item.asset.title} [{item.source_kind}]")
            raise CommandError(f"{invalid.count()} فایل با وضعیت انتشار نامعتبر پیدا شد.")
        self.stdout.write(self.style.SUCCESS("سلامت مجوز و انتشار کاتالوگ خارجی تأیید شد."))
