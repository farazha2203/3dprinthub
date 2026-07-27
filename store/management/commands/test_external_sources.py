from django.core.management.base import BaseCommand, CommandError

from store.market_pricing import test_bambu_collection, test_exchange_provider
from store.models import CatalogSourcePolicy, ExchangeRateProvider
from store.source_probes import EXPECTED_SOURCE_STATES, test_catalog_source


class Command(BaseCommand):
    help = "تست اتصال و پارسر منابع؛ وضعیت‌های نیازمند توکن یا مسدود توسط منبع به‌صورت هشدار گزارش می‌شوند."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            choices=["all", "tgju", "bambu", "makerworld", "printables", "thingiverse", "grabcad"],
            default="all",
        )

    def handle(self, *args, **options):
        source = options["source"]
        failures = []
        warnings = []

        if source in {"all", "tgju"}:
            provider = ExchangeRateProvider.objects.filter(code="tgju-dollar").first()
            if not provider:
                failures.append("TGJU: provider not found")
            else:
                try:
                    rate, payload, log = test_exchange_provider(provider)
                    self.stdout.write(self.style.SUCCESS(
                        f"TGJU OK current={rate} daily_high={payload.get('daily_high_toman')} log={log.pk}"
                    ))
                except Exception as exc:
                    failures.append(f"TGJU: {exc}")

        if source in {"all", "bambu"}:
            try:
                records, meta, log = test_bambu_collection()
                self.stdout.write(self.style.SUCCESS(
                    f"Bambu OK products={len(records)} mode={meta.get('mode')} collection={meta.get('collection_url')} log={log.pk}"
                ))
            except Exception as exc:
                failures.append(f"Bambu: {exc}")

        catalog_sources = {"makerworld", "printables", "thingiverse", "grabcad"}
        selected = catalog_sources if source == "all" else ({source} if source in catalog_sources else set())
        for key in sorted(selected):
            policy = CatalogSourcePolicy.objects.select_related("source").filter(source_kind=key, is_active=True).first()
            if not policy:
                failures.append(f"{key}: policy not found")
                continue
            try:
                record, log = test_catalog_source(policy)
                status = record.get("_probe_status", "success")
                if status in EXPECTED_SOURCE_STATES:
                    message = f"{key} WARNING state={status}: {record.get('title')} log={log.pk}"
                    warnings.append(message)
                    self.stdout.write(self.style.WARNING(message))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f"{key} OK title={record.get('title')} log={log.pk}"
                    ))
            except Exception as exc:
                failures.append(f"{key}: {exc}")

        for failure in failures:
            self.stderr.write(self.style.ERROR(failure))
        if warnings:
            self.stdout.write(self.style.WARNING(f"{len(warnings)} source(s) need configuration or manual seed URLs."))
        if failures:
            raise CommandError(f"{len(failures)} unexpected source test(s) failed")
