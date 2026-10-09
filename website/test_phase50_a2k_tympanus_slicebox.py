from pathlib import Path
from types import SimpleNamespace

from django.template.loader import render_to_string
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
        self.assertIn('id="nav-dots"', template)
        self.assertNotIn('id="nav-options"', template)
        self.assertNotIn('id="shadow"', template)
        self.assertIn("jquery.slicebox.js v1.1.0", vendor)
        self.assertIn("Licensed under the MIT license", vendor)
        self.assertNotIn("data-p50j", template)
        self.assertNotIn("phase50-a2j-slicebox-hero", template)
        self.assertIn('loading="eager"', template)
        self.assertNotIn('loading="lazy"', template)

    def test_example4_runtime_uses_reference_rotation_random_cuboids_and_disperse(self):
        runtime = self.read("static/js/phase50-a2k-tympanus-slicebox.js")
        for token in (
            'orientation: "r"',
            "cuboidsRandom: true",
            "disperseFactor: 30",
            "slicebox.next()",
            "slicebox.previous()",
            "slicebox.jump(index + 1)",
        ):
            self.assertIn(token, runtime)
        self.assertNotIn("autoplay:", runtime)
        self.assertNotIn("slicebox.play()", runtime)
        self.assertNotIn("slicebox.pause()", runtime)

    def test_reference_visual_assets_use_site_background_and_index4_frame(self):
        css = self.read("static/css/phase50-a2k-tympanus-slicebox.css")
        core = self.read("static/vendor/slicebox/css/slicebox.css")
        template = self.read("templates/website/partials/hero.html")
        self.assertIn("background: #f6f9fc", css)
        self.assertNotIn("fancy_deboss.png", css)
        self.assertNotIn("shadow.png", css)
        self.assertIn("nav.png", css)
        self.assertIn("max-width: 1280px", css)
        self.assertIn("max-width: none !important", css)
        self.assertGreaterEqual(css.count("aspect-ratio: 16 / 9"), 2)
        self.assertIn("aspect-ratio: 4 / 3", css)
        self.assertIn("border: 0 !important", css)
        self.assertIn('id="nav-dots"', template)
        self.assertNotIn('id="nav-options"', template)
        self.assertNotIn("navPlay", template)
        self.assertNotIn("navPause", template)
        self.assertIn(".sb-perspective", core)
        runtime = self.read("static/js/phase50-a2k-tympanus-slicebox.js")
        self.assertNotIn('$shadow.show()', runtime)
        self.assertIn('root.querySelector("#shadow")', runtime)
        self.assertIn("legacyShadow.remove()", runtime)
        self.assertIn(".p50k-slicebox #shadow", css)
        self.assertIn("display: none !important", css)
        self.assertIn("background: none !important", css)
        self.assertIn("box-shadow: none !important", css)
        self.assertIn("50.10.0", template)
        for relative in (
            "static/vendor/slicebox/images/nav.png",
        ):
            self.assertTrue((ROOT / relative).is_file())

    def test_ssr_product_copy_media_seo_and_link_remain_authoritative(self):
        template = self.read("templates/website/partials/hero.html")
        for token in (
            "slide.effective_title",
            "slide.effective_description",
            "slide.effective_alt_text",
            "slide.effective_image_url",
            "slide.target_url",
            "product.meta_title",
            "product.meta_description",
            "product.short_description",
            "product.seo_focus_keyword",
            "p50k-slicebox__product-copy",
        ):
            self.assertIn(token, template)
        self.assertIn('href="{{ slide.target_url }}"', template)
        # A homepage is a navigation/marketing page, not a Product rich-result
        # detail page. Structured Product + Offer belongs to the Store page.
        self.assertNotIn('itemscope', template)
        self.assertNotIn('itemtype="https://schema.org/Product"', template)
        self.assertNotIn('itemprop=', template)

    def test_six_hero_slides_render_as_links_without_six_invalid_products(self):
        slides = []
        for number in range(6):
            product = SimpleNamespace(
                meta_title=f"Sample product {number}",
                meta_description=f"Sample description {number}",
                short_description=f"Short description {number}",
                seo_focus_keyword=f"SEO term {number}",
            )
            slides.append(SimpleNamespace(
                asset=SimpleNamespace(product=product),
                target_url=f"/store/product/example-{number}/",
                effective_title=f"Sample product {number}",
                effective_alt_text=f"Photo {number}",
                effective_image_url=f"/media/example-{number}.webp",
                effective_description=f"Description {number}",
            ))
        html = render_to_string(
            "website/partials/hero.html",
            {"homepage_hero_slides": slides},
        )
        self.assertEqual(html.count('<li>'), 6)
        for number in range(6):
            self.assertIn(f'/store/product/example-{number}/', html)
            self.assertIn(f'Sample product {number}', html)
            self.assertIn(f'/media/example-{number}.webp', html)
        self.assertIn('id="sb-slider"', html)
        self.assertIn('id="nav-arrows"', html)
        self.assertIn('id="nav-dots"', html)
        self.assertNotIn('itemscope', html)
        self.assertNotIn('itemtype=', html)
        self.assertNotIn('itemprop=', html)

    def test_superseded_runtime_assets_are_deleted(self):
        self.assertFalse((ROOT / "static/css/phase50-a2j-slicebox-hero.css").exists())
        self.assertFalse((ROOT / "static/js/phase50-a2j-slicebox-hero.js").exists())

    def test_public_query_still_excludes_unsafe_assets(self):
        source = self.read("website/views.py")
        self.assertIn("asset__isnull=False", source)
        self.assertIn("asset__product__is_active=True", source)
        self.assertIn("asset__commercial_license_status__in", source)
        self.assertIn("asset__editorial_status__in", source)

    def test_public_query_prefers_product_backed_slides_before_source_fallback(self):
        source = self.read("website/views.py")
        self.assertIn("product_homepage_hero_slides = list(", source)
        self.assertIn("if product_homepage_hero_slides:", source)
        self.assertIn("homepage_hero_slides = product_homepage_hero_slides", source)
        self.assertIn("asset__product__isnull=True", source)
