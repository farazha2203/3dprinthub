from io import BytesIO
from tempfile import TemporaryDirectory

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from store.models import (
    CatalogAssetMetrics,
    CatalogAssetPublication,
    ImportedPrintAsset,
    PrintCatalogSource,
)
from store.presentation import presentation_assets
from website.models import ClientReference, CustomerReusableModel, TeamMember


def image_bytes():
    buffer = BytesIO()
    Image.new("RGB", (48, 48), "white").save(buffer, format="JPEG")
    return buffer.getvalue()


@override_settings(MEDIA_ROOT="/tmp/phase14-media-tests")
class Phase14PresentationTests(TestCase):
    def setUp(self):
        self.source = PrintCatalogSource.objects.create(
            name="Printables Test",
            code="printables-phase14",
            base_url="https://www.printables.com/",
            allowed_domains="printables.com,www.printables.com",
        )

    def create_asset(self, title="مدل تست", with_file=True):
        asset = ImportedPrintAsset.objects.create(
            source=self.source,
            source_url=f"https://www.printables.com/model/{ImportedPrintAsset.objects.count()+1}",
            external_id=str(ImportedPrintAsset.objects.count()+1),
            title=title,
            private_download_url="https://files.example.com/model.stl" if with_file else "",
            file_format="STL",
        )
        asset.preview_image.save("preview.jpg", ContentFile(image_bytes()), save=True)
        metrics = CatalogAssetMetrics.objects.create(
            asset=asset,
            source_kind="printables",
            segment="industrial",
            downloads_count=500,
            likes_count=50,
            file_links=["https://files.example.com/model.stl"] if with_file else [],
            commercial_use_allowed=True,
            license_review_status="allowed",
            public_approved=True,
        )
        CatalogAssetPublication.objects.create(metrics=metrics, show_on_homepage=True)
        return asset

    def test_hero_assets_include_visible_references_even_without_file(self):
        with_file = self.create_asset("مدل دارای فایل", with_file=True)
        without_file = self.create_asset("مدل بدون فایل", with_file=False)
        self.assertEqual(
            {asset.pk for asset in presentation_assets(limit=10)},
            {with_file.pk, without_file.pk},
        )

    def test_anonymous_home_is_presentation_only_and_requires_login_for_order(self):
        self.create_asset()
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ورود و ثبت سفارش")
        self.assertContains(response, "data-p27-home-hero")
        self.assertNotContains(response, "data-p13-order-form")

    def test_authenticated_home_shows_order_form(self):
        user = User.objects.create_user(username="09120001010", password="StrongPass123!")
        self.client.force_login(user)
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-p13-order-form")

    def test_reorder_option_only_appears_when_customer_has_saved_model(self):
        user = User.objects.create_user(username="09120001011", password="StrongPass123!")
        self.client.force_login(user)
        response = self.client.get(reverse("website:home"))
        self.assertNotContains(response, 'value="reorder_model"')
        CustomerReusableModel.objects.create(
            customer=user,
            display_name="چرخ‌دنده محفوظ",
            internal_code="SAVED-14",
            model_file=SimpleUploadedFile("saved.stl", b"solid saved\nendsolid saved"),
            file_format="STL",
            available_for_reorder=True,
        )
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, 'value="reorder_model"')
        self.assertContains(response, "مدل‌های محفوظ من")

    def test_team_and_only_permitted_clients_are_public(self):
        TeamMember.objects.create(name="مهندس تست", role="طراح CAD", is_active=True, is_featured=True)
        ClientReference.objects.create(name="مشتری مجاز", display_permission_confirmed=True, is_active=True, is_featured=True)
        ClientReference.objects.create(name="مشتری بدون مجوز", display_permission_confirmed=False, is_active=True, is_featured=True)
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, "مهندس تست")
        self.assertContains(response, "مشتری مجاز")
        self.assertNotContains(response, "مشتری بدون مجوز")

    def test_catalog_detail_requires_login_to_order(self):
        asset = self.create_asset()
        response = self.client.get(reverse("store:external_catalog_detail", args=[asset.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ورود برای استعلام و سفارش")
        self.assertNotContains(response, ">سفارش چاپ این مدل با نرخ روز<")

    def test_image_sitemap_contains_catalog_image(self):
        asset = self.create_asset()
        response = self.client.get(reverse("store:external_catalog_sitemap"))
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        self.assertIn("xmlns:image=", body)
        self.assertIn("<image:loc>", body)
        self.assertIn(str(asset.pk), body)
