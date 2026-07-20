from decimal import Decimal, ROUND_HALF_UP
import uuid
from django.conf import settings

from django.db import models
from django.urls import reverse

class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        verbose_name="کاربر"
    )

    phone = models.CharField(max_length=20, unique=True, verbose_name="شماره تماس")
    first_name = models.CharField(max_length=100, blank=True, verbose_name="نام")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="نام خانوادگی")
    address = models.TextField(blank=True, verbose_name="آدرس")
    company_name = models.CharField(max_length=150, blank=True, verbose_name="نام شرکت")
    national_code = models.CharField(max_length=20, blank=True, verbose_name="کد ملی / شناسه")
    # BEGIN CUSTOMER PORTAL PHASE 3 PROFILE FIELDS
    avatar = models.ImageField(
        upload_to="customers/avatars/",
        blank=True,
        null=True,
        verbose_name="تصویر پروفایل",
    )
    father_name = models.CharField(max_length=100, blank=True, verbose_name="نام پدر")
    birth_date = models.DateField(blank=True, null=True, verbose_name="تاریخ تولد")
    gender = models.CharField(
        max_length=20,
        blank=True,
        choices=[("male", "مرد"), ("female", "زن"), ("other", "سایر")],
        verbose_name="جنسیت",
    )
    landline = models.CharField(max_length=20, blank=True, verbose_name="تلفن ثابت")
    occupation = models.CharField(max_length=120, blank=True, verbose_name="شغل / سمت")
    # END CUSTOMER PORTAL PHASE 3 PROFILE FIELDS

    # BEGIN PHASE 4 CUSTOMER THEME
    theme_preference = models.CharField(
        max_length=20,
        default="original",
        choices=[("original", "رنگ‌بندی اصلی"), ("brand-gold", "طلایی و سرمه‌ای"), ("hybrid", "ترکیبی")],
        verbose_name="رنگ‌بندی انتخابی",
    )
    theme_prompt_seen = models.BooleanField(default=False, verbose_name="انتخاب رنگ نمایش داده شده")
    # END PHASE 4 CUSTOMER THEME

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ عضویت")

    class Meta:
        verbose_name = "پروفایل مشتری"
        verbose_name_plural = "پروفایل مشتریان"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone}"


class SiteSetting(models.Model):
    brand_name = models.CharField(max_length=100, default="3DprintHub.ir", verbose_name="نام برند")

    logo = models.ImageField(
        upload_to="site/",
        blank=True,
        null=True,
        verbose_name="لوگو"
    )

    primary_color = models.CharField(
        max_length=20,
        default="#38BDF8",
        verbose_name="رنگ اصلی برند"
    )
    secondary_color = models.CharField(
        max_length=20,
        default="#0F172A",
        verbose_name="رنگ دوم برند"
    )
    accent_color = models.CharField(
        max_length=20,
        default="#22C55E",
        verbose_name="رنگ تأکیدی"
    )

    hero_title = models.CharField(
        max_length=255,
        default="طراحی، چاپ سه‌بعدی و مهندسی معکوس قطعات صنعتی",
        verbose_name="عنوان اصلی سایت",
    )
    hero_subtitle = models.TextField(
        default="از نمونه‌سازی اولیه تا ساخت قطعات کاربردی صنعتی با متریال‌های مهندسی.",
        verbose_name="توضیح اصلی سایت",
    )

    phone = models.CharField(max_length=50, blank=True, verbose_name="شماره تماس")
    whatsapp = models.CharField(max_length=50, blank=True, verbose_name="شماره واتساپ")
    email = models.EmailField(blank=True, verbose_name="ایمیل")
    instagram = models.URLField(blank=True, verbose_name="لینک اینستاگرام")
    telegram = models.URLField(blank=True, verbose_name="لینک تلگرام")
    address = models.TextField(blank=True, verbose_name="آدرس")
    working_hours = models.CharField(max_length=150, blank=True, verbose_name="ساعت کاری")
    map_embed_url = models.TextField(blank=True, verbose_name="کد iframe نقشه یا لینک نقشه")

    meta_title = models.CharField(
        max_length=255,
        default="3DprintHub.ir | طراحی، چاپ سه‌بعدی و مهندسی معکوس قطعات صنعتی",
        verbose_name="عنوان سئو",
    )
    meta_description = models.TextField(
        default="خدمات طراحی سه‌بعدی، چاپ سه‌بعدی صنعتی، مهندسی معکوس و ساخت قطعات سفارشی با متریال‌های مهندسی.",
        verbose_name="توضیحات سئو",
    )

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return self.brand_name


class Material(models.Model):
    name = models.CharField(max_length=100, verbose_name="متریال")

    price_per_kg = models.PositiveIntegerField(
        default=0,
        verbose_name="قیمت هر کیلوگرم به تومان"
    )

    strength = models.PositiveSmallIntegerField(default=0, verbose_name="استحکام")
    heat_resistance = models.PositiveSmallIntegerField(default=0, verbose_name="مقاومت حرارتی")
    flexibility = models.PositiveSmallIntegerField(default=0, verbose_name="انعطاف")
    chemical_resistance = models.PositiveSmallIntegerField(default=0, verbose_name="مقاومت شیمیایی")
    printability = models.PositiveSmallIntegerField(default=0, verbose_name="سختی/سهولت چاپ")
    main_usage = models.CharField(max_length=255, verbose_name="کاربردهای اصلی")
    sample_parts = models.TextField(verbose_name="نمونه قطعات")
    is_active = models.BooleanField(default=True, verbose_name="فعال باشد؟")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "متریال"
        verbose_name_plural = "متریال‌ها"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.name

    @property
    def price_per_gram(self):
        if not self.price_per_kg:
            return 0
        return round(self.price_per_kg / 1000)


class IndustryRecommendation(models.Model):
    industry = models.CharField(max_length=150, verbose_name="صنعت")
    recommended_materials = models.CharField(max_length=255, verbose_name="متریال مناسب")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "پیشنهاد متریال برای صنعت"
        verbose_name_plural = "پیشنهاد متریال برای صنایع"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.industry


class PartRecommendation(models.Model):
    part_name = models.CharField(max_length=150, verbose_name="قطعه")
    best_material = models.CharField(max_length=150, verbose_name="بهترین متریال")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "پیشنهاد متریال برای قطعه"
        verbose_name_plural = "پیشنهاد متریال برای قطعات"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.part_name


class PortfolioItem(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان نمونه‌کار")
    category = models.CharField(max_length=100, verbose_name="دسته‌بندی")
    material = models.CharField(max_length=100, blank=True, verbose_name="متریال")
    industry = models.CharField(max_length=100, blank=True, verbose_name="صنعت")
    description = models.TextField(verbose_name="توضیحات")
    image = models.ImageField(upload_to="portfolio/", verbose_name="تصویر")
    project_duration = models.CharField(max_length=100, blank=True, verbose_name="مدت انجام")
    is_featured = models.BooleanField(default=False, verbose_name="نمایش ویژه")
    is_active = models.BooleanField(default=True, verbose_name="فعال باشد؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "نمونه‌کار"
        verbose_name_plural = "نمونه‌کارها"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    customer_name = models.CharField(max_length=150, verbose_name="نام مشتری")
    company_name = models.CharField(max_length=150, blank=True, verbose_name="نام شرکت")
    text = models.TextField(verbose_name="متن رضایت")
    rating = models.PositiveSmallIntegerField(default=5, verbose_name="امتیاز")
    image = models.ImageField(upload_to="testimonials/", blank=True, null=True, verbose_name="تصویر")
    is_active = models.BooleanField(default=True, verbose_name="فعال باشد؟")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "رضایت مشتری"
        verbose_name_plural = "رضایت مشتریان"
        ordering = ["-created_at"]

    def __str__(self):
        return self.customer_name


class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name="نام محصول")
    description = models.TextField(verbose_name="توضیحات")
    base_price = models.PositiveIntegerField(default=0, verbose_name="قیمت پایه به تومان")
    delivery_time = models.CharField(max_length=100, verbose_name="زمان آماده‌سازی")
    materials = models.CharField(max_length=255, verbose_name="متریال‌های قابل انتخاب")
    colors = models.CharField(max_length=255, verbose_name="رنگ‌بندی")
    image = models.ImageField(upload_to="products/", verbose_name="تصویر محصول")
    is_active = models.BooleanField(default=True, verbose_name="فعال باشد؟")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "محصول سفارشی"
        verbose_name_plural = "محصولات سفارشی"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="سوال")
    answer = models.TextField(verbose_name="پاسخ")
    is_active = models.BooleanField(default=True, verbose_name="فعال باشد؟")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "سوال متداول"
        verbose_name_plural = "سوالات متداول"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.question


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "جدید"),
        ("reviewing", "در حال بررسی"),
        ("quoted", "پیش‌فاکتور صادر شده"),
        ("accepted", "تأیید شده توسط مشتری"),
        ("paid", "پرداخت شده"),
        ("in_progress", "در حال انجام"),
        ("done", "انجام شده"),
        ("cancelled", "لغو شده"),
    ]

    SERVICE_TYPE_CHOICES = [
        ("3d_print", "چاپ سه‌بعدی"),
        ("design", "طراحی سه‌بعدی"),
        ("reverse_engineering", "مهندسی معکوس"),
        ("prototype", "نمونه‌سازی"),
        ("custom_part", "ساخت قطعه سفارشی"),
    ]

    public_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="توکن عمومی سفارش"
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="مشتری"
    )

    first_name = models.CharField(max_length=100, verbose_name="نام")
    last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")

    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_TYPE_CHOICES,
        default="3d_print",
        verbose_name="نوع خدمت"
    )

    material = models.ForeignKey(
        Material,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="متریال انتخابی"
    )

    color = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="رنگ موردنظر"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد"
    )

    description = models.TextField(verbose_name="توضیحات سفارش")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone}"

    def get_quote_url(self):
        return reverse("website:quote_detail", kwargs={"token": self.public_token})


class OrderImage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="images", verbose_name="سفارش")
    image = models.ImageField(upload_to="orders/", verbose_name="تصویر سفارش")

    class Meta:
        verbose_name = "تصویر سفارش"
        verbose_name_plural = "تصاویر سفارش"

    def __str__(self):
        return f"تصویر سفارش {self.order_id}"


class Quote(models.Model):
    STATUS_CHOICES = [
        ("draft", "پیش‌نویس"),
        ("sent", "ارسال شده برای مشتری"),
        ("accepted", "تأیید شده"),
        ("rejected", "رد شده"),
        ("expired", "منقضی شده"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="quote",
        verbose_name="سفارش"
    )

    price_tolerance_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="تلورانس قیمت درصدی"
    )

    material = models.ForeignKey(
        Material,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="متریال نهایی"
    )

    weight_grams = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="وزن قطعه به گرم"
    )

    print_time_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="زمان چاپ به دقیقه"
    )

    machine_hourly_rate = models.PositiveIntegerField(
        default=0,
        verbose_name="هزینه ساعتی دستگاه به تومان"
    )

    labor_fee = models.PositiveIntegerField(
        default=0,
        verbose_name="دستمزد ساخت/اپراتوری به تومان"
    )

    design_fee = models.PositiveIntegerField(
        default=0,
        verbose_name="هزینه طراحی یا مهندسی معکوس به تومان"
    )

    post_processing_fee = models.PositiveIntegerField(
        default=0,
        verbose_name="هزینه پرداخت‌کاری/مونتاژ به تومان"
    )

    shipping_fee = models.PositiveIntegerField(
        default=0,
        verbose_name="هزینه ارسال به تومان"
    )

    discount = models.PositiveIntegerField(
        default=0,
        verbose_name="تخفیف به تومان"
    )

    admin_note = models.TextField(
        blank=True,
        verbose_name="توضیحات داخلی"
    )

    customer_note = models.TextField(
        blank=True,
        verbose_name="توضیحات قابل نمایش به مشتری"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="وضعیت پیش‌فاکتور"
    )

    valid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="اعتبار پیش‌فاکتور تا تاریخ"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    @property
    def tolerance_amount(self):
        if not self.total_price:
            return 0

        return self.total_price * self.price_tolerance_percent / Decimal("100")


    @property
    def min_estimated_price(self):
        if not self.total_price:
            return 0

        return self.total_price - self.tolerance_amount


    @property
    def max_estimated_price(self):
        if not self.total_price:
            return 0

        return self.total_price + self.tolerance_amount

    class Meta:
        verbose_name = "پیش‌فاکتور"
        verbose_name_plural = "پیش‌فاکتورها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"پیش‌فاکتور سفارش {self.order_id}"

    @property
    def selected_material(self):
        return self.material or self.order.material

    @property
    def material_price_per_kg(self):
        material = self.selected_material
        if not material:
            return 0
        return material.price_per_kg or 0

    @property
    def material_price_per_gram(self):
        if not self.material_price_per_kg:
            return 0
        return Decimal(self.material_price_per_kg) / Decimal(1000)

    @property
    def material_cost(self):
        value = self.material_price_per_gram * self.weight_grams * Decimal(self.order.quantity)
        return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    @property
    def print_hours(self):
        if not self.print_time_minutes:
            return Decimal(0)
        return Decimal(self.print_time_minutes) / Decimal(60)

    @property
    def machine_cost(self):
        value = Decimal(self.machine_hourly_rate) * self.print_hours * Decimal(self.order.quantity)
        return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    @property
    def subtotal(self):
        return (
            self.material_cost
            + self.machine_cost
            + self.labor_fee
            + self.design_fee
            + self.post_processing_fee
            + self.shipping_fee
        )

    @property
    def total_price(self):
        total = self.subtotal - self.discount
        if total < 0:
            return 0
        return total


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار پرداخت"),
        ("paid", "پرداخت موفق"),
        ("failed", "پرداخت ناموفق"),
        ("cancelled", "لغو شده"),
    ]

    METHOD_CHOICES = [
        ("gateway", "درگاه پرداخت"),
        ("bank_transfer", "کارت به کارت / واریز دستی"),
    ]

    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="پیش‌فاکتور"
    )

    amount = models.PositiveIntegerField(verbose_name="مبلغ به تومان")
    method = models.CharField(max_length=30, choices=METHOD_CHOICES, default="gateway", verbose_name="روش پرداخت")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="وضعیت پرداخت")

    authority = models.CharField(max_length=255, blank=True, verbose_name="Authority درگاه")
    ref_id = models.CharField(max_length=255, blank=True, verbose_name="کد پیگیری پرداخت")

    receipt_image = models.ImageField(
        upload_to="payments/receipts/",
        blank=True,
        null=True,
        verbose_name="تصویر رسید پرداخت دستی"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ پرداخت")

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"پرداخت {self.amount} تومان - {self.get_status_display()}"

class OrderReview(models.Model):
    RATING_CHOICES = [
        (1, "1 ستاره"),
        (2, "2 ستاره"),
        (3, "3 ستاره"),
        (4, "4 ستاره"),
        (5, "5 ستاره"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="review",
        verbose_name="سفارش"
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_reviews",
        verbose_name="مشتری"
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=5,
        verbose_name="امتیاز"
    )

    comment = models.TextField(verbose_name="نظر مشتری")

    is_approved = models.BooleanField(
        default=False,
        verbose_name="تأیید شده توسط ادمین"
    )

    display_on_site = models.BooleanField(
        default=True,
        verbose_name="نمایش در سایت"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "نظر مشتری روی سفارش"
        verbose_name_plural = "نظرات مشتریان روی سفارشات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"نظر سفارش #{self.order_id} - {self.customer}"

# BEGIN PHASE 4 SEO SETTINGS
class SEOSettings(models.Model):
    site_name = models.CharField(max_length=120, default="3DprintHub.ir", verbose_name="نام سایت")
    site_url = models.URLField(default="https://3dprinthub.ir", verbose_name="آدرس اصلی سایت")
    default_meta_title = models.CharField(max_length=180, default="3DprintHub.ir | طراحی و چاپ سه‌بعدی", verbose_name="عنوان پیش‌فرض سئو")
    default_meta_description = models.CharField(max_length=320, default="طراحی، چاپ سه‌بعدی، مهندسی معکوس و ساخت قطعات صنعتی و سفارشی.", verbose_name="توضیح پیش‌فرض سئو")
    default_og_image = models.ImageField(upload_to="seo/", blank=True, null=True, verbose_name="تصویر پیش‌فرض اشتراک‌گذاری")
    organization_name = models.CharField(max_length=180, default="3DprintHub", verbose_name="نام سازمان در اسکیما")
    organization_logo = models.ImageField(upload_to="seo/", blank=True, null=True, verbose_name="لوگوی سازمان در اسکیما")
    google_site_verification = models.CharField(max_length=255, blank=True, verbose_name="کد تأیید Google Search Console")
    bing_site_verification = models.CharField(max_length=255, blank=True, verbose_name="کد تأیید Bing Webmaster")
    allow_search_indexing = models.BooleanField(default=True, verbose_name="اجازه ایندکس سایت")
    twitter_card = models.CharField(max_length=30, default="summary_large_image", choices=[("summary", "Summary"), ("summary_large_image", "Summary Large Image")], verbose_name="نوع Twitter Card")
    robots_extra = models.TextField(blank=True, verbose_name="دستورات اضافه robots.txt")
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "تنظیمات سئو سایت"
        verbose_name_plural = "تنظیمات سئو سایت"
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
    def __str__(self):
        return "تنظیمات سئو 3DprintHub"
# END PHASE 4 SEO SETTINGS

