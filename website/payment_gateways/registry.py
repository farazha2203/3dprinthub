from __future__ import annotations

from django.conf import settings

from .base import BasePaymentGateway, PaymentGatewayError
from .zarinpal import ZarinPalGateway


def gateway_configuration_status(site_setting=None) -> tuple[bool, str]:
    if not bool(getattr(settings, "PAYMENT_GATEWAY_ENABLED", False)):
        return False, "پرداخت آنلاین در تنظیمات محیط غیرفعال است."
    if site_setting is not None and not bool(getattr(site_setting, "online_payment_enabled", False)):
        return False, "پرداخت آنلاین در تنظیمات سایت غیرفعال است."
    provider = str(
        getattr(site_setting, "online_payment_provider", "")
        or getattr(settings, "PAYMENT_GATEWAY_PROVIDER", "zarinpal")
    ).strip().lower()
    if provider != "zarinpal":
        return False, "ارائه‌دهنده پرداخت آنلاین پشتیبانی نمی‌شود."
    if not str(getattr(settings, "ZARINPAL_MERCHANT_ID", "") or "").strip():
        return False, "شناسه پذیرنده زرین‌پال در .env ثبت نشده است."
    return True, "آماده"


def get_payment_gateway(site_setting=None, *, require_enabled: bool = True, provider_slug: str = "") -> BasePaymentGateway:
    if require_enabled:
        ready, reason = gateway_configuration_status(site_setting)
        if not ready:
            raise PaymentGatewayError(reason)
    elif not str(getattr(settings, "ZARINPAL_MERCHANT_ID", "") or "").strip():
        raise PaymentGatewayError("شناسه پذیرنده زرین‌پال برای Verify تنظیم نشده است.")
    provider = str(
        provider_slug
        or getattr(site_setting, "online_payment_provider", "")
        or getattr(settings, "PAYMENT_GATEWAY_PROVIDER", "zarinpal")
    ).strip().lower()
    if provider == "zarinpal":
        return ZarinPalGateway()
    raise PaymentGatewayError("درگاه پرداخت انتخاب‌شده پشتیبانی نمی‌شود.")
