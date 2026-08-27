from __future__ import annotations

from functools import wraps
from typing import Any

from django.db import models

from .models import Product, ProductVariant, ShippingMethod


PRICING_POLICY_CHOICES = [
    ("formula", "فرمولی / محاسباتی"),
    ("product_fixed", "قیمت قطعی کل محصول"),
    ("profile_fixed", "قیمت قطعی هر پروفایل / سایز"),
    ("profile_material_fixed", "قیمت قطعی هر پروفایل + متریال"),
    ("profile_material_color_fixed", "قیمت قطعی هر پروفایل + متریال + رنگ"),
]

SHIPPING_SERVICE_CHOICES = [
    ("generic", "روش عمومی"),
    ("pickup_isfahan", "تحویل حضوری اصفهان"),
    ("courier_isfahan", "پیک اصفهان"),
    ("post", "پست"),
    ("tipax", "تیپاکس"),
]

SHIPPING_SCOPE_CHOICES = [
    ("nationwide", "تمام ایران"),
    ("isfahan_only", "فقط اصفهان"),
]

SHIPPING_FEE_MODE_CHOICES = [
    ("calculated", "محاسبه با مبلغ ثابت / قوانین وزن"),
    ("free", "رایگان"),
    ("postpaid", "پس‌کرایه / پرداخت هزینه حمل هنگام تحویل"),
]


class StorePaymentSettings(models.Model):
    title = models.CharField(
        max_length=160,
        default="اطلاعات پرداخت کارت به کارت",
        verbose_name="عنوان نمایشی",
    )
    bank_name = models.CharField(max_length=120, blank=True, verbose_name="نام بانک")
    account_holder = models.CharField(max_length=160, blank=True, verbose_name="نام صاحب حساب")
    card_number = models.CharField(max_length=32, blank=True, verbose_name="شماره کارت")
    sheba_number = models.CharField(max_length=40, blank=True, verbose_name="شماره شبا")
    account_number = models.CharField(max_length=40, blank=True, verbose_name="شماره حساب")
    transfer_instructions = models.TextField(
        blank=True,
        verbose_name="راهنمای واریز برای مشتری",
    )
    is_active = models.BooleanField(default=True, verbose_name="نمایش اطلاعات پرداخت")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "store"
        verbose_name = "اطلاعات پرداخت کارت به کارت"
        verbose_name_plural = "اطلاعات پرداخت کارت به کارت"

    def __str__(self) -> str:
        return self.title or "اطلاعات پرداخت"

    @classmethod
    def load(cls) -> "StorePaymentSettings":
        obj = cls.objects.order_by("pk").first()
        if obj is None:
            obj = cls.objects.create()
        return obj

    def save(self, *args, **kwargs):
        if self.pk is None:
            existing = type(self).objects.order_by("pk").first()
            if existing is not None:
                self.pk = existing.pk
        super().save(*args, **kwargs)
        type(self).objects.exclude(pk=self.pk).delete()


def _has_field(model, name: str) -> bool:
    return any(field.name == name for field in model._meta.get_fields())


def _contribute(model, name: str, field: models.Field) -> None:
    if not _has_field(model, name):
        field.contribute_to_class(model, name)


def install_model_fields() -> None:
    _contribute(
        Product,
        "pricing_policy",
        models.CharField(
            max_length=40,
            choices=PRICING_POLICY_CHOICES,
            default="formula",
            db_index=True,
            verbose_name="سیاست قیمت‌گذاری فروش",
        ),
    )
    _contribute(
        Product,
        "sales_notice",
        models.TextField(
            blank=True,
            default="",
            verbose_name="توضیح اپراتور برای مشتری / محتویات و آماده‌سازی",
        ),
    )
    _contribute(
        Product,
        "enforce_color_stock",
        models.BooleanField(
            default=False,
            verbose_name="کنترل سخت موجودی رنگ/فیلامنت هنگام سفارش",
            help_text=(
                "اگر خاموش باشد، صفر بودن موجودی ثبت‌شده رنگ مانع سفارش محصولات تولید پس از سفارش نمی‌شود. "
                "برای فروش مبتنی بر موجودی واقعی روشن شود."
            ),
        ),
    )
    _contribute(
        ProductVariant,
        "fixed_price_override",
        models.PositiveBigIntegerField(
            default=0,
            verbose_name="قیمت قطعی این پروفایل/ترکیب",
            help_text="در سیاست‌های قیمت قطعی پروفایل/متریال/رنگ استفاده می‌شود؛ صفر یعنی استفاده از قیمت پایه محصول.",
        ),
    )

    for name, field in (
        (
            "service_type",
            models.CharField(
                max_length=32,
                choices=SHIPPING_SERVICE_CHOICES,
                default="generic",
                db_index=True,
                verbose_name="نوع سرویس ارسال",
            ),
        ),
        (
            "delivery_scope",
            models.CharField(
                max_length=24,
                choices=SHIPPING_SCOPE_CHOICES,
                default="nationwide",
                db_index=True,
                verbose_name="محدوده ارائه سرویس",
            ),
        ),
        (
            "fee_mode",
            models.CharField(
                max_length=24,
                choices=SHIPPING_FEE_MODE_CHOICES,
                default="calculated",
                verbose_name="روش محاسبه هزینه ارسال",
            ),
        ),
        (
            "requires_address",
            models.BooleanField(default=True, verbose_name="نیازمند نشانی کامل"),
        ),
        (
            "requires_postal_code",
            models.BooleanField(default=False, verbose_name="نیازمند کد پستی"),
        ),
        (
            "customer_notice",
            models.CharField(max_length=300, blank=True, default="", verbose_name="توضیح روش ارسال برای مشتری"),
        ),
    ):
        _contribute(ShippingMethod, name, field)


def _active_promotion(product, price: int) -> int:
    try:
        promotion = next(
            (
                item
                for item in product.promotions.filter(is_active=True).order_by("-created_at")
                if item.is_current
            ),
            None,
        )
    except Exception:
        promotion = None
    return int(promotion.apply(price)) if promotion else int(price)


def resolve_variant_fixed_price(variant: ProductVariant) -> int:
    product = variant.product
    policy = str(getattr(product, "pricing_policy", "formula") or "formula")
    if policy == "product_fixed":
        return max(0, int(getattr(product, "fixed_price", 0) or 0))
    if policy in {
        "profile_fixed",
        "profile_material_fixed",
        "profile_material_color_fixed",
    }:
        override = max(0, int(getattr(variant, "fixed_price_override", 0) or 0))
        return override or max(0, int(getattr(product, "fixed_price", 0) or 0))
    return 0


def _install_pricing_contract() -> None:
    original = ProductVariant.price_breakdown
    if getattr(original, "_phase50_commerce_policy", False):
        return

    @wraps(original)
    def price_breakdown(self: ProductVariant) -> dict[str, Any]:
        result = dict(original(self))
        policy = str(getattr(self.product, "pricing_policy", "formula") or "formula")
        if policy == "formula":
            result["pricing_policy"] = policy
            return result

        fixed = resolve_variant_fixed_price(self)
        if fixed <= 0:
            result["pricing_policy"] = policy
            result["pricing_policy_fallback"] = "formula"
            return result

        discounted = _active_promotion(self.product, fixed)
        estimated_cost = int(result.get("estimated_cost") or 0)
        result.update(
            {
                "pricing_policy": policy,
                "fixed_policy_price": fixed,
                "unit_price_before_discount": fixed,
                "unit_price": discounted,
                "gross_profit": int(discounted) - estimated_cost,
            }
        )
        return result

    price_breakdown._phase50_commerce_policy = True
    price_breakdown._phase50_commerce_policy_original = original
    ProductVariant.price_breakdown = price_breakdown


def _install_shipping_fee_contract() -> None:
    original = ShippingMethod.calculate_fee
    if getattr(original, "_phase50_commerce_policy", False):
        return

    @wraps(original)
    def calculate_fee(self: ShippingMethod, order_amount, total_weight_grams):
        fee_mode = str(getattr(self, "fee_mode", "calculated") or "calculated")
        if fee_mode in {"free", "postpaid"}:
            return 0
        return original(self, order_amount, total_weight_grams)

    calculate_fee._phase50_commerce_policy = True
    calculate_fee._phase50_commerce_policy_original = original
    ShippingMethod.calculate_fee = calculate_fee


def _location_name(value, *, model_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if "اصفهان" in text:
        return text
    if not text.isdigit():
        return text
    try:
        from website.models import IranCity, IranCounty, IranProvince

        model = {
            "province": IranProvince,
            "county": IranCounty,
            "city": IranCity,
        }.get(model_name)
        if model is None:
            return text
        obj = model.objects.filter(pk=int(text)).only("name").first()
        return str(getattr(obj, "name", "") or text)
    except Exception:
        return text


def shipping_method_available(method: ShippingMethod, *, province="", county="", city="") -> bool:
    if str(getattr(method, "delivery_scope", "nationwide") or "nationwide") != "isfahan_only":
        return True
    location = " ".join(
        [
            _location_name(province, model_name="province"),
            _location_name(county, model_name="county"),
            _location_name(city, model_name="city"),
        ]
    )
    return "اصفهان" in location


def _install_checkout_form_contract() -> None:
    from .forms import CheckoutOperationsForm

    original = CheckoutOperationsForm.clean
    if getattr(original, "_phase50_commerce_policy", False):
        return

    @wraps(original)
    def clean(self):
        cleaned = original(self)
        shipping = cleaned.get("shipping_method")
        if shipping is None:
            return cleaned

        saved_address = cleaned.get("saved_address")
        if saved_address is not None:
            province = getattr(saved_address, "province", "")
            county = getattr(saved_address, "county", "")
            city = getattr(saved_address, "city", "")
            address = getattr(saved_address, "address", "")
            postal_code = getattr(saved_address, "postal_code", "")
        else:
            province = cleaned.get("province")
            county = cleaned.get("county")
            city = cleaned.get("city")
            address = cleaned.get("address")
            postal_code = cleaned.get("postal_code")

        if not shipping_method_available(
            shipping,
            province=province,
            county=county,
            city=city,
        ):
            self.add_error("shipping_method", "این روش ارسال فقط برای مقصد اصفهان قابل انتخاب است.")
        if getattr(shipping, "requires_address", True) and not str(address or "").strip():
            self.add_error("address", "برای این روش ارسال، نشانی کامل الزامی است.")
        if getattr(shipping, "requires_postal_code", False) and not str(postal_code or "").strip():
            self.add_error("postal_code", "برای این روش ارسال، کد پستی الزامی است.")
        return cleaned

    clean._phase50_commerce_policy = True
    clean._phase50_commerce_policy_original = original
    CheckoutOperationsForm.clean = clean


def install_runtime() -> None:
    _install_pricing_contract()
    _install_shipping_fee_contract()
    _install_checkout_form_contract()
