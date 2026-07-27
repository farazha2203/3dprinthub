from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone

from store.models import CustomerLinkAnalysis, CustomerLinkAnalysisAttempt, CustomerLinkAnalysisJob


class Command(BaseCommand):
    help = "گزارش سلامت صف تحلیل لینک، Retryها، قفل‌های فعال و تحلیل‌های بدون Job."

    def handle(self, *args, **options):
        now = timezone.now()
        job_counts = dict(
            CustomerLinkAnalysisJob.objects.values_list("status").annotate(total=Count("id"))
        )
        attempt_counts = dict(
            CustomerLinkAnalysisAttempt.objects.values_list("status").annotate(total=Count("id"))
        )
        orphaned = CustomerLinkAnalysis.objects.filter(
            status__in=["pending", "processing"],
            job__isnull=True,
        ).count()
        overdue = CustomerLinkAnalysisJob.objects.filter(
            status__in=["queued", "retry"],
            next_run_at__lte=now,
        ).count()
        running = CustomerLinkAnalysisJob.objects.filter(status="running").count()

        self.stdout.write("Phase 24 link queue audit")
        self.stdout.write(f"jobs={job_counts}")
        self.stdout.write(f"attempts={attempt_counts}")
        self.stdout.write(f"due_jobs={overdue}")
        self.stdout.write(f"running_jobs={running}")
        self.stdout.write(f"orphaned_pending_analyses={orphaned}")
        if orphaned:
            self.stdout.write(self.style.WARNING("Pending analyses without a queue job were found."))
        else:
            self.stdout.write(self.style.SUCCESS("Queue relationships are healthy."))
