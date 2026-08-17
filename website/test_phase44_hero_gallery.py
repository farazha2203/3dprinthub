from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class Phase44HeroGalleryCompatibilityTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(settings.BASE_DIR)

    def test_retired_phase44_css_is_not_loaded_by_active_home(self):
        index = (self.root / "templates/website/index.html").read_text(encoding="utf-8", errors="replace")
        self.assertNotIn("css/phase27-home-hero.css", index)
        self.assertNotIn("css/phase44-hero-gallery-clear.css", index)
        self.assertIn("css/phase45-home-hero.css", index)

    def test_historical_hotfix_asset_still_documents_dimming_removal(self):
        css = (self.root / "static/css/phase44-hero-gallery-clear.css").read_text(encoding="utf-8", errors="replace")
        self.assertIn(".p27-home-hero__backdrop", css)
        self.assertIn(".p27-home-hero__veil", css)
        self.assertIn("display: none !important", css)
        self.assertIn("filter: none !important", css)
        self.assertIn("opacity: 1 !important", css)

    def test_active_mobile_contract_is_owned_by_phase45_and_phase49_2a(self):
        phase45 = (self.root / "static/css/phase45-home-hero.css").read_text(encoding="utf-8", errors="replace")
        mobile = (self.root / "static/css/phase49_2a-mobile-first.css").read_text(encoding="utf-8", errors="replace")
        self.assertIn("@media(max-width:820px)", phase45)
        self.assertIn("@media (max-width: 767px)", mobile)
        self.assertIn(".p45-hero__viewport", mobile)
