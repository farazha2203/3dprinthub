from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0020_phase49_2c_hero_studio"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepageheroslide",
            name="sync_revision",
            field=models.PositiveBigIntegerField(db_index=True, default=1, verbose_name="نسخه همگام‌سازی"),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="last_modified_source",
            field=models.CharField(db_index=True, default="desktop", max_length=20, verbose_name="منبع آخرین تغییر"),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="last_modified_by",
            field=models.CharField(blank=True, max_length=120, verbose_name="عامل آخرین تغییر"),
        ),
    ]
