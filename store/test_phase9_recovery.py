from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from website.models import Material


User = get_user_model()


class Phase89RecoveryRegressionTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="phase89-recovery-admin",
            email="phase89@example.com",
            password="StrongAdminPass123!",
        )
        self.client.force_login(self.admin)

    def test_material_admin_changelist_renders(self):
        Material.objects.create(
            name="PLA Recovery Test",
            price_per_kg=2_500_000,
            main_usage="تست",
            sample_parts="تست",
        )
        response = self.client.get(reverse("admin:website_material_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PLA Recovery Test")

    def test_external_catalog_route_resolves_and_renders(self):
        response = self.client.get(reverse("store:external_catalog"))
        self.assertEqual(response.status_code, 200)
