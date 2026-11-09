"""Quote price agreement: freeze once, never silently reprice a sent quote.

The pre-existing quote price formulas are retained for drafts. No legacy data
migration/backfill is performed; existing finalized quotes without snapshots
must be reviewed before a manual financial transaction is accepted.
"""
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone

FROZEN_INPUT_FIELDS = (
    "order_id", "material_id", "weight_grams", "print_time_minutes",
    "machine_hourly_rate", "minimum_billable_minutes",
    "billing_increment_minutes", "labor_fee", "design_fee",
    "post_processing_fee", "shipping_fee", "discount",
    "price_tolerance_percent", "deposit_percent",
)
SNAPSHOT_FIELDS = (
    "pricing_snapshot_at", "pricing_snapshot_material_rate",
    "pricing_snapshot_quantity", "pricing_snapshot_material_cost",
    "pricing_snapshot_machine_cost", "pricing_snapshot_subtotal",
    "pricing_snapshot_discount", "pricing_snapshot_total",
)
FINAL_QUOTE_STATUSES = frozenset({"sent", "accepted"})


def validate_quote_pricing(quote):
    if quote.pk:
        previous = type(quote).objects.filter(pk=quote.pk).first()
        if previous and previous.pricing_snapshot_at:
            changed = [name for name in FROZEN_INPUT_FIELDS if getattr(quote, name) != getattr(previous, name)]
            if changed:
                raise ValidationError(
                    "این پیش‌فاکتور قطعی شده و تغییر مبلغ یا مشخصات مالی آن مجاز نیست. "
                    "برای اصلاح مالی، گردش مستند اصلاحیه لازم است."
                )
            if quote.status == "draft":
                raise ValidationError("پیش‌فاکتور تثبیت‌شده را نمی‌توان بدون اصلاحیه به پیش‌نویس بازگرداند.")
            if any(getattr(quote, name) != getattr(previous, name) for name in SNAPSHOT_FIELDS):
                raise ValidationError("اطلاعات تثبیت قیمت پیش‌فاکتور قابل ویرایش نیست.")
    if quote.status in FINAL_QUOTE_STATUSES and not quote.pricing_snapshot_at:
        if not quote.total_price:
            raise ValidationError("پیش‌فاکتور بدون مبلغ نهایی مثبت قابل ارسال یا تأیید نیست.")
        if int(quote.discount) > int(quote.subtotal):
            raise ValidationError("مبلغ تخفیف نمی‌تواند از جمع کل بیشتر باشد.")
        if Decimal(quote.deposit_percent) > Decimal("100"):
            raise ValidationError("درصد بیعانه نباید بیش از ۱۰۰ باشد.")


def take_quote_pricing_snapshot(quote):
    """Compute *before* assigning any snapshot field to avoid frozen getters."""
    values = {
        "pricing_snapshot_material_rate": Decimal(quote.material_price_per_gram).quantize(Decimal("0.0001")),
        "pricing_snapshot_quantity": int(quote.order.quantity),
        "pricing_snapshot_material_cost": int(quote.material_cost),
        "pricing_snapshot_machine_cost": int(quote.machine_cost),
        "pricing_snapshot_subtotal": int(quote.subtotal),
        "pricing_snapshot_discount": int(quote.discount),
        "pricing_snapshot_total": int(quote.total_price),
        "pricing_snapshot_at": timezone.now(),
    }
    for name, value in values.items():
        setattr(quote, name, value)
