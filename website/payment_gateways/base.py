from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class PaymentGatewayError(RuntimeError):
    """Safe gateway exception that may be shown to the customer."""

    def __init__(self, message: str, *, code: int | None = None, payload: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.payload = payload or {}


class PaymentGatewayTemporaryError(PaymentGatewayError):
    """Network/provider error where retrying verification can be safe."""


@dataclass(frozen=True)
class GatewayRequestResult:
    authority: str
    checkout_url: str
    status_code: int
    message: str = ""
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GatewayVerifyResult:
    success: bool
    status_code: int
    ref_id: str = ""
    message: str = ""
    already_verified: bool = False
    card_pan: str = ""
    fee: int = 0
    raw_response: dict[str, Any] = field(default_factory=dict)


class BasePaymentGateway:
    slug = "base"

    def amount_for_provider(self, amount_toman: int) -> int:
        raise NotImplementedError

    @property
    def currency(self) -> str:
        raise NotImplementedError

    def create_payment(self, *, amount_toman: int, callback_url: str, description: str, mobile: str = "", email: str = "") -> GatewayRequestResult:
        raise NotImplementedError

    def verify_payment(self, *, amount_toman: int, authority: str, gateway_amount: int | None = None, currency: str | None = None) -> GatewayVerifyResult:
        raise NotImplementedError
