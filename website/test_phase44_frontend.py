from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class Phase44FrontendCompatibilityTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(settings.BASE_DIR)

    def read(self, relative):
        return (self.root / relative).read_text(encoding="utf-8", errors="replace")

    def test_current_mobile_hero_contract_is_installed(self):
        css = self.read("static/css/phase45-home-hero.css")
        self.assertIn("100svh", css)
        self.assertIn("@media(max-width:820px)", css)
        self.assertIn("object-fit:var(--p45-fit,cover)", css)

    def test_current_server_rendered_hero_contract_is_preserved(self):
        hero = self.read("templates/website/partials/hero.html")
        self.assertIn("data-p45-hero", hero)
        self.assertIn("data-p45-slide", hero)
        self.assertIn("p45-hero__media", hero)
        self.assertIn('fetchpriority="high"', hero)
        self.assertNotIn("data-p27-home-hero", hero)
        self.assertNotIn("store:external_catalog", hero)

    def test_product_images_are_lazy(self):
        products = self.read("templates/website/partials/products.html")
        self.assertIn('loading="lazy"', products)
        self.assertIn('decoding="async"', products)
