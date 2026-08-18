from __future__ import annotations

import json
from functools import wraps

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from store.epic49_catalog_profile import ProductCatalogProfile, _unique_public_slug, SLIDER_EFFECT_CODES
from store.models import ImportedPrintAssetImage, Product
from website.models import HomepageHeroSlide

from .views import _authorized, _unauthorized


MAX_JSON_BODY = 256 * 1024


def _auth(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not _authorized(request):
            return _unauthorized()
        return view(request, *args, **kwargs)
    return wrapped


def _json_body(request):
    if int(request.headers.get("Content-Length") or 0) > MAX_JSON_BODY:
        return None, JsonResponse({"status": "invalid_request", "detail": "Request body is too large."}, status=413)
    if len(request.body or b"") > MAX_JSON_BODY:
        return None, JsonResponse({"status": "invalid_request", "detail": "Request body is too large."}, status=413)
    try:
        payload = json.loads((request.body or b"{}").decode("utf-8"))
    except Exception:
        return None, JsonResponse({"status": "invalid_request", "detail": "A valid JSON object is required."}, status=400)
    if not isinstance(payload, dict):
        return None, JsonResponse({"status": "invalid_request", "detail": "A JSON object is required."}, status=400)
    return payload, None


def _file_url(field_file) -> str:
    if not field_file:
        return ""
    try:
        return str(field_file.url or "").strip()
    except Exception:
        return ""


def _asset_for_product(product):
    try:
        return product.imported_source_asset
    except Exception:
        return None


def _profile_for(product, *, create=False):
    profile = ProductCatalogProfile.objects.filter(product=product).first()
    if profile is None and create:
        profile = ProductCatalogProfile.objects.create(
            product=product,
            public_slug=_unique_public_slug(product, getattr(product, "title_en", "")),
            legacy_slug=str(getattr(product, "slug", "") or ""),
            sync_revision=1,
            last_modified_source="api",
        )
    return profile


def _slide_for_product(product):
    asset = _asset_for_product(product)
    if asset is None:
        return None
    return HomepageHeroSlide.objects.filter(asset=asset).order_by("id").first()


def _image_rows(asset) -> list[dict]:
    if asset is None:
        return []
    output = []
    for row in asset.images.all().order_by("sort_order", "id")[:80]:
        url = _file_url(row.image) or str(row.remote_url or "").strip()
        if not url:
            continue
        output.append({
            "id": row.pk,
            "url": url,
            "remote_url": str(row.remote_url or ""),
            "alt": str(row.alt_text or ""),
            "is_primary": bool(row.is_primary),
            "is_selected": bool(row.is_selected),
            "width": int(row.source_width or 0),
            "height": int(row.source_height or 0),
        })
    return output


def _profile_payload(profile) -> dict:
    if profile is None:
        return {
            "sync_revision": 0,
            "last_modified_source": "",
            "last_modified_by": "",
        }
    return {
        "public_slug": profile.public_slug,
        "desktop_product_id": profile.desktop_product_id,
        "product_type": profile.product_type,
        "use_description": profile.use_description,
        "availability_status": profile.availability_status,
        "stock_quantity": profile.stock_quantity,
        "lead_time_min_days": profile.lead_time_min_days,
        "lead_time_max_days": profile.lead_time_max_days,
        "has_3d_file": profile.has_3d_file,
        "commercial_license_status": profile.commercial_license_status,
        "license_name": profile.license_name,
        "license_url": profile.license_url,
        "technical_features": profile.technical_features,
        "keywords": profile.keywords,
        "price_min": profile.price_min,
        "price_max": profile.price_max,
        "price_mode": profile.price_mode,
        "download_image_limit": profile.download_image_limit,
        "homepage_slider_enabled": profile.homepage_slider_enabled,
        "homepage_slider_image_url": profile.homepage_slider_image_url,
        "homepage_slider_sort_order": profile.homepage_slider_sort_order,
        "homepage_slider_title_fa": profile.homepage_slider_title_fa,
        "homepage_slider_description_fa": profile.homepage_slider_description_fa,
        "homepage_slider_alt_text": profile.homepage_slider_alt_text,
        "homepage_slider_button_text": profile.homepage_slider_button_text,
        "homepage_slider_focus_keyword": profile.homepage_slider_focus_keyword,
        "homepage_slider_transition_effect": profile.homepage_slider_transition_effect,
        "homepage_slider_transition_duration_ms": profile.homepage_slider_transition_duration_ms,
        "homepage_slider_display_duration_ms": profile.homepage_slider_display_duration_ms,
        "sync_revision": int(profile.sync_revision or 1),
        "last_modified_source": profile.last_modified_source,
        "last_modified_by": profile.last_modified_by,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else "",
    }


def serialize_product(product) -> dict:
    profile = _profile_for(product)
    asset = _asset_for_product(product)
    slide = _slide_for_product(product)
    return {
        "id": product.pk,
        "asset_id": getattr(asset, "pk", None),
        "source_external_id": str(getattr(product, "source_external_id", "") or getattr(asset, "external_id", "") or ""),
        "sku": str(product.sku or ""),
        "title": str(product.title or ""),
        "title_en": str(getattr(product, "title_en", "") or ""),
        "short_description": str(getattr(product, "short_description", "") or ""),
        "description": str(getattr(product, "description", "") or ""),
        "category_id": product.category_id,
        "category": str(product.category.name if product.category_id else ""),
        "is_active": bool(product.is_active),
        "main_image": _file_url(getattr(product, "main_image", None)),
        "meta_title": str(getattr(product, "meta_title", "") or ""),
        "meta_description": str(getattr(product, "meta_description", "") or ""),
        "seo_focus_keyword": str(getattr(product, "seo_focus_keyword", "") or ""),
        "og_title": str(getattr(product, "og_title", "") or ""),
        "og_description": str(getattr(product, "og_description", "") or ""),
        "hashtags": str(getattr(product, "hashtags", "") or ""),
        "robots_index": bool(getattr(product, "robots_index", False)),
        "robots_follow": bool(getattr(product, "robots_follow", False)),
        "profile": _profile_payload(profile),
        "hero_slide_id": getattr(slide, "pk", None),
        "hero_revision": int(getattr(slide, "sync_revision", 0) or 0),
        "images": _image_rows(asset),
        "updated_at": product.updated_at.isoformat() if getattr(product, "updated_at", None) else "",
    }


def serialize_slide(slide) -> dict:
    asset = slide.asset
    product = getattr(asset, "product", None) if asset else None
    profile = _profile_for(product) if product else None
    selected = getattr(slide, "selected_asset_image", None)
    return {
        "id": slide.pk,
        "asset_id": slide.asset_id,
        "product_id": getattr(product, "pk", None),
        "product_title": str(getattr(product, "title", "") or getattr(asset, "persian_title", "") or getattr(asset, "title", "") or ""),
        "selected_asset_image_id": getattr(slide, "selected_asset_image_id", None),
        "selected_image_url": _file_url(getattr(selected, "image", None)) or str(getattr(selected, "remote_url", "") or ""),
        "image_url": str(slide.image_url or ""),
        "effective_image_url": str(slide.effective_image_url or ""),
        "image_alt_text": str(slide.image_alt_text or ""),
        "group_title": str(slide.group_title or ""),
        "title_override": str(slide.title_override or ""),
        "description": str(slide.description or ""),
        "button_text": str(slide.button_text or ""),
        "object_fit": str(slide.object_fit or ""),
        "focal_position": str(slide.focal_position or ""),
        "transition_effect": str(slide.transition_effect or "cinematic_fade"),
        "transition_duration_ms": int(slide.transition_duration_ms or 1400),
        "display_duration_ms": int(slide.display_duration_ms or 7000),
        "sort_order": int(slide.sort_order or 0),
        "is_active": bool(slide.is_active),
        "sync_revision": int(getattr(slide, "sync_revision", 1) or 1),
        "last_modified_source": str(getattr(slide, "last_modified_source", "") or ""),
        "last_modified_by": str(getattr(slide, "last_modified_by", "") or ""),
        "focus_keyword": str(getattr(profile, "homepage_slider_focus_keyword", "") or ""),
        "images": _image_rows(asset),
        "updated_at": slide.updated_at.isoformat() if slide.updated_at else "",
    }


def _conflict(entity: str, expected: int, current: int, current_payload: dict):
    return JsonResponse({
        "status": "conflict",
        "entity": entity,
        "expected_revision": expected,
        "current_revision": current,
        "current": current_payload,
    }, status=409)


def _as_int(value, default=0):
    try:
        return int(float(str(value if value not in (None, "") else default).replace(",", "")))
    except Exception:
        return int(default)


def _bounded(value, default, minimum, maximum):
    return min(maximum, max(minimum, _as_int(value, default)))


@require_GET
@_auth
def products_view(request):
    q = str(request.GET.get("q") or "").strip()
    queryset = Product.objects.select_related("category").order_by("-updated_at", "-id")
    if q:
        from django.db.models import Q
        queryset = queryset.filter(Q(title__icontains=q) | Q(title_en__icontains=q) | Q(sku__icontains=q) | Q(source_external_id__icontains=q))
    try:
        limit = min(200, max(1, int(request.GET.get("limit") or 50)))
    except Exception:
        limit = 50
    items = [serialize_product(item) for item in queryset[:limit]]
    return JsonResponse({"status": "ok", "items": items, "count": len(items), "contract": "epic49-unified-v1"})


@require_GET
@_auth
def product_detail_view(request, product_id: int):
    product = get_object_or_404(Product.objects.select_related("category"), pk=product_id)
    return JsonResponse({"status": "ok", "product": serialize_product(product), "contract": "epic49-unified-v1"})


@csrf_exempt
@require_POST
@_auth
def product_sync_view(request, product_id: int):
    payload, error = _json_body(request)
    if error:
        return error
    product = get_object_or_404(Product.objects.select_related("category"), pk=product_id)
    profile = _profile_for(product, create=True)
    expected = max(0, _as_int(payload.get("expected_revision"), 0))
    current = int(profile.sync_revision or 1)
    if expected != current:
        return _conflict(f"product:{product.pk}", expected, current, serialize_product(product))

    actor = str(payload.get("operator") or "desktop")[:120]
    product_data = payload.get("product") if isinstance(payload.get("product"), dict) else {}
    profile_data = payload.get("profile") if isinstance(payload.get("profile"), dict) else {}

    string_fields = {
        "title": 220,
        "title_en": 220,
        "short_description": 350,
        "description": 0,
        "meta_title": 180,
        "meta_description": 320,
        "seo_focus_keyword": 180,
        "og_title": 180,
        "og_description": 320,
        "hashtags": 1000,
    }
    boolean_fields = {"is_active", "robots_index", "robots_follow"}
    profile_strings = {
        "product_type": 40,
        "use_description": 0,
        "availability_status": 40,
        "commercial_license_status": 30,
        "license_name": 200,
        "license_url": 1000,
        "homepage_slider_image_url": 2000,
        "homepage_slider_title_fa": 220,
        "homepage_slider_description_fa": 0,
        "homepage_slider_alt_text": 240,
        "homepage_slider_button_text": 80,
        "homepage_slider_focus_keyword": 180,
    }

    with transaction.atomic():
        update_fields = []
        for name, max_length in string_fields.items():
            if name in product_data and hasattr(product, name):
                value = str(product_data.get(name) or "")
                setattr(product, name, value[:max_length] if max_length else value)
                update_fields.append(name)
        for name in boolean_fields:
            if name in product_data and hasattr(product, name):
                setattr(product, name, bool(product_data.get(name)))
                update_fields.append(name)
        if update_fields:
            product.save(update_fields=list(dict.fromkeys([*update_fields, "updated_at"])))

        for name, max_length in profile_strings.items():
            if name in profile_data:
                value = str(profile_data.get(name) or "")
                setattr(profile, name, value[:max_length] if max_length else value)
        if "stock_quantity" in profile_data:
            profile.stock_quantity = max(0, _as_int(profile_data["stock_quantity"], 0))
        if "lead_time_min_days" in profile_data:
            profile.lead_time_min_days = max(0, _as_int(profile_data["lead_time_min_days"], 0))
        if "lead_time_max_days" in profile_data:
            profile.lead_time_max_days = max(profile.lead_time_min_days, _as_int(profile_data["lead_time_max_days"], profile.lead_time_min_days))
        if "price_min" in profile_data:
            profile.price_min = max(0, _as_int(profile_data["price_min"], 0))
        if "price_max" in profile_data:
            profile.price_max = max(0, _as_int(profile_data["price_max"], profile.price_min))
        if "download_image_limit" in profile_data:
            profile.download_image_limit = min(200, max(1, _as_int(profile_data["download_image_limit"], 10)))
        if "homepage_slider_enabled" in profile_data:
            profile.homepage_slider_enabled = bool(profile_data["homepage_slider_enabled"])
        if "homepage_slider_sort_order" in profile_data:
            profile.homepage_slider_sort_order = max(0, _as_int(profile_data["homepage_slider_sort_order"], 100))
        if "homepage_slider_transition_effect" in profile_data:
            effect = str(profile_data["homepage_slider_transition_effect"] or "cinematic_fade")
            profile.homepage_slider_transition_effect = effect if effect in SLIDER_EFFECT_CODES else "cinematic_fade"
        if "homepage_slider_transition_duration_ms" in profile_data:
            profile.homepage_slider_transition_duration_ms = _bounded(profile_data["homepage_slider_transition_duration_ms"], 1400, 300, 4000)
        if "homepage_slider_display_duration_ms" in profile_data:
            profile.homepage_slider_display_duration_ms = _bounded(profile_data["homepage_slider_display_duration_ms"], 7000, 2000, 30000)
        if "technical_features" in profile_data and isinstance(profile_data["technical_features"], dict):
            profile.technical_features = profile_data["technical_features"]
        if "keywords" in profile_data and isinstance(profile_data["keywords"], list):
            profile.keywords = profile_data["keywords"]
        profile.sync_revision = current + 1
        profile.last_modified_source = "desktop"
        profile.last_modified_by = actor
        profile.save()

    return JsonResponse({"status": "ok", "product": serialize_product(product), "revision": profile.sync_revision})


@require_GET
@_auth
def hero_slides_view(request):
    queryset = HomepageHeroSlide.objects.select_related("asset", "selected_asset_image").order_by("sort_order", "id")
    items = [serialize_slide(slide) for slide in queryset]
    return JsonResponse({"status": "ok", "items": items, "count": len(items), "contract": "epic49-unified-v1"})


@require_GET
@_auth
def hero_slide_detail_view(request, slide_id: int):
    slide = get_object_or_404(HomepageHeroSlide.objects.select_related("asset", "selected_asset_image"), pk=slide_id)
    return JsonResponse({"status": "ok", "slide": serialize_slide(slide), "contract": "epic49-unified-v1"})


@csrf_exempt
@require_POST
@_auth
def hero_slide_sync_view(request, slide_id: int):
    payload, error = _json_body(request)
    if error:
        return error
    slide = get_object_or_404(HomepageHeroSlide.objects.select_related("asset", "selected_asset_image"), pk=slide_id)
    expected = max(0, _as_int(payload.get("expected_revision"), 0))
    current = int(getattr(slide, "sync_revision", 1) or 1)
    if expected != current:
        return _conflict(f"hero:{slide.pk}", expected, current, serialize_slide(slide))

    data = payload.get("slide") if isinstance(payload.get("slide"), dict) else {}
    actor = str(payload.get("operator") or "desktop")[:120]
    string_fields = {
        "image_url": 1000,
        "image_alt_text": 240,
        "group_title": 160,
        "title_override": 220,
        "description": 0,
        "button_text": 80,
        "object_fit": 20,
        "focal_position": 30,
    }
    with transaction.atomic():
        for name, max_length in string_fields.items():
            if name in data:
                value = str(data.get(name) or "")
                setattr(slide, name, value[:max_length] if max_length else value)
        if "transition_effect" in data:
            effect = str(data.get("transition_effect") or "cinematic_fade")
            slide.transition_effect = effect if effect in SLIDER_EFFECT_CODES else "cinematic_fade"
        if "transition_duration_ms" in data:
            slide.transition_duration_ms = _bounded(data["transition_duration_ms"], 1400, 300, 4000)
        if "display_duration_ms" in data:
            slide.display_duration_ms = _bounded(data["display_duration_ms"], 7000, 2000, 30000)
        if "sort_order" in data:
            slide.sort_order = max(0, _as_int(data["sort_order"], 0))
        if "is_active" in data:
            slide.is_active = bool(data["is_active"])
        if "selected_asset_image_id" in data:
            raw = data.get("selected_asset_image_id")
            if raw in (None, "", 0, "0"):
                slide.selected_asset_image = None
            else:
                image = get_object_or_404(ImportedPrintAssetImage, pk=_as_int(raw), asset_id=slide.asset_id)
                slide.selected_asset_image = image
        slide.sync_revision = current + 1
        slide.last_modified_source = "desktop"
        slide.last_modified_by = actor
        slide.save()

        # Keep ProductCatalogProfile's dedicated slider SEO mirror aligned when
        # this slide belongs to a Store Product. Product revision is intentionally
        # not bumped here; Hero has its own optimistic revision.
        product = getattr(slide.asset, "product", None) if slide.asset else None
        profile = _profile_for(product) if product else None
        if profile is not None:
            profile.homepage_slider_enabled = bool(slide.is_active)
            profile.homepage_slider_sort_order = slide.sort_order
            profile.homepage_slider_title_fa = slide.title_override
            profile.homepage_slider_description_fa = slide.description
            profile.homepage_slider_alt_text = slide.image_alt_text
            profile.homepage_slider_button_text = slide.button_text
            profile.homepage_slider_transition_effect = slide.transition_effect
            profile.homepage_slider_transition_duration_ms = slide.transition_duration_ms
            profile.homepage_slider_display_duration_ms = slide.display_duration_ms
            if "focus_keyword" in data:
                profile.homepage_slider_focus_keyword = str(data.get("focus_keyword") or "")[:180]
            profile.save()

    return JsonResponse({"status": "ok", "slide": serialize_slide(slide), "revision": slide.sync_revision})
