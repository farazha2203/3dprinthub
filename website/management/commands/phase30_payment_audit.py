from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, F, Sum
from django.utils import timezone

from website.models import Payment, PaymentLedgerEntry, SiteSetting
from website.payment_services import payment_gateway_status


class Command(BaseCommand):
    help = "Audit Phase 30 online payment configuration, idempotency and ledger integrity."

    def add_arguments(self, parser):
        parser.add_argument("--strict", action="store_true")

    def handle(self, *args, **options):
        site = SiteSetting.objects.first()
        ready, reason = payment_gateway_status(site)
        failures = []
        warnings = []

        paid_gateway = Payment.objects.filter(method="gateway", status="paid")
        paid_without_ref = paid_gateway.filter(ref_id="").count()
        paid_without_ledger = paid_gateway.annotate(ledger_count=Count("ledger_entries")).filter(ledger_count=0).count()
        duplicate_refs = list(
            paid_gateway.exclude(ref_id="")
            .values("provider", "ref_id")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
        )
        wrong_ledger_amount = PaymentLedgerEntry.objects.filter(
            entry_type="payment",
            direction="credit",
        ).exclude(amount=F("payment__amount")).count()
        duplicate_ledger_events = list(
            PaymentLedgerEntry.objects.values("event_key").annotate(total=Count("id")).filter(total__gt=1)
        )
        stale_minutes = max(int(getattr(settings, "PAYMENT_GATEWAY_PENDING_TTL_MINUTES", 30) or 30), 5)
        stale_pending = Payment.objects.filter(
            method="gateway",
            status__in=["pending", "verifying"],
            created_at__lt=timezone.now() - timedelta(minutes=stale_minutes * 2),
        ).count()
        invalid_amounts = Payment.objects.filter(amount=0).count()
        callback_without_authority = Payment.objects.filter(
            method="gateway",
            callback_received_at__isnull=False,
            authority="",
        ).count()

        if bool(getattr(settings, "PAYMENT_GATEWAY_ENABLED", False)) and not ready:
            failures.append(reason)
        if paid_without_ref:
            failures.append(f"{paid_without_ref} پرداخت آنلاین موفق بدون کد پیگیری وجود دارد.")
        if paid_without_ledger:
            failures.append(f"{paid_without_ledger} پرداخت آنلاین موفق بدون ثبت دفتر مالی وجود دارد.")
        if duplicate_refs:
            failures.append(f"{len(duplicate_refs)} کد پیگیری تکراری میان پرداخت‌های موفق وجود دارد.")
        if wrong_ledger_amount:
            failures.append(f"{wrong_ledger_amount} ثبت دفتر مالی با مبلغ پرداخت همسان نیست.")
        if duplicate_ledger_events:
            failures.append(f"{len(duplicate_ledger_events)} کلید تکراری دفتر مالی وجود دارد.")
        if invalid_amounts:
            failures.append(f"{invalid_amounts} پرداخت با مبلغ صفر وجود دارد.")
        if callback_without_authority:
            failures.append(f"{callback_without_authority} Callback آنلاین بدون Authority ذخیره شده است.")
        if stale_pending:
            warnings.append(f"{stale_pending} پرداخت آنلاین قدیمی هنوز در انتظار یا Verify است.")
        if not bool(getattr(settings, "PAYMENT_GATEWAY_ENABLED", False)):
            warnings.append("درگاه آنلاین در .env غیرفعال است.")
        if site and not site.online_payment_enabled:
            warnings.append("درگاه آنلاین در تنظیمات سایت غیرفعال است.")
        if bool(getattr(settings, "ZARINPAL_SANDBOX", False)):
            warnings.append("زرین‌پال در حالت Sandbox است.")

        metrics = {
            "gateway_ready": int(ready),
            "gateway_paid": paid_gateway.count(),
            "gateway_pending": Payment.objects.filter(method="gateway", status__in=["pending", "verifying"]).count(),
            "gateway_failed": Payment.objects.filter(method="gateway", status__in=["failed", "cancelled"]).count(),
            "paid_without_ref": paid_without_ref,
            "paid_without_ledger": paid_without_ledger,
            "duplicate_paid_refs": len(duplicate_refs),
            "ledger_entries": PaymentLedgerEntry.objects.count(),
            "stale_pending": stale_pending,
        }
        for key, value in metrics.items():
            self.stdout.write(f"{key}: {value}")
        for item in warnings:
            self.stdout.write(self.style.WARNING(f"WARNING: {item}"))
        for item in failures:
            self.stdout.write(self.style.ERROR(f"FAIL: {item}"))

        if failures:
            self.stdout.write("PHASE30_AUDIT=FAIL")
            raise CommandError("Phase 30 payment audit failed.")
        if options["strict"] and warnings:
            self.stdout.write("PHASE30_AUDIT=WARN")
            raise CommandError("Phase 30 strict audit found warnings.")
        self.stdout.write(self.style.SUCCESS("PHASE30_AUDIT=OK"))
