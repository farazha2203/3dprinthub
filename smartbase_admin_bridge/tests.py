from __future__ import annotations

from importlib.metadata import version

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from django_smartbase_admin.admin.site import sb_admin_site
from django_smartbase_admin.messaging.models import Message, MessageRecipient


class SmartBaseAdminIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username="smartbase-test-admin",
            email="smartbase@example.test",
            password="StrongPassword123!",
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_official_package_version(self):
        self.assertEqual(version("django-smartbase-admin"), "2.3.1")

    def test_official_assets_are_discoverable(self):
        for asset in (
            "sb_admin/dist/main.js",
            "sb_admin/dist/main_style.css",
            "sb_admin/dist/table.js",
            "sb_admin/dist/chart.js",
            "smartbase_admin_bridge/css/rtl.css",
        ):
            with self.subTest(asset=asset):
                self.assertTrue(finders.find(asset), asset)

    def test_project_models_are_registered(self):
        self.assertGreater(len(sb_admin_site._registry), 0)

    def test_dashboard_loads(self):
        response = self.client.get(
            reverse("sb_admin:sb_admin_base"),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "کل سفارش‌ها")
        self.assertContains(response, "sb_admin/dist/main.js")

    def test_components_gallery_loads_in_debug(self):
        if not settings.DEBUG:
            self.skipTest("components gallery is intentionally DEBUG-only")
        response = self.client.get(reverse("sb_admin:components"))
        self.assertEqual(response.status_code, 200)

    def test_messaging_models_work(self):
        message = Message.objects.create(
            title="اعلان آزمایشی",
            type="info",
            content="تست",
        )
        MessageRecipient.objects.create(message=message, user=self.user)
        self.assertEqual(
            MessageRecipient.objects.filter(
                user=self.user,
                read_at__isnull=True,
            ).count(),
            1,
        )
