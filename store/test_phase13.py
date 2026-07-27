from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from store.models import (
    CatalogAssetMetrics,
    CatalogAssetPublication,
    CatalogSourcePolicy,
    ImportedPrintAsset,
    PrintCatalogSource,
)
from website.models import Material


def _image(name="phase13.jpg"):
    buffer = BytesIO()
    Image.new("RGB", (64, 64), "white").save(buffer, format="JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


def _material():
    fields = {field.name for field in Material._meta.fields}
    data = {
        "name": "PETG",
        "main_usage": "قطعات کاربردی و مقاوم",
        "sample_parts": "براکت و قاب",
    }
    if "is_active" in fields:
        data["is_active"] = True
    if "sale_price_per_gram" in fields:
        data["sale_price_per_gram"] = 5000
    return Material.objects.create(**data)


def _asset(*, homepage=True):
    source = PrintCatalogSource.objects.create(
        name="Printables",
        code="phase13-printables",
        base_url="https://www.printables.com/",
        allowed_domains="www.printables.com,printables.com",
        adapter_key="printables",
    )
    CatalogSourcePolicy.objects.create(
        source=source,
        source_kind="printables",
        discovery_mode="public_html",
        public_display_policy="licensed_only",
    )
    asset = ImportedPrintAsset.objects.create(
        source=source,
        source_url="https://www.printables.com/model/13001",
        external_id="13001",
        title="براکت صنعتی آماده چاپ",
        short_description="مدل کاربردی برای تست فرانت‌اند",
        description="توضیحات کامل مدل آماده چاپ",
        author_name="Test Designer",
        preview_image=_image(),
        private_download_url="https://private.example/phase13-model.zip",
    )
    metrics = CatalogAssetMetrics.objects.create(
        asset=asset,
        source_kind="printables",
        segment="industrial",
        commercial_use_allowed=True,
        license_review_status="allowed",
        public_approved=True,
        downloads_count=1250,
        likes_count=82,
        views_count=4200,
        file_formats=["STL", "3MF"],
    )
    CatalogAssetPublication.objects.create(
        metrics=metrics,
        show_on_homepage=homepage,
        image_alt_text="براکت صنعتی آماده چاپ سه‌بعدی",
    )
    return asset


class Phase13FrontendTests(TestCase):
    def test_homepage_renders_new_frontend_when_catalog_is_empty(self):
        _material()
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "phase13-frontend.css")
        self.assertContains(response, "طراحی و ساخت قطعات دقیق")
        self.assertNotContains(response, "data-p13-order-form")
        self.assertContains(response, "قیمت هر گرم، شفاف و به‌روز")

    def test_homepage_renders_slider_and_order_link_for_safe_asset(self):
        asset = _asset(homepage=True)
        _material()
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, asset.title)
        self.assertContains(response, reverse("store:external_catalog_detail", args=[asset.pk]))
        self.assertContains(response, "data-p27-home-hero")

    def test_catalog_page_renders_search_filters_and_cards(self):
        asset = _asset(homepage=False)
        response = self.client.get(reverse("store:external_catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-p13-catalog-filter")
        self.assertContains(response, asset.title)
        self.assertContains(response, "phase23-catalog-link.css")

    def test_catalog_detail_renders_without_private_download_links(self):
        asset = _asset(homepage=False)
        asset.private_download_url = "https://private.example/model.zip"
        asset.save(update_fields=["private_download_url"])
        response = self.client.get(reverse("store:external_catalog_detail", args=[asset.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, asset.title)
        self.assertContains(response, "ورود برای استعلام و سفارش")
        self.assertNotContains(response, "private.example")

    def test_order_wizard_has_four_named_photo_inputs(self):
        user = get_user_model().objects.create_user(
            username="phase13-authenticated-order",
            password="StrongPass123!",
        )
        self.client.force_login(user)
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        for field_name in ("photo_top", "photo_front", "photo_right", "photo_left"):
            self.assertContains(response, f'name="{field_name}"')
