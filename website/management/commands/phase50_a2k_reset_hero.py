from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from store.models import ImportedPrintAsset
from website.models import HomepageHeroSlide


CONFIRMATION = "RESET_HOMEPAGE_HERO"
SEED_SLIDES = (
    (119, 10, "نظم‌دهنده کفش دیواری", "محصولات کاربردی", "راهکاری جمع‌وجور برای مرتب‌کردن کفش‌ها؛ قابل سفارش با چاپ سه‌بعدی و متریال متناسب."),
    (120, 20, "نگهدارنده و نظم‌دهنده کلاه", "محصولات کاربردی", "نگهدارنده دیواری برای مرتب‌کردن کلاه‌ها؛ قابل ساخت با رنگ و متریال انتخابی."),
    (135, 30, "چراغ رومیزی ارگانیک Driftbloom", "نورپردازی و دکور", "چراغ رومیزی با فرم ارگانیک برای نورپردازی دکوراتیو؛ قابل سفارش با چاپ سه‌بعدی."),
    (136, 40, "چراغ رومیزی Crystal Summit", "نورپردازی و دکور", "چراغ رومیزی با فرم کریستالی برای دکور و نور محیطی؛ قابل سفارش با چاپ سه‌بعدی."),
)
SAFE_COMMERCIAL_STATUSES = {"allowed", "owned", "public_domain"}
DESCRIPTION_MAX = int(HomepageHeroSlide._meta.get_field("description").max_length or 480)


class Command(BaseCommand):
    help = "Destroy every previous homepage HeroSlide row and seed only the Phase50.A.2K Tympanus showcase."
    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--confirm", default="")

    def handle(self, *args, **options):
        asset_ids = [row[0] for row in SEED_SLIDES]
        assets = {asset.pk: asset for asset in ImportedPrintAsset.objects.filter(pk__in=asset_ids)}
        missing = [asset_id for asset_id in asset_ids if asset_id not in assets]
        if missing:
            raise CommandError(f"Missing required assets: {missing}")
        invalid = [
            asset_id for asset_id in asset_ids
            if assets[asset_id].editorial_status in {"rejected", "archived", "license_review"}
            or assets[asset_id].commercial_license_status not in SAFE_COMMERCIAL_STATUSES
            or not assets[asset_id].catalog_image_url
        ]
        if invalid:
            raise CommandError(f"Unsafe hero assets: {invalid}")

        before = HomepageHeroSlide.objects.count()
        self.stdout.write(f"A2K_HERO_ROWS_BEFORE={before}")
        self.stdout.write("A2K_HERO_SEED_PLAN=" + ",".join(map(str, asset_ids)))
        self.stdout.write("A2K_HERO_RESET_APPLY=" + str(bool(options["apply"])))
        if not options["apply"]:
            self.stdout.write(self.style.SUCCESS("A2K_HERO_RESET_DRY_RUN=PASS"))
            return
        if str(options.get("confirm") or "") != CONFIRMATION:
            raise CommandError(f"Apply requires --confirm {CONFIRMATION}")

        with transaction.atomic():
            HomepageHeroSlide.objects.all().delete()
            active_ids = []
            for asset_id, sort_order, title, group_title, description in SEED_SLIDES:
                slide = HomepageHeroSlide.objects.create(
                    asset=assets[asset_id],
                    title_override=title,
                    group_title=group_title,
                    description=description[:DESCRIPTION_MAX],
                    button_text="ثبت سفارش چاپ مشابه",
                    image_url="",
                    image_alt_text=f"{title} - نمونه چاپ سه‌بعدی 3DPrintHub",
                    object_fit="cover",
                    focal_position="center",
                    sort_order=sort_order,
                    is_active=True,
                )
                active_ids.append(slide.pk)

        total = HomepageHeroSlide.objects.count()
        active = HomepageHeroSlide.objects.filter(is_active=True).count()
        self.stdout.write(f"A2K_HERO_ROWS_AFTER={total}")
        self.stdout.write(f"A2K_HERO_ACTIVE_COUNT={active}")
        self.stdout.write("A2K_HERO_ACTIVE_IDS=" + ",".join(map(str, active_ids)))
        if total != len(SEED_SLIDES) or active != len(SEED_SLIDES):
            raise CommandError(f"Expected exactly {len(SEED_SLIDES)} total/active slides, found total={total}, active={active}")
        self.stdout.write(self.style.SUCCESS("A2K_HERO_RESET_APPLY=PASS"))
