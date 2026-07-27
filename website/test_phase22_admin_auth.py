from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from website.forms import CustomerLoginForm, CustomerRegisterForm


class Phase22CustomerAuthTests(TestCase):
    def test_registration_requires_unique_email_and_saves_it(self):
        form = CustomerRegisterForm({
            "first_name": "فراز",
            "last_name": "حراجی",
            "phone": "09120000001",
            "email": "faraz@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.email, "faraz@example.com")

    def test_customer_can_login_with_email(self):
        User.objects.create_user(username="09120000002", email="login@example.com", password="StrongPass123!")
        form = CustomerLoginForm(None, data={"username": "LOGIN@example.com", "password": "StrongPass123!"})
        self.assertTrue(form.is_valid(), form.errors)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_sends_email(self):
        User.objects.create_user(username="09120000003", email="reset@example.com", password="StrongPass123!")
        response = self.client.post(reverse("website:customer_password_reset"), {"email": "reset@example.com"})
        self.assertRedirects(response, reverse("website:customer_password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("customer/reset/", mail.outbox[0].body)

    @override_settings(
        GOOGLE_OAUTH_ENABLED=True,
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [{"client_id": "test", "secret": "test", "key": ""}],
                "OAUTH_PKCE_ENABLED": True,
            }
        },
    )
    def test_google_button_is_available_on_login_and_register(self):
        self.assertContains(self.client.get(reverse("website:customer_login")), "ادامه با حساب گوگل")
        self.assertContains(self.client.get(reverse("website:customer_register")), "ادامه با حساب گوگل")
