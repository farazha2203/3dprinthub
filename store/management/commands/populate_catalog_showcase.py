from django.core.management.base import BaseCommand, CommandError

from store.catalog_population import catalog_population_counts, populate_ready_catalog
from store.catalog_preview import refresh_assets
from store.models import ImportedPrintAsset


class Command(BaseCommand):
    help = "دریافت مدل‌های محبوب، سپس ذخیره تصاویر، توضیحات و وزن‌ها برای پیش‌نمایش ادمین و سایت"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--publish-limit", type=int, default=80)
        parser.add_argument("--preview-limit", type=int, default=200)
        parser.add_argument("--max-images", type=int, default=20)
        parser.add_argument("--delay-ms", type=int, default=None)

    def handle(self, *args, **options):
        try:
            population = populate_ready_catalog(
                limit_per_source=max(1, options["limit"]),
                publish_limit_per_source=max(1, options["publish_limit"]),
                delay_ms=options["delay_ms"],
            )
        except Exception as exc:
            raise CommandError(f"دریافت فهرست مدل‌ها ناموفق بود: {exc}") from exc

        for row in population:
            self.stdout.write(self.style.SUCCESS(
                f"{row.source_key}: کشف={row.discovered}، جدید={row.imported}، "
                f"بروزرسانی={row.updated}، مجاز={row.allowed}، منتشر={row.published}"
            ))

        queryset = ImportedPrintAsset.objects.select_related("source").filter(
            metrics__source_kind__in=("makerworld", "printables")
        ).order_by(
            "-metrics__views_count",
            "-metrics__downloads_count",
            "-metrics__likes_count",
            "id",
        )[: max(1, options["preview_limit"])]
        results, errors = refresh_assets(
            queryset,
            download_images=True,
            max_images=max(1, min(20, options["max_images"])),
        )
        self.stdout.write(self.style.SUCCESS(
            f"پیش‌نمایش‌ها: مدل={len(results)}، تصویر محلی={sum(x.images_downloaded for x in results)}، "
            f"پروفایل وزن={sum(x.profiles_found for x in results)}، خطا={len(errors)}"
        ))
        for error in errors[:20]:
            self.stderr.write(self.style.WARNING(error))
        self.stdout.write(self.style.SUCCESS(str(catalog_population_counts())))
