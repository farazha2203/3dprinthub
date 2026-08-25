from django.contrib import admin
from django.test import TestCase

from store.models import ImportedPrintAsset, ImportedPrintAssetImage
from store.phase50_admin_media_integrity import public_asset_image, public_imported_image


class Phase50AdminMediaIntegrityTests(TestCase):
    def test_imported_asset_admin_exposes_safe_preview_and_completeness(self):
        model_admin = admin.site._registry[ImportedPrintAsset]
        self.assertIn("safe_preview", model_admin.list_display)
        self.assertIn("completeness", model_admin.list_display)
        self.assertIn("translation_status", model_admin.list_filter)
        self.assertIn("price_status", model_admin.list_filter)
        self.assertIn("commercial_license_status", model_admin.list_filter)

    def test_imported_image_inline_uses_safe_preview_and_dimensions(self):
        model_admin = admin.site._registry[ImportedPrintAsset]
        inline = next(item for item in model_admin.inlines if item.model is ImportedPrintAssetImage)
        self.assertIn("safe_preview", inline.fields)
        self.assertIn("source_dimensions", inline.fields)
        self.assertIn("safe_preview", inline.readonly_fields)
        self.assertIn("source_dimensions", inline.readonly_fields)

    def test_internal_working_media_is_never_returned_as_public_preview(self):
        class File:
            name = "store/imported-models/gallery/private.webp"

        class Images:
            def order_by(self, *args):
                return self

            def first(self):
                return None

        class Asset:
            product = None
            preview_image = File()
            remote_image_url = ""
            images = Images()

        url, source = public_asset_image(Asset())
        self.assertEqual(url, "")
        self.assertEqual(source, "ناموجود")

    def test_remote_image_is_allowed_as_last_safe_fallback(self):
        class Asset:
            product = None

        class Row:
            asset = Asset()
            image = None
            remote_url = "https://example.com/model.webp"

        url, source = public_imported_image(Row())
        self.assertEqual(url, "https://example.com/model.webp")
        self.assertEqual(source, "تصویر منبع")
