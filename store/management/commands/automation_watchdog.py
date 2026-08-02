from django.core.management.base import BaseCommand

from store.automation_watchdog import expire_stale_automation


class Command(BaseCommand):
    help = "Detect and finalize stale automation logs and catalog sync runs."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        summary = expire_stale_automation(dry_run=options["dry_run"])
        for key in sorted(summary):
            self.stdout.write(f"{key}={summary[key]}")
        if options["dry_run"]:
            self.stdout.write("AUTOMATION_WATCHDOG_DRY_RUN=OK")
        else:
            self.stdout.write("AUTOMATION_WATCHDOG=OK")
