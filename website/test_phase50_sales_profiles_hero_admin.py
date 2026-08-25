from pathlib import Path

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from store.models import (
    Category,
    ImportedPrintAsset,
    ImportedPrintAssetImage,
    PrintCatalogSource,
    Product,
    ProductImage,
    ProductVariant,
)
from website.models import HomepageHeroSlide


class Phase50SalesProfileContractTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent

    def read(self, relative):
        return (self.root / relative).read_text(encoding="utf-8", errors="replace")

    def test_runtime_models_expose_sales_profile_contract(self):
        self.assertEqual(Product._meta.get_field("sales_profile_selection_mode").default, "size_build")
        self.assertEqual(ProductVariant._meta.get_field("sales_profile_name").max_length, 120)
        self.assertEqual(ProductVariant._meta.get_field("sales_profile_key").max_length, 80)
        self.assertTrue(ProductVariant._meta.get_field("sales_profile_is_default").db_index)
        self.assertTrue(hasattr(ProductVariant, "sales_profile_display_label"))
        self.assertTrue(hasattr(ProductVariant, "sales_profile_selection_value"))

    def test_migration_0035_extends_profile_identity(self):
        migration = self.read("store/migrations/0035_phase50_sales_profiles.py")
        self.assertIn('("store", "0034_phase50_variant2_commerce")', migration)
        self.assertIn('name="sales_profile_selection_mode"', migration)
        self.assertIn('name="sales_profile_key"', migration)
        self.assertIn('name="uniq_product_material_quality_color_size_build_profile"', migration)
        self.assertNotIn("RunSQL", migration)
        self.assertNotIn("DeleteModel", migration)

    def test_admin_has_copy_profile_action_and_product_selector_mode(self):
        variant_admin = admin.site._registry[ProductVariant]
        self.assertIn("duplicate_sales_profiles", variant_admin.actions)
        self.assertIn("sales_profile_is_default", variant_admin.list_display)
        self.assertIn("sales_profile_sort_order", variant_admin.list_display)

        product_admin = admin.site._registry[Product]
        self.assertIn("sales_profile_selection_mode", product_admin.list_display)


class Phase50HeroAdminPublicMediaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username="phase50-hero-admin",
            email="phase50-hero@example.com",
            password="StrongTestPass123!",
        )
        cls.category = Category.objects.create(name="Hero Public Media", slug="hero-public-media")
        cls.product = Product.objects.create(
            category=cls.category,
            title="محصول تست رسانه Hero",
            title_en="Hero Public Media Product",
            slug="phase50-hero-public-media",
            sku="P50-HERO-001",
            short_description="تست رسانه عمومی",
            description="تست رسانه عمومی اسلایدر ادمین",
            main_image="store/products/phase50-hero-main.webp",
            is_active=True,
        )
        ProductImage.objects.create(
            product=cls.product,
            image="store/products/gallery/phase50-hero-gallery.webp",
            alt_text="تصویر عمومی محصول",
            sort_order=0,
        )
        cls.source = PrintCatalogSource.objects.create(
            name="Phase50 Hero Source",
            code="phase50-hero-source",
            base_url="https://example.com/",
        )
        cls.asset = ImportedPrintAsset.objects.create(
            source=cls.source,
            source_url="https://example.com/models/hero",
            external_id="P50-HERO-ASSET",
            title="Hero Source Product",
            persian_title="محصول رسانه Hero",
            product=cls.product,
        )
        cls.asset_image = ImportedPrintAssetImage.objects.create(
            asset=cls.asset,
            remote_url="https://example.com/images/phase50-hero-gallery.webp",
            image="store/imported-models/gallery/phase50-hero-gallery.webp",
            alt_text="تصویر انتخابی Hero",
            is_primary=True,
            is_selected=True,
            sort_order=0,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_hero_album_detail_uses_product_owned_public_gallery(self):
        response = self.client.get(
            reverse("admin:website_homepageheroslide_asset_detail"),
            {"asset_id": self.asset.pk},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        row = next(item for item in payload["images"] if item["id"] == self.asset_image.pk)
        self.assertIn("/media/store/products/gallery/phase50-hero-gallery.webp", row["url"])
        self.assertNotIn("/media/store/imported-models/", row["url"])

    def test_hero_product_browser_thumbnail_is_public(self):
        response = self.client.get(
            reverse("admin:website_homepageheroslide_product_browser"),
            {"q": "P50-HERO-001"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        item = next(row for row in payload["items"] if row["sku"] == "P50-HERO-001")
        self.assertTrue(item["image"])
        self.assertNotIn("/media/store/imported-models/", item["image"])
