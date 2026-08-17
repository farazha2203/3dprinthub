from decimal import Decimal

from django.template import Context, Template
from django.test import TestCase

from website.models import SiteSetting

from .link_intelligence import (
    _estimate_weight_from_filament_length,
    _extract_contextual_weight,
    _extract_image_specs,
)


class Phase28ConsultationTests(TestCase):
    def setUp(self):
        SiteSetting.objects.create(
            brand_name="3DPrintHub",
            whatsapp="09121234567",
            telegram="https://t.me/3dprinthub",
            default_deposit_percent=35,
        )

    def test_consultation_links_include_active_store_product_and_support_channels(self):
        template = Template(
            "{% load store_consultation %}"
            "{% consultation_links 'براکت صنعتی' '/store/p/42/' as consult %}"
            "{{ consult.whatsapp }}|{{ consult.telegram }}|{{ consult.telegram_support }}"
        )
        rendered = template.render(Context({"request": None}))
        self.assertIn("https://wa.me/989121234567", rendered)
        self.assertIn("t.me/share/url", rendered)
        self.assertIn("https://t.me/3dprinthub", rendered)


class Phase28ExtractionTests(TestCase):
    """Extraction helpers remain covered although public link intake is retired."""

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
