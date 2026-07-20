# Generated for 3DprintHub Store Commerce Phase 2
import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import store.models


def create_default_shipping(apps, schema_editor):
    ShippingMethod = apps.get_model("store", "ShippingMethod")
    ShippingMethod.objects.get_or_create(
        code="pickup",
        defaults={
            "title": "تحویل حضوری در اصفهان",
            "description": "تحویل حضوری با هماهنگی قبلی",
            "flat_fee": 0,
            "sort_order": 0,
            "is_active": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShippingMethod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.SlugField(max_length=50, unique=True, verbose_name="کد روش ارسال")),
                ("title", models.CharField(max_length=120, verbose_name="عنوان روش ارسال")),
                ("description", models.CharField(blank=True, max_length=300, verbose_name="توضیحات")),
                ("flat_fee", models.PositiveIntegerField(default=0, verbose_name="هزینه ثابت ارسال به تومان")),
                ("free_over", models.PositiveIntegerField(default=0, verbose_name="ارسال رایگان از مبلغ")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
            ],
            options={"verbose_name": "روش ارسال فروشگاه", "verbose_name_plural": "روش‌های ارسال فروشگاه", "ordering": ["sort_order", "title"]},
        ),
        migrations.CreateModel(
            name="StoreAddress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(default="آدرس اصلی", max_length=80, verbose_name="عنوان آدرس")),
                ("full_name", models.CharField(max_length=150, verbose_name="نام تحویل‌گیرنده")),
                ("phone", models.CharField(max_length=20, verbose_name="شماره تماس")),
                ("province", models.CharField(max_length=100, verbose_name="استان")),
                ("city", models.CharField(max_length=100, verbose_name="شهر")),
                ("address", models.TextField(verbose_name="نشانی کامل")),
                ("postal_code", models.CharField(blank=True, max_length=20, verbose_name="کد پستی")),
                ("is_default", models.BooleanField(db_index=True, default=False, verbose_name="آدرس پیش‌فرض")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="store_addresses", to=settings.AUTH_USER_MODEL, verbose_name="کاربر")),
            ],
            options={"verbose_name": "آدرس فروشگاهی مشتری", "verbose_name_plural": "آدرس‌های فروشگاهی مشتریان", "ordering": ["-is_default", "-updated_at"]},
        ),
        migrations.CreateModel(
            name="StoreOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_number", models.CharField(db_index=True, default=store.models.generate_store_order_number, editable=False, max_length=40, unique=True, verbose_name="شماره سفارش فروشگاه")),
                ("status", models.CharField(choices=[("awaiting_payment", "در انتظار پرداخت"), ("payment_review", "در انتظار بررسی پرداخت"), ("paid", "پرداخت شده"), ("processing", "در حال تولید"), ("ready", "آماده ارسال"), ("shipped", "ارسال شده"), ("delivered", "تحویل شده"), ("cancelled", "لغو شده"), ("refunded", "مسترد شده")], db_index=True, default="awaiting_payment", max_length=30, verbose_name="وضعیت سفارش")),
                ("payment_status", models.CharField(choices=[("pending", "در انتظار پرداخت"), ("awaiting_review", "در انتظار بررسی رسید"), ("paid", "پرداخت موفق"), ("failed", "پرداخت ناموفق"), ("refunded", "مسترد شده")], db_index=True, default="pending", max_length=30, verbose_name="وضعیت پرداخت")),
                ("shipping_title", models.CharField(max_length=120, verbose_name="عنوان روش ارسال هنگام سفارش")),
                ("full_name", models.CharField(max_length=150, verbose_name="نام تحویل‌گیرنده")),
                ("phone", models.CharField(db_index=True, max_length=20, verbose_name="شماره تماس")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="ایمیل")),
                ("province", models.CharField(max_length=100, verbose_name="استان")),
                ("city", models.CharField(max_length=100, verbose_name="شهر")),
                ("address", models.TextField(verbose_name="نشانی کامل")),
                ("postal_code", models.CharField(blank=True, max_length=20, verbose_name="کد پستی")),
                ("customer_note", models.TextField(blank=True, verbose_name="توضیحات مشتری")),
                ("admin_note", models.TextField(blank=True, verbose_name="یادداشت داخلی")),
                ("tracking_code", models.CharField(blank=True, max_length=100, verbose_name="کد رهگیری ارسال")),
                ("subtotal", models.PositiveBigIntegerField(default=0, verbose_name="جمع کالاها")),
                ("packaging_fee", models.PositiveBigIntegerField(default=0, verbose_name="هزینه بسته‌بندی")),
                ("shipping_fee", models.PositiveBigIntegerField(default=0, verbose_name="هزینه ارسال")),
                ("tax_amount", models.PositiveBigIntegerField(default=0, verbose_name="مالیات")),
                ("discount_amount", models.PositiveBigIntegerField(default=0, verbose_name="تخفیف")),
                ("total_amount", models.PositiveBigIntegerField(default=0, verbose_name="مبلغ نهایی")),
                ("total_weight_grams", models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name="وزن ارسال")),
                ("paid_at", models.DateTimeField(blank=True, null=True, verbose_name="تاریخ پرداخت")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("shipping_method", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to="store.shippingmethod", verbose_name="روش ارسال")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="store_orders", to=settings.AUTH_USER_MODEL, verbose_name="مشتری")),
            ],
            options={"verbose_name": "سفارش فروشگاهی", "verbose_name_plural": "سفارش‌های فروشگاهی", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="StoreOrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_title", models.CharField(max_length=220, verbose_name="نام محصول هنگام سفارش")),
                ("product_sku", models.CharField(max_length=80, verbose_name="کد محصول هنگام سفارش")),
                ("variant_code", models.CharField(max_length=100, verbose_name="کد تنوع هنگام سفارش")),
                ("material_name", models.CharField(max_length=100, verbose_name="متریال هنگام سفارش")),
                ("quality_name", models.CharField(max_length=100, verbose_name="کیفیت هنگام سفارش")),
                ("unit_price", models.PositiveBigIntegerField(verbose_name="قیمت واحد هنگام سفارش")),
                ("quantity", models.PositiveIntegerField(default=1, verbose_name="تعداد")),
                ("line_total", models.PositiveBigIntegerField(verbose_name="جمع ردیف")),
                ("unit_weight_grams", models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="وزن واحد")),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="store.storeorder", verbose_name="سفارش")),
                ("product", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="store_order_items", to="store.product", verbose_name="محصول")),
                ("variant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="store_order_items", to="store.productvariant", verbose_name="تنوع")),
            ],
            options={"verbose_name": "ردیف سفارش فروشگاهی", "verbose_name_plural": "ردیف‌های سفارش فروشگاهی", "ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="StorePayment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.PositiveBigIntegerField(verbose_name="مبلغ")),
                ("method", models.CharField(choices=[("bank_transfer", "کارت به کارت / واریز بانکی"), ("gateway", "درگاه آنلاین")], default="bank_transfer", max_length=30, verbose_name="روش")),
                ("status", models.CharField(choices=[("pending", "در انتظار پرداخت"), ("awaiting_review", "در انتظار بررسی رسید"), ("paid", "پرداخت موفق"), ("failed", "پرداخت ناموفق"), ("cancelled", "لغو شده"), ("refunded", "مسترد شده")], db_index=True, default="pending", max_length=30, verbose_name="وضعیت")),
                ("idempotency_key", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("authority", models.CharField(blank=True, max_length=255, verbose_name="Authority")),
                ("ref_id", models.CharField(blank=True, db_index=True, max_length=255, verbose_name="کد پیگیری")),
                ("card_holder", models.CharField(blank=True, max_length=150, verbose_name="نام صاحب حساب")),
                ("receipt_image", models.ImageField(blank=True, null=True, upload_to="store/payments/receipts/", verbose_name="تصویر رسید")),
                ("note", models.TextField(blank=True, verbose_name="توضیحات پرداخت")),
                ("raw_response", models.JSONField(blank=True, default=dict, verbose_name="پاسخ خام درگاه")),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="store.storeorder", verbose_name="سفارش")),
            ],
            options={"verbose_name": "پرداخت فروشگاهی", "verbose_name_plural": "پرداخت‌های فروشگاهی", "ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="storeorder", index=models.Index(fields=["user", "-created_at"], name="store_order_user_created_idx")),
        migrations.AddIndex(model_name="storeorder", index=models.Index(fields=["status", "payment_status"], name="store_order_status_pay_idx")),
        migrations.RunPython(create_default_shipping, migrations.RunPython.noop),
    ]
