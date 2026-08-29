from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0039_phase50_filament_offer_pricing"),
    ]

    operations = [
        migrations.AddField(
            model_name="materialcoloroption",
            name="print_hourly_rate",
            field=models.PositiveBigIntegerField(
                default=0,
                verbose_name="نرخ ساعت چاپ این Offer",
            ),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="supervision_hourly_rate",
            field=models.PositiveBigIntegerField(
                default=0,
                verbose_name="نرخ ساعت نظارت این Offer",
            ),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="preheat_hours",
            field=models.DecimalField(
                max_digits=8,
                decimal_places=2,
                default=0,
                verbose_name="مدت پیش‌گرم فیلامنت (ساعت)",
            ),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="preheat_temperature_c",
            field=models.DecimalField(
                max_digits=7,
                decimal_places=2,
                default=0,
                verbose_name="دمای پیش‌گرم فیلامنت (°C)",
            ),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="preheat_hourly_rate",
            field=models.PositiveBigIntegerField(
                default=0,
                verbose_name="هزینه ساعتی پیش‌گرم",
            ),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="filament_image_url",
            field=models.URLField(
                blank=True,
                default="",
                max_length=500,
                verbose_name="تصویر فیلامنت",
            ),
        ),
    ]
