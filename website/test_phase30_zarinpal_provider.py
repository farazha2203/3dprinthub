from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from website.payment_gateways.base import PaymentGatewayError
from website.payment_gateways.zarinpal import ZarinPalGateway


@override_settings(
    ZARINPAL_MERCHANT_ID="00000000-0000-0000-0000-000000000000",
    ZARINPAL_SANDBOX=True,
    PAYMENT_GATEWAY_HTTP_TIMEOUT=5,
)
class Phase30ZarinPalProviderTests(SimpleTestCase):
    @override_settings(ZARINPAL_CURRENCY="IRT")
    def test_toman_amount_is_sent_without_multiplier(self):
        gateway = ZarinPalGateway()
        self.assertEqual(gateway.amount_for_provider(125000), 125000)

    @override_settings(ZARINPAL_CURRENCY="IRR")
    def test_rial_amount_is_ten_times_toman(self):
        gateway = ZarinPalGateway()
        self.assertEqual(gateway.amount_for_provider(125000), 1250000)

    @patch("website.payment_gateways.zarinpal.requests.post")
    def test_request_accepts_only_code_100_with_authority(self, post):
        response = Mock(status_code=200)
        response.json.return_value = {"data": {"code": 100, "authority": "A123", "message": "ok"}, "errors": []}
        post.return_value = response
        result = ZarinPalGateway().create_payment(
            amount_toman=10000,
            callback_url="https://example.com/callback",
            description="Order",
        )
        self.assertEqual(result.authority, "A123")
        self.assertTrue(result.checkout_url.endswith("/A123"))
        sent = post.call_args.kwargs["json"]
        self.assertEqual(sent["amount"], 10000)
        self.assertEqual(sent["currency"], "IRT")

    @patch("website.payment_gateways.zarinpal.requests.post")
    def test_request_error_does_not_return_checkout_url(self, post):
        response = Mock(status_code=200)
        response.json.return_value = {"data": {}, "errors": {"code": -9, "message": "validation failed"}}
        post.return_value = response
        with self.assertRaises(PaymentGatewayError):
            ZarinPalGateway().create_payment(
                amount_toman=10000,
                callback_url="https://example.com/callback",
                description="Order",
            )

    @patch("website.payment_gateways.zarinpal.requests.post")
    def test_verify_code_101_is_idempotent_success(self, post):
        response = Mock(status_code=200)
        response.json.return_value = {"data": {"code": 101, "ref_id": 555, "message": "verified"}, "errors": []}
        post.return_value = response
        result = ZarinPalGateway().verify_payment(amount_toman=10000, authority="A123")
        self.assertTrue(result.success)
        self.assertTrue(result.already_verified)
        self.assertEqual(result.ref_id, "555")

    @patch("website.payment_gateways.zarinpal.requests.post")
    def test_verify_uses_stored_gateway_amount_and_currency(self, post):
        response = Mock(status_code=200)
        response.json.return_value = {"data": {"code": 100, "ref_id": 777, "message": "verified"}, "errors": []}
        post.return_value = response
        ZarinPalGateway().verify_payment(
            amount_toman=10000,
            authority="A123",
            gateway_amount=100000,
            currency="IRR",
        )
        sent = post.call_args.kwargs["json"]
        self.assertEqual(sent["amount"], 100000)
        self.assertEqual(sent["currency"], "IRR")
