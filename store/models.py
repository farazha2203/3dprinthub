from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


MONEY_QUANT = Decimal("1")
PERCENT_DIVISOR = Decimal("100")
GRAMS_PER_KG = Decimal("1000")
MINUTES_PER_HOUR = Decimal("60")


class Category(models.Model):
    SECTION_CHOICES = [
        ("automotive", "قطعات خودرو"),
        ("motorcycle", "قطعات موتورسیکلت"),
        ("home_appliance", "قطعات لوازم خانگی"),
        ("industrial", "قطعات صنعتی"),
        ("academic", "ماکت و پروژه دانشگاهی"),
        ("creative", "محصولات خلاقانه و شخصی‌سازی"),
        ("general", "سایر محصولات"),
    ]

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
        verbose_name="دسته والد",
    )
    section = models.CharField(
        max_length=30,
        choices=SECTION_CHOICES,
        default="general",
        db_index=True,
        verbose_name="بخش اصلی",
    )
    name = models.CharField(max_length=150, verbose_name="نام دسته")
    slug = models.SlugField(max_length=180, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    image = models.ImageField(upload_to="store/categories/", blank=True, null=True, verbose_name="تصویر")
    meta_title = models.CharField(max_length=180, blank=True, verbose_name="عنوان سئو")
    meta_description = models.CharField(max_length=320, blank=True, verbose_name="توضیحات سئو")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "دسته محصول"
        verbose_name_plural = "دسته‌های محصولات"

    def __str__(self):
        if self.parent_id:
            return f"{self.parent} ← {self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse("store:category", kwargs={"slug": self.slug})


class PrintQuality(models.Model):
    code = models.SlugField(max_length=50, unique=True, verbose_name="کد")
    name = models.CharField(max_length=100, verbose_name="نام کیفیت")
    layer_height_mm = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="ارتفاع لایه میلی‌متر",
    )
    description = models.CharField(max_length=300, blank=True, verbose_name="توضیحات")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "کیفیت چاپ"
        verbose_name_plural = "کیفیت‌های چاپ"

    def __str__(self):
        return self.name


class PricingSetting(models.Model):
    default_hourly_rate = models.PositiveIntegerField(
        default=100_000,
        verbose_name="نرخ پیش‌فرض هر ساعت چاپ به تومان",
    )
    default_labor_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("30"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="درصد پیش‌فرض دستمزد",
    )
    minimum_order_amount = models.PositiveIntegerField(default=0, verbose_name="حداقل مبلغ سفارش")
    packaging_fee = models.PositiveIntegerField(default=0, verbose_name="هزینه بسته‌بندی")
    tax_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="درصد مالیات",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات قیمت‌گذاری فروشگاه"
        verbose_name_plural = "تنظیمات قیمت‌گذاری فروشگاه"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "تنظیمات اصلی قیمت‌گذاری"


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="دسته‌بندی",
    )
    title = models.CharField(max_length=220, verbose_name="نام محصول")
    slug = models.SlugField(max_length=240, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    sku = models.CharField(max_length=80, unique=True, verbose_name="کد محصول")
    short_description = models.CharField(max_length=350, verbose_name="توضیح کوتاه")
    description = models.TextField(verbose_name="توضیحات کامل")
    main_image = models.ImageField(upload_to="store/products/", verbose_name="تصویر اصلی")
    model_file = models.FileField(
        upload_to="store/private-models/",
        blank=True,
        null=True,
        verbose_name="فایل سه‌بعدی داخلی",
        help_text="این فایل نباید به‌صورت عمومی لینک شود.",
    )
    dimensions = models.CharField(max_length=120, blank=True, verbose_name="ابعاد")
    technical_notes = models.TextField(blank=True, verbose_name="مشخصات و نکات فنی")
    installation_guide = models.TextField(blank=True, verbose_name="راهنمای نصب")
    is_featured = models.BooleanField(default=False, db_index=True, verbose_name="محصول ویژه")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    published_at = models.DateTimeField(default=timezone.now, db_index=True, verbose_name="تاریخ انتشار")
    view_count = models.PositiveBigIntegerField(default=0, db_index=True, verbose_name="تعداد بازدید")
    meta_title = models.CharField(max_length=180, blank=True, verbose_name="عنوان سئو")
    meta_description = models.CharField(max_length=320, blank=True, verbose_name="توضیحات سئو")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-id"]
        indexes = [
            models.Index(fields=["is_active", "-published_at"]),
            models.Index(fields=["category", "is_active"]),
        ]
        verbose_name = "محصول آماده چاپ"
        verbose_name_plural = "محصولات آماده چاپ"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("store:product_detail", kwargs={"slug": self.slug})

    @property
    def seo_title(self):
        return self.meta_title or f"{self.title} | سفارش چاپ سه‌بعدی"

    @property
    def seo_description(self):
        return self.meta_description or self.short_description


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name="محصول")
    image = models.ImageField(upload_to="store/products/gallery/", verbose_name="تصویر")
    alt_text = models.CharField(max_length=220, blank=True, verbose_name="متن جایگزین تصویر")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"

    def __str__(self):
        return self.alt_text or f"تصویر {self.product}"


class ProductCompatibility(models.Model):
    DOMAIN_CHOICES = [
        ("vehicle", "خودرو"),
        ("motorcycle", "موتورسیکلت"),
        ("appliance", "لوازم خانگی"),
        ("industrial", "تجهیزات صنعتی"),
        ("other", "سایر"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="compatibilities",
        verbose_name="محصول",
    )
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES, verbose_name="نوع سازگاری")
    brand = models.CharField(max_length=120, blank=True, verbose_name="برند")
    model = models.CharField(max_length=150, blank=True, verbose_name="مدل")
    variant = models.CharField(max_length=150, blank=True, verbose_name="تیپ یا نسخه")
    year_from = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="از سال")
    year_to = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="تا سال")
    notes = models.CharField(max_length=300, blank=True, verbose_name="توضیحات سازگاری")

    class Meta:
        verbose_name = "سازگاری محصول"
        verbose_name_plural = "سازگاری‌های محصول"

    def __str__(self):
        parts = [self.get_domain_display(), self.brand, self.model, self.variant]
        return " - ".join(part for part in parts if part)


class ProductVariant(models.Model):
    STOCK_CHOICES = [
        ("made_to_order", "تولید پس از سفارش"),
        ("in_stock", "آماده ارسال"),
        ("preorder", "پیش‌سفارش"),
        ("out_of_stock", "ناموجود"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants", verbose_name="محصول")
    material = models.ForeignKey(
        "website.Material",
        on_delete=models.PROTECT,
        related_name="store_variants",
        verbose_name="متریال",
    )
    quality = models.ForeignKey(
        PrintQuality,
        on_delete=models.PROTECT,
        related_name="variants",
        verbose_name="کیفیت چاپ",
    )
    code = models.CharField(max_length=100, unique=True, verbose_name="کد تنوع")
    material_weight_grams = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="وزن مصرفی متریال به گرم",
    )
    final_weight_grams = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="وزن نهایی محصول به گرم",
    )
    shipping_weight_grams = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="وزن قابل محاسبه برای ارسال به گرم",
    )
    print_time_minutes = models.PositiveIntegerField(verbose_name="زمان چاپ به دقیقه")
    hourly_rate_override = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="نرخ ساعتی اختصاصی",
    )
    labor_percent_override = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="درصد دستمزد اختصاصی",
    )
    post_processing_fee = models.PositiveIntegerField(default=0, verbose_name="هزینه پرداخت‌کاری")
    fixed_fee = models.PositiveIntegerField(default=0, verbose_name="هزینه ثابت اختصاصی")
    cached_unit_price = models.PositiveIntegerField(default=0, db_index=True, verbose_name="قیمت واحد محاسبه‌شده")
    minimum_quantity = models.PositiveIntegerField(default=1, verbose_name="حداقل تعداد")
    maximum_quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name="حداکثر تعداد")
    stock_status = models.CharField(
        max_length=20,
        choices=STOCK_CHOICES,
        default="made_to_order",
        db_index=True,
        verbose_name="وضعیت موجودی",
    )
    lead_time_min_days = models.PositiveSmallIntegerField(default=1, verbose_name="حداقل زمان آماده‌سازی")
    lead_time_max_days = models.PositiveSmallIntegerField(default=3, verbose_name="حداکثر زمان آماده‌سازی")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "material", "quality"],
                name="unique_store_product_material_quality",
            )
        ]
        ordering = ["product", "quality__sort_order", "material__sort_order"]
        verbose_name = "تنوع قابل سفارش محصول"
        verbose_name_plural = "تنوع‌های قابل سفارش محصولات"

    def __str__(self):
        return f"{self.product} | {self.material} | {self.quality}"

    @staticmethod
    def _round_money(value: Decimal) -> int:
        return int(value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP))

    def price_breakdown(self) -> dict[str, int | str]:
        pricing = PricingSetting.load()
        hourly_rate = self.hourly_rate_override or pricing.default_hourly_rate
        labor_percent = (
            self.labor_percent_override
            if self.labor_percent_override is not None
            else pricing.default_labor_percent
        )

        material_cost_decimal = (
            Decimal(self.material.price_per_kg)
            / GRAMS_PER_KG
            * Decimal(self.material_weight_grams)
        )
        machine_cost_decimal = (
            Decimal(hourly_rate)
            * Decimal(self.print_time_minutes)
            / MINUTES_PER_HOUR
        )
        labor_base = material_cost_decimal + machine_cost_decimal
        labor_cost_decimal = labor_base * Decimal(labor_percent) / PERCENT_DIVISOR

        material_cost = self._round_money(material_cost_decimal)
        machine_cost = self._round_money(machine_cost_decimal)
        labor_cost = self._round_money(labor_cost_decimal)
        subtotal = material_cost + machine_cost + labor_cost + self.post_processing_fee + self.fixed_fee
        unit_price = max(subtotal, pricing.minimum_order_amount)

        return {
            "material_cost": material_cost,
            "machine_cost": machine_cost,
            "labor_cost": labor_cost,
            "post_processing_fee": self.post_processing_fee,
            "fixed_fee": self.fixed_fee,
            "unit_price": unit_price,
            "hourly_rate": hourly_rate,
            "labor_percent": str(labor_percent),
        }

    def recalculate_price(self, *, save=True) -> int:
        price = int(self.price_breakdown()["unit_price"])
        self.cached_unit_price = price
        if save:
            type(self).objects.filter(pk=self.pk).update(cached_unit_price=price)
        return price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.recalculate_price(save=True)


class ProductLike(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="likes", verbose_name="محصول")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="store_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["product", "user"], name="unique_store_product_like")
        ]
        verbose_name = "پسند محصول"
        verbose_name_plural = "پسندهای محصولات"


class ProductComment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments", verbose_name="محصول")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="store_comments")
    body = models.TextField(verbose_name="متن دیدگاه")
    is_approved = models.BooleanField(default=False, db_index=True, verbose_name="تأیید شده")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "دیدگاه محصول"
        verbose_name_plural = "دیدگاه‌های محصولات"

    def __str__(self):
        return f"دیدگاه {self.user} برای {self.product}"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="محصول")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="store_reviews")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="امتیاز",
    )
    title = models.CharField(max_length=150, blank=True, verbose_name="عنوان نظر")
    body = models.TextField(verbose_name="متن نظر")
    is_verified_purchase = models.BooleanField(default=False, db_index=True, verbose_name="خرید تأییدشده")
    is_approved = models.BooleanField(default=False, db_index=True, verbose_name="تأیید شده")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["product", "user"], name="unique_store_product_review")
        ]
        ordering = ["-created_at"]
        verbose_name = "نظر و امتیاز محصول"
        verbose_name_plural = "نظرات و امتیازهای محصولات"


class ServicePage(models.Model):
    SERVICE_CHOICES = [
        ("printing", "پرینت سه‌بعدی"),
        ("reverse_engineering", "مهندسی معکوس"),
        ("automotive", "قطعات خودرو و موتورسیکلت"),
        ("home_appliance", "قطعات لوازم خانگی"),
        ("model_making", "ماکت‌سازی و پروژه دانشگاهی"),
        ("kids_drawing", "تبدیل نقاشی کودک به فیگور"),
        ("custom_figure", "فیگور و هدیه شخصی‌سازی‌شده"),
        ("industrial", "قطعات صنعتی"),
    ]

    service_type = models.CharField(max_length=40, choices=SERVICE_CHOICES, db_index=True, verbose_name="نوع خدمت")
    title = models.CharField(max_length=220, verbose_name="عنوان صفحه")
    slug = models.SlugField(max_length=240, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    short_description = models.CharField(max_length=350, verbose_name="توضیح کوتاه")
    content = models.TextField(verbose_name="محتوای کامل")
    hero_image = models.ImageField(upload_to="store/services/", blank=True, null=True, verbose_name="تصویر اصلی")
    meta_title = models.CharField(max_length=180, blank=True, verbose_name="عنوان سئو")
    meta_description = models.CharField(max_length=320, blank=True, verbose_name="توضیحات سئو")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "title"]
        verbose_name = "صفحه خدمات سئویی"
        verbose_name_plural = "صفحات خدمات سئویی"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("store:service_page", kwargs={"slug": self.slug})


class ProductRequest(models.Model):
    REQUEST_CHOICES = [
        ("automotive", "قطعه خودرو"),
        ("motorcycle", "قطعه موتورسیکلت"),
        ("home_appliance", "قطعه لوازم خانگی"),
        ("industrial", "قطعه صنعتی"),
        ("academic", "ماکت یا پروژه دانشگاهی"),
        ("kids_drawing", "نقاشی کودک به فیگور"),
        ("custom_figure", "فیگور سفارشی"),
        ("other", "سایر"),
    ]
    STATUS_CHOICES = [
        ("new", "جدید"),
        ("reviewing", "در حال بررسی"),
        ("waiting_sample", "در انتظار نمونه"),
        ("modeling", "در حال طراحی"),
        ("testing", "در حال تست"),
        ("published", "تبدیل‌شده به محصول"),
        ("rejected", "رد شده"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="store_product_requests",
        verbose_name="کاربر",
    )
    request_type = models.CharField(max_length=30, choices=REQUEST_CHOICES, db_index=True, verbose_name="نوع درخواست")
    full_name = models.CharField(max_length=150, verbose_name="نام و نام خانوادگی")
    phone = models.CharField(max_length=20, db_index=True, verbose_name="شماره تماس")
    title = models.CharField(max_length=220, verbose_name="عنوان درخواست")
    brand = models.CharField(max_length=120, blank=True, verbose_name="برند")
    model = models.CharField(max_length=150, blank=True, verbose_name="مدل")
    year = models.CharField(max_length=30, blank=True, verbose_name="سال یا نسخه")
    description = models.TextField(verbose_name="توضیحات کامل")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="new", db_index=True, verbose_name="وضعیت")
    matched_product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_requests",
        verbose_name="محصول مرتبط",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "درخواست قطعه یا پروژه"
        verbose_name_plural = "درخواست‌های قطعه و پروژه"

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.title}"


class ProductRequestImage(models.Model):
    request = models.ForeignKey(
        ProductRequest,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="درخواست",
    )
    image = models.ImageField(upload_to="store/requests/", verbose_name="تصویر")

    class Meta:
        verbose_name = "تصویر درخواست"
        verbose_name_plural = "تصاویر درخواست"
