from pathlib import Path

from django.contrib import admin
from django.test import SimpleTestCase, TestCase

from store.models import Category, ImportedPrintAsset, PrintCatalogSource, Product
from website.models import HomepageHeroSlide


class Phase493BHeroMediaContractTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent

    def read(self, relative):
        return (self.root / relative).read_text(encoding="utf-8", errors="replace")

    def test_runtime_model_has_media_presentation_fields(self):
        defaults = {
            "presentation_mode": "product_fit",
            "image_scale_percent": 100,
            "image_position_x_percent": 50,
            "image_position_y_percent": 50,
            "background_mode": "blur",
            "background_color": "#071827",
            "background_blur_px": 18,
            "desktop_max_width_percent": 78,
            "desktop_max_height_percent": 88,
            "mobile_max_width_percent": 92,
            "mobile_max_height_percent": 72,
        }
        for name, default in defaults.items():
            self.assertEqual(HomepageHeroSlide._meta.get_field(name).default, default)

    def test_migration_0022_is_additive(self):
        migration = self.read("website/migrations/0022_phase49_hero_media_presentation.py")
        self.assertIn('("website", "0021_phase49_unified_hero_sync")', migration)
        for name in (
            "presentation_mode",
            "image_scale_percent",
            "image_position_x_percent",
            "image_position_y_percent",
            "background_mode",
            "background_color",
            "background_blur_px",
            "desktop_max_width_percent",
            "mobile_max_height_percent",
        ):
            self.assertIn(f'name="{name}"', migration)
        self.assertNotIn("DeleteModel", migration)
        self.assertNotIn("RemoveField", migration)
        self.assertNotIn("RunSQL", migration)

    def test_admin_exposes_media_controls(self):
        model_admin = admin.site._registry[HomepageHeroSlide]
        flattened = []
        for _title, options in model_admin.fieldsets:
            flattened.extend(options.get("fields") or [])
        for name in (
            "presentation_mode", "object_fit", "image_scale_percent",
            "image_position_x_percent", "image_position_y_percent",
            "background_mode", "desktop_max_width_percent", "mobile_max_height_percent",
        ):
            self.assertIn(name, flattened)

    def test_public_hero_renders_media_contract_and_new_css(self):
        hero = self.read("templates/website/partials/hero.html")
        css = self.read("static/css/phase49_3b-hero-media.css")
        for token in (
            "phase49_3b-hero-media.css",
            "slide.presentation_mode",
            "slide.background_mode",
            "slide.image_position_x_percent",
            "slide.image_scale_percent",
            "slide.desktop_max_width_percent",
            "slide.mobile_max_height_percent",
        ):
            self.assertIn(token, hero)
        self.assertIn('data-p49b-presentation="full_bleed"', css)
        self.assertIn("object-fit:var(--p45-fit,contain)!important", css)
        self.assertIn("--p49b-mobile-w", css)


class Phase493BHeroMediaBehaviorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Hero Media Test", slug="hero-media-test")
        cls.product = Product.objects.create(
            category=cls.category,
            title="محصول تست قاب‌بندی Hero",
            title_en="Hero Media Product",
            slug="hero-media-product",
            sku="P493B-HERO-001",
            short_description="توضیح تست",
            description="توضیح کامل تست",
            is_active=True,
        )
        cls.source = PrintCatalogSource.objects.create(name="Hero Media Source", code="hero-media-source", base_url="https://example.com/")
        cls.asset = ImportedPrintAsset.objects.create(
            source=cls.source,
            source_url="https://example.com/models/media",
            external_id="P493B-ASSET",
            title="Hero Media Asset",
            persian_title="محصول تست قاب‌بندی Hero",
            product=cls.product,
        )

    def test_desktop_publish_contract_applies_media_values(self):
        from store.epic49_publish_options import apply_homepage_slider

        result = apply_homepage_slider(self.product, self.asset, {
            "homepage_slider_enabled": True,
            "homepage_slider_title_fa": "خرید محصول تست قاب‌بندی Hero",
            "homepage_slider_description_fa": "توضیح فارسی کوتاه برای اسلایدر",
            "homepage_slider_alt_text": "تصویر محصول تست قاب‌بندی Hero",
            "homepage_slider_button_text": "مشاهده محصول",
            "homepage_slider_focus_keyword": "خرید محصول تست",
            "homepage_slider_presentation_mode": "cinematic",
            "homepage_slider_object_fit": "contain",
            "homepage_slider_focal_position": "center",
            "homepage_slider_image_scale_percent": 86,
            "homepage_slider_position_x_percent": 43,
            "homepage_slider_position_y_percent": 57,
            "homepage_slider_background_mode": "blur",
            "homepage_slider_background_color": "#112233",
            "homepage_slider_background_blur_px": 24,
            "homepage_slider_desktop_max_width_percent": 74,
            "homepage_slider_desktop_max_height_percent": 82,
            "homepage_slider_mobile_max_width_percent": 91,
            "homepage_slider_mobile_max_height_percent": 69,
        })
        self.assertTrue(result["enabled"])
        slide = HomepageHeroSlide.objects.get(pk=result["slide_id"])
        self.assertEqual(slide.presentation_mode, "cinematic")
        self.assertEqual(slide.object_fit, "contain")
        self.assertEqual(slide.image_scale_percent, 86)
        self.assertEqual(slide.image_position_x_percent, 43)
        self.assertEqual(slide.image_position_y_percent, 57)
        self.assertEqual(slide.background_mode, "blur")
        self.assertEqual(slide.background_color, "#112233")
        self.assertEqual(slide.background_blur_px, 24)
        self.assertEqual(slide.desktop_max_width_percent, 74)
        self.assertEqual(slide.mobile_max_height_percent, 69)

    def test_bridge_serializer_exposes_media_fields(self):
        from catalog_bridge.unified_views import serialize_slide

        slide = HomepageHeroSlide.objects.create(
            asset=self.asset,
            presentation_mode="framed",
            object_fit="contain",
            image_scale_percent=90,
            image_position_x_percent=44,
            image_position_y_percent=55,
            background_mode="solid",
            background_color="#223344",
            is_active=True,
        )
        payload = serialize_slide(slide)
        self.assertEqual(payload["presentation_mode"], "framed")
        self.assertEqual(payload["image_scale_percent"], 90)
        self.assertEqual(payload["image_position_x_percent"], 44)
        self.assertEqual(payload["background_color"], "#223344")
