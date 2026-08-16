from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from urllib.parse import urljoin

from django.utils.text import slugify


def _safe_list(value):
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value or "[]")
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def _desktop_data(asset) -> dict:
    payload = asset.source_payload or {}
    data = payload.get("desktop_catalog_v85") if isinstance(payload, dict) else {}
    return data if isinstance(data, dict) else {}


def _positive_int(value, default=0) -> int:
    try:
        return max(0, int(float(str(value or default).replace(",", ""))))
    except Exception:
        return max(0, int(default or 0))


def _color_code(material_id: int, color_name: str) -> str:
    base = slugify(str(color_name or ""), allow_unicode=False).strip("-")
    if not base:
        base = "color-" + hashlib.sha1(str(color_name or "").encode("utf-8")).hexdigest()[:10]
    return f"m{material_id}-{base}"[:120]


def normalized_material_color_options(data: dict) -> list[dict]:
    raw = _safe_list(data.get("material_color_options_json"))
    output = []
    seen = set()
    for item in raw:
        if not isinstance(item, dict):
            continue
        material = str(item.get("material") or item.get("material_name") or "").strip()
        color = str(item.get("color") or item.get("color_name") or "").strip()
        if not material or not color:
            continue
        key = (material.casefold(), color.casefold())
        if key in seen:
            continue
        seen.add(key)
        output.append({"material": material, "color": color, "hex": str(item.get("hex") or item.get("hex_code") or "").strip()})
    return output


def apply_price_range(product, asset, data: dict) -> tuple[int, int]:
    fallback = _positive_int(data.get("final_price") if data.get("price_is_final") else data.get("suggested_price"), getattr(asset, "fixed_print_price", 0))
    minimum = _positive_int(data.get("price_min"), fallback)
    maximum = _positive_int(data.get("price_max"), minimum)
    if minimum and not maximum:
        maximum = minimum
    if maximum and not minimum:
        minimum = maximum
    if maximum and minimum and maximum < minimum:
        minimum, maximum = maximum, minimum
    updates = {}
    if minimum:
        updates["fixed_price"] = minimum
    if minimum and maximum and maximum > minimum:
        updates["price_is_final"] = False
        updates["consultation_required"] = True
        updates["price_note"] = f"بازه قیمت اعلامی: {minimum:,} تا {maximum:,} تومان؛ مبلغ نهایی بر اساس متریال، رنگ و مشخصات سفارش تعیین می‌شود."
    elif minimum:
        updates["price_note"] = f"قیمت پایه اعلامی: {minimum:,} تومان."
    if updates:
        type(product).objects.filter(pk=product.pk).update(**updates)
        for key, value in updates.items():
            setattr(product, key, value)
    return minimum, maximum


def apply_material_color_variants(product, asset, data: dict, *, minimum_price: int) -> list[dict]:
    options = normalized_material_color_options(data)
    if not options:
        return []
    from website.models import Material
    from store.models import PrintQuality, ProductVariant
    from store.phase39_models import MaterialColorOption, ProductMaterialRecommendation
    quality = PrintQuality.objects.filter(is_active=True).order_by("sort_order", "id").first()
    if quality is None:
        return []
    specs = asset.technical_specs or {}
    weight = Decimal(str(specs.get("estimated_weight_grams") or 1))
    minutes = max(1, _positive_int(specs.get("estimated_print_minutes"), 60))
    selected_codes = []
    output = []
    material_seen = set()
    for index, item in enumerate(options):
        material = Material.objects.filter(name__iexact=item["material"]).order_by("id").first()
        if material is None:
            material = Material.objects.create(name=item["material"][:100], main_usage="تعریف‌شده از Catalog Center", sample_parts="محصولات انتخاب‌شده در 3DPrintHub", is_active=True)
        elif not material.is_active:
            Material.objects.filter(pk=material.pk).update(is_active=True); material.is_active = True
        color = MaterialColorOption.objects.filter(material=material, name__iexact=item["color"]).order_by("id").first()
        if color is None:
            code = _color_code(material.pk, item["color"]); suffix = 1; candidate = code
            while MaterialColorOption.objects.filter(material=material, code=candidate).exists():
                suffix += 1; candidate = f"{code[:110]}-{suffix}"
            color = MaterialColorOption.objects.create(material=material, name=item["color"][:100], code=candidate, hex_code=item["hex"][:20], is_active=True, sort_order=index)
        else:
            changes = {}
            if item["hex"] and color.hex_code != item["hex"][:20]: changes["hex_code"] = item["hex"][:20]
            if not color.is_active: changes["is_active"] = True
            if changes:
                MaterialColorOption.objects.filter(pk=color.pk).update(**changes)
                for key, value in changes.items(): setattr(color, key, value)
        if material.pk not in material_seen:
            ProductMaterialRecommendation.objects.update_or_create(
                product=product, material=material,
                defaults={"recommendation": "recommended", "suitability_score": 90, "reason": "این متریال در Catalog Center برای این محصول فعال شده است.", "customer_note": "متریال و رنگ موجود توسط اپراتور 3DPrintHub تأیید شده است.", "is_customer_selectable": True, "sort_order": len(material_seen)},
            )
            material_seen.add(material.pk)
        code = f"EP49-{product.pk}-M{material.pk}-C{color.pk}"[:100]
        selected_codes.append(code)
        defaults = {
            "product": product, "material": material, "quality": quality, "color": color,
            "material_weight_grams": weight, "final_weight_grams": weight, "shipping_weight_grams": weight,
            "print_time_minutes": minutes, "fixed_fee": minimum_price or getattr(product, "fixed_price", 0) or 0,
            "cached_unit_price": minimum_price or getattr(product, "fixed_price", 0) or 0,
            "lead_time_min_days": max(1, int(getattr(product, "fixed_delivery_days", 1) or 1)),
            "lead_time_max_days": max(1, int(getattr(product, "fixed_delivery_days", 1) or 1)),
            "stock_status": "made_to_order", "is_active": True,
        }
        variant = ProductVariant.objects.filter(code=code).first()
        if variant is None:
            variant = ProductVariant.objects.create(code=code, **defaults)
        else:
            for key, value in defaults.items(): setattr(variant, key, value)
            variant.save()
        output.append({"material": material.name, "color": color.name, "variant_id": variant.pk})
    ProductVariant.objects.filter(product=product, code__startswith=f"EP49-{product.pk}-").exclude(code__in=selected_codes).update(is_active=False)
    ProductVariant.objects.filter(product=product, code=f"MW-FIX-{asset.pk:07d}-DEFAULT").update(is_active=False)
    return output


def _absolute_internal_media_url(relative_url: str) -> str:
    from website.models import SEOSettings
    site_url = str(SEOSettings.load().site_url or "https://3dprinthub.ir").strip().rstrip("/") + "/"
    return urljoin(site_url, str(relative_url or "").lstrip("/"))


def apply_homepage_slider(product, asset, data: dict) -> dict:
    from website.models import HomepageHeroSlide
    enabled = bool(data.get("homepage_slider_enabled"))
    existing = HomepageHeroSlide.objects.filter(asset=asset).order_by("id")
    slide = existing.first()
    if not enabled:
        if slide is not None and slide.is_active:
            slide.is_active = False; slide.save(update_fields=["is_active", "updated_at"])
        existing.exclude(pk=getattr(slide, "pk", None)).update(is_active=False)
        return {"enabled": False, "slide_id": getattr(slide, "pk", None)}
    requested = str(data.get("homepage_slider_image_url") or "").strip()
    image_url = ""
    if requested:
        image_row = asset.images.filter(remote_url=requested).exclude(image="").order_by("sort_order", "id").first()
        if image_row is not None and image_row.image:
            image_url = _absolute_internal_media_url(image_row.image.url)
    if not image_url and asset.preview_image:
        image_url = _absolute_internal_media_url(asset.preview_image.url)
    defaults = {
        "image_url": image_url, "image_alt_text": product.title[:240], "title_override": product.title[:220],
        "group_title": getattr(product.category, "name", "")[:160], "description": (product.short_description or "")[:480],
        "button_text": "مشاهده محصول", "sort_order": max(0, _positive_int(data.get("homepage_slider_sort_order"), 100)), "is_active": True,
    }
    if slide is None:
        slide = HomepageHeroSlide.objects.create(asset=asset, **defaults)
    else:
        for key, value in defaults.items(): setattr(slide, key, value)
        slide.save()
    existing.exclude(pk=slide.pk).update(is_active=False)
    return {"enabled": True, "slide_id": slide.pk, "image_url": image_url}


def sync_epic49_publish_options(asset) -> dict:
    if not getattr(asset, "product_id", None): return {}
    data = _desktop_data(asset)
    if not data: return {}
    product = asset.product
    minimum, maximum = apply_price_range(product, asset, data)
    variants = apply_material_color_variants(product, asset, data, minimum_price=minimum)
    slider = apply_homepage_slider(product, asset, data)
    return {"price_min": minimum, "price_max": maximum, "material_color_variants": variants, "homepage_slider": slider, "download_image_limit": _positive_int(data.get("download_image_limit"), 10)}
