from django.core.management.base import BaseCommand
from django.db.models import F
from store.models import ProductVariant, StoreOrder


class Command(BaseCommand):
    help = "سلامت موجودی، رزروها و سفارش‌های فروشگاه را بررسی می‌کند."

    def handle(self, *args, **options):
        errors = []
        negative = ProductVariant.objects.filter(reserved_quantity__gt=F("stock_quantity"), track_inventory=True, allow_backorder=False)
        for variant in negative:
            errors.append(f"رزرو بیشتر از موجودی: {variant.code}")
        orphan_reserved = StoreOrder.objects.filter(inventory_reserved=True, items__isnull=True).distinct()
        for order in orphan_reserved:
            errors.append(f"سفارش رزروشده بدون ردیف: {order.order_number}")
        paid_reserved = StoreOrder.objects.filter(payment_status="paid", inventory_reserved=True)
        for order in paid_reserved:
            errors.append(f"سفارش پرداخت‌شده با رزرو باز: {order.order_number}")
        if errors:
            for item in errors:
                self.stdout.write(self.style.ERROR(item))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS("سلامت عملیات فروشگاه تأیید شد."))
