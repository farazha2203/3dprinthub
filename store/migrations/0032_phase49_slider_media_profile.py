from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0031_phase49_rich_material_colors"),
    ]

    operations = [
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_presentation_mode",
            field=models.CharField(
                choices=[
                    ("product_fit", "نمایش کامل محصول"),
                    ("full_bleed", "پر کردن کامل اسلایدر"),
                    ("framed", "کادر محصول"),
                    ("cinematic", "سینمایی با پس‌زمینه"),
                ],
                default="product_fit",
                max_length=20,
                verbose_name="حالت ارائه تصویر اسلایدر",
            ),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_object_fit",
            field=models.CharField(
                choices=[("contain", "نمایش کامل"), ("cover", "پر کردن کامل")],
                default="contain",
                max_length=12,
                verbose_name="Object Fit اسلایدر",
            ),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_focal_position",
            field=models.CharField(
                choices=[
                    ("center", "وسط"), ("top", "بالا"), ("bottom", "پایین"),
                    ("left", "چپ"), ("right", "راست"),
                ],
                default="center",
                max_length=12,
                verbose_name="نقطه تمرکز اسلایدر",
            ),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_image_scale_percent",
            field=models.PositiveSmallIntegerField(
                default=100,
                validators=[MinValueValidator(60), MaxValueValidator(140)],
                verbose_name="مقیاس تصویر اسلایدر درصد",
            ),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_position_x_percent",
            field=models.PositiveSmallIntegerField(
                default=50,
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                verbose_name="موقعیت افقی تصویر اسلایدر درصد",
            ),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_position_y_percent",
            field=models.PositiveSmallIntegerField(
                default=50,
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                verbose_name="موقعیت عمودی تصویر اسلایدر درصد",
            ),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_background_mode",
            field=models.CharField(
                choices=[
                    ("solid", "رنگ ثابت"),
                    ("blur", "پس‌زمینه Blur از تصویر"),
                    ("gradient", "گرادیان"),
                    ("image", "خود تصویر"),
                ],
                default="blur",
                max_length=20,
                verbose_name="حالت پس‌زمینه اسلایدر",
            ),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_background_color",
            field=models.CharField(default="#071827", max_length=24, verbose_name="رنگ پس‌زمینه اسلایدر"),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_background_blur_px",
            field=models.PositiveSmallIntegerField(
                default=18,
                validators=[MinValueValidator(0), MaxValueValidator(60)],
                verbose_name="Blur پس‌زمینه اسلایدر",
            ),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_desktop_max_width_percent",
            field=models.PositiveSmallIntegerField(
                default=78,
                validators=[MinValueValidator(30), MaxValueValidator(100)],
                verbose_name="حداکثر عرض تصویر دسکتاپ درصد",
            ),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_desktop_max_height_percent",
            field=models.PositiveSmallIntegerField(
                default=88,
                validators=[MinValueValidator(30), MaxValueValidator(100)],
                verbose_name="حداکثر ارتفاع تصویر دسکتاپ درصد",
            ),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_mobile_max_width_percent",
            field=models.PositiveSmallIntegerField(
                default=92,
                validators=[MinValueValidator(30), MaxValueValidator(100)],
                verbose_name="حداکثر عرض تصویر موبایل درصد",
            ),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_mobile_max_height_percent",
            field=models.PositiveSmallIntegerField(
                default=72,
                validators=[MinValueValidator(30), MaxValueValidator(100)],
                verbose_name="حداکثر ارتفاع تصویر موبایل درصد",
            ),
        ),
    ]
