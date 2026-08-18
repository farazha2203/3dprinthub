from pathlib import Path

from django.contrib import admin
from django.test import SimpleTestCase

from website.models import HomepageHeroSlide


class Phase49_2CHeroStudioContractTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent

    def read(self, relative):
        return (self.root / relative).read_text(encoding="utf-8", errors="replace")

    def test_runtime_model_has_persistent_studio_fields(self):
        selected = HomepageHeroSlide._meta.get_field("selected_asset_image")
        self.assertEqual(selected.remote_field.model._meta.label_lower, "store.importedprintassetimage")
        self.assertTrue(selected.null)
        self.assertEqual(HomepageHeroSlide._meta.get_field("transition_effect").default, "cinematic_fade")
        self.assertEqual(HomepageHeroSlide._meta.get_field("transition_duration_ms").default, 1400)
        self.assertEqual(HomepageHeroSlide._meta.get_field("display_duration_ms").default, 7000)

    def test_migration_0020_is_additive_and_non_destructive(self):
        migration = self.read("website/migrations/0020_phase49_2c_hero_studio.py")
        self.assertIn('("website", "0019_phase45_managed_homepage_hero")', migration)
        self.assertIn('name="selected_asset_image"', migration)
        self.assertIn('to="store.importedprintassetimage"', migration)
        self.assertIn('name="transition_effect"', migration)
        self.assertIn('name="transition_duration_ms"', migration)
        self.assertIn('name="display_duration_ms"', migration)
        self.assertNotIn("DeleteModel", migration)
        self.assertNotIn("RemoveField", migration)
        self.assertNotIn("RunSQL", migration)

    def test_admin_studio_is_installed_with_album_endpoints_and_editing(self):
        model_admin = admin.site._registry[HomepageHeroSlide]
        self.assertEqual(model_admin.change_form_template, "admin/website/homepageheroslide/change_form.html")
        self.assertIn("transition_effect", model_admin.list_display)
        self.assertIn("transition_effect", model_admin.list_editable)
        self.assertIn("edit_slide_link", model_admin.list_display)
        patterns = [pattern.name for pattern in model_admin.get_urls()]
        self.assertIn("website_homepageheroslide_product_browser", patterns)
        self.assertIn("website_homepageheroslide_asset_detail", patterns)

    def test_album_picker_template_and_assets_exist(self):
        template = self.read("templates/admin/website/homepageheroslide/change_form.html")
        self.assertIn("data-p49c-products", template)
        self.assertIn("data-p49c-gallery", template)
        self.assertIn("data-p49c-preview-effect", template)
        self.assertIn("website_homepageheroslide_product_browser", template)
        self.assertIn("website_homepageheroslide_asset_detail", template)
        js = self.read("static/js/admin-phase49_2c-hero-studio.js")
        self.assertIn('setValue("id_selected_asset_image"', js)
        self.assertIn("loadProducts", js)
        self.assertIn("selectAsset", js)
        css = self.read("static/css/admin-phase49_2c-hero-studio.css")
        self.assertIn(".p49c-product", css)
        self.assertIn(".p49c-gallery", css)
        self.assertIn(".p49c-edit-link", css)

    def test_frontend_uses_per_slide_effect_and_timing_contract(self):
        hero = self.read("templates/website/partials/hero.html")
        self.assertIn("data-p49c-engine", hero)
        self.assertIn("data-p49c-effect", hero)
        self.assertIn("slide.transition_duration_ms", hero)
        self.assertIn("slide.display_duration_ms", hero)
        self.assertIn("phase49_2c-hero-effects.css", hero)
        self.assertIn("phase49_2c-home-hero.js", hero)

        engine = self.read("static/js/phase49_2c-home-hero.js")
        self.assertIn('root.removeAttribute("data-p45-hero")', engine)
        self.assertIn("displayOf", engine)
        self.assertIn("transitionOf", engine)
        self.assertIn("setTimeout", engine)
        self.assertNotIn("setInterval", engine)

    def test_all_cinematic_effects_and_accessibility_fallback_are_present(self):
        runtime = self.read("website/phase49_2c_hero_studio.py")
        styles = self.read("static/css/phase49_2c-hero-effects.css")
        for effect in (
            "cinematic_fade",
            "wedding_dissolve",
            "cinematic_zoom",
            "ken_burns",
            "soft_blur",
            "cinematic_reveal",
        ):
            self.assertIn(effect, runtime)
            self.assertIn(effect, styles)
        self.assertIn("prefers-reduced-motion:reduce", styles)
        self.assertIn("@media(max-width:600px)", styles)
