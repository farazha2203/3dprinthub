from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from website.models import Material


def _material():
    fields = {field.name for field in Material._meta.fields}
    data = {
        "name": "PETG",
        "main_usage": "قطعات کاربردی و مقاوم",
        "sample_parts": "براکت و قاب",
    }
    if "is_active" in fields:
        data["is_active"] = True
    if "sale_price_per_gram" in fields:
        data["sale_price_per_gram"] = 5000
    return Material.objects.create(**data)


class Phase13FrontendTests(TestCase):
    """Keep the still-active Phase 13 homepage/order contracts.

    The public external ready-model catalog introduced in older phases was
    retired by Phase 49.2A, so its list/detail UI is intentionally no longer
    part of this regression module.
    """

    def test_homepage_renders_current_frontend_and_store_cta(self):
        _material()
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "phase13-frontend.css")
        self.assertContains(response, "طراحی، چاپ سه‌بعدی و مهندسی معکوس قطعات صنعتی")
        self.assertContains(response, reverse("store:product_list"))
        self.assertNotContains(response, "data-p13-order-form")
        self.assertContains(response, "قیمت هر گرم، شفاف و به‌روز")

    def test_order_wizard_has_four_named_photo_inputs_for_authenticated_customer(self):
        user = get_user_model().objects.create_user(
            username="phase13-authenticated-order",
            password="StrongPass123!",
        )
        self.client.force_login(user)
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        for field_name in ("photo_top", "photo_front", "photo_right", "photo_left"):
            self.assertContains(response, f'name="{field_name}"')
