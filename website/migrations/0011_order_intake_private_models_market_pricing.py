import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import website.private_storage


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("website", "0010_material_inventory_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="material",
            name="market_pricing_enabled",
            field=models.BooleanField(default=False, help_text="در صورت فعال‌بودن، قیمت فروش هر گرم از قیمت دلاری مرجع و بیشترین نرخ دلار روز محاسبه می‌شود.", verbose_name="قیمت‌گذاری خودکار با دلار و Bambu Lab"),
        ),
        migrations.AddField(model_name="material", name="bambu_product_url", field=models.URLField(blank=True, help_text="فقط لینک فروشگاه رسمی آمریکا مانند https://us.store.bambulab.com/products/...", verbose_name="لینک رسمی فیلامنت در Bambu Lab")),
        migrations.AddField(model_name="material", name="bambu_variant_hint", field=models.CharField(blank=True, help_text="مثلاً Filament with spool یا Refill. برای بررسی ادمین ذخیره می‌شود.", max_length=120, verbose_name="راهنمای نوع/Variant")),
        migrations.AddField(model_name="material", name="bambu_reference_weight_grams", field=models.DecimalField(decimal_places=2, default=1000, max_digits=10, verbose_name="وزن مرجع Bambu به گرم")),
        migrations.AddField(model_name="material", name="market_import_cost_percent", field=models.DecimalField(blank=True, decimal_places=2, help_text="اگر خالی باشد از مقدار عمومی تنظیمات بازار استفاده می‌شود.", max_digits=6, null=True, verbose_name="هزینه واردات اختصاصی درصدی")),
        migrations.AddField(model_name="material", name="market_margin_percent", field=models.DecimalField(blank=True, decimal_places=2, help_text="اگر خالی باشد از مقدار عمومی استفاده می‌شود. 100 درصد یعنی دو برابر بهای محاسبه‌شده.", max_digits=6, null=True, verbose_name="حاشیه فروش اختصاصی درصدی")),
        migrations.AddField(model_name="material", name="market_bambu_usd_price", field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name="آخرین قیمت دلاری Bambu")),
        migrations.AddField(model_name="material", name="market_fx_daily_high_toman", field=models.DecimalField(decimal_places=2, default=0, max_digits=18, verbose_name="بیشترین نرخ دلار روز")),
        migrations.AddField(model_name="material", name="market_cost_price_per_gram", field=models.DecimalField(decimal_places=2, default=0, max_digits=16, verbose_name="بهای محاسباتی هر گرم")),
        migrations.AddField(model_name="material", name="market_sale_price_per_gram", field=models.PositiveBigIntegerField(default=0, verbose_name="قیمت فروش بازار هر گرم")),
        migrations.AddField(model_name="material", name="market_price_updated_at", field=models.DateTimeField(blank=True, null=True, verbose_name="آخرین بروزرسانی قیمت بازار")),
        migrations.CreateModel(
            name="CustomerReusableModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("source_kind", models.CharField(choices=[("site_order", "سفارش ثبت‌شده در سایت"), ("offline_order", "سفارش حضوری یا ثبت دفتر"), ("admin_upload", "آپلود مستقیم مدیریت")], default="site_order", max_length=30, verbose_name="منبع ثبت")),
                ("display_name", models.CharField(help_text="مشتری فقط این نام و وضعیت موجودبودن فایل را می‌بیند.", max_length=220, verbose_name="نام قابل نمایش مدل")),
                ("internal_code", models.CharField(max_length=80, unique=True, verbose_name="کد داخلی")),
                ("model_file", models.FileField(blank=True, help_text="این فایل خارج از Media عمومی ذخیره می‌شود و به مشتری یا نماینده تحویل داده نمی‌شود.", null=True, storage=website.private_storage.private_model_storage, upload_to="customer-models/%Y/%m/", verbose_name="فایل سه‌بعدی خصوصی")),
                ("file_format", models.CharField(blank=True, max_length=40, verbose_name="فرمت فایل")),
                ("version", models.CharField(blank=True, max_length=40, verbose_name="نسخه")),
                ("default_color", models.CharField(blank=True, max_length=100, verbose_name="رنگ قبلی")),
                ("default_quantity", models.PositiveIntegerField(default=1, verbose_name="تعداد پیش‌فرض")),
                ("last_known_weight_grams", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="آخرین وزن چاپ")),
                ("last_known_print_minutes", models.PositiveIntegerField(blank=True, null=True, verbose_name="آخرین زمان چاپ")),
                ("available_for_reorder", models.BooleanField(db_index=True, default=True, verbose_name="قابل سفارش مجدد")),
                ("customer_note", models.TextField(blank=True, verbose_name="توضیح قابل مشاهده مشتری")),
                ("admin_note", models.TextField(blank=True, verbose_name="یادداشت داخلی")),
                ("last_ordered_at", models.DateTimeField(blank=True, null=True, verbose_name="آخرین سفارش مجدد")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reusable_3d_models", to=settings.AUTH_USER_MODEL, verbose_name="مشتری یا همکار")),
                ("material_hint", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reusable_customer_models", to="website.material", verbose_name="متریال پیشنهادی قبلی")),
                ("source_order", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="saved_models", to="website.order", verbose_name="سفارش مبنا")),
            ],
            options={"verbose_name": "مدل سه‌بعدی محفوظ مشتری", "verbose_name_plural": "مدل‌های سه‌بعدی محفوظ مشتریان", "ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="OrderIntakeDetail",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("request_mode", models.CharField(choices=[("new_part", "ساخت قطعه جدید از روی عکس/نمونه"), ("reorder_model", "سفارش مجدد مدل محفوظ قبلی"), ("ready_catalog", "سفارش مدل آماده کاتالوگ")], db_index=True, default="new_part", max_length=30, verbose_name="نوع درخواست")),
                ("ready_catalog_asset_id", models.PositiveBigIntegerField(blank=True, null=True, verbose_name="شناسه مدل آماده")),
                ("usage_environment", models.CharField(choices=[("indoor", "فضای داخلی"), ("outdoor", "فضای باز"), ("both", "هر دو"), ("unknown", "نیازمند بررسی")], default="unknown", max_length=20, verbose_name="محیط استفاده")),
                ("contact_with_gasoline", models.BooleanField(default=False, verbose_name="تماس با بنزین")),
                ("contact_with_oil", models.BooleanField(default=False, verbose_name="تماس با روغن")),
                ("contact_with_grease", models.BooleanField(default=False, verbose_name="تماس با گریس")),
                ("contact_with_water", models.BooleanField(default=False, verbose_name="تماس با آب یا رطوبت")),
                ("contact_with_chemicals", models.BooleanField(default=False, verbose_name="تماس با مواد شیمیایی")),
                ("chemical_details", models.CharField(blank=True, max_length=300, verbose_name="نوع ماده شیمیایی")),
                ("operating_temperature_min", models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name="حداقل دمای کاری")),
                ("operating_temperature_max", models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name="حداکثر دمای کاری")),
                ("required_properties", models.TextField(blank=True, verbose_name="خواص مورد انتظار قطعه")),
                ("exact_dimensions", models.TextField(blank=True, verbose_name="ابعاد و اندازه‌های دقیق")),
                ("installation_location", models.TextField(blank=True, verbose_name="محل و نحوه نصب")),
                ("load_conditions", models.TextField(blank=True, verbose_name="نوع فشار، ضربه یا بار")),
                ("dimensional_tolerance", models.CharField(blank=True, max_length=120, verbose_name="تلرانس مورد نیاز")),
                ("has_physical_sample", models.BooleanField(default=False, verbose_name="نمونه فیزیکی موجود است")),
                ("sample_delivery_method", models.CharField(blank=True, max_length=200, verbose_name="روش تحویل نمونه")),
                ("extra_notes", models.TextField(blank=True, verbose_name="توضیحات تکمیلی")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="intake_detail", to="website.order", verbose_name="سفارش")),
                ("reusable_model", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="reorders", to="website.customerreusablemodel", verbose_name="مدل محفوظ انتخاب‌شده")),
            ],
            options={"verbose_name": "اطلاعات فنی سفارش", "verbose_name_plural": "اطلاعات فنی سفارش‌ها"},
        ),
        migrations.CreateModel(
            name="OrderReferencePhoto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("view_type", models.CharField(choices=[("top", "نمای بالا"), ("front", "نمای روبه‌رو"), ("right", "نمای راست"), ("left", "نمای چپ"), ("extra_1", "نمای تکمیلی اول"), ("extra_2", "نمای تکمیلی دوم")], db_index=True, max_length=20, verbose_name="زاویه تصویر")),
                ("image", models.ImageField(upload_to="orders/reference/%Y/%m/", verbose_name="تصویر")),
                ("note", models.CharField(blank=True, max_length=250, verbose_name="توضیح")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reference_photos", to="website.order", verbose_name="سفارش")),
            ],
            options={"verbose_name": "تصویر مرجع سفارش", "verbose_name_plural": "تصاویر مرجع سفارش", "ordering": ["id"]},
        ),
        migrations.AddConstraint(model_name="orderreferencephoto", constraint=models.UniqueConstraint(fields=("order", "view_type"), name="unique_order_reference_view")),
    ]
