from __future__ import annotations

import random
from typing import Iterable

from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.urls import path, reverse

from store.models import ImportedPrintAsset, Product
from .models import HomepageHeroSlide
from .phase49_2b_hero_hotfix import hero_suggestions


ACTIVE_EXCLUDED_EDITORIAL = {"rejected", "archived"}


def _eligible_asset_queryset():
    return (
        ImportedPrintAsset.objects.select_related("product", "source")
        .filter(product__is_active=True)
        .exclude(status="rejected")
        .exclude(editorial_status__in=ACTIVE_EXCLUDED_EDITORIAL)
        .order_by("id")
    )


def _eligible_assets() -> list[ImportedPrintAsset]:
    """Return only assets that are safe to use as public Product-backed Hero slides."""

    rows: list[ImportedPrintAsset] = []
    for asset in _eligible_asset_queryset().iterator():
        try:
            if asset.public_display_mode == "hidden":
                continue
            suggestion = hero_suggestions(asset)
            if not str(suggestion.get("preview_url") or "").strip():
                continue
            product = getattr(asset, "product", None)
            if product is None or not getattr(product, "is_active", False):
                continue
        except Exception:
            continue
        rows.append(asset)
    return rows


def _next_sort_order() -> int:
    current = HomepageHeroSlide.objects.aggregate(value=Max("sort_order"))["value"] or 0
    return max(int(current), 0) + 10


def _primary_slide_for(asset: ImportedPrintAsset):
    return HomepageHeroSlide.objects.filter(asset=asset).order_by("id").first()


def _prefill_new_slide(slide: HomepageHeroSlide, asset: ImportedPrintAsset) -> None:
    suggestion = hero_suggestions(asset)
    slide.image_url = str(suggestion.get("image_url") or "")[:2000]
    slide.image_alt_text = str(suggestion.get("image_alt_text") or "")[:240]
    slide.title_override = str(suggestion.get("title") or "")[:220]
    slide.group_title = str(suggestion.get("group_title") or "")[:160]
    slide.description = str(suggestion.get("description") or "")[:480]
    slide.button_text = str(suggestion.get("button_text") or "مشاهده محصول")[:80]


@transaction.atomic
def activate_assets_on_slider(assets: Iterable[ImportedPrintAsset]) -> int:
    """Activate one preserved slide per asset without overwriting operator edits."""

    count = 0
    sort_order = _next_sort_order()
    for asset in assets:
        product = getattr(asset, "product", None)
        if product is None or not getattr(product, "is_active", False):
            continue
        suggestion = hero_suggestions(asset)
        if not str(suggestion.get("preview_url") or "").strip():
            continue

        slide = _primary_slide_for(asset)
        if slide is None:
            slide = HomepageHeroSlide(asset=asset, sort_order=sort_order)
            _prefill_new_slide(slide, asset)
            slide.is_active = True
            slide.save()
            sort_order += 10
        else:
            update_fields = []
            if not slide.is_active:
                slide.is_active = True
                update_fields.append("is_active")
            if update_fields:
                update_fields.append("updated_at")
                slide.save(update_fields=update_fields)
            HomepageHeroSlide.objects.filter(asset=asset).exclude(pk=slide.pk).update(is_active=False)
        count += 1
    return count


@transaction.atomic
def deactivate_assets_from_slider(assets: Iterable[ImportedPrintAsset]) -> int:
    ids = [asset.pk for asset in assets if getattr(asset, "pk", None)]
    if not ids:
        return 0
    return HomepageHeroSlide.objects.filter(asset_id__in=ids, is_active=True).update(is_active=False)


@transaction.atomic
def replace_slider_with_random_products(count: int) -> int:
    count = max(1, min(int(count), 20))
    eligible = _eligible_assets()
    selected = random.SystemRandom().sample(eligible, min(count, len(eligible))) if eligible else []
    HomepageHeroSlide.objects.filter(is_active=True).update(is_active=False)
    return activate_assets_on_slider(selected)


def _assets_for_products(products: Iterable[Product]) -> list[ImportedPrintAsset]:
    product_ids = [product.pk for product in products if getattr(product, "pk", None)]
    if not product_ids:
        return []
    return list(
        ImportedPrintAsset.objects.select_related("product", "source")
        .filter(product_id__in=product_ids)
        .exclude(status="rejected")
        .exclude(editorial_status__in=ACTIVE_EXCLUDED_EDITORIAL)
    )


@admin.action(description="افزودن محصولات انتخاب‌شده به اسلایدر صفحه اصلی")
def add_products_to_homepage_slider(modeladmin, request, queryset):
    count = activate_assets_on_slider(_assets_for_products(queryset))
    if count:
        modeladmin.message_user(request, f"{count} محصول به اسلایدر صفحه اصلی اضافه/فعال شد.", level=messages.SUCCESS)
    else:
        modeladmin.message_user(
            request,
            "برای محصولات انتخاب‌شده دارایی کاتالوگِ قابل نمایش با تصویر عمومی پیدا نشد.",
            level=messages.WARNING,
        )


@admin.action(description="حذف محصولات انتخاب‌شده از اسلایدر صفحه اصلی")
def remove_products_from_homepage_slider(modeladmin, request, queryset):
    count = deactivate_assets_from_slider(_assets_for_products(queryset))
    modeladmin.message_user(request, f"{count} اسلاید غیرفعال شد.", level=messages.SUCCESS)


@admin.action(description="افزودن فایل‌های انتخاب‌شده به اسلایدر صفحه اصلی")
def add_assets_to_homepage_slider(modeladmin, request, queryset):
    count = activate_assets_on_slider(queryset.select_related("product", "source"))
    if count:
        modeladmin.message_user(request, f"{count} مورد به اسلایدر اضافه/فعال شد.", level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, "مورد قابل نمایش با محصول فعال و تصویر عمومی پیدا نشد.", level=messages.WARNING)


@admin.action(description="حذف فایل‌های انتخاب‌شده از اسلایدر صفحه اصلی")
def remove_assets_from_homepage_slider(modeladmin, request, queryset):
    count = deactivate_assets_from_slider(queryset)
    modeladmin.message_user(request, f"{count} اسلاید غیرفعال شد.", level=messages.SUCCESS)


def _append_action(model_admin, action) -> None:
    actions = list(getattr(model_admin, "actions", ()) or ())
    existing_names = {
        item if isinstance(item, str) else getattr(item, "__name__", "")
        for item in actions
    }
    if action.__name__ not in existing_names:
        actions.append(action)
        model_admin.actions = tuple(actions)


def _install_product_actions() -> None:
    product_admin = admin.site._registry.get(Product)
    if product_admin is not None:
        _append_action(product_admin, add_products_to_homepage_slider)
        _append_action(product_admin, remove_products_from_homepage_slider)

    asset_admin = admin.site._registry.get(ImportedPrintAsset)
    if asset_admin is not None:
        _append_action(asset_admin, add_assets_to_homepage_slider)
        _append_action(asset_admin, remove_assets_from_homepage_slider)


def _install_hero_controls() -> None:
    hero_admin = admin.site._registry.get(HomepageHeroSlide)
    if hero_admin is None:
        return

    cls = hero_admin.__class__
    if getattr(cls, "_phase50_storefront_parity_installed", False):
        return

    original_get_urls = cls.get_urls

    def get_urls(self):
        custom = [
            path("random-5/", self.admin_site.admin_view(self.random_five_view), name="website_homepageheroslide_random_5"),
            path("random-10/", self.admin_site.admin_view(self.random_ten_view), name="website_homepageheroslide_random_10"),
            path("deactivate-all/", self.admin_site.admin_view(self.deactivate_all_view), name="website_homepageheroslide_deactivate_all"),
        ]
        return custom + original_get_urls(self)

    def _replace_random(self, request, count: int):
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])
        if not self.has_change_permission(request):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        activated = replace_slider_with_random_products(count)
        if activated:
            self.message_user(request, f"اسلایدر با {activated} محصول رندومِ معتبر جایگزین شد.", level=messages.SUCCESS)
        else:
            self.message_user(request, "هیچ محصول فعال دارای تصویر عمومی برای اسلایدر پیدا نشد.", level=messages.WARNING)
        return redirect(reverse("admin:website_homepageheroslide_changelist"))

    def random_five_view(self, request):
        return _replace_random(self, request, 5)

    def random_ten_view(self, request):
        return _replace_random(self, request, 10)

    def deactivate_all_view(self, request):
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])
        if not self.has_change_permission(request):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        changed = HomepageHeroSlide.objects.filter(is_active=True).update(is_active=False)
        self.message_user(request, f"{changed} اسلاید غیرفعال شد؛ اطلاعات و سابقه حذف نشد.", level=messages.SUCCESS)
        return redirect(reverse("admin:website_homepageheroslide_changelist"))

    cls.get_urls = get_urls
    cls.random_five_view = random_five_view
    cls.random_ten_view = random_ten_view
    cls.deactivate_all_view = deactivate_all_view
    cls.change_list_template = "admin/website/homepageheroslide/change_list.html"
    cls._phase50_storefront_parity_installed = True


def install_storefront_admin_parity() -> None:
    """Expose mature storefront/Hero operations in Django Admin without schema changes."""

    _install_product_actions()
    _install_hero_controls()
