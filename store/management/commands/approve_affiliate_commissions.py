from django.core.management.base import BaseCommand

from store.affiliate_services import approve_due_commissions


class Command(BaseCommand):
    help = "پورسانت‌های تحویل‌شده‌ای را که دوره انتظارشان تمام شده تأیید می‌کند."

    def handle(self, *args, **options):
        count = approve_due_commissions()
        self.stdout.write(self.style.SUCCESS(f"{count} پورسانت تأیید شد."))
