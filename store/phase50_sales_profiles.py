from __future__ import annotations

from django.db import models

from .models import Product, ProductVariant


PROFILE_SELECTION_CHOICES = [
    ("list", "فهرست کامل پروفایل‌ها"),
    ("size", "انتخاب بر اساس سایز"),
    ("weight", "انتخاب بر اساس وزن"),
    ("build", "انتخاب بر اساس مدل ساخت"),
    ("size_build", "سایز ← مدل ساخت"),
    ("build_size", "مدل ساخت ← سایز"),
    ("size_weight", "سایز ← وزن"),
    ("weight_size", "وزن ← سایز"),
    ("size_weight_build", "سایز ← وزن ← مدل ساخت"),
    ("size_build_weight", "سایز ← مدل ساخت ← وزن"),
]


def _has_field(model, name: str) -> bool:
    return any(field.name == name for field in model._meta.get_fields())


def _contribute(model, name: str, field: models.Field) -> None:
    if not _has_field(model, name):
        field.contribute_to_class(model, name)


def _selection_value(self) -> str:
    mode = str(getattr(self.product, "sales_profile_selection_mode", "size_build") or "size_build")
    size = str(getattr(self, "size_label", "") or "").strip()
    build = ""
    if hasattr(self, "get_build_profile_display"):
        try:
            build = str(self.get_build_profile_display() or "").strip()
        except Exception:
            build = str(getattr(self, "build_profile", "") or "").strip()
    weight = getattr(self, "final_weight_grams", 0) or getattr(self, "material_weight_grams", 0) or 0
    weight_label = f"{weight:g} گرم" if hasattr(weight, "__format__") else f"{weight} گرم"

    if mode == "size":
        return size or str(getattr(self, "sales_profile_name", "") or "")
    if mode == "weight":
        return weight_label
    if mode == "build":
        return build or str(getattr(self, "sales_profile_name", "") or "")
    if mode == "size_build":
        return " • ".join(part for part in (size, build) if part)
    if mode == "build_size":
        return " • ".join(part for part in (build, size) if part)
    if mode == "size_weight":
        return " • ".join(part for part in (size, weight_label) if part)
    if mode == "weight_size":
        return " • ".join(part for part in (weight_label, size) if part)
    if mode == "size_weight_build":
        return " • ".join(part for part in (size, weight_label, build) if part)
    if mode == "size_build_weight":
        return " • ".join(part for part in (size, build, weight_label) if part)
    return str(getattr(self, "sales_profile_name", "") or getattr(self, "commerce_display_label", "") or "")


def _profile_display_label(self) -> str:
    explicit = str(getattr(self, "sales_profile_name", "") or "").strip()
    if explicit:
        return explicit
    return _selection_value(self) or str(getattr(self, "commerce_display_label", "") or self.code)


def _install_variant_constraint_state() -> None:
    constraints = [
        constraint
        for constraint in ProductVariant._meta.constraints
        if constraint.name not in {
            "uniq_product_material_quality_color_size_build",
            "uniq_product_material_quality_color_size_build_profile",
        }
    ]
    constraints.append(
        models.UniqueConstraint(
            fields=(
                "product",
                "material",
                "quality",
                "color",
                "size_label",
                "build_profile",
                "sales_profile_key",
            ),
            name="uniq_product_material_quality_color_size_build_profile",
        )
    )
    ProductVariant._meta.constraints = constraints


def install() -> None:
    _contribute(
        Product,
        "sales_profile_selection_mode",
        models.CharField(
            max_length=24,
            choices=PROFILE_SELECTION_CHOICES,
            default="size_build",
            db_index=True,
            verbose_name="روش انتخاب پروفایل فروش",
            help_text="تعیین می‌کند مشتری پروفایل‌های این محصول را بر اساس سایز، وزن، مدل ساخت یا ترکیب آن‌ها انتخاب کند.",
        ),
    )
    _contribute(
        Product,
        "sales_profile_selector_label",
        models.CharField(
            max_length=120,
            blank=True,
            default="",
            verbose_name="عنوان انتخاب پروفایل",
            help_text="مثال: سایز و مدل ساخت را انتخاب کنید. اگر خالی باشد عنوان مناسب خودکار نمایش داده می‌شود.",
        ),
    )

    _contribute(
        ProductVariant,
        "sales_profile_name",
        models.CharField(
            max_length=120,
            blank=True,
            default="",
            verbose_name="نام پروفایل فروش",
            help_text="مثال: 24 سانتی‌متر سبک یا 300 گرم توپر.",
        ),
    )
    _contribute(
        ProductVariant,
        "sales_profile_key",
        models.CharField(
            max_length=80,
            blank=True,
            default="",
            db_index=True,
            verbose_name="کلید پروفایل",
            help_text="شناسه داخلی برای اجازه داشتن چند پروفایل با متریال/رنگ/سایز مشابه اما وزن، زمان چاپ یا قیمت متفاوت.",
        ),
    )
    _contribute(
        ProductVariant,
        "sales_profile_sort_order",
        models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش پروفایل"),
    )
    _contribute(
        ProductVariant,
        "sales_profile_is_default",
        models.BooleanField(default=False, db_index=True, verbose_name="پروفایل پیش‌فرض"),
    )

    _install_variant_constraint_state()

    if not hasattr(ProductVariant, "sales_profile_selection_value"):
        ProductVariant.sales_profile_selection_value = property(_selection_value)
    if not hasattr(ProductVariant, "sales_profile_display_label"):
        ProductVariant.sales_profile_display_label = property(_profile_display_label)
