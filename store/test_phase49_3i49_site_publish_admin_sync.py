from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib import admin
from django.test import RequestFactory, TestCase

from catalog_bridge import unified_views
from store.epic49_catalog_profile import ProductCatalogProfile
from store.models import Category, Product
from website.models import HomepageHeroSlide


class Phase493I49SitePublishAdminSyncTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="دکور تست 3I49",
            slug="phase49-3i49-test",
            is_active=True,
        )
        self.product = Product.objects.create(
            title="محصول تست انتشار",
            title_en="Site Publish Test",
            slug="site-publish-test",
            sku="P49I49-TEST",
            category=self.category,
            fixed_price=900000,
            is_active=True,
        )
        self.profile = ProductCatalogProfile.objects.create(
            product=self.product,
            public_slug="site-publish-test",
            sync_revision=1,
        )
        self.factory = RequestFactory()

    @staticmethod
    def _media_payload():
        return {
            "homepage_slider_presentation_mode": "cinematic",
            "homepage_slider_object_fit": "contain",
            "homepage_slider_focal_position": "top",
            "homepage_slider_image_scale_percent": 116,
            "homepage_slider_position_x_percent": 42,
            "homepage_slider_position_y_percent": 58,
            "homepage_slider_background_mode": "gradient",
            "homepage_slider_background_color": "#102A43",
            "homepage_slider_background_blur_px": 24,
            "homepage_slider_desktop_max_width_percent": 82,
            "homepage_slider_desktop_max_height_percent": 86,
            "homepage_slider_mobile_max_width_percent": 94,
            "homepage_slider_mobile_max_height_percent": 70,
        }

    def test_profile_payload_contains_full_windows_slider_contract(self):
        for name, value in self._media_payload().items():
            setattr(self.profile, name, value)
        self.profile.save()

        payload = unified_views._profile_payload(self.profile)
        for name, value in self._media_payload().items():
            self.assertEqual(payload[name], value)

    def test_product_sync_round_trips_full_slider_profile_contract(self):
        payload = {
            "expected_revision": 1,
            "operator": "desktop-test",
            "profile": {
                **self._media_payload(),
                "homepage_slider_enabled": True,
                "homepage_slider_transition_effect": "ken_burns",
                "homepage_slider_transition_duration_ms": 1700,
                "homepage_slider_display_duration_ms": 8200,
                "price_mode": "fixed",
                "has_3d_file": True,
            },
        }
        request = self.factory.post(
            f"/api/catalog-bridge/v1/products/{self.product.pk}/sync/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        with patch.object(unified_views, "_authorized", return_value=True):
            response = unified_views.product_sync_view(
                request,
                self.product.pk,
            )

        self.assertEqual(response.status_code, 200, response.content)
        self.profile.refresh_from_db()
        for name, value in self._media_payload().items():
            self.assertEqual(getattr(self.profile, name), value)
        self.assertTrue(self.profile.homepage_slider_enabled)
        self.assertTrue(self.profile.has_3d_file)
        self.assertEqual(self.profile.price_mode, "fixed")
        self.assertEqual(self.profile.sync_revision, 2)

    def test_slide_media_patch_validates_desktop_equivalent_fields(self):
        slide = SimpleNamespace(
            presentation_mode="product_fit",
            object_fit="contain",
            focal_position="center",
            image_scale_percent=100,
            image_position_x_percent=50,
            image_position_y_percent=50,
            background_mode="blur",
            background_color="#071827",
            background_blur_px=18,
            desktop_max_width_percent=78,
            desktop_max_height_percent=88,
            mobile_max_width_percent=92,
            mobile_max_height_percent=72,
        )
        values = unified_views._normalized_slide_media_patch(
            slide,
            {
                "presentation_mode": "cinematic",
                "object_fit": "cover",
                "focal_position": "right",
                "image_scale_percent": 999,
                "image_position_x_percent": -3,
                "image_position_y_percent": 120,
                "background_mode": "gradient",
                "background_color": "#123456",
                "background_blur_px": 100,
                "desktop_max_width_percent": 22,
                "desktop_max_height_percent": 120,
                "mobile_max_width_percent": 95,
                "mobile_max_height_percent": 61,
            },
        )
        self.assertEqual(values["presentation_mode"], "cinematic")
        self.assertEqual(values["object_fit"], "cover")
        self.assertEqual(values["focal_position"], "right")
        self.assertEqual(values["image_scale_percent"], 140)
        self.assertEqual(values["image_position_x_percent"], 0)
        self.assertEqual(values["image_position_y_percent"], 100)
        self.assertEqual(values["background_blur_px"], 60)
        self.assertEqual(values["desktop_max_width_percent"], 30)
        self.assertEqual(values["desktop_max_height_percent"], 100)

    def test_final_admin_composition_exposes_all_slider_controls(self):
        hero_admin = admin.site._registry[HomepageHeroSlide]
        hero_fields = {
            field
            for _title, options in hero_admin.fieldsets
            for field in options.get("fields", ())
        }
        for field in (
            "presentation_mode",
            "image_scale_percent",
            "image_position_x_percent",
            "background_mode",
            "desktop_max_width_percent",
            "mobile_max_height_percent",
            "transition_effect",
            "transition_duration_ms",
            "display_duration_ms",
            "is_active",
            "sync_revision",
        ):
            self.assertIn(field, hero_fields)

        profile_admin = admin.site._registry[ProductCatalogProfile]
        profile_fields = {
            field
            for _title, options in profile_admin.fieldsets
            for field in options.get("fields", ())
        }
        for field in self._media_payload():
            self.assertIn(field, profile_fields)
        self.assertIn("homepage_slider_transition_effect", profile_fields)
        self.assertIn("sync_revision", profile_fields)
