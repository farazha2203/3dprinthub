from pathlib import Path

from django.contrib import admin
from django.test import SimpleTestCase, TestCase

from website.models import SiteSetting


ROOT = Path(__file__).resolve().parents[1]


class Phase50MobileHeroContractTests(SimpleTestCase):
    def test_reference_slicebox_owns_mobile_behavior_without_legacy_override(self):
        template = (ROOT / "templates" / "website" / "partials" / "hero.html").read_text(encoding="utf-8")
        self.assertIn("phase50-a2k-tympanus-slicebox.css", template)
        self.assertIn("phase50-a2k-tympanus-slicebox.js", template)
        self.assertIn("vendor/slicebox/css/slicebox.css", template)
        self.assertNotIn("phase50-a2j-slicebox-hero", template)
        self.assertNotIn("phase50-mobile-hero.css", template)
        self.assertNotIn("phase49_3b-hero-media.css", template)
    def test_mobile_caption_is_compact_and_description_is_hidden(self):
        css = (ROOT / "static" / "css" / "phase50-a2k-tympanus-slicebox.css").read_text(encoding="utf-8")
        template = (ROOT / "templates" / "website" / "partials" / "hero.html").read_text(encoding="utf-8")
        self.assertIn("@media (max-width: 720px)", css)
        self.assertIn(".p50k-slicebox .sb-description p", css)
        self.assertIn("display: none", css)
        self.assertIn("padding: 0 12px", css)
        self.assertIn("aspect-ratio: 4 / 3", css)
        self.assertIn(".p50k-slicebox__keyword {\n    display: none;", css)
        self.assertIn("font-size: 14px", css)
        self.assertIn("v=50.8.0", template)

    def test_public_hero_frame_has_no_visible_border_or_outline(self):
        css = (ROOT / "static" / "css" / "phase50-a2k-tympanus-slicebox.css").read_text(encoding="utf-8")
        self.assertIn(".p50k-slicebox .sb-perspective", css)
        self.assertIn("border: 0 !important", css)
        self.assertIn("outline: 0 !important", css)
        self.assertIn("box-shadow: none !important", css)
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
