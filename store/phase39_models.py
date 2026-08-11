from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.utils import timezone


class MaterialColorOption(models.Model):
    material = models.ForeignKey(
        "website.Material", on_delete=models.CASCADE, related_name="store_color_options", verbose_name="متریال"
    )
    name = models.CharField(max_length=100, verbose_name="نام رنگ")
    code = models.SlugField(max_length=120, verbose_name="کد رنگ")
    hex_code = models.CharField(max_length=20, blank=True, verbose_name="کد HEX")
    sale_price_per_gram_override = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="قیمت فروش اختصاصی هر گرم"
    )
    low_stock_threshold_grams = models.DecimalField(
        max_digits=12, decimal_places=2, default=100, verbose_name="هشدار موجودی رنگ به گرم"
    )
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        ordering = ["material", "sort_order", "name"]
        constraints = [models.UniqueConstraint(fields=["material", "code"], name="uniq_material_color_code")]
        verbose_name = "رنگ قابل فروش متریال"
        verbose_name_plural = "رنگ‌های قابل فروش متریال"

    def __str__(self):
        return f"{self.material} - {self.name}"

    @property
    def current_stock_grams(self):
        qs = self.material.filament_spools.exclude(status__in=["empty", "archived", "quarantine"])
        qs = qs.filter(color_name__iexact=self.name)
        return qs.aggregate(value=models.Sum("remaining_weight_grams"))["value"] or Decimal("0")

    @property
    def current_roll_count(self):
        return self.material.filament_spools.exclude(status__in=["empty", "archived", "quarantine"]).filter(
            color_name__iexact=self.name, remaining_weight_grams__gt=0
        ).count()

    @property
    def effective_sale_price_per_gram(self):
        return self.sale_price_per_gram_override or self.material.effective_sale_price_per_gram


class ProductMaterialRecommendation(models.Model):
    RECOMMENDATION_CHOICES = [
        ("best", "پیشنهاد اصلی"),
        ("recommended", "پیشنهادی"),
        ("allowed", "قابل استفاده"),
        ("not_recommended", "توصیه نمی‌شود"),
    ]
    product = models.ForeignKey("store.Product", on_delete=models.CASCADE, related_name="material_options", verbose_name="محصول")
    material = models.ForeignKey("website.Material", on_delete=models.PROTECT, related_name="recommended_products", verbose_name="متریال")
    recommendation = models.CharField(max_length=30, choices=RECOMMENDATION_CHOICES, default="recommended", db_index=True, verbose_name="سطح پیشنهاد")
    suitability_score = models.PositiveSmallIntegerField(default=70, verbose_name="امتیاز تناسب از ۱۰۰")
    reason = models.TextField(blank=True, verbose_name="دلیل و تفاوت متریال")
    customer_note = models.TextField(blank=True, verbose_name="توضیح برای مشتری")
    is_customer_selectable = models.BooleanField(default=True, db_index=True, verbose_name="قابل انتخاب توسط مشتری")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        ordering = ["sort_order", "-suitability_score", "material__sort_order"]
        constraints = [models.UniqueConstraint(fields=["product", "material"], name="uniq_product_material_recommendation")]
        verbose_name = "پیشنهاد متریال محصول"
        verbose_name_plural = "پیشنهادهای متریال محصول"

    def __str__(self):
        return f"{self.product} - {self.material}"


class AccessoryComponent(models.Model):
    name = models.CharField(max_length=160, verbose_name="نام قطعه جانبی")
    sku = models.CharField(max_length=80, unique=True, verbose_name="کد داخلی")
    unit_cost = models.PositiveBigIntegerField(default=0, verbose_name="قیمت خرید واحد")
    default_sale_price = models.PositiveBigIntegerField(default=0, verbose_name="قیمت فروش واحد")
    weight_grams = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="وزن واحد")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="موجودی")
    low_stock_threshold = models.PositiveIntegerField(default=2, verbose_name="هشدار موجودی")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")

    class Meta:
        ordering = ["name"]
        verbose_name = "قطعه جانبی / BOM"
        verbose_name_plural = "قطعات جانبی / BOM"

    def __str__(self):
        return self.name


class ProductBOMItem(models.Model):
    product = models.ForeignKey("store.Product", on_delete=models.CASCADE, related_name="bom_items", verbose_name="محصول")
    component = models.ForeignKey(AccessoryComponent, on_delete=models.PROTECT, related_name="product_usages", verbose_name="قطعه جانبی")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name="تعداد")
    sale_price_override = models.PositiveBigIntegerField(null=True, blank=True, verbose_name="قیمت فروش اختصاصی")
    assembly_minutes = models.PositiveIntegerField(default=0, verbose_name="زمان مونتاژ به دقیقه")
    is_required = models.BooleanField(default=True, verbose_name="اجباری")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [models.UniqueConstraint(fields=["product", "component"], name="uniq_product_bom_component")]
        verbose_name = "ردیف BOM محصول"
        verbose_name_plural = "BOM و لوازم جانبی محصولات"

    def __str__(self):
        return f"{self.product} - {self.component}"

    @property
    def sale_total(self):
        unit = self.sale_price_override if self.sale_price_override is not None else self.component.default_sale_price
        return int((Decimal(unit) * Decimal(self.quantity)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    @property
    def cost_total(self):
        return int((Decimal(self.component.unit_cost) * Decimal(self.quantity)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class ProductPromotion(models.Model):
    KIND_CHOICES = [
        ("featured", "محصول ویژه"),
        ("sale", "فروش ویژه"),
        ("limited", "تعداد محدود"),
        ("new", "محصول جدید"),
        ("bestseller", "پرفروش"),
    ]
    product = models.ForeignKey("store.Product", on_delete=models.CASCADE, related_name="promotions", verbose_name="محصول")
    kind = models.CharField(max_length=30, choices=KIND_CHOICES, db_index=True, verbose_name="نوع")
    title = models.CharField(max_length=120, blank=True, verbose_name="عنوان نمایشی")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="درصد تخفیف")
    discount_amount = models.PositiveBigIntegerField(default=0, verbose_name="تخفیف ثابت تومان")
    stock_limit = models.PositiveIntegerField(default=0, verbose_name="تعداد محدود / صفر یعنی نامحدود")
    starts_at = models.DateTimeField(null=True, blank=True, verbose_name="شروع")
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name="پایان")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_active", "-created_at"]
        verbose_name = "کمپین محصول"
        verbose_name_plural = "فروش ویژه و کمپین محصولات"

    @property
    def remaining_quantity(self):
        if not self.stock_limit:
            return None
        sold = self.product.store_order_items.filter(order__payment_status="paid").aggregate(v=models.Sum("quantity"))["v"] or 0
        return max(0, int(self.stock_limit) - int(sold))

    @property
    def is_current(self):
        now = timezone.now()
        time_ok = self.is_active and (not self.starts_at or self.starts_at <= now) and (not self.ends_at or self.ends_at >= now)
        stock_ok = self.remaining_quantity is None or self.remaining_quantity > 0
        return bool(time_ok and stock_ok)

    def apply(self, price: int) -> int:
        if not self.is_current:
            return int(price)
        value = Decimal(price)
        if self.discount_percent:
            value -= value * Decimal(self.discount_percent) / Decimal("100")
        if self.discount_amount:
            value -= Decimal(self.discount_amount)
        return max(0, int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)))


class ProductReviewImage(models.Model):
    review = models.ForeignKey("store.ProductReview", on_delete=models.CASCADE, related_name="images", verbose_name="نظر")
    image = models.ImageField(upload_to="store/reviews/%Y/%m/", verbose_name="تصویر مشتری")
    alt_text = models.CharField(max_length=220, blank=True, verbose_name="Alt تصویر")
    is_approved = models.BooleanField(default=False, db_index=True, verbose_name="تأیید شده")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "تصویر نظر مشتری"
        verbose_name_plural = "تصاویر نظرات مشتریان"


class ShippingRateRule(models.Model):
    shipping_method = models.ForeignKey("store.ShippingMethod", on_delete=models.CASCADE, related_name="rate_rules", verbose_name="روش ارسال")
    title = models.CharField(max_length=120, verbose_name="عنوان قانون")
    min_weight_grams = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="حداقل وزن")
    max_weight_grams = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="حداکثر وزن / صفر یعنی نامحدود")
    base_fee = models.PositiveBigIntegerField(default=0, verbose_name="هزینه پایه")
    per_kg_fee = models.PositiveBigIntegerField(default=0, verbose_name="هزینه هر کیلو")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        ordering = ["sort_order", "min_weight_grams"]
        verbose_name = "قانون وزنی ارسال"
        verbose_name_plural = "قوانین وزنی ارسال"

    def calculate(self, weight_grams):
        weight = Decimal(weight_grams or 0)
        kilograms = (weight / Decimal("1000")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return int(Decimal(self.base_fee) + Decimal(self.per_kg_fee) * kilograms)
