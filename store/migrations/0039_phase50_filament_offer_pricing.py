from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0038_phase50_profile_matrix"),
    ]

    operations = [
        migrations.AddField(
            model_name="materialcoloroption",
            name="brand_name",
            field=models.CharField(blank=True, default="", max_length=120, verbose_name="برند فیلامنت"),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="manufacturer_name",
            field=models.CharField(blank=True, default="", max_length=160, verbose_name="کارخانه / سازنده فیلامنت"),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="roll_weight_grams",
            field=models.DecimalField(decimal_places=2, default=1000, max_digits=10, verbose_name="وزن هر رول به گرم"),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="stock_roll_count_snapshot",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="اسنپ‌شات تعداد رول موجود"),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="purchase_price_per_roll",
            field=models.PositiveBigIntegerField(default=0, verbose_name="قیمت خرید هر رول"),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="sale_price_per_roll",
            field=models.PositiveBigIntegerField(default=0, verbose_name="قیمت فروش هر رول"),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="usd_price_per_roll",
            field=models.DecimalField(decimal_places=4, default=0, max_digits=14, verbose_name="قیمت دلاری هر رول"),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="usd_fx_rate_toman",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name="نرخ دلار ثبت‌شده برای این رول"),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="support_weight_grams",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="وزن ساپورت مصرفی"),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="support_weight_grams",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="وزن ساپورت هنگام سفارش"),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="filament_brand_name",
            field=models.CharField(blank=True, default="", max_length=120, verbose_name="برند فیلامنت هنگام سفارش"),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="filament_manufacturer_name",
            field=models.CharField(blank=True, default="", max_length=160, verbose_name="سازنده فیلامنت هنگام سفارش"),
        ),
    ]
