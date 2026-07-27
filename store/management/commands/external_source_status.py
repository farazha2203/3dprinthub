from django.core.management.base import BaseCommand

from store.models import CatalogSeedURL, CatalogSourcePolicy, ExternalSourceFetchLog, MarketPricingSetting


class Command(BaseCommand):
    help = "نمایش خلاصه وضعیت عملیاتی منابع خارجی و آخرین گزارش آن‌ها."

    def handle(self, *args, **options):
        setting = MarketPricingSetting.load()
        self.stdout.write(f"Bambu collection: {setting.bambu_collection_url}")
        for key in ["tgju", "bambu", "makerworld", "printables", "thingiverse", "grabcad"]:
            log = ExternalSourceFetchLog.objects.filter(source_key=key).order_by("-created_at", "-id").first()
            if log:
                self.stdout.write(
                    f"{key}: {log.status} | {log.current_stage} | {log.message or log.error or '-'}"
                )
            else:
                self.stdout.write(f"{key}: no log")
        for policy in CatalogSourcePolicy.objects.select_related("source"):
            seeds = CatalogSeedURL.objects.filter(source=policy.source, is_active=True).count()
            self.stdout.write(f"seed {policy.source_kind}: {seeds}")
