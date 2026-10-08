"""Shared public Store price/default-variant truth for HTML and Google JSON-LD.

The list order is set by product_detail_view: first material (filament),
then first sales/print profile, then first color. Never choose the
cheapest variant or advertise an unpriced/unorderable default.
"""
from __future__ import annotations

from .phase50_orderability import variant_is_orderable


def public_variant_price(variant) -> int:
    """Return the same unit price as the customer-facing selector."""
    snapshot = getattr(variant, "_public_price_breakdown", None)
    if snapshot is None:
        snapshot = variant.price_breakdown()
        variant._public_price_breakdown = snapshot
        variant.public_price_breakdown = snapshot
    variant.public_unit_price = max(0, int(snapshot.get("unit_price") or 0))
    return variant.public_unit_price


def first_orderable_variant(product, variants):
    """Select the first real priced/orderable combination in supplied order."""
    if getattr(product, "order_mode", "variant") == "fixed":
        return None
    for variant in variants:
        if public_variant_price(variant) > 0 and variant_is_orderable(variant):
            return variant
    return None
