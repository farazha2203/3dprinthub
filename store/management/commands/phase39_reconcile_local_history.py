from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder


REQUIRED_TABLES = {
    "store_materialcoloroption",
    "store_productmaterialrecommendation",
    "store_accessorycomponent",
    "store_productbomitem",
    "store_productpromotion",
    "store_productreviewimage",
    "store_shippingraterule",
}


def columns(table: str) -> set[str]:
    with connection.cursor() as cursor:
        if table not in set(connection.introspection.table_names(cursor)):
            return set()
        return {c.name for c in connection.introspection.get_table_description(cursor, table)}


class Command(BaseCommand):
    help = "Reconcile local migration history when old Phase39 0026 already created the final schema before v39.0.3 split."

    def handle(self, *args, **options):
        recorder = MigrationRecorder(connection)
        applied = set(recorder.migration_qs.filter(app="store").values_list("name", flat=True))
        old = "0026_phase39_smart_commerce_engine" in applied
        new = "0027_phase39_variant_color_fk" in applied
        if not old or new:
            self.stdout.write("PHASE39_LOCAL_RECONCILE=NOT_NEEDED")
            return

        with connection.cursor() as cursor:
            tables = set(connection.introspection.table_names(cursor))
        missing_tables = sorted(REQUIRED_TABLES - tables)
        required_columns = {
            "store_productvariant": {"color_id", "cached_cost_price", "material_price_per_gram_override", "color_price_adjustment", "assembly_fee_override"},
            "store_pricingsetting": {"vat_enabled", "assembly_hourly_rate", "default_margin_percent"},
            "store_storeorderitem": {"color_name", "unit_cost_snapshot", "gross_profit", "material_charge_snapshot", "machine_charge_snapshot", "labor_charge_snapshot", "accessory_charge_snapshot", "assembly_charge_snapshot", "color_adjustment_snapshot"},
        }
        missing_columns = []
        for table, needed in required_columns.items():
            have = columns(table)
            for name in sorted(needed - have):
                missing_columns.append(f"{table}.{name}")
        if missing_tables or missing_columns:
            raise CommandError(
                "Refusing to reconcile migration history because final Phase39 schema is incomplete. "
                f"missing_tables={missing_tables} missing_columns={missing_columns}"
            )
        recorder.record_applied("store", "0027_phase39_variant_color_fk")
        self.stdout.write("PHASE39_LOCAL_RECONCILE=RECORDED_0027")
