from django.core.management.base import BaseCommand, CommandError

from store.models import (
    BambuFilamentCatalogItem,
    ExchangeRateProvider,
    ExchangeRateSnapshot,
    ExternalSourceFetchLog,
    MarketPricingSetting,
)


class Command(BaseCommand):
    help = "ممیزی تنظیمات TGJU، Bambu Lab و لاگ تست منابع فاز ۱۱."

    def handle(self, *args, **options):
        errors = []
        setting = MarketPricingSetting.load()
        provider = ExchangeRateProvider.objects.filter(code="tgju-dollar").first()
        if not provider or provider.provider_type != "tgju_html" or not provider.is_active:
            errors.append("منبع فعال TGJU تنظیم نشده است.")
        if "tgju.org/profile/price_dollar_rl" not in setting.tgju_profile_url:
            errors.append("آدرس TGJU صحیح نیست.")
        if "us.store.bambulab.com/collections/" not in setting.bambu_collection_url:
            errors.append("آدرس مجموعه Bambu صحیح نیست.")
        if ExchangeRateSnapshot.objects.exists():
            current = ExchangeRateSnapshot.objects.order_by("-observed_at", "-id").first()
            if current.sell_rate_toman <= 0:
                errors.append("آخرین نرخ دلار نامعتبر است.")
        failed = ExternalSourceFetchLog.objects.filter(status="failed").count()
        self.stdout.write(f"Bambu catalog items: {BambuFilamentCatalogItem.objects.filter(is_active=True).count()}")
        self.stdout.write(f"Source logs: {ExternalSourceFetchLog.objects.count()} failed={failed}")
        if errors:
            for error in errors:
                self.stderr.write(error)
            raise CommandError("ممیزی فاز ۱۱ ناموفق بود.")
        self.stdout.write(self.style.SUCCESS("تنظیمات پایه فاز ۱۱ سالم است."))
