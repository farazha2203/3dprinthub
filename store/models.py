from __future__ import annotations

from datetime import timedelta
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
    # BEGIN PHASE 4 SEO FIELDS
    seo_focus_keyword = models.CharField(max_length=180, blank=True, verbose_name="عبارت کلیدی اصلی")
    canonical_url = models.URLField(blank=True, verbose_name="Canonical اختصاصی")
    robots_index = models.BooleanField(default=True, db_index=True, verbose_name="اجازه ایندکس")
    robots_follow = models.BooleanField(default=True, verbose_name="اجازه دنبال‌کردن لینک‌ها")
    og_title = models.CharField(max_length=180, blank=True, verbose_name="عنوان Open Graph")
    og_description = models.CharField(max_length=320, blank=True, verbose_name="توضیح Open Graph")
    og_image = models.ImageField(upload_to="store/seo/", blank=True, null=True, verbose_name="تصویر Open Graph")
    # END PHASE 4 SEO FIELDS
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
    minimum_billable_minutes = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1)],
        verbose_name="حداقل زمان قابل محاسبه به دقیقه",
        help_text="برای قطعات زیر یک ساعت مقدار ۶۰ قرار دهید تا حداقل یک ساعت محاسبه شود.",
    )
    billing_increment_minutes = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1)],
        verbose_name="پله گردکردن زمان چاپ به دقیقه",
        help_text="با مقدار ۶۰، زمان ۶۱ تا ۱۲۰ دقیقه دو ساعت محاسبه می‌شود.",
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
    brand_name = models.CharField(max_length=120, default="3DprintHub", verbose_name="برند محصول")
    mpn = models.CharField(max_length=100, blank=True, verbose_name="کد MPN")
    gtin = models.CharField(max_length=14, blank=True, verbose_name="GTIN / بارکد")
    schema_enabled = models.BooleanField(default=True, verbose_name="ساخت اسکیما محصول")
    # BEGIN PHASE 4 SEO FIELDS
    seo_focus_keyword = models.CharField(max_length=180, blank=True, verbose_name="عبارت کلیدی اصلی")
    canonical_url = models.URLField(blank=True, verbose_name="Canonical اختصاصی")
    robots_index = models.BooleanField(default=True, db_index=True, verbose_name="اجازه ایندکس")
    robots_follow = models.BooleanField(default=True, verbose_name="اجازه دنبال‌کردن لینک‌ها")
    og_title = models.CharField(max_length=180, blank=True, verbose_name="عنوان Open Graph")
    og_description = models.CharField(max_length=320, blank=True, verbose_name="توضیح Open Graph")
    og_image = models.ImageField(upload_to="store/seo/", blank=True, null=True, verbose_name="تصویر Open Graph")
    # END PHASE 4 SEO FIELDS
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
    track_inventory = models.BooleanField(default=False, verbose_name="کنترل موجودی عددی")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="موجودی فیزیکی")
    reserved_quantity = models.PositiveIntegerField(default=0, editable=False, verbose_name="موجودی رزروشده")
    low_stock_threshold = models.PositiveIntegerField(default=2, verbose_name="آستانه هشدار موجودی")
    allow_backorder = models.BooleanField(default=False, verbose_name="اجازه سفارش بیشتر از موجودی")
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

        material_sale_per_gram = Decimal(
            getattr(self.material, "sale_price_per_gram", 0)
            or getattr(self.material, "price_per_gram", 0)
            or 0
        )
        material_cost_decimal = material_sale_per_gram * Decimal(self.material_weight_grams)
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
    # BEGIN PHASE 4 SEO FIELDS
    seo_focus_keyword = models.CharField(max_length=180, blank=True, verbose_name="عبارت کلیدی اصلی")
    canonical_url = models.URLField(blank=True, verbose_name="Canonical اختصاصی")
    robots_index = models.BooleanField(default=True, db_index=True, verbose_name="اجازه ایندکس")
    robots_follow = models.BooleanField(default=True, verbose_name="اجازه دنبال‌کردن لینک‌ها")
    og_title = models.CharField(max_length=180, blank=True, verbose_name="عنوان Open Graph")
    og_description = models.CharField(max_length=320, blank=True, verbose_name="توضیح Open Graph")
    og_image = models.ImageField(upload_to="store/seo/", blank=True, null=True, verbose_name="تصویر Open Graph")
    # END PHASE 4 SEO FIELDS
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

# BEGIN STORE COMMERCE PHASE 2
import uuid


def generate_store_order_number():
    return f"SPH-{timezone.now():%y%m%d}-{uuid.uuid4().hex[:8].upper()}"


class ShippingMethod(models.Model):
    code = models.SlugField(max_length=50, unique=True, verbose_name="کد روش ارسال")
    title = models.CharField(max_length=120, verbose_name="عنوان روش ارسال")
    description = models.CharField(max_length=300, blank=True, verbose_name="توضیحات")
    flat_fee = models.PositiveIntegerField(default=0, verbose_name="هزینه ثابت ارسال به تومان")
    free_over = models.PositiveIntegerField(default=0, verbose_name="ارسال رایگان از مبلغ")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")

    class Meta:
        ordering = ["sort_order", "title"]
        verbose_name = "روش ارسال فروشگاه"
        verbose_name_plural = "روش‌های ارسال فروشگاه"

    def __str__(self):
        return self.title

    def calculate_fee(self, subtotal, total_weight_grams=0):
        if self.free_over and int(subtotal) >= self.free_over:
            return 0
        return self.flat_fee


class StoreAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="store_addresses",
        verbose_name="کاربر",
    )
    title = models.CharField(max_length=80, default="آدرس اصلی", verbose_name="عنوان آدرس")
    full_name = models.CharField(max_length=150, verbose_name="نام تحویل‌گیرنده")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    province = models.CharField(max_length=100, verbose_name="استان")
    county = models.CharField(max_length=120, blank=True, verbose_name="شهرستان")
    city = models.CharField(max_length=100, verbose_name="شهر")
    address = models.TextField(verbose_name="نشانی کامل")
    postal_code = models.CharField(max_length=20, verbose_name="کد پستی")
    # BEGIN CUSTOMER PORTAL PHASE 3 ADDRESS FIELDS
    district = models.CharField(max_length=120, blank=True, verbose_name="منطقه / محله")
    plaque = models.CharField(max_length=20, blank=True, verbose_name="پلاک")
    unit = models.CharField(max_length=20, blank=True, verbose_name="واحد")
    recipient_national_code = models.CharField(max_length=10, blank=True, verbose_name="کد ملی تحویل‌گیرنده")
    delivery_notes = models.CharField(max_length=300, blank=True, verbose_name="توضیحات تحویل")
    # END CUSTOMER PORTAL PHASE 3 ADDRESS FIELDS
    is_default = models.BooleanField(default=False, db_index=True, verbose_name="آدرس پیش‌فرض")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-updated_at"]
        verbose_name = "آدرس فروشگاهی مشتری"
        verbose_name_plural = "آدرس‌های فروشگاهی مشتریان"

    def __str__(self):
        return f"{self.user} - {self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            type(self).objects.filter(user=self.user).exclude(pk=self.pk).update(is_default=False)


class StoreOrder(models.Model):
    STATUS_CHOICES = [
        ("awaiting_payment", "در انتظار پرداخت"),
        ("payment_review", "در انتظار بررسی پرداخت"),
        ("paid", "پرداخت شده"),
        ("processing", "در حال تولید"),
        ("ready", "آماده ارسال"),
        ("shipped", "ارسال شده"),
        ("delivered", "تحویل شده"),
        ("cancelled", "لغو شده"),
        ("refunded", "مسترد شده"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("pending", "در انتظار پرداخت"),
        ("awaiting_review", "در انتظار بررسی رسید"),
        ("paid", "پرداخت موفق"),
        ("failed", "پرداخت ناموفق"),
        ("refunded", "مسترد شده"),
    ]

    order_number = models.CharField(
        max_length=40,
        default=generate_store_order_number,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="شماره سفارش فروشگاه",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="store_orders",
        verbose_name="مشتری",
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="awaiting_payment",
        db_index=True,
        verbose_name="وضعیت سفارش",
    )
    payment_status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
        db_index=True,
        verbose_name="وضعیت پرداخت",
    )
    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="روش ارسال",
    )
    shipping_title = models.CharField(max_length=120, verbose_name="عنوان روش ارسال هنگام سفارش")
    full_name = models.CharField(max_length=150, verbose_name="نام تحویل‌گیرنده")
    phone = models.CharField(max_length=20, db_index=True, verbose_name="شماره تماس")
    email = models.EmailField(blank=True, verbose_name="ایمیل")
    province = models.CharField(max_length=100, verbose_name="استان")
    county = models.CharField(max_length=120, blank=True, verbose_name="شهرستان")
    city = models.CharField(max_length=100, verbose_name="شهر")
    address = models.TextField(verbose_name="نشانی کامل")
    postal_code = models.CharField(max_length=20, verbose_name="کد پستی")
    customer_note = models.TextField(blank=True, verbose_name="توضیحات مشتری")
    admin_note = models.TextField(blank=True, verbose_name="یادداشت داخلی")
    tracking_code = models.CharField(max_length=100, blank=True, verbose_name="کد رهگیری ارسال")
    subtotal = models.PositiveBigIntegerField(default=0, verbose_name="جمع کالاها")
    packaging_fee = models.PositiveBigIntegerField(default=0, verbose_name="هزینه بسته‌بندی")
    shipping_fee = models.PositiveBigIntegerField(default=0, verbose_name="هزینه ارسال")
    tax_amount = models.PositiveBigIntegerField(default=0, verbose_name="مالیات")
    discount_amount = models.PositiveBigIntegerField(default=0, verbose_name="تخفیف")
    coupon = models.ForeignKey("Coupon", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders", verbose_name="کد تخفیف")
    coupon_code = models.CharField(max_length=50, blank=True, verbose_name="کد تخفیف هنگام سفارش")
    inventory_reserved = models.BooleanField(default=False, verbose_name="موجودی رزرو شده")
    reservation_expires_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="پایان اعتبار رزرو")
    affiliate_partner = models.ForeignKey("AffiliatePartner", on_delete=models.SET_NULL, null=True, blank=True, related_name="referred_orders", verbose_name="همکار معرف")
    affiliate_campaign = models.ForeignKey("AffiliateCampaign", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders", verbose_name="کمپین معرف")
    affiliate_code = models.CharField(max_length=40, blank=True, db_index=True, verbose_name="کد معرف هنگام سفارش")
    total_amount = models.PositiveBigIntegerField(default=0, verbose_name="مبلغ نهایی")
    total_weight_grams = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="وزن ارسال")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ پرداخت")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="store_order_user_created_idx"),
            models.Index(fields=["status", "payment_status"], name="store_order_status_pay_idx"),
        ]
        verbose_name = "سفارش فروشگاهی"
        verbose_name_plural = "سفارش‌های فروشگاهی"

    def __str__(self):
        return self.order_number

    def get_absolute_url(self):
        return reverse("store:order_detail", kwargs={"order_number": self.order_number})

    @property
    def can_pay(self):
        return self.payment_status in {"pending", "failed"} and self.status not in {"cancelled", "refunded"}

    def mark_paid(self, *, ref_id=""):
        self.payment_status = "paid"
        if self.status in {"awaiting_payment", "payment_review"}:
            self.status = "paid"
        self.paid_at = timezone.now()
        self.save(update_fields=["payment_status", "status", "paid_at", "updated_at"])


class StoreOrderItem(models.Model):
    order = models.ForeignKey(StoreOrder, on_delete=models.CASCADE, related_name="items", verbose_name="سفارش")
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="store_order_items",
        verbose_name="محصول",
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="store_order_items",
        verbose_name="تنوع",
    )
    product_title = models.CharField(max_length=220, verbose_name="نام محصول هنگام سفارش")
    product_sku = models.CharField(max_length=80, verbose_name="کد محصول هنگام سفارش")
    variant_code = models.CharField(max_length=100, verbose_name="کد تنوع هنگام سفارش")
    material_name = models.CharField(max_length=100, verbose_name="متریال هنگام سفارش")
    quality_name = models.CharField(max_length=100, verbose_name="کیفیت هنگام سفارش")
    unit_price = models.PositiveBigIntegerField(verbose_name="قیمت واحد هنگام سفارش")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    line_total = models.PositiveBigIntegerField(verbose_name="جمع ردیف")
    unit_weight_grams = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="وزن واحد")

    class Meta:
        ordering = ["id"]
        verbose_name = "ردیف سفارش فروشگاهی"
        verbose_name_plural = "ردیف‌های سفارش فروشگاهی"

    def __str__(self):
        return f"{self.product_title} × {self.quantity}"

    def save(self, *args, **kwargs):
        self.line_total = int(self.unit_price) * int(self.quantity)
        super().save(*args, **kwargs)


class StorePayment(models.Model):
    METHOD_CHOICES = [
        ("bank_transfer", "کارت به کارت / واریز بانکی"),
        ("gateway", "درگاه آنلاین"),
    ]
    STATUS_CHOICES = [
        ("pending", "در انتظار پرداخت"),
        ("awaiting_review", "در انتظار بررسی رسید"),
        ("paid", "پرداخت موفق"),
        ("failed", "پرداخت ناموفق"),
        ("cancelled", "لغو شده"),
        ("refunded", "مسترد شده"),
    ]

    order = models.ForeignKey(StoreOrder, on_delete=models.CASCADE, related_name="payments", verbose_name="سفارش")
    amount = models.PositiveBigIntegerField(verbose_name="مبلغ")
    method = models.CharField(max_length=30, choices=METHOD_CHOICES, default="bank_transfer", verbose_name="روش")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending", db_index=True, verbose_name="وضعیت")
    idempotency_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    authority = models.CharField(max_length=255, blank=True, verbose_name="Authority")
    ref_id = models.CharField(max_length=255, blank=True, db_index=True, verbose_name="کد پیگیری")
    card_holder = models.CharField(max_length=150, blank=True, verbose_name="نام صاحب حساب")
    receipt_image = models.ImageField(upload_to="store/payments/receipts/", blank=True, null=True, verbose_name="تصویر رسید")
    note = models.TextField(blank=True, verbose_name="توضیحات پرداخت")
    raw_response = models.JSONField(default=dict, blank=True, verbose_name="پاسخ خام درگاه")
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "پرداخت فروشگاهی"
        verbose_name_plural = "پرداخت‌های فروشگاهی"

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"

    def mark_paid(self, ref_id=""):
        self.status = "paid"
        if ref_id:
            self.ref_id = ref_id
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "ref_id", "paid_at", "updated_at"])
        self.order.mark_paid(ref_id=ref_id)
        from .services import finalize_paid_order
        finalize_paid_order(self.order)
# END STORE COMMERCE PHASE 2

# BEGIN STORE OPERATIONS PHASE 6


def generate_invoice_number():
    return f"INV-{timezone.now():%y%m%d}-{uuid.uuid4().hex[:8].upper()}"


class Coupon(models.Model):
    DISCOUNT_CHOICES = [("percent", "درصدی"), ("fixed", "مبلغ ثابت")]
    code = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="کد تخفیف")
    title = models.CharField(max_length=150, verbose_name="عنوان")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_CHOICES, default="percent", verbose_name="نوع تخفیف")
    value = models.PositiveBigIntegerField(verbose_name="مقدار تخفیف")
    minimum_order_amount = models.PositiveBigIntegerField(default=0, verbose_name="حداقل مبلغ سفارش")
    maximum_discount = models.PositiveBigIntegerField(default=0, verbose_name="سقف تخفیف؛ صفر یعنی بدون سقف")
    usage_limit = models.PositiveIntegerField(default=0, verbose_name="سقف کل استفاده؛ صفر یعنی نامحدود")
    per_user_limit = models.PositiveIntegerField(default=1, verbose_name="سقف استفاده هر مشتری")
    used_count = models.PositiveIntegerField(default=0, editable=False, verbose_name="تعداد استفاده قطعی")
    starts_at = models.DateTimeField(null=True, blank=True, verbose_name="شروع اعتبار")
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name="پایان اعتبار")
    categories = models.ManyToManyField(Category, blank=True, related_name="coupons", verbose_name="دسته‌های مجاز")
    products = models.ManyToManyField(Product, blank=True, related_name="coupons", verbose_name="محصولات مجاز")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف"

    def __str__(self):
        return f"{self.code} - {self.title}"

    @property
    def is_currently_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.starts_at and self.starts_at > now:
            return False
        if self.ends_at and self.ends_at < now:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        return True


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name="usages", verbose_name="کد تخفیف")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="coupon_usages", verbose_name="مشتری")
    order = models.OneToOneField("StoreOrder", on_delete=models.CASCADE, related_name="coupon_usage", verbose_name="سفارش")
    discount_amount = models.PositiveBigIntegerField(default=0, verbose_name="مبلغ تخفیف")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "استفاده از کد تخفیف"
        verbose_name_plural = "استفاده‌های کد تخفیف"


class InventoryMovement(models.Model):
    TYPE_CHOICES = [
        ("stock_in", "ورود موجودی"), ("stock_out", "خروج موجودی"),
        ("reserve", "رزرو سفارش"), ("release", "آزادسازی رزرو"),
        ("sale", "فروش قطعی"), ("return", "بازگشت کالا"),
        ("adjustment", "اصلاح دستی"),
    ]
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="inventory_movements", verbose_name="تنوع محصول")
    order = models.ForeignKey("StoreOrder", on_delete=models.SET_NULL, null=True, blank=True, related_name="inventory_movements", verbose_name="سفارش")
    movement_type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True, verbose_name="نوع گردش")
    quantity = models.IntegerField(verbose_name="تعداد تغییر")
    stock_after = models.PositiveIntegerField(default=0, verbose_name="موجودی پس از تغییر")
    reserved_after = models.PositiveIntegerField(default=0, verbose_name="رزرو پس از تغییر")
    note = models.CharField(max_length=300, blank=True, verbose_name="توضیح")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="inventory_actions", verbose_name="ثبت‌کننده")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "گردش موجودی"
        verbose_name_plural = "گردش‌های موجودی"


class StoreOrderEvent(models.Model):
    order = models.ForeignKey("StoreOrder", on_delete=models.CASCADE, related_name="events", verbose_name="سفارش")
    status = models.CharField(max_length=30, blank=True, verbose_name="وضعیت")
    title = models.CharField(max_length=180, verbose_name="عنوان رویداد")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    is_public = models.BooleanField(default=True, verbose_name="قابل نمایش به مشتری")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="store_order_events", verbose_name="ثبت‌کننده")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "رویداد سفارش"
        verbose_name_plural = "رویدادهای سفارش"


class Shipment(models.Model):
    STATUS_CHOICES = [("preparing", "در حال آماده‌سازی"), ("shipped", "تحویل شرکت حمل"), ("delivered", "تحویل مشتری"), ("returned", "مرجوع‌شده")]
    order = models.OneToOneField("StoreOrder", on_delete=models.CASCADE, related_name="shipment", verbose_name="سفارش")
    carrier = models.CharField(max_length=120, blank=True, verbose_name="شرکت حمل")
    service_name = models.CharField(max_length=120, blank=True, verbose_name="نوع سرویس")
    tracking_code = models.CharField(max_length=120, blank=True, db_index=True, verbose_name="کد رهگیری")
    tracking_url = models.URLField(blank=True, verbose_name="لینک رهگیری")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="preparing", db_index=True, verbose_name="وضعیت ارسال")
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان ارسال")
    estimated_delivery_date = models.DateField(null=True, blank=True, verbose_name="تحویل تخمینی")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان تحویل")
    note = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مرسوله"
        verbose_name_plural = "مرسوله‌ها"


class StoreInvoice(models.Model):
    order = models.OneToOneField("StoreOrder", on_delete=models.PROTECT, related_name="invoice", verbose_name="سفارش")
    invoice_number = models.CharField(max_length=40, default=generate_invoice_number, unique=True, db_index=True, editable=False, verbose_name="شماره فاکتور")
    seller_name = models.CharField(max_length=180, verbose_name="نام فروشنده")
    seller_phone = models.CharField(max_length=30, blank=True, verbose_name="تلفن فروشنده")
    seller_address = models.TextField(blank=True, verbose_name="آدرس فروشنده")
    buyer_name = models.CharField(max_length=180, verbose_name="نام خریدار")
    buyer_phone = models.CharField(max_length=30, verbose_name="تلفن خریدار")
    buyer_address = models.TextField(verbose_name="آدرس خریدار")
    subtotal = models.PositiveBigIntegerField(default=0, verbose_name="جمع کالا")
    discount_amount = models.PositiveBigIntegerField(default=0, verbose_name="تخفیف")
    shipping_fee = models.PositiveBigIntegerField(default=0, verbose_name="هزینه ارسال")
    packaging_fee = models.PositiveBigIntegerField(default=0, verbose_name="هزینه بسته‌بندی")
    tax_amount = models.PositiveBigIntegerField(default=0, verbose_name="مالیات")
    total_amount = models.PositiveBigIntegerField(default=0, verbose_name="مبلغ نهایی")
    issued_at = models.DateTimeField(default=timezone.now, db_index=True, verbose_name="تاریخ صدور")

    class Meta:
        ordering = ["-issued_at"]
        verbose_name = "فاکتور فروش"
        verbose_name_plural = "فاکتورهای فروش"


class CustomerNotification(models.Model):
    TYPE_CHOICES = [("order", "سفارش"), ("payment", "پرداخت"), ("shipping", "ارسال"), ("system", "سیستمی")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="store_notifications", verbose_name="مشتری")
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="system", db_index=True, verbose_name="نوع")
    title = models.CharField(max_length=180, verbose_name="عنوان")
    message = models.TextField(verbose_name="پیام")
    url = models.CharField(max_length=500, blank=True, verbose_name="لینک")
    read_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="زمان مشاهده")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "اعلان مشتری"
        verbose_name_plural = "اعلان‌های مشتریان"

    @property
    def is_read(self):
        return bool(self.read_at)


class ReturnRequest(models.Model):
    REASON_CHOICES = [("defect", "ایراد یا شکستگی"), ("wrong_item", "کالای اشتباه"), ("not_as_described", "مغایرت با توضیحات"), ("other", "سایر")]
    STATUS_CHOICES = [("submitted", "ثبت‌شده"), ("reviewing", "در حال بررسی"), ("approved", "تأیید مرجوعی"), ("rejected", "ردشده"), ("received", "کالا دریافت شد"), ("refunded", "وجه مسترد شد"), ("closed", "بسته‌شده")]
    order = models.ForeignKey("StoreOrder", on_delete=models.PROTECT, related_name="return_requests", verbose_name="سفارش")
    item = models.ForeignKey(StoreOrderItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="return_requests", verbose_name="ردیف سفارش")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="store_return_requests", verbose_name="مشتری")
    reason = models.CharField(max_length=30, choices=REASON_CHOICES, verbose_name="دلیل")
    description = models.TextField(verbose_name="شرح درخواست")
    image = models.ImageField(upload_to="store/returns/", blank=True, null=True, verbose_name="تصویر")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted", db_index=True, verbose_name="وضعیت")
    admin_response = models.TextField(blank=True, verbose_name="پاسخ مدیریت")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "درخواست مرجوعی"
        verbose_name_plural = "درخواست‌های مرجوعی"


class ProductFAQ(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="faqs", verbose_name="محصول")
    question = models.CharField(max_length=300, verbose_name="سؤال")
    answer = models.TextField(verbose_name="پاسخ")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "پرسش متداول محصول"
        verbose_name_plural = "پرسش‌های متداول محصول"


class StoreOperationsDashboard(StoreOrder):
    class Meta:
        proxy = True
        verbose_name = "داشبورد عملیات فروشگاه"
        verbose_name_plural = "داشبورد عملیات فروشگاه"


# Runtime helpers are attached here to keep the phase additive and migration-safe.
def _variant_available_quantity(self):
    if not getattr(self, "track_inventory", False):
        return None
    return max(0, int(self.stock_quantity) - int(self.reserved_quantity))


def _variant_is_low_stock(self):
    available = _variant_available_quantity(self)
    return available is not None and available <= int(self.low_stock_threshold)


ProductVariant.available_quantity = property(_variant_available_quantity)
ProductVariant.is_low_stock = property(_variant_is_low_stock)


def _order_can_request_return(self):
    return self.status == "delivered" and self.payment_status == "paid"


StoreOrder.can_request_return = property(_order_can_request_return)
# END STORE OPERATIONS PHASE 6

# BEGIN AFFILIATE PARTNER PROGRAM PHASE 7


def generate_affiliate_code():
    return f"P{uuid.uuid4().hex[:9].upper()}"


def generate_payout_number():
    return f"PAY-{timezone.now():%y%m%d}-{uuid.uuid4().hex[:7].upper()}"


class AffiliateTier(models.Model):
    COMMISSION_CHOICES = [("percent", "درصدی"), ("fixed", "مبلغ ثابت برای هر سفارش")]
    name = models.CharField(max_length=120, unique=True, verbose_name="نام سطح همکاری")
    slug = models.SlugField(max_length=140, unique=True, allow_unicode=True, verbose_name="شناسه")
    commission_type = models.CharField(max_length=20, choices=COMMISSION_CHOICES, default="percent", verbose_name="نوع پورسانت")
    commission_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("5"), verbose_name="مقدار پورسانت")
    attribution_days = models.PositiveIntegerField(default=30, verbose_name="اعتبار لینک معرفی به روز")
    hold_days = models.PositiveIntegerField(default=7, verbose_name="دوره انتظار تأیید پورسانت پس از تحویل")
    minimum_payout = models.PositiveBigIntegerField(default=500_000, verbose_name="حداقل مبلغ تسویه به تومان")
    include_self_orders = models.BooleanField(default=False, verbose_name="محاسبه پاداش خریدهای شخصی همکار")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "سطح همکاری"
        verbose_name_plural = "سطوح همکاری"

    def __str__(self):
        return self.name


class AffiliatePartner(models.Model):
    TYPE_CHOICES = [
        ("referrer", "معرف مشتری"),
        ("publisher", "سایت یا رسانه تبلیغاتی"),
        ("wholesale", "همکار خرید عمده"),
        ("agency", "آژانس یا بازاریاب"),
        ("other", "سایر"),
    ]
    STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("active", "فعال"),
        ("suspended", "تعلیق‌شده"),
        ("rejected", "ردشده"),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="affiliate_partner", verbose_name="حساب کاربری")
    tier = models.ForeignKey(AffiliateTier, on_delete=models.PROTECT, related_name="partners", verbose_name="سطح همکاری")
    code = models.SlugField(max_length=40, unique=True, default=generate_affiliate_code, db_index=True, verbose_name="کد معرف")
    partner_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="referrer", verbose_name="نوع همکاری")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True, verbose_name="وضعیت")
    display_name = models.CharField(max_length=160, verbose_name="نام نمایشی همکار")
    company_name = models.CharField(max_length=180, blank=True, verbose_name="نام شرکت یا وب‌سایت")
    website = models.URLField(blank=True, verbose_name="نشانی وب‌سایت")
    channel = models.CharField(max_length=180, blank=True, verbose_name="کانال معرفی / شبکه اجتماعی")
    description = models.TextField(blank=True, verbose_name="توضیحات همکاری")
    commission_type_override = models.CharField(max_length=20, choices=AffiliateTier.COMMISSION_CHOICES, blank=True, verbose_name="نوع پورسانت اختصاصی")
    commission_value_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="مقدار پورسانت اختصاصی")
    attribution_days_override = models.PositiveIntegerField(null=True, blank=True, verbose_name="اعتبار اختصاصی لینک به روز")
    hold_days_override = models.PositiveIntegerField(null=True, blank=True, verbose_name="دوره انتظار اختصاصی")
    minimum_payout_override = models.PositiveBigIntegerField(null=True, blank=True, verbose_name="حداقل تسویه اختصاصی")
    include_self_orders_override = models.BooleanField(null=True, blank=True, verbose_name="پاداش خرید شخصی اختصاصی")
    sheba_number = models.CharField(max_length=26, blank=True, verbose_name="شماره شبا")
    card_number = models.CharField(max_length=16, blank=True, verbose_name="شماره کارت")
    account_holder = models.CharField(max_length=160, blank=True, verbose_name="نام صاحب حساب")
    terms_accepted = models.BooleanField(default=False, verbose_name="پذیرش قوانین همکاری")
    admin_note = models.TextField(blank=True, verbose_name="یادداشت مدیریت")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان تأیید")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "همکار فروش و معرف"
        verbose_name_plural = "همکاران فروش و معرف‌ها"

    def __str__(self):
        return f"{self.display_name} ({self.code})"

    def get_absolute_url(self):
        return reverse("store:partner_dashboard")

    @property
    def effective_commission_type(self):
        return self.commission_type_override or self.tier.commission_type

    @property
    def effective_commission_value(self):
        return self.commission_value_override if self.commission_value_override is not None else self.tier.commission_value

    @property
    def effective_attribution_days(self):
        return self.attribution_days_override if self.attribution_days_override is not None else self.tier.attribution_days

    @property
    def effective_hold_days(self):
        return self.hold_days_override if self.hold_days_override is not None else self.tier.hold_days

    @property
    def effective_minimum_payout(self):
        return self.minimum_payout_override if self.minimum_payout_override is not None else self.tier.minimum_payout

    @property
    def effective_include_self_orders(self):
        return self.include_self_orders_override if self.include_self_orders_override is not None else self.tier.include_self_orders

    @property
    def ledger_balance(self):
        from django.db.models import Sum
        return self.ledger_entries.aggregate(value=Sum("amount"))["value"] or 0


class AffiliateCampaign(models.Model):
    partner = models.ForeignKey(AffiliatePartner, on_delete=models.CASCADE, related_name="campaigns", verbose_name="همکار")
    name = models.CharField(max_length=140, verbose_name="عنوان کمپین")
    slug = models.SlugField(max_length=160, allow_unicode=True, verbose_name="شناسه کمپین")
    target_path = models.CharField(max_length=500, default="/", verbose_name="مسیر مقصد داخلی")
    utm_source = models.CharField(max_length=100, blank=True, verbose_name="UTM Source")
    utm_medium = models.CharField(max_length=100, blank=True, verbose_name="UTM Medium")
    utm_campaign = models.CharField(max_length=100, blank=True, verbose_name="UTM Campaign")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["partner", "slug"], name="affiliate_campaign_partner_slug_uniq")]
        verbose_name = "کمپین معرف"
        verbose_name_plural = "کمپین‌های معرف"

    def __str__(self):
        return f"{self.partner.display_name} - {self.name}"


class AffiliateClick(models.Model):
    partner = models.ForeignKey(AffiliatePartner, on_delete=models.CASCADE, related_name="clicks", verbose_name="همکار")
    campaign = models.ForeignKey(AffiliateCampaign, on_delete=models.SET_NULL, null=True, blank=True, related_name="clicks", verbose_name="کمپین")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="affiliate_clicks", verbose_name="کاربر شناسایی‌شده")
    visitor_hash = models.CharField(max_length=64, db_index=True, verbose_name="شناسه ناشناس بازدیدکننده")
    ip_hash = models.CharField(max_length=64, blank=True, verbose_name="هش IP")
    user_agent_hash = models.CharField(max_length=64, blank=True, verbose_name="هش مرورگر")
    landing_path = models.CharField(max_length=500, blank=True, verbose_name="صفحه ورود")
    referrer_url = models.CharField(max_length=500, blank=True, verbose_name="صفحه ارجاع‌دهنده")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["partner", "-created_at"], name="aff_click_partner_date_idx")]
        verbose_name = "کلیک معرفی"
        verbose_name_plural = "کلیک‌های معرفی"


class AffiliateAttribution(models.Model):
    customer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="affiliate_attribution", verbose_name="مشتری معرفی‌شده")
    partner = models.ForeignKey(AffiliatePartner, on_delete=models.PROTECT, related_name="attributions", verbose_name="معرف")
    campaign = models.ForeignKey(AffiliateCampaign, on_delete=models.SET_NULL, null=True, blank=True, related_name="attributions", verbose_name="کمپین")
    click = models.ForeignKey(AffiliateClick, on_delete=models.SET_NULL, null=True, blank=True, related_name="attributions", verbose_name="کلیک مبنا")
    is_locked = models.BooleanField(default=True, verbose_name="انتساب دائمی")
    admin_note = models.TextField(blank=True, verbose_name="یادداشت مدیریت")
    attributed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-attributed_at"]
        verbose_name = "انتساب مشتری به معرف"
        verbose_name_plural = "انتساب مشتریان به معرف‌ها"

    def __str__(self):
        return f"{self.customer} ← {self.partner}"


class AffiliateCommission(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار تحویل/تأیید"),
        ("approved", "قابل تسویه"),
        ("requested", "درخواست تسویه شده"),
        ("paid", "پرداخت شده"),
        ("reversed", "برگشت خورده"),
        ("cancelled", "لغو شده"),
    ]
    partner = models.ForeignKey(AffiliatePartner, on_delete=models.PROTECT, related_name="commissions", verbose_name="همکار")
    order = models.OneToOneField(StoreOrder, on_delete=models.PROTECT, related_name="affiliate_commission", verbose_name="سفارش")
    campaign = models.ForeignKey(AffiliateCampaign, on_delete=models.SET_NULL, null=True, blank=True, related_name="commissions", verbose_name="کمپین")
    attribution = models.ForeignKey(AffiliateAttribution, on_delete=models.SET_NULL, null=True, blank=True, related_name="commissions", verbose_name="انتساب مشتری")
    commission_type = models.CharField(max_length=20, choices=AffiliateTier.COMMISSION_CHOICES, verbose_name="نوع پورسانت ثبت‌شده")
    commission_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="نرخ یا مبلغ ثبت‌شده")
    basis_amount = models.PositiveBigIntegerField(default=0, verbose_name="مبلغ مبنای محاسبه")
    amount = models.PositiveBigIntegerField(default=0, verbose_name="مبلغ پورسانت")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True, verbose_name="وضعیت")
    eligible_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="زمان قابل تأیید شدن")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان تأیید")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان پرداخت")
    reversed_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان برگشت")
    note = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "پورسانت همکاری"
        verbose_name_plural = "پورسانت‌های همکاری"

    def __str__(self):
        return f"{self.partner} - {self.order.order_number} - {self.amount:,}"


class AffiliatePayout(models.Model):
    STATUS_CHOICES = [
        ("requested", "درخواست‌شده"),
        ("approved", "تأیید مدیریت"),
        ("paid", "پرداخت‌شده"),
        ("rejected", "ردشده"),
        ("cancelled", "لغوشده"),
    ]
    payout_number = models.CharField(max_length=40, default=generate_payout_number, unique=True, editable=False, db_index=True, verbose_name="شماره تسویه")
    partner = models.ForeignKey(AffiliatePartner, on_delete=models.PROTECT, related_name="payouts", verbose_name="همکار")
    amount = models.PositiveBigIntegerField(default=0, verbose_name="مبلغ تسویه")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="requested", db_index=True, verbose_name="وضعیت")
    sheba_number = models.CharField(max_length=26, blank=True, verbose_name="شماره شبا هنگام درخواست")
    card_number = models.CharField(max_length=16, blank=True, verbose_name="شماره کارت هنگام درخواست")
    account_holder = models.CharField(max_length=160, blank=True, verbose_name="صاحب حساب")
    reference_number = models.CharField(max_length=120, blank=True, verbose_name="شماره پیگیری پرداخت")
    partner_note = models.TextField(blank=True, verbose_name="توضیح همکار")
    admin_note = models.TextField(blank=True, verbose_name="یادداشت مدیریت")
    requested_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان پردازش")

    class Meta:
        ordering = ["-requested_at"]
        verbose_name = "درخواست تسویه همکار"
        verbose_name_plural = "درخواست‌های تسویه همکاران"

    def __str__(self):
        return self.payout_number


class AffiliatePayoutItem(models.Model):
    payout = models.ForeignKey(AffiliatePayout, on_delete=models.CASCADE, related_name="items", verbose_name="تسویه")
    commission = models.OneToOneField(AffiliateCommission, on_delete=models.PROTECT, related_name="payout_item", verbose_name="پورسانت")
    amount = models.PositiveBigIntegerField(verbose_name="مبلغ")

    class Meta:
        verbose_name = "ردیف تسویه"
        verbose_name_plural = "ردیف‌های تسویه"


class AffiliateLedgerEntry(models.Model):
    TYPE_CHOICES = [
        ("commission", "اعتبار پورسانت"),
        ("payout", "پرداخت تسویه"),
        ("reversal", "برگشت پورسانت"),
        ("adjustment", "اصلاح دستی"),
    ]
    partner = models.ForeignKey(AffiliatePartner, on_delete=models.PROTECT, related_name="ledger_entries", verbose_name="همکار")
    entry_type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True, verbose_name="نوع تراکنش")
    amount = models.BigIntegerField(verbose_name="مبلغ؛ مثبت بستانکار، منفی بدهکار")
    commission = models.ForeignKey(AffiliateCommission, on_delete=models.SET_NULL, null=True, blank=True, related_name="ledger_entries", verbose_name="پورسانت")
    payout = models.ForeignKey(AffiliatePayout, on_delete=models.SET_NULL, null=True, blank=True, related_name="ledger_entries", verbose_name="تسویه")
    note = models.CharField(max_length=300, blank=True, verbose_name="توضیح")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="affiliate_ledger_actions", verbose_name="ثبت‌کننده")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "گردش مالی همکار"
        verbose_name_plural = "گردش مالی همکاران"


class AffiliateProgramDashboard(AffiliatePartner):
    class Meta:
        proxy = True
        verbose_name = "داشبورد همکاری در فروش"
        verbose_name_plural = "داشبورد همکاری در فروش"

# END AFFILIATE PARTNER PROGRAM PHASE 7

# BEGIN INVENTORY FINANCE CATALOG PHASE 8


def generate_filament_purchase_number():
    return f"FPR-{timezone.now():%y%m%d}-{uuid.uuid4().hex[:7].upper()}"


def generate_filament_spool_code():
    return f"SPL-{uuid.uuid4().hex[:10].upper()}"


def generate_production_job_number():
    return f"JOB-{timezone.now():%y%m%d}-{uuid.uuid4().hex[:7].upper()}"


class PrintCatalogSource(models.Model):
    ADAPTER_CHOICES = [
        ("generic", "استخراج عمومی OpenGraph و JSON-LD"),
        ("custom", "آداپتور اختصاصی سایت"),
    ]

    name = models.CharField(max_length=160, verbose_name="نام منبع")
    code = models.SlugField(max_length=80, unique=True, verbose_name="کد منبع")
    base_url = models.URLField(verbose_name="آدرس پایه")
    allowed_domains = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="دامنه‌های مجاز",
        help_text="چند دامنه را با ویرگول جدا کنید. اگر خالی باشد دامنه base_url استفاده می‌شود.",
    )
    adapter_key = models.CharField(
        max_length=50,
        choices=ADAPTER_CHOICES,
        default="generic",
        verbose_name="نوع استخراج",
    )
    default_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="catalog_sources",
        verbose_name="دسته پیش‌فرض محصول",
    )
    request_headers = models.JSONField(default=dict, blank=True, verbose_name="هدرهای درخواست")
    request_timeout_seconds = models.PositiveSmallIntegerField(default=20, verbose_name="مهلت درخواست به ثانیه")
    respect_robots_txt = models.BooleanField(default=True, verbose_name="رعایت robots.txt")
    download_preview_images = models.BooleanField(default=True, verbose_name="ذخیره تصویر پیش‌نمایش")
    store_private_download_url = models.BooleanField(
        default=True,
        verbose_name="ذخیره لینک دانلود خصوصی برای ادمین",
    )
    license_note = models.TextField(
        blank=True,
        verbose_name="یادداشت مجوز و شرایط استفاده",
        help_text="فقط منابعی را وارد کنید که اجازه استفاده، چاپ یا فروش آن‌ها را دارید.",
    )
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "منبع کاتالوگ فایل چاپ"
        verbose_name_plural = "منابع کاتالوگ فایل‌های چاپ"

    def __str__(self):
        return self.name


class ImportedPrintAsset(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("reviewed", "بررسی‌شده"),
        ("converted", "تبدیل‌شده به محصول"),
        ("rejected", "ردشده"),
    ]

    source = models.ForeignKey(
        PrintCatalogSource,
        on_delete=models.PROTECT,
        related_name="assets",
        verbose_name="منبع",
    )
    source_url = models.URLField(max_length=1000, verbose_name="صفحه منبع")
    external_id = models.CharField(max_length=160, blank=True, db_index=True, verbose_name="شناسه در سایت منبع")
    title = models.CharField(max_length=260, verbose_name="عنوان")
    slug = models.SlugField(max_length=280, allow_unicode=True, blank=True, verbose_name="شناسه داخلی")
    short_description = models.CharField(max_length=500, blank=True, verbose_name="توضیح کوتاه")
    description = models.TextField(blank=True, verbose_name="توضیحات کامل")
    technical_specs = models.JSONField(default=dict, blank=True, verbose_name="مشخصات فنی استخراج‌شده")
    tags = models.CharField(max_length=700, blank=True, verbose_name="برچسب‌ها")
    author_name = models.CharField(max_length=200, blank=True, verbose_name="طراح یا ناشر")
    license_name = models.CharField(max_length=200, blank=True, verbose_name="نوع مجوز")
    license_url = models.URLField(max_length=1000, blank=True, verbose_name="لینک مجوز")
    remote_image_url = models.URLField(max_length=1000, blank=True, verbose_name="آدرس تصویر اصلی منبع")
    preview_image = models.ImageField(
        upload_to="store/imported-models/previews/",
        blank=True,
        null=True,
        verbose_name="تصویر ذخیره‌شده",
    )
    private_download_url = models.URLField(
        max_length=2000,
        blank=True,
        verbose_name="لینک دانلود خصوصی",
        help_text="این لینک فقط در پنل مدیریت قابل مشاهده است و در صفحات عمومی، Schema و فیدها نمایش داده نمی‌شود.",
    )
    file_format = models.CharField(max_length=80, blank=True, verbose_name="فرمت فایل")
    ARCHIVE_STATUS_CHOICES = [
        ("none", "فایل محلی نداریم"),
        ("downloaded", "فایل دانلود شده"),
        ("archived", "فایل بایگانی و قابل استفاده"),
        ("ordered", "فایل برای سفارش مشتری نگهداری می‌شود"),
    ]
    archive_status = models.CharField(
        max_length=20, choices=ARCHIVE_STATUS_CHOICES, default="none", db_index=True,
        verbose_name="وضعیت فایل محلی",
    )
    archived_model_file = models.FileField(
        upload_to="store/private-imported-models/", blank=True, null=True,
        verbose_name="فایل سه‌بعدی آرشیوی",
        help_text="فایل خصوصی است و فقط مدیریت به آن دسترسی دارد.",
    )
    keep_public_when_source_disabled = models.BooleanField(
        default=False,
        verbose_name="حفظ نمایش در صورت قطع منبع",
        help_text="برای مدل‌هایی که فایل آن‌ها موجود یا قبلاً سفارش گرفته شده فعال می‌شود.",
    )
    source_payload = models.JSONField(default=dict, blank=True, verbose_name="داده خام استخراج")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True, verbose_name="وضعیت")
    product = models.OneToOneField(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="imported_source_asset",
        verbose_name="محصول ساخته‌شده",
    )
    admin_note = models.TextField(blank=True, verbose_name="یادداشت داخلی")
    imported_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-imported_at", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["source", "source_url"], name="unique_imported_asset_source_url")
        ]
        verbose_name = "فایل آماده چاپ واردشده"
        verbose_name_plural = "فایل‌های آماده چاپ واردشده"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.archived_model_file or self.archive_status in {"downloaded", "archived", "ordered"}:
            self.keep_public_when_source_disabled = True
            if kwargs.get("update_fields") is not None:
                kwargs["update_fields"] = set(kwargs["update_fields"]) | {"keep_public_when_source_disabled"}
        super().save(*args, **kwargs)

    @property
    def catalog_image_url(self):
        """Best available public preview without exposing private file links."""
        if self.preview_image:
            try:
                return self.preview_image.url
            except Exception:
                pass
        if self.remote_image_url:
            return self.remote_image_url
        try:
            return next((url for url in (self.metrics.image_urls or []) if url), "")
        except Exception:
            return ""

    @property
    def has_source_file_reference(self):
        if self.private_download_url or self.file_format:
            return True
        try:
            return bool(self.metrics.file_links or self.metrics.file_formats)
        except Exception:
            return bool((self.technical_specs or {}).get("source_file_available"))

    @property
    def has_retained_local_file(self):
        product_file = False
        if self.product_id:
            try:
                product_file = bool(self.product.model_file)
            except Exception:
                product_file = False
        return bool(
            self.archived_model_file
            or self.archive_status in {"downloaded", "archived", "ordered"}
            or self.keep_public_when_source_disabled
            or product_file
        )

    @property
    def public_display_mode(self):
        """Return hidden, reference, or printable based on source policy and retained files."""
        retained = self.has_retained_local_file
        if not self.source.is_active and not retained:
            return "hidden"
        try:
            policy = self.source.sync_policy
        except Exception:
            return "printable" if retained and self.has_source_file_reference else "reference"
        if (not policy.is_active or not policy.public_reference_enabled) and not retained:
            return "hidden"
        try:
            if self.metrics.may_be_public and self.has_source_file_reference:
                return "printable"
        except Exception:
            pass
        return "reference"


class ImportedPrintAssetImage(models.Model):
    asset = models.ForeignKey(ImportedPrintAsset, on_delete=models.CASCADE, related_name="images", verbose_name="فایل واردشده")
    remote_url = models.URLField(max_length=1000, blank=True, verbose_name="آدرس تصویر منبع")
    image = models.ImageField(upload_to="store/imported-models/gallery/", blank=True, null=True, verbose_name="تصویر ذخیره‌شده")
    alt_text = models.CharField(max_length=260, blank=True, verbose_name="متن جایگزین")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "تصویر فایل واردشده"
        verbose_name_plural = "تصاویر فایل‌های واردشده"


class PrintCatalogImportJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار اجرا"),
        ("running", "در حال اجرا"),
        ("success", "موفق"),
        ("failed", "ناموفق"),
    ]

    source = models.ForeignKey(PrintCatalogSource, on_delete=models.PROTECT, related_name="import_jobs", verbose_name="منبع")
    source_url = models.URLField(max_length=1000, verbose_name="صفحه هدف")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True, verbose_name="وضعیت")
    result_asset = models.ForeignKey(
        ImportedPrintAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="import_jobs",
        verbose_name="نتیجه",
    )
    log = models.TextField(blank=True, verbose_name="گزارش اجرا")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="catalog_import_jobs",
        verbose_name="ثبت‌کننده",
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "اجرای واردسازی کاتالوگ"
        verbose_name_plural = "اجراهای واردسازی کاتالوگ"


class FilamentPurchase(models.Model):
    STATUS_CHOICES = [("draft", "پیش‌نویس"), ("received", "وارد انبار شده"), ("cancelled", "لغو شده")]

    purchase_number = models.CharField(
        max_length=40,
        default=generate_filament_purchase_number,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="شماره خرید",
    )
    supplier_name = models.CharField(max_length=180, blank=True, verbose_name="فروشنده")
    invoice_number = models.CharField(max_length=100, blank=True, verbose_name="شماره فاکتور خرید")
    purchased_at = models.DateField(default=timezone.localdate, db_index=True, verbose_name="تاریخ خرید")
    shipping_cost = models.PositiveBigIntegerField(default=0, verbose_name="هزینه حمل خرید")
    other_cost = models.PositiveBigIntegerField(default=0, verbose_name="سایر هزینه‌های خرید")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", db_index=True, verbose_name="وضعیت")
    note = models.TextField(blank=True, verbose_name="توضیحات")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="filament_purchases",
        verbose_name="ثبت‌کننده",
    )
    received_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان ورود انبار")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-purchased_at", "-id"]
        verbose_name = "خرید فیلامنت"
        verbose_name_plural = "خریدهای فیلامنت"

    def __str__(self):
        return self.purchase_number


class FilamentPurchaseItem(models.Model):
    purchase = models.ForeignKey(FilamentPurchase, on_delete=models.CASCADE, related_name="items", verbose_name="خرید")
    material = models.ForeignKey("website.Material", on_delete=models.PROTECT, related_name="filament_purchase_items", verbose_name="متریال")
    brand = models.CharField(max_length=120, blank=True, verbose_name="برند")
    color_name = models.CharField(max_length=100, blank=True, verbose_name="رنگ")
    color_hex = models.CharField(max_length=20, blank=True, verbose_name="کد رنگ")
    quantity_rolls = models.PositiveIntegerField(default=1, verbose_name="تعداد رول")
    net_weight_per_roll_grams = models.DecimalField(max_digits=10, decimal_places=2, default=1000, verbose_name="وزن خالص هر رول به گرم")
    total_purchase_amount = models.PositiveBigIntegerField(default=0, verbose_name="جمع مبلغ خرید رول‌ها")
    allocated_extra_cost = models.PositiveBigIntegerField(default=0, verbose_name="سهم هزینه حمل و جانبی")
    sale_price_per_gram = models.PositiveIntegerField(default=0, verbose_name="قیمت فروش هر گرم")
    generated_spools = models.BooleanField(default=False, editable=False, verbose_name="رول‌ها ساخته شده‌اند")

    class Meta:
        verbose_name = "ردیف خرید فیلامنت"
        verbose_name_plural = "ردیف‌های خرید فیلامنت"

    @property
    def total_weight_grams(self):
        return Decimal(self.quantity_rolls) * Decimal(self.net_weight_per_roll_grams)

    @property
    def landed_cost(self):
        return int(self.total_purchase_amount) + int(self.allocated_extra_cost)

    @property
    def cost_per_gram(self):
        if not self.total_weight_grams:
            return Decimal("0")
        return (Decimal(self.landed_cost) / self.total_weight_grams).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def __str__(self):
        return f"{self.material} - {self.quantity_rolls} رول"


class FilamentSpool(models.Model):
    STATUS_CHOICES = [
        ("sealed", "پلمب"),
        ("open", "بازشده"),
        ("empty", "تمام‌شده"),
        ("quarantine", "قرنطینه"),
        ("archived", "بایگانی"),
    ]

    purchase_item = models.ForeignKey(
        FilamentPurchaseItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="spools",
        verbose_name="ردیف خرید",
    )
    material = models.ForeignKey("website.Material", on_delete=models.PROTECT, related_name="filament_spools", verbose_name="متریال")
    code = models.CharField(max_length=40, default=generate_filament_spool_code, unique=True, db_index=True, verbose_name="کد رول")
    brand = models.CharField(max_length=120, blank=True, verbose_name="برند")
    color_name = models.CharField(max_length=100, blank=True, verbose_name="رنگ")
    color_hex = models.CharField(max_length=20, blank=True, verbose_name="کد رنگ")
    nominal_weight_grams = models.DecimalField(max_digits=10, decimal_places=2, default=1000, verbose_name="وزن اولیه خالص")
    remaining_weight_grams = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_index=True, verbose_name="وزن باقی‌مانده")
    tare_weight_grams = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="وزن قرقره خالی")
    purchase_price = models.PositiveBigIntegerField(default=0, verbose_name="قیمت خرید این رول")
    cost_per_gram_snapshot = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="قیمت تمام‌شده هر گرم")
    sale_price_per_gram_snapshot = models.PositiveIntegerField(default=0, verbose_name="قیمت فروش هر گرم هنگام ورود")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="sealed", db_index=True, verbose_name="وضعیت")
    location = models.CharField(max_length=120, blank=True, verbose_name="محل نگهداری")
    purchased_at = models.DateField(default=timezone.localdate, db_index=True, verbose_name="تاریخ خرید")
    opened_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان بازشدن")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["material", "purchased_at", "id"]
        indexes = [models.Index(fields=["material", "status", "remaining_weight_grams"], name="filament_spool_stock_idx")]
        verbose_name = "رول فیلامنت"
        verbose_name_plural = "رول‌های فیلامنت"

    def __str__(self):
        return f"{self.code} - {self.material} - {self.remaining_weight_grams} گرم"

    def save(self, *args, **kwargs):
        if self._state.adding and not self.remaining_weight_grams and self.status not in {"empty", "archived"}:
            self.remaining_weight_grams = self.nominal_weight_grams
        if Decimal(self.remaining_weight_grams or 0) <= 0 and self.status not in {"quarantine", "archived"}:
            self.remaining_weight_grams = Decimal("0")
            self.status = "empty"
        super().save(*args, **kwargs)


class ProductionJob(models.Model):
    STATUS_CHOICES = [
        ("planned", "برنامه‌ریزی"),
        ("printing", "در حال چاپ"),
        ("post_processing", "پرداخت‌کاری و تکمیل"),
        ("completed", "تکمیل‌شده"),
        ("cancelled", "لغوشده"),
    ]

    job_number = models.CharField(max_length=40, default=generate_production_job_number, unique=True, editable=False, db_index=True, verbose_name="شماره پروژه")
    store_order = models.OneToOneField(
        "StoreOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="production_job",
        verbose_name="سفارش فروشگاه",
    )
    custom_order = models.OneToOneField(
        "website.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="production_job",
        verbose_name="سفارش ساخت سفارشی",
    )
    title = models.CharField(max_length=260, verbose_name="عنوان پروژه")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="planned", db_index=True, verbose_name="وضعیت")
    revenue_snapshot = models.PositiveBigIntegerField(default=0, verbose_name="درآمد ثبت‌شده")
    tax_snapshot = models.PositiveBigIntegerField(default=0, verbose_name="مالیات ثبت‌شده")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="شروع اجرا")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="پایان اجرا")
    note = models.TextField(blank=True, verbose_name="توضیحات داخلی")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "پروژه تولید و سود"
        verbose_name_plural = "پروژه‌های تولید و سود"

    def __str__(self):
        return f"{self.job_number} - {self.title}"

    @property
    def base_revenue(self):
        if self.revenue_snapshot:
            return int(self.revenue_snapshot)
        if self.store_order_id:
            return max(0, int(self.store_order.total_amount) - int(self.store_order.tax_amount))
        if self.custom_order_id:
            try:
                return int(self.custom_order.quote.total_price)
            except Exception:
                return 0
        return 0

    @property
    def extra_revenue(self):
        return int(self.cost_entries.filter(included_in_order_total=False).aggregate(value=models.Sum("customer_charge"))["value"] or 0)

    @property
    def total_revenue(self):
        return self.base_revenue + self.extra_revenue

    @property
    def material_cost(self):
        return int(self.material_usages.aggregate(value=models.Sum("material_cost_snapshot"))["value"] or 0)

    @property
    def operating_cost(self):
        return int(self.cost_entries.aggregate(value=models.Sum("actual_cost"))["value"] or 0)

    @property
    def affiliate_cost(self):
        if not self.store_order_id:
            return 0
        try:
            commission = self.store_order.affiliate_commission
        except Exception:
            return 0
        if commission.status in {"reversed", "cancelled"}:
            return 0
        return int(commission.amount)

    @property
    def total_cost(self):
        return self.material_cost + self.operating_cost + self.affiliate_cost

    @property
    def net_profit(self):
        return self.total_revenue - self.total_cost

    @property
    def profit_margin_percent(self):
        if not self.total_revenue:
            return Decimal("0")
        return (Decimal(self.net_profit) * Decimal("100") / Decimal(self.total_revenue)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class MaterialUsage(models.Model):
    job = models.ForeignKey(ProductionJob, on_delete=models.CASCADE, related_name="material_usages", verbose_name="پروژه")
    material = models.ForeignKey("website.Material", on_delete=models.PROTECT, related_name="production_usages", verbose_name="متریال")
    color_name = models.CharField(max_length=100, blank=True, verbose_name="رنگ")
    planned_grams = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="مصرف برآوردی")
    actual_grams = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="مصرف واقعی")
    waste_grams = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="پرت و تست")
    sale_price_per_gram_snapshot = models.PositiveIntegerField(default=0, verbose_name="قیمت فروش هر گرم")
    material_charge_snapshot = models.PositiveBigIntegerField(default=0, verbose_name="فروش متریال")
    cost_per_gram_snapshot = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="میانگین قیمت خرید هر گرم")
    material_cost_snapshot = models.PositiveBigIntegerField(default=0, verbose_name="بهای تمام‌شده متریال")
    posted_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="زمان ثبت خروج انبار")
    note = models.TextField(blank=True, verbose_name="توضیحات")

    class Meta:
        ordering = ["id"]
        verbose_name = "مصرف متریال پروژه"
        verbose_name_plural = "مصرف‌های متریال پروژه"

    @property
    def consumption_grams(self):
        actual = Decimal(self.actual_grams or 0)
        planned = Decimal(self.planned_grams or 0)
        waste = Decimal(self.waste_grams or 0)
        return max(Decimal("0"), (actual if actual > 0 else planned) + waste)


class FilamentMovement(models.Model):
    TYPE_CHOICES = [
        ("purchase", "ورود خرید"),
        ("consume", "مصرف تولید"),
        ("waste", "پرت و تست"),
        ("adjustment", "اصلاح موجودی"),
        ("return", "بازگشت به انبار"),
    ]

    spool = models.ForeignKey(FilamentSpool, on_delete=models.PROTECT, related_name="movements", verbose_name="رول")
    material = models.ForeignKey("website.Material", on_delete=models.PROTECT, related_name="filament_movements", verbose_name="متریال")
    job = models.ForeignKey(ProductionJob, on_delete=models.SET_NULL, null=True, blank=True, related_name="filament_movements", verbose_name="پروژه")
    usage = models.ForeignKey(MaterialUsage, on_delete=models.SET_NULL, null=True, blank=True, related_name="movements", verbose_name="مصرف پروژه")
    movement_type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True, verbose_name="نوع گردش")
    grams = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="تغییر وزن؛ خروج منفی")
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="مانده رول")
    unit_cost_snapshot = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="قیمت خرید هر گرم")
    total_cost = models.PositiveBigIntegerField(default=0, verbose_name="ارزش گردش")
    note = models.CharField(max_length=400, blank=True, verbose_name="توضیح")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="filament_movements",
        verbose_name="ثبت‌کننده",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "گردش وزنی فیلامنت"
        verbose_name_plural = "گردش‌های وزنی فیلامنت"


class CostEntry(models.Model):
    CATEGORY_CHOICES = [
        ("design", "طراحی و مهندسی معکوس"),
        ("courier", "پیک"),
        ("shipping", "ارسال"),
        ("packaging", "بسته‌بندی"),
        ("labor", "دستمزد"),
        ("machine", "کارکرد دستگاه"),
        ("electricity", "برق و انرژی"),
        ("maintenance", "استهلاک و تعمیر"),
        ("post_processing", "پرداخت‌کاری و مونتاژ"),
        ("software", "نرم‌افزار و خدمات"),
        ("other", "سایر"),
    ]

    job = models.ForeignKey(
        ProductionJob,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cost_entries",
        verbose_name="پروژه؛ برای هزینه عمومی خالی بماند",
    )
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, db_index=True, verbose_name="نوع هزینه")
    description = models.CharField(max_length=300, verbose_name="شرح")
    actual_cost = models.PositiveBigIntegerField(default=0, verbose_name="هزینه واقعی")
    customer_charge = models.PositiveBigIntegerField(default=0, verbose_name="مبلغ دریافت‌شده از مشتری")
    included_in_order_total = models.BooleanField(
        default=True,
        verbose_name="مبلغ دریافتی قبلاً در فاکتور سفارش حساب شده",
    )
    receipt = models.FileField(upload_to="store/finance/receipts/", blank=True, null=True, verbose_name="رسید یا مدرک")
    incurred_at = models.DateField(default=timezone.localdate, db_index=True, verbose_name="تاریخ هزینه")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cost_entries",
        verbose_name="ثبت‌کننده",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-incurred_at", "-id"]
        verbose_name = "هزینه و درآمد جانبی"
        verbose_name_plural = "هزینه‌ها و درآمدهای جانبی"

    def __str__(self):
        return f"{self.get_category_display()} - {self.description}"


class BusinessFinanceDashboard(ProductionJob):
    class Meta:
        proxy = True
        verbose_name = "داشبورد انبار و سود"
        verbose_name_plural = "داشبورد انبار و سود"

# END INVENTORY FINANCE CATALOG PHASE 8

# BEGIN MULTI SOURCE CATALOG PHASE 9
class CatalogSourcePolicy(models.Model):
    SOURCE_KIND_CHOICES = [
        ("makerworld", "MakerWorld / Bambu Lab"),
        ("printables", "Printables"),
        ("thingiverse", "Thingiverse"),
        ("grabcad", "GrabCAD"),
        ("custom", "سفارشی"),
    ]
    DISCOVERY_MODE_CHOICES = [
        ("public_html", "HTML عمومی"),
        ("official_api", "API رسمی"),
        ("admin_reference", "فقط مرجع مدیریتی"),
    ]
    PUBLIC_POLICY_CHOICES = [
        ("admin_only", "فقط ادمین"),
        ("licensed_only", "فقط با مجوز تجاری معتبر"),
        ("source_link_only", "نمایش عمومی فقط با لینک منبع"),
    ]

    source = models.OneToOneField(
        "PrintCatalogSource",
        on_delete=models.CASCADE,
        related_name="sync_policy",
        verbose_name="منبع",
    )
    source_kind = models.CharField(
        max_length=30,
        choices=SOURCE_KIND_CHOICES,
        db_index=True,
        verbose_name="نوع منبع",
    )
    discovery_mode = models.CharField(
        max_length=30,
        choices=DISCOVERY_MODE_CHOICES,
        default="public_html",
        verbose_name="روش دریافت",
    )
    public_display_policy = models.CharField(
        max_length=30,
        choices=PUBLIC_POLICY_CHOICES,
        default="licensed_only",
        verbose_name="سیاست نمایش عمومی",
    )
    public_reference_enabled = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="نمایش مرجع عمومی",
        help_text=(
            "در صورت فعال‌بودن، نام، تصاویر، مشخصات و لینک صفحه منبع حتی بدون فایل مستقیم یا مجوز فروش "
            "به‌صورت مرجع نمایش داده می‌شود. لینک فایل خصوصی هرگز عمومی نمی‌شود."
        ),
    )
    discovery_url_template = models.CharField(
        max_length=600,
        blank=True,
        verbose_name="قالب آدرس لیست",
        help_text="می‌تواند شامل {page}، {sort} و {limit} باشد.",
    )
    api_base_url = models.URLField(blank=True, verbose_name="آدرس پایه API")
    api_token_env = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="نام متغیر محیطی توکن",
    )
    source_priority = models.PositiveSmallIntegerField(
        default=100, db_index=True,
        verbose_name="اولویت منبع",
        help_text="عدد کمتر یعنی دریافت و نمایش زودتر؛ برای MakerWorld مقدار ۱۰ پیشنهاد می‌شود.",
    )
    default_limit = models.PositiveIntegerField(default=200, verbose_name="تعداد پیش‌فرض دریافت")
    maximum_limit = models.PositiveIntegerField(default=2000, verbose_name="حداکثر تعداد در هر اجرا")
    page_size = models.PositiveIntegerField(default=24, verbose_name="تعداد در هر صفحه")
    request_delay_ms = models.PositiveIntegerField(default=1200, verbose_name="فاصله درخواست‌ها میلی‌ثانیه")
    max_pages = models.PositiveIntegerField(default=100, verbose_name="حداکثر صفحه")
    cache_images_after_approval = models.BooleanField(
        default=True,
        verbose_name="ذخیره محلی تصویر پس از تأیید",
    )
    store_download_links = models.BooleanField(
        default=True,
        verbose_name="ذخیره لینک فایل فقط برای ادمین",
    )
    auto_create_draft_products = models.BooleanField(
        default=False,
        verbose_name="ساخت خودکار محصول غیرفعال پس از تأیید",
    )
    terms_url = models.URLField(blank=True, verbose_name="لینک قوانین منبع")
    requires_attribution = models.BooleanField(default=True, verbose_name="الزام ذکر منبع")
    policy_note = models.TextField(blank=True, verbose_name="یادداشت حقوقی و اجرایی")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    last_synced_at = models.DateTimeField(blank=True, null=True, verbose_name="آخرین همگام‌سازی")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "سیاست دریافت کاتالوگ"
        verbose_name_plural = "سیاست‌های دریافت کاتالوگ"

    def __str__(self):
        return f"{self.source.name} - {self.get_discovery_mode_display()}"

    def clamp_limit(self, requested=None):
        value = int(requested or self.default_limit or 1)
        return max(1, min(value, self.maximum_limit or value))


class CatalogCategoryRule(models.Model):
    SEGMENT_CHOICES = [
        ("industrial", "صنعتی و مهندسی"),
        ("functional", "کاربردی و ابزار"),
        ("decorative", "تزئینی و دکور"),
        ("toy", "اسباب‌بازی و سرگرمی"),
        ("cosplay", "کازپلی و ماکت"),
        ("education", "آموزشی و دانشگاهی"),
        ("automotive", "خودرو و موتورسیکلت"),
        ("other", "سایر"),
    ]

    source_kind = models.CharField(
        max_length=30,
        blank=True,
        choices=[("", "همه منابع")] + CatalogSourcePolicy.SOURCE_KIND_CHOICES,
        verbose_name="منبع",
    )
    title_keywords = models.TextField(
        blank=True,
        verbose_name="کلیدواژه‌های عنوان/برچسب",
        help_text="با ویرگول جدا کنید.",
    )
    source_category_keywords = models.TextField(
        blank=True,
        verbose_name="کلیدواژه دسته منبع",
    )
    target_category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="catalog_rules",
        verbose_name="دسته مقصد",
    )
    segment = models.CharField(max_length=30, choices=SEGMENT_CHOICES, verbose_name="گروه خودکار")
    priority = models.PositiveIntegerField(default=100, db_index=True, verbose_name="اولویت")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")

    class Meta:
        ordering = ["priority", "id"]
        verbose_name = "قانون دسته‌بندی خودکار"
        verbose_name_plural = "قوانین دسته‌بندی خودکار"

    def __str__(self):
        return f"{self.get_segment_display()} ← {self.target_category}"


class CatalogSyncRun(models.Model):
    SORT_CHOICES = [
        ("downloads", "بیشترین دانلود"),
        ("likes", "بیشترین لایک"),
        ("views", "بیشترین بازدید"),
        ("trending", "ترند"),
        ("newest", "جدیدترین"),
    ]
    STATUS_CHOICES = [
        ("queued", "در صف"),
        ("running", "در حال اجرا"),
        ("completed", "تکمیل‌شده"),
        ("partial", "نیمه‌کامل"),
        ("failed", "ناموفق"),
        ("cancelled", "متوقف‌شده"),
    ]

    source = models.ForeignKey(
        "PrintCatalogSource",
        on_delete=models.CASCADE,
        related_name="sync_runs",
        verbose_name="منبع",
    )
    sort_mode = models.CharField(max_length=20, choices=SORT_CHOICES, default="downloads", verbose_name="مرتب‌سازی")
    requested_limit = models.PositiveIntegerField(default=200, verbose_name="تعداد درخواستی")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued", db_index=True, verbose_name="وضعیت")
    discovered_count = models.PositiveIntegerField(default=0, verbose_name="کشف‌شده")
    imported_count = models.PositiveIntegerField(default=0, verbose_name="ثبت یا به‌روزرسانی")
    skipped_count = models.PositiveIntegerField(default=0, verbose_name="ردشده")
    failed_count = models.PositiveIntegerField(default=0, verbose_name="خطا")
    current_page = models.PositiveIntegerField(default=0, verbose_name="صفحه فعلی")
    cursor = models.CharField(max_length=500, blank=True, verbose_name="نشانگر ادامه")
    log = models.TextField(blank=True, verbose_name="گزارش")
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="catalog_sync_runs",
        verbose_name="اجراکننده",
    )
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    deadline_at = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name="مهلت پایان")
    heartbeat_at = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name="آخرین فعالیت")
    cancelled_at = models.DateTimeField(blank=True, null=True, verbose_name="زمان توقف دستی")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "اجرای دریافت کاتالوگ"
        verbose_name_plural = "اجراهای دریافت کاتالوگ"

    def __str__(self):
        return f"{self.source.name} - {self.requested_limit} - {self.get_status_display()}"


class CatalogAssetMetrics(models.Model):
    LICENSE_REVIEW_CHOICES = [
        ("unknown", "نامشخص"),
        ("allowed", "مجاز برای فروش چاپ"),
        ("blocked", "غیرمجاز برای فروش چاپ"),
        ("manual", "نیازمند بررسی دستی"),
    ]

    asset = models.OneToOneField(
        "ImportedPrintAsset",
        on_delete=models.CASCADE,
        related_name="metrics",
        verbose_name="فایل واردشده",
    )
    source_kind = models.CharField(max_length=30, db_index=True, verbose_name="منبع")
    source_category = models.CharField(max_length=250, blank=True, verbose_name="دسته منبع")
    segment = models.CharField(
        max_length=30,
        choices=CatalogCategoryRule.SEGMENT_CHOICES,
        default="other",
        db_index=True,
        verbose_name="گروه خودکار",
    )
    target_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="external_catalog_assets",
        blank=True,
        null=True,
        verbose_name="دسته مقصد",
    )
    popularity_rank = models.PositiveIntegerField(default=0, verbose_name="رتبه محبوبیت")
    views_count = models.PositiveBigIntegerField(default=0, db_index=True, verbose_name="بازدید")
    likes_count = models.PositiveBigIntegerField(default=0, db_index=True, verbose_name="لایک")
    downloads_count = models.PositiveBigIntegerField(default=0, db_index=True, verbose_name="دانلود")
    makes_count = models.PositiveBigIntegerField(default=0, verbose_name="تعداد ساخت")
    comments_count = models.PositiveBigIntegerField(default=0, verbose_name="نظر")
    rating = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name="امتیاز")
    estimated_weight_grams = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="وزن تخمینی گرم",
    )
    estimated_print_minutes = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="زمان تخمینی چاپ دقیقه",
    )
    estimate_source = models.CharField(max_length=100, blank=True, verbose_name="منبع برآورد وزن/زمان")
    file_formats = models.JSONField(default=list, blank=True, verbose_name="فرمت فایل‌ها")
    file_links = models.JSONField(
        default=list,
        blank=True,
        verbose_name="لینک فایل‌ها فقط برای ادمین",
    )
    image_urls = models.JSONField(default=list, blank=True, verbose_name="آدرس تصاویر منبع")
    creator_url = models.URLField(blank=True, verbose_name="صفحه سازنده")
    license_code = models.CharField(max_length=120, blank=True, verbose_name="کد مجوز")
    commercial_use_allowed = models.BooleanField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name="اجازه فروش چاپ فیزیکی",
    )
    license_review_status = models.CharField(
        max_length=20,
        choices=LICENSE_REVIEW_CHOICES,
        default="unknown",
        db_index=True,
        verbose_name="بررسی مجوز",
    )
    public_approved = models.BooleanField(default=False, db_index=True, verbose_name="تأیید نمایش عمومی")
    blocked_reason = models.TextField(blank=True, verbose_name="علت مسدودی")
    attribution_text = models.CharField(max_length=500, blank=True, verbose_name="متن انتساب")
    raw_metrics = models.JSONField(default=dict, blank=True, verbose_name="داده خام شاخص‌ها")
    last_synced_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-downloads_count", "-likes_count", "-views_count", "id"]
        verbose_name = "آمار و مجوز فایل خارجی"
        verbose_name_plural = "آمار و مجوز فایل‌های خارجی"
        indexes = [
            models.Index(fields=["source_kind", "public_approved"], name="store_cat_src_pub_idx"),
            models.Index(fields=["segment", "public_approved"], name="store_cat_seg_pub_idx"),
        ]

    def __str__(self):
        return f"{self.asset.title} - {self.get_license_review_status_display()}"

    @property
    def may_be_public(self):
        if self.source_kind == "grabcad":
            return False
        return (
            self.public_approved
            and self.commercial_use_allowed is True
            and self.license_review_status == "allowed"
        )

    def clean(self):
        from django.core.exceptions import ValidationError
        errors = {}
        if self.public_approved and self.source_kind == "grabcad":
            errors["public_approved"] = "محتوای GrabCAD در این سیستم فقط برای مرجع داخلی ادمین نگهداری می‌شود."
        if self.public_approved and self.commercial_use_allowed is not True:
            errors["public_approved"] = "برای نمایش عمومی باید مجوز فروش چاپ فیزیکی صریحاً تأیید شده باشد."
        if self.public_approved and self.license_review_status != "allowed":
            errors["license_review_status"] = "وضعیت مجوز باید «مجاز» باشد."
        if errors:
            raise ValidationError(errors)


class CatalogSyncDashboard(CatalogSyncRun):
    class Meta:
        proxy = True
        verbose_name = "داشبورد کاتالوگ خارجی"
        verbose_name_plural = "داشبورد کاتالوگ خارجی"

# END MULTI SOURCE CATALOG PHASE 9

# BEGIN PHASE 10 AUTOMATION PRICING AND HOMEPAGE MODELS
from decimal import Decimal
from datetime import time


class CatalogAutomationSetting(models.Model):
    queue_enabled = models.BooleanField(
        default=True,
        verbose_name="صف دریافت فعال باشد",
        help_text="اگر غیرفعال شود، اجرای زمان‌بندی‌شده منابع انجام نمی‌شود؛ اجرای دستی همچنان قابل ثبت است.",
    )
    timezone_name = models.CharField(
        max_length=80,
        default="Asia/Tehran",
        verbose_name="منطقه زمانی اجرای خودکار",
        help_text="برای سایت ایران معمولاً Asia/Tehran مناسب است.",
    )
    process_batch_size = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="تعداد Job در هر اجرای Worker",
        help_text="برای جلوگیری از فشار به هاست اشتراکی مقدار ۱ یا ۲ پیشنهاد می‌شود.",
    )
    stale_run_minutes = models.PositiveIntegerField(
        default=90,
        verbose_name="زمان تشخیص اجرای گیرکرده به دقیقه",
    )
    homepage_slider_count = models.PositiveSmallIntegerField(
        default=10,
        verbose_name="تعداد مدل در اسلایدر صفحه اول",
    )
    homepage_grid_count = models.PositiveSmallIntegerField(
        default=12,
        verbose_name="تعداد مدل در شبکه صفحه اول",
    )
    last_queue_scan_at = models.DateTimeField(blank=True, null=True, verbose_name="آخرین بررسی زمان‌بندی")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات اتوماسیون کاتالوگ"
        verbose_name_plural = "تنظیمات اتوماسیون کاتالوگ"

    def save(self, *args, **kwargs):
        self.pk = 1
        return super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "تنظیمات اتوماسیون کاتالوگ"


class CatalogSourceSchedule(models.Model):
    WEEKDAY_HELP = "روزهای هفته با عدد 0 تا 6 و جداشده با ویرگول؛ 0 دوشنبه و 6 یکشنبه است. برای هر روز: 0,1,2,3,4,5,6"

    policy = models.OneToOneField(
        CatalogSourcePolicy,
        on_delete=models.CASCADE,
        related_name="schedule",
        verbose_name="سیاست منبع",
    )
    enabled = models.BooleanField(default=False, db_index=True, verbose_name="اجرای روزانه فعال")
    run_time = models.TimeField(
        default=time(3, 30),
        verbose_name="ساعت اجرای روزانه",
        help_text="زمان بر اساس منطقه زمانی تنظیم‌شده در اتوماسیون تفسیر می‌شود.",
    )
    weekdays = models.CharField(
        max_length=30,
        default="0,1,2,3,4,5,6",
        verbose_name="روزهای اجرا",
        help_text=WEEKDAY_HELP,
    )
    sort_mode = models.CharField(
        max_length=20,
        choices=CatalogSyncRun.SORT_CHOICES,
        default="downloads",
        verbose_name="مرتب‌سازی دریافت",
    )
    requested_limit = models.PositiveIntegerField(
        default=200,
        verbose_name="تعداد مدل در هر اجرا",
        help_text="این مقدار از سقف تعیین‌شده در سیاست منبع بیشتر نمی‌شود.",
    )
    hydrate_files = models.BooleanField(
        default=False,
        verbose_name="دریافت جزئیات فایل‌ها",
        help_text="برای Thingiverse نیازمند API رسمی است. فایل‌ها برای مشتری قابل دانلود نیستند.",
    )
    auto_approve_commercial = models.BooleanField(
        default=False,
        verbose_name="تأیید خودکار مجوزهای تجاری صریح",
        help_text="فقط وقتی Adapter به‌طور صریح اجازه فروش چاپ فیزیکی را تشخیص دهد اعمال می‌شود.",
    )
    cache_images_after_approval = models.BooleanField(
        default=True,
        verbose_name="ذخیره تصویر محلی پس از تأیید",
    )
    show_approved_on_homepage = models.BooleanField(
        default=True,
        verbose_name="نمایش مدل‌های تأییدشده در صفحه اول",
    )
    last_queued_on = models.DateField(blank=True, null=True, verbose_name="آخرین روز صف‌شدن")
    last_completed_at = models.DateTimeField(blank=True, null=True, verbose_name="آخرین اجرای موفق")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "زمان‌بندی دریافت منبع"
        verbose_name_plural = "زمان‌بندی دریافت منابع"

    def __str__(self):
        return f"{self.policy.source.name} - {self.run_time}"

    def active_weekdays(self):
        result = set()
        for item in (self.weekdays or "").split(","):
            try:
                value = int(item.strip())
            except (TypeError, ValueError):
                continue
            if 0 <= value <= 6:
                result.add(value)
        return result


class CatalogQueuedJob(models.Model):
    TRIGGER_CHOICES = [
        ("manual", "دستی از پنل"),
        ("scheduled", "زمان‌بندی‌شده"),
        ("command", "خط فرمان"),
    ]

    run = models.OneToOneField(CatalogSyncRun, on_delete=models.CASCADE, related_name="queue_job", verbose_name="اجرای کاتالوگ")
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default="manual", db_index=True, verbose_name="نوع اجرا")
    scheduled_for = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name="زمان برنامه‌ریزی‌شده")
    hydrate_files = models.BooleanField(default=False, verbose_name="دریافت جزئیات فایل")
    attempts = models.PositiveSmallIntegerField(default=0, verbose_name="تعداد تلاش")
    claimed_at = models.DateTimeField(blank=True, null=True, verbose_name="زمان دریافت توسط Worker")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Job صف همگام‌سازی"
        verbose_name_plural = "Jobهای صف همگام‌سازی"

    def __str__(self):
        return f"{self.run} - {self.get_trigger_display()}"


class CatalogAssetPublication(models.Model):
    metrics = models.OneToOneField(
        CatalogAssetMetrics,
        on_delete=models.CASCADE,
        related_name="publication",
        verbose_name="مدل خارجی",
    )
    seo_title = models.CharField(
        max_length=180,
        blank=True,
        verbose_name="عنوان سئو",
        help_text="اگر خالی باشد، بر اساس نام مدل و سفارش چاپ سه‌بعدی ساخته می‌شود.",
    )
    seo_description = models.CharField(
        max_length=320,
        blank=True,
        verbose_name="توضیحات متا",
    )
    image_alt_text = models.CharField(
        max_length=260,
        blank=True,
        verbose_name="متن جایگزین تصویر",
    )
    show_on_homepage = models.BooleanField(default=False, db_index=True, verbose_name="نمایش در صفحه اول")
    homepage_priority = models.PositiveIntegerField(default=100, db_index=True, verbose_name="اولویت صفحه اول")
    first_published_at = models.DateTimeField(blank=True, null=True, verbose_name="اولین انتشار")
    last_public_refresh_at = models.DateTimeField(blank=True, null=True, verbose_name="آخرین بروزرسانی عمومی")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["homepage_priority", "-metrics__downloads_count"]
        verbose_name = "انتشار و سئوی مدل خارجی"
        verbose_name_plural = "انتشار و سئوی مدل‌های خارجی"

    def __str__(self):
        return self.metrics.asset.title

    def ensure_defaults(self):
        asset = self.metrics.asset
        segment = self.metrics.get_segment_display()
        if not self.seo_title:
            self.seo_title = f"سفارش چاپ سه‌بعدی {asset.title}"[:180]
        if not self.seo_description:
            base = asset.short_description or asset.description or f"مدل آماده {segment} برای سفارش چاپ سه‌بعدی"
            self.seo_description = base.replace("\n", " ")[:320]
        if not self.image_alt_text:
            self.image_alt_text = f"مدل سه‌بعدی {asset.title} برای سفارش چاپ"[:260]

    def save(self, *args, **kwargs):
        self.ensure_defaults()
        return super().save(*args, **kwargs)


class MarketPricingSetting(models.Model):
    enabled = models.BooleanField(default=False, verbose_name="قیمت‌گذاری بازار فعال")
    refresh_fx_minutes = models.PositiveIntegerField(default=10, verbose_name="فاصله بروزرسانی ارز به دقیقه")
    refresh_bambu_hours = models.PositiveIntegerField(default=12, verbose_name="فاصله بروزرسانی Bambu Lab به ساعت")
    refresh_fx_on_public_request = models.BooleanField(
        default=True,
        verbose_name="تلاش برای بروزرسانی ارز هنگام بازدید",
        help_text="فقط وقتی داده قدیمی باشد و با قفل ضدتکرار؛ شکست منبع باعث اختلال صفحه مشتری نمی‌شود.",
    )
    use_daily_high_fx = models.BooleanField(
        default=True,
        verbose_name="استفاده از بیشترین نرخ دلار روز",
        help_text="اگر نرخ صبح بیشتر از نرخ فعلی باشد، همان بیشترین نرخ روز در محاسبه استفاده می‌شود.",
    )
    default_import_cost_percent = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="هزینه واردات و تبدیل پیش‌فرض درصدی",
    )
    default_margin_percent = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("100"),
        verbose_name="حاشیه فروش پیش‌فرض درصدی",
        help_text="۱۰۰ درصد یعنی دو برابر بهای محاسبه‌شده.",
    )
    price_rounding_toman = models.PositiveIntegerField(
        default=100,
        verbose_name="گردکردن قیمت هر گرم به تومان",
    )
    tgju_profile_url = models.URLField(
        default="https://www.tgju.org/profile/price_dollar_rl",
        verbose_name="صفحه نرخ دلار TGJU",
        help_text="صفحه عمومی دلار آزاد؛ نرخ فعلی و بالاترین نرخ روز از همین صفحه استخراج می‌شود.",
    )
    bambu_collection_url = models.URLField(
        default="https://us.store.bambulab.com/collections/all-filaments/",
        verbose_name="مجموعه فیلامنت Bambu Lab",
        help_text="مجموعه رسمی All Filaments؛ در صورت تغییر ساختار، مسیرهای رسمی جایگزین و product.js بررسی می‌شوند.",
    )
    source_timeout_seconds = models.PositiveSmallIntegerField(
        default=20,
        verbose_name="مهلت اتصال به منابع به ثانیه",
    )
    last_bambu_catalog_sync_at = models.DateTimeField(blank=True, null=True, verbose_name="آخرین همگام‌سازی مجموعه Bambu")
    last_fx_refresh_at = models.DateTimeField(blank=True, null=True)
    last_bambu_refresh_at = models.DateTimeField(blank=True, null=True)
    last_error = models.TextField(blank=True, verbose_name="آخرین خطا")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات قیمت‌گذاری بازار"
        verbose_name_plural = "تنظیمات قیمت‌گذاری بازار"

    def save(self, *args, **kwargs):
        self.pk = 1
        return super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "تنظیمات قیمت‌گذاری بازار"


class ExchangeRateProvider(models.Model):
    PROVIDER_CHOICES = [
        ("manual", "ثبت دستی"),
        ("bonbast", "Bonbast API"),
        ("generic_json", "JSON API عمومی/اختصاصی"),
        ("tgju_html", "صفحه عمومی TGJU"),
    ]
    UNIT_CHOICES = [("toman", "تومان"), ("rial", "ریال")]

    name = models.CharField(max_length=120, verbose_name="نام منبع")
    code = models.SlugField(max_length=60, unique=True, verbose_name="کد")
    provider_type = models.CharField(max_length=30, choices=PROVIDER_CHOICES, default="manual", verbose_name="نوع منبع")
    endpoint_url = models.URLField(blank=True, verbose_name="آدرس منبع / API")
    username_env = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="نام متغیر محیطی نام کاربری",
        help_text="برای Bonbast مانند BONBAST_USERNAME؛ مقدار محرمانه در دیتابیس ذخیره نمی‌شود.",
    )
    secret_env = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="نام متغیر محیطی کلید",
        help_text="برای Bonbast مانند BONBAST_API_KEY.",
    )
    json_sell_path = models.CharField(
        max_length=200,
        default="usd1",
        verbose_name="مسیر نرخ فروش در JSON",
        help_text="نمونه: result.usd.sell یا usd1",
    )
    response_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="toman", verbose_name="واحد پاسخ")
    multiplier = models.DecimalField(max_digits=12, decimal_places=4, default=1, verbose_name="ضریب اصلاح")
    manual_sell_rate_toman = models.PositiveBigIntegerField(default=0, verbose_name="نرخ فروش دستی دلار به تومان")
    timeout_seconds = models.PositiveSmallIntegerField(default=8, verbose_name="مهلت پاسخ ثانیه")
    priority = models.PositiveSmallIntegerField(default=10, db_index=True, verbose_name="اولویت")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    last_success_at = models.DateTimeField(blank=True, null=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "id"]
        verbose_name = "منبع نرخ ارز"
        verbose_name_plural = "منابع نرخ ارز"

    def __str__(self):
        return self.name


class ExchangeRateSnapshot(models.Model):
    provider = models.ForeignKey(ExchangeRateProvider, on_delete=models.PROTECT, related_name="snapshots", verbose_name="منبع")
    currency = models.CharField(max_length=10, default="USD", db_index=True)
    sell_rate_toman = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="نرخ فروش به تومان")
    observed_at = models.DateTimeField(default=timezone.now, db_index=True)
    local_date = models.DateField(db_index=True, verbose_name="تاریخ محلی")
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-observed_at"]
        indexes = [models.Index(fields=["currency", "local_date", "-sell_rate_toman"], name="store_fx_day_high_idx")]
        verbose_name = "نمونه نرخ ارز"
        verbose_name_plural = "تاریخچه نرخ ارز"

    def __str__(self):
        return f"{self.currency} {self.sell_rate_toman} - {self.observed_at}"


class MaterialMarketPriceSnapshot(models.Model):
    material = models.ForeignKey("website.Material", on_delete=models.CASCADE, related_name="market_price_snapshots", verbose_name="متریال")
    bambu_usd_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="قیمت دلاری Bambu")
    fx_current_toman = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="نرخ فعلی دلار")
    fx_daily_high_toman = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="بیشترین نرخ دلار روز")
    cost_per_gram_toman = models.DecimalField(max_digits=16, decimal_places=2, verbose_name="بهای محاسباتی هر گرم")
    sale_per_gram_toman = models.PositiveBigIntegerField(verbose_name="قیمت فروش هر گرم")
    observed_at = models.DateTimeField(default=timezone.now, db_index=True)
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-observed_at"]
        verbose_name = "تاریخچه قیمت متریال"
        verbose_name_plural = "تاریخچه قیمت متریال‌ها"

    def __str__(self):
        return f"{self.material} - {self.sale_per_gram_toman} تومان/گرم"


class CatalogAutomationDashboard(CatalogSourceSchedule):
    class Meta:
        proxy = True
        verbose_name = "داشبورد همگام‌سازی و قیمت زنده"
        verbose_name_plural = "داشبورد همگام‌سازی و قیمت زنده"

# END PHASE 10 AUTOMATION PRICING AND HOMEPAGE MODELS

# BEGIN PHASE 11 SOURCE HEALTH AND BAMBU CATALOG
class ExternalSourceFetchLog(models.Model):
    SOURCE_CHOICES = [
        ("tgju", "TGJU نرخ دلار"),
        ("bambu", "Bambu Lab"),
        ("makerworld", "MakerWorld"),
        ("printables", "Printables"),
        ("thingiverse", "Thingiverse"),
        ("grabcad", "GrabCAD"),
        ("fx", "سایر منابع ارز"),
    ]
    ACTION_CHOICES = [
        ("test", "تست اتصال و پارسر"),
        ("fetch_rate", "دریافت نرخ"),
        ("sync", "همگام‌سازی"),
        ("catalog_probe", "تست دریافت مدل"),
    ]
    STATUS_CHOICES = [
        ("queued", "در صف"),
        ("running", "در حال اجرا"),
        ("success", "موفق"),
        ("partial", "نسبی"),
        ("failed", "ناموفق"),
        ("cancelled", "متوقف‌شده"),
    ]
    source_key = models.CharField(max_length=30, choices=SOURCE_CHOICES, db_index=True, verbose_name="منبع")
    action = models.CharField(max_length=30, choices=ACTION_CHOICES, db_index=True, verbose_name="عملیات")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued", db_index=True, verbose_name="وضعیت")
    progress_percent = models.PositiveSmallIntegerField(default=0, verbose_name="پیشرفت درصدی")
    current_stage = models.CharField(max_length=160, blank=True, verbose_name="مرحله فعلی")
    message = models.TextField(blank=True, verbose_name="پیام نتیجه")
    error = models.TextField(blank=True, verbose_name="جزئیات خطا")
    http_status = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="HTTP Status")
    duration_ms = models.PositiveIntegerField(default=0, verbose_name="مدت اجرا میلی‌ثانیه")
    records_found = models.PositiveIntegerField(default=0, verbose_name="رکورد پیدا شده")
    records_saved = models.PositiveIntegerField(default=0, verbose_name="رکورد جدید")
    records_updated = models.PositiveIntegerField(default=0, verbose_name="رکورد بروزشده")
    records_failed = models.PositiveIntegerField(default=0, verbose_name="رکورد ناموفق")
    details = models.JSONField(default=dict, blank=True, verbose_name="خلاصه فنی")
    started_at = models.DateTimeField(blank=True, null=True, verbose_name="شروع")
    finished_at = models.DateTimeField(blank=True, null=True, verbose_name="پایان")
    deadline_at = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name="مهلت پایان")
    heartbeat_at = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name="آخرین فعالیت")
    cancelled_at = models.DateTimeField(blank=True, null=True, verbose_name="زمان توقف دستی")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="external_source_logs", verbose_name="اجراکننده")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "گزارش دریافت منبع"
        verbose_name_plural = "گزارش‌های دریافت و تست منابع"

    def __str__(self):
        return f"{self.get_source_key_display()} - {self.get_status_display()}"


class BambuFilamentCatalogItem(models.Model):
    external_id = models.CharField(max_length=120, blank=True, db_index=True, verbose_name="شناسه Bambu")
    handle = models.SlugField(max_length=220, unique=True, verbose_name="Handle محصول")
    title = models.CharField(max_length=220, verbose_name="نام فیلامنت")
    product_url = models.URLField(max_length=1000, verbose_name="لینک رسمی محصول")
    image_url = models.URLField(max_length=1000, blank=True, verbose_name="تصویر رسمی")
    vendor = models.CharField(max_length=120, blank=True, verbose_name="برند")
    product_type = models.CharField(max_length=120, blank=True, verbose_name="نوع محصول")
    tags = models.JSONField(default=list, blank=True, verbose_name="برچسب‌ها")
    min_price_usd = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="کمترین قیمت دلار")
    max_price_usd = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="بیشترین قیمت دلار")
    conservative_price_usd = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="قیمت محافظه‌کارانه")
    available = models.BooleanField(default=True, db_index=True, verbose_name="موجود")
    variants = models.JSONField(default=list, blank=True, verbose_name="تنوع‌ها و قیمت‌ها")
    raw_payload = models.JSONField(default=dict, blank=True, verbose_name="داده خام")
    last_seen_at = models.DateTimeField(default=timezone.now, db_index=True, verbose_name="آخرین مشاهده")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title", "id"]
        verbose_name = "قیمت فیلامنت Bambu"
        verbose_name_plural = "کاتالوگ قیمت فیلامنت‌های Bambu Lab"

    def __str__(self):
        return f"{self.title} - ${self.conservative_price_usd}"
# END PHASE 11 SOURCE HEALTH AND BAMBU CATALOG

# BEGIN PHASE 12 RESILIENT SOURCE MODELS
class CatalogSeedURL(models.Model):
    source = models.ForeignKey(
        PrintCatalogSource,
        on_delete=models.CASCADE,
        related_name="seed_urls",
        verbose_name="منبع",
    )
    url = models.URLField(max_length=1200, verbose_name="لینک عمومی مدل")
    label = models.CharField(max_length=220, blank=True, verbose_name="عنوان داخلی")
    priority = models.PositiveIntegerField(default=100, db_index=True, verbose_name="اولویت")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    last_status = models.CharField(max_length=30, blank=True, verbose_name="آخرین وضعیت")
    last_error = models.TextField(blank=True, verbose_name="آخرین خطا")
    last_checked_at = models.DateTimeField(blank=True, null=True, verbose_name="آخرین بررسی")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "id"]
        constraints = [
            models.UniqueConstraint(fields=["source", "url"], name="store_seed_source_url_uniq"),
        ]
        verbose_name = "لینک بذر کاتالوگ"
        verbose_name_plural = "لینک‌های بذر و نمونه منابع"

    def __str__(self):
        return self.label or self.url
# END PHASE 12 RESILIENT SOURCE MODELS

# BEGIN PHASE 16 BAMBU PRICE HISTORY
class BambuFilamentPriceHistory(models.Model):
    item = models.ForeignKey(
        "BambuFilamentCatalogItem",
        on_delete=models.CASCADE,
        related_name="price_history",
        verbose_name="محصول Bambu",
    )
    observed_at = models.DateTimeField(default=timezone.now, db_index=True, verbose_name="زمان مشاهده")
    min_price_usd = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="کمترین قیمت جدید")
    max_price_usd = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="بیشترین قیمت جدید")
    conservative_price_usd = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="قیمت جدید")
    previous_conservative_price_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="قیمت قبلی",
    )
    delta_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="تغییر دلاری")
    delta_percent = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name="درصد تغییر")
    available = models.BooleanField(default=True, db_index=True, verbose_name="موجود")
    changed = models.BooleanField(default=False, db_index=True, verbose_name="قیمت تغییر کرده")
    source_mode = models.CharField(max_length=80, blank=True, verbose_name="روش دریافت")
    variants = models.JSONField(default=list, blank=True, verbose_name="تنوع‌ها و قیمت‌ها")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-observed_at", "-id"]
        verbose_name = "تاریخچه قیمت Bambu"
        verbose_name_plural = "تاریخچه قیمت‌های Bambu Lab"
        indexes = [
            models.Index(fields=["item", "-observed_at"], name="store_bambu_hist_item_idx"),
            models.Index(fields=["changed", "-observed_at"], name="store_bambu_hist_chg_idx"),
        ]

    def __str__(self):
        return f"{self.item.title}: ${self.previous_conservative_price_usd or '-'} → ${self.conservative_price_usd}"
# END PHASE 16 BAMBU PRICE HISTORY

# BEGIN PHASE 17 CATALOG PREVIEW AND PRINT PROFILES
class ImportedPrintAssetPrintProfile(models.Model):
    asset = models.ForeignKey(
        "ImportedPrintAsset",
        on_delete=models.CASCADE,
        related_name="print_profiles",
        verbose_name="مدل دریافت‌شده",
    )
    source_key = models.CharField(max_length=160, blank=True, verbose_name="شناسه پروفایل منبع")
    profile_name = models.CharField(max_length=220, default="پروفایل چاپ", verbose_name="نام پروفایل")
    weight_grams = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="وزن چاپ (گرم)",
    )
    print_minutes = models.PositiveIntegerField(blank=True, null=True, verbose_name="زمان چاپ (دقیقه)")
    material = models.CharField(max_length=120, blank=True, verbose_name="متریال پیشنهادی")
    nozzle_mm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="نازل (میلی‌متر)")
    layer_height_mm = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True, verbose_name="ارتفاع لایه")
    infill_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="درصد پرشدگی")
    source_payload = models.JSONField(default=dict, blank=True, verbose_name="داده خام پروفایل")
    is_manual = models.BooleanField(default=False, db_index=True, verbose_name="ثبت دستی")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["weight_grams", "profile_name", "id"]
        verbose_name = "وزن و پروفایل چاپ"
        verbose_name_plural = "وزن‌ها و پروفایل‌های چاپ مدل‌ها"
        constraints = [
            models.UniqueConstraint(
                fields=["asset", "source_key"],
                condition=~models.Q(source_key=""),
                name="store_asset_profile_source_key_uniq",
            )
        ]

    def __str__(self):
        weight = f"{self.weight_grams} گرم" if self.weight_grams is not None else "وزن نامشخص"
        return f"{self.asset.title} — {self.profile_name} — {weight}"
# END PHASE 17 CATALOG PREVIEW AND PRINT PROFILES


# BEGIN PHASE 29 VERIFIED CATALOG PRICING
class CatalogPricingReview(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار تکمیل اپراتور"),
        ("verified", "وزن و زمان تأیید شده"),
        ("rejected", "غیرقابل قیمت‌گذاری"),
    ]
    asset = models.OneToOneField(
        "ImportedPrintAsset", on_delete=models.CASCADE, related_name="pricing_review",
        verbose_name="مدل کاتالوگ",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True, verbose_name="وضعیت")
    material = models.ForeignKey(
        "website.Material", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="catalog_pricing_reviews", verbose_name="متریال تأییدشده",
    )
    weight_grams = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="وزن تأییدشده گرم")
    print_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name="زمان واقعی چاپ دقیقه")
    price_override = models.PositiveBigIntegerField(default=0, verbose_name="قیمت قطعی دستی (اختیاری)")
    operator_note = models.TextField(blank=True, verbose_name="یادداشت اپراتور")
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="verified_catalog_prices", verbose_name="اپراتور تأییدکننده",
    )
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان تأیید")
    notification_sent_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان اعلان به اپراتور")
    notification_error = models.TextField(blank=True, verbose_name="خطای اعلان")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "-updated_at"]
        verbose_name = "قیمت‌گذاری اپراتوری مدل"
        verbose_name_plural = "صف قیمت‌گذاری اپراتوری مدل‌ها"

    def __str__(self):
        return f"{self.asset.title} - {self.get_status_display()}"

    @property
    def is_complete(self):
        return bool(self.status == "verified" and self.material_id and self.weight_grams and self.print_minutes)
# END PHASE 29 VERIFIED CATALOG PRICING


# BEGIN PHASE 23 RESILIENT CATALOG AND LINK INTELLIGENCE
class CatalogRefreshRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("running", "در حال بروزرسانی"),
        ("completed", "بروزرسانی شد"),
        ("failed", "ناموفق"),
    ]

    asset = models.ForeignKey(
        ImportedPrintAsset,
        on_delete=models.CASCADE,
        related_name="refresh_requests",
        verbose_name="مدل خارجی",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="catalog_refresh_requests",
        verbose_name="درخواست‌کننده",
    )
    session_key = models.CharField(max_length=80, blank=True, db_index=True, verbose_name="شناسه نشست")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True, verbose_name="وضعیت")
    customer_note = models.CharField(max_length=500, blank=True, verbose_name="توضیح مشتری")
    result_summary = models.TextField(blank=True, verbose_name="نتیجه بروزرسانی")
    requested_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="زمان درخواست")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان پردازش")

    class Meta:
        ordering = ["-requested_at", "-id"]
        verbose_name = "درخواست بروزرسانی مدل خارجی"
        verbose_name_plural = "درخواست‌های بروزرسانی مدل‌های خارجی"
        indexes = [models.Index(fields=["status", "requested_at"], name="store_cat_refresh_q_idx")]

    def __str__(self):
        return f"{self.asset.title} - {self.get_status_display()}"


class CustomerLinkAnalysis(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار تحلیل"),
        ("processing", "در حال تحلیل"),
        ("ready", "آماده برآورد"),
        ("needs_input", "نیازمند اطلاعات تکمیلی"),
        ("partial", "اطلاعات ناقص دریافت شد"),
        ("failed", "تحلیل ناموفق"),
        ("converted", "تبدیل‌شده به سفارش"),
    ]

    public_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="شناسه عمومی")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="external_link_analyses",
        verbose_name="مشتری",
    )
    session_key = models.CharField(max_length=80, blank=True, db_index=True, verbose_name="شناسه نشست")
    source_url = models.URLField(max_length=2000, verbose_name="لینک ارسالی مشتری")
    normalized_url = models.URLField(max_length=2000, db_index=True, verbose_name="لینک نرمال‌شده")
    source_domain = models.CharField(max_length=255, db_index=True, verbose_name="دامنه منبع")
    source_name = models.CharField(max_length=255, blank=True, verbose_name="نام سایت منبع")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True, verbose_name="وضعیت")

    title = models.CharField(max_length=300, blank=True, verbose_name="نام محصول یا فایل")
    short_description = models.CharField(max_length=700, blank=True, verbose_name="توضیح کوتاه")
    description = models.TextField(blank=True, verbose_name="توضیحات استخراج‌شده")
    author_name = models.CharField(max_length=220, blank=True, verbose_name="طراح یا فروشنده")
    image_url = models.URLField(max_length=2000, blank=True, verbose_name="تصویر اصلی منبع")
    cached_image = models.ImageField(upload_to="store/link-analysis/previews/", blank=True, null=True, verbose_name="تصویر ذخیره‌شده")
    image_urls = models.JSONField(default=list, blank=True, verbose_name="تصاویر استخراج‌شده")
    tags = models.JSONField(default=list, blank=True, verbose_name="برچسب‌ها")
    technical_specs = models.JSONField(default=dict, blank=True, verbose_name="مشخصات فنی")
    file_formats = models.JSONField(default=list, blank=True, verbose_name="فرمت‌های شناسایی‌شده")
    file_links = models.JSONField(default=list, blank=True, verbose_name="لینک فایل‌ها فقط برای ادمین")
    source_payload = models.JSONField(default=dict, blank=True, verbose_name="داده خام امن‌شده")

    detected_material_name = models.CharField(max_length=120, blank=True, verbose_name="متریال تشخیص‌داده‌شده")
    material = models.ForeignKey(
        "website.Material",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="link_analyses",
        verbose_name="متریال برآورد",
    )
    estimated_weight_grams = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="وزن تخمینی گرم")
    estimated_print_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name="زمان تخمینی چاپ دقیقه")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    estimate_confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="اعتماد برآورد درصد")
    estimated_price = models.PositiveBigIntegerField(default=0, verbose_name="قیمت میانی تخمینی تومان")
    estimated_price_min = models.PositiveBigIntegerField(default=0, verbose_name="حداقل قیمت تخمینی تومان")
    estimated_price_max = models.PositiveBigIntegerField(default=0, verbose_name="حداکثر قیمت تخمینی تومان")
    estimate_breakdown = models.JSONField(default=dict, blank=True, verbose_name="جزئیات برآورد")
    analysis_warnings = models.JSONField(default=list, blank=True, verbose_name="هشدارهای تحلیل")
    error_message = models.TextField(blank=True, verbose_name="خطای تحلیل")

    related_asset = models.ForeignKey(
        ImportedPrintAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_link_analyses",
        verbose_name="مدل خارجی مرتبط",
    )
    order = models.OneToOneField(
        "website.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_link_analysis",
        verbose_name="سفارش ساخته‌شده",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    analyzed_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان تحلیل")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "تحلیل لینک محصول مشتری"
        verbose_name_plural = "تحلیل لینک‌های محصولات مشتریان"
        indexes = [
            models.Index(fields=["status", "-created_at"], name="store_link_status_idx"),
            models.Index(fields=["source_domain", "-created_at"], name="store_link_domain_idx"),
        ]

    def __str__(self):
        return self.title or self.normalized_url

    @property
    def display_image_url(self):
        if self.cached_image:
            try:
                return self.cached_image.url
            except Exception:
                pass
        return self.image_url or next((url for url in (self.image_urls or []) if url), "")

    @property
    def pricing_sources(self):
        specs = self.technical_specs or {}
        return {
            "weight": str(specs.get("weight_source_kind") or "unknown"),
            "time": str(specs.get("print_time_source_kind") or "unknown"),
        }

    @property
    def has_authoritative_pricing_inputs(self):
        allowed = {"source_explicit", "source_profile", "operator_verified"}
        sources = self.pricing_sources
        return bool(
            self.material_id and self.estimated_weight_grams and self.estimated_print_minutes
            and sources["weight"] in allowed and sources["time"] in allowed
        )

    @property
    def pricing_locked(self):
        return self.pricing_sources["weight"] == "operator_verified" and self.pricing_sources["time"] == "operator_verified"

    @property
    def can_estimate(self):
        return self.has_authoritative_pricing_inputs

    @property
    def can_convert_to_order(self):
        return self.status in {"ready", "needs_input", "partial"} and self.can_estimate and not self.order_id

    @property
    def can_request_manual_quote(self):
        return not self.order_id and self.status != "converted"
# END PHASE 23 RESILIENT CATALOG AND LINK INTELLIGENCE

# BEGIN PHASE 24 ASYNC LINK ANALYSIS QUEUE
class CustomerLinkAnalysisJob(models.Model):
    STATUS_CHOICES = [
        ("queued", "در صف"),
        ("running", "در حال پردازش"),
        ("retry", "در انتظار تلاش مجدد"),
        ("completed", "تکمیل‌شده"),
        ("failed", "ناموفق"),
        ("cancelled", "لغوشده"),
    ]

    analysis = models.OneToOneField(
        CustomerLinkAnalysis,
        on_delete=models.CASCADE,
        related_name="job",
        verbose_name="تحلیل لینک",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="queued",
        db_index=True,
        verbose_name="وضعیت صف",
    )
    priority = models.SmallIntegerField(default=100, db_index=True, verbose_name="اولویت")
    adapter_key = models.CharField(max_length=40, default="generic", db_index=True, verbose_name="Adapter تحلیل")
    attempt_count = models.PositiveSmallIntegerField(default=0, verbose_name="تعداد تلاش")
    max_attempts = models.PositiveSmallIntegerField(default=4, verbose_name="حداکثر تلاش")
    next_run_at = models.DateTimeField(default=timezone.now, db_index=True, verbose_name="زمان اجرای بعدی")
    locked_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="زمان قفل")
    worker_id = models.CharField(max_length=180, blank=True, verbose_name="شناسه Worker")
    progress_percent = models.PositiveSmallIntegerField(default=0, verbose_name="درصد پیشرفت")
    progress_stage = models.CharField(max_length=80, blank=True, verbose_name="مرحله فعلی")
    progress_message = models.CharField(max_length=300, blank=True, verbose_name="پیام پیشرفت")
    last_error_type = models.CharField(max_length=160, blank=True, verbose_name="نوع آخرین خطا")
    last_error = models.TextField(blank=True, verbose_name="آخرین خطا")
    last_started_at = models.DateTimeField(null=True, blank=True, verbose_name="شروع آخرین تلاش")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان تکمیل")
    success_notified_at = models.DateTimeField(null=True, blank=True, verbose_name="اعلان موفقیت ارسال شد")
    failure_notified_at = models.DateTimeField(null=True, blank=True, verbose_name="اعلان شکست ارسال شد")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "next_run_at", "id"]
        verbose_name = "صف تحلیل لینک مشتری"
        verbose_name_plural = "صف تحلیل لینک‌های مشتریان"
        indexes = [
            models.Index(fields=["status", "next_run_at", "-priority"], name="store_link_job_queue_idx"),
            models.Index(fields=["status", "locked_at"], name="store_link_job_lock_idx"),
        ]

    def __str__(self):
        return f"#{self.pk} - {self.analysis} - {self.get_status_display()}"

    @property
    def is_terminal(self):
        return self.status in {"completed", "failed", "cancelled"}

    @property
    def attempts_remaining(self):
        return max(int(self.max_attempts or 0) - int(self.attempt_count or 0), 0)


class CustomerLinkAnalysisAttempt(models.Model):
    STATUS_CHOICES = [
        ("running", "در حال اجرا"),
        ("success", "موفق"),
        ("transient_failure", "خطای موقت"),
        ("permanent_failure", "خطای قطعی"),
    ]

    job = models.ForeignKey(
        CustomerLinkAnalysisJob,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Job تحلیل",
    )
    attempt_number = models.PositiveSmallIntegerField(verbose_name="شماره تلاش")
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default="running", db_index=True)
    stage = models.CharField(max_length=80, blank=True, verbose_name="آخرین مرحله")
    error_type = models.CharField(max_length=160, blank=True, verbose_name="نوع خطا")
    error_message = models.TextField(blank=True, verbose_name="متن خطا")
    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveBigIntegerField(default=0, verbose_name="مدت اجرا میلی‌ثانیه")
    worker_id = models.CharField(max_length=180, blank=True, verbose_name="شناسه Worker")

    class Meta:
        ordering = ["-started_at", "-id"]
        verbose_name = "تلاش تحلیل لینک"
        verbose_name_plural = "تلاش‌های تحلیل لینک"
        constraints = [
            models.UniqueConstraint(fields=["job", "attempt_number"], name="store_link_attempt_unique"),
        ]
        indexes = [
            models.Index(fields=["job", "-started_at"], name="store_link_attempt_job_idx"),
            models.Index(fields=["status", "-started_at"], name="store_link_attempt_status_idx"),
        ]

    def __str__(self):
        return f"Job {self.job_id} / Attempt {self.attempt_number}"
# END PHASE 24 ASYNC LINK ANALYSIS QUEUE

# BEGIN PHASE 25 PRODUCTION LINK WORKER AND OPERATIONS
class LinkAnalysisQueueControl(models.Model):
    singleton_key = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)
    is_paused = models.BooleanField(default=False, db_index=True, verbose_name="توقف سراسری صف")
    pause_reason = models.CharField(max_length=300, blank=True, verbose_name="دلیل توقف")
    heartbeat_timeout_seconds = models.PositiveIntegerField(default=90, verbose_name="مهلت سلامت Worker ثانیه")
    stale_lock_minutes = models.PositiveSmallIntegerField(default=15, verbose_name="مهلت آزادسازی قفل دقیقه")
    default_batch_size = models.PositiveSmallIntegerField(default=3, verbose_name="تعداد Job در هر چرخه")
    default_sleep_seconds = models.PositiveSmallIntegerField(default=3, verbose_name="فاصله چرخه Worker ثانیه")
    notify_customer_on_success = models.BooleanField(default=True, verbose_name="اعلان موفقیت به مشتری")
    notify_customer_on_failure = models.BooleanField(default=True, verbose_name="اعلان خطای نهایی به مشتری")
    email_customer_on_success = models.BooleanField(default=False, verbose_name="ایمیل موفقیت به مشتری")
    email_customer_on_failure = models.BooleanField(default=False, verbose_name="ایمیل خطای نهایی به مشتری")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_link_queue_controls",
        verbose_name="آخرین ویرایش‌کننده",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات صف تحلیل لینک"
        verbose_name_plural = "تنظیمات صف تحلیل لینک"

    def save(self, *args, **kwargs):
        self.singleton_key = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(singleton_key=1)
        return obj

    def __str__(self):
        return "تنظیمات صف تحلیل لینک"


class LinkAnalysisAdapterPolicy(models.Model):
    ADAPTER_CHOICES = [
        ("makerworld", "MakerWorld"),
        ("printables", "Printables"),
        ("thingiverse", "Thingiverse"),
        ("grabcad", "GrabCAD"),
        ("direct_file", "لینک مستقیم فایل"),
        ("generic", "تحلیل عمومی وب"),
    ]

    adapter_key = models.CharField(max_length=40, choices=ADAPTER_CHOICES, unique=True, db_index=True, verbose_name="Adapter")
    display_name = models.CharField(max_length=120, blank=True, verbose_name="نام نمایشی")
    domain_patterns = models.JSONField(default=list, blank=True, verbose_name="دامنه‌های منطبق")
    is_enabled = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    paused_until = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="توقف تا")
    priority_override = models.SmallIntegerField(null=True, blank=True, verbose_name="اولویت جایگزین")
    max_attempts = models.PositiveSmallIntegerField(default=4, verbose_name="حداکثر تلاش")
    retry_delays_seconds = models.JSONField(default=list, blank=True, verbose_name="فواصل Retry ثانیه")
    request_timeout_seconds = models.PositiveSmallIntegerField(default=20, verbose_name="مهلت دریافت صفحه ثانیه")
    cache_remote_images = models.BooleanField(default=True, verbose_name="ذخیره تصویر منبع")
    notify_on_success = models.BooleanField(default=True, verbose_name="اعلان موفقیت")
    notify_on_failure = models.BooleanField(default=True, verbose_name="اعلان شکست")
    success_count = models.PositiveBigIntegerField(default=0, verbose_name="تعداد موفق")
    failure_count = models.PositiveBigIntegerField(default=0, verbose_name="تعداد ناموفق")
    consecutive_failure_count = models.PositiveIntegerField(default=0, verbose_name="خطاهای پیاپی")
    last_success_at = models.DateTimeField(null=True, blank=True, verbose_name="آخرین موفقیت")
    last_failure_at = models.DateTimeField(null=True, blank=True, verbose_name="آخرین شکست")
    last_error = models.TextField(blank=True, verbose_name="آخرین خطا")
    notes = models.TextField(blank=True, verbose_name="یادداشت اجرایی")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["adapter_key"]
        verbose_name = "سیاست Adapter تحلیل لینک"
        verbose_name_plural = "سیاست‌های Adapter تحلیل لینک"

    def __str__(self):
        return self.display_name or self.get_adapter_key_display()

    @property
    def is_available(self):
        return bool(self.is_enabled and (self.paused_until is None or self.paused_until <= timezone.now()))


class LinkAnalysisWorkerHeartbeat(models.Model):
    STATUS_CHOICES = [
        ("starting", "در حال شروع"),
        ("idle", "آماده"),
        ("running", "در حال پردازش"),
        ("stopping", "در حال توقف"),
        ("stopped", "متوقف"),
        ("error", "خطا"),
    ]

    worker_id = models.CharField(max_length=180, unique=True, db_index=True, verbose_name="شناسه Worker")
    hostname = models.CharField(max_length=180, blank=True, verbose_name="نام میزبان")
    process_id = models.PositiveIntegerField(default=0, verbose_name="PID")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="starting", db_index=True, verbose_name="وضعیت")
    current_job = models.ForeignKey(
        CustomerLinkAnalysisJob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="worker_heartbeats",
        verbose_name="Job فعلی",
    )
    started_at = models.DateTimeField(default=timezone.now, db_index=True, verbose_name="زمان شروع")
    last_seen_at = models.DateTimeField(default=timezone.now, db_index=True, verbose_name="آخرین Heartbeat")
    stopped_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان توقف")
    loop_count = models.PositiveBigIntegerField(default=0, verbose_name="تعداد چرخه")
    processed_count = models.PositiveBigIntegerField(default=0, verbose_name="کل پردازش")
    succeeded_count = models.PositiveBigIntegerField(default=0, verbose_name="موفق")
    failed_count = models.PositiveBigIntegerField(default=0, verbose_name="ناموفق")
    last_error = models.TextField(blank=True, verbose_name="آخرین خطا")
    worker_version = models.CharField(max_length=40, default="phase25", verbose_name="نسخه Worker")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="اطلاعات اجرا")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_seen_at", "worker_id"]
        verbose_name = "Heartbeat Worker تحلیل لینک"
        verbose_name_plural = "Heartbeatهای Worker تحلیل لینک"
        indexes = [
            models.Index(fields=["status", "-last_seen_at"], name="store_link_worker_health_idx"),
        ]

    def __str__(self):
        return f"{self.worker_id} - {self.get_status_display()}"

    def is_alive(self, timeout_seconds=None):
        timeout = int(timeout_seconds or LinkAnalysisQueueControl.load().heartbeat_timeout_seconds or 90)
        return self.status in {"starting", "idle", "running"} and self.last_seen_at >= timezone.now() - timedelta(seconds=timeout)


class LinkAnalysisOperationsDashboard(CustomerLinkAnalysisJob):
    class Meta:
        proxy = True
        verbose_name = "داشبورد عملیات تحلیل لینک"
        verbose_name_plural = "داشبورد عملیات تحلیل لینک"
# END PHASE 25 PRODUCTION LINK WORKER AND OPERATIONS


# BEGIN PHASE 26 REALTIME AND MANUAL REVIEW
class LinkAnalysisManualReview(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("in_progress", "در حال بررسی"),
        ("resolved", "حل‌شده"),
        ("rejected", "ردشده"),
        ("cancelled", "لغوشده"),
    ]
    REASON_CHOICES = [
        ("auto_failed", "شکست تحلیل خودکار"),
        ("customer_request", "درخواست مشتری"),
        ("admin_escalation", "ارجاع مدیریت"),
        ("adapter_blocked", "محدودیت منبع"),
        ("incomplete_data", "اطلاعات ناقص"),
    ]
    RESOLUTION_CHOICES = [
        ("", "بدون اقدام نهایی"),
        ("retry", "تحلیل مجدد"),
        ("data_completed", "تکمیل دستی اطلاعات"),
        ("customer_contacted", "ارتباط با مشتری"),
        ("rejected", "غیرقابل پردازش"),
        ("no_action", "بدون اقدام"),
    ]

    analysis = models.ForeignKey(
        CustomerLinkAnalysis,
        on_delete=models.CASCADE,
        related_name="manual_reviews",
        verbose_name="تحلیل لینک",
    )
    job = models.ForeignKey(
        CustomerLinkAnalysisJob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="manual_reviews",
        verbose_name="Job مرتبط",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_link_manual_reviews",
        verbose_name="درخواست‌کننده",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_link_manual_reviews",
        verbose_name="کارشناس مسئول",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True, verbose_name="وضعیت")
    reason = models.CharField(max_length=30, choices=REASON_CHOICES, default="customer_request", db_index=True, verbose_name="دلیل")
    priority = models.SmallIntegerField(default=100, db_index=True, verbose_name="اولویت")
    customer_note = models.TextField(blank=True, verbose_name="توضیح مشتری")
    reviewer_note = models.TextField(blank=True, verbose_name="یادداشت کارشناس")
    resolution_action = models.CharField(max_length=30, choices=RESOLUTION_CHOICES, blank=True, verbose_name="اقدام نهایی")
    error_snapshot = models.TextField(blank=True, verbose_name="خطای زمان ارجاع")
    source_snapshot = models.JSONField(default=dict, blank=True, verbose_name="خلاصه منبع")
    operator_material = models.ForeignKey(
        "website.Material", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="manual_link_pricing_reviews", verbose_name="متریال تأییدشده اپراتور",
    )
    operator_weight_grams = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        verbose_name="وزن قطعی اپراتور به گرم",
    )
    operator_print_minutes = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="زمان واقعی چاپ به دقیقه",
    )
    operator_price_override = models.PositiveBigIntegerField(
        default=0, verbose_name="قیمت قطعی دستی (اختیاری)",
        help_text="اگر صفر باشد، قیمت از وزن، زمان، نرخ روز متریال و تنظیمات ساعتی محاسبه می‌شود.",
    )
    operator_specs = models.JSONField(
        default=dict, blank=True, verbose_name="مشخصات تکمیلی اپراتور",
        help_text="ابعاد، نازل، ساپورت، پرشدگی، تعداد قطعات و هر نکته لازم برای چاپ.",
    )
    operator_notification_sent_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان اعلان به اپراتور")
    operator_notification_error = models.TextField(blank=True, verbose_name="خطای اعلان اپراتور")
    requested_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="زمان درخواست")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="شروع بررسی")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="پایان بررسی")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "requested_at", "id"]
        verbose_name = "بررسی دستی تحلیل لینک"
        verbose_name_plural = "صف بررسی دستی تحلیل لینک‌ها"
        indexes = [
            models.Index(fields=["status", "-priority", "requested_at"], name="store_link_review_queue_idx"),
            models.Index(fields=["analysis", "status"], name="store_link_review_analysis_idx"),
        ]

    def __str__(self):
        return f"#{self.pk} - {self.analysis} - {self.get_status_display()}"

    @property
    def is_open(self):
        return self.status in {"pending", "in_progress"}

    @property
    def operator_pricing_complete(self):
        return bool(self.operator_material_id and self.operator_weight_grams and self.operator_print_minutes)
# END PHASE 26 REALTIME AND MANUAL REVIEW
