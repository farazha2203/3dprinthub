from django.core.management.base import BaseCommand

from store.link_analysis_operations import health_payload, mark_stale_workers, queue_metrics


class Command(BaseCommand):
    help = "نمایش سلامت Workerها و صف تحلیل لینک."

    def add_arguments(self, parser):
        parser.add_argument("--json", action="store_true", help="خروجی JSON")

    def handle(self, *args, **options):
        import json

        mark_stale_workers()
        payload, code = health_payload()
        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(f"status={payload['status']} active_workers={payload['active_workers']}")
            self.stdout.write(
                f"queued={payload['queued']} running={payload['running']} retry={payload['retry']} failed={payload['failed']}"
            )
            self.stdout.write(f"oldest_wait_seconds={payload['oldest_wait_seconds']} http_status={code}")
