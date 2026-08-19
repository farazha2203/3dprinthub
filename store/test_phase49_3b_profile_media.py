from pathlib import Path

from django.contrib import admin
from django.test import SimpleTestCase, TestCase

from store.epic49_catalog_profile import ProductCatalogProfile
from store.models import Category, Product


class Phase493BProfileMediaContractTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent

    def test_profile_runtime_has_hero_media_fields(self):
        defaults = {
            "homepage_slider_presentation_mode": "product_fit",
            "homepage_slider_object_fit": "contain",
            "homepage_slider_focal_position": "center",
            "homepage_slider_image_scale_percent": 100,
            "homepage_slider_position_x_percent": 50,
            "homepage_slider_position_y_percent": 50,
            "homepage_slider_background_mode": "blur",
            "homepage_slider_background_color": "#071827",
            "homepage_slider_background_blur_px": 18,
            "homepage_slider_desktop_max_width_percent": 78,
            "homepage_slider_desktop_max_height_percent": 88,
            "homepage_slider_mobile_max_width_percent": 92,
            "homepage_slider_mobile_max_height_percent": 72,
        }
        for name, default in defaults.items():
            self.assertEqual(ProductCatalogProfile._meta.get_field(name).default, default)

    def test_store_0032_is_additive(self):
        text = (self.root / "store/migrations/0032_phase49_slider_media_profile.py").read_text(encoding="utf-8")
        self.assertIn('("store", "0031_phase49_rich_material_colors")', text)
        self.assertIn('name="homepage_slider_presentation_mode"', text)
        self.assertIn('name="homepage_slider_mobile_max_height_percent"', text)
        self.assertNotIn("DeleteModel", text)
        self.assertNotIn("RemoveField", text)
        self.assertNotIn("RunSQL", text)

    def test_profile_admin_exposes_media_controls(self):
        model_admin = admin.site._registry[ProductCatalogProfile]
        flattened = []
        for _title, options in model_admin.fieldsets:
            flattened.extend(options.get("fields") or [])
        for name in (
            "homepage_slider_presentation_mode",
            "homepage_slider_object_fit",
            "homepage_slider_image_scale_percent",
            "homepage_slider_background_mode",
            "homepage_slider_mobile_max_height_percent",
        ):
            self.assertIn(name, flattened)


class Phase493BProfileMediaBehaviorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Profile Hero", slug="profile-hero")
        cls.product = Product.objects.create(
            category=category,
            title="محصول تست Profile Hero",
            title_en="Profile Hero Product",
            slug="profile-hero-product",
            sku="P493B-PROFILE-001",
            short_description="توضیح تست",
            description="توضیح کامل",
            is_active=True,
        )
        cls.profile = ProductCatalogProfile.objects.create(
            product=cls.product,
            public_slug="profile-hero-product-public",
        )

    def test_windows_style_values_persist_without_active_slide(self):
        from store.phase49_3b_profile_media import apply_profile_media

        changed = apply_profile_media(self.profile, {
            "homepage_slider_presentation_mode": "framed",
            "homepage_slider_object_fit": "contain",
            "homepage_slider_focal_position": "top",
            "homepage_slider_image_scale_percent": 84,
            "homepage_slider_position_x_percent": 46,
            "homepage_slider_position_y_percent": 52,
            "homepage_slider_background_mode": "gradient",
            "homepage_slider_background_color": "#223344",
            "homepage_slider_background_blur_px": 22,
            "homepage_slider_desktop_max_width_percent": 72,
            "homepage_slider_desktop_max_height_percent": 81,
            "homepage_slider_mobile_max_width_percent": 90,
            "homepage_slider_mobile_max_height_percent": 68,
        })
        self.assertIn("homepage_slider_presentation_mode", changed)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.homepage_slider_presentation_mode, "framed")
        self.assertEqual(self.profile.homepage_slider_image_scale_percent, 84)
        self.assertEqual(self.profile.homepage_slider_background_mode, "gradient")
        self.assertEqual(self.profile.homepage_slider_mobile_max_height_percent, 68)

    def test_bridge_product_payload_exposes_profile_media(self):
        from catalog_bridge.unified_views import serialize_product

        self.profile.homepage_slider_presentation_mode = "cinematic"
        self.profile.homepage_slider_image_scale_percent = 87
        self.profile.homepage_slider_background_mode = "blur"
        self.profile.save()
        payload = serialize_product(self.product)
        profile = payload["profile"]
        self.assertEqual(profile["homepage_slider_presentation_mode"], "cinematic")
        self.assertEqual(profile["homepage_slider_image_scale_percent"], 87)
        self.assertEqual(profile["homepage_slider_background_mode"], "blur")
