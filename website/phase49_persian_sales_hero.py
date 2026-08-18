from __future__ import annotations

from django.db.models.signals import pre_save

from store.phase49_persian_sales_copy import build_slider_sales_copy, safe_persian_text
from .models import HomepageHeroSlide
from . import phase49_2b_hero_hotfix as legacy


def _resolved_copy(asset) -> dict:
    if asset is None:
        return build_slider_sales_copy({}, product=None, asset=None)
    data = legacy._desktop_data(asset)
    product = legacy._product_for(asset)
    return build_slider_sales_copy(data, product=product, asset=asset)


def _asset_title(asset) -> str:
    return _resolved_copy(asset)["title_fa"]


def _asset_description(asset) -> str:
    return _resolved_copy(asset)["description_fa"]


def hero_suggestions(asset) -> dict:
    copy = _resolved_copy(asset)
    title = copy["title_fa"]
    group = legacy._asset_group(asset) or "محصول منتخب"
    preview_url = legacy._asset_image(asset)
    return {
        "title": title[:220],
        "description": copy["description_fa"],
        "group_title": group[:160],
        "image_alt_text": copy["image_alt_fa"][:240],
        "button_text": copy["button_text_fa"][:80],
        "focus_keyword": copy["focus_keyword_fa"][:180],
        "preview_url": preview_url,
        "image_url": legacy._absolute_remote_url(preview_url),
        "target_url": legacy._asset_target(asset),
        "images": legacy._candidate_urls(asset),
    }


def _effective_title(self: HomepageHeroSlide) -> str:
    explicit = safe_persian_text(self.title_override, limit=220)
    return explicit or _resolved_copy(getattr(self, "asset", None))["title_fa"]


def _effective_description(self: HomepageHeroSlide) -> str:
    explicit = safe_persian_text(self.description, limit=1200)
    return explicit or _resolved_copy(getattr(self, "asset", None))["description_fa"]


def _effective_alt_text(self: HomepageHeroSlide) -> str:
    explicit = safe_persian_text(self.image_alt_text, limit=240)
    return explicit or _resolved_copy(getattr(self, "asset", None))["image_alt_fa"]


def _effective_button_text(self: HomepageHeroSlide) -> str:
    explicit = safe_persian_text(self.button_text, limit=80)
    return explicit or _resolved_copy(getattr(self, "asset", None))["button_text_fa"] or "مشاهده محصول"


def _repair_slide_before_save(sender, instance: HomepageHeroSlide, **_kwargs):
    if not instance.asset_id:
        return
    data = hero_suggestions(instance.asset)

    if not safe_persian_text(instance.title_override, limit=220):
        instance.title_override = data["title"]
    if not safe_persian_text(instance.description, limit=1200):
        instance.description = data["description"]
    if not safe_persian_text(instance.image_alt_text, limit=240):
        instance.image_alt_text = data["image_alt_text"]
    if not safe_persian_text(instance.button_text, limit=80):
        instance.button_text = data["button_text"] or "مشاهده محصول"
    if not str(instance.group_title or "").strip():
        instance.group_title = data["group_title"]


# Rebind the Phase49.2B resolver so its existing Admin AJAX endpoint and its
# pre_save safety net immediately inherit the Persian-sales contract.
legacy._asset_title = _asset_title
legacy._asset_description = _asset_description
legacy.hero_suggestions = hero_suggestions

HomepageHeroSlide.effective_title = property(_effective_title)
HomepageHeroSlide.effective_description = property(_effective_description)
HomepageHeroSlide.effective_alt_text = property(_effective_alt_text)
HomepageHeroSlide.effective_button_text = property(_effective_button_text)

pre_save.connect(
    _repair_slide_before_save,
    sender=HomepageHeroSlide,
    weak=False,
    dispatch_uid="phase49_persian_sales_hero_repair",
)
