from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Material, Order, Payment, PaymentLedgerEntry, Quote, SiteSetting
from .payment_gateways.base import GatewayRequestResult, GatewayVerifyResult


class FakeGateway:
    slug = "zarinpal"
    currency = "IRT"

    def amount_for_provider(self, amount_toman):
        return int(amount_toman)

    def create_payment(self, **kwargs):
        return GatewayRequestResult(
            authority="A000000000000000000000000000000000001",
            checkout_url="https://gateway.example/start/A000000000000000000000000000000000001",
            status_code=100,
            message="created",
            raw_response={"data": {"code": 100, "authority": "A000000000000000000000000000000000001"}},
        )

    def verify_payment(self, **kwargs):
        return GatewayVerifyResult(
            success=True,
            status_code=100,
            ref_id="987654321",
            message="verified",
            card_pan="621986******1234",
            fee=0,
            raw_response={"data": {"code": 100, "ref_id": 987654321}},
        )


@override_settings(
    PAYMENT_GATEWAY_ENABLED=True,
    PAYMENT_GATEWAY_PROVIDER="zarinpal",
    ZARINPAL_MERCHANT_ID="00000000-0000-0000-0000-000000000000",
    ZARINPAL_SANDBOX=True,
)
class Phase30OnlinePaymentTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="phase30", email="phase30@example.com", password="pass12345")
        self.other = user_model.objects.create_user(username="other30", email="other30@example.com", password="pass12345")
        self.site = SiteSetting.objects.create(
            brand_name="3DPrintHub",
            online_payment_enabled=True,
            online_payment_provider="zarinpal",
            online_payment_minimum_toman=1000,
        )
        material = Material.objects.create(name="PLA", price_per_kg=500000, is_active=True)
        self.order = Order.objects.create(
            customer=self.user,
            first_name="فراز",
            last_name="آزمایش",
            phone="09120000000",
            material=material,
            quantity=1,
            description="تست پرداخت آنلاین",
            status="accepted",
        )
        self.quote = Quote.objects.create(
            order=self.order,
            material=material,
            weight_grams=100,
            print_time_minutes=60,
            machine_hourly_rate=100000,
            labor_fee=50000,
            status="accepted",
            deposit_percent=30,
        )
        self.client.force_login(self.user)

    @patch("website.payment_services.get_payment_gateway", return_value=FakeGateway())
    def _start(self, mocked_gateway, kind="deposit"):
        response = self.client.post(
            reverse("website:quote_gateway_start", args=[self.order.public_token]),
            {"payment_kind": kind},
        )
        return response

    def test_guest_cannot_start_gateway_payment(self):
        self.client.logout()
        response = self.client.post(
            reverse("website:quote_gateway_start", args=[self.order.public_token]),
            {"payment_kind": "deposit"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)
        self.assertEqual(Payment.objects.count(), 0)

    def test_other_customer_cannot_start_payment(self):
        self.client.force_login(self.other)
        response = self.client.post(
            reverse("website:quote_gateway_start", args=[self.order.public_token]),
            {"payment_kind": "deposit"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Payment.objects.count(), 0)

    def test_start_creates_pending_payment_and_redirects_to_gateway(self):
        response = self._start()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("https://gateway.example/start/"))
        payment = Payment.objects.get()
        self.assertEqual(payment.method, "gateway")
        self.assertEqual(payment.status, "pending")
        self.assertEqual(payment.amount, self.quote.deposit_amount)
        self.assertEqual(payment.gateway_amount, self.quote.deposit_amount)
        self.assertEqual(payment.gateway_currency, "IRT")
        self.assertTrue(payment.authority)
        self.assertTrue(payment.callback_token)

    def test_cancelled_callback_does_not_mark_payment_paid(self):
        self._start()
        payment = Payment.objects.get()
        response = self.client.get(
            reverse("website:quote_gateway_callback", args=[payment.callback_token]),
            {"Status": "NOK", "Authority": payment.authority},
        )
        self.assertEqual(response.status_code, 302)
        payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(payment.status, "cancelled")
        self.assertNotEqual(self.order.status, "paid")
        self.assertEqual(PaymentLedgerEntry.objects.count(), 0)

    def test_authority_mismatch_is_rejected_without_verify(self):
        self._start()
        payment = Payment.objects.get()
        with patch("website.payment_services.get_payment_gateway") as gateway_mock:
            response = self.client.get(
                reverse("website:quote_gateway_callback", args=[payment.callback_token]),
                {"Status": "OK", "Authority": "WRONG"},
            )
        self.assertEqual(response.status_code, 302)
        gateway_mock.assert_not_called()
        payment.refresh_from_db()
        self.assertEqual(payment.status, "failed")
        self.assertEqual(PaymentLedgerEntry.objects.count(), 0)

    @patch("website.payment_services.get_payment_gateway", return_value=FakeGateway())
    def test_verified_deposit_creates_exactly_one_ledger_entry(self, mocked_gateway):
        self._start()
        payment = Payment.objects.get()
        callback_url = reverse("website:quote_gateway_callback", args=[payment.callback_token])
        first = self.client.get(callback_url, {"Status": "OK", "Authority": payment.authority})
        second = self.client.get(callback_url, {"Status": "OK", "Authority": payment.authority})
        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(payment.status, "paid")
        self.assertEqual(payment.ref_id, "987654321")
        self.assertEqual(self.order.status, "accepted")
        self.assertEqual(PaymentLedgerEntry.objects.filter(payment=payment).count(), 1)
        ledger = PaymentLedgerEntry.objects.get(payment=payment)
        self.assertEqual(ledger.amount, payment.amount)
        self.assertEqual(ledger.direction, "credit")

    @patch("website.payment_services.get_payment_gateway", return_value=FakeGateway())
    def test_full_payment_marks_order_paid(self, mocked_gateway):
        self._start(kind="full")
        payment = Payment.objects.get()
        self.client.get(
            reverse("website:quote_gateway_callback", args=[payment.callback_token]),
            {"Status": "OK", "Authority": payment.authority},
        )
        payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(payment.amount, self.quote.total_price)
        self.assertEqual(payment.status, "paid")
        self.assertEqual(self.order.status, "paid")

    @override_settings(PAYMENT_GATEWAY_ENABLED=False)
    def test_disabled_gateway_does_not_create_payment(self):
        response = self.client.post(
            reverse("website:quote_gateway_start", args=[self.order.public_token]),
            {"payment_kind": "deposit"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Payment.objects.count(), 0)

    def test_unknown_callback_token_returns_404(self):
        import uuid
        response = self.client.get(
            reverse("website:quote_gateway_callback", args=[uuid.uuid4()]),
            {"Status": "OK", "Authority": "A"},
        )
        self.assertEqual(response.status_code, 404)
