from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from store.catalog_sync import sync_catalog_source
from store.models import PrintCatalogSource


class Command(BaseCommand):
    help = "دریافت فایل‌های محبوب از MakerWorld، Printables، Thingiverse و GrabCAD"

    def add_arguments(self, parser):
        parser.add_argument("--source", help="کد منبع؛ مانند makerworld یا printables")
        parser.add_argument("--all", action="store_true", help="اجرای همه منابع فعال")
        parser.add_argument("--limit", type=int, help="تعداد مدل؛ مقدار پیش‌فرض از تنظیمات منبع")
        parser.add_argument(
            "--sort",
            default="downloads",
            choices=["downloads", "likes", "views", "trending", "newest"],
        )
        parser.add_argument("--hydrate-files", action="store_true", help="دریافت جزئیات فایل‌ها در منابع مجاز")

    def handle(self, *args, **options):
        if not options["all"] and not options["source"]:
            raise CommandError("یکی از --source یا --all الزامی است.")
        queryset = PrintCatalogSource.objects.filter(is_active=True, sync_policy__is_active=True)
        if options["source"]:
            queryset = queryset.filter(code=options["source"])
        sources = list(queryset.select_related("sync_policy"))
        if not sources:
            raise CommandError("منبع فعالی با این مشخصات پیدا نشد.")

        failed = 0
        for source in sources:
            self.stdout.write(self.style.NOTICE(f"شروع {source.name}..."))
            run = sync_catalog_source(
                source=source,
                requested_limit=options["limit"],
                sort_mode=options["sort"],
                hydrate_files=options["hydrate_files"],
            )
            self.stdout.write(
                f"وضعیت={run.status} کشف={run.discovered_count} "
                f"ثبت={run.imported_count} خطا={run.failed_count}"
            )
            if run.status == "failed":
                failed += 1
                self.stderr.write(run.log)
        if failed:
            raise CommandError(f"{failed} منبع ناموفق بود.")
        self.stdout.write(self.style.SUCCESS("همگام‌سازی منابع تکمیل شد."))
