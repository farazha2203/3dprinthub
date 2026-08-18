from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0030_phase49_unified_sync_contract"),
    ]

    operations = [
        migrations.AddField(
            model_name="materialcoloroption",
            name="color_type",
            field=models.CharField(
                choices=[
                    ("solid", "ساده"),
                    ("transparent", "شفاف / شیشه‌ای"),
                    ("translucent", "نیمه‌شفاف"),
                    ("metallic", "متالیک"),
                    ("silk", "Silk / ابریشمی"),
                    ("dual", "دو رنگ"),
                    ("multicolor", "چند رنگ"),
                    ("gradient", "گرادیانی"),
                ],
                db_index=True,
                default="solid",
                max_length=20,
                verbose_name="نوع رنگ",
            ),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="secondary_hex",
            field=models.CharField(blank=True, max_length=20, verbose_name="HEX دوم"),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="tertiary_hex",
            field=models.CharField(blank=True, max_length=20, verbose_name="HEX سوم"),
        ),
        migrations.AlterField(
            model_name="materialcoloroption",
            name="hex_code",
            field=models.CharField(blank=True, max_length=20, verbose_name="کد HEX اصلی"),
        ),
    ]
