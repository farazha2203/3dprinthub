import base64
from unittest.mock import patch
import os

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from store.models import ImportedPrintAsset
from store.operator_notifications import send_telegram_message
from website.models import CustomerProfile, SiteSetting, SupportConversation, SupportMessage


ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZQmcAAAAASUVORK5CYII="
)


class Phase38AdminIntegrationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser(
            username="phase38admin",
            email="admin@example.com",
            password="pass12345",
        )
        self.customer = User.objects.create_user(
            username="phase38customer",
            password="pass12345",
        )
        self.site = SiteSetting.objects.create(brand_name="3DPrintHub")

    def test_support_unread_endpoint_uses_unread_key(self):
        conversation = SupportConversation.objects.create(customer=self.customer, subject="test")
        SupportMessage.objects.create(conversation=conversation, sender=self.customer, body="hello")
        self.client.force_login(self.admin)
        response = self.client.get(reverse("admin:website_supportconversation_unread_count"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["unread"], 1)

    @patch("store.operator_notifications._post_json")
    def test_telegram_can_use_database_settings(self, post_json):
        self.site.telegram_operator_enabled = True
        self.site.telegram_operator_bot_token = "token"
        self.site.telegram_operator_chat_id = "123"
        self.site.save()
        with patch.dict(os.environ, {"TELEGRAM_OPERATOR_ENABLED": "0"}, clear=False):
            sent, error = send_telegram_message("test")
        self.assertTrue(sent)
        self.assertEqual(error, "")
        post_json.assert_called_once()

    @patch("store.operator_notifications._post_json")
    def test_telegram_environment_is_fallback_without_site_settings(self, post_json):
        SiteSetting.objects.all().delete()
        with patch.dict(
            os.environ,
            {
                "TELEGRAM_OPERATOR_ENABLED": "1",
                "TELEGRAM_OPERATOR_BOT_TOKEN": "env-token",
                "TELEGRAM_OPERATOR_CHAT_ID": "456",
            },
            clear=False,
        ):
            sent, error = send_telegram_message("fallback")
        self.assertTrue(sent)
        self.assertEqual(error, "")
        post_json.assert_called_once()

    def test_contact_content_is_editable_from_site_settings(self):
        self.site.contact_eyebrow = "ارتباط مستقیم"
        self.site.contact_title = "پروژه‌ات را بررسی می‌کنیم"
        self.site.contact_description = "توضیح تست تماس"
        self.site.contact_location_title = "کارگاه تست"
        self.site.save()
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, "ارتباط مستقیم")
        self.assertContains(response, "پروژه‌ات را بررسی می‌کنیم")
        self.assertContains(response, "توضیح تست تماس")
        self.assertContains(response, "کارگاه تست")

    def test_customer_avatar_is_served_by_django(self):
        profile, _ = CustomerProfile.objects.get_or_create(user=self.customer)
        profile.avatar = SimpleUploadedFile("avatar.png", ONE_PIXEL_PNG, content_type="image/png")
        profile.save(update_fields=["avatar"])
        self.client.force_login(self.customer)
        response = self.client.get(reverse("website:customer_avatar"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertIn("no-store", response["Cache-Control"])

    def test_imported_asset_admin_keeps_phase35_preview_and_source_link(self):
        registered = admin.site._registry[ImportedPrintAsset]
        self.assertIn("preview_thumbnail", registered.list_display)
        self.assertIn("source_title_admin", registered.list_display)
        self.assertIn("price_is_final", registered.list_display)
