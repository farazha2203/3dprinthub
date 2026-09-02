from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from functools import wraps
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from PIL import Image

from store.epic49_catalog_profile import ProductCatalogProfile, _unique_public_slug, SLIDER_EFFECT_CODES
from store.models import ImportedPrintAssetImage, Product
from store.phase39_models import FilamentBrand, MaterialColorOption
from website.models import HomepageHeroSlide, Material

from .views import _authorized, _unauthorized


MAX_JSON_BODY = 256 * 1024
MAX_FILAMENT_SYNC_BODY = 3 * 1024 * 1024
MAX_FILAMENT_IMAGE_BYTES = 2 * 1024 * 1024
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _auth(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not _authorized(request):
            return _unauthorized()
        return view(request, *args, **kwargs)
    return wrapped


def _json_body(request, *, max_bytes=MAX_JSON_BODY):
    if int(request.headers.get("Content-Length") or 0) > int(max_bytes):
        return None, JsonResponse({"status": "invalid_request", "detail": "Request body is too large."}, status=413)
    if len(request.body or b"") > int(max_bytes):
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
        "homepage_slider_presentation_mode": profile.homepage_slider_presentation_mode,
        "homepage_slider_object_fit": profile.homepage_slider_object_fit,
        "homepage_slider_focal_position": profile.homepage_slider_focal_position,
        "homepage_slider_image_scale_percent": profile.homepage_slider_image_scale_percent,
        "homepage_slider_position_x_percent": profile.homepage_slider_position_x_percent,
        "homepage_slider_position_y_percent": profile.homepage_slider_position_y_percent,
        "homepage_slider_background_mode": profile.homepage_slider_background_mode,
        "homepage_slider_background_color": profile.homepage_slider_background_color,
        "homepage_slider_background_blur_px": profile.homepage_slider_background_blur_px,
        "homepage_slider_desktop_max_width_percent": profile.homepage_slider_desktop_max_width_percent,
        "homepage_slider_desktop_max_height_percent": profile.homepage_slider_desktop_max_height_percent,
        "homepage_slider_mobile_max_width_percent": profile.homepage_slider_mobile_max_width_percent,
        "homepage_slider_mobile_max_height_percent": profile.homepage_slider_mobile_max_height_percent,
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
        "presentation_mode": str(slide.presentation_mode or "product_fit"),
        "image_scale_percent": int(slide.image_scale_percent or 100),
        "image_position_x_percent": int(slide.image_position_x_percent or 50),
        "image_position_y_percent": int(slide.image_position_y_percent or 50),
        "background_mode": str(slide.background_mode or "blur"),
        "background_color": str(slide.background_color or "#071827"),
        "background_blur_px": int(slide.background_blur_px or 18),
        "desktop_max_width_percent": int(slide.desktop_max_width_percent or 78),
        "desktop_max_height_percent": int(slide.desktop_max_height_percent or 88),
        "mobile_max_width_percent": int(slide.mobile_max_width_percent or 92),
        "mobile_max_height_percent": int(slide.mobile_max_height_percent or 72),
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



def _decimal(value, default="0") -> Decimal:
    try:
        return Decimal(str(value if value not in (None, "") else default))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(str(default))


def _filament_code(material_id: int, brand: str, color: str) -> str:
    digest = hashlib.sha1(
        f"{int(material_id)}|{str(brand or '').strip().casefold()}|{str(color or '').strip().casefold()}".encode("utf-8")
    ).hexdigest()[:14]
    return f"desktop-{int(material_id)}-{digest}"[:120]


def _normalize_filament_hex(value) -> str:
    text = str(value or "").strip().upper()
    if not text:
        return ""
    if not text.startswith("#"):
        text = "#" + text
    return text if HEX_RE.match(text) else ""


def _normalize_filament_palette(data) -> list[str]:
    raw = data.get("palette_hexes")
    if not isinstance(raw, list):
        raw = []
    candidates = [
        *raw,
        data.get("hex") or data.get("hex_code") or "",
        data.get("secondary_hex") or "",
        data.get("tertiary_hex") or "",
    ]
    output = []
    seen = set()
    for item in candidates:
        value = str(item or "").strip().upper()
        if not value:
            continue
        if not value.startswith("#"):
            value = "#" + value
        if not HEX_RE.match(value):
            continue
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        output.append(value)
        if len(output) >= 7:
            break
    return output


def _filament_image_payload(data):
    encoded = str(data.get("filament_image_base64") or "").strip()
    if not encoded:
        return None
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("filament_image_base64 is invalid") from exc
    if not raw or len(raw) > MAX_FILAMENT_IMAGE_BYTES:
        raise ValueError("filament image exceeds the 2 MB decoded limit")

    try:
        with Image.open(BytesIO(raw)) as image:
            image.verify()
            fmt = str(image.format or "").upper()
    except Exception as exc:
        raise ValueError("filament image is not a valid raster image") from exc

    extensions = {"WEBP": "webp", "PNG": "png", "JPEG": "jpg"}
    if fmt not in extensions:
        raise ValueError("filament image must be WEBP, PNG or JPEG")
    digest = hashlib.sha256(raw).hexdigest()[:20]
    return raw, f"filament-{digest}.{extensions[fmt]}"


def serialize_filament(option) -> dict:
    stock_grams = getattr(option, "current_stock_grams", None)
    if stock_grams is None:
        stock_grams = (
            _decimal(getattr(option, "stock_roll_count_snapshot", 0))
            * _decimal(getattr(option, "roll_weight_grams", 0))
        )
    roll_weight = _decimal(getattr(option, "roll_weight_grams", 0))
    sale_roll = _decimal(getattr(option, "sale_price_per_roll", 0))
    effective_rate = (
        sale_roll / roll_weight
        if roll_weight > 0 and sale_roll > 0
        else Decimal("0")
    )
    brand = str(getattr(option, "brand_name", "") or "").strip()
    brand_row = FilamentBrand.objects.filter(name__iexact=brand).first() if brand else None
    palette = list(getattr(option, "palette_hexes", None) or [])
    if not palette:
        palette = _normalize_filament_palette({
            "hex": getattr(option, "hex_code", ""),
            "secondary_hex": getattr(option, "secondary_hex", ""),
            "tertiary_hex": getattr(option, "tertiary_hex", ""),
        })
    server_image = _file_url(getattr(option, "filament_image", None))
    external_image = str(getattr(option, "filament_image_url", "") or "").strip()
    return {
        "id": int(option.pk),
        "material": str(option.material.name or ""),
        "material_id": int(option.material_id),
        "material_description": str(getattr(option.material, "catalog_description", "") or ""),
        "material_price_per_kg": int(getattr(option.material, "price_per_kg", 0) or 0),
        "brand": brand,
        "brand_description": str(getattr(brand_row, "description", "") or ""),
        "manufacturer": brand,
        "description": str(getattr(option, "description", "") or ""),
        "color": str(option.name or ""),
        "code": str(option.code or ""),
        "hex": str(option.hex_code or ""),
        "color_type": str(option.color_type or "solid"),
        "color_finish": str(getattr(option, "color_finish", "matte") or "matte"),
        "palette_hexes": palette[:7],
        "secondary_hex": str(option.secondary_hex or ""),
        "tertiary_hex": str(option.tertiary_hex or ""),
        "roll_weight_grams": str(getattr(option, "roll_weight_grams", 1000) or 1000),
        "stock_roll_count": str(getattr(option, "stock_roll_count_snapshot", 0) or 0),
        "current_stock_grams": str(stock_grams or 0),
        "purchase_price_per_roll": int(getattr(option, "purchase_price_per_roll", 0) or 0),
        "sale_price_per_roll": int(getattr(option, "sale_price_per_roll", 0) or 0),
        "usd_price_per_roll": str(getattr(option, "usd_price_per_roll", 0) or 0),
        "usd_fx_rate_toman": str(getattr(option, "usd_fx_rate_toman", 0) or 0),
        "print_hourly_rate": int(getattr(option, "print_hourly_rate", 0) or 0),
        "supervision_hourly_rate": int(getattr(option, "supervision_hourly_rate", 0) or 0),
        "preheat_hours": str(getattr(option, "preheat_hours", 0) or 0),
        "preheat_temperature_c": str(getattr(option, "preheat_temperature_c", 0) or 0),
        "preheat_hourly_rate": int(getattr(option, "preheat_hourly_rate", 0) or 0),
        "filament_image_url": server_image or external_image,
        "filament_image_server_url": server_image,
        "effective_sale_price_per_gram": str(effective_rate),
        "is_active": bool(option.is_active),
    }


@require_GET
@_auth
def filaments_view(request):
    queryset = MaterialColorOption.objects.select_related("material").order_by(
        "material__name", "brand_name", "name", "id"
    )
    q = str(request.GET.get("q") or "").strip()
    material_name = str(request.GET.get("material") or "").strip()
    active = str(request.GET.get("active") or "1").strip().lower()
    if active not in {"0", "false", "all"}:
        queryset = queryset.filter(is_active=True)
    if material_name:
        queryset = queryset.filter(material__name__iexact=material_name)
    if q:
        from django.db.models import Q
        queryset = queryset.filter(
            Q(material__name__icontains=q)
            | Q(name__icontains=q)
            | Q(brand_name__icontains=q)
            | Q(manufacturer_name__icontains=q)
        )
    items = [serialize_filament(item) for item in queryset[:500]]
    return JsonResponse({
        "status": "ok",
        "items": items,
        "count": len(items),
        "contract": "phase49-filament-library-v3",
    })


@csrf_exempt
@require_POST
@_auth
def filament_sync_view(request):
    payload, error = _json_body(request, max_bytes=MAX_FILAMENT_SYNC_BODY)
    if error:
        return error
    data = payload.get("filament") if isinstance(payload.get("filament"), dict) else payload

    material_name = str(data.get("material") or data.get("material_name") or "").strip()[:100]
    color = str(data.get("color") or data.get("color_name") or "").strip()[:100]
    brand = str(data.get("brand") or data.get("brand_name") or "").strip()[:120]
    legacy_manufacturer = str(
        data.get("manufacturer") or data.get("manufacturer_name") or ""
    ).strip()[:160]
    filament_description = str(
        data.get("description") or data.get("filament_description") or ""
    ).strip()
    brand_description = str(data.get("brand_description") or "").strip()
    material_description = str(data.get("material_description") or "").strip()
    if not brand:
        brand = legacy_manufacturer[:120]
    manufacturer = brand
    if not material_name or not color or not brand:
        return JsonResponse(
            {
                "status": "invalid_request",
                "detail": "material, brand and color are required",
            },
            status=400,
        )

    roll_weight = max(Decimal("1"), _decimal(data.get("roll_weight_grams"), "1000"))
    stock_roll_count = max(Decimal("0"), _decimal(
        data.get("stock_roll_count", data.get("stock_roll_count_snapshot", 0)),
        "0",
    ))
    palette = _normalize_filament_palette(data)
    primary_hex = _normalize_filament_hex(
        data.get("hex") or data.get("hex_code") or ""
    )
    secondary_hex = _normalize_filament_hex(data.get("secondary_hex") or "")
    tertiary_hex = _normalize_filament_hex(data.get("tertiary_hex") or "")
    try:
        image_payload = _filament_image_payload(data)
    except ValueError as exc:
        return JsonResponse(
            {"status": "invalid_request", "detail": str(exc)},
            status=400,
        )

    with transaction.atomic():
        material = Material.objects.filter(name__iexact=material_name).order_by("id").first()
        if material is None:
            material = Material.objects.create(
                name=material_name,
                main_usage="تعریف‌شده از کتابخانه Filament در Catalog Center",
                sample_parts="محصولات 3DPrintHub",
                is_active=True,
            )
        elif not material.is_active:
            Material.objects.filter(pk=material.pk).update(is_active=True)
            material.is_active = True

        material_updates = {}
        if "material_description" in data:
            material_updates["catalog_description"] = material_description
        if "material_price_per_kg" in data:
            material_updates["price_per_kg"] = max(
                0, _as_int(data.get("material_price_per_kg"), 0)
            )
        if material_updates:
            Material.objects.filter(pk=material.pk).update(**material_updates)
            for key, value in material_updates.items():
                setattr(material, key, value)

        brand_row = FilamentBrand.objects.filter(name__iexact=brand).first()
        if brand_row is None:
            brand_row = FilamentBrand.objects.create(
                name=brand,
                description=brand_description,
                is_active=True,
            )
        else:
            brand_updates = {}
            if not brand_row.is_active:
                brand_updates["is_active"] = True
            if "brand_description" in data:
                brand_updates["description"] = brand_description
            if brand_updates:
                FilamentBrand.objects.filter(pk=brand_row.pk).update(**brand_updates)
                for key, value in brand_updates.items():
                    setattr(brand_row, key, value)

        option = MaterialColorOption.objects.filter(
            material=material,
            name__iexact=color,
            brand_name__iexact=brand,
        ).order_by("id").first()

        color_type = str(data.get("color_type") or "solid").strip().lower()
        valid_color_types = {code for code, _label in MaterialColorOption.COLOR_TYPE_CHOICES}
        if color_type not in valid_color_types:
            color_type = "solid"
        color_finish = str(data.get("color_finish") or "matte").strip().lower()
        valid_finishes = {
            code
            for code, _label in MaterialColorOption._meta.get_field("color_finish").choices
        }
        if color_finish not in valid_finishes:
            color_finish = "matte"

        values = {
            "brand_name": brand,
            "manufacturer_name": manufacturer,
            "description": filament_description,
            "hex_code": primary_hex or (palette[0] if palette else ""),
            "color_type": color_type,
            "color_finish": color_finish,
            "palette_hexes": palette,
            "secondary_hex": (
                secondary_hex
                or (palette[1] if len(palette) > 1 else "")
            ),
            "tertiary_hex": (
                tertiary_hex
                or (palette[2] if len(palette) > 2 else "")
            ),
            "roll_weight_grams": roll_weight,
            "stock_roll_count_snapshot": stock_roll_count,
            "purchase_price_per_roll": max(0, _as_int(data.get("purchase_price_per_roll"), 0)),
            "sale_price_per_roll": max(0, _as_int(data.get("sale_price_per_roll"), 0)),
            "usd_price_per_roll": max(Decimal("0"), _decimal(data.get("usd_price_per_roll"), "0")),
            "usd_fx_rate_toman": max(Decimal("0"), _decimal(data.get("usd_fx_rate_toman"), "0")),
            "print_hourly_rate": max(0, _as_int(data.get("print_hourly_rate"), 0)),
            "supervision_hourly_rate": max(0, _as_int(data.get("supervision_hourly_rate"), 0)),
            "preheat_hours": max(Decimal("0"), _decimal(data.get("preheat_hours"), "0")),
            "preheat_temperature_c": max(Decimal("0"), _decimal(data.get("preheat_temperature_c"), "0")),
            "preheat_hourly_rate": max(0, _as_int(data.get("preheat_hourly_rate"), 0)),
            "filament_image_url": str(data.get("filament_image_url") or "").strip()[:500],
            "is_active": bool(data.get("is_active", True)),
        }

        if option is None:
            code = _filament_code(material.pk, brand, color)
            candidate = code
            suffix = 1
            while MaterialColorOption.objects.filter(material=material, code=candidate).exists():
                suffix += 1
                candidate = f"{code[:110]}-{suffix}"
            option = MaterialColorOption.objects.create(
                material=material,
                name=color,
                code=candidate,
                **values,
            )
            created = True
        else:
            for key, value in values.items():
                setattr(option, key, value)
            created = False

        if image_payload is not None:
            raw_image, image_name = image_payload
            option.filament_image.save(
                image_name,
                ContentFile(raw_image),
                save=False,
            )
        option.save()

    return JsonResponse({
        "status": "ok",
        "created": created,
        "filament": serialize_filament(option),
        "contract": "phase49-filament-library-v3",
    })


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


PROFILE_MEDIA_FIELDS = (
    "homepage_slider_presentation_mode",
    "homepage_slider_object_fit",
    "homepage_slider_focal_position",
    "homepage_slider_image_scale_percent",
    "homepage_slider_position_x_percent",
    "homepage_slider_position_y_percent",
    "homepage_slider_background_mode",
    "homepage_slider_background_color",
    "homepage_slider_background_blur_px",
    "homepage_slider_desktop_max_width_percent",
    "homepage_slider_desktop_max_height_percent",
    "homepage_slider_mobile_max_width_percent",
    "homepage_slider_mobile_max_height_percent",
)


def _normalized_profile_media_patch(profile, data: dict) -> dict:
    from store.phase49_3b_profile_media import normalized_profile_media

    merged = {
        name: getattr(profile, name)
        for name in PROFILE_MEDIA_FIELDS
    }
    merged.update({
        name: data[name]
        for name in PROFILE_MEDIA_FIELDS
        if name in data
    })
    normalized = normalized_profile_media(merged)
    return {
        name: value
        for name, value in normalized.items()
        if name in data
    }


def _normalized_slide_media_patch(slide, data: dict) -> dict:
    output = {}
    if "presentation_mode" in data:
        value = str(data.get("presentation_mode") or "product_fit").strip().lower()
        output["presentation_mode"] = value if value in {"product_fit", "full_bleed", "framed", "cinematic"} else "product_fit"
    if "object_fit" in data:
        value = str(data.get("object_fit") or "contain").strip().lower()
        output["object_fit"] = value if value in {"contain", "cover"} else "contain"
    if "focal_position" in data:
        value = str(data.get("focal_position") or "center").strip().lower()
        output["focal_position"] = value if value in {"center", "top", "bottom", "left", "right"} else "center"
    if "background_mode" in data:
        value = str(data.get("background_mode") or "blur").strip().lower()
        output["background_mode"] = value if value in {"solid", "blur", "gradient", "image"} else "blur"
    if "background_color" in data:
        output["background_color"] = str(data.get("background_color") or "#071827").strip()[:24] or "#071827"

    for name, default, minimum, maximum in (
        ("image_scale_percent", 100, 60, 140),
        ("image_position_x_percent", 50, 0, 100),
        ("image_position_y_percent", 50, 0, 100),
        ("background_blur_px", 18, 0, 60),
        ("desktop_max_width_percent", 78, 30, 100),
        ("desktop_max_height_percent", 88, 30, 100),
        ("mobile_max_width_percent", 92, 30, 100),
        ("mobile_max_height_percent", 72, 30, 100),
    ):
        if name in data:
            output[name] = _bounded(data[name], default, minimum, maximum)
    return output


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
        if "has_3d_file" in profile_data:
            profile.has_3d_file = bool(profile_data["has_3d_file"])
        if "price_mode" in profile_data:
            price_mode = str(profile_data.get("price_mode") or "fixed")
            if price_mode in {"fixed", "range", "variant", "quote"}:
                profile.price_mode = price_mode
        for name, value in _normalized_profile_media_patch(profile, profile_data).items():
            setattr(profile, name, value)
        if "technical_features" in profile_data and isinstance(profile_data["technical_features"], dict):
            profile.technical_features = profile_data["technical_features"]
        if "keywords" in profile_data and isinstance(profile_data["keywords"], list):
            profile.keywords = profile_data["keywords"]
        profile.sync_revision = current + 1
        profile.last_modified_source = "desktop"
        profile.last_modified_by = actor
        profile.save()

        # Reuse the existing ProductCatalogProfile -> HomepageHeroSlide mirror.
        # The Phase49.3B wrapper extends it with fit/scale/background fields, so
        # Desktop/API/Admin all operate on one persistent Slider contract.
        from store import epic49_catalog_admin
        epic49_catalog_admin._mirror_profile_to_hero(profile, actor)

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
        for name, value in _normalized_slide_media_patch(slide, data).items():
            setattr(slide, name, value)
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
            selected = getattr(slide, "selected_asset_image", None)
            selected_url = _file_url(getattr(selected, "image", None)) or str(getattr(selected, "remote_url", "") or "")
            profile.homepage_slider_image_url = selected_url or str(slide.image_url or "")
            profile.homepage_slider_presentation_mode = slide.presentation_mode
            profile.homepage_slider_object_fit = slide.object_fit
            profile.homepage_slider_focal_position = slide.focal_position
            profile.homepage_slider_image_scale_percent = slide.image_scale_percent
            profile.homepage_slider_position_x_percent = slide.image_position_x_percent
            profile.homepage_slider_position_y_percent = slide.image_position_y_percent
            profile.homepage_slider_background_mode = slide.background_mode
            profile.homepage_slider_background_color = slide.background_color
            profile.homepage_slider_background_blur_px = slide.background_blur_px
            profile.homepage_slider_desktop_max_width_percent = slide.desktop_max_width_percent
            profile.homepage_slider_desktop_max_height_percent = slide.desktop_max_height_percent
            profile.homepage_slider_mobile_max_width_percent = slide.mobile_max_width_percent
            profile.homepage_slider_mobile_max_height_percent = slide.mobile_max_height_percent
            profile.homepage_slider_transition_effect = slide.transition_effect
            profile.homepage_slider_transition_duration_ms = slide.transition_duration_ms
            profile.homepage_slider_display_duration_ms = slide.display_duration_ms
            if "focus_keyword" in data:
                profile.homepage_slider_focus_keyword = str(data.get("focus_keyword") or "")[:180]
            profile.save()

    return JsonResponse({"status": "ok", "slide": serialize_slide(slide), "revision": slide.sync_revision})
