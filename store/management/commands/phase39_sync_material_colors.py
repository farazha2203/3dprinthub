from django.core.management.base import BaseCommand
from django.db.models import Max

from store.models import FilamentSpool
from store.phase39_models import MaterialColorOption


class Command(BaseCommand):
    help = "Create/update storefront material color options from actual filament spool inventory."

    def handle(self, *args, **options):
        created = updated = skipped = 0
        rows = (
            FilamentSpool.objects.exclude(status__in=["empty", "archived", "quarantine"])
            .exclude(color_name="")
            .values("material_id", "color_name")
            .annotate(last_sale=Max("sale_price_per_gram_snapshot"))
            .order_by("material_id", "color_name")
        )
        for row in rows:
            sample = (
                FilamentSpool.objects.filter(material_id=row["material_id"], color_name=row["color_name"])
                .order_by("-updated_at", "-id")
                .first()
            )
            if not sample:
                skipped += 1
                continue
            code = "-".join(filter(None, [str(sample.material_id), row["color_name"].strip().lower().replace(" ", "-")]))[:120]
            obj, is_created = MaterialColorOption.objects.get_or_create(
                material_id=row["material_id"], code=code,
                defaults={"name": row["color_name"], "hex_code": sample.color_hex or ""},
            )
            changed = False
            if obj.name != row["color_name"]:
                obj.name = row["color_name"]; changed = True
            if sample.color_hex and obj.hex_code != sample.color_hex:
                obj.hex_code = sample.color_hex; changed = True
            if row["last_sale"] and not obj.sale_price_per_gram_override:
                obj.sale_price_per_gram_override = row["last_sale"]; changed = True
            if changed:
                obj.save(); updated += 1
            if is_created:
                created += 1
        self.stdout.write(f"PHASE39_MATERIAL_COLORS_CREATED={created}")
        self.stdout.write(f"PHASE39_MATERIAL_COLORS_UPDATED={updated}")
        self.stdout.write(f"PHASE39_MATERIAL_COLORS_SKIPPED={skipped}")
        self.stdout.write("PHASE39_MATERIAL_COLOR_SYNC=OK")
