from __future__ import annotations

from django import template

from store.phase50_commerce_policy import StorePaymentSettings


register = template.Library()


@register.simple_tag
def store_payment_settings():
    """Return the singleton public bank-transfer destination settings."""
    try:
        return StorePaymentSettings.load()
    except Exception:
        return None
