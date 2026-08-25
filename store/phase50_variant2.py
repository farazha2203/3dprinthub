from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from .models import ProductVariant, StoreOrderItem


BUILD_PROFILE_CHOICES = [
    ("standard", "استاندارد"),
    ("hollow", "توخالی / سبک"),
    ("reinforced", "تقویت‌شده"),
    ("solid", "توپر / سنگین"),
    ("custom", "سفارشی"),
]


def _has_field(model, name: str) -> bool:
    return any(field.name == name for field in model._meta.get_fields())


def _contribute(model, name: str, field: models.Field) -> None:
    if not _has_field(model, name):
        field.contribute_to_class(model, name)


def _variant_display_label(self) -> str:
    parts = []
    if getattr(self, "size_label", ""):
        parts.append(str(self.size_label))
    profile = getattr(self, "build_profile", "standard")
    labels = dict(BUILD_PROFILE_CHOICES)
    if profile:
        parts.append(labels.get(profile, str(profile)))
    if getattr(self, "material_id", None):
        parts.append(str(self.material))
    if getattr(self, "color_id", None):
        parts.append(str(self.color))
    if getattr(self, "quality_id", None):
        parts.append(str(self.quality))
    return " | ".join(parts)


def _effective_shipping_weight_grams(self) -> Decimal:
    explicit = Decimal(getattr(self, "shipping_weight_grams", 0) or 0)
    if explicit > 0:
        return explicit
    product_weight = Decimal(
        getattr(self, "final_weight_grams", 0)
        or getattr(self, "material_weight_grams", 0)
        or 0
    )
    packaging = Decimal(getattr(self, "packaging_weight_grams", 0) or 0)
    return product_weight + packaging


def install() -> None:
    """Add Phase50 Variant 2.0 runtime fields owned by migration 0034.

    The mature ``store.models`` module remains stable; this follows the same
    additive runtime-field pattern already used by Phase49 pricing/media work.
    """

    _contribute(
        ProductVariant,
        "size_label",
        models.CharField(
            max_length=80,
            blank=True,
            default="",
            verbose_name="سایز / ابعاد فروش",
            help_text="مثال: 20 سانتی‌متر، 24 سانتی‌متر یا Large.",
        ),
    )
    _contribute(
        ProductVariant,
        "build_profile",
        models.CharField(
            max_length=20,
            choices=BUILD_PROFILE_CHOICES,
            default="standard",
            db_index=True,
            verbose_name="مدل ساخت / میزان پُری",
        ),
    )
    _contribute(
        ProductVariant,
        "packaging_weight_grams",
        models.DecimalField(
            max_digits=10,
            decimal_places=2,
            default=0,
            validators=[MinValueValidator(0)],
            verbose_name="وزن بسته‌بندی به گرم",
        ),
    )
    for name, label in (
        ("package_length_cm", "طول بسته به سانتی‌متر"),
        ("package_width_cm", "عرض بسته به سانتی‌متر"),
        ("package_height_cm", "ارتفاع بسته به سانتی‌متر"),
    ):
        _contribute(
            ProductVariant,
            name,
            models.DecimalField(
                max_digits=8,
                decimal_places=2,
                default=0,
                validators=[MinValueValidator(0)],
                verbose_name=label,
            ),
        )

    _contribute(
        StoreOrderItem,
        "size_label",
        models.CharField(max_length=80, blank=True, default="", verbose_name="سایز هنگام سفارش"),
    )
    _contribute(
        StoreOrderItem,
        "build_profile",
        models.CharField(max_length=20, blank=True, default="standard", verbose_name="مدل ساخت هنگام سفارش"),
    )
    _contribute(
        StoreOrderItem,
        "packaging_weight_grams",
        models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="وزن بسته‌بندی هنگام سفارش"),
    )
    for name, label in (
        ("package_length_cm", "طول بسته هنگام سفارش"),
        ("package_width_cm", "عرض بسته هنگام سفارش"),
        ("package_height_cm", "ارتفاع بسته هنگام سفارش"),
    ):
        _contribute(
            StoreOrderItem,
            name,
            models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=label),
        )

    if not hasattr(ProductVariant, "commerce_display_label"):
        ProductVariant.commerce_display_label = property(_variant_display_label)
    if not hasattr(ProductVariant, "effective_shipping_weight_grams"):
        ProductVariant.effective_shipping_weight_grams = property(_effective_shipping_weight_grams)
