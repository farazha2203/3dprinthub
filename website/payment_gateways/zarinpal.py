from __future__ import annotations

from typing import Any

import requests
from django.conf import settings

from .base import (
    BasePaymentGateway,
    GatewayRequestResult,
    GatewayVerifyResult,
    PaymentGatewayError,
    PaymentGatewayTemporaryError,
)


class ZarinPalGateway(BasePaymentGateway):
    slug = "zarinpal"

    def __init__(self):
        self.merchant_id = str(getattr(settings, "ZARINPAL_MERCHANT_ID", "") or "").strip()
        self.sandbox = bool(getattr(settings, "ZARINPAL_SANDBOX", False))
        self.timeout = max(int(getattr(settings, "PAYMENT_GATEWAY_HTTP_TIMEOUT", 15) or 15), 3)
        self._currency = str(getattr(settings, "ZARINPAL_CURRENCY", "IRT") or "IRT").upper()
        if self._currency not in {"IRT", "IRR"}:
            raise PaymentGatewayError("واحد پول درگاه باید IRT یا IRR باشد.")
        if not self.merchant_id:
            raise PaymentGatewayError("شناسه پذیرنده زرین‌پال تنظیم نشده است.")

        if self.sandbox:
            self.request_url = str(getattr(settings, "ZARINPAL_SANDBOX_REQUEST_URL", "https://sandbox.zarinpal.com/pg/v4/payment/request.json"))
            self.verify_url = str(getattr(settings, "ZARINPAL_SANDBOX_VERIFY_URL", "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"))
            self.start_url = str(getattr(settings, "ZARINPAL_SANDBOX_START_URL", "https://sandbox.zarinpal.com/pg/StartPay/"))
        else:
            self.request_url = str(getattr(settings, "ZARINPAL_REQUEST_URL", "https://api.zarinpal.com/pg/v4/payment/request.json"))
            self.verify_url = str(getattr(settings, "ZARINPAL_VERIFY_URL", "https://api.zarinpal.com/pg/v4/payment/verify.json"))
            self.start_url = str(getattr(settings, "ZARINPAL_START_URL", "https://www.zarinpal.com/pg/StartPay/"))

    @property
    def currency(self) -> str:
        return self._currency

    def amount_for_provider(self, amount_toman: int) -> int:
        amount = int(amount_toman)
        if amount <= 0:
            raise PaymentGatewayError("مبلغ پرداخت نامعتبر است.")
        return amount if self.currency == "IRT" else amount * 10

    def _post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
            )
        except requests.RequestException as exc:
            raise PaymentGatewayTemporaryError("ارتباط با درگاه پرداخت برقرار نشد. چند لحظه دیگر دوباره تلاش کنید.") from exc

        try:
            body = response.json()
        except ValueError as exc:
            raise PaymentGatewayTemporaryError("پاسخ نامعتبر از درگاه پرداخت دریافت شد.") from exc

        if not isinstance(body, dict):
            raise PaymentGatewayTemporaryError("ساختار پاسخ درگاه پرداخت نامعتبر است.")
        if response.status_code >= 500:
            raise PaymentGatewayTemporaryError("درگاه پرداخت موقتاً در دسترس نیست.", payload=body)
        return body

    @staticmethod
    def _extract(body: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        data = body.get("data") if isinstance(body.get("data"), dict) else {}
        errors_raw = body.get("errors")
        if isinstance(errors_raw, list):
            errors = [item for item in errors_raw if isinstance(item, dict)]
        elif isinstance(errors_raw, dict):
            errors = [errors_raw]
        else:
            errors = []
        return data, errors

    @staticmethod
    def _error_message(errors: list[dict[str, Any]], code: int | None = None) -> str:
        for item in errors:
            message = item.get("message") or item.get("validation")
            if message:
                return str(message)
        return f"درگاه پرداخت درخواست را نپذیرفت (کد {code})." if code is not None else "درگاه پرداخت درخواست را نپذیرفت."

    def create_payment(self, *, amount_toman: int, callback_url: str, description: str, mobile: str = "", email: str = "") -> GatewayRequestResult:
        provider_amount = self.amount_for_provider(amount_toman)
        metadata = {}
        if mobile:
            metadata["mobile"] = mobile
        if email:
            metadata["email"] = email
        payload: dict[str, Any] = {
            "merchant_id": self.merchant_id,
            "amount": provider_amount,
            "description": description[:255],
            "callback_url": callback_url,
            "currency": self.currency,
        }
        if metadata:
            payload["metadata"] = metadata

        body = self._post(self.request_url, payload)
        data, errors = self._extract(body)
        code = int(data.get("code") or (errors[0].get("code") if errors else 0) or 0)
        authority = str(data.get("authority") or "").strip()
        if code != 100 or not authority:
            raise PaymentGatewayError(self._error_message(errors, code), code=code, payload=body)
        return GatewayRequestResult(
            authority=authority,
            checkout_url=f"{self.start_url.rstrip('/')}/{authority}",
            status_code=code,
            message=str(data.get("message") or ""),
            raw_response=body,
        )

    def verify_payment(self, *, amount_toman: int, authority: str, gateway_amount: int | None = None, currency: str | None = None) -> GatewayVerifyResult:
        verify_currency = str(currency or self.currency).upper()
        if verify_currency not in {"IRT", "IRR"}:
            raise PaymentGatewayError("واحد ذخیره‌شده تراکنش نامعتبر است.")
        provider_amount = int(gateway_amount or 0) or (int(amount_toman) if verify_currency == "IRT" else int(amount_toman) * 10)
        payload = {
            "merchant_id": self.merchant_id,
            "amount": provider_amount,
            "authority": authority,
            "currency": verify_currency,
        }
        body = self._post(self.verify_url, payload)
        data, errors = self._extract(body)
        code = int(data.get("code") or (errors[0].get("code") if errors else 0) or 0)
        ref_id = str(data.get("ref_id") or "")
        success = code in {100, 101} and bool(ref_id)
        message = str(data.get("message") or "") if success else self._error_message(errors, code)
        return GatewayVerifyResult(
            success=success,
            status_code=code,
            ref_id=ref_id,
            message=message,
            already_verified=code == 101,
            card_pan=str(data.get("card_pan") or ""),
            fee=int(data.get("fee") or 0),
            raw_response=body,
        )
