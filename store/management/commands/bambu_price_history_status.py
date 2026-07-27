from django.core.management.base import BaseCommand

from store.models import BambuFilamentCatalogItem, BambuFilamentPriceHistory


class Command(BaseCommand):
    help = "نمایش خلاصه کاتالوگ فعلی و تاریخچه قیمت Bambu Lab"

    def handle(self, *args, **options):
        self.stdout.write(f"محصول فعال Bambu: {BambuFilamentCatalogItem.objects.filter(is_active=True).count()}")
        self.stdout.write(f"کل Snapshotهای قیمت: {BambuFilamentPriceHistory.objects.count()}")
        self.stdout.write(f"تغییر قیمت ثبت‌شده: {BambuFilamentPriceHistory.objects.filter(changed=True).count()}")
        latest = BambuFilamentPriceHistory.objects.select_related("item").order_by("-observed_at", "-id")[:10]
        for row in latest:
            previous = row.previous_conservative_price_usd
            previous_text = f"${previous:,.2f}" if previous is not None else "-"
            self.stdout.write(
                f"{row.item.title}: {previous_text} -> ${row.conservative_price_usd:,.2f} "
                f"({row.delta_percent:,.2f}%) @ {row.observed_at}"
            )
