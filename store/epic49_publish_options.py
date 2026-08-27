from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from urllib.parse import urljoin

from django.utils.text import slugify


COLOR_TYPE_CODES = {
    "solid", "transparent", "translucent", "metallic", "silk", "dual", "multicolor", "gradient"
}


def _safe_list(value):
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value or "[]")
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def _safe_dict(value):
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(value or "{}")
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


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


def _normalized_materials(data: dict) -> list[str]:
    output = []
    seen = set()
    for item in _safe_list(data.get("material_options_json")):
        name = str(item.get("name") if isinstance(item, dict) else item or "").strip()
        if not name or name.casefold() in seen:
            continue
        seen.add(name.casefold())
        output.append(name)
    return output


def _normalized_colors(data: dict) -> list[dict]:
    output = []
    seen = set()
    for item in _safe_list(data.get("color_options_json")):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("color") or item.get("color_name") or "").strip()
        if not name:
            continue
        kind = str(item.get("color_type") or item.get("type") or "solid").strip().lower()
        if kind not in COLOR_TYPE_CODES:
            kind = "solid"
        key = (name.casefold(), kind)
        if key in seen:
            continue
        seen.add(key)
        output.append({
            "color": name,
            "hex": str(item.get("hex") or item.get("hex_code") or "").strip(),
            "color_type": kind,
            "secondary_hex": str(item.get("secondary_hex") or item.get("hex2") or "").strip(),
            "tertiary_hex": str(item.get("tertiary_hex") or item.get("hex3") or "").strip(),
        })
    return output


def normalized_material_color_options(data: dict) -> list[dict]:
    # Prefer the exact pair/offer payload when present because brand,
    # manufacturer and roll-price facts belong to a specific material+color
    # offer. The independent material/color lists remain a legacy fallback.
    raw = _safe_list(data.get("material_color_options_json"))
    output = []
    seen = set()
    for item in raw:
        if not isinstance(item, dict):
            continue
        material = str(item.get("material") or item.get("material_name") or "").strip()
        color = str(item.get("color") or item.get("color_name") or "").strip()
        brand = str(item.get("brand") or item.get("brand_name") or "").strip()
        if not material or not color:
            continue
        kind = str(item.get("color_type") or item.get("type") or "solid").strip().lower()
        if kind not in COLOR_TYPE_CODES:
            kind = "solid"
        key = (material.casefold(), brand.casefold(), color.casefold(), kind)
        if key in seen:
            continue
        seen.add(key)
        output.append({
            "material": material,
            "brand": brand,
            "manufacturer": str(item.get("manufacturer") or item.get("manufacturer_name") or "").strip(),
            "color": color,
            "hex": str(item.get("hex") or item.get("hex_code") or "").strip(),
            "color_type": kind,
            "secondary_hex": str(item.get("secondary_hex") or item.get("hex2") or "").strip(),
            "tertiary_hex": str(item.get("tertiary_hex") or item.get("hex3") or "").strip(),
            "roll_weight_grams": _positive_int(item.get("roll_weight_grams"), 1000),
            "stock_roll_count": item.get("stock_roll_count") or 0,
            "purchase_price_per_roll": _positive_int(item.get("purchase_price_per_roll"), 0),
            "sale_price_per_roll": _positive_int(item.get("sale_price_per_roll"), 0),
            "usd_price_per_roll": item.get("usd_price_per_roll") or 0,
            "usd_fx_rate_toman": item.get("usd_fx_rate_toman") or 0,
        })
    if output:
        return output

    materials = _normalized_materials(data)
    colors = _normalized_colors(data)
    if materials and colors:
        return [
            {
                "material": material,
                "brand": "",
                "manufacturer": "",
                "color": color["color"],
                "hex": color.get("hex", ""),
                "color_type": color.get("color_type", "solid"),
                "secondary_hex": color.get("secondary_hex", ""),
                "tertiary_hex": color.get("tertiary_hex", ""),
                "roll_weight_grams": 1000,
                "stock_roll_count": 0,
                "purchase_price_per_roll": 0,
                "sale_price_per_roll": 0,
                "usd_price_per_roll": 0,
                "usd_fx_rate_toman": 0,
            }
            for material in materials
            for color in colors
        ]
    return []

def _homepage_slider_seo(data: dict, product) -> dict:
    """Return operator-approved 8.7.1 slider copy with AI-pack fallback."""
    content_pack = _safe_dict(data.get("content_pack_json"))
    ai = content_pack.get("homepage_slider_seo") or {}
    if not isinstance(ai, dict):
        ai = {}
    image_alts = _safe_list(data.get("image_alt_texts_json"))
    title = str(
        data.get("homepage_slider_title_fa")
        or ai.get("title_fa")
        or data.get("title_fa")
        or getattr(product, "title", "")
        or ""
    ).strip()
    description = str(
        data.get("homepage_slider_description_fa")
        or ai.get("description_fa")
        or data.get("short_description_fa")
        or data.get("seo_description_fa")
        or getattr(product, "short_description", "")
        or ""
    ).strip()
    alt_text = str(
        data.get("homepage_slider_alt_text")
        or ai.get("image_alt_fa")
        or (image_alts[0] if image_alts else "")
        or title
        or getattr(product, "title", "")
        or ""
    ).strip()
    button = str(
        data.get("homepage_slider_button_text")
        or ai.get("button_text_fa")
        or "مشاهده محصول"
    ).strip()
    focus = str(
        data.get("homepage_slider_focus_keyword")
        or ai.get("focus_keyword_fa")
        or ""
    ).strip()
    return {
        "title_fa": title[:220],
        "description_fa": description[:480],
        "image_alt_fa": alt_text[:240],
        "button_text_fa": button[:80] or "مشاهده محصول",
        "focus_keyword_fa": focus[:180],
    }


def apply_price_range(product, asset, data: dict) -> tuple[int, int]:
    fallback = _positive_int(
        data.get("final_price") if data.get("price_is_final") else data.get("suggested_price"),
        getattr(asset, "fixed_print_price", 0),
    )
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
        updates["price_note"] = (
            f"بازه قیمت اعلامی: {minimum:,} تا {maximum:,} تومان؛ "
            "مبلغ نهایی بر اساس متریال، رنگ و مشخصات سفارش تعیین می‌شود."
        )
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
    from store.models import PrintQuality, Product, ProductVariant
    from store.phase39_models import MaterialColorOption, ProductMaterialRecommendation

    quality = PrintQuality.objects.filter(is_active=True).order_by("sort_order", "id").first()
    if quality is None:
        return []
    specs = asset.technical_specs or {}
    weight = Decimal(str(specs.get("estimated_weight_grams") or 1))
    minutes = max(1, _positive_int(specs.get("estimated_print_minutes"), 60))
    lead_min = max(1, _positive_int(data.get("lead_time_min_days"), getattr(product, "fixed_delivery_days", 1) or 1))
    lead_max = max(lead_min, _positive_int(data.get("lead_time_max_days"), lead_min))
    selected_codes = []
    output = []
    material_seen = set()

    for index, item in enumerate(options):
        material = Material.objects.filter(name__iexact=item["material"]).order_by("id").first()
        if material is None:
            material = Material.objects.create(
                name=item["material"][:100],
                main_usage="تعریف‌شده از Catalog Center",
                sample_parts="محصولات انتخاب‌شده در 3DPrintHub",
                is_active=True,
            )
        elif not material.is_active:
            Material.objects.filter(pk=material.pk).update(is_active=True)
            material.is_active = True

        brand = str(item.get("brand") or "").strip()[:120]
        manufacturer = str(item.get("manufacturer") or "").strip()[:160]
        color = MaterialColorOption.objects.filter(
            material=material,
            name__iexact=item["color"],
            brand_name__iexact=brand,
        ).order_by("id").first()
        color_defaults = {
            "brand_name": brand,
            "manufacturer_name": manufacturer,
            "hex_code": item.get("hex", "")[:20],
            "color_type": item.get("color_type", "solid"),
            "secondary_hex": item.get("secondary_hex", "")[:20],
            "tertiary_hex": item.get("tertiary_hex", "")[:20],
            "roll_weight_grams": Decimal(str(item.get("roll_weight_grams") or 1000)),
            "stock_roll_count_snapshot": Decimal(str(item.get("stock_roll_count") or 0)),
            "purchase_price_per_roll": _positive_int(item.get("purchase_price_per_roll"), 0),
            "sale_price_per_roll": _positive_int(item.get("sale_price_per_roll"), 0),
            "usd_price_per_roll": Decimal(str(item.get("usd_price_per_roll") or 0)),
            "usd_fx_rate_toman": Decimal(str(item.get("usd_fx_rate_toman") or 0)),
            "is_active": True,
        }
        if color is None:
            code = _color_code(material.pk, f"{brand}-{item['color']}" if brand else item["color"])
            suffix = 1
            candidate = code
            while MaterialColorOption.objects.filter(material=material, code=candidate).exists():
                suffix += 1
                candidate = f"{code[:110]}-{suffix}"
            color = MaterialColorOption.objects.create(
                material=material,
                name=item["color"][:100],
                code=candidate,
                sort_order=index,
                **color_defaults,
            )
        else:
            changes = {}
            for key, value in color_defaults.items():
                if getattr(color, key) != value:
                    changes[key] = value
            if changes:
                MaterialColorOption.objects.filter(pk=color.pk).update(**changes)
                for key, value in changes.items():
                    setattr(color, key, value)

        if material.pk not in material_seen:
            ProductMaterialRecommendation.objects.update_or_create(
                product=product,
                material=material,
                defaults={
                    "recommendation": "recommended",
                    "suitability_score": 90,
                    "reason": "این متریال در Catalog Center برای این محصول فعال شده است.",
                    "customer_note": "متریال و رنگ موجود توسط اپراتور 3DPrintHub تأیید شده است.",
                    "is_customer_selectable": True,
                    "sort_order": len(material_seen),
                },
            )
            material_seen.add(material.pk)

        code = f"EP49-{product.pk}-M{material.pk}-C{color.pk}"[:100]
        selected_codes.append(code)
        defaults = {
            "product": product,
            "material": material,
            "quality": quality,
            "color": color,
            "material_weight_grams": weight,
            "final_weight_grams": weight,
            "shipping_weight_grams": weight,
            "print_time_minutes": minutes,
            "fixed_fee": minimum_price or getattr(product, "fixed_price", 0) or 0,
            "cached_unit_price": minimum_price or getattr(product, "fixed_price", 0) or 0,
            "lead_time_min_days": lead_min,
            "lead_time_max_days": lead_max,
            "stock_status": "made_to_order",
            "is_active": True,
        }
        variant = ProductVariant.objects.filter(code=code).first()
        if variant is None:
            variant = ProductVariant.objects.create(code=code, **defaults)
        else:
            for key, value in defaults.items():
                setattr(variant, key, value)
            variant.save()
        output.append({
            "material": material.name,
            "brand": str(getattr(color, "brand_name", "") or ""),
            "manufacturer": str(getattr(color, "manufacturer_name", "") or ""),
            "color": color.name,
            "color_type": color.color_type,
            "hex": color.hex_code,
            "secondary_hex": color.secondary_hex,
            "tertiary_hex": color.tertiary_hex,
            "variant_id": variant.pk,
        })

    ProductVariant.objects.filter(product=product, code__startswith=f"EP49-{product.pk}-").exclude(code__in=selected_codes).update(is_active=False)
    ProductVariant.objects.filter(product=product, code=f"MW-FIX-{asset.pk:07d}-DEFAULT").update(is_active=False)
    if product.order_mode != "variant":
        Product.objects.filter(pk=product.pk).update(order_mode="variant")
        product.order_mode = "variant"
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
            slide.is_active = False
            slide.save(update_fields=["is_active", "updated_at"])
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

    slider_seo = _homepage_slider_seo(data, product)
    defaults = {
        "image_url": image_url,
        "image_alt_text": slider_seo["image_alt_fa"],
        "title_override": slider_seo["title_fa"],
        "group_title": getattr(product.category, "name", "")[:160],
        "description": slider_seo["description_fa"],
        "button_text": slider_seo["button_text_fa"],
        "sort_order": max(0, _positive_int(data.get("homepage_slider_sort_order"), 100)),
        "is_active": True,
    }
    if slide is None:
        slide = HomepageHeroSlide.objects.create(asset=asset, **defaults)
    else:
        for key, value in defaults.items():
            setattr(slide, key, value)
        slide.save()
    existing.exclude(pk=slide.pk).update(is_active=False)
    return {
        "enabled": True,
        "slide_id": slide.pk,
        "image_url": image_url,
        "title": slider_seo["title_fa"],
        "description": slider_seo["description_fa"],
        "image_alt": slider_seo["image_alt_fa"],
        "button_text": slider_seo["button_text_fa"],
        "focus_keyword": slider_seo["focus_keyword_fa"],
    }


def sync_epic49_publish_options(asset) -> dict:
    if not getattr(asset, "product_id", None):
        return {}
    data = _desktop_data(asset)
    if not data:
        return {}

    from store.epic49_catalog_profile import sync_catalog_profile, sync_product_seo

    product = asset.product
    minimum, maximum = apply_price_range(product, asset, data)
    profile = sync_catalog_profile(product, asset, data, price_min=minimum, price_max=maximum)
    sync_product_seo(product, asset, data)
    variants = apply_material_color_variants(product, asset, data, minimum_price=minimum)
    slider = apply_homepage_slider(product, asset, data)
    return {
        "profile_id": profile.pk,
        "public_slug": profile.public_slug,
        "price_min": minimum,
        "price_max": maximum,
        "price_mode": profile.price_mode,
        "material_color_variants": variants,
        "homepage_slider": slider,
        "download_image_limit": profile.download_image_limit,
    }
