from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from store.finance_reconciliation import collect_finance_reconciliation


class Command(BaseCommand):
    help = (
        "Read-only reconciliation of Store payments, Website payment ledger, "
        "ProductionJob finance authority and manual-receipt reviewer evidence."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-storage-check",
            action="store_true",
            help="Validate receipt references without probing receipt storage.",
        )
        parser.add_argument(
            "--strict-warnings",
            action="store_true",
            help="Treat reconciliation warnings as a failed gate.",
        )

    def handle(self, *args, **options):
        result = collect_finance_reconciliation(
            check_storage=not options["skip_storage_check"],
        )

        for key, value in sorted(result["metrics"].items()):
            self.stdout.write(f"{key}={value}")
        for key, value in sorted(result["warnings"].items()):
            self.stdout.write(self.style.WARNING(f"WARNING:{key}={value}"))
        for key, value in sorted(result["failures"].items()):
            self.stdout.write(self.style.ERROR(f"FAIL:{key}={value}"))

        if result["failures"]:
            self.stdout.write("PHASE50_FINANCE_RECONCILIATION=FAIL")
            raise CommandError("Finance reconciliation found integrity failures.")
        if options["strict_warnings"] and result["warnings"]:
            self.stdout.write("PHASE50_FINANCE_RECONCILIATION=WARN")
            raise CommandError("Finance reconciliation found warnings in strict mode.")

        self.stdout.write(self.style.SUCCESS("PHASE50_FINANCE_RECONCILIATION=OK"))
