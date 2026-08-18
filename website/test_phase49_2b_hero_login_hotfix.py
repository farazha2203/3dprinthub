from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class Phase492BHeroAndLoginHotfixContractTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(settings.BASE_DIR)

    def read(self, relative):
        return (self.root / relative).read_text(encoding="utf-8", errors="replace")

    def test_hero_runtime_uses_store_product_and_not_retired_external_catalog(self):
        hotfix = self.read("website/phase49_2b_hero_hotfix.py")
        hero = self.read("templates/website/partials/hero.html")
        self.assertIn('reverse("store:product_list")', hotfix)
        self.assertNotIn("external_catalog_detail", hotfix)
        self.assertNotIn("external_catalog_detail", hero)
        self.assertIn("{{ slide.target_url }}", hero)
        self.assertIn("slide.effective_description", hero)

    def test_admin_product_selection_prefills_hero_content(self):
        """49.2C replaces the old Select2 UI while retaining 49.2B server fallbacks."""
        urls = self.read("website/urls.py")
        legacy_hotfix = self.read("website/phase49_2b_hero_hotfix.py")
        studio_runtime = self.read("website/phase49_2c_hero_studio.py")
        studio_js = self.read("static/js/admin-phase49_2c-hero-studio.js")
        form = self.read("templates/admin/website/homepageheroslide/change_form.html")

        # 49.2B server-side compatibility remains available for non-JS/runtime paths.
        self.assertIn("hero-slide-prefill", urls)
        self.assertIn("hero_asset_prefill_view", legacy_hotfix)
        self.assertIn("pre_save.connect", legacy_hotfix)
        self.assertIn('initial.setdefault("is_active", True)', legacy_hotfix)

        # 49.2C is now the only Admin UI contract.
        self.assertIn("data-p49c-studio", form)
        self.assertIn("website_homepageheroslide_product_browser", form)
        self.assertIn("website_homepageheroslide_asset_detail", form)
        self.assertNotIn("P49_HERO_PREFILL_URL", form)
        self.assertNotIn("admin-phase45-hero.js", form)

        self.assertIn("product-browser/", studio_runtime)
        self.assertIn("asset-detail/", studio_runtime)
        self.assertIn('"id_title_override"', studio_js)
        self.assertIn('"id_group_title"', studio_js)
        self.assertIn('"id_description"', studio_js)
        self.assertIn('"id_image_alt_text"', studio_js)
        self.assertIn('setValue("id_selected_asset_image"', studio_js)
        self.assertIn("loadProducts", studio_js)
        self.assertIn("selectAsset", studio_js)

    def test_server_side_prefill_remains_as_compatibility_layer(self):
        hotfix = self.read("website/phase49_2b_hero_hotfix.py")
        self.assertIn("pre_save.connect", hotfix)
        self.assertIn("HomepageHeroSlide.effective_image_url = property", hotfix)
        self.assertIn("HomepageHeroSlide.target_url = property", hotfix)
        self.assertNotIn("AlterField", hotfix)
        self.assertNotIn("schema_editor", hotfix)

    def test_phase49_2c_ui_does_not_reload_legacy_admin_engine(self):
        form = self.read("templates/admin/website/homepageheroslide/change_form.html")
        studio = self.read("website/phase49_2c_hero_studio.py")
        self.assertNotIn("admin-phase45-hero.js", form)
        self.assertNotIn("P49_HERO_PREFILL_URL", form)
        self.assertIn("admin-phase49_2c-hero-studio.js", studio)
        self.assertIn("admin-phase49_2c-hero-studio.css", studio)

    def test_desktop_admin_login_is_not_locked_to_mobile_width(self):
        css = self.read("static/css/phase49_2b-admin.css")
        base = self.read("templates/admin/base_site.html")
        self.assertNotIn("width:min(460px,100%)", css)
        self.assertIn(".admin-login-page #content-start{width:100%!important", css)
        self.assertIn("max-width:520px!important", css)
        self.assertIn("?v=49.2.1", base)
