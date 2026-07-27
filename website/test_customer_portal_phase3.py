from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from store.models import StoreAddress
from website.models import CustomerProfile


class CustomerPortalPhase3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="09120000000",
            password="test-pass-123",
            first_name="فراز",
            last_name="حراجی",
        )
        self.profile = CustomerProfile.objects.create(
            user=self.user,
            phone="09120000000",
            first_name="فراز",
            last_name="حراجی",
        )
        self.client.login(username="09120000000", password="test-pass-123")

    def test_dashboard_has_professional_context(self):
        response = self.client.get(reverse("website:customer_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "فراز")
        self.assertIn("profile_completion", response.context)
        self.assertIn("store_stats", response.context)

    def test_profile_extended_fields_are_saved(self):
        response = self.client.post(reverse("website:customer_profile"), {
            "first_name": "فراز",
            "last_name": "حراجی",
            "father_name": "علی",
            "birth_date": "1979-01-01",
            "gender": "male",
            "phone": "09120000000",
            "email": "customer@example.com",
            "national_code": "0084575948",
            "landline": "03132220000",
            "occupation": "مدیر",
            "company_name": "پرینتر هاب",
        })
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.profile.father_name, "علی")
        self.assertEqual(self.profile.birth_date, date(1979, 1, 1))
        self.assertEqual(self.profile.national_code, "0084575948")
        self.assertEqual(self.user.email, "customer@example.com")

    def test_first_address_becomes_default(self):
        response = self.client.post(reverse("website:customer_address_create"), {
            "title": "منزل",
            "full_name": "فراز حراجی",
            "phone": "09120000000",
            "recipient_national_code": "0084575948",
            "province": "اصفهان",
            "county": "اصفهان",
            "city": "اصفهان",
            "district": "مرکز",
            "address": "خیابان تست",
            "plaque": "10",
            "unit": "2",
            "postal_code": "8174676471",
            "delivery_notes": "تماس قبل از تحویل",
        })
        self.assertEqual(response.status_code, 302)
        address = StoreAddress.objects.get(user=self.user)
        self.assertTrue(address.is_default)
        self.assertEqual(address.province, "اصفهان")
        self.assertEqual(address.postal_code, "8174676471")

    def test_other_user_cannot_edit_address(self):
        other = get_user_model().objects.create_user(username="09121111111", password="x")
        address = StoreAddress.objects.create(
            user=other,
            title="دیگری",
            full_name="کاربر دیگر",
            phone="09121111111",
            province="تهران",
            city="تهران",
            address="نشانی",
            postal_code="1234567890",
        )
        response = self.client.get(reverse("website:customer_address_edit", args=[address.pk]))
        self.assertEqual(response.status_code, 404)
