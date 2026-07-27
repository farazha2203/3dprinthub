from django.conf import settings
from django.core.management.base import BaseCommand

from store.models import LinkAnalysisManualReview
from store.realtime import operations_snapshot


class Command(BaseCommand):
    help = "Audit Phase 26 realtime, manual-review queue, and channel-layer configuration."

    def handle(self, *args, **options):
        backend = settings.CHANNEL_LAYERS.get("default", {}).get("BACKEND", "")
        snapshot = operations_snapshot()
        self.stdout.write(f"channel_backend={backend}")
        self.stdout.write(f"redis_configured={bool(getattr(settings, 'REALTIME_REDIS_URL', ''))}")
        self.stdout.write(f"manual_review_pending={snapshot['manual_review_pending']}")
        self.stdout.write(f"manual_review_in_progress={snapshot['manual_review_in_progress']}")
        self.stdout.write(f"active_workers={snapshot['active_workers']}")
        self.stdout.write(f"queued={snapshot['queued']} running={snapshot['running']} retry={snapshot['retry']}")
        stale_open = LinkAnalysisManualReview.objects.filter(status__in=["pending", "in_progress"], analysis__isnull=True).count()
        self.stdout.write(f"invalid_open_reviews={stale_open}")
        if not settings.DEBUG and backend == "channels.layers.InMemoryChannelLayer":
            self.stdout.write(self.style.WARNING("Production realtime is in fallback mode. Configure REALTIME_REDIS_URL."))
        else:
            self.stdout.write(self.style.SUCCESS("Phase 26 realtime configuration audit completed."))
