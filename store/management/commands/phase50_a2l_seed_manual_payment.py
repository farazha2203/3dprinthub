from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from store.phase50_commerce_policy import StorePaymentSettings


BANK_NAME = "بانک پاسارگاد"
ACCOUNT_HOLDER = "فراز حراجی"
CARD_NUMBER = "5022-2910-9403-4343"
TRANSFER_INSTRUCTIONS = (
    "مبلغ سفارش را به کارت بالا واریز کنید، سپس تصویر رسید را در همین صفحه ثبت کنید. "
    "رسید ابتدا در وضعیت «در انتظار بررسی» قرار می‌گیرد و توسط ادمین تأیید می‌شود. "
    "هیچ رمز کارت، CVV2 یا رمز پویا در سایت وارد نکنید."
)


class Command(BaseCommand):
    help = "Seed the approved manual bank-transfer payment details for 3DPrintHub."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Persist the payment settings. Without this flag the command is read-only.",
        )
    def handle(self, *args, **options):
        apply = bool(options["apply"])
        # Keep console output ASCII-safe on Windows/cPanel and avoid logging
        # customer-visible banking identity or the full card number.
        self.stdout.write("A2L_MANUAL_PAYMENT_BANK_CONFIGURED=YES")
        self.stdout.write("A2L_MANUAL_PAYMENT_CARD_LAST4=" + CARD_NUMBER[-4:])
        self.stdout.write("A2L_MANUAL_PAYMENT_APPLY=" + str(apply))
        if not apply:
            self.stdout.write(self.style.SUCCESS("A2L_MANUAL_PAYMENT_DRY_RUN=PASS"))
            return

        with transaction.atomic():
            row = StorePaymentSettings.objects.order_by("pk").first()
            if row is None:
                row = StorePaymentSettings()
            row.title = "اطلاعات پرداخت کارت به کارت"
            row.bank_name = BANK_NAME
            row.account_holder = ACCOUNT_HOLDER
            row.card_number = CARD_NUMBER
            row.transfer_instructions = TRANSFER_INSTRUCTIONS
            row.is_active = True
            row.save()

        row.refresh_from_db()
        self.stdout.write("A2L_MANUAL_PAYMENT_ROW_ID=" + str(row.pk))
        self.stdout.write("A2L_MANUAL_PAYMENT_ACTIVE=" + str(bool(row.is_active)))
        self.stdout.write(self.style.SUCCESS("A2L_MANUAL_PAYMENT_APPLY=PASS"))
