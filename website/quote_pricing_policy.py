"""Quote price agreement: freeze once, never silently reprice a sent quote.

The pre-existing quote price formulas are retained for drafts. No legacy data
migration/backfill is performed; existing finalized quotes without snapshots
must be reviewed before a manual financial transaction is accepted.
"""
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone

FROZEN_INPUT_FIELDS = (
    "order_id", "material_id", "filament_offer_id", "print_quality_id",
    "weight_grams", "support_weight_grams", "support_cost_multiplier",
    "assembly_fee_per_unit", "print_time_minutes",
    "print_time_scope", "machine_hourly_rate", "minimum_billable_minutes",
    "billing_increment_minutes", "labor_fee", "design_fee",
    "post_processing_fee", "shipping_fee", "discount",
    "price_tolerance_percent", "deposit_percent",
)
SNAPSHOT_FIELDS = (
    "pricing_snapshot_at", "pricing_snapshot_material_rate",
    "pricing_snapshot_quantity", "pricing_snapshot_material_cost",
    "pricing_snapshot_machine_cost", "pricing_snapshot_supervision_cost",
    "pricing_snapshot_preheat_cost", "pricing_snapshot_assembly_cost",
    "pricing_snapshot_offer_rounding_adjustment", "pricing_snapshot_subtotal",
    "pricing_snapshot_discount", "pricing_snapshot_total",
)
FINAL_QUOTE_STATUSES = frozenset({"sent", "accepted"})


def validate_quote_pricing(quote):
    if quote.print_time_scope not in {"per_piece", "batch"}:
        raise ValidationError("مبنای زمان چاپ باید «هر قطعه» یا «کل تیراژ» باشد.")
    if quote.support_weight_grams < 0 or quote.support_cost_multiplier < 0:
        raise ValidationError("وزن یا ضریب ساپورت نباید منفی باشد.")
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
        if quote.filament_offer_id:
            offer = quote.filament_offer
            if not offer.is_active or not offer.material.is_active:
                raise ValidationError("فیلامنت انتخابی دیگر قابل عرضه نیست.")
            if Decimal(offer.effective_sale_price_per_gram) <= 0 or offer.print_hourly_rate <= 0:
                raise ValidationError("نرخ واقعی گرم و ساعت چاپ این فیلامنت باید در کاتالوگ تنظیم شود.")
            if quote.weight_grams <= 0 or quote.print_time_minutes <= 0:
                raise ValidationError("وزن و زمان اسلایسر برای پیش‌فاکتور فیلامنت باید مثبت باشند.")
            required_grams = (quote.weight_grams + quote.support_weight_grams) * quote.order.quantity
            if offer.current_stock_grams < required_grams:
                raise ValidationError("موجودی واقعی فیلامنت برای وزن این سفارش کافی نیست؛ ابتدا موجودی را اصلاح کنید.")
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
        "pricing_snapshot_supervision_cost": int(quote.supervision_cost),
        "pricing_snapshot_preheat_cost": int(quote.preheat_cost),
        "pricing_snapshot_assembly_cost": int(quote.assembly_cost),
        "pricing_snapshot_offer_rounding_adjustment": int(quote.offer_rounding_adjustment),
        "pricing_snapshot_subtotal": int(quote.subtotal),
        "pricing_snapshot_discount": int(quote.discount),
        "pricing_snapshot_total": int(quote.total_price),
        "pricing_snapshot_at": timezone.now(),
    }
    for name, value in values.items():
        setattr(quote, name, value)
