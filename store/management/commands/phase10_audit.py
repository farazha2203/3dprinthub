from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

from store.models import (
    CatalogAssetPublication,
    CatalogSourceSchedule,
    ExchangeRateProvider,
    MarketPricingSetting,
)
from website.models import CustomerReusableModel, Material


class Command(BaseCommand):
    help = "ممیزی زمان‌بندی، انتشار عمومی، فایل‌های خصوصی و قیمت متریال فاز ۱۰."

    def handle(self, *args, **options):
        errors = []
        for publication in CatalogAssetPublication.objects.select_related("metrics", "metrics__asset"):
            metrics = publication.metrics
            if publication.show_on_homepage and not metrics.may_be_public:
                errors.append(f"Homepage asset is not public-safe: {metrics.asset_id}")
            if publication.show_on_homepage and not metrics.asset.preview_image:
                errors.append(f"Homepage asset has no local image: {metrics.asset_id}")
        for schedule in CatalogSourceSchedule.objects.filter(enabled=True):
            if not schedule.active_weekdays():
                errors.append(f"Schedule has no valid weekdays: {schedule.pk}")
        for material in Material.objects.filter(market_pricing_enabled=True):
            if not material.bambu_product_url:
                errors.append(f"Market-priced material has no Bambu URL: {material.name}")
        for model in CustomerReusableModel.objects.exclude(model_file=""):
            try:
                model.model_file.url
                errors.append(f"Private model unexpectedly has public URL: {model.pk}")
            except Exception:
                pass
        setting = MarketPricingSetting.load()
        if setting.enabled and not ExchangeRateProvider.objects.filter(is_active=True).exists():
            errors.append("Market pricing enabled but no active FX provider exists.")
        if errors:
            for error in errors:
                self.stderr.write(error)
            raise CommandError(f"Phase 10 audit failed with {len(errors)} issue(s).")
        self.stdout.write(self.style.SUCCESS("سلامت اتوماسیون، انتشار، فایل خصوصی و قیمت‌گذاری فاز ۱۰ تأیید شد."))
