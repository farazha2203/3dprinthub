from pathlib import Path

from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parents[1]


class Phase50A2JStandaloneSliceboxHeroContractTests(SimpleTestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8", errors="replace")

    def test_top_hero_is_fully_owned_by_standalone_slicebox_runtime(self):
        template = self.read("templates/website/partials/hero.html")
        index = self.read("templates/website/index.html")
        self.assertIn("data-p50j-slicebox", template)
        self.assertIn('data-p50j-version="50.4.0"', template)
        self.assertIn("phase50-a2j-slicebox-hero.css", template)
        self.assertIn("phase50-a2j-slicebox-hero.js", template)
        self.assertNotIn("phase49_2c-home-hero.js", template)
        self.assertNotIn("phase50-a2i-slicebox-hero.js", template)
        self.assertNotIn("data-p49c-engine", template)
        self.assertNotIn("data-p45-hero", template)
        self.assertNotIn("phase45-home-hero.js", index)
        self.assertNotIn("jquery", template.lower())

    def test_runtime_owns_navigation_autoplay_swipe_keyboard_and_jump(self):
        runtime = self.read("static/js/phase50-a2j-slicebox-hero.js")
        for token in (
            "data-p50j-next",
            "data-p50j-prev",
            "data-p50j-dot",
            "visibilitychange",
            "touchstart",
            "touchend",
            "ArrowLeft",
            "ArrowRight",
            "setTimeout",
        ):
            self.assertIn(token, runtime)
        self.assertNotIn("P50SliceboxHero", runtime)
        self.assertNotIn("setInterval", runtime)

    def test_revised_slicebox_options_and_fallbacks_are_native(self):
        runtime = self.read("static/js/phase50-a2j-slicebox-hero.js")
        template = self.read("templates/website/partials/hero.html")
        css = self.read("static/css/phase50-a2j-slicebox-hero.css")
        for token in (
            "data-p50j-orientation",
            "data-p50j-cuboids-random",
            "data-p50j-max-cuboids",
            "data-p50j-perspective",
            "data-p50j-disperse",
            "data-p50j-sequential",
        ):
            self.assertIn(token, template)
        self.assertIn("cuboidCount", runtime)
        self.assertIn("orientation", runtime)
        self.assertIn("prefers-reduced-motion", runtime)
        self.assertIn("window.innerWidth >= 721", runtime)
        self.assertIn("transform-style: preserve-3d", css)
        self.assertIn("p50j-cuboid-v", css)
        self.assertIn("p50j-cuboid-h", css)
        self.assertIn("max-width: 720px", css)
        self.assertIn("prefers-reduced-motion: reduce", css)

    def test_ssr_product_copy_media_and_timing_remain_authoritative(self):
        template = self.read("templates/website/partials/hero.html")
        for token in (
            "slide.effective_title",
            "slide.effective_description",
            "slide.effective_alt_text",
            "slide.effective_image_url",
            "slide.target_url",
            "slide.transition_duration_ms",
            "slide.display_duration_ms",
            "slide.image_scale_percent",
            "slide.image_position_x_percent",
            "slide.mobile_max_height_percent",
        ):
            self.assertIn(token, template)

    def test_public_query_fail_closes_orphaned_or_inactive_products(self):
        source = self.read("website/views.py")
        self.assertIn("asset__product__is_active=True", source)
        self.assertIn('"asset__product"', source)
