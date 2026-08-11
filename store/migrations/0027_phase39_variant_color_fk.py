from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


PHASE39_NEW_TABLES = (
    "store_materialcoloroption",
    "store_productmaterialrecommendation",
    "store_accessorycomponent",
    "store_productbomitem",
    "store_productpromotion",
    "store_productreviewimage",
    "store_shippingraterule",
)

# Foreign keys that MyISAM accepts syntactically but does not enforce/store.
PHASE39_FOREIGN_KEYS = (
    ("store_materialcoloroption", "material_id", "website_material", "id", "p39_mco_material_fk"),
    ("store_productmaterialrecommendation", "material_id", "website_material", "id", "p39_pmr_material_fk"),
    ("store_productmaterialrecommendation", "product_id", "store_product", "id", "p39_pmr_product_fk"),
    ("store_productbomitem", "component_id", "store_accessorycomponent", "id", "p39_bom_component_fk"),
    ("store_productbomitem", "product_id", "store_product", "id", "p39_bom_product_fk"),
    ("store_productpromotion", "product_id", "store_product", "id", "p39_promo_product_fk"),
    ("store_productreviewimage", "review_id", "store_productreview", "id", "p39_reviewimg_review_fk"),
    ("store_shippingraterule", "shipping_method_id", "store_shippingmethod", "id", "p39_shiprule_method_fk"),
)


def _engine(cursor, table: str):
    cursor.execute(
        """
        SELECT ENGINE
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
        """,
        [table],
    )
    row = cursor.fetchone()
    return row[0] if row else None


def _fk_exists(cursor, table: str, column: str, parent: str) -> bool:
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
          AND REFERENCED_TABLE_NAME = %s
        LIMIT 1
        """,
        [table, column, parent],
    )
    return cursor.fetchone() is not None


def prepare_mysql_phase39_relations(apps, schema_editor):
    """
    Repair Phase39 tables created as MyISAM on shared hosts before adding
    ProductVariant.color. Django doesn't specify a storage engine on CREATE
    TABLE, so a host default of MyISAM can silently discard FK definitions.
    """
    connection = schema_editor.connection
    if connection.vendor != "mysql":
        return

    qn = connection.ops.quote_name
    with connection.cursor() as cursor:
        cursor.execute("SET SESSION default_storage_engine=InnoDB")

        # Existing parents used by Phase39 must support FK relationships.
        parent_tables = {spec[2] for spec in PHASE39_FOREIGN_KEYS} | {"store_productvariant"}
        bad_parents = []
        for table in sorted(parent_tables):
            engine = _engine(cursor, table)
            if engine and engine.lower() != "innodb":
                bad_parents.append(f"{table}={engine}")
        if bad_parents:
            raise RuntimeError(
                "Phase39 cannot create reliable foreign keys because existing parent/child tables "
                "are not InnoDB: " + ", ".join(bad_parents)
            )

        # Tables created by 0026 may have inherited a MyISAM server default.
        for table in PHASE39_NEW_TABLES:
            engine = _engine(cursor, table)
            if engine is None:
                raise RuntimeError(f"Expected Phase39 table is missing: {table}")
            if engine.lower() != "innodb":
                cursor.execute(f"ALTER TABLE {qn(table)} ENGINE=InnoDB")

        # Recreate FK constraints MyISAM discarded during CREATE TABLE.
        for child, column, parent, parent_column, constraint_name in PHASE39_FOREIGN_KEYS:
            if _fk_exists(cursor, child, column, parent):
                continue
            cursor.execute(
                f"ALTER TABLE {qn(child)} "
                f"ADD CONSTRAINT {qn(constraint_name)} "
                f"FOREIGN KEY ({qn(column)}) REFERENCES {qn(parent)} ({qn(parent_column)})"
            )


def noop_reverse(apps, schema_editor):
    # Engine normalization and restored integrity constraints are intentionally
    # retained if this migration is reversed.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0026_phase39_smart_commerce_engine"),
    ]

    operations = [
        migrations.RunPython(prepare_mysql_phase39_relations, noop_reverse),
        migrations.AddField(
            model_name="productvariant",
            name="color",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="variants",
                to="store.materialcoloroption",
                verbose_name="رنگ",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="productvariant",
            name="unique_store_product_material_quality",
        ),
        migrations.AddConstraint(
            model_name="productvariant",
            constraint=models.UniqueConstraint(
                fields=("product", "material", "quality", "color"),
                name="uniq_product_material_quality_color",
            ),
        ),
    ]
