import tempfile
from io import BytesIO

from PIL import Image

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from website.admin import (
    OrderReferencePhotoAdmin,
    Phase10OrderReferencePhotoInline,
    SecureOrderImageClearableFileInput,
)
from website.models import Order, OrderImage, OrderReferencePhoto


class OrderImagePreviewTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)
        self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            username="order-owner",
            password="test-password",
        )
        self.other_user = user_model.objects.create_user(
            username="other-customer",
            password="test-password",
        )
        self.staff = user_model.objects.create_superuser(
            username="order-admin",
            email="admin@example.test",
            password="test-password",
        )
        self.order = Order.objects.create(
            customer=self.owner,
            first_name="Test",
            last_name="Customer",
            phone="09120000000",
            description="Order image preview test",
        )
        self.order_image = OrderImage.objects.create(
            order=self.order,
            image=self._uploaded_jpeg("order.jpg"),
        )
        self.reference_photo = OrderReferencePhoto.objects.create(
            order=self.order,
            view_type="front",
            image=self._uploaded_jpeg("reference.jpg"),
        )

    @staticmethod
    def _uploaded_jpeg(name):
        buffer = BytesIO()
        Image.new("RGB", (8, 8), "white").save(buffer, format="JPEG")
        return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")

    def _url(self, kind, image_id):
        return reverse("website:order_image_preview", args=[kind, image_id])

    def test_order_owner_and_staff_can_preview_both_uploaded_image_types(self):
        self.client.force_login(self.owner)
        for kind, image_id in (
            ("order", self.order_image.pk),
            ("reference", self.reference_photo.pk),
        ):
            with self.subTest(kind=kind):
                response = self.client.get(self._url(kind, image_id))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "image/jpeg")
                self.assertEqual(response["Cache-Control"], "private, no-store, max-age=0")
                try:
                    self.assertEqual(b"".join(response.streaming_content)[:2], b"\xff\xd8")
                finally:
                    response.close()

        self.client.force_login(self.staff)
        response = self.client.get(self._url("reference", self.reference_photo.pk))
        try:
            self.assertEqual(response.status_code, 200)
        finally:
            response.close()

    def test_other_customer_cannot_preview_an_order_image(self):
        self.client.force_login(self.other_user)

        response = self.client.get(self._url("reference", self.reference_photo.pk))

        self.assertEqual(response.status_code, 404)

    def test_admin_gallery_uses_protected_preview_routes_not_public_media_urls(self):
        gallery = str(admin.site._registry[Order].media_gallery(self.order))

        self.assertIn(self._url("order", self.order_image.pk), gallery)
        self.assertIn(self._url("reference", self.reference_photo.pk), gallery)
        self.assertEqual(gallery.count(self._url("reference", self.reference_photo.pk)), 2)
        self.assertNotIn("/media/orders/", gallery)

    def test_reference_photo_inline_and_current_file_link_use_protected_preview(self):
        inline = Phase10OrderReferencePhotoInline(Order, admin.site)
        preview = str(inline.preview(self.reference_photo))
        field = SecureOrderImageClearableFileInput().render(
            "image", self.reference_photo.image, attrs={"id": "id_reference_image"}
        )

        self.assertIn(self._url("reference", self.reference_photo.pk), preview)
        self.assertIn(self._url("reference", self.reference_photo.pk), field)
        self.assertNotIn("/media/orders/", preview + field)
        self.assertIs(
            OrderReferencePhotoAdmin.formfield_overrides[models.ImageField]["widget"],
            SecureOrderImageClearableFileInput,
        )
