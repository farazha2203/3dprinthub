from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from store.models import AffiliatePayout, CostEntry, FilamentPurchase, ProductionJob, StoreOrder, StorePayment
from website.models import Payment, PaymentLedgerEntry


class Phase50AAdminCommandCenterTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username="phase50-admin",
            email="phase50@example.com",
            password="safe-test-password",
        )

    def test_command_center_requires_admin_authentication(self):
        response = self.client.get(reverse("phase50_admin_command_center"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_superuser_sees_business_oriented_command_center(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("phase50_admin_command_center"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "مرکز مالی، فروش و عملیات")
        self.assertContains(response, "فروش")
        self.assertContains(response, "خزانه‌داری")
        self.assertContains(response, "حسابداری و دفاتر موجود")
        self.assertContains(response, "خرید و تأمین")
        self.assertContains(response, "انبار و تولید")
        self.assertContains(response, "دریافت‌های خدمات")
        self.assertContains(response, "پرداخت‌های فروشگاه")
        self.assertContains(response, "دفتر رخدادهای پرداخت خدمات")
        self.assertContains(response, "خریدهای فیلامنت")
        self.assertContains(response, "کدینگ حساب‌ها: کل / معین / تفصیلی")

    def test_phase50a_admin_navigation_contract_has_no_new_models(self):
        contracts = {
            Payment: "created_at",
            PaymentLedgerEntry: "created_at",
            StorePayment: "created_at",
            StoreOrder: "created_at",
            FilamentPurchase: "purchased_at",
            CostEntry: "incurred_at",
            ProductionJob: "created_at",
            AffiliatePayout: "requested_at",
        }
        for model, expected_date_hierarchy in contracts.items():
            with self.subTest(model=model.__name__):
                model_admin = admin.site._registry.get(model)
                self.assertIsNotNone(model_admin)
                self.assertEqual(model_admin.date_hierarchy, expected_date_hierarchy)
                self.assertEqual(model_admin.list_per_page, 50)

    def test_admin_base_loads_phase50_sidebar_entry_script(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "phase50a-admin-command-center.js")
