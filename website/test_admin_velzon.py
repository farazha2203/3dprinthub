from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from store.models import ProductVariant, StorePayment


class VelzonAdminIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser(
            username="velzon-admin-test",
            email="velzon@example.com",
            password="AdminTestPass123!",
        )

    def test_admin_login_uses_velzon_shell(self):
        response = self.client.get(reverse("admin:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "velzon_master/css/app-rtl.min.css")
        self.assertContains(response, "ورود مدیران")

    def test_admin_dashboard_renders_real_django_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/index.html")
        self.assertContains(response, "مرکز فرمان کسب‌وکار")
        self.assertContains(response, "همه ماژول‌های مدیریتی")

    def test_legacy_model_admin_actions_and_hooks_are_preserved(self):
        payment_admin = admin.site._registry[StorePayment]
        variant_admin = admin.site._registry[ProductVariant]

        self.assertIn("approve_payments", payment_admin.actions)
        self.assertIn("reject_payments", payment_admin.actions)
        self.assertEqual(
            type(variant_admin).save_model.__module__,
            "store.admin",
        )

    def test_smartbase_backup_route_is_available(self):
        self.client.force_login(self.admin_user)
        response = self.client.get("/smart-admin/")

        self.assertNotEqual(response.status_code, 404)

    def test_customer_cannot_open_either_admin_surface(self):
        customer = get_user_model().objects.create_user(
            username="velzon-customer-test",
            password="CustomerTestPass123!",
        )
        self.client.force_login(customer)

        self.assertEqual(self.client.get("/admin/").status_code, 404)
        self.assertEqual(self.client.get("/smart-admin/").status_code, 404)

