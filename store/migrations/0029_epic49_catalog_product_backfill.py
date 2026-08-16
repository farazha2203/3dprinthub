from __future__ import annotations

import json

from django.db import migrations
from django.utils.text import slugify


def _json_value(value, default):
    if isinstance(value, type(default)):
        return value
    try:
        parsed = json.loads(value or "")
        return parsed if isinstance(parsed, type(default)) else default
    except Exception:
        return default


def _positive_int(value, default=0):
    try:
        normalized = str(value if value not in (None, "") else default).replace(",", "").strip()
        return max(0, int(float(normalized or 0)))
    except Exception:
        try:
            return max(0, int(default or 0))
        except Exception:
            return 0


def _unique_slug(Profile, Product, product):
    candidates = [getattr(product, "title_en", ""), getattr(product, "source_external_id", ""), getattr(product, "sku", "")]
    base = ""
    for value in candidates:
        base = slugify(str(value or ""), allow_unicode=False).strip("-")
        if base:
            break
    base = (base or f"product-{product.pk}")[:200]
    candidate = base
    counter = 1
    while (
        Profile.objects.filter(public_slug=candidate).exists()
        or Product.objects.exclude(pk=product.pk).filter(slug=candidate).exists()
    ):
        counter += 1
        suffix = f"-{counter}"
        candidate = f"{base[:220-len(suffix)]}{suffix}"
    return candidate


def backfill_catalog_profiles(apps, schema_editor):
    ProductCatalogProfile = apps.get_model("store", "ProductCatalogProfile")
    ImportedPrintAsset = apps.get_model("store", "ImportedPrintAsset")
    Product = apps.get_model("store", "Product")

    assets = ImportedPrintAsset.objects.exclude(product_id=None).select_related("product", "source").order_by("pk")
    for asset in assets.iterator():
        product = asset.product
        legacy_slug = str(getattr(product, "slug", "") or "")[:240]
        payload = asset.source_payload or {}
        data = payload.get("desktop_catalog_v85") if isinstance(payload, dict) else {}
        data = data if isinstance(data, dict) else {}

        fallback_price = _positive_int(getattr(product, "fixed_price", 0), getattr(asset, "fixed_print_price", 0))
        minimum = _positive_int(data.get("price_min"), fallback_price)
        maximum = _positive_int(data.get("price_max"), minimum)
        if minimum and maximum and maximum < minimum:
            minimum, maximum = maximum, minimum
        options = _json_value(data.get("material_color_options_json"), [])
        availability = str(data.get("availability_status") or "made_to_order")
        if availability == "quote_required":
            price_mode = "quote"
        elif options:
            price_mode = "variant"
        elif maximum > minimum > 0:
            price_mode = "range"
        else:
            price_mode = "fixed"

        lead_min = _positive_int(data.get("lead_time_min_days"), 0)
        lead_max = max(lead_min, _positive_int(data.get("lead_time_max_days"), lead_min))
        public_slug = _unique_slug(ProductCatalogProfile, Product, product)
        keywords = _json_value(data.get("keywords_json"), [])
        tags_fa = _json_value(data.get("tags_fa_json"), [])
        hashtags = _json_value(data.get("hashtags_fa_json"), [])
        desktop_id = _positive_int(data.get("desktop_product_id"), 0)

        ProductCatalogProfile.objects.update_or_create(
            product_id=product.pk,
            defaults={
                "public_slug": public_slug,
                "legacy_slug": legacy_slug if legacy_slug != public_slug else "",
                "desktop_product_id": desktop_id or None,
                "batch_uuid": str(data.get("batch_uuid") or "")[:80],
                "source_hash": str(data.get("source_hash") or "")[:64],
                "product_type": str(data.get("product_type") or "ready_product")[:40],
                "use_description": str(data.get("use_description") or ""),
                "availability_status": availability[:40],
                "stock_quantity": _positive_int(data.get("stock_quantity"), 0),
                "lead_time_min_days": lead_min,
                "lead_time_max_days": lead_max,
                "has_3d_file": bool(data.get("has_3d_file")),
                "commercial_license_status": str(data.get("commercial_status") or getattr(asset, "commercial_license_status", "unknown"))[:30],
                "license_name": str(data.get("license_name") or getattr(asset, "license_name", ""))[:200],
                "license_url": str(data.get("license_url") or getattr(asset, "license_url", ""))[:1000],
                "technical_features": _json_value(data.get("technical_features_json"), {}),
                "keywords": keywords,
                "price_min": minimum,
                "price_max": maximum,
                "price_mode": price_mode,
                "download_image_limit": min(200, max(1, _positive_int(data.get("download_image_limit"), 10))),
                "homepage_slider_enabled": bool(data.get("homepage_slider_enabled")),
                "homepage_slider_image_url": str(data.get("homepage_slider_image_url") or "")[:2000],
                "homepage_slider_sort_order": _positive_int(data.get("homepage_slider_sort_order"), 100),
                "last_synced_at": getattr(asset, "updated_at", None),
            },
        )

        meta_title = str(data.get("seo_title_fa") or getattr(product, "meta_title", "") or getattr(product, "title", ""))[:180]
        meta_description = str(data.get("seo_description_fa") or getattr(product, "meta_description", "") or getattr(product, "short_description", "")).replace("\n", " ")[:320]
        focus = next((str(x).strip() for x in [*keywords, *tags_fa] if str(x).strip()), getattr(product, "title", ""))[:180]
        attribution = str(data.get("author_name") or getattr(asset, "author_name", "") or getattr(asset.source, "name", ""))[:220]
        editorial_url = str(data.get("source_url") or getattr(asset, "source_url", ""))[:1000]
        Product.objects.filter(pk=product.pk).update(
            slug=public_slug,
            canonical_url="",
            meta_title=meta_title,
            meta_description=meta_description,
            seo_focus_keyword=focus,
            og_title=meta_title,
            og_description=meta_description,
            editorial_source_url=editorial_url,
            source_attribution=attribution,
            hashtags=" ".join(str(x).strip() for x in hashtags if str(x).strip()),
            robots_index=bool(getattr(product, "is_active", False)),
            robots_follow=bool(getattr(product, "is_active", False)),
        )


def reverse_catalog_slugs(apps, schema_editor):
    ProductCatalogProfile = apps.get_model("store", "ProductCatalogProfile")
    Product = apps.get_model("store", "Product")
    for profile in ProductCatalogProfile.objects.exclude(legacy_slug="").order_by("pk").iterator():
        if not Product.objects.exclude(pk=profile.product_id).filter(slug=profile.legacy_slug).exists():
            Product.objects.filter(pk=profile.product_id).update(slug=profile.legacy_slug)


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0028_epic49_catalog_product_schema"),
    ]

    operations = [
        migrations.RunPython(backfill_catalog_profiles, reverse_catalog_slugs),
    ]
