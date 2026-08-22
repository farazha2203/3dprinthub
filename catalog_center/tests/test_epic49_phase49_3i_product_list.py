from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Phase493IProductListContractTests(unittest.TestCase):
    def test_products_page_is_lightweight_and_routes_to_product_workspace(self):
        source = (ROOT / "app" / "phase49_3i_product_list.py").read_text(encoding="utf-8")
        self.assertIn('displaycolumns=("en",)', source)
        self.assertIn('text="📄 صفحه محصول / ویرایش کامل"', source)
        self.assertIn("pane.forget", source)
        self.assertIn("self.open_product_studio(self.current_product)", source)
        self.assertIn("self.current_product = int(selection[0])", source)

    def test_main_embedded_editor_is_hidden_not_deleted_from_mature_source(self):
        phase_source = (ROOT / "app" / "phase49_3i_product_list.py").read_text(encoding="utf-8")
        mature = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
        self.assertIn("self.fields={}", mature)
        self.assertIn("Keep the mature embedded editor widgets alive", phase_source)
        self.assertNotIn("destroy()", phase_source)

    def test_list_thumbnail_loader_is_local_only(self):
        source = (ROOT / "app" / "phase49_3i_product_list.py").read_text(encoding="utf-8")
        self.assertIn("strict_local_image", source)
        self.assertNotIn("urlopen", source)
        self.assertNotIn("requests.get", source)


if __name__ == "__main__":
    unittest.main()
