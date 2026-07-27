from decimal import Decimal

from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse

from website.models import Material, Order, Quote, SiteSetting

from .link_intelligence import (
    _estimate_weight_from_filament_length,
    _extract_contextual_weight,
    _extract_image_specs,
)
from .models import CustomerLinkAnalysis


class Phase28AuthenticatedConversionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="phase28-customer",
            email="phase28@example.com",
            password="StrongPass123!",
            first_name="فراز",
            last_name="حراجی",
        )
        self.material = Material.objects.create(
            name="PETG",
            price_per_kg=1_000_000,
            sale_price_per_gram=1_200,
            main_usage="قطعات کاربردی",
            sample_parts="براکت",
            is_active=True,
        )
        self.site_setting = SiteSetting.objects.create(
            brand_name="3DPrintHub",
            whatsapp="09121234567",
            telegram="https://t.me/3dprinthub",
            default_deposit_percent=35,
        )

    def create_analysis(self, **overrides):
        defaults = {
            "user": self.user,
            "source_url": "https://www.printables.com/model/123-test-part",
            "normalized_url": "https://www.printables.com/model/123-test-part",
            "source_domain": "www.printables.com",
            "source_name": "Printables",
            "title": "براکت صنعتی",
            "status": "failed",
            "error_message": "جزئیات خودکار دریافت نشد.",
            "image_url": "https://media.example.com/bracket.jpg",
            "image_urls": ["https://media.example.com/bracket.jpg"],
        }
        defaults.update(overrides)
        return CustomerLinkAnalysis.objects.create(**defaults)

    def test_guest_cannot_open_or_submit_link_analyzer(self):
        url = reverse("store:external_link_analyzer")
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 302)
        self.assertIn(reverse("website:customer_login"), get_response.url)

        post_response = self.client.post(url, {"source_url": "https://www.printables.com/model/123"})
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(CustomerLinkAnalysis.objects.count(), 0)

    def test_failed_analysis_can_be_converted_to_manual_quote(self):
        analysis = self.create_analysis()
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("store:external_link_analysis", args=[analysis.public_token]),
            {
                "action": "manual_quote",
                "full_name": "فراز حراجی",
                "phone": "09121234567",
                "quantity": 2,
                "desired_material": self.material.pk,
                "customer_note": "قطعه برای محیط صنعتی و تحمل بار متوسط است.",
            },
        )

        self.assertEqual(response.status_code, 302)
        analysis.refresh_from_db()
        self.assertIsNotNone(analysis.order_id)
        order = Order.objects.get(pk=analysis.order_id)
        self.assertEqual(order.customer, self.user)
        self.assertEqual(order.status, "reviewing")
        self.assertEqual(order.quantity, 2)
        self.assertIn(analysis.normalized_url, order.description)
        quote = Quote.objects.get(order=order)
        self.assertEqual(quote.status, "draft")
        self.assertEqual(quote.deposit_percent, Decimal("35"))
        self.assertRedirects(response, reverse("website:quote_detail", args=[order.public_token]))

    def test_consultation_links_include_product_and_support_channels(self):
        template = Template(
            "{% load store_consultation %}"
            "{% consultation_links 'براکت صنعتی' '/store/ready-models/42/' as consult %}"
            "{{ consult.whatsapp }}|{{ consult.telegram }}|{{ consult.telegram_support }}"
        )
        rendered = template.render(Context({"request": None}))
        self.assertIn("https://wa.me/989121234567", rendered)
        self.assertIn("t.me/share/url", rendered)
        self.assertIn("https://t.me/3dprinthub", rendered)


class Phase28ExtractionTests(TestCase):
    def test_extracts_contextual_weight_in_grams_and_kilograms(self):
        self.assertEqual(_extract_contextual_weight("Filament weight: 84 g"), Decimal("84.00"))
        self.assertEqual(_extract_contextual_weight("وزن قطعه 0.32 کیلوگرم"), Decimal("320.00"))

    def test_estimates_weight_from_filament_length(self):
        weight = _estimate_weight_from_filament_length(
            "Filament used: 12.5 m; filament diameter: 1.75 mm",
            "PETG",
        )
        self.assertIsNotNone(weight)
        self.assertGreater(weight, Decimal("30"))
        self.assertLess(weight, Decimal("50"))

    def test_extracts_image_count_alt_and_dimensions(self):
        specs = _extract_image_specs(
            '<img src="a.jpg" alt="نمای جلو" width="1200" height="800">'
            '<img src="b.jpg" alt="نمای پشت">'
        )
        self.assertEqual(specs["image_count_detected"], 2)
        self.assertIn("نمای جلو", specs["image_alt_samples"])
        self.assertIn("1200×800 px", specs["image_dimension_samples"])
