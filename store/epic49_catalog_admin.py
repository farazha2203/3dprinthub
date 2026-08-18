from django.contrib import admin

from .epic49_catalog_profile import ProductCatalogProfile


def _admin_actor(request) -> str:
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return ""
    return str(
        getattr(user, "username", "")
        or getattr(user, "email", "")
        or getattr(user, "pk", "")
        or ""
    )[:120]


def _asset_for_product(product):
    try:
        return product.imported_source_asset
    except Exception:
        return None


def _selected_slider_image(asset, value: str):
    if asset is None:
        return None
    value = str(value or "").strip()
    if not value:
        return None
    row = asset.images.filter(remote_url=value).order_by("sort_order", "id").first()
    if row is not None:
        return row
    for candidate in asset.images.exclude(image="").order_by("sort_order", "id")[:80]:
        try:
            local = str(candidate.image.url or "").strip()
        except Exception:
            local = ""
        if local and (value == local or value.endswith(local)):
            return candidate
    return None


def _mirror_profile_to_hero(profile: ProductCatalogProfile, actor: str) -> None:
    asset = _asset_for_product(profile.product)
    if asset is None:
        return
    from website.models import HomepageHeroSlide

    slide = HomepageHeroSlide.objects.filter(asset=asset).order_by("id").first()
    if slide is None and not profile.homepage_slider_enabled:
        return
    selected = _selected_slider_image(asset, profile.homepage_slider_image_url)
    image_url = str(profile.homepage_slider_image_url or "").strip()
    if image_url and not image_url.startswith(("http://", "https://")):
        image_url = ""

    if slide is None:
        slide = HomepageHeroSlide(asset=asset, sync_revision=1)
        changed = True
    else:
        before = (
            slide.selected_asset_image_id,
            slide.image_url,
            slide.image_alt_text,
            slide.title_override,
            slide.description,
            slide.button_text,
            slide.sort_order,
            slide.transition_effect,
            slide.transition_duration_ms,
            slide.display_duration_ms,
            slide.is_active,
        )
        changed = False

    slide.selected_asset_image = selected
    slide.image_url = image_url
    slide.image_alt_text = str(profile.homepage_slider_alt_text or "")[:240]
    slide.title_override = str(profile.homepage_slider_title_fa or "")[:220]
    slide.group_title = str(getattr(profile.product.category, "name", "") or "")[:160]
    slide.description = str(profile.homepage_slider_description_fa or "")
    slide.button_text = str(profile.homepage_slider_button_text or "مشاهده محصول")[:80]
    slide.sort_order = max(0, int(profile.homepage_slider_sort_order or 0))
    slide.transition_effect = str(profile.homepage_slider_transition_effect or "cinematic_fade")[:32]
    slide.transition_duration_ms = int(profile.homepage_slider_transition_duration_ms or 1400)
    slide.display_duration_ms = int(profile.homepage_slider_display_duration_ms or 7000)
    slide.is_active = bool(profile.homepage_slider_enabled)
    slide.last_modified_source = "admin"
    slide.last_modified_by = actor

    if slide.pk:
        after = (
            slide.selected_asset_image_id,
            slide.image_url,
            slide.image_alt_text,
            slide.title_override,
            slide.description,
            slide.button_text,
            slide.sort_order,
            slide.transition_effect,
            slide.transition_duration_ms,
            slide.display_duration_ms,
            slide.is_active,
        )
        changed = before != after
    if changed and slide.pk:
        slide.sync_revision = max(1, int(slide.sync_revision or 1)) + 1
    slide.save()


@admin.register(ProductCatalogProfile)
class ProductCatalogProfileAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "public_slug",
        "product_type",
        "availability_status",
        "price_mode",
        "price_min",
        "price_max",
        "stock_quantity",
        "homepage_slider_enabled",
        "homepage_slider_transition_effect",
        "sync_revision",
        "last_modified_source",
        "last_synced_at",
    ]
    list_filter = [
        "product_type",
        "availability_status",
        "price_mode",
        "commercial_license_status",
        "homepage_slider_enabled",
        "homepage_slider_transition_effect",
        "last_modified_source",
        "has_3d_file",
    ]
    search_fields = [
        "product__title",
        "product__sku",
        "public_slug",
        "legacy_slug",
        "desktop_product_id",
        "batch_uuid",
        "source_hash",
        "homepage_slider_title_fa",
        "homepage_slider_alt_text",
        "homepage_slider_focus_keyword",
        "last_modified_by",
    ]
    readonly_fields = [
        "legacy_slug",
        "sync_revision",
        "last_modified_source",
        "last_modified_by",
        "created_at",
        "updated_at",
        "last_synced_at",
    ]
    raw_id_fields = ["product"]
    fieldsets = [
        ("اتصال محصول", {"fields": ["product", "public_slug", "legacy_slug", "desktop_product_id", "batch_uuid", "source_hash"]}),
        ("فروش و سفارش", {"fields": ["product_type", "use_description", "availability_status", "stock_quantity", "lead_time_min_days", "lead_time_max_days", "has_3d_file"]}),
        ("قیمت", {"fields": ["price_mode", "price_min", "price_max"]}),
        ("مجوز", {"fields": ["commercial_license_status", "license_name", "license_url"]}),
        ("اطلاعات فنی و SEO", {"fields": ["technical_features", "keywords", "download_image_limit"]}),
        (
            "اسلایدر صفحه اول — انتشار و تصویر",
            {"fields": ["homepage_slider_enabled", "homepage_slider_image_url", "homepage_slider_sort_order"]},
        ),
        (
            "اسلایدر صفحه اول — SEO اختصاصی",
            {"fields": [
                "homepage_slider_title_fa",
                "homepage_slider_description_fa",
                "homepage_slider_alt_text",
                "homepage_slider_button_text",
                "homepage_slider_focus_keyword",
            ]},
        ),
        (
            "اسلایدر صفحه اول — افکت سینمایی",
            {"fields": [
                "homepage_slider_transition_effect",
                "homepage_slider_transition_duration_ms",
                "homepage_slider_display_duration_ms",
            ]},
        ),
        (
            "همگام‌سازی Desktop / Server",
            {"fields": ["sync_revision", "last_modified_source", "last_modified_by", "last_synced_at", "created_at", "updated_at"]},
        ),
    ]

    def save_model(self, request, obj, form, change):
        if change:
            obj.sync_revision = max(1, int(obj.sync_revision or 1)) + 1
        else:
            obj.sync_revision = max(1, int(obj.sync_revision or 1))
        obj.last_modified_source = "admin"
        actor = _admin_actor(request)
        obj.last_modified_by = actor
        super().save_model(request, obj, form, change)
        _mirror_profile_to_hero(obj, actor)
