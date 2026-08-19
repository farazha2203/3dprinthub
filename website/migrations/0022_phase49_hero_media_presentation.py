from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0021_phase49_unified_hero_sync"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepageheroslide",
            name="presentation_mode",
            field=models.CharField(
                choices=[
                    ("product_fit", "نمایش کامل محصول"),
                    ("full_bleed", "پر کردن کامل اسلایدر"),
                    ("framed", "کادر محصول"),
                    ("cinematic", "سینمایی با پس‌زمینه"),
                ],
                default="product_fit",
                max_length=20,
                verbose_name="حالت ارائه تصویر",
            ),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="image_scale_percent",
            field=models.PositiveSmallIntegerField(
                default=100,
                validators=[MinValueValidator(60), MaxValueValidator(140)],
                verbose_name="مقیاس تصویر درصد",
            ),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="image_position_x_percent",
            field=models.PositiveSmallIntegerField(
                default=50,
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                verbose_name="موقعیت افقی تصویر درصد",
            ),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="image_position_y_percent",
            field=models.PositiveSmallIntegerField(
                default=50,
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                verbose_name="موقعیت عمودی تصویر درصد",
            ),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="background_mode",
            field=models.CharField(
                choices=[
                    ("solid", "رنگ ثابت"),
                    ("blur", "پس‌زمینه Blur از تصویر"),
                    ("gradient", "گرادیان"),
                    ("image", "خود تصویر"),
                ],
                default="blur",
                max_length=20,
                verbose_name="حالت پس‌زمینه Hero",
            ),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="background_color",
            field=models.CharField(default="#071827", max_length=24, verbose_name="رنگ پس‌زمینه Hero"),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="background_blur_px",
            field=models.PositiveSmallIntegerField(
                default=18,
                validators=[MinValueValidator(0), MaxValueValidator(60)],
                verbose_name="Blur پس‌زمینه پیکسل",
            ),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="desktop_max_width_percent",
            field=models.PositiveSmallIntegerField(
                default=78,
                validators=[MinValueValidator(30), MaxValueValidator(100)],
                verbose_name="حداکثر عرض تصویر دسکتاپ درصد",
            ),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="desktop_max_height_percent",
            field=models.PositiveSmallIntegerField(
                default=88,
                validators=[MinValueValidator(30), MaxValueValidator(100)],
                verbose_name="حداکثر ارتفاع تصویر دسکتاپ درصد",
            ),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="mobile_max_width_percent",
            field=models.PositiveSmallIntegerField(
                default=92,
                validators=[MinValueValidator(30), MaxValueValidator(100)],
                verbose_name="حداکثر عرض تصویر موبایل درصد",
            ),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="mobile_max_height_percent",
            field=models.PositiveSmallIntegerField(
                default=72,
                validators=[MinValueValidator(30), MaxValueValidator(100)],
                verbose_name="حداکثر ارتفاع تصویر موبایل درصد",
            ),
        ),
    ]
