from __future__ import annotations

import json
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


PRICE_MODE_CHOICES = [
    ("fixed", "قیمت ثابت"),
    ("range", "بازه قیمت"),
    ("variant", "بر اساس متریال/رنگ"),
    ("quote", "نیازمند استعلام"),
]

SLIDER_EFFECT_CHOICES = [
    ("cinematic_fade", "Cinematic Fade"),
    ("wedding_dissolve", "Wedding Dissolve"),
    ("cinematic_zoom", "Cinematic Zoom"),
    ("ken_burns", "Ken Burns Fade"),
    ("soft_blur", "Soft Blur Dissolve"),
    ("cinematic_reveal", "Cinematic Reveal"),
]
SLIDER_EFFECT_CODES = {code for code, _label in SLIDER_EFFECT_CHOICES}


class ProductCatalogProfile(models.Model):
    product = models.OneToOneField(
        "store.Product",
        on_delete=models.CASCADE,
        related_name="catalog_profile",
        verbose_name="محصول فروشگاه",
    )
    public_slug = models.SlugField(max_length=220, unique=True, allow_unicode=False, verbose_name="اسلاگ عمومی امن")
    legacy_slug = models.CharField(max_length=240, blank=True, db_index=True, verbose_name="اسلاگ قبلی برای Redirect")
    desktop_product_id = models.PositiveBigIntegerField(null=True, blank=True, db_index=True, verbose_name="شناسه محصول دسکتاپ")
    batch_uuid = models.CharField(max_length=80, blank=True, db_index=True, verbose_name="شناسه Batch")
    source_hash = models.CharField(max_length=64, blank=True, db_index=True, verbose_name="هش منبع")
    product_type = models.CharField(max_length=40, default="ready_product", db_index=True, verbose_name="نوع محصول")
    use_description = models.TextField(blank=True, verbose_name="شرح کاربرد")
    availability_status = models.CharField(max_length=40, default="made_to_order", db_index=True, verbose_name="وضعیت عرضه")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="موجودی")
    lead_time_min_days = models.PositiveIntegerField(default=1, verbose_name="حداقل زمان آماده‌سازی")
    lead_time_max_days = models.PositiveIntegerField(default=1, verbose_name="حداکثر زمان آماده‌سازی")
    has_3d_file = models.BooleanField(default=False, verbose_name="فایل سه‌بعدی موجود است")
    commercial_license_status = models.CharField(max_length=30, default="unknown", db_index=True, verbose_name="وضعیت مجوز تجاری")
    license_name = models.CharField(max_length=200, blank=True, verbose_name="نام مجوز")
    license_url = models.URLField(max_length=1000, blank=True, verbose_name="لینک مجوز")
    technical_features = models.JSONField(default=dict, blank=True, verbose_name="ویژگی‌های فنی")
    keywords = models.JSONField(default=list, blank=True, verbose_name="کلیدواژه‌ها")
    price_min = models.PositiveBigIntegerField(default=0, db_index=True, verbose_name="حداقل قیمت")
    price_max = models.PositiveBigIntegerField(default=0, db_index=True, verbose_name="حداکثر قیمت")
    price_mode = models.CharField(max_length=20, choices=PRICE_MODE_CHOICES, default="fixed", db_index=True, verbose_name="مدل قیمت")
    download_image_limit = models.PositiveSmallIntegerField(default=10, verbose_name="سقف دریافت تصویر")

    # Epic49 unified desktop/server homepage slider contract.
    homepage_slider_enabled = models.BooleanField(default=False, db_index=True, verbose_name="نمایش در اسلایدر")
    homepage_slider_image_url = models.CharField(max_length=2000, blank=True, verbose_name="تصویر انتخابی اسلایدر")
    homepage_slider_sort_order = models.PositiveIntegerField(default=100, db_index=True, verbose_name="ترتیب اسلایدر")
    homepage_slider_title_fa = models.CharField(max_length=220, blank=True, verbose_name="عنوان اختصاصی اسلایدر")
    homepage_slider_description_fa = models.TextField(blank=True, verbose_name="توضیح اختصاصی اسلایدر")
    homepage_slider_alt_text = models.CharField(max_length=240, blank=True, verbose_name="Alt اختصاصی تصویر اسلایدر")
    homepage_slider_button_text = models.CharField(max_length=80, blank=True, default="مشاهده محصول", verbose_name="متن دکمه اسلایدر")
    homepage_slider_focus_keyword = models.CharField(max_length=180, blank=True, verbose_name="عبارت کلیدی اسلایدر")
    homepage_slider_transition_effect = models.CharField(max_length=32, choices=SLIDER_EFFECT_CHOICES, default="cinematic_fade", verbose_name="افکت اسلایدر")
    homepage_slider_transition_duration_ms = models.PositiveIntegerField(default=1400, verbose_name="مدت Transition اسلایدر")
    homepage_slider_display_duration_ms = models.PositiveIntegerField(default=7000, verbose_name="مدت نمایش اسلایدر")

    sync_revision = models.PositiveBigIntegerField(default=1, db_index=True, verbose_name="نسخه همگام‌سازی")
    last_modified_source = models.CharField(max_length=20, default="desktop", db_index=True, verbose_name="منبع آخرین تغییر")
    last_modified_by = models.CharField(max_length=120, blank=True, verbose_name="عامل آخرین تغییر")
    last_synced_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="آخرین همگام‌سازی")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "store"
        ordering = ["-updated_at", "-id"]
        verbose_name = "پروفایل کاتالوگ محصول"
        verbose_name_plural = "پروفایل‌های کاتالوگ محصولات"

    def __str__(self):
        return f"{self.product} / {self.public_slug}"


def _json_value(value, default):
    if isinstance(value, type(default)):
        return value
    try:
        parsed = json.loads(value or "")
        return parsed if isinstance(parsed, type(default)) else default
    except Exception:
        return default


def _positive_int(value, default=0) -> int:
    try:
        normalized = str(value if value not in (None, "") else default).replace(",", "").strip()
        return max(0, int(float(normalized or 0)))
    except Exception:
        try:
            return max(0, int(default or 0))
        except Exception:
            return 0


def _bounded_int(value, default: int, minimum: int, maximum: int) -> int:
    return min(maximum, max(minimum, _positive_int(value, default)))


def _slider_seo_from_data(data: dict, product) -> dict:
    content_pack = _json_value(data.get("content_pack_json"), {})
    ai = content_pack.get("homepage_slider_seo") if isinstance(content_pack, dict) else {}
    if not isinstance(ai, dict):
        ai = {}
    image_alts = _json_value(data.get("image_alt_texts_json"), [])
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
    ).strip()
    return {
        "title": title[:220],
        "description": description[:480],
        "alt": alt_text[:240],
        "button": str(data.get("homepage_slider_button_text") or ai.get("button_text_fa") or "مشاهده محصول").strip()[:80] or "مشاهده محصول",
        "focus": str(data.get("homepage_slider_focus_keyword") or ai.get("focus_keyword_fa") or "").strip()[:180],
    }


def _slider_effect(value) -> str:
    value = str(value or "").strip()
    return value if value in SLIDER_EFFECT_CODES else "cinematic_fade"


def _slug_base(product) -> str:
    for value in [getattr(product, "title_en", ""), getattr(product, "source_external_id", ""), getattr(product, "sku", "")]:
        base = slugify(str(value or ""), allow_unicode=False).strip("-")
        if base:
            return base[:200]
    return f"product-{product.pk}"


def safe_public_slug(product) -> str:
    try:
        current = str(product.catalog_profile.public_slug or "").strip()
        if current:
            return current
    except Exception:
        pass
    return _slug_base(product)


def public_product_url(product) -> str:
    return reverse("store:product_detail", kwargs={"slug": safe_public_slug(product)})


def _unique_public_slug(product, preferred="") -> str:
    from store.models import Product

    base = slugify(str(preferred or ""), allow_unicode=False).strip("-") or _slug_base(product)
    base = (base or f"product-{product.pk}")[:200]
    candidate = base
    counter = 1
    while (
        ProductCatalogProfile.objects.exclude(product=product).filter(public_slug=candidate).exists()
        or Product.objects.exclude(pk=product.pk).filter(slug=candidate).exists()
    ):
        counter += 1
        suffix = f"-{counter}"
        candidate = f"{base[:220-len(suffix)]}{suffix}"
    return candidate


def sync_catalog_profile(
    product,
    asset,
    data: dict,
    *,
    price_min=0,
    price_max=0,
    sync_source="desktop",
    sync_actor="",
    bump_revision=True,
) -> ProductCatalogProfile:
    from store.models import Product

    original_slug = str(getattr(product, "slug", "") or "")
    profile = ProductCatalogProfile.objects.filter(product=product).first()
    created = profile is None
    if profile is None:
        profile = ProductCatalogProfile(
            product=product,
            public_slug=_unique_public_slug(product, getattr(product, "title_en", "")),
            legacy_slug=original_slug,
        )
    elif not profile.public_slug:
        profile.public_slug = _unique_public_slug(product, getattr(product, "title_en", ""))
    if not profile.legacy_slug and original_slug and original_slug != profile.public_slug:
        profile.legacy_slug = original_slug

    minimum = _positive_int(price_min or data.get("price_min"), getattr(product, "fixed_price", 0))
    maximum = _positive_int(price_max or data.get("price_max"), minimum)
    if minimum and maximum and maximum < minimum:
        minimum, maximum = maximum, minimum
    options = _json_value(data.get("material_color_options_json"), [])
    if str(data.get("availability_status") or "") == "quote_required":
        price_mode = "quote"
    elif options:
        price_mode = "variant"
    elif maximum > minimum > 0:
        price_mode = "range"
    else:
        price_mode = "fixed"

    desktop_id = _positive_int(data.get("desktop_product_id"), 0)
    profile.desktop_product_id = desktop_id or None
    profile.batch_uuid = str(data.get("batch_uuid") or "")[:80]
    profile.source_hash = str(data.get("source_hash") or "")[:64]
    profile.product_type = str(data.get("product_type") or "ready_product")[:40]
    profile.use_description = str(data.get("use_description") or "")
    profile.availability_status = str(data.get("availability_status") or "made_to_order")[:40]
    profile.stock_quantity = _positive_int(data.get("stock_quantity"), 0)
    profile.lead_time_min_days = _positive_int(data.get("lead_time_min_days"), 0)
    profile.lead_time_max_days = max(
        profile.lead_time_min_days,
        _positive_int(data.get("lead_time_max_days"), profile.lead_time_min_days),
    )
    profile.has_3d_file = bool(data.get("has_3d_file"))
    profile.commercial_license_status = str(data.get("commercial_status") or getattr(asset, "commercial_license_status", "unknown"))[:30]
    profile.license_name = str(data.get("license_name") or getattr(asset, "license_name", ""))[:200]
    profile.license_url = str(data.get("license_url") or getattr(asset, "license_url", ""))[:1000]
    profile.technical_features = _json_value(data.get("technical_features_json"), {})
    profile.keywords = _json_value(data.get("keywords_json"), [])
    profile.price_min = minimum
    profile.price_max = maximum
    profile.price_mode = price_mode
    profile.download_image_limit = min(200, max(1, _positive_int(data.get("download_image_limit"), 10)))

    slider = _slider_seo_from_data(data, product)
    profile.homepage_slider_enabled = bool(data.get("homepage_slider_enabled"))
    profile.homepage_slider_image_url = str(data.get("homepage_slider_image_url") or "")[:2000]
    profile.homepage_slider_sort_order = _positive_int(data.get("homepage_slider_sort_order"), 100)
    profile.homepage_slider_title_fa = slider["title"]
    profile.homepage_slider_description_fa = slider["description"]
    profile.homepage_slider_alt_text = slider["alt"]
    profile.homepage_slider_button_text = slider["button"]
    profile.homepage_slider_focus_keyword = slider["focus"]
    profile.homepage_slider_transition_effect = _slider_effect(data.get("homepage_slider_transition_effect"))
    profile.homepage_slider_transition_duration_ms = _bounded_int(data.get("homepage_slider_transition_duration_ms"), 1400, 300, 4000)
    profile.homepage_slider_display_duration_ms = _bounded_int(data.get("homepage_slider_display_duration_ms"), 7000, 2000, 30000)

    if created:
        profile.sync_revision = 1
    elif bump_revision:
        profile.sync_revision = max(1, int(profile.sync_revision or 1)) + 1
    profile.last_modified_source = str(sync_source or "desktop")[:20]
    profile.last_modified_by = str(sync_actor or "")[:120]
    profile.last_synced_at = timezone.now()
    profile.save()

    if product.slug != profile.public_slug:
        Product.objects.filter(pk=product.pk).update(slug=profile.public_slug)
        product.slug = profile.public_slug
    return profile


def sync_product_seo(product, asset, data: dict) -> None:
    keywords = _json_value(data.get("keywords_json"), [])
    tags_fa = _json_value(data.get("tags_fa_json"), [])
    hashtags = _json_value(data.get("hashtags_fa_json"), [])
    title = str(data.get("seo_title_fa") or product.title or "").strip()[:180]
    description = str(data.get("seo_description_fa") or product.short_description or "").replace("\n", " ").strip()[:320]
    focus = next((str(x).strip() for x in [*keywords, *tags_fa] if str(x).strip()), product.title)[:180]
    product.meta_title = title or product.meta_title
    product.meta_description = description or product.meta_description
    product.seo_focus_keyword = focus
    product.og_title = title or product.title
    product.og_description = description or product.short_description
    product.editorial_source_url = str(data.get("source_url") or getattr(asset, "source_url", ""))[:1000]
    product.source_attribution = str(data.get("author_name") or getattr(asset, "author_name", "") or getattr(asset.source, "name", ""))[:220]
    product.hashtags = " ".join(str(x).strip() for x in hashtags if str(x).strip())
    product.canonical_url = ""
    product.save(update_fields=[
        "meta_title", "meta_description", "seo_focus_keyword", "og_title", "og_description",
        "editorial_source_url", "source_attribution", "hashtags", "canonical_url", "updated_at",
    ])
