from pathlib import Path

from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parents[1]


class Phase50A2KProductDetailFilamentUXTests(SimpleTestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8", errors="replace")

    def test_redundant_filament_gallery_is_removed_and_guided_wizard_remains(self):
        template = self.read("templates/store/product_detail.html")
        views = self.read("store/views.py")
        self.assertNotIn("filament_visual_options", template)
        self.assertNotIn("filament_visual_options", views)
        self.assertNotIn("\u0631\u0646\u06af \u0648 Filament \u0642\u0627\u0628\u0644 \u0633\u0641\u0627\u0631\u0634", template)
        base = self.read("templates/store/base.html")
        runtime = self.read("static/store/js/phase50-profile-selector.js")
        self.assertIn('id="variant-select"', template)
        self.assertIn("phase50-profile-selector.js", base)
        self.assertIn('shell.className = "store-profile-selector"', runtime)
        self.assertIn('document.getElementById("variant-select")', runtime)

    def test_material_step_renders_description_usage_and_examples_from_variant_api(self):
        runtime = self.read("static/store/js/phase50-profile-selector.js")
        styles = self.read("static/store/css/phase50-profile-selector.css")
        endpoint = self.read("store/phase50_variant_views.py")
        for token in ("material_description", "material_main_usage", "material_sample_parts"):
            self.assertIn(token, endpoint)
        self.assertIn("materialMainUsage", runtime)
        self.assertIn("materialSampleParts", runtime)
        self.assertIn("store-profile-material-help", runtime)
        self.assertIn(".store-profile-material-help", styles)
