from pathlib import Path

from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parents[1]


class Phase50A2ISliceboxHeroContractTests(SimpleTestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8", errors="replace")

    def test_hero_loads_dependency_free_slicebox_layer(self):
        template = self.read("templates/website/partials/hero.html")
        self.assertIn("data-p50i-slicebox", template)
        self.assertIn("phase50-a2i-slicebox-hero.css", template)
        self.assertIn("phase50-a2i-slicebox-hero.js", template)
        self.assertLess(template.index("phase50-a2i-slicebox-hero.js"), template.index("phase49_2c-home-hero.js"))
        self.assertNotIn("jquery", template.lower())

    def test_slicebox_runtime_preserves_existing_hero_engine(self):
        runtime = self.read("static/js/phase50-a2i-slicebox-hero.js")
        engine = self.read("static/js/phase49_2c-home-hero.js")
        self.assertIn("window.P50SliceboxHero", runtime)
        self.assertIn("cloneNode(true)", runtime)
        self.assertIn("slices = 7", runtime)
        self.assertIn("prefers-reduced-motion", runtime)
        self.assertIn("window.innerWidth < 721", runtime)
        self.assertIn("P50SliceboxHero.play", engine)
        self.assertIn("data-p49c-effect", self.read("templates/website/partials/hero.html"))

    def test_css_has_segmented_3d_and_safe_fallbacks(self):
        css = self.read("static/css/phase50-a2i-slicebox-hero.css")
        self.assertIn("perspective: 1400px", css)
        self.assertIn("transform-style: preserve-3d", css)
        self.assertIn("clip-path: inset", css)
        self.assertIn("p50i-slicebox-turn", css)
        self.assertIn("max-width: 720px", css)
        self.assertIn("prefers-reduced-motion: reduce", css)

    def test_existing_ssr_copy_and_product_link_remain_authoritative(self):
        template = self.read("templates/website/partials/hero.html")
        self.assertIn("slide.effective_title", template)
        self.assertIn("slide.effective_description", template)
        self.assertIn("slide.effective_alt_text", template)
        self.assertIn("slide.target_url", template)
        self.assertIn("slide.transition_duration_ms", template)
        self.assertIn("slide.display_duration_ms", template)
