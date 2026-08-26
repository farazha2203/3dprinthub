from django.db import migrations, models


def backfill_fixed_products(apps, schema_editor):
    Product = apps.get_model("store", "Product")
    Product.objects.filter(order_mode="fixed", fixed_price__gt=0).update(
        pricing_policy="product_fixed"
    )


def create_shipping_presets(apps, schema_editor):
    ShippingMethod = apps.get_model("store", "ShippingMethod")
    presets = (
        (
            "pickup-isfahan",
            {
                "title": "تحویل حضوری در اصفهان",
                "description": "تحویل حضوری سفارش در اصفهان؛ هماهنگی زمان تحویل پس از آماده‌شدن سفارش.",
                "service_type": "pickup_isfahan",
                "delivery_scope": "isfahan_only",
                "fee_mode": "free",
                "requires_address": False,
                "requires_postal_code": False,
                "customer_notice": "هزینه ارسال ندارد؛ زمان و محل تحویل با شما هماهنگ می‌شود.",
                "flat_fee": 0,
                "is_active": True,
            },
        ),
        (
            "courier-isfahan-postpaid",
            {
                "title": "پیک اصفهان — پس‌کرایه",
                "description": "ارسال با پیک داخل اصفهان؛ کرایه پیک هنگام تحویل توسط مشتری پرداخت می‌شود.",
                "service_type": "courier_isfahan",
                "delivery_scope": "isfahan_only",
                "fee_mode": "postpaid",
                "requires_address": True,
                "requires_postal_code": False,
                "customer_notice": "کرایه پیک جداگانه و هنگام تحویل پرداخت می‌شود.",
                "flat_fee": 0,
                "is_active": True,
            },
        ),
        (
            "post",
            {
                "title": "ارسال با پست",
                "description": "ارسال پستی؛ قبل از فعال‌سازی عمومی، مبلغ ثابت یا قوانین وزنی را در مدیریت فروشگاه تنظیم کنید.",
                "service_type": "post",
                "delivery_scope": "nationwide",
                "fee_mode": "calculated",
                "requires_address": True,
                "requires_postal_code": True,
                "customer_notice": "هزینه ارسال بر اساس تنظیمات پست و وزن مرسوله محاسبه می‌شود.",
                "flat_fee": 0,
                "is_active": False,
            },
        ),
        (
            "tipax",
            {
                "title": "ارسال با تیپاکس",
                "description": "ارسال با تیپاکس؛ قبل از فعال‌سازی عمومی، روش دریافت کرایه یا مبلغ/قوانین حمل را مشخص کنید.",
                "service_type": "tipax",
                "delivery_scope": "nationwide",
                "fee_mode": "calculated",
                "requires_address": True,
                "requires_postal_code": False,
                "customer_notice": "هزینه ارسال مطابق تنظیمات فعال تیپاکس محاسبه یا اعلام می‌شود.",
                "flat_fee": 0,
                "is_active": False,
            },
        ),
    )
    for code, defaults in presets:
        if not ShippingMethod.objects.filter(code=code).exists():
            ShippingMethod.objects.create(code=code, **defaults)


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0036_phase50_checkout_snapshot"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="pricing_policy",
            field=models.CharField(
                choices=[
                    ("formula", "فرمولی / محاسباتی"),
                    ("product_fixed", "قیمت قطعی کل محصول"),
                    ("profile_fixed", "قیمت قطعی هر پروفایل / سایز"),
                    ("profile_material_fixed", "قیمت قطعی هر پروفایل + متریال"),
                    ("profile_material_color_fixed", "قیمت قطعی هر پروفایل + متریال + رنگ"),
                ],
                db_index=True,
                default="formula",
                max_length=40,
                verbose_name="سیاست قیمت‌گذاری فروش",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="sales_notice",
            field=models.TextField(
                blank=True,
                default="",
                verbose_name="توضیح اپراتور برای مشتری / محتویات و آماده‌سازی",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="enforce_color_stock",
            field=models.BooleanField(
                default=False,
                help_text="اگر خاموش باشد، صفر بودن موجودی ثبت‌شده رنگ مانع سفارش محصولات تولید پس از سفارش نمی‌شود. برای فروش مبتنی بر موجودی واقعی روشن شود.",
                verbose_name="کنترل سخت موجودی رنگ/فیلامنت هنگام سفارش",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="fixed_price_override",
            field=models.PositiveBigIntegerField(
                default=0,
                help_text="در سیاست‌های قیمت قطعی پروفایل/متریال/رنگ استفاده می‌شود؛ صفر یعنی استفاده از قیمت پایه محصول.",
                verbose_name="قیمت قطعی این پروفایل/ترکیب",
            ),
        ),
        migrations.AddField(
            model_name="shippingmethod",
            name="service_type",
            field=models.CharField(
                choices=[
                    ("generic", "روش عمومی"),
                    ("pickup_isfahan", "تحویل حضوری اصفهان"),
                    ("courier_isfahan", "پیک اصفهان"),
                    ("post", "پست"),
                    ("tipax", "تیپاکس"),
                ],
                db_index=True,
                default="generic",
                max_length=32,
                verbose_name="نوع سرویس ارسال",
            ),
        ),
        migrations.AddField(
            model_name="shippingmethod",
            name="delivery_scope",
            field=models.CharField(
                choices=[("nationwide", "تمام ایران"), ("isfahan_only", "فقط اصفهان")],
                db_index=True,
                default="nationwide",
                max_length=24,
                verbose_name="محدوده ارائه سرویس",
            ),
        ),
        migrations.AddField(
            model_name="shippingmethod",
            name="fee_mode",
            field=models.CharField(
                choices=[
                    ("calculated", "محاسبه با مبلغ ثابت / قوانین وزن"),
                    ("free", "رایگان"),
                    ("postpaid", "پس‌کرایه / پرداخت هزینه حمل هنگام تحویل"),
                ],
                default="calculated",
                max_length=24,
                verbose_name="روش محاسبه هزینه ارسال",
            ),
        ),
        migrations.AddField(
            model_name="shippingmethod",
            name="requires_address",
            field=models.BooleanField(default=True, verbose_name="نیازمند نشانی کامل"),
        ),
        migrations.AddField(
            model_name="shippingmethod",
            name="requires_postal_code",
            field=models.BooleanField(default=False, verbose_name="نیازمند کد پستی"),
        ),
        migrations.AddField(
            model_name="shippingmethod",
            name="customer_notice",
            field=models.CharField(blank=True, default="", max_length=300, verbose_name="توضیح روش ارسال برای مشتری"),
        ),
        migrations.CreateModel(
            name="StorePaymentSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(default="اطلاعات پرداخت کارت به کارت", max_length=160, verbose_name="عنوان نمایشی")),
                ("bank_name", models.CharField(blank=True, max_length=120, verbose_name="نام بانک")),
                ("account_holder", models.CharField(blank=True, max_length=160, verbose_name="نام صاحب حساب")),
                ("card_number", models.CharField(blank=True, max_length=32, verbose_name="شماره کارت")),
                ("sheba_number", models.CharField(blank=True, max_length=40, verbose_name="شماره شبا")),
                ("account_number", models.CharField(blank=True, max_length=40, verbose_name="شماره حساب")),
                ("transfer_instructions", models.TextField(blank=True, verbose_name="راهنمای واریز برای مشتری")),
                ("is_active", models.BooleanField(default=True, verbose_name="نمایش اطلاعات پرداخت")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "اطلاعات پرداخت کارت به کارت",
                "verbose_name_plural": "اطلاعات پرداخت کارت به کارت",
            },
        ),
        migrations.RunPython(backfill_fixed_products, migrations.RunPython.noop),
        migrations.RunPython(create_shipping_presets, migrations.RunPython.noop),
    ]
