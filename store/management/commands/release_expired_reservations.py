from django.core.management.base import BaseCommand
from store.services import release_expired_reservations


class Command(BaseCommand):
    help = "رزروهای منقضی‌شده سفارش‌های پرداخت‌نشده را آزاد می‌کند."

    def handle(self, *args, **options):
        count = release_expired_reservations()
        self.stdout.write(self.style.SUCCESS(f"{count} رزرو منقضی‌شده آزاد شد."))
