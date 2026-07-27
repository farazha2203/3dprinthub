from django.core.management.base import BaseCommand

from store.market_pricing import refresh_fx_rates, refresh_material_market_prices


class Command(BaseCommand):
    help = "دریافت نرخ دلار، نگهداری بیشترین نرخ روز و بروزرسانی قیمت متریال‌های متصل به Bambu Lab."

    def add_arguments(self, parser):
        parser.add_argument("--fx-only", action="store_true")
        parser.add_argument("--no-bambu", action="store_true")

    def handle(self, *args, **options):
        rates = refresh_fx_rates()
        self.stdout.write(f"FX snapshots: {len(rates)}")
        if options["fx_only"]:
            return
        snapshots, errors = refresh_material_market_prices(refresh_bambu=not options["no_bambu"])
        self.stdout.write(self.style.SUCCESS(f"Material prices: {len(snapshots)}"))
        for error in errors:
            self.stderr.write(error)
