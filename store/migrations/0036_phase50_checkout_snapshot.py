from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0035_phase50_sales_profiles"),
    ]

    operations = [
        migrations.AddField(
            model_name="storeorder",
            name="insured_value",
            field=models.PositiveBigIntegerField(
                default=0,
                verbose_name="ارزش اظهارشده / بیمه مرسوله",
            ),
        ),
        migrations.AddField(
            model_name="storeorder",
            name="shipping_quote_snapshot",
            field=models.JSONField(
                blank=True,
                default=dict,
                verbose_name="اسنپ‌شات محاسبه ارسال",
            ),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="sales_profile_name",
            field=models.CharField(
                blank=True,
                default="",
                max_length=120,
                verbose_name="نام پروفایل هنگام سفارش",
            ),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="sales_profile_key",
            field=models.CharField(
                blank=True,
                default="",
                max_length=80,
                verbose_name="کلید پروفایل هنگام سفارش",
            ),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="sales_profile_label",
            field=models.CharField(
                blank=True,
                default="",
                max_length=180,
                verbose_name="عنوان نمایشی پروفایل هنگام سفارش",
            ),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="sales_profile_selection_mode",
            field=models.CharField(
                blank=True,
                default="",
                max_length=24,
                verbose_name="روش انتخاب پروفایل هنگام سفارش",
            ),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="sales_profile_selection_value",
            field=models.CharField(
                blank=True,
                default="",
                max_length=180,
                verbose_name="انتخاب قابل مشاهده مشتری هنگام سفارش",
            ),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="final_weight_grams",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name="وزن نهایی قطعه هنگام سفارش",
            ),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="shipping_weight_grams",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name="وزن قابل محاسبه ارسال هنگام سفارش",
            ),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="print_time_minutes",
            field=models.PositiveIntegerField(
                default=0,
                verbose_name="زمان چاپ هنگام سفارش به دقیقه",
            ),
        ),
    ]
