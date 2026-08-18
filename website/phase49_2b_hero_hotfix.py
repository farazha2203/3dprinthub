from __future__ import annotations

from types import MethodType
from urllib.parse import urlparse

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.signals import pre_save
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_GET

from store.models import ImportedPrintAsset
from .models import HomepageHeroSlide


# Phase 49.2B hotfix: keep the existing database schema intact while making the
# managed homepage hero use the Store/Product data that Catalog Center already
# imported. The public External Catalog was retired in Phase 49.2A and must not
# be used as a hero target anymore.


def _safe_file_url(field_file) -> str:
    if not field_file:
        return ""
    try:
        return str(field_file.url or "").strip()
    except Exception:
        return ""


def _product_for(asset: ImportedPrintAsset | None):
    if asset is None:
        return None
    try:
        return asset.product
    except Exception:
        return None


def _desktop_data(asset: ImportedPrintAsset | None) -> dict:
    if asset is None:
        return {}
    try:
        payload = asset.source_payload or {}
        data = payload.get("desktop_catalog_v85") if isinstance(payload, dict) else {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _slider_seo(asset: ImportedPrintAsset | None) -> dict:
    """Reuse the Catalog Center 8.7.1 operator/AI slider SEO resolver."""
    if asset is None:
        return {}
    try:
        from store.epic49_publish_options import _homepage_slider_seo

        data = _desktop_data(asset)
        if not data:
            return {}
        return _homepage_slider_seo(data, _product_for(asset))
    except Exception:
        return {}


def _asset_title(asset: ImportedPrintAsset | None) -> str:
    if asset is None:
        return ""
    product = _product_for(asset)
    slider = _slider_seo(asset)
    return (
        str(slider.get("title_fa") or "").strip()
        or str(getattr(asset, "persian_title", "") or "").strip()
        or str(getattr(product, "title", "") or "").strip()
        or str(getattr(asset, "display_title", "") or "").strip()
        or str(getattr(asset, "title", "") or "").strip()
    )


def _asset_description(asset: ImportedPrintAsset | None) -> str:
    if asset is None:
        return ""
    product = _product_for(asset)
    slider = _slider_seo(asset)
    value = (
        str(slider.get("description_fa") or "").strip()
        or str(getattr(asset, "persian_short_description", "") or "").strip()
        or str(getattr(product, "short_description", "") or "").strip()
        or str(getattr(asset, "short_description", "") or "").strip()
        or str(getattr(asset, "persian_description", "") or "").strip()
        or str(getattr(asset, "description", "") or "").strip()
    )
    return " ".join(value.split())[:480]


def _asset_group(asset: ImportedPrintAsset | None) -> str:
    if asset is None:
        return ""
    product = _product_for(asset)
    try:
        category_name = str(product.category.name or "").strip() if product and product.category_id else ""
    except Exception:
        category_name = ""
    if category_name:
        return category_name[:160]

    try:
        metrics = asset.metrics
        display = getattr(metrics, "get_segment_display", None)
        if callable(display):
            value = str(display() or "").strip()
            if value:
                return value[:160]
    except Exception:
        pass

    try:
        return str(asset.source.name or "").strip()[:160]
    except Exception:
        return "مدل منتخب"


def _requested_slider_image(asset: ImportedPrintAsset | None) -> str:
    """Resolve the exact image selected by the Windows Catalog Center when possible."""
    if asset is None:
        return ""
    data = _desktop_data(asset)
    requested = str(data.get("homepage_slider_image_url") or "").strip()

    if not requested:
        product = _product_for(asset)
        try:
            requested = str(product.catalog_profile.homepage_slider_image_url or "").strip() if product else ""
        except Exception:
            requested = ""

    if requested:
        try:
            row = asset.images.filter(remote_url=requested).exclude(image="").order_by("sort_order", "id").first()
            if row is not None:
                local = _safe_file_url(getattr(row, "image", None))
                if local:
                    return local
        except Exception:
            pass
        return requested
    return ""


def _asset_image(asset: ImportedPrintAsset | None) -> str:
    if asset is None:
        return ""

    selected = _requested_slider_image(asset)
    if selected:
        return selected

    # catalog_image_url already prefers the locally imported preview and then
    # falls back to the original remote image / extracted gallery.
    try:
        value = str(asset.catalog_image_url or "").strip()
        if value:
            return value
    except Exception:
        pass

    product = _product_for(asset)
    if product is not None:
        value = _safe_file_url(getattr(product, "main_image", None))
        if value:
            return value
    return ""


def _absolute_remote_url(value: str) -> str:
    """Return only an http(s) URL suitable for the model URLField.

    Local /media/... previews remain perfectly valid for rendering, but putting a
    relative path inside HomepageHeroSlide.image_url would fail URLField form
    validation. Therefore local previews are shown by effective_image_url while
    image_url remains empty unless the candidate is genuinely remote.
    """

    value = str(value or "").strip()
    parsed = urlparse(value)
    return value if parsed.scheme in {"http", "https"} and parsed.netloc else ""


def _asset_target(asset: ImportedPrintAsset | None) -> str:
    product = _product_for(asset)
    if product is not None and getattr(product, "is_active", False):
        try:
            return product.get_absolute_url()
        except Exception:
            pass
    return reverse("store:product_list")


def _candidate_urls(asset: ImportedPrintAsset | None) -> list[str]:
    urls: list[str] = []

    def add(value):
        value = str(value or "").strip()
        if value and value not in urls:
            urls.append(value)

    if asset is None:
        return urls

    add(_requested_slider_image(asset))
    add(_asset_image(asset))
    add(_safe_file_url(getattr(asset, "preview_image", None)))
    add(getattr(asset, "remote_image_url", ""))

    try:
        for row in asset.images.all().order_by("sort_order", "id")[:40]:
            add(getattr(row, "remote_url", ""))
            add(_safe_file_url(getattr(row, "image", None)))
    except Exception:
        pass

    try:
        for value in asset.metrics.image_urls or []:
            add(value)
    except Exception:
        pass

    product = _product_for(asset)
    if product is not None:
        add(_safe_file_url(getattr(product, "main_image", None)))
        try:
            for row in product.images.all().order_by("sort_order", "id")[:24]:
                add(_safe_file_url(getattr(row, "image", None)))
        except Exception:
            pass
    return urls[:40]


def hero_suggestions(asset: ImportedPrintAsset | None) -> dict:
    title = _asset_title(asset) or "مدل منتخب"
    group = _asset_group(asset) or "مدل منتخب"
    preview_url = _asset_image(asset)
    slider = _slider_seo(asset)
    alt_text = str(slider.get("image_alt_fa") or "").strip() or f"{title} - {group} | 3DPrintHub"
    button_text = str(slider.get("button_text_fa") or "").strip() or "مشاهده محصول"
    return {
        "title": title[:220],
        "description": _asset_description(asset),
        "group_title": group[:160],
        "image_alt_text": alt_text[:240],
        "button_text": button_text[:80],
        "focus_keyword": str(slider.get("focus_keyword_fa") or "").strip()[:180],
        "preview_url": preview_url,
        "image_url": _absolute_remote_url(preview_url),
        "target_url": _asset_target(asset),
        "images": _candidate_urls(asset),
    }


# ---- Runtime model contract -------------------------------------------------
# These properties replace the Phase45 fallbacks without changing a database
# field, therefore makemigrations remains clean.


def _effective_image_url(self: HomepageHeroSlide) -> str:
    return str(self.image_url or "").strip() or _asset_image(getattr(self, "asset", None))


def _effective_title(self: HomepageHeroSlide) -> str:
    return str(self.title_override or "").strip() or _asset_title(getattr(self, "asset", None)) or "مدل منتخب"


def _effective_description(self: HomepageHeroSlide) -> str:
    return str(self.description or "").strip() or _asset_description(getattr(self, "asset", None))


def _effective_group_title(self: HomepageHeroSlide) -> str:
    return str(self.group_title or "").strip() or _asset_group(getattr(self, "asset", None)) or "مدل منتخب"


def _effective_alt_text(self: HomepageHeroSlide) -> str:
    explicit = str(self.image_alt_text or "").strip()
    if explicit:
        return explicit
    slider = _slider_seo(getattr(self, "asset", None))
    slider_alt = str(slider.get("image_alt_fa") or "").strip()
    if slider_alt:
        return slider_alt[:240]
    return f"{self.effective_title} - {self.effective_group_title} | 3DPrintHub"[:240]


def _target_url(self: HomepageHeroSlide) -> str:
    return _asset_target(getattr(self, "asset", None))


def _candidate_image_urls(self: HomepageHeroSlide) -> list[str]:
    return _candidate_urls(getattr(self, "asset", None))


HomepageHeroSlide.effective_image_url = property(_effective_image_url)
HomepageHeroSlide.effective_title = property(_effective_title)
HomepageHeroSlide.effective_description = property(_effective_description)
HomepageHeroSlide.effective_group_title = property(_effective_group_title)
HomepageHeroSlide.effective_alt_text = property(_effective_alt_text)
HomepageHeroSlide.target_url = property(_target_url)
HomepageHeroSlide.candidate_image_urls = _candidate_image_urls


# ---- Server-side save safety net -------------------------------------------
# JS provides immediate UX. This signal guarantees blank fields are still
# completed when JavaScript is blocked/cached.


def _prefill_slide_before_save(sender, instance: HomepageHeroSlide, **_kwargs):
    if not instance.asset_id:
        return
    data = hero_suggestions(instance.asset)
    if not str(instance.title_override or "").strip():
        instance.title_override = data["title"]
    if not str(instance.group_title or "").strip():
        instance.group_title = data["group_title"]
    if not str(instance.description or "").strip():
        instance.description = data["description"]
    if not str(instance.image_alt_text or "").strip():
        instance.image_alt_text = data["image_alt_text"]
    if not str(instance.button_text or "").strip() or instance.button_text == "مشاهده محصول":
        instance.button_text = data["button_text"] or "مشاهده محصول"
    if not str(instance.image_url or "").strip() and data["image_url"]:
        instance.image_url = data["image_url"]


pre_save.connect(
    _prefill_slide_before_save,
    sender=HomepageHeroSlide,
    weak=False,
    dispatch_uid="phase49_2b_homepage_hero_prefill",
)


# ---- Admin defaults ---------------------------------------------------------
# New slides should start with the approval checkbox selected, while still
# allowing an editor to explicitly turn it off before saving.


def _install_admin_initial_defaults():
    model_admin = admin.site._registry.get(HomepageHeroSlide)
    if model_admin is None or getattr(model_admin, "_phase49_2b_initial_patched", False):
        return

    original = model_admin.get_changeform_initial_data

    def get_changeform_initial_data(this, request):
        initial = dict(original(request) or {})
        initial.setdefault("is_active", True)
        return initial

    model_admin.get_changeform_initial_data = MethodType(get_changeform_initial_data, model_admin)
    model_admin._phase49_2b_initial_patched = True


_install_admin_initial_defaults()


# ---- Staff-only AJAX endpoint ----------------------------------------------

@staff_member_required
@require_GET
def hero_asset_prefill_view(request):
    raw_id = str(request.GET.get("asset_id") or "").strip()
    if not raw_id.isdigit():
        return JsonResponse({"ok": False, "error": "asset_id نامعتبر است."}, status=400)

    asset = get_object_or_404(
        ImportedPrintAsset.objects.select_related("source", "product__category"),
        pk=int(raw_id),
    )
    return JsonResponse({"ok": True, "asset_id": asset.pk, **hero_suggestions(asset)})
