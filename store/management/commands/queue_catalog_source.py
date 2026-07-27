from django.core.management.base import BaseCommand, CommandError

from store.catalog_automation import queue_catalog_source
from store.models import CatalogSourceSchedule


class Command(BaseCommand):
    help = "قرار دادن یک منبع یا همه منابع فعال در صف دریافت."

    def add_arguments(self, parser):
        parser.add_argument("--source", help="کد منبع مانند printables؛ اگر حذف شود همه زمان‌بندی‌های فعال صف می‌شوند.")

    def handle(self, *args, **options):
        qs = CatalogSourceSchedule.objects.select_related("policy", "policy__source")
        if options.get("source"):
            qs = qs.filter(policy__source__code=options["source"])
        else:
            qs = qs.filter(enabled=True)
        if not qs.exists():
            raise CommandError("زمان‌بندی منبع پیدا نشد.")
        count = 0
        for schedule in qs:
            try:
                run = queue_catalog_source(schedule=schedule, trigger="command")
            except Exception as exc:
                self.stderr.write(f"{schedule.policy.source.name}: {exc}")
                continue
            count += 1
            self.stdout.write(f"Queued {schedule.policy.source.name}, run={run.pk}")
        self.stdout.write(self.style.SUCCESS(f"Queued {count} source(s)."))
