from __future__ import annotations

from pathlib import Path

from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parents[1]


class Phase491FrontendContractTests(SimpleTestCase):
    def test_store_filters_have_explicit_labels_and_ids(self):
        text = (ROOT / "templates" / "store" / "product_list.html").read_text(encoding="utf-8")
        for field_id in (
            "store-filter-q",
            "store-filter-section",
            "store-filter-material",
            "store-filter-quality",
            "store-filter-sort",
        ):
            self.assertIn(f'for="{field_id}"', text)
            self.assertIn(f'id="{field_id}"', text)

    def test_public_layouts_use_approved_brand_asset_and_accessibility_assets(self):
        store_base = (ROOT / "templates" / "store" / "base.html").read_text(encoding="utf-8")
        homepage = (ROOT / "templates" / "website" / "index.html").read_text(encoding="utf-8")
        canonical_brand = "img/brand/3dprinthublogo.png"
        for text in (store_base, homepage):
            self.assertIn(canonical_brand, text)
            self.assertIn('rel="icon"', text)
            self.assertIn('rel="apple-touch-icon"', text)
            self.assertIn("phase49_1-accessibility.css", text)
            self.assertIn("phase49_1-accessibility.js", text)
            self.assertNotIn("favicon/favicon.ico", text)

    def test_legacy_favicon_pack_remains_available_but_is_not_the_brand_source_of_truth(self):
        favicon_root = ROOT / "static" / "favicon"
        self.assertTrue((favicon_root / "favicon.ico").is_file())
        self.assertTrue((favicon_root / "favicon-32x32.png").is_file())
        self.assertTrue((favicon_root / "apple-touch-icon.png").is_file())
        self.assertTrue((ROOT / "static" / "img" / "brand" / "3dprinthublogo.png").is_file())

    def test_tailwind_production_build_scaffold_exists(self):
        self.assertTrue((ROOT / "package.json").is_file())
        self.assertTrue((ROOT / "tailwind.config.js").is_file())
        self.assertTrue((ROOT / "static" / "css" / "tailwind-input.css").is_file())
        script = (ROOT / "BUILD_PHASE49_1_FRONTEND.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("tailwind-production.css", script)
        self.assertIn("git push origin $Branch", script)
