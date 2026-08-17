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

    def test_mobile_stylesheet_has_no_unscoped_desktop_image_reset(self):
        css = self.read("static/css/phase49_2a-mobile-first.css")
        first_breakpoint = css.index("@media (max-width:1023px)")
        prelude = css[:first_breakpoint]
        self.assertNotIn("img{height:auto}", css.replace(" ", ""))
        self.assertNotIn("html,body", prelude)
        self.assertNotIn("img,svg", prelude)

    def test_header_uses_mobile_nav_until_desktop(self):
        header = self.read("templates/website/partials/header.html")
        self.assertIn('aria-controls="mobile-menu"', header)
        self.assertIn('aria-expanded="false"', header)
        self.assertIn('class="mobile-menu lg:hidden', header)

    def test_header_brand_logo_has_hard_desktop_size_lock(self):
        header = self.read("templates/website/partials/header.html")
        self.assertIn("site-header__brand-logo", header)
        self.assertIn("height:56px", header)
        self.assertIn("max-width:220px", header)
        self.assertIn("max-height:56px", header)
        self.assertIn("object-fit:contain", header)

    def test_fallback_hero_logo_is_explicitly_capped(self):
        hero = self.read("templates/website/partials/hero.html")
        self.assertIn('class="p45-hero__fallback-logo"', hero)
        self.assertIn("max-width:320px", hero)
        self.assertIn("max-height:320px", hero)
        self.assertIn('width="320" height="320"', hero)

    def test_current_hero_has_no_retired_public_catalog_link(self):
        hero = self.read("templates/website/partials/hero.html")
        self.assertIn("data-p45-hero", hero)
        self.assertNotIn("store:external_catalog", hero)
        self.assertNotIn("/store/ready-models/", hero)
