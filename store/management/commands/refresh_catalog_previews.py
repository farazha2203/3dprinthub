from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from store.catalog_preview import refresh_assets
from store.models import ImportedPrintAsset


class Command(BaseCommand):
    help = "دریافت تصاویر، توضیحات و وزن‌های چاپ مدل‌های ذخیره‌شده بدون دانلود فایل سه‌بعدی"

    def add_arguments(self, parser):
        parser.add_argument("--source", choices=("all", "makerworld", "printables", "thingiverse", "grabcad"), default="all")
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--max-images", type=int, default=20)
        parser.add_argument("--no-download-images", action="store_true")
        parser.add_argument("--only-missing", action="store_true")

    def handle(self, *args, **options):
        queryset = ImportedPrintAsset.objects.select_related("source").all()
        if options["source"] != "all":
            queryset = queryset.filter(metrics__source_kind=options["source"])
        if options["only_missing"]:
            queryset = queryset.filter(Q(preview_image="") | Q(preview_image__isnull=True))
        queryset = queryset.order_by(
            "-metrics__views_count",
            "-metrics__downloads_count",
            "-metrics__likes_count",
            "id",
        )[: max(1, options["limit"])]

        results, errors = refresh_assets(
            queryset,
            download_images=not options["no_download_images"],
            max_images=max(1, min(20, options["max_images"])),
        )
        for result in results:
            self.stdout.write(self.style.SUCCESS(
                f"#{result.asset_id} {result.title}: تصاویر پیدا={result.images_found}، "
                f"دانلود={result.images_downloaded}، وزن/پروفایل={result.profiles_found}"
            ))
        for error in errors:
            self.stderr.write(self.style.ERROR(error))
        self.stdout.write(self.style.SUCCESS(
            f"تکمیل: مدل موفق={len(results)}، خطا={len(errors)}، "
            f"تصویر محلی={sum(row.images_downloaded for row in results)}، "
            f"پروفایل وزن={sum(row.profiles_found for row in results)}"
        ))
        if errors and not results:
            raise CommandError("هیچ مدلی با موفقیت بروزرسانی نشد.")
