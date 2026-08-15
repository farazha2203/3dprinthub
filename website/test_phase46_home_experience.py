from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[1]


class Phase46HomeExperienceContractTests(SimpleTestCase):
    databases = set()

    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_phase45_active_home_view_is_consistent(self):
        source = self.source("website/views.py")
        self.assertIn("from website.models import HomepageHeroSlide", source)
        self.assertIn("HomepageHeroSlide.objects.filter(is_active=True)", source)

    def test_material_guide_is_tabbed_and_not_table_based(self):
        source = self.source("templates/website/partials/recommendations.html")
        self.assertIn("PHASE46_MATERIAL_GUIDE", source)
        self.assertIn('data-p46-tab="industries"', source)
        self.assertIn('data-p46-tab="parts"', source)
        self.assertNotIn("<table", source)

    def test_ready_product_order_supports_code_and_list(self):
        form = self.source("website/order_intake.py")
        template = self.source("templates/website/partials/order-form.html")
        self.assertIn("ready_catalog_code = forms.CharField", form)
        self.assertIn("resolve_ready_order_asset", form)
        self.assertIn("data-p46-ready-picker", template)
        self.assertIn("form.ready_catalog_code", template)

    def test_phase46_does_not_add_model_fields_or_migration(self):
        migration_dir = ROOT / "website" / "migrations"
        self.assertFalse(any(path.name.startswith("0020_phase46") for path in migration_dir.glob("*.py")))
        self.assertIn('return f"PH-{pk:06d}"', self.source("store/catalog_sync.py"))

    def test_catalog_surfaces_order_code(self):
        for relative in (
            "templates/website/partials/external-models-home.html",
            "templates/store/external_catalog.html",
            "templates/store/external_catalog_detail.html",
        ):
            self.assertIn("PH-", self.source(relative))

    def test_new_static_assets_are_loaded(self):
        source = self.source("templates/website/index.html")
        self.assertIn("phase46-home-experience.css", source)
        self.assertIn("phase46-home-experience.js", source)
