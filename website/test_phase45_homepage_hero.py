from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class Phase45HomepageHeroContractTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(settings.BASE_DIR)

    def read(self, relative):
        return (self.root / relative).read_text(encoding="utf-8", errors="replace")

    def test_manual_hero_model_exists(self):
        models_py = self.read("website/models.py")
        self.assertIn("class HomepageHeroSlide(models.Model):", models_py)
        self.assertIn("تأیید و نمایش در اسلایدر", models_py)
        self.assertIn('"store.ImportedPrintAsset"', models_py)

    def test_home_uses_only_manually_approved_slides_for_hero(self):
        views = self.read("website/views.py")
        self.assertIn("HomepageHeroSlide.objects.filter(is_active=True)", views)
        self.assertIn('"homepage_hero_slides": homepage_hero_slides', views)
        hero = self.read("templates/website/partials/hero.html")
        self.assertIn("homepage_hero_slides", hero)
        self.assertNotIn("hero_model_slider", hero)

    def test_fullscreen_and_mobile_contract(self):
        css = self.read("static/css/phase45-home-hero.css")
        self.assertIn("100svh", css)
        self.assertIn("--p45-header-height", css)
        self.assertIn("object-fit:var(--p45-fit,cover)", css)
        self.assertIn("@media(max-width:820px)", css)
        self.assertNotIn("brightness(", css)

    def test_fixed_site_intro_is_below_slider_and_h1_is_preserved(self):
        hero = self.read("templates/website/partials/hero.html")
        self.assertLess(hero.index('class="p45-hero"'), hero.index('class="p45-intro"'))
        self.assertEqual(hero.count("<h1"), 1)
        self.assertIn("home-intro-title", hero)
        self.assertIn("ثبت سفارش ساخت قطعه", hero)

    def test_first_approved_slide_is_preloaded_for_lcp(self):
        index = self.read("templates/website/index.html")
        self.assertIn("homepage_hero_slides.0.effective_image_url", index)
        self.assertIn("phase45-home-hero.css", index)
        self.assertIn("phase45-home-hero.js", index)
        self.assertNotIn("phase27-home-hero.js", index)

    def test_admin_image_picker_assets_are_installed(self):
        admin_py = self.read("website/admin.py")
        self.assertIn("HomepageHeroSlideAdmin", admin_py)
        self.assertIn("autocomplete_fields", admin_py)
        self.assertIn("candidate_image_gallery", admin_py)
        self.assertTrue((self.root / "static/js/admin-phase45-hero.js").is_file())
        self.assertTrue((self.root / "static/css/admin-phase45-hero.css").is_file())
