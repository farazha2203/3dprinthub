from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import connection


TABLES = (
    "store_materialcoloroption",
    "store_productmaterialrecommendation",
    "store_accessorycomponent",
    "store_productbomitem",
    "store_productpromotion",
    "store_productreviewimage",
    "store_shippingraterule",
    "store_productvariant",
    "website_material",
    "store_product",
    "store_productreview",
    "store_shippingmethod",
)

FK_EXPECTATIONS = (
    ("store_materialcoloroption", "material_id", "website_material"),
    ("store_productmaterialrecommendation", "material_id", "website_material"),
    ("store_productmaterialrecommendation", "product_id", "store_product"),
    ("store_productbomitem", "component_id", "store_accessorycomponent"),
    ("store_productbomitem", "product_id", "store_product"),
    ("store_productpromotion", "product_id", "store_product"),
    ("store_productreviewimage", "review_id", "store_productreview"),
    ("store_shippingraterule", "shipping_method_id", "store_shippingmethod"),
)


class Command(BaseCommand):
    help = "Read-only Phase39 MySQL engine and FK audit."

    def handle(self, *args, **options):
        if connection.vendor != "mysql":
            raise CommandError(f"MySQL-only audit. Current vendor={connection.vendor}")

        with connection.cursor() as cursor:
            cursor.execute("SELECT @@session.default_storage_engine")
            self.stdout.write(f"PHASE39_MYSQL_SESSION_DEFAULT_ENGINE={cursor.fetchone()[0]}")
            cursor.execute("SELECT @@global.default_storage_engine")
            self.stdout.write(f"PHASE39_MYSQL_GLOBAL_DEFAULT_ENGINE={cursor.fetchone()[0]}")

            all_innodb = True
            for table in TABLES:
                cursor.execute(
                    "SELECT ENGINE, TABLE_COLLATION FROM information_schema.TABLES "
                    "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s",
                    [table],
                )
                row = cursor.fetchone()
                if not row:
                    self.stdout.write(f"ENGINE {table}=MISSING")
                    all_innodb = False
                    continue
                engine, collation = row
                self.stdout.write(f"ENGINE {table}={engine} COLLATION={collation}")
                if engine.lower() != "innodb":
                    all_innodb = False

            missing_fk = []
            for child, column, parent in FK_EXPECTATIONS:
                cursor.execute(
                    """
                    SELECT CONSTRAINT_NAME
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s
                      AND REFERENCED_TABLE_NAME=%s
                    LIMIT 1
                    """,
                    [child, column, parent],
                )
                row = cursor.fetchone()
                label = f"{child}.{column}->{parent}"
                if row:
                    self.stdout.write(f"FK {label}=OK ({row[0]})")
                else:
                    self.stdout.write(f"FK {label}=MISSING")
                    missing_fk.append(label)

        self.stdout.write(f"PHASE39_MYSQL_ALL_INNODB={int(all_innodb)}")
        self.stdout.write(f"PHASE39_MYSQL_MISSING_FK_COUNT={len(missing_fk)}")
        self.stdout.write("PHASE39_MYSQL_ENGINE_AUDIT=OK")
