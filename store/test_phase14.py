from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from website.models import ClientReference, CustomerReusableModel, TeamMember


@override_settings(MEDIA_ROOT="/tmp/phase14-media-tests")
class Phase14PresentationTests(TestCase):
    """Regression coverage for presentation/customer features still public.

    External ready-model presentation/detail/sitemap contracts were retired in
    Phase 49.2A. Store Products and managed homepage slides are now the public
    product presentation surface.
    """

    def test_anonymous_home_requires_login_for_order_and_links_store(self):
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ورود و ثبت سفارش")
        self.assertContains(response, reverse("store:product_list"))
        self.assertContains(response, 'class="p45-home"')
        self.assertNotContains(response, "data-p13-order-form")

    def test_authenticated_home_shows_order_form(self):
        user = User.objects.create_user(username="09120001010", password="StrongPass123!")
        self.client.force_login(user)
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-p13-order-form")

    def test_reorder_option_only_appears_when_customer_has_saved_model(self):
        user = User.objects.create_user(username="09120001011", password="StrongPass123!")
        self.client.force_login(user)
        response = self.client.get(reverse("website:home"))
        self.assertNotContains(response, 'value="reorder_model"')
        CustomerReusableModel.objects.create(
            customer=user,
            display_name="چرخ‌دنده محفوظ",
            internal_code="SAVED-14",
            model_file=SimpleUploadedFile("saved.stl", b"solid saved\nendsolid saved"),
            file_format="STL",
            available_for_reorder=True,
        )
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, 'value="reorder_model"')
        self.assertContains(response, "مدل‌های محفوظ من")

    def test_team_and_only_permitted_clients_are_public(self):
        TeamMember.objects.create(name="مهندس تست", role="طراح CAD", is_active=True, is_featured=True)
        ClientReference.objects.create(name="مشتری مجاز", display_permission_confirmed=True, is_active=True, is_featured=True)
        ClientReference.objects.create(name="مشتری بدون مجوز", display_permission_confirmed=False, is_active=True, is_featured=True)
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, "مهندس تست")
        self.assertContains(response, "مشتری مجاز")
        self.assertNotContains(response, "مشتری بدون مجوز")
