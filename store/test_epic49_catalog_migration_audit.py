from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from store.epic49_catalog_profile import ProductCatalogProfile
from store.models import Category, ImportedPrintAsset, PrintCatalogSource, Product


class Epic49CatalogMigrationAuditTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Audit Category",
            slug="epic49-audit-category",
        )
        cls.product = Product.objects.create(
            category=cls.category,
            title="محصول تست Audit",
            title_en="Audit Product New Slug",
            slug="legacy-audit-product",
            sku="AUDIT-001",
            short_description="توضیح قدیمی",
            description="توضیحات تست",
            main_image="store/products/audit-product.jpg",
            meta_title="عنوان قدیمی",
            meta_description="توضیح متای قدیمی",
            seo_focus_keyword="کلید قدیمی",
            is_active=True,
        )
        cls.source = PrintCatalogSource.objects.create(
            name="Audit Source",
            code="epic49-audit-source",
            base_url="https://example.com/",
        )
        cls.asset = ImportedPrintAsset.objects.create(
            source=cls.source,
            source_url="https://example.com/audit-product",
            external_id="AUDIT-ASSET-001",
            title="Audit Imported Asset",
            product=cls.product,
            source_payload={
                "desktop_catalog_v85": {
                    "seo_title_fa": "عنوان جدید پیشنهادی Audit",
                    "seo_description_fa": "توضیح جدید پیشنهادی Audit",
                    "keywords_json": ["کلید جدید"],
                    "hashtags_fa_json": ["#audit", "#3dprint"],
                    "homepage_slider_enabled": True,
                    "homepage_slider_sort_order": 12,
                }
            },
        )

    def test_command_reports_changes_without_mutating_product_or_profile(self):
        before = Product.objects.values(
            "slug",
            "meta_title",
            "meta_description",
            "seo_focus_keyword",
            "hashtags",
            "canonical_url",
        ).get(pk=self.product.pk)
        self.assertFalse(ProductCatalogProfile.objects.filter(product=self.product).exists())

        stdout = StringIO()
        call_command("epic49_catalog_migration_audit", limit=0, stdout=stdout)
        output = stdout.getvalue()

        after = Product.objects.values(
            "slug",
            "meta_title",
            "meta_description",
            "seo_focus_keyword",
            "hashtags",
            "canonical_url",
        ).get(pk=self.product.pk)

        self.assertEqual(before, after)
        self.assertFalse(ProductCatalogProfile.objects.filter(product=self.product).exists())
        self.assertIn("READ_ONLY=YES", output)
        self.assertIn("AUDIT_DB_MUTATIONS=0", output)
        self.assertIn("PRODUCTS_WITH_ANY_CHANGE=1", output)
        self.assertIn("PRODUCTS_WITH_SLUG_CHANGE=1", output)
        self.assertIn("AUDIT-001", output)
