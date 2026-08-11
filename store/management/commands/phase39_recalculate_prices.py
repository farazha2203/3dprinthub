from django.core.management.base import BaseCommand

from store.models import ProductVariant


class Command(BaseCommand):
    help = "Recalculate all active product variant prices/cost snapshots after material/BOM/assembly changes."

    def handle(self, *args, **options):
        ok = failed = 0
        for variant in ProductVariant.objects.filter(is_active=True).select_related("product", "material", "quality", "color"):
            try:
                variant.recalculate_price(save=True)
                ok += 1
            except Exception as exc:
                failed += 1
                self.stderr.write(f"FAILED variant={variant.pk}: {type(exc).__name__}: {exc}")
        self.stdout.write(f"PHASE39_VARIANT_PRICES_RECALCULATED={ok}")
        self.stdout.write(f"PHASE39_VARIANT_PRICE_FAILURES={failed}")
        if failed:
            raise RuntimeError(f"{failed} variant price recalculation(s) failed")
        self.stdout.write("PHASE39_PRICE_RECALC=OK")
