from decimal import Decimal, ROUND_HALF_UP
import uuid
from django.conf import settings

from django.db import models
from django.urls import reverse
from website.private_storage import private_model_storage

class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        verbose_name="کاربر"
    )

    phone = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="شماره تماس")
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
    contact_eyebrow = models.CharField(
        max_length=120,
        default="تماس با ما",
        verbose_name="برچسب بخش تماس",
    )
    contact_title = models.CharField(
        max_length=255,
        default="آماده بررسی پروژه شما هستیم",
        verbose_name="عنوان بخش تماس",
    )
    contact_description = models.TextField(
        default="برای طراحی، ساخت، چاپ سه‌بعدی صنعتی و مهندسی معکوس قطعات با ما در ارتباط باشید.",
        verbose_name="توضیح بخش تماس",
    )
    contact_location_title = models.CharField(
        max_length=180,
        default="محل فعالیت 3DprintHub.ir",
        verbose_name="عنوان محل فعالیت",
    )
    telegram_operator_enabled = models.BooleanField(
        default=False,
        verbose_name="اعلان تلگرام برای اپراتور فعال باشد؟",
    )
    telegram_operator_bot_token = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="توکن ربات تلگرام اپراتور",
        help_text="توکن BotFather؛ فقط مدیر ارشد باید به این مقدار دسترسی داشته باشد.",
    )
    telegram_operator_chat_id = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Chat ID تلگرام اپراتور",
    )
    operator_alert_emails = models.TextField(
        blank=True,
        verbose_name="ایمیل‌های اعلان اپراتور",
        help_text="چند ایمیل را با ویرگول جدا کنید.",
    )
    payment_card_number = models.CharField(max_length=32, blank=True, verbose_name="شماره کارت دریافت وجه")
    payment_card_holder = models.CharField(max_length=150, blank=True, verbose_name="نام صاحب کارت")
    default_deposit_percent = models.PositiveSmallIntegerField(default=30, verbose_name="درصد پیش‌فرض بیعانه")
    online_payment_enabled = models.BooleanField(default=False, verbose_name="درگاه پرداخت آنلاین فعال باشد؟")
    online_payment_provider = models.CharField(
        max_length=30,
        default="zarinpal",
        choices=[("zarinpal", "زرین‌پال")],
        verbose_name="درگاه پرداخت آنلاین",
    )
    online_payment_title = models.CharField(
        max_length=120,
        default="پرداخت امن آنلاین",
        verbose_name="عنوان نمایش درگاه",
    )
    online_payment_minimum_toman = models.PositiveIntegerField(
        default=1000,
        verbose_name="حداقل مبلغ پرداخت آنلاین به تومان",
    )
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

    # BEGIN MATERIAL INVENTORY PHASE 8 FIELDS
    default_roll_weight_grams = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1000,
        verbose_name="وزن پیش‌فرض هر رول به گرم",
    )
    default_purchase_price_per_roll = models.PositiveBigIntegerField(
        default=0,
        verbose_name="قیمت خرید پیش‌فرض هر رول",
    )
    sale_price_per_gram = models.PositiveIntegerField(
        default=0,
        verbose_name="قیمت فروش هر گرم",
    )
    reorder_threshold_grams = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=250,
        verbose_name="حد هشدار سفارش مجدد به گرم",
    )
    track_filament_inventory = models.BooleanField(
        default=False,
        verbose_name="کنترل موجودی وزنی فیلامنت",
    )
        # BEGIN PHASE 10 MARKET MATERIAL PRICING FIELDS
    market_pricing_enabled = models.BooleanField(
        default=False,
        verbose_name="قیمت‌گذاری خودکار با دلار و Bambu Lab",
        help_text="در صورت فعال‌بودن، قیمت فروش هر گرم از قیمت دلاری مرجع و بیشترین نرخ دلار روز محاسبه می‌شود.",
    )
    bambu_product_url = models.URLField(
        blank=True,
        verbose_name="لینک رسمی فیلامنت در Bambu Lab",
        help_text="فقط لینک فروشگاه رسمی آمریکا مانند https://us.store.bambulab.com/products/...",
    )
    bambu_variant_hint = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="راهنمای نوع/Variant",
        help_text="مثلاً Filament with spool یا Refill. برای بررسی ادمین ذخیره می‌شود.",
    )
    bambu_reference_weight_grams = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1000,
        verbose_name="وزن مرجع Bambu به گرم",
    )
    market_import_cost_percent = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="هزینه واردات اختصاصی درصدی",
        help_text="اگر خالی باشد از مقدار عمومی تنظیمات بازار استفاده می‌شود.",
    )
    market_margin_percent = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="حاشیه فروش اختصاصی درصدی",
        help_text="اگر خالی باشد از مقدار عمومی استفاده می‌شود. 100 درصد یعنی دو برابر بهای محاسبه‌شده.",
    )
    market_bambu_usd_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="آخرین قیمت دلاری Bambu",
    )
    market_fx_daily_high_toman = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="بیشترین نرخ دلار روز",
    )
    market_cost_price_per_gram = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=0,
        verbose_name="بهای محاسباتی هر گرم",
    )
    market_sale_price_per_gram = models.PositiveBigIntegerField(
        default=0,
        verbose_name="قیمت فروش بازار هر گرم",
    )
    market_price_updated_at = models.DateTimeField(blank=True, null=True, verbose_name="آخرین بروزرسانی قیمت بازار")
    # END PHASE 10 MARKET MATERIAL PRICING FIELDS
# END MATERIAL INVENTORY PHASE 8 FIELDS

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


    # BEGIN MATERIAL INVENTORY PHASE 8 PROPERTIES
    @property
    def purchase_cost_per_gram(self):
        if self.default_roll_weight_grams and self.default_purchase_price_per_roll:
            return round(self.default_purchase_price_per_roll / float(self.default_roll_weight_grams), 2)
        return self.price_per_gram

    @property
    def effective_sale_price_per_gram(self):
        return self.market_sale_price_per_gram or self.sale_price_per_gram or self.price_per_gram

    @property
    def current_stock_grams(self):
        return self.filament_spools.exclude(status__in=["empty", "archived", "quarantine"]).aggregate(
            value=models.Sum("remaining_weight_grams")
        )["value"] or 0

    @property
    def current_roll_count(self):
        return self.filament_spools.exclude(status__in=["empty", "archived", "quarantine"]).filter(
            remaining_weight_grams__gt=0
        ).count()

    @property
    def needs_reorder(self):
        return bool(self.track_filament_inventory and self.current_stock_grams <= self.reorder_threshold_grams)
        # BEGIN PHASE 10 MARKET MATERIAL PRICING PROPERTIES
    @property
    def public_sale_price_per_gram(self):
        if self.market_pricing_enabled and self.market_sale_price_per_gram:
            return self.market_sale_price_per_gram
        return self.sale_price_per_gram or self.price_per_gram

    @property
    def public_price_per_kg(self):
        value = self.public_sale_price_per_gram
        return int(value * 1000) if value else 0
    # END PHASE 10 MARKET MATERIAL PRICING PROPERTIES
# END MATERIAL INVENTORY PHASE 8 PROPERTIES


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

    minimum_billable_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name="حداقل زمان قابل محاسبه به دقیقه",
    )

    billing_increment_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name="پله گردکردن زمان چاپ به دقیقه",
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

    deposit_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30,
        verbose_name="درصد بیعانه",
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
        public_per_gram = getattr(material, "public_sale_price_per_gram", 0) or getattr(material, "effective_sale_price_per_gram", 0)
        if public_per_gram:
            return int(Decimal(public_per_gram) * Decimal("1000"))
        return material.price_per_kg or 0

    @property
    def material_price_per_gram(self):
        material = self.selected_material
        if not material:
            return 0
        sale_price = (
            getattr(material, "public_sale_price_per_gram", 0)
            or getattr(material, "effective_sale_price_per_gram", 0)
            or getattr(material, "sale_price_per_gram", 0)
            or 0
        )
        if sale_price:
            return Decimal(sale_price)
        if not self.material_price_per_kg:
            return 0
        return Decimal(self.material_price_per_kg) / Decimal(1000)

    @property
    def material_cost(self):
        value = self.material_price_per_gram * self.weight_grams * Decimal(self.order.quantity)
        return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    @property
    def billable_print_minutes(self):
        if not self.print_time_minutes:
            return 0
        import math
        minimum = max(int(self.minimum_billable_minutes or 1), 1)
        increment = max(int(self.billing_increment_minutes or 1), 1)
        rounded = int(math.ceil(int(self.print_time_minutes) / increment) * increment)
        return max(minimum, rounded)

    @property
    def print_hours(self):
        if not self.billable_print_minutes:
            return Decimal(0)
        return Decimal(self.billable_print_minutes) / Decimal(60)

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

    @property
    def deposit_amount(self):
        if not self.total_price:
            return 0
        percent = max(Decimal(self.deposit_percent or 0), Decimal("0"))
        amount = Decimal(self.total_price) * percent / Decimal("100")
        return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    @property
    def paid_amount(self):
        return int(sum(self.payments.filter(status="paid").values_list("amount", flat=True)))

    @property
    def pending_amount(self):
        return int(sum(self.payments.filter(status__in=["pending", "verifying", "awaiting_review"]).values_list("amount", flat=True)))

    @property
    def remaining_amount(self):
        return max(int(self.total_price) - self.paid_amount, 0)

    @property
    def available_payment_amount(self):
        return max(int(self.total_price) - self.paid_amount - self.pending_amount, 0)


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار پرداخت"),
        ("verifying", "در حال تأیید درگاه"),
        ("awaiting_review", "در انتظار بررسی رسید"),
        ("paid", "پرداخت موفق"),
        ("failed", "پرداخت ناموفق"),
        ("cancelled", "لغو شده"),
    ]

    METHOD_CHOICES = [
        ("gateway", "درگاه پرداخت"),
        ("bank_transfer", "کارت به کارت / واریز دستی"),
    ]

    PAYMENT_KIND_CHOICES = [
        ("deposit", "بیعانه"),
        ("full", "پرداخت کامل"),
        ("balance", "تسویه مانده"),
    ]

    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="پیش‌فاکتور"
    )

    amount = models.PositiveIntegerField(verbose_name="مبلغ به تومان")
    payment_kind = models.CharField(max_length=20, choices=PAYMENT_KIND_CHOICES, default="deposit", verbose_name="نوع پرداخت")
    method = models.CharField(max_length=30, choices=METHOD_CHOICES, default="gateway", verbose_name="روش پرداخت")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="وضعیت پرداخت")

    authority = models.CharField(max_length=255, blank=True, verbose_name="Authority درگاه")
    ref_id = models.CharField(max_length=255, blank=True, verbose_name="کد پیگیری پرداخت")
    idempotency_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    callback_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    provider = models.CharField(max_length=30, blank=True, default="", db_index=True, verbose_name="ارائه‌دهنده درگاه")
    gateway_amount = models.PositiveBigIntegerField(default=0, verbose_name="مبلغ ارسال‌شده به درگاه")
    gateway_currency = models.CharField(max_length=8, default="IRT", verbose_name="واحد مبلغ درگاه")
    checkout_url = models.URLField(max_length=800, blank=True, verbose_name="لینک پرداخت درگاه")
    provider_status_code = models.IntegerField(null=True, blank=True, verbose_name="کد وضعیت درگاه")
    provider_message = models.CharField(max_length=500, blank=True, verbose_name="پیام درگاه")
    request_payload = models.JSONField(default=dict, blank=True, verbose_name="درخواست ارسال‌شده به درگاه")
    raw_response = models.JSONField(default=dict, blank=True, verbose_name="پاسخ خام درگاه")
    callback_payload = models.JSONField(default=dict, blank=True, verbose_name="پارامترهای بازگشت درگاه")
    client_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP شروع‌کننده پرداخت")
    user_agent = models.CharField(max_length=500, blank=True, verbose_name="مرورگر شروع‌کننده")
    initiated_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان ایجاد Authority")
    callback_received_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان دریافت Callback")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان تأیید سمت سرور")
    failed_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان شکست")
    retry_count = models.PositiveSmallIntegerField(default=0, verbose_name="تعداد تلاش تأیید")
    note = models.TextField(blank=True, verbose_name="توضیحات پرداخت")

    receipt_image = models.ImageField(
        storage=private_model_storage,
        upload_to="payments/receipts/",
        blank=True,
        null=True,
        verbose_name="تصویر رسید پرداخت دستی"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ پرداخت")

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["provider", "authority"], name="webpay_provider_auth_idx"),
            models.Index(fields=["status", "created_at"], name="webpay_status_created_idx"),
        ]

    def __str__(self):
        return f"{self.get_payment_kind_display()} {self.amount} تومان - {self.get_status_display()}"

    @property
    def is_terminal(self):
        return self.status in {"paid", "failed", "cancelled"}

    def mark_paid(self, ref_id="", *, provider_status_code=None, provider_message="", metadata=None):
        from .payment_services import mark_payment_paid
        return mark_payment_paid(
            self,
            ref_id=ref_id,
            provider_status_code=provider_status_code,
            provider_message=provider_message,
            metadata=metadata or {},
        )


class PaymentLedgerEntry(models.Model):
    DIRECTION_CHOICES = [("credit", "بستانکار"), ("debit", "بدهکار")]
    ENTRY_TYPE_CHOICES = [
        ("payment", "دریافت وجه"),
        ("refund", "استرداد وجه"),
        ("adjustment", "اصلاح مالی"),
    ]

    quote = models.ForeignKey(Quote, on_delete=models.PROTECT, related_name="ledger_entries", verbose_name="پیش‌فاکتور")
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name="ledger_entries", verbose_name="پرداخت")
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES, default="payment", db_index=True, verbose_name="نوع ثبت")
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default="credit", verbose_name="جهت")
    amount = models.PositiveBigIntegerField(verbose_name="مبلغ به تومان")
    currency = models.CharField(max_length=8, default="IRT", verbose_name="واحد")
    event_key = models.CharField(max_length=180, unique=True, db_index=True, verbose_name="کلید یکتای رویداد")
    provider_ref = models.CharField(max_length=255, blank=True, db_index=True, verbose_name="شناسه مرجع درگاه")
    description = models.CharField(max_length=500, blank=True, verbose_name="شرح")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="اطلاعات تکمیلی")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="زمان ثبت")

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "ثبت دفتر مالی پرداخت"
        verbose_name_plural = "دفتر مالی پرداخت‌ها"
        indexes = [models.Index(fields=["quote", "created_at"], name="webpay_ledger_quote_idx")]

    def __str__(self):
        return f"{self.get_entry_type_display()} - {self.amount} تومان"


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
    organization_phone = models.CharField(max_length=30, blank=True, verbose_name="تلفن سازمان")
    organization_email = models.EmailField(blank=True, verbose_name="ایمیل سازمان")
    street_address = models.CharField(max_length=255, blank=True, verbose_name="نشانی سازمان")
    address_locality = models.CharField(max_length=100, blank=True, verbose_name="شهر سازمان")
    address_region = models.CharField(max_length=100, blank=True, verbose_name="استان سازمان")
    organization_postal_code = models.CharField(max_length=20, blank=True, verbose_name="کد پستی سازمان")
    country_code = models.CharField(max_length=2, default="IR", verbose_name="کد کشور")
    same_as = models.TextField(blank=True, verbose_name="شبکه‌های اجتماعی", help_text="هر لینک در یک خط")
    merchant_return_days = models.PositiveSmallIntegerField(default=7, verbose_name="مهلت بازگشت کالا (روز)")
    shipping_rate = models.PositiveIntegerField(default=0, verbose_name="هزینه پایه ارسال در اسکیما (تومان)")
    handling_min_days = models.PositiveSmallIntegerField(default=1, verbose_name="حداقل زمان آماده‌سازی")
    handling_max_days = models.PositiveSmallIntegerField(default=3, verbose_name="حداکثر زمان آماده‌سازی")
    transit_min_days = models.PositiveSmallIntegerField(default=1, verbose_name="حداقل زمان حمل")
    transit_max_days = models.PositiveSmallIntegerField(default=7, verbose_name="حداکثر زمان حمل")
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

# BEGIN PHASE 5 IRAN LOCATION MODELS
class IranProvince(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="استان")
    code = models.CharField(max_length=20, blank=True, db_index=True, verbose_name="کد استان")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "استان ایران"
        verbose_name_plural = "استان‌های ایران"

    def __str__(self):
        return self.name


class IranCounty(models.Model):
    province = models.ForeignKey(IranProvince, on_delete=models.CASCADE, related_name="counties", verbose_name="استان")
    name = models.CharField(max_length=120, db_index=True, verbose_name="شهرستان")
    code = models.CharField(max_length=30, blank=True, db_index=True, verbose_name="کد شهرستان")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")

    class Meta:
        ordering = ["province__sort_order", "name"]
        constraints = [models.UniqueConstraint(fields=["province", "name"], name="unique_iran_county_per_province")]
        verbose_name = "شهرستان ایران"
        verbose_name_plural = "شهرستان‌های ایران"

    def __str__(self):
        return f"{self.province} - {self.name}"


class IranCity(models.Model):
    province = models.ForeignKey(IranProvince, on_delete=models.CASCADE, related_name="cities", verbose_name="استان")
    county = models.ForeignKey(IranCounty, on_delete=models.CASCADE, related_name="cities", verbose_name="شهرستان")
    name = models.CharField(max_length=120, db_index=True, verbose_name="شهر")
    district_name = models.CharField(max_length=120, blank=True, verbose_name="بخش")
    division_code = models.CharField(max_length=30, blank=True, db_index=True, verbose_name="کد تقسیمات کشوری")
    source_id = models.CharField(max_length=100, blank=True, db_index=True, verbose_name="شناسه منبع")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")

    class Meta:
        ordering = ["province__sort_order", "county__name", "name"]
        constraints = [models.UniqueConstraint(fields=["province", "county", "name"], name="unique_iran_city_per_county")]
        verbose_name = "شهر ایران"
        verbose_name_plural = "شهرهای ایران"

    def __str__(self):
        return f"{self.province} - {self.county.name} - {self.name}"
# END PHASE 5 IRAN LOCATION MODELS

# BEGIN PHASE 10 ORDER INTAKE AND PRIVATE MODEL VAULT


class CustomerReusableModel(models.Model):
    SOURCE_CHOICES = [
        ("site_order", "سفارش ثبت‌شده در سایت"),
        ("offline_order", "سفارش حضوری یا ثبت دفتر"),
        ("admin_upload", "آپلود مستقیم مدیریت"),
    ]

    public_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reusable_3d_models",
        verbose_name="مشتری یا همکار",
    )
    source_order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="saved_models",
        verbose_name="سفارش مبنا",
    )
    source_kind = models.CharField(max_length=30, choices=SOURCE_CHOICES, default="site_order", verbose_name="منبع ثبت")
    display_name = models.CharField(
        max_length=220,
        verbose_name="نام قابل نمایش مدل",
        help_text="مشتری فقط این نام و وضعیت موجودبودن فایل را می‌بیند.",
    )
    internal_code = models.CharField(max_length=80, unique=True, verbose_name="کد داخلی")
    model_file = models.FileField(
        storage=private_model_storage,
        upload_to="customer-models/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="فایل سه‌بعدی خصوصی",
        help_text="این فایل خارج از Media عمومی ذخیره می‌شود و به مشتری یا نماینده تحویل داده نمی‌شود.",
    )
    file_format = models.CharField(max_length=40, blank=True, verbose_name="فرمت فایل")
    version = models.CharField(max_length=40, blank=True, verbose_name="نسخه")
    material_hint = models.ForeignKey(
        Material,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reusable_customer_models",
        verbose_name="متریال پیشنهادی قبلی",
    )
    default_color = models.CharField(max_length=100, blank=True, verbose_name="رنگ قبلی")
    default_quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد پیش‌فرض")
    last_known_weight_grams = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="آخرین وزن چاپ")
    last_known_print_minutes = models.PositiveIntegerField(blank=True, null=True, verbose_name="آخرین زمان چاپ")
    available_for_reorder = models.BooleanField(default=True, db_index=True, verbose_name="قابل سفارش مجدد")
    customer_note = models.TextField(blank=True, verbose_name="توضیح قابل مشاهده مشتری")
    admin_note = models.TextField(blank=True, verbose_name="یادداشت داخلی")
    last_ordered_at = models.DateTimeField(blank=True, null=True, verbose_name="آخرین سفارش مجدد")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "مدل سه‌بعدی محفوظ مشتری"
        verbose_name_plural = "مدل‌های سه‌بعدی محفوظ مشتریان"

    def __str__(self):
        return f"{self.display_name} - {self.customer}"

    @property
    def file_is_available(self):
        return bool(self.model_file)


class OrderIntakeDetail(models.Model):
    REQUEST_MODE_CHOICES = [
        ("new_part", "ساخت قطعه جدید از روی عکس/نمونه"),
        ("reorder_model", "سفارش مجدد مدل محفوظ قبلی"),
        ("ready_catalog", "سفارش مدل آماده کاتالوگ"),
    ]
    ENVIRONMENT_CHOICES = [
        ("indoor", "فضای داخلی"),
        ("outdoor", "فضای باز"),
        ("both", "هر دو"),
        ("unknown", "نیازمند بررسی"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="intake_detail", verbose_name="سفارش")
    request_mode = models.CharField(max_length=30, choices=REQUEST_MODE_CHOICES, default="new_part", db_index=True, verbose_name="نوع درخواست")
    reusable_model = models.ForeignKey(
        CustomerReusableModel,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="reorders",
        verbose_name="مدل محفوظ انتخاب‌شده",
    )
    ready_catalog_asset_id = models.PositiveBigIntegerField(blank=True, null=True, verbose_name="شناسه مدل آماده")
    usage_environment = models.CharField(max_length=20, choices=ENVIRONMENT_CHOICES, default="unknown", verbose_name="محیط استفاده")
    contact_with_gasoline = models.BooleanField(default=False, verbose_name="تماس با بنزین")
    contact_with_oil = models.BooleanField(default=False, verbose_name="تماس با روغن")
    contact_with_grease = models.BooleanField(default=False, verbose_name="تماس با گریس")
    contact_with_water = models.BooleanField(default=False, verbose_name="تماس با آب یا رطوبت")
    contact_with_chemicals = models.BooleanField(default=False, verbose_name="تماس با مواد شیمیایی")
    chemical_details = models.CharField(max_length=300, blank=True, verbose_name="نوع ماده شیمیایی")
    operating_temperature_min = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name="حداقل دمای کاری")
    operating_temperature_max = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name="حداکثر دمای کاری")
    required_properties = models.TextField(blank=True, verbose_name="خواص مورد انتظار قطعه")
    exact_dimensions = models.TextField(blank=True, verbose_name="ابعاد و اندازه‌های دقیق")
    installation_location = models.TextField(blank=True, verbose_name="محل و نحوه نصب")
    load_conditions = models.TextField(blank=True, verbose_name="نوع فشار، ضربه یا بار")
    dimensional_tolerance = models.CharField(max_length=120, blank=True, verbose_name="تلرانس مورد نیاز")
    has_physical_sample = models.BooleanField(default=False, verbose_name="نمونه فیزیکی موجود است")
    sample_delivery_method = models.CharField(max_length=200, blank=True, verbose_name="روش تحویل نمونه")
    extra_notes = models.TextField(blank=True, verbose_name="توضیحات تکمیلی")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "اطلاعات فنی سفارش"
        verbose_name_plural = "اطلاعات فنی سفارش‌ها"

    def __str__(self):
        return f"اطلاعات فنی سفارش {self.order_id}"


class OrderReferencePhoto(models.Model):
    VIEW_CHOICES = [
        ("top", "نمای بالا"),
        ("front", "نمای روبه‌رو"),
        ("right", "نمای راست"),
        ("left", "نمای چپ"),
        ("extra_1", "نمای تکمیلی اول"),
        ("extra_2", "نمای تکمیلی دوم"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reference_photos", verbose_name="سفارش")
    view_type = models.CharField(max_length=20, choices=VIEW_CHOICES, db_index=True, verbose_name="زاویه تصویر")
    image = models.ImageField(upload_to="orders/reference/%Y/%m/", verbose_name="تصویر")
    note = models.CharField(max_length=250, blank=True, verbose_name="توضیح")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [models.UniqueConstraint(fields=["order", "view_type"], name="unique_order_reference_view")]
        verbose_name = "تصویر مرجع سفارش"
        verbose_name_plural = "تصاویر مرجع سفارش"

    def __str__(self):
        return f"{self.order_id} - {self.get_view_type_display()}"

# END PHASE 10 ORDER INTAKE AND PRIVATE MODEL VAULT

# BEGIN PHASE 14 PRESENTATION MODELS
class HomePresentationSetting(models.Model):
    hero_slider_count = models.PositiveSmallIntegerField(
        default=6,
        verbose_name="تعداد تصاویر اسلایدر Hero",
        help_text="برای حفظ سرعت صفحه اول، مقدار ۴ تا ۶ پیشنهاد می‌شود.",
    )
    catalog_preview_count = models.PositiveSmallIntegerField(
        default=9,
        verbose_name="تعداد مدل در بخش معرفی",
        help_text="مدل‌ها در شبکه سه‌ستونه نمایش داده می‌شوند؛ مقدار پیشنهادی ۹ است.",
    )
    randomize_hero = models.BooleanField(
        default=True,
        verbose_name="نمایش رندوم مدل‌های Hero",
    )
    show_team_section = models.BooleanField(default=True, verbose_name="نمایش بخش متخصصان")
    show_clients_section = models.BooleanField(default=True, verbose_name="نمایش بخش مشتریان")
    hero_badge = models.CharField(
        max_length=180,
        default="مرکز تخصصی طراحی، مهندسی معکوس و چاپ سه‌بعدی",
        verbose_name="نشان بالای Hero",
    )
    catalog_heading = models.CharField(
        max_length=180,
        default="مدل‌های آماده برای چاپ",
        verbose_name="عنوان بخش معرفی مدل‌ها",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات پرزنت صفحه اول"
        verbose_name_plural = "تنظیمات پرزنت صفحه اول"

    def save(self, *args, **kwargs):
        self.pk = 1
        return super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "تنظیمات پرزنت صفحه اول"


class TeamMember(models.Model):
    name = models.CharField(max_length=160, verbose_name="نام و نام خانوادگی")
    role = models.CharField(max_length=180, verbose_name="سمت یا تخصص اصلی")
    photo = models.ImageField(
        upload_to="website/team/",
        blank=True,
        null=True,
        verbose_name="تصویر متخصص",
        help_text="تصویر عمودی یا مربعی با کیفیت مناسب و حجم بهینه بارگذاری شود.",
    )
    years_experience = models.PositiveSmallIntegerField(default=0, verbose_name="سال سابقه")
    short_bio = models.TextField(
        blank=True,
        verbose_name="معرفی کوتاه",
        help_text="در ۲ تا ۴ جمله، تجربه مرتبط با طراحی، چاپ، مهندسی معکوس یا کنترل کیفیت نوشته شود.",
    )
    expertise = models.TextField(
        blank=True,
        verbose_name="توانمندی‌ها",
        help_text="هر توانمندی را در یک خط بنویسید؛ مانند طراحی CAD، مهندسی معکوس، انتخاب متریال.",
    )
    certifications = models.CharField(max_length=300, blank=True, verbose_name="گواهی‌ها و دوره‌ها")
    linkedin_url = models.URLField(blank=True, verbose_name="لینک حرفه‌ای")
    sort_order = models.PositiveIntegerField(default=100, db_index=True, verbose_name="ترتیب نمایش")
    is_featured = models.BooleanField(default=True, db_index=True, verbose_name="نمایش در صفحه اول")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "متخصص مجموعه"
        verbose_name_plural = "متخصصان مجموعه"

    @property
    def expertise_list(self):
        return [item.strip() for item in self.expertise.splitlines() if item.strip()]

    def __str__(self):
        return f"{self.name} - {self.role}"


class ClientReference(models.Model):
    name = models.CharField(max_length=180, verbose_name="نام مشتری یا مجموعه")
    logo = models.ImageField(
        upload_to="website/clients/",
        blank=True,
        null=True,
        verbose_name="لوگو",
        help_text="لوگوی دارای مجوز نمایش، ترجیحاً PNG یا WebP با پس‌زمینه شفاف.",
    )
    industry = models.CharField(max_length=160, blank=True, verbose_name="حوزه فعالیت")
    project_summary = models.CharField(
        max_length=360,
        blank=True,
        verbose_name="خلاصه همکاری",
        help_text="بدون افشای اطلاعات محرمانه، نوع خدمت یا نتیجه همکاری را کوتاه بنویسید.",
    )
    website_url = models.URLField(blank=True, verbose_name="وب‌سایت مشتری")
    display_permission_confirmed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="مجوز نمایش نام و لوگو تأیید شده",
        help_text="بدون تأیید این گزینه، مشتری در سایت عمومی نمایش داده نمی‌شود.",
    )
    sort_order = models.PositiveIntegerField(default=100, db_index=True, verbose_name="ترتیب نمایش")
    is_featured = models.BooleanField(default=True, db_index=True, verbose_name="نمایش در صفحه اول")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "مشتری مجموعه"
        verbose_name_plural = "مشتریان مجموعه"

    def __str__(self):
        return self.name
# END PHASE 14 PRESENTATION MODELS


# BEGIN PHASE 19 SUPPORT CHAT AND PRIVATE ORDER ATTACHMENTS
class OrderAttachment(models.Model):
    """Private technical files submitted with a manufacturing order."""

    public_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="سفارش",
    )
    file = models.FileField(
        storage=private_model_storage,
        upload_to="order-attachments/%Y/%m/",
        verbose_name="فایل خصوصی",
    )
    original_name = models.CharField(max_length=255, verbose_name="نام اصلی فایل")
    content_type = models.CharField(max_length=120, blank=True, verbose_name="نوع فایل")
    size_bytes = models.PositiveBigIntegerField(default=0, verbose_name="حجم فایل")
    note = models.CharField(max_length=300, blank=True, verbose_name="توضیح")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ارسال")

    class Meta:
        ordering = ["id"]
        verbose_name = "مدرک یا فایل سفارش"
        verbose_name_plural = "مدارک و فایل‌های سفارش"

    def __str__(self):
        return self.original_name or f"فایل سفارش {self.order_id}"

    @property
    def size_label(self):
        size = int(self.size_bytes or 0)
        if size < 1024:
            return f"{size} بایت"
        if size < 1024 * 1024:
            return f"{size / 1024:.1f} کیلوبایت"
        return f"{size / (1024 * 1024):.1f} مگابایت"

    @property
    def extension(self):
        return Path(self.original_name or self.file.name).suffix.lower()

    @property
    def is_image(self):
        return self.extension in {".jpg", ".jpeg", ".png", ".webp"}

    @property
    def is_pdf(self):
        return self.extension == ".pdf"

    @property
    def is_previewable(self):
        return self.is_image or self.is_pdf


class SupportConversation(models.Model):
    STATUS_CHOICES = [
        ("open", "باز"),
        ("waiting_customer", "منتظر پاسخ مشتری"),
        ("waiting_staff", "منتظر پاسخ پشتیبانی"),
        ("closed", "بسته شده"),
    ]

    public_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_conversations",
        limit_choices_to={"is_staff": False},
        verbose_name="مشتری",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_support_conversations",
        null=True,
        blank=True,
        limit_choices_to={"is_staff": True},
        verbose_name="کارشناس پاسخ‌گو",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        related_name="support_conversations",
        null=True,
        blank=True,
        verbose_name="سفارش مرتبط",
    )
    subject = models.CharField(max_length=220, default="گفت‌وگو با پشتیبانی", verbose_name="موضوع")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="open", db_index=True, verbose_name="وضعیت")
    last_message_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="آخرین پیام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="بروزرسانی")

    class Meta:
        ordering = ["-last_message_at", "-updated_at"]
        verbose_name = "گفت‌وگوی پشتیبانی"
        verbose_name_plural = "گفت‌وگوهای پشتیبانی"

    def __str__(self):
        name = self.customer.get_full_name() or self.customer.get_username()
        return f"{name} — {self.subject}"

    @property
    def unread_for_staff(self):
        return self.messages.filter(sender__is_staff=False, read_by_staff_at__isnull=True).count()

    @property
    def unread_for_customer(self):
        return self.messages.filter(sender__is_staff=True, read_by_customer_at__isnull=True).count()


class SupportMessage(models.Model):
    public_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    conversation = models.ForeignKey(
        SupportConversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="گفت‌وگو",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="support_messages",
        verbose_name="فرستنده",
    )
    body = models.TextField(blank=True, verbose_name="متن پیام")
    attachment = models.FileField(
        storage=private_model_storage,
        upload_to="support-chat/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="پیوست خصوصی",
    )
    attachment_name = models.CharField(max_length=255, blank=True, verbose_name="نام پیوست")
    attachment_content_type = models.CharField(max_length=120, blank=True, verbose_name="نوع پیوست")
    attachment_size = models.PositiveBigIntegerField(default=0, verbose_name="حجم پیوست")
    read_by_customer_at = models.DateTimeField(null=True, blank=True, verbose_name="خوانده‌شده توسط مشتری")
    read_by_staff_at = models.DateTimeField(null=True, blank=True, verbose_name="خوانده‌شده توسط پشتیبانی")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="زمان ارسال")

    class Meta:
        ordering = ["created_at", "id"]
        verbose_name = "پیام پشتیبانی"
        verbose_name_plural = "پیام‌های پشتیبانی"

    def __str__(self):
        return f"پیام {self.pk or 'جدید'} — {self.sender}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        SupportConversation.objects.filter(pk=self.conversation_id).update(
            last_message_at=self.created_at,
            status="waiting_customer" if self.sender.is_staff else "waiting_staff",
        )
# END PHASE 19 SUPPORT CHAT AND PRIVATE ORDER ATTACHMENTS
