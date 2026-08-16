from __future__ import annotations

from django.test import SimpleTestCase
from django.urls import resolve, reverse

from .converters import UnicodeSlugConverter
from .epic49_publish_options import normalized_material_color_options


class Epic49UnicodeProductionRouteTests(SimpleTestCase):
    def test_percent_encoded_persian_slug_is_normalized(self):
        converter = UnicodeSlugConverter()
        self.assertEqual(
            converter.to_python("%D8%A2%D8%A8%D8%A7%DA%98%D9%88%D8%B1"),
            "آباژور",
        )

    def test_wsgi_latin1_mojibake_is_repaired(self):
        original = "آباژور"
        mojibake = original.encode("utf-8").decode("latin-1")
        self.assertEqual(UnicodeSlugConverter().to_python(mojibake), original)

    def test_percent_encoded_store_route_resolves_to_decoded_slug(self):
        match = resolve("/store/product/%D8%A2%D8%A8%D8%A7%DA%98%D9%88%D8%B1/")
        self.assertEqual(match.view_name, "store:product_detail")
        self.assertEqual(match.kwargs["slug"], "آباژور")

    def test_stable_product_id_fallback_is_registered(self):
        path = reverse("epic49_product_by_id", kwargs={"pk": 4})
        self.assertEqual(path, "/store/p/4/")
        self.assertEqual(resolve(path).view_name, "epic49_product_by_id")


class Epic49OperatorPublishContractTests(SimpleTestCase):
    def test_material_color_payload_is_normalized(self):
        result = normalized_material_color_options({
            "material_color_options_json": [
                {"material": "PLA", "color": "صورتی", "hex": "#ff69b4"},
                {"material": "pla", "color": "صورتی"},
                {"material": "PETG", "color": "مشکی"},
            ]
        })
        self.assertEqual(
            result,
            [
                {"material": "PLA", "color": "صورتی", "hex": "#ff69b4"},
                {"material": "PETG", "color": "مشکی", "hex": ""},
            ],
        )

    def test_server_sync_contract_contains_price_variant_and_slider_paths(self):
        from pathlib import Path
        root = Path(__file__).resolve().parent
        source = (root / "epic49_publish_options.py").read_text(encoding="utf-8")
        for marker in [
            "def apply_price_range",
            "def apply_material_color_variants",
            "MaterialColorOption",
            "ProductMaterialRecommendation",
            "def apply_homepage_slider",
            "HomepageHeroSlide",
            "homepage_slider_image_url",
            "material_color_options_json",
        ]:
            self.assertIn(marker, source)

    def test_store_template_exposes_price_note_and_nontracked_colors_remain_selectable(self):
        from pathlib import Path
        template = (Path(__file__).resolve().parents[1] / "templates" / "store" / "product_detail.html").read_text(encoding="utf-8")
        self.assertIn("{{ product.price_note }}", template)
        self.assertIn("variant.material.track_filament_inventory", template)
        self.assertIn("{{ variant.color.name }}", template)

    def test_hero_links_to_store_product_when_published(self):
        from pathlib import Path
        template = (Path(__file__).resolve().parents[1] / "templates" / "website" / "partials" / "hero.html").read_text(encoding="utf-8")
        self.assertIn("slide.asset.product.get_absolute_url", template)
        self.assertIn("slide.asset.product.is_active", template)


if __name__ == "__main__":
    import unittest
    unittest.main()
