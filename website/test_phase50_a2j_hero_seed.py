from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from store.models import ImportedPrintAsset, PrintCatalogSource, Product
from website.models import HomepageHeroSlide


class Phase50A2JHeroSeedTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        source = PrintCatalogSource.objects.create(
            name="A2J Seed Source",
            code="a2j-seed-source",
            base_url="https://example.com/",
        )
        for asset_id in (119, 120, 135, 136):
            ImportedPrintAsset.objects.create(
                id=asset_id,
                source=source,
                source_url=f"https://example.com/model/{asset_id}",
                external_id=f"A2J-{asset_id}",
                title=f"A2J Asset {asset_id}",
                remote_image_url=f"https://example.com/image/{asset_id}.webp",
                editorial_status="imported",
                commercial_license_status="allowed",
            )
    def test_dry_run_does_not_write(self):
        out = StringIO()
        call_command("phase50_a2j_seed_hero", stdout=out)
        self.assertIn("A2J_HERO_SEED_DRY_RUN=PASS", out.getvalue())
        self.assertEqual(HomepageHeroSlide.objects.count(), 0)
        self.assertEqual(Product.objects.count(), 0)

    def test_apply_creates_four_active_source_backed_slides(self):
        out = StringIO()
        call_command("phase50_a2j_seed_hero", "--apply", stdout=out)
        self.assertIn("A2J_HERO_SEED_APPLY=PASS", out.getvalue())
        slides = list(HomepageHeroSlide.objects.filter(is_active=True).order_by("sort_order"))
        self.assertEqual([slide.asset_id for slide in slides], [119, 120, 135, 136])
        self.assertEqual(Product.objects.count(), 0)
        self.assertTrue(all(slide.target_url == "/#order" for slide in slides))
        self.assertTrue(all(slide.effective_image_url for slide in slides))
    def test_unknown_commercial_license_is_rejected(self):
        asset = ImportedPrintAsset.objects.get(pk=119)
        asset.commercial_license_status = "unknown"
        asset.save(update_fields=["commercial_license_status"])
        with self.assertRaises(CommandError):
            call_command("phase50_a2j_seed_hero", "--apply")
        self.assertEqual(HomepageHeroSlide.objects.filter(is_active=True).count(), 0)
        self.assertEqual(Product.objects.count(), 0)
