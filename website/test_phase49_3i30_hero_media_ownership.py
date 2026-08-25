from django.test import TestCase

from store.models import (
    Category,
    ImportedPrintAsset,
    ImportedPrintAssetImage,
    PrintCatalogSource,
    Product,
    ProductImage,
)
from website.models import HomepageHeroSlide


class Phase493I30HeroMediaOwnershipTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Hero ownership", slug="hero-ownership")
        cls.product = Product.objects.create(
            category=category,
            title="محصول تست Hero",
            slug="hero-owned-media",
            sku="P493I30-HERO-001",
            short_description="تست",
            description="تست",
            main_image="store/products/main-owned.webp",
            is_active=True,
        )
        source = PrintCatalogSource.objects.create(
            name="MakerWorld",
            code="makerworld-i30-test",
            base_url="https://makerworld.com/",
        )
        cls.asset = ImportedPrintAsset.objects.create(
            source=source,
            source_url="https://makerworld.com/en/models/1-test",
            external_id="1",
            title="Hero source asset",
            product=cls.product,
        )
        cls.selected = ImportedPrintAssetImage.objects.create(
            asset=cls.asset,
            remote_url="https://makerworld.bblmw.com/example/hero-owned.webp",
            image="store/imported-models/gallery/hero-owned.webp",
            is_selected=True,
            is_primary=False,
            sort_order=1,
        )
        ProductImage.objects.create(
            product=cls.product,
            image="store/products/gallery/hero-owned.webp",
            alt_text="تصویر Hero",
            sort_order=1,
        )

    def test_selected_imported_gallery_image_resolves_to_product_owned_gallery(self):
        slide = HomepageHeroSlide.objects.create(
            asset=self.asset,
            selected_asset_image=self.selected,
            image_url="/media/store/imported-models/gallery/hero-owned.webp",
            is_active=True,
        )
        self.assertEqual(
            slide.effective_image_url,
            "/media/store/products/gallery/hero-owned.webp",
        )
        self.assertNotIn("/media/store/imported-models/", slide.effective_image_url)

    def test_missing_exact_gallery_copy_falls_back_to_product_main_image(self):
        self.product.images.all().delete()
        slide = HomepageHeroSlide.objects.create(
            asset=self.asset,
            selected_asset_image=self.selected,
            image_url="/media/store/imported-models/gallery/hero-owned.webp",
            is_active=True,
        )
        self.assertEqual(slide.effective_image_url, "/media/store/products/main-owned.webp")

    def test_remote_source_is_only_fallback_when_product_has_no_public_media(self):
        Product.objects.filter(pk=self.product.pk).update(main_image="")
        self.product.refresh_from_db()
        self.product.images.all().delete()
        slide = HomepageHeroSlide.objects.create(
            asset=self.asset,
            selected_asset_image=self.selected,
            image_url="/media/store/imported-models/gallery/hero-owned.webp",
            is_active=True,
        )
        self.assertEqual(
            slide.effective_image_url,
            "https://makerworld.bblmw.com/example/hero-owned.webp",
        )
