from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0022_phase49_hero_media_presentation"),
    ]

    operations = [
        migrations.AddField(
            model_name="material",
            name="print_hourly_rate_toman",
            field=models.PositiveBigIntegerField(
                default=0,
                verbose_name="نرخ ساعتی چاپ این متریال (تومان)",
            ),
        ),
        migrations.AddField(
            model_name="material",
            name="supervision_hourly_rate_toman",
            field=models.PositiveBigIntegerField(
                default=0,
                verbose_name="نرخ ساعتی نظارت اپراتور برای این متریال (تومان)",
            ),
        ),
    ]
