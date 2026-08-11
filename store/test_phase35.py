from django.test import TestCase
from store.models import ImportedPrintAsset, PrintCatalogSource, Category
from store.phase35_catalog_editor import calculate_provisional_price


class Phase35PricingTests(TestCase):
    def test_price_has_500k_floor(self):
        category = Category.objects.create(name="Test", slug="test-phase35")
        source = PrintCatalogSource.objects.create(name="MakerWorld", code="mw-phase35", base_url="https://makerworld.com", default_category=category)
        asset = ImportedPrintAsset.objects.create(source=source, source_url="https://makerworld.com/en/models/1", title="Test", technical_specs={})
        price, material_cost, note = calculate_provisional_price(asset)
        self.assertEqual(price, 500_000)
        self.assertEqual(material_cost, 0)
        self.assertIn("علی‌الحساب", note)


class Phase35DuplicateProtectionTests(TestCase):
    def test_same_source_and_external_id_updates_existing_asset(self):
        from types import SimpleNamespace
        from store.catalog_sync import save_external_record

        category = Category.objects.create(
            name="Duplicate Test",
            slug="duplicate-test-phase35",
        )
        source = PrintCatalogSource.objects.create(
            name="MakerWorld Duplicate Test",
            code="makerworld-duplicate-phase35",
            base_url="https://makerworld.com",
            default_category=category,
        )
        policy = SimpleNamespace(
            store_download_links=True,
            source_kind="makerworld",
            public_display_policy="licensed_only",
        )

        first, _ = save_external_record(
            source=source,
            policy=policy,
            parsed={
                "source_url": "https://makerworld.com/en/models/123-test?utm_source=x",
                "external_id": "123",
                "title": "Original title",
                "images": [],
                "file_links": [],
            },
        )
        second, _ = save_external_record(
            source=source,
            policy=policy,
            parsed={
                "source_url": "https://makerworld.com/en/models/123-test",
                "external_id": "123",
                "title": "Updated title",
                "images": [],
                "file_links": [],
            },
        )

        self.assertEqual(first.pk, second.pk)
        self.assertEqual(
            ImportedPrintAsset.objects.filter(
                source=source,
                external_id="123",
            ).count(),
            1,
        )
        second.refresh_from_db()
        self.assertEqual(second.title, "Updated title")
