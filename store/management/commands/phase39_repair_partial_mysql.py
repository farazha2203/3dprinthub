from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder


MIGRATIONS = {
    "0026_phase39_smart_commerce_engine",
    "0027_phase39_variant_color_fk",
}

PRICING_COLUMNS = [
    "vat_enabled",
    "assembly_hourly_rate",
    "default_margin_percent",
]
PRODUCT_COLUMNS = [
    "editorial_source_url",
    "source_attribution",
    "hashtags",
    "material_selection_intro",
    "show_public_order_count",
    "customer_gallery_enabled",
]


def qn(name: str) -> str:
    return connection.ops.quote_name(name)


def table_names() -> set[str]:
    with connection.cursor() as cursor:
        return set(connection.introspection.table_names(cursor))


def column_names(table: str) -> set[str]:
    if table not in table_names():
        return set()
    with connection.cursor() as cursor:
        return {col.name for col in connection.introspection.get_table_description(cursor, table)}


def fk_names(table: str, column: str) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT CONSTRAINT_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = %s
              AND COLUMN_NAME = %s
              AND REFERENCED_TABLE_NAME IS NOT NULL
            """,
            [table, column],
        )
        return [row[0] for row in cursor.fetchall()]


def index_names(table: str, column: str) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT INDEX_NAME
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = %s
              AND COLUMN_NAME = %s
              AND INDEX_NAME <> 'PRIMARY'
            """,
            [table, column],
        )
        return [row[0] for row in cursor.fetchall()]


class Command(BaseCommand):
    help = "Inspect or safely remove the partial MySQL schema left by failed Phase39 migration 0026."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Apply cleanup. Without this flag the command is read-only.")

    def handle(self, *args, **options):
        if connection.vendor != "mysql":
            raise CommandError(f"This repair command is MySQL-only. Current vendor={connection.vendor}")

        applied = set(
            MigrationRecorder(connection).migration_qs.filter(app="store", name__in=MIGRATIONS).values_list("name", flat=True)
        )
        self.stdout.write(f"PHASE39_REPAIR_DB={connection.settings_dict.get('NAME')}")
        self.stdout.write(f"PHASE39_REPAIR_APPLIED={','.join(sorted(applied)) or 'none'}")
        if applied:
            raise CommandError("Phase39 migration is already recorded as applied; refusing partial cleanup.")

        tables = table_names()
        pricing_cols = column_names("store_pricingsetting")
        product_cols = column_names("store_product")
        variant_cols = column_names("store_productvariant")
        material_color_exists = "store_materialcoloroption" in tables

        found = {
            "pricing": [c for c in PRICING_COLUMNS if c in pricing_cols],
            "product": [c for c in PRODUCT_COLUMNS if c in product_cols],
            "variant_color_id": "color_id" in variant_cols,
            "material_color_table": material_color_exists,
        }
        self.stdout.write(f"PHASE39_PARTIAL_PRICING={','.join(found['pricing']) or 'none'}")
        self.stdout.write(f"PHASE39_PARTIAL_PRODUCT={','.join(found['product']) or 'none'}")
        self.stdout.write(f"PHASE39_PARTIAL_VARIANT_COLOR_ID={int(found['variant_color_id'])}")
        self.stdout.write(f"PHASE39_PARTIAL_MATERIAL_COLOR_TABLE={int(found['material_color_table'])}")

        any_found = bool(found["pricing"] or found["product"] or found["variant_color_id"] or found["material_color_table"])
        if not options["apply"]:
            self.stdout.write("PHASE39_REPAIR_MODE=INSPECT_ONLY")
            self.stdout.write("PHASE39_REPAIR_PARTIAL_FOUND=" + ("1" if any_found else "0"))
            return

        if not any_found:
            self.stdout.write("PHASE39_REPAIR_NOTHING_TO_CLEAN=1")
            self.stdout.write("PHASE39_REPAIR=OK")
            return

        with connection.cursor() as cursor:
            if found["variant_color_id"]:
                for fk in fk_names("store_productvariant", "color_id"):
                    self.stdout.write(f"DROP_FK store_productvariant.{fk}")
                    cursor.execute(f"ALTER TABLE {qn('store_productvariant')} DROP FOREIGN KEY {qn(fk)}")
                # Drop non-primary indexes that only exist for the failed color relation when possible.
                for idx in index_names("store_productvariant", "color_id"):
                    try:
                        self.stdout.write(f"DROP_INDEX store_productvariant.{idx}")
                        cursor.execute(f"ALTER TABLE {qn('store_productvariant')} DROP INDEX {qn(idx)}")
                    except Exception:
                        pass
                self.stdout.write("DROP_COLUMN store_productvariant.color_id")
                cursor.execute(f"ALTER TABLE {qn('store_productvariant')} DROP COLUMN {qn('color_id')}")

            if found["material_color_table"]:
                self.stdout.write("DROP_TABLE store_materialcoloroption")
                cursor.execute(f"DROP TABLE {qn('store_materialcoloroption')}")

            for col in found["product"]:
                self.stdout.write(f"DROP_COLUMN store_product.{col}")
                cursor.execute(f"ALTER TABLE {qn('store_product')} DROP COLUMN {qn(col)}")

            for col in found["pricing"]:
                self.stdout.write(f"DROP_COLUMN store_pricingsetting.{col}")
                cursor.execute(f"ALTER TABLE {qn('store_pricingsetting')} DROP COLUMN {qn(col)}")

        self.stdout.write("PHASE39_REPAIR=OK")
