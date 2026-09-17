from pathlib import Path

from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parents[1]


class Phase50A2KTympanusSliceboxContractTests(SimpleTestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8", errors="replace")

    def test_top_hero_uses_original_slicebox_structure_and_vendored_engine(self):
        template = self.read("templates/website/partials/hero.html")
        vendor = self.read("static/vendor/slicebox/js/jquery.slicebox.js")
        self.assertIn("data-p50k-slicebox", template)
        self.assertIn('id="sb-slider"', template)
        self.assertIn('class="sb-slider"', template)
        self.assertIn('id="nav-arrows"', template)
        self.assertIn('id="nav-options"', template)
        self.assertIn('id="nav-dots"', template)
        self.assertIn('id="shadow"', template)
        self.assertIn("jquery.slicebox.js v1.1.0", vendor)
        self.assertIn("Licensed under the MIT license", vendor)
        self.assertNotIn("data-p50j", template)
        self.assertNotIn("phase50-a2j-slicebox-hero", template)

    def test_combined_reference_modes_cover_play_pause_random_slices_and_disperse(self):
        runtime = self.read("static/js/phase50-a2k-tympanus-slicebox.js")
        for token in (
            'orientation: "r"',
            "cuboidsRandom: true",
            "maxCuboidsCount: 7",
            "disperseFactor: 30",
            "autoplay: true",
            "slicebox.play()",
            "slicebox.pause()",
            "slicebox.jump(index + 1)",
        ):
            self.assertIn(token, runtime)

    def test_reference_visual_assets_and_background_are_local(self):
        css = self.read("static/css/phase50-a2k-tympanus-slicebox.css")
        core = self.read("static/vendor/slicebox/css/slicebox.css")
        self.assertIn("#e4ebe9", css)
        self.assertIn("fancy_deboss.png", css)
        self.assertIn("shadow.png", css)
        self.assertIn("nav.png", css)
        self.assertIn("options.png", css)
        self.assertIn("max-width: 840px", css)
        self.assertIn(".sb-perspective", core)
        for relative in (
            "static/vendor/slicebox/images/fancy_deboss.png",
            "static/vendor/slicebox/images/shadow.png",
            "static/vendor/slicebox/images/nav.png",
            "static/vendor/slicebox/images/options.png",
        ):
            self.assertTrue((ROOT / relative).is_file())

    def test_ssr_product_copy_and_media_remain_authoritative(self):
        template = self.read("templates/website/partials/hero.html")
        for token in (
            "slide.effective_title",
            "slide.effective_description",
            "slide.effective_alt_text",
            "slide.effective_image_url",
            "slide.target_url",
        ):
            self.assertIn(token, template)

    def test_superseded_runtime_assets_are_deleted(self):
        self.assertFalse((ROOT / "static/css/phase50-a2j-slicebox-hero.css").exists())
        self.assertFalse((ROOT / "static/js/phase50-a2j-slicebox-hero.js").exists())

    def test_public_query_still_excludes_unsafe_assets(self):
        source = self.read("website/views.py")
        self.assertIn("asset__isnull=False", source)
        self.assertIn("asset__product__is_active=True", source)
        self.assertIn("asset__commercial_license_status__in", source)
        self.assertIn("asset__editorial_status__in", source)
