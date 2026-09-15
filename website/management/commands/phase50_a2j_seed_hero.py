from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from store.models import ImportedPrintAsset
from website.models import HomepageHeroSlide


SEED_SLIDES = (
    (119, 10, "نظم‌دهنده کفش دیواری", "محصولات کاربردی"),
    (120, 20, "نگهدارنده و نظم‌دهنده کلاه", "محصولات کاربردی"),
    (135, 30, "چراغ رومیزی ارگانیک Driftbloom", "نورپردازی و دکور"),
    (136, 40, "چراغ رومیزی Crystal Summit", "نورپردازی و دکور"),
)

SAFE_COMMERCIAL_STATUSES = {"allowed", "owned", "public_domain"}


class Command(BaseCommand):
    help = "Seed the safe Phase50.A.2J showcase hero without creating Store Products."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply the curated Hero data. Without this flag the command is read-only.",
        )
    def handle(self, *args, **options):
        asset_ids = [row[0] for row in SEED_SLIDES]
        assets = {
            asset.pk: asset
            for asset in ImportedPrintAsset.objects.filter(pk__in=asset_ids)
        }
        missing = [asset_id for asset_id in asset_ids if asset_id not in assets]
        if missing:
            raise CommandError(f"Missing required assets: {missing}")

        invalid = [
            asset_id
            for asset_id in asset_ids
            if assets[asset_id].editorial_status in {"rejected", "archived", "license_review"}
            or assets[asset_id].commercial_license_status not in SAFE_COMMERCIAL_STATUSES
            or not assets[asset_id].catalog_image_url
        ]
        if invalid:
            raise CommandError(f"Unsafe hero assets: {invalid}")

        self.stdout.write("A2J_HERO_SEED_PLAN=" + ",".join(map(str, asset_ids)))
        self.stdout.write("A2J_HERO_SEED_APPLY=" + str(bool(options["apply"])))
        if not options["apply"]:
            self.stdout.write(self.style.SUCCESS("A2J_HERO_SEED_DRY_RUN=PASS"))
            return
        with transaction.atomic():
            HomepageHeroSlide.objects.filter(is_active=True).update(is_active=False)
            active_ids = []
            for asset_id, sort_order, title, group_title in SEED_SLIDES:
                asset = assets[asset_id]
                slide = HomepageHeroSlide.objects.filter(asset=asset).order_by("id").first()
                if slide is None:
                    slide = HomepageHeroSlide(asset=asset)
                slide.title_override = title
                slide.group_title = group_title
                slide.description = ""
                slide.button_text = "ثبت سفارش چاپ مشابه"
                slide.image_url = ""
                slide.image_alt_text = f"{title} - نمونه چاپ سه‌بعدی 3DPrintHub"
                slide.object_fit = "cover"
                slide.focal_position = "center"
                slide.sort_order = sort_order
                slide.is_active = True
                slide.save()
                active_ids.append(slide.pk)

        count = HomepageHeroSlide.objects.filter(is_active=True).count()
        self.stdout.write("A2J_HERO_ACTIVE_COUNT=" + str(count))
        self.stdout.write("A2J_HERO_ACTIVE_IDS=" + ",".join(map(str, active_ids)))
        if count != len(SEED_SLIDES):
            raise CommandError(f"Expected {len(SEED_SLIDES)} active slides, found {count}")
        self.stdout.write(self.style.SUCCESS("A2J_HERO_SEED_APPLY=PASS"))
