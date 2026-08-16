from __future__ import annotations

import json

from django.db import migrations, models
from django.db.models.deletion import CASCADE
from django.utils.text import slugify


def _json_value(value, default):
    if isinstance(value, type(default)):
        return value
    try:
        parsed = json.loads(value or "")
        return parsed if isinstance(parsed, type(default)) else default
    except Exception:
        return default


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

        minimum = int(data.get("price_min") or getattr(product, "fixed_price", 0) or getattr(asset, "fixed_print_price", 0) or 0)
        maximum = int(data.get("price_max") or minimum or 0)
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

        lead_min = max(0, int(data.get("lead_time_min_days") or 0))
        lead_max = max(lead_min, int(data.get("lead_time_max_days") or lead_min or 0))
        public_slug = _unique_slug(ProductCatalogProfile, Product, product)
        keywords = _json_value(data.get("keywords_json"), [])
        tags_fa = _json_value(data.get("tags_fa_json"), [])
        hashtags = _json_value(data.get("hashtags_fa_json"), [])

        ProductCatalogProfile.objects.update_or_create(
            product_id=product.pk,
            defaults={
                "public_slug": public_slug,
                "legacy_slug": legacy_slug if legacy_slug != public_slug else "",
                "desktop_product_id": int(data.get("desktop_product_id") or 0) or None,
                "batch_uuid": str(data.get("batch_uuid") or "")[:80],
                "source_hash": str(data.get("source_hash") or "")[:64],
                "product_type": str(data.get("product_type") or "ready_product")[:40],
                "use_description": str(data.get("use_description") or ""),
                "availability_status": availability[:40],
                "stock_quantity": max(0, int(data.get("stock_quantity") or 0)),
                "lead_time_min_days": lead_min,
                "lead_time_max_days": lead_max,
                "has_3d_file": bool(data.get("has_3d_file")),
                "commercial_license_status": str(data.get("commercial_status") or getattr(asset, "commercial_license_status", "unknown"))[:30],
                "license_name": str(data.get("license_name") or getattr(asset, "license_name", ""))[:200],
                "license_url": str(data.get("license_url") or getattr(asset, "license_url", ""))[:1000],
                "technical_features": _json_value(data.get("technical_features_json"), {}),
                "keywords": keywords,
                "price_min": max(0, minimum),
                "price_max": max(0, maximum),
                "price_mode": price_mode,
                "download_image_limit": min(200, max(1, int(data.get("download_image_limit") or 10))),
                "homepage_slider_enabled": bool(data.get("homepage_slider_enabled")),
                "homepage_slider_image_url": str(data.get("homepage_slider_image_url") or "")[:2000],
                "homepage_slider_sort_order": max(0, int(data.get("homepage_slider_sort_order") or 100)),
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
        )


def noop_reverse(apps, schema_editor):
    # The profile is additive and can be regenerated from ImportedPrintAsset.source_payload.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0027_phase39_variant_color_fk"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductCatalogProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_slug", models.SlugField(max_length=220, unique=True, verbose_name="اسلاگ عمومی امن")),
                ("legacy_slug", models.CharField(blank=True, db_index=True, max_length=240, verbose_name="اسلاگ قبلی برای Redirect")),
                ("desktop_product_id", models.PositiveBigIntegerField(blank=True, db_index=True, null=True, verbose_name="شناسه محصول دسکتاپ")),
                ("batch_uuid", models.CharField(blank=True, db_index=True, max_length=80, verbose_name="شناسه Batch")),
                ("source_hash", models.CharField(blank=True, db_index=True, max_length=64, verbose_name="هش منبع")),
                ("product_type", models.CharField(db_index=True, default="ready_product", max_length=40, verbose_name="نوع محصول")),
                ("use_description", models.TextField(blank=True, verbose_name="شرح کاربرد")),
                ("availability_status", models.CharField(db_index=True, default="made_to_order", max_length=40, verbose_name="وضعیت عرضه")),
                ("stock_quantity", models.PositiveIntegerField(default=0, verbose_name="موجودی")),
                ("lead_time_min_days", models.PositiveIntegerField(default=1, verbose_name="حداقل زمان آماده‌سازی")),
                ("lead_time_max_days", models.PositiveIntegerField(default=1, verbose_name="حداکثر زمان آماده‌سازی")),
                ("has_3d_file", models.BooleanField(default=False, verbose_name="فایل سه‌بعدی موجود است")),
                ("commercial_license_status", models.CharField(db_index=True, default="unknown", max_length=30, verbose_name="وضعیت مجوز تجاری")),
                ("license_name", models.CharField(blank=True, max_length=200, verbose_name="نام مجوز")),
                ("license_url", models.URLField(blank=True, max_length=1000, verbose_name="لینک مجوز")),
                ("technical_features", models.JSONField(blank=True, default=dict, verbose_name="ویژگی‌های فنی")),
                ("keywords", models.JSONField(blank=True, default=list, verbose_name="کلیدواژه‌ها")),
                ("price_min", models.PositiveBigIntegerField(db_index=True, default=0, verbose_name="حداقل قیمت")),
                ("price_max", models.PositiveBigIntegerField(db_index=True, default=0, verbose_name="حداکثر قیمت")),
                ("price_mode", models.CharField(choices=[("fixed", "قیمت ثابت"), ("range", "بازه قیمت"), ("variant", "بر اساس متریال/رنگ"), ("quote", "نیازمند استعلام")], db_index=True, default="fixed", max_length=20, verbose_name="مدل قیمت")),
                ("download_image_limit", models.PositiveSmallIntegerField(default=10, verbose_name="سقف دریافت تصویر")),
                ("homepage_slider_enabled", models.BooleanField(db_index=True, default=False, verbose_name="نمایش در اسلایدر")),
                ("homepage_slider_image_url", models.CharField(blank=True, max_length=2000, verbose_name="تصویر انتخابی اسلایدر")),
                ("homepage_slider_sort_order", models.PositiveIntegerField(db_index=True, default=100, verbose_name="ترتیب اسلایدر")),
                ("last_synced_at", models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="آخرین همگام‌سازی")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("product", models.OneToOneField(on_delete=CASCADE, related_name="catalog_profile", to="store.product", verbose_name="محصول فروشگاه")),
            ],
            options={
                "verbose_name": "پروفایل کاتالوگ محصول",
                "verbose_name_plural": "پروفایل‌های کاتالوگ محصولات",
                "ordering": ["-updated_at", "-id"],
            },
        ),
        migrations.RunPython(backfill_catalog_profiles, noop_reverse),
    ]
