from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Phase493IProductListContractTests(unittest.TestCase):
    def test_installer_wraps_real_ux87_modernize_boundary(self):
        source = (ROOT / "app" / "phase49_3i_product_list.py").read_text(encoding="utf-8")
        shell = (ROOT / "app" / "ux87_shell.py").read_text(encoding="utf-8")
        self.assertIn("original_modernize = app_class._modernize_products_page", source)
        self.assertIn("app_class._modernize_products_page = _modernize_products_page", source)
        self.assertNotIn("app_class._products_ui =", source)
        self.assertIn("self._modernize_products_page()", shell)

    def test_products_surface_is_gallery_only_image_title_edit(self):
        source = (ROOT / "app" / "phase49_3i_product_list.py").read_text(encoding="utf-8")
        self.assertIn('PRODUCT_CARD_FIELDS = ("thumbnail", "title", "edit")', source)
        self.assertIn("PRODUCT_THUMBNAIL_SIZE = (260, 190)", source)
        self.assertIn('text="ویرایش محصول"', source)
        self.assertIn("tk.Canvas(shell", source)
        self.assertIn("pane.pack_forget()", source)
        self.assertIn("self.open_product_studio(product_id)", source)
        self.assertNotIn("displaycolumns=", source)

    def test_legacy_editor_is_hidden_not_destroyed(self):
        phase_source = (ROOT / "app" / "phase49_3i_product_list.py").read_text(encoding="utf-8")
        mature = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
        self.assertIn("self.fields={}", mature)
        self.assertIn("Keep them alive for compatibility", phase_source)
        self.assertNotIn("self._phase49_3i_legacy_product_pane.destroy", phase_source)

    def test_list_thumbnail_loader_is_local_only_with_fallbacks(self):
        source = (ROOT / "app" / "phase49_3i_product_list.py").read_text(encoding="utf-8")
        self.assertIn("strict_local_image", source)
        self.assertIn('local_dir / "page_extract.json"', source)
        self.assertIn('local_dir / "images"', source)
        self.assertNotIn("urlopen", source)
        self.assertNotIn("requests.get", source)

    def test_thumbnail_loading_is_batched_through_tk_after(self):
        source = (ROOT / "app" / "phase49_3i_product_list.py").read_text(encoding="utf-8")
        self.assertIn("_phase49_3i_gallery_load_queue", source)
        self.assertIn("self.after(8, self._phase49_3i_load_next_thumbnail)", source)
        self.assertIn("self.after_idle(self._phase49_3i_render_gallery)", source)

    def test_image_click_has_large_local_preview(self):
        source = (ROOT / "app" / "phase49_3i_product_list.py").read_text(encoding="utf-8")
        self.assertIn("PRODUCT_PREVIEW_SIZE = (1000, 720)", source)
        self.assertIn("_phase49_3i_open_image_preview", source)
        self.assertIn('image_label.bind("<Button-1>"', source)


if __name__ == "__main__":
    unittest.main()
