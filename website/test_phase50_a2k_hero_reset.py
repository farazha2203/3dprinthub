from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from store.models import ImportedPrintAsset, PrintCatalogSource, Product
from website.models import HomepageHeroSlide


class Phase50A2KHeroResetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        source = PrintCatalogSource.objects.create(
            name="A2K Seed Source", code="a2k-seed-source", base_url="https://example.com/"
        )
        for asset_id in (119, 120, 135, 136, 999):
            ImportedPrintAsset.objects.create(
                id=asset_id,
                source=source,
                source_url=f"https://example.com/model/{asset_id}",
                external_id=f"A2K-{asset_id}",
                title=f"A2K Asset {asset_id}",
                remote_image_url=f"https://example.com/image/{asset_id}.webp",
                editorial_status="imported",
                commercial_license_status="allowed",
            )
    def test_dry_run_reports_existing_rows_without_writing(self):
        HomepageHeroSlide.objects.create(asset=ImportedPrintAsset.objects.get(pk=999), title_override="Old")
        out = StringIO()
        call_command("phase50_a2k_reset_hero", stdout=out)
        self.assertIn("A2K_HERO_ROWS_BEFORE=1", out.getvalue())
        self.assertIn("A2K_HERO_RESET_DRY_RUN=PASS", out.getvalue())
        self.assertEqual(HomepageHeroSlide.objects.count(), 1)

    def test_apply_requires_explicit_confirmation(self):
        with self.assertRaises(CommandError):
            call_command("phase50_a2k_reset_hero", "--apply")
        self.assertEqual(HomepageHeroSlide.objects.count(), 0)

    def test_apply_destroys_all_old_rows_and_seeds_exactly_four(self):
        HomepageHeroSlide.objects.create(asset=ImportedPrintAsset.objects.get(pk=999), title_override="Old", is_active=True)
        out = StringIO()
        call_command(
            "phase50_a2k_reset_hero", "--apply", "--confirm", "RESET_HOMEPAGE_HERO", stdout=out
        )
        self.assertIn("A2K_HERO_ROWS_BEFORE=1", out.getvalue())
        self.assertIn("A2K_HERO_ROWS_AFTER=4", out.getvalue())
        self.assertIn("A2K_HERO_RESET_APPLY=PASS", out.getvalue())
        slides = list(HomepageHeroSlide.objects.order_by("sort_order", "id"))
        self.assertEqual([slide.asset_id for slide in slides], [119, 120, 135, 136])
        self.assertTrue(all(slide.is_active for slide in slides))
        self.assertEqual(Product.objects.count(), 0)
