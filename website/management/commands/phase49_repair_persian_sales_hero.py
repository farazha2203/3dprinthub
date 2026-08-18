from __future__ import annotations

from django.core.management.base import BaseCommand

from store.models import ImportedPrintAsset
from store.epic49_catalog_profile import ProductCatalogProfile
from store.phase49_persian_sales_copy import build_slider_sales_copy, safe_persian_text
from website.models import HomepageHeroSlide
from website.phase49_2b_hero_hotfix import _desktop_data
from website.phase49_persian_sales_hero import hero_suggestions


class Command(BaseCommand):
    help = (
        "Audit/repair legacy homepage Hero/Profile copy that contains English source text, "
        "cookie boilerplate or unsafe HTML. Dry-run by default; use --apply to persist."
    )

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Persist safe Persian replacements.")

    def handle(self, *args, **options):
        apply_changes = bool(options["apply"])
        slide_changes = 0
        profile_changes = 0

        self.stdout.write("PHASE49_PERSIAN_SALES_HERO_REPAIR")
        self.stdout.write(f"MODE={'APPLY' if apply_changes else 'DRY_RUN'}")

        for slide in HomepageHeroSlide.objects.select_related("asset", "asset__product").order_by("id"):
            if not slide.asset_id:
                continue
            suggested = hero_suggestions(slide.asset)
            updates = {}
            if not safe_persian_text(slide.title_override, limit=220):
                updates["title_override"] = suggested["title"]
            if not safe_persian_text(slide.description, limit=1200):
                updates["description"] = suggested["description"]
            if not safe_persian_text(slide.image_alt_text, limit=240):
                updates["image_alt_text"] = suggested["image_alt_text"]
            if not safe_persian_text(slide.button_text, limit=80):
                updates["button_text"] = suggested["button_text"] or "مشاهده محصول"

            if updates:
                slide_changes += 1
                self.stdout.write(
                    f"SLIDE id={slide.pk} asset={slide.asset_id} fields={','.join(sorted(updates))}"
                )
                if apply_changes:
                    for key, value in updates.items():
                        setattr(slide, key, value)
                    slide.save(update_fields=[*updates.keys(), "updated_at"])

        for profile in ProductCatalogProfile.objects.select_related("product").order_by("id"):
            asset = ImportedPrintAsset.objects.filter(product=profile.product).order_by("id").first()
            if asset is None:
                continue
            resolved = build_slider_sales_copy(
                _desktop_data(asset),
                product=profile.product,
                asset=asset,
            )
            updates = {}
            if not safe_persian_text(profile.homepage_slider_title_fa, limit=220):
                updates["homepage_slider_title_fa"] = resolved["title_fa"]
            if not safe_persian_text(profile.homepage_slider_description_fa, limit=1200):
                updates["homepage_slider_description_fa"] = resolved["description_fa"]
            if not safe_persian_text(profile.homepage_slider_alt_text, limit=240):
                updates["homepage_slider_alt_text"] = resolved["image_alt_fa"]
            if not safe_persian_text(profile.homepage_slider_button_text, limit=80):
                updates["homepage_slider_button_text"] = resolved["button_text_fa"]
            if not safe_persian_text(profile.homepage_slider_focus_keyword, limit=180):
                updates["homepage_slider_focus_keyword"] = resolved["focus_keyword_fa"]

            if updates:
                profile_changes += 1
                self.stdout.write(
                    f"PROFILE id={profile.pk} product={profile.product_id} fields={','.join(sorted(updates))}"
                )
                if apply_changes:
                    for key, value in updates.items():
                        setattr(profile, key, value)
                    profile.last_modified_source = "repair"
                    profile.last_modified_by = "phase49_persian_sales_hero"
                    profile.save(update_fields=[*updates.keys(), "last_modified_source", "last_modified_by", "updated_at"])

        self.stdout.write(f"SLIDES_TO_REPAIR={slide_changes}")
        self.stdout.write(f"PROFILES_TO_REPAIR={profile_changes}")
        self.stdout.write(f"DB_MUTATIONS={slide_changes + profile_changes if apply_changes else 0}")
