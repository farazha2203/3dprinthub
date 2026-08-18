from pathlib import Path

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from store.models import Category, ImportedPrintAsset, ImportedPrintAssetImage, PrintCatalogSource, Product
from website.models import HomepageHeroSlide


class Phase49_2CHeroStudioContractTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent

    def read(self, relative):
        return (self.root / relative).read_text(encoding="utf-8", errors="replace")

    def test_runtime_model_has_persistent_studio_fields(self):
        selected = HomepageHeroSlide._meta.get_field("selected_asset_image")
        self.assertEqual(selected.remote_field.model._meta.label_lower, "store.importedprintassetimage")
        self.assertTrue(selected.null)
        self.assertEqual(HomepageHeroSlide._meta.get_field("transition_effect").default, "cinematic_fade")
        self.assertEqual(HomepageHeroSlide._meta.get_field("transition_duration_ms").default, 1400)
        self.assertEqual(HomepageHeroSlide._meta.get_field("display_duration_ms").default, 7000)

    def test_migration_0020_is_additive_and_non_destructive(self):
        migration = self.read("website/migrations/0020_phase49_2c_hero_studio.py")
        self.assertIn('("website", "0019_phase45_managed_homepage_hero")', migration)
        self.assertIn('name="selected_asset_image"', migration)
        self.assertIn('to="store.importedprintassetimage"', migration)
        self.assertIn('name="transition_effect"', migration)
        self.assertIn('name="transition_duration_ms"', migration)
        self.assertIn('name="display_duration_ms"', migration)
        self.assertNotIn("DeleteModel", migration)
        self.assertNotIn("RemoveField", migration)
        self.assertNotIn("RunSQL", migration)

    def test_admin_studio_is_installed_with_album_endpoints_and_editing(self):
        model_admin = admin.site._registry[HomepageHeroSlide]
        self.assertEqual(model_admin.change_form_template, "admin/website/homepageheroslide/change_form.html")
        self.assertIn("transition_effect", model_admin.list_display)
        self.assertIn("transition_effect", model_admin.list_editable)
        self.assertIn("edit_slide_link", model_admin.list_display)
        patterns = [pattern.name for pattern in model_admin.get_urls()]
        self.assertIn("website_homepageheroslide_product_browser", patterns)
        self.assertIn("website_homepageheroslide_asset_detail", patterns)

    def test_album_picker_template_and_assets_exist(self):
        template = self.read("templates/admin/website/homepageheroslide/change_form.html")
        self.assertIn("data-p49c-products", template)
        self.assertIn("data-p49c-gallery", template)
        self.assertIn("data-p49c-preview-effect", template)
        self.assertIn("website_homepageheroslide_product_browser", template)
        self.assertIn("website_homepageheroslide_asset_detail", template)
        js = self.read("static/js/admin-phase49_2c-hero-studio.js")
        self.assertIn('setValue("id_selected_asset_image"', js)
        self.assertIn("loadProducts", js)
        self.assertIn("selectAsset", js)
        css = self.read("static/css/admin-phase49_2c-hero-studio.css")
        self.assertIn(".p49c-product", css)
        self.assertIn(".p49c-gallery", css)
        self.assertIn(".p49c-edit-link", css)

    def test_frontend_uses_per_slide_effect_and_timing_contract(self):
        hero = self.read("templates/website/partials/hero.html")
        self.assertIn("data-p49c-engine", hero)
        self.assertIn("data-p49c-effect", hero)
        self.assertIn("slide.transition_duration_ms", hero)
        self.assertIn("slide.display_duration_ms", hero)
        self.assertIn("phase49_2c-hero-effects.css", hero)
        self.assertIn("phase49_2c-home-hero.js", hero)

        engine = self.read("static/js/phase49_2c-home-hero.js")
        self.assertIn('root.removeAttribute("data-p45-hero")', engine)
        self.assertIn("displayOf", engine)
        self.assertIn("transitionOf", engine)
        self.assertIn("setTimeout", engine)
        self.assertNotIn("setInterval", engine)

    def test_all_cinematic_effects_and_accessibility_fallback_are_present(self):
        runtime = self.read("website/phase49_2c_hero_studio.py")
        styles = self.read("static/css/phase49_2c-hero-effects.css")
        for effect in (
            "cinematic_fade",
            "wedding_dissolve",
            "cinematic_zoom",
            "ken_burns",
            "soft_blur",
            "cinematic_reveal",
        ):
            self.assertIn(effect, runtime)
            self.assertIn(effect, styles)
        self.assertIn("prefers-reduced-motion:reduce", styles)
        self.assertIn("@media(max-width:600px)", styles)


class Phase49_2CHeroStudioBehaviorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username="phase49c-admin",
            email="phase49c@example.com",
            password="StrongTestPass123!",
        )
        cls.category = Category.objects.create(name="قطعات تست Hero", slug="phase49c-hero")
        cls.product = Product.objects.create(
            category=cls.category,
            title="چرخ دنده تست Hero Studio",
            title_en="Hero Studio Test Gear",
            slug="phase49c-test-gear",
            sku="P49C-GEAR-001",
            short_description="توضیح کوتاه محصول تست",
            description="توضیحات کامل محصول تست برای Hero Studio",
            main_image="store/products/phase49c-main.jpg",
            is_active=True,
        )
        cls.source = PrintCatalogSource.objects.create(
            name="Phase49C Test Source",
            code="phase49c-test-source",
            base_url="https://example.com/",
        )
        cls.asset = ImportedPrintAsset.objects.create(
            source=cls.source,
            source_url="https://example.com/models/gear",
            external_id="P49C-ASSET-001",
            title="Hero Test Gear",
            persian_title="چرخ دنده فارسی Hero",
            persian_short_description="توضیح فارسی اختصاصی اسلایدر",
            product=cls.product,
        )
        cls.asset_image = ImportedPrintAssetImage.objects.create(
            asset=cls.asset,
            remote_url="https://example.com/images/gear-hero.jpg",
            image="store/imported-models/gallery/phase49c-hero.jpg",
            alt_text="چرخ دنده تست در Hero",
            is_primary=True,
            is_selected=True,
            sort_order=0,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_product_browser_returns_visual_product_card_payload(self):
        response = self.client.get(
            reverse("admin:website_homepageheroslide_product_browser"),
            {"q": "P49C-GEAR-001"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        matches = [item for item in payload["items"] if item["sku"] == "P49C-GEAR-001"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["asset_id"], self.asset.pk)
        self.assertEqual(matches[0]["category"], self.category.name)

    def test_asset_detail_returns_real_image_ids_without_initial_slide_save(self):
        response = self.client.get(
            reverse("admin:website_homepageheroslide_asset_detail"),
            {"asset_id": self.asset.pk},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        image_ids = [row["id"] for row in payload["images"] if row["id"] is not None]
        self.assertIn(self.asset_image.pk, image_ids)
        self.assertEqual(payload["suggestions"]["title"], "چرخ دنده فارسی Hero")

    def test_selected_asset_image_is_persistent_and_has_render_priority(self):
        slide = HomepageHeroSlide.objects.create(
            asset=self.asset,
            selected_asset_image=self.asset_image,
            image_url="https://example.com/images/legacy-fallback.jpg",
            transition_effect="wedding_dissolve",
            transition_duration_ms=1800,
            display_duration_ms=8500,
            is_active=True,
        )
        slide.refresh_from_db()
        self.assertEqual(slide.selected_asset_image_id, self.asset_image.pk)
        self.assertEqual(slide.transition_effect, "wedding_dissolve")
        self.assertEqual(slide.transition_duration_ms, 1800)
        self.assertEqual(slide.display_duration_ms, 8500)
        self.assertTrue(slide.effective_image_url.endswith("/store/imported-models/gallery/phase49c-hero.jpg"))
