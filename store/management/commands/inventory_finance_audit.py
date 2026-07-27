from decimal import Decimal

from django.core.management.base import BaseCommand

from store.models import FilamentSpool, MaterialUsage, ProductionJob
from store.production_services import finance_summary, inventory_summary


class Command(BaseCommand):
    help = "کنترل سلامت انبار وزنی، مصرف پروژه و گزارش مالی"

    def handle(self, *args, **options):
        errors = []
        for spool in FilamentSpool.objects.all():
            if Decimal(spool.remaining_weight_grams) < 0:
                errors.append(f"رول {spool.code} مانده منفی دارد.")
            if Decimal(spool.remaining_weight_grams) > Decimal(spool.nominal_weight_grams):
                errors.append(f"رول {spool.code} بیشتر از وزن اولیه موجودی دارد.")
            if spool.status == "empty" and Decimal(spool.remaining_weight_grams) != 0:
                errors.append(f"رول {spool.code} خالی است ولی مانده صفر نیست.")

        for usage in MaterialUsage.objects.filter(posted_at__isnull=False):
            consumed = -sum((movement.grams for movement in usage.movements.filter(grams__lt=0)), Decimal("0"))
            if usage.material.track_filament_inventory and consumed != usage.consumption_grams:
                errors.append(
                    f"مصرف پروژه {usage.job.job_number} برای {usage.material}: "
                    f"ثبت‌شده {usage.consumption_grams}، گردش {consumed}"
                )

        if errors:
            for error in errors:
                self.stderr.write(self.style.ERROR(error))
            raise SystemExit(1)

        summary = finance_summary()
        self.stdout.write(f"پروژه‌ها: {ProductionJob.objects.count()}")
        self.stdout.write(f"درآمد ثبت‌شده: {summary['revenue']:,} تومان")
        self.stdout.write(f"هزینه پروژه: {summary['project_cost']:,} تومان")
        self.stdout.write(f"هزینه عمومی: {summary['general_expenses']:,} تومان")
        self.stdout.write(f"سود خالص: {summary['net_profit']:,} تومان")
        self.stdout.write(f"متریال‌های پایش‌شده: {len(inventory_summary())}")
        self.stdout.write(self.style.SUCCESS("سلامت انبار و محاسبات مالی تأیید شد."))
