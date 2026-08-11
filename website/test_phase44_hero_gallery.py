from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class Phase44HeroGalleryClearTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(settings.BASE_DIR)

    def test_new_css_is_loaded_after_legacy_hero_css(self):
        index = (self.root / "templates/website/index.html").read_text(encoding="utf-8", errors="replace")
        legacy = "css/phase27-home-hero.css"
        hotfix = "css/phase44-hero-gallery-clear.css"
        self.assertIn(legacy, index)
        self.assertIn(hotfix, index)
        self.assertLess(index.index(legacy), index.index(hotfix))

    def test_hotfix_disables_dimming_layers(self):
        css = (self.root / "static/css/phase44-hero-gallery-clear.css").read_text(encoding="utf-8", errors="replace")
        self.assertIn(".p27-home-hero__backdrop", css)
        self.assertIn(".p27-home-hero__veil", css)
        self.assertIn("display: none !important", css)
        self.assertIn("filter: none !important", css)
        self.assertIn("opacity: 1 !important", css)
        self.assertIn("object-fit: contain !important", css)

    def test_mobile_gallery_has_explicit_height(self):
        css = (self.root / "static/css/phase44-hero-gallery-clear.css").read_text(encoding="utf-8", errors="replace")
        self.assertIn("@media (max-width: 900px)", css)
        self.assertIn("height: clamp(280px, 42svh, 420px) !important", css)
        self.assertIn("@media (max-width: 680px)", css)
