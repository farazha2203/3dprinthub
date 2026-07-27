from django.core.management.base import BaseCommand, CommandError

from store.catalog_population import (
    PUBLIC_SOURCE_KEYS,
    catalog_population_counts,
    populate_ready_catalog,
)


class Command(BaseCommand):
    help = "دریافت واقعی MakerWorld/Printables، ذخیره تصاویر و انتشار مدل‌های دارای مجوز تجاری"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            choices=["all", *PUBLIC_SOURCE_KEYS],
            default="all",
        )
        parser.add_argument("--limit", type=int, default=80)
        parser.add_argument("--publish-limit", type=int, default=60)
        parser.add_argument(
            "--delay-ms",
            type=int,
            default=None,
            help="فاصله درخواست‌ها؛ پیش‌فرض از سیاست منبع",
        )

    def handle(self, *args, **options):
        source_keys = PUBLIC_SOURCE_KEYS if options["source"] == "all" else (options["source"],)
        self.stdout.write(
            self.style.WARNING(
                "این فرمان تست نیست؛ مدل‌ها را واقعاً دریافت و در دیتابیس ذخیره می‌کند."
            )
        )
        try:
            results = populate_ready_catalog(
                source_keys=source_keys,
                limit_per_source=max(1, options["limit"]),
                publish_limit_per_source=max(1, options["publish_limit"]),
                delay_ms=options["delay_ms"],
            )
        except Exception as exc:
            raise CommandError(str(exc)) from exc

        for result in results:
            level = self.style.SUCCESS if result.published else self.style.WARNING
            self.stdout.write(
                level(
                    f"{result.source_key}: کشف={result.discovered}، جدید={result.imported}، "
                    f"بروزرسانی={result.updated}، مجاز={result.allowed}، "
                    f"منتشر={result.published}، تصویر محلی={result.images_cached}، خطا={result.failed}"
                )
            )
            for error in result.errors[-5:]:
                self.stdout.write(self.style.WARNING(f"  - {error}"))

        counts = catalog_population_counts()
        self.stdout.write(self.style.SUCCESS(f"وضعیت نهایی کاتالوگ: {counts}"))
