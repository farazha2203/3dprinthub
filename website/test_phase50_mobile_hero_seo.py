from pathlib import Path

from django.contrib import admin
from django.test import SimpleTestCase, TestCase

from website.models import SiteSetting


ROOT = Path(__file__).resolve().parents[1]


class Phase50MobileHeroContractTests(SimpleTestCase):
    def test_mobile_hero_override_is_loaded_after_phase49_media_styles(self):
        template = (ROOT / "templates" / "website" / "partials" / "hero.html").read_text(encoding="utf-8")
        self.assertIn("phase50-mobile-hero.css", template)
        self.assertGreater(template.index("phase50-mobile-hero.css"), template.index("phase49_3b-hero-media.css"))

    def test_mobile_caption_is_compact_and_small_phone_hides_description(self):
        css = (ROOT / "static" / "css" / "phase50-mobile-hero.css").read_text(encoding="utf-8")
        self.assertIn("max-height: 36svh", css)
        self.assertIn("font-size: clamp(1rem, 4.4vw, 1.38rem)", css)
        self.assertIn("max-width: 420px", css)
        self.assertIn(".p49c-hero__description", css)
        self.assertIn("display: none", css)


class Phase50HomepageSeoAdminTests(TestCase):
    def test_existing_site_setting_is_extended_not_replaced(self):
        model_admin = admin.site._registry[SiteSetting]
        self.assertIn("homepage_seo_health", model_admin.readonly_fields)
        self.assertIn("homepage_search_preview", model_admin.readonly_fields)
        self.assertIn("homepage_hero_seo_status", model_admin.readonly_fields)
        seo_sections = [options for title, options in model_admin.fieldsets if title == "SEO صفحه اصلی"]
        self.assertEqual(len(seo_sections), 1)
        fields = seo_sections[0]["fields"]
        self.assertIn("meta_title", fields)
        self.assertIn("meta_description", fields)
