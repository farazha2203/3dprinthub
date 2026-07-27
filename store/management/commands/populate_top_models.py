from django.core.management.base import BaseCommand, CommandError

from store.catalog_population import catalog_population_counts, populate_ready_catalog


class Command(BaseCommand):
    help = "دریافت مدل‌های پربازدید، پردانلود، پرلایک و ترند MakerWorld و Printables"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--publish-limit", type=int, default=80)
        parser.add_argument("--delay-ms", type=int, default=None)

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            "اولویت دریافت: پربازدیدترین، پردانلودترین، پرلایک‌ترین، سپس ترند."
        ))
        try:
            results = populate_ready_catalog(
                limit_per_source=max(1, options["limit"]),
                publish_limit_per_source=max(1, options["publish_limit"]),
                delay_ms=options["delay_ms"],
            )
        except Exception as exc:
            raise CommandError(str(exc)) from exc
        for result in results:
            style = self.style.SUCCESS if result.published else self.style.WARNING
            self.stdout.write(style(
                f"{result.source_key}: کشف={result.discovered}، جدید={result.imported}، "
                f"بروزرسانی={result.updated}، مجاز={result.allowed}، منتشر={result.published}"
            ))
        self.stdout.write(self.style.SUCCESS(str(catalog_population_counts())))
