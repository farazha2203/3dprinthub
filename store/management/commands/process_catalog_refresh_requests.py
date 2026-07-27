from django.core.management.base import BaseCommand

from store.link_intelligence import process_catalog_refresh_requests


class Command(BaseCommand):
    help = "پردازش درخواست‌های بروزرسانی مدل‌های خارجی ثبت‌شده توسط مشتریان."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=5)

    def handle(self, *args, **options):
        processed = process_catalog_refresh_requests(limit=max(int(options["limit"] or 5), 1))
        completed = sum(1 for item in processed if item.status == "completed")
        failed = sum(1 for item in processed if item.status == "failed")
        self.stdout.write(self.style.SUCCESS(f"processed={len(processed)} completed={completed} failed={failed}"))
