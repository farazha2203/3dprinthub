"""Catalog-authoritative selectors for service quotes.

Only the same active, explicitly-priced filament offers shown as orderable
options in Store/Catalog are eligible for an administrator's new quote.
"""
from store.phase39_models import MaterialColorOption


def available_filament_offers():
    return MaterialColorOption.objects.filter(
        is_active=True, material__is_active=True,
        sale_price_per_roll__gt=0, roll_weight_grams__gt=0,
        print_hourly_rate__gt=0,
    ).select_related("material").order_by("material__sort_order", "material__name", "brand_name", "name")


def format_filament_offer(offer):
    rate = offer.effective_sale_price_per_gram
    return (
        f"{offer.material.name} / {offer.brand_name or 'بدون برند'} / {offer.name}"
        f" | {rate:,.0f} تومان/گرم"
        f" | چاپ {int(offer.print_hourly_rate):,}/ساعت"
        f" | نظارت {int(offer.supervision_hourly_rate):,}/ساعت"
        f" | پیش گرم {offer.preheat_hours} ساعت × {offer.preheat_hourly_rate:,}"
    )
