from django.core.management.base import BaseCommand

from store.catalog_automation import process_catalog_queue


class Command(BaseCommand):
    help = "پردازش Jobهای صف دریافت کاتالوگ."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=None)

    def handle(self, *args, **options):
        runs = process_catalog_queue(limit=options["limit"])
        for run in runs:
            self.stdout.write(f"{run.pk}: {run.source.name} -> {run.status} imported={run.imported_count} failed={run.failed_count}")
        self.stdout.write(self.style.SUCCESS(f"Processed {len(runs)} catalog job(s)."))
