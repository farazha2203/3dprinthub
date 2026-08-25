from __future__ import annotations

from types import MethodType

from django.contrib import admin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path
from django.views.decorators.http import require_GET

from store.models import Category, ImportedPrintAsset, ImportedPrintAssetImage
from store.phase50_admin_media_integrity import public_asset_image, public_imported_image

from .models import HomepageHeroSlide
from .phase49_2b_hero_hotfix import hero_suggestions


def _http_url(value) -> str:
    text = str(value or "").strip()
    return text if text.startswith(("https://", "http://")) else ""


def _hero_admin_row_url(row: ImportedPrintAssetImage) -> tuple[str, str]:
    """Return a usable Hero Studio preview URL without exposing working-media.

    The shared Admin resolver prefers a Product-owned gallery match. If its only
    Product fallback is the main image, prefer this row's remote source URL so
    distinct gallery rows do not all collapse to one thumbnail.
    """
    url, source = public_imported_image(row)
    if source == "تصویر اصلی محصول":
        remote = _http_url(getattr(row, "remote_url", ""))
        if remote:
            return remote, "تصویر منبع"
    return url, source


def _product_payload(asset: ImportedPrintAsset) -> dict:
    product = asset.product
    image, image_source = public_asset_image(asset)
    return {
        "asset_id": asset.pk,
        "product_id": product.pk,
        "title": str(product.title or asset.persian_title or asset.title),
        "title_en": str(getattr(product, "title_en", "") or ""),
        "sku": str(product.sku or ""),
        "category_id": product.category_id,
        "category": str(product.category.name if product.category_id else ""),
        "source": str(asset.source.name if asset.source_id else ""),
        "external_id": str(asset.external_id or getattr(product, "source_external_id", "") or ""),
        "image": image,
        "image_source": image_source,
        "is_active": bool(product.is_active),
    }


def _browser_queryset():
    return (
        ImportedPrintAsset.objects
        .filter(product__isnull=False, product__is_active=True)
        .select_related("product", "product__category", "source")
        .order_by("-updated_at", "-id")
    )


def install() -> None:
    model_admin = admin.site._registry.get(HomepageHeroSlide)
    if model_admin is None or getattr(model_admin, "_phase50_hero_media_integrity_installed", False):
        return

    previous_get_urls = model_admin.get_urls

    @require_GET
    def product_browser_view(request):
        if not model_admin.has_view_permission(request):
            return JsonResponse({"ok": False, "error": "دسترسی کافی ندارید."}, status=403)

        query = str(request.GET.get("q") or "").strip()
        category = str(request.GET.get("category") or "").strip()
        try:
            page_number = max(1, int(request.GET.get("page") or 1))
        except Exception:
            page_number = 1

        queryset = _browser_queryset()
        if query:
            queryset = queryset.filter(
                Q(product__title__icontains=query)
                | Q(product__title_en__icontains=query)
                | Q(product__sku__icontains=query)
                | Q(product__source_external_id__icontains=query)
                | Q(persian_title__icontains=query)
                | Q(title__icontains=query)
                | Q(external_id__icontains=query)
                | Q(source__name__icontains=query)
            )
        if category.isdigit():
            queryset = queryset.filter(product__category_id=int(category))

        paginator = Paginator(queryset, 24)
        page_obj = paginator.get_page(page_number)
        categories = list(
            Category.objects.filter(
                is_active=True,
                products__is_active=True,
                products__imported_source_asset__isnull=False,
            )
            .distinct()
            .order_by("sort_order", "name")
            .values("id", "name")
        )
        return JsonResponse({
            "ok": True,
            "items": [_product_payload(asset) for asset in page_obj.object_list],
            "page": page_obj.number,
            "pages": paginator.num_pages,
            "count": paginator.count,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "categories": categories,
        })

    @require_GET
    def asset_detail_view(request):
        if not model_admin.has_view_permission(request):
            return JsonResponse({"ok": False, "error": "دسترسی کافی ندارید."}, status=403)

        raw_id = str(request.GET.get("asset_id") or "").strip()
        if not raw_id.isdigit():
            return JsonResponse({"ok": False, "error": "asset_id نامعتبر است."}, status=400)

        asset = get_object_or_404(
            ImportedPrintAsset.objects.select_related("source", "product__category"),
            pk=int(raw_id),
            product__isnull=False,
        )
        suggestions = hero_suggestions(asset)
        rows = []
        seen = set()

        for image in asset.images.all().order_by("sort_order", "id")[:60]:
            url, source = _hero_admin_row_url(image)
            if not url or url in seen:
                continue
            seen.add(url)
            rows.append({
                "id": image.pk,
                "url": url,
                "url_source": source,
                "alt": str(image.alt_text or suggestions.get("image_alt_text") or ""),
                "is_primary": bool(image.is_primary),
                "is_selected": bool(image.is_selected),
                "width": int(image.source_width or 0),
                "height": int(image.source_height or 0),
                "kind": "asset_image",
            })

        preview, preview_source = public_asset_image(asset)
        if preview and preview not in seen:
            rows.insert(0, {
                "id": None,
                "url": preview,
                "url_source": preview_source,
                "alt": str(suggestions.get("image_alt_text") or ""),
                "is_primary": True,
                "is_selected": True,
                "width": 0,
                "height": 0,
                "kind": "fallback",
            })

        return JsonResponse({
            "ok": True,
            "asset": _product_payload(asset),
            "suggestions": suggestions,
            "images": rows,
        })

    def get_urls(this):
        old_patterns = [
            pattern for pattern in previous_get_urls()
            if getattr(pattern, "name", "") not in {
                "website_homepageheroslide_product_browser",
                "website_homepageheroslide_asset_detail",
            }
        ]
        custom = [
            path(
                "product-browser/",
                this.admin_site.admin_view(product_browser_view),
                name="website_homepageheroslide_product_browser",
            ),
            path(
                "asset-detail/",
                this.admin_site.admin_view(asset_detail_view),
                name="website_homepageheroslide_asset_detail",
            ),
        ]
        return custom + old_patterns

    model_admin.get_urls = MethodType(get_urls, model_admin)
    model_admin._phase50_hero_media_integrity_installed = True
