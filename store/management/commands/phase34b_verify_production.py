from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db.migrations.recorder import MigrationRecorder

from store.management.commands.phase34b_import_makerworld import (
    resolve_makerworld_source,
)
from store.models import (
    CatalogSourcePolicy,
    ImportedPrintAsset,
    ImportedPrintAssetImage,
    PrintCatalogSource,
)


class Command(BaseCommand):
    help = (
        "Run Phase 34B production checks without creating a Django test "
        "database."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--repair-source",
            action="store_true",
            help="Create or repair the MakerWorld source and policy.",
        )

    def handle(self, *args, **options):
        applied = MigrationRecorder.Migration.objects.filter(
            app="store",
            name="0024_phase34b_makerworld_editorial_commerce",
        ).exists()
        if not applied:
            raise CommandError("Phase 34B migration is not applied.")

        if options["repair_source"]:
            source, policy = resolve_makerworld_source()
        else:
            source = PrintCatalogSource.objects.filter(
                code="makerworld"
            ).first()
            policy = (
                CatalogSourcePolicy.objects.filter(
                    source=source,
                    source_kind="makerworld",
                ).first()
                if source is not None
                else None
            )

        if source is None:
            raise CommandError("MakerWorld source is missing.")
        if not source.is_active:
            raise CommandError("MakerWorld source is inactive.")
        if source.adapter_key != "custom":
            raise CommandError(
                "MakerWorld source adapter_key must be 'custom'."
            )
        if policy is None:
            raise CommandError("MakerWorld source policy is missing.")
        if not policy.is_active:
            raise CommandError("MakerWorld source policy is inactive.")

        print("PHASE34B_MIGRATION_APPLIED=OK")
        print(f"MAKERWORLD_SOURCE_ID={source.pk}")
        print(f"MAKERWORLD_SOURCE_CODE={source.code}")
        print(f"MAKERWORLD_SOURCE_ADAPTER={source.adapter_key}")
        print(f"MAKERWORLD_POLICY_KIND={policy.source_kind}")
        print(
            "IMPORTED_ASSET_COUNT="
            f"{ImportedPrintAsset.objects.count()}"
        )
        print(
            "IMPORTED_IMAGE_COUNT="
            f"{ImportedPrintAssetImage.objects.count()}"
        )
        print("PHASE34B_PRODUCTION_VERIFY=OK")
