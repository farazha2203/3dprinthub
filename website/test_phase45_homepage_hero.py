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

    def test_home_uses_active_safe_asset_backed_slides_for_hero(self):
        views = self.read("website/views.py")
        self.assertIn("HomepageHeroSlide.objects.filter(", views)
        self.assertIn("is_active=True", views)
        self.assertIn("asset__isnull=False", views)
        self.assertIn("asset__product__is_active=True", views)
        self.assertIn("asset__commercial_license_status__in", views)
        self.assertIn("asset__editorial_status__in", views)
        self.assertIn('"homepage_hero_slides": homepage_hero_slides', views)
        hero = self.read("templates/website/partials/hero.html")
        self.assertIn("homepage_hero_slides", hero)
        self.assertNotIn("hero_model_slider", hero)

    def test_source_backed_hero_has_safe_order_fallback_contract(self):
        models_py = self.read("website/models.py")
        command = self.read("website/management/commands/phase50_a2k_reset_hero.py")
        self.assertIn('reverse("store:product_detail"', models_py)
        self.assertIn('reverse("website:home") + "#order"', models_py)
        self.assertNotIn('store:external_catalog_detail', models_py)
        self.assertIn("SEED_SLIDES", command)
        self.assertIn("SAFE_COMMERCIAL_STATUSES", command)
        self.assertIn('CONFIRMATION = "RESET_HOMEPAGE_HERO"', command)
        self.assertIn("A2K_HERO_RESET_DRY_RUN=PASS", command)

    def test_reference_slicebox_component_and_mobile_contract_is_current(self):
        css = self.read("static/css/phase50-a2k-tympanus-slicebox.css")
        vendor = self.read("static/vendor/slicebox/css/slicebox.css")
        self.assertIn("max-width: 840px", css)
        self.assertIn("fancy_deboss.png", css)
        self.assertIn("@media (max-width: 720px)", css)
        self.assertIn(".sb-perspective", vendor)
        self.assertIn("transform-style: preserve-3d", vendor)
    def test_fixed_site_intro_is_below_new_slider_and_h1_is_preserved(self):
        hero = self.read("templates/website/partials/hero.html")
        self.assertLess(hero.index('class="p50k-slicebox"'), hero.index('class="p45-intro"'))
        self.assertEqual(hero.count("<h1"), 1)
        self.assertIn("home-intro-title", hero)
        self.assertIn("<h1 id=\"home-intro-title\">", hero)
    def test_first_approved_slide_is_preloaded_for_lcp(self):
        index = self.read("templates/website/index.html")
        hero = self.read("templates/website/partials/hero.html")
        self.assertIn("homepage_hero_slides.0.effective_image_url", index)
        self.assertIn("phase45-home-hero.css", index)  # intro foundation remains
        self.assertNotIn("phase45-home-hero.js", index)
        self.assertIn("phase50-a2k-tympanus-slicebox.js", hero)

    def test_admin_image_picker_assets_are_installed(self):
        admin_py = self.read("website/admin.py")
        self.assertIn("HomepageHeroSlideAdmin", admin_py)
        self.assertIn("autocomplete_fields", admin_py)
        self.assertIn("candidate_image_gallery", admin_py)
        self.assertTrue((self.root / "static/js/admin-phase45-hero.js").is_file())
        self.assertTrue((self.root / "static/css/admin-phase45-hero.css").is_file())
