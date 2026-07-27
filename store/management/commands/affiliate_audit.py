from django.core.management.base import BaseCommand
from django.db.models import Sum

from store.models import AffiliateCommission, AffiliateLedgerEntry, AffiliatePartner, AffiliatePayout


class Command(BaseCommand):
    help = "سلامت حسابداری و انتساب سیستم همکاری در فروش را بررسی می‌کند."

    def handle(self, *args, **options):
        errors = []
        warnings = []
        for partner in AffiliatePartner.objects.select_related("tier"):
            if not partner.tier_id:
                errors.append(f"همکار {partner.pk} سطح همکاری ندارد.")
            if partner.status == "active" and not partner.terms_accepted:
                warnings.append(f"همکار فعال {partner.code} پذیرش قوانین ندارد.")
        for commission in AffiliateCommission.objects.select_related("order", "partner"):
            if commission.order.affiliate_partner_id != commission.partner_id:
                errors.append(f"پورسانت {commission.pk} با معرف سفارش همخوان نیست.")
            if commission.amount < 0 or commission.basis_amount < 0:
                errors.append(f"پورسانت {commission.pk} مبلغ نامعتبر دارد.")
            if commission.status in {"approved", "requested", "paid"}:
                credit = AffiliateLedgerEntry.objects.filter(commission=commission, entry_type="commission").aggregate(value=Sum("amount"))["value"] or 0
                if credit != commission.amount:
                    errors.append(f"اعتبار دفتر پورسانت {commission.pk} ناقص است.")
        for payout in AffiliatePayout.objects.prefetch_related("items"):
            item_total = sum(item.amount for item in payout.items.all())
            if item_total != payout.amount and payout.status != "cancelled":
                errors.append(f"جمع ردیف‌های تسویه {payout.payout_number} با مبلغ آن برابر نیست.")
        for partner in AffiliatePartner.objects.all():
            balance = partner.ledger_entries.aggregate(value=Sum("amount"))["value"] or 0
            if balance < 0:
                warnings.append(f"مانده همکار {partner.code} منفی است: {balance:,} تومان")
        for line in warnings:
            self.stdout.write(self.style.WARNING(line))
        if errors:
            for line in errors:
                self.stdout.write(self.style.ERROR(line))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS("سلامت سیستم همکاری در فروش تأیید شد."))
