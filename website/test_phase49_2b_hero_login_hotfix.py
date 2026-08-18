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
        urls = self.read("website/urls.py")
        js = self.read("static/js/admin-phase45-hero.js")
        form = self.read("templates/admin/website/homepageheroslide/change_form.html")
        self.assertIn("hero-slide-prefill", urls)
        self.assertIn("P49_HERO_PREFILL_URL", form)
        self.assertIn("id_title_override", js)
        self.assertIn("id_group_title", js)
        self.assertIn("id_description", js)
        self.assertIn("id_image_alt_text", js)
        self.assertIn("select2:select", js)
        self.assertIn("id_is_active", js)

    def test_server_side_prefill_is_migration_free(self):
        hotfix = self.read("website/phase49_2b_hero_hotfix.py")
        self.assertIn("pre_save.connect", hotfix)
        self.assertIn("HomepageHeroSlide.effective_image_url = property", hotfix)
        self.assertIn("HomepageHeroSlide.target_url = property", hotfix)
        self.assertNotIn("AlterField", hotfix)
        self.assertNotIn("schema_editor", hotfix)

    def test_desktop_admin_login_is_not_locked_to_mobile_width(self):
        css = self.read("static/css/phase49_2b-admin.css")
        base = self.read("templates/admin/base_site.html")
        self.assertNotIn("width:min(460px,100%)", css)
        self.assertIn(".admin-login-page #content-start{width:100%!important", css)
        self.assertIn("max-width:520px!important", css)
        self.assertIn("?v=49.2.1", base)
