from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from django.test import SimpleTestCase

from store.templatetags.store_product_presentation import product_public_facts


class _Variants:
    def filter(self, **kwargs):
        return self

    def select_related(self, *args):
        return self

    def order_by(self, *args):
        return []


class Phase49WebProductPresentationTests(SimpleTestCase):
    def _product(self):
        notes = '''منبع: MakerWorld
صفحه اصلی: https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter
طراح: -
مجوز: -
مدرک مجوز تجاری: -

{
  "estimated_weight_grams": 150.0,
  "estimated_print_minutes": 95,
  "desktop_catalog_categories_fa": ["دکور و لوازم خانه", "لوازم پذیرایی"],
  "desktop_catalog_tags_fa": ["پایه کیک", "سینی کوکی"],
  "materials": ["PLA", "PETG"],
  "colors": ["سیاه مات"],
  "sales_bullets": ["طراحی دوکاره برای سرو کیک و شیرینی"],
  "ai_provider": "avalai",
  "ai_model": "gpt-5-chat-latest",
  "fingerprint": "must-not-be-public"
}
'''
        profile = SimpleNamespace(
            license_name="",
            technical_features={"نوع ساخت": "چاپ سه‌بعدی"},
            lead_time_min_days=1,
            lead_time_max_days=3,
        )
        return SimpleNamespace(
            technical_notes=notes,
            catalog_profile=profile,
            source_name="MakerWorld",
            source_url="https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter",
            source_attribution="",
            dimensions="",
            variants=_Variants(),
        )

    def test_legacy_json_becomes_customer_facing_facts(self):
        facts = product_public_facts(self._product())
        self.assertEqual(facts["source"]["name"], "MakerWorld")
        self.assertEqual(facts["source"]["designer"], "")
        self.assertEqual(facts["source"]["license_name"], "")
        self.assertIn({"label": "وزن تقریبی", "value": "150 گرم"}, facts["specs"])
        self.assertIn({"label": "زمان تقریبی چاپ", "value": "1 ساعت و 35 دقیقه"}, facts["specs"])
        self.assertEqual(facts["materials"], ["PLA", "PETG"])
        self.assertEqual(facts["colors"], ["سیاه مات"])
        self.assertIn("دکور و لوازم خانه", facts["categories"])
        self.assertIn("پایه کیک", facts["tags"])

    def test_internal_ai_and_audit_fields_are_not_returned(self):
        rendered = repr(product_public_facts(self._product()))
        self.assertNotIn("gpt-5-chat-latest", rendered)
        self.assertNotIn("must-not-be-public", rendered)
        self.assertNotIn("ai_provider", rendered)
        self.assertNotIn("fingerprint", rendered)

    def test_product_template_never_renders_raw_technical_notes(self):
        template_path = Path(__file__).resolve().parent.parent / "templates" / "store" / "product_detail.html"
        text = template_path.read_text(encoding="utf-8")
        self.assertIn("store_product_presentation", text)
        self.assertIn("product_public_facts product as public_facts", text)
        self.assertNotIn("product.technical_notes|linebreaks", text)
        self.assertIn("منبع و اعتبار مدل", text)
        self.assertIn("مشخصات فنی و ساخت", text)
