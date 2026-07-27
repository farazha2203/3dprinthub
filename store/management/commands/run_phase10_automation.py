from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from store.catalog_automation import process_catalog_queue, queue_due_catalog_sources
from store.link_intelligence import process_catalog_refresh_requests
from store.link_analysis_queue import process_link_analysis_queue
from store.market_pricing import refresh_fx_rates, refresh_material_market_prices
from store.models import MarketPricingSetting
from store.operator_notifications import process_pending_operator_notifications


class Command(BaseCommand):
    help = "صف‌کردن دریافت‌های زمان‌بندی‌شده، پردازش صف و بروزرسانی قیمت بازار. مناسب Cron هر ۵ تا ۱۰ دقیقه."

    def add_arguments(self, parser):
        parser.add_argument("--queue-only", action="store_true")
        parser.add_argument("--process-only", action="store_true")
        parser.add_argument("--skip-prices", action="store_true")
        parser.add_argument("--limit", type=int, default=None)

    def handle(self, *args, **options):
        queued = []
        processed = []
        if not options["process_only"]:
            queued = queue_due_catalog_sources()
        if not options["queue_only"]:
            processed = process_catalog_queue(limit=options["limit"])
        automation_limit = max(int(options.get("limit") or 5), 1)
        refresh_requests = process_catalog_refresh_requests(limit=automation_limit)
        link_jobs = process_link_analysis_queue(limit=automation_limit)
        alerts = process_pending_operator_notifications(limit=automation_limit)
        self.stdout.write(
            f"Catalog queued={len(queued)} processed={len(processed)} "
            f"refresh_requests={len(refresh_requests)} link_jobs={len(link_jobs)} "
            f"operator_alerts={alerts}"
        )

        if options["skip_prices"]:
            return
        setting = MarketPricingSetting.load()
        if not setting.enabled:
            self.stdout.write("Market pricing is disabled.")
            return
        now = timezone.now()
        fx_due = not setting.last_fx_refresh_at or setting.last_fx_refresh_at < now - timedelta(minutes=max(setting.refresh_fx_minutes, 1))
        bambu_due = not setting.last_bambu_refresh_at or setting.last_bambu_refresh_at < now - timedelta(hours=max(setting.refresh_bambu_hours, 1))
        if fx_due:
            rates = refresh_fx_rates(now=now)
            self.stdout.write(f"FX snapshots={len(rates)}")
        if fx_due or bambu_due:
            snapshots, errors = refresh_material_market_prices(refresh_bambu=bambu_due, now=now)
            self.stdout.write(f"Material prices={len(snapshots)} errors={len(errors)}")
            for error in errors[:10]:
                self.stderr.write(error)
