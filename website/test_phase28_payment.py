from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Material, Order, Payment, Quote, SiteSetting


GIF_1X1 = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class Phase28QuotePaymentTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="phase28-pay-user",
            email="pay@example.com",
            password="StrongPass123!",
        )
        self.other_user = get_user_model().objects.create_user(
            username="phase28-other-user",
            email="other@example.com",
            password="StrongPass123!",
        )
        self.staff_user = get_user_model().objects.create_user(
            username="phase28-staff",
            email="staff@example.com",
            password="StrongPass123!",
            is_staff=True,
        )
        SiteSetting.objects.create(
            brand_name="3DPrintHub",
            payment_card_number="6037991234567890",
            payment_card_holder="فراز حراجی",
            default_deposit_percent=30,
        )
        self.material = Material.objects.create(
            name="PETG",
            price_per_kg=1_000_000,
            sale_price_per_gram=1_000,
            main_usage="قطعه کاربردی",
            sample_parts="براکت",
            is_active=True,
        )
        self.order = Order.objects.create(
            customer=self.user,
            first_name="فراز",
            last_name="حراجی",
            phone="09121234567",
            service_type="3d_print",
            material=self.material,
            quantity=1,
            description="سفارش تست پرداخت بیعانه",
            status="quoted",
        )
        self.quote = Quote.objects.create(
            order=self.order,
            material=self.material,
            weight_grams=100,
            print_time_minutes=60,
            machine_hourly_rate=100_000,
            labor_fee=50_000,
            status="sent",
            deposit_percent=30,
        )

    def test_quote_is_private_to_its_customer(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse("website:quote_detail", args=[self.order.public_token]))
        self.assertEqual(response.status_code, 404)

    def test_customer_can_accept_quote_and_submit_deposit_receipt(self):
        self.client.force_login(self.user)
        accept_response = self.client.post(reverse("website:accept_quote", args=[self.order.public_token]))
        self.assertEqual(accept_response.status_code, 302)
        self.quote.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.quote.status, "accepted")
        self.assertEqual(self.order.status, "accepted")
        self.assertGreater(self.quote.deposit_amount, 0)

        receipt = SimpleUploadedFile("receipt.gif", GIF_1X1, content_type="image/gif")
        payment_response = self.client.post(
            reverse("website:quote_payment", args=[self.order.public_token]),
            {
                "payment_kind": "deposit",
                "receipt_image": receipt,
                "note": "چهار رقم آخر کارت 1234",
            },
        )
        self.assertEqual(payment_response.status_code, 302)
        payment = Payment.objects.get(quote=self.quote)
        self.assertEqual(payment.status, "awaiting_review")
        self.assertEqual(payment.payment_kind, "deposit")
        self.assertEqual(payment.amount, self.quote.deposit_amount)
        self.assertTrue(bool(payment.receipt_image))

        secure_url = reverse("website:payment_receipt_admin", args=[payment.pk])
        customer_response = self.client.get(secure_url)
        self.assertEqual(customer_response.status_code, 302)
        self.client.force_login(self.staff_user)
        staff_response = self.client.get(secure_url)
        self.assertEqual(staff_response.status_code, 200)
        self.assertEqual(staff_response["Cache-Control"], "private, no-store, max-age=0")

    def test_duplicate_pending_deposit_is_not_created(self):
        self.quote.status = "accepted"
        self.quote.save(update_fields=["status"])
        Payment.objects.create(
            quote=self.quote,
            amount=self.quote.deposit_amount,
            payment_kind="deposit",
            method="bank_transfer",
            status="awaiting_review",
        )
        self.client.force_login(self.user)
        receipt = SimpleUploadedFile("receipt.gif", GIF_1X1, content_type="image/gif")
        self.client.post(
            reverse("website:quote_payment", args=[self.order.public_token]),
            {"payment_kind": "deposit", "receipt_image": receipt},
        )
        self.assertEqual(Payment.objects.filter(quote=self.quote).count(), 1)
