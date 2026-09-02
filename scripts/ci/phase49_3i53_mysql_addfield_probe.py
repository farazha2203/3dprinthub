from __future__ import annotations

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.db import connection, models
from django.db.migrations.state import ModelState, ProjectState

import importlib

migration_0039 = importlib.import_module(
    "store.migrations.0039_phase50_filament_offer_pricing"
)
AddFieldIfMissing = migration_0039.AddFieldIfMissing


TABLE = "phase49_3i53_mysql_probe"


def column_names() -> set[str]:
    with connection.cursor() as cursor:
        description = connection.introspection.get_table_description(cursor, TABLE)
    return {str(item.name) for item in description}


def main() -> int:
    if connection.vendor != "mysql":
        raise SystemExit("MYSQL_ADDFIELD_PROBE=FAIL:vendor")

    with connection.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE}")

    before = ProjectState()
    before.add_model(
        ModelState(
            app_label="probeapp",
            name="Probe",
            fields=[
                ("id", models.BigAutoField(primary_key=True)),
            ],
            options={"db_table": TABLE},
        )
    )

    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(before.apps.get_model("probeapp", "Probe"))

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"ALTER TABLE {TABLE} "
                "ADD COLUMN recovered varchar(32) NOT NULL DEFAULT ''"
            )

        recovered_op = AddFieldIfMissing(
            model_name="probe",
            name="recovered",
            field=models.CharField(max_length=32, default=""),
        )
        recovered_state = before.clone()
        recovered_op.state_forwards("probeapp", recovered_state)

        with connection.schema_editor() as schema_editor:
            recovered_op.database_forwards(
                "probeapp",
                schema_editor,
                before,
                recovered_state,
            )

        columns = column_names()
        if "recovered" not in columns:
            raise SystemExit("MYSQL_ADDFIELD_PROBE=FAIL:existing_column_lost")

        fresh_op = AddFieldIfMissing(
            model_name="probe",
            name="fresh",
            field=models.PositiveBigIntegerField(default=0),
        )
        fresh_state = recovered_state.clone()
        fresh_op.state_forwards("probeapp", fresh_state)

        with connection.schema_editor() as schema_editor:
            fresh_op.database_forwards(
                "probeapp",
                schema_editor,
                recovered_state,
                fresh_state,
            )

        columns = column_names()
        if "fresh" not in columns:
            raise SystemExit("MYSQL_ADDFIELD_PROBE=FAIL:missing_column_not_added")

        print("MYSQL_ADDFIELD_EXISTING_COLUMN_SKIP=PASS")
        print("MYSQL_ADDFIELD_MISSING_COLUMN_ADD=PASS")
        print("MYSQL_ADDFIELD_PROBE=PASS")
        return 0
    finally:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {TABLE}")


if __name__ == "__main__":
    raise SystemExit(main())
