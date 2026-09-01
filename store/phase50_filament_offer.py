from __future__ import annotations

from decimal import Decimal

from django.db import models

from .models import ProductVariant, StoreOrderItem
from .phase39_models import MaterialColorOption


COLOR_BEHAVIOR_CHOICES = [
    ("solid", "تک‌رنگ"),
    ("dual", "دو‌رنگ"),
    ("multicolor", "چندرنگ"),
    ("gradient", "گرادیانی"),
    ("color_shift", "تغییررنگ / Color Shift"),
]

COLOR_FINISH_CHOICES = [
    ("matte", "مات"),
    ("glossy", "براق"),
    ("metallic", "متالیک"),
    ("transparent_matte", "شیشه‌ای مات"),
    ("transparent_glossy", "شیشه‌ای براق"),
    ("silk", "Silk / ابریشمی"),
]


def _has_field(model, name: str) -> bool:
    return any(field.name == name for field in model._meta.get_fields())


def _contribute(model, name: str, field: models.Field) -> None:
    if not _has_field(model, name):
        field.contribute_to_class(model, name)


def install_model_fields() -> None:
    for name, field in (
        (
            "brand_name",
            models.CharField(
                max_length=120,
                blank=True,
                default="",
                verbose_name="برند فیلامنت",
            ),
        ),
        (
            "manufacturer_name",
            models.CharField(
                max_length=160,
                blank=True,
                default="",
                verbose_name="کارخانه / سازنده فیلامنت",
            ),
        ),
        (
            "roll_weight_grams",
            models.DecimalField(
                max_digits=10,
                decimal_places=2,
                default=1000,
                verbose_name="وزن هر رول به گرم",
            ),
        ),
        (
            "stock_roll_count_snapshot",
            models.DecimalField(
                max_digits=10,
                decimal_places=2,
                default=0,
                verbose_name="اسنپ‌شات تعداد رول موجود",
            ),
        ),
        (
            "purchase_price_per_roll",
            models.PositiveBigIntegerField(default=0, verbose_name="قیمت خرید هر رول"),
        ),
        (
            "sale_price_per_roll",
            models.PositiveBigIntegerField(default=0, verbose_name="قیمت فروش هر رول"),
        ),
        (
            "usd_price_per_roll",
            models.DecimalField(
                max_digits=14,
                decimal_places=4,
                default=0,
                verbose_name="قیمت دلاری هر رول",
            ),
        ),
        (
            "usd_fx_rate_toman",
            models.DecimalField(
                max_digits=14,
                decimal_places=2,
                default=0,
                verbose_name="نرخ دلار ثبت‌شده برای این رول",
            ),
        ),
        (
            "print_hourly_rate",
            models.PositiveBigIntegerField(
                default=0,
                verbose_name="نرخ ساعت چاپ این Offer",
            ),
        ),
        (
            "supervision_hourly_rate",
            models.PositiveBigIntegerField(
                default=0,
                verbose_name="نرخ ساعت نظارت این Offer",
            ),
        ),
        (
            "preheat_hours",
            models.DecimalField(
                max_digits=8,
                decimal_places=2,
                default=0,
                verbose_name="مدت پیش‌گرم فیلامنت (ساعت)",
            ),
        ),
        (
            "preheat_temperature_c",
            models.DecimalField(
                max_digits=7,
                decimal_places=2,
                default=0,
                verbose_name="دمای پیش‌گرم فیلامنت (°C)",
            ),
        ),
        (
            "preheat_hourly_rate",
            models.PositiveBigIntegerField(
                default=0,
                verbose_name="هزینه ساعتی پیش‌گرم",
            ),
        ),
        (
            "filament_image_url",
            models.URLField(
                max_length=500,
                blank=True,
                default="",
                verbose_name="تصویر فیلامنت خارجی / سازگاری",
            ),
        ),
        (
            "color_finish",
            models.CharField(
                max_length=32,
                choices=COLOR_FINISH_CHOICES,
                default="matte",
                verbose_name="نوع سطح / Finish",
            ),
        ),
        (
            "palette_hexes",
            models.JSONField(
                blank=True,
                default=list,
                verbose_name="پالت رنگ فیلامنت",
            ),
        ),
        (
            "filament_image",
            models.ImageField(
                blank=True,
                upload_to="store/filaments/%Y/%m/",
                verbose_name="تصویر فیلامنت",
            ),
        ),
    ):
        _contribute(MaterialColorOption, name, field)

    # Migration 0041 changes the persisted field choices. Because this project
    # contributes Phase50 fields at AppConfig.ready() rather than rewriting the
    # mature phase39_models module, mirror the migration state at runtime too.
    MaterialColorOption.COLOR_TYPE_CHOICES = COLOR_BEHAVIOR_CHOICES
    MaterialColorOption._meta.get_field("color_type").choices = COLOR_BEHAVIOR_CHOICES

    _contribute(
        ProductVariant,
        "support_weight_grams",
        models.DecimalField(
            max_digits=10,
            decimal_places=2,
            default=0,
            verbose_name="وزن ساپورت مصرفی",
        ),
    )
    for name, field in (
        (
            "support_weight_grams",
            models.DecimalField(
                max_digits=10,
                decimal_places=2,
                default=0,
                verbose_name="وزن ساپورت هنگام سفارش",
            ),
        ),
        (
            "filament_brand_name",
            models.CharField(
                max_length=120,
                blank=True,
                default="",
                verbose_name="برند فیلامنت هنگام سفارش",
            ),
        ),
        (
            "filament_manufacturer_name",
            models.CharField(
                max_length=160,
                blank=True,
                default="",
                verbose_name="سازنده فیلامنت هنگام سفارش",
            ),
        ),
    ):
        _contribute(StoreOrderItem, name, field)

    MaterialColorOption.current_stock_grams = property(_current_stock_grams)
    MaterialColorOption.current_roll_count = property(_current_roll_count)
    MaterialColorOption.effective_sale_price_per_gram = property(_effective_sale_price_per_gram)


def _matching_spools(option):
    qs = option.material.filament_spools.exclude(
        status__in=["empty", "archived", "quarantine"]
    ).filter(color_name__iexact=option.name)
    brand = str(getattr(option, "brand_name", "") or "").strip()
    if brand:
        qs = qs.filter(brand__iexact=brand)
    return qs


def _current_stock_grams(option):
    qs = _matching_spools(option)
    if qs.exists():
        return qs.aggregate(value=models.Sum("remaining_weight_grams"))["value"] or Decimal("0")
    rolls = Decimal(getattr(option, "stock_roll_count_snapshot", 0) or 0)
    roll_weight = Decimal(getattr(option, "roll_weight_grams", 0) or 0)
    return rolls * roll_weight


def _current_roll_count(option):
    qs = _matching_spools(option).filter(remaining_weight_grams__gt=0)
    if qs.exists():
        return qs.count()
    return Decimal(getattr(option, "stock_roll_count_snapshot", 0) or 0)


def _effective_sale_price_per_gram(option):
    """Owner authority: sale price per roll / roll weight, with no hidden fallback."""
    roll_weight = Decimal(getattr(option, "roll_weight_grams", 0) or 0)
    sale_roll = Decimal(getattr(option, "sale_price_per_roll", 0) or 0)
    if roll_weight <= 0 or sale_roll <= 0:
        return Decimal("0")
    return sale_roll / roll_weight
