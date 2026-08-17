from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class MobileContractTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(settings.BASE_DIR)

    def read(self, relative):
        return (self.root / relative).read_text(encoding="utf-8", errors="replace")

    def test_mobile_css_is_loaded_last(self):
        name = "phase49_2a-mobile-first.css"
        index = self.read("templates/website/index.html")
        store_base = self.read("templates/store/base.html")
        self.assertIn(name, index)
        self.assertIn(name, store_base)
        self.assertGreater(index.index(name), index.index("phase47-home-polish.css"))
        self.assertGreater(store_base.index(name), store_base.index("phase49_1-accessibility.css"))

    def test_mobile_css_has_phone_breakpoints(self):
        css = self.read("static/css/phase49_2a-mobile-first.css")
        self.assertIn("@media (max-width:1023px)", css)
        self.assertIn("@media (max-width:767px)", css)
        self.assertIn("@media (max-width:479px)", css)
        self.assertIn(".p45-hero__viewport", css)
        self.assertIn(".p13-wizard__steps", css)
        self.assertIn(".store-quick-nav", css)

    def test_header_uses_mobile_nav_until_desktop(self):
        header = self.read("templates/website/partials/header.html")
        self.assertIn('aria-controls="mobile-menu"', header)
        self.assertIn('aria-expanded="false"', header)
        self.assertIn('class="mobile-menu lg:hidden', header)

    def test_current_hero_has_no_retired_public_catalog_link(self):
        hero = self.read("templates/website/partials/hero.html")
        self.assertIn("data-p45-hero", hero)
        self.assertNotIn("store:external_catalog", hero)
        self.assertNotIn("/store/ready-models/", hero)
