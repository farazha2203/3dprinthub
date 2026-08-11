from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class Phase44FrontendExactSourceTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(settings.BASE_DIR)

    def read(self, relative):
        return (self.root / relative).read_text(encoding="utf-8", errors="replace")

    def test_hero_clear_mobile_override_is_installed(self):
        css = self.read("static/css/phase27-home-hero.css")
        self.assertIn("BEGIN PHASE 44.0.1 CLEAR HERO", css)
        self.assertIn("display:none!important", css)
        self.assertIn("object-fit:contain!important", css)
        self.assertIn("height:clamp(250px,38svh,340px)!important", css)
        self.assertIn("z-index:0!important", css)

    def test_existing_server_rendered_hero_contract_is_preserved(self):
        hero = self.read("templates/website/partials/hero.html")
        self.assertIn("data-p27-home-hero", hero)
        self.assertIn("data-p27-hero-slide", hero)
        self.assertIn("p27-home-hero__subject", hero)
        self.assertIn('fetchpriority="high"', hero)

    def test_product_images_are_lazy(self):
        products = self.read("templates/website/partials/products.html")
        self.assertIn('loading="lazy"', products)
        self.assertIn('decoding="async"', products)
