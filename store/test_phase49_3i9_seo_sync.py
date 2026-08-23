from __future__ import annotations

import types

from django.test import SimpleTestCase

from store.phase49_3i9_seo_sync import apply_catalog_seo_to_product


class _Product:
    def __init__(self):
        self.source_name = ""
        self.source_attribution = ""
        self.editorial_source_url = ""
        self.meta_title = ""
        self.meta_description = ""
        self.og_title = ""
        self.og_description = ""
        self.seo_focus_keyword = ""
        self.saved_fields = []

    def save(self, update_fields=None):
        self.saved_fields = list(update_fields or [])


class Phase493I9SeoSyncTests(SimpleTestCase):
    def test_desktop_seo_and_publisher_reach_real_product_fields(self):
        product = _Product()
        asset = types.SimpleNamespace(
            source=types.SimpleNamespace(name="MakerWorld"),
            source_url="https://makerworld.com/en/models/3132472-example",
        )
        data = {
            "source_name": "MakerWorld",
            "source_code": "makerworld",
            "source_url": asset.source_url,
            "seo_title_fa": "جا شمعی کدو تنبل هالووین | سفارش چاپ سه‌بعدی",
            "seo_description_fa": "جا شمعی وارمر طرح کدو تنبل هالووین با طراحی گوتیک و امکان سفارش چاپ سه‌بعدی.",
            "keywords_json": '["جا شمعی هالووین", "خرید دکور هالووین"]',
        }
        updates = apply_catalog_seo_to_product(product, asset, data)
        self.assertEqual(product.source_name, "MakerWorld")
        self.assertEqual(product.source_attribution, "MakerWorld")
        self.assertEqual(product.editorial_source_url, asset.source_url)
        self.assertEqual(product.meta_title, data["seo_title_fa"])
        self.assertEqual(product.meta_description, data["seo_description_fa"])
        self.assertEqual(product.og_title, data["seo_title_fa"])
        self.assertEqual(product.og_description, data["seo_description_fa"])
        self.assertEqual(product.seo_focus_keyword, "جا شمعی هالووین")
        self.assertIn("meta_title", updates)
        self.assertIn("source_attribution", updates)

    def test_converter_is_wrapped_in_store_composition_root(self):
        from pathlib import Path
        apps = (Path(__file__).resolve().parent / "apps.py").read_text(encoding="utf-8")
        module = (Path(__file__).resolve().parent / "phase49_3i9_seo_sync.py").read_text(encoding="utf-8")
        self.assertIn("install_phase49_3i9_seo_sync()", apps)
        self.assertIn("publishing.convert_to_fixed_product = convert_to_fixed_product", module)
        self.assertNotIn("Product.objects.create", module)


