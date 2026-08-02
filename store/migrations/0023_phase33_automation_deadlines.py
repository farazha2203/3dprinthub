from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0022_phase29_source_kind_state_sync"),
    ]

    operations = [
        migrations.AlterField(
            model_name="catalogsyncrun",
            name="status",
            field=models.CharField(
                choices=[
                    ("queued", "در صف"),
                    ("running", "در حال اجرا"),
                    ("completed", "تکمیل‌شده"),
                    ("partial", "نیمه‌کامل"),
                    ("failed", "ناموفق"),
                    ("cancelled", "متوقف‌شده"),
                ],
                db_index=True,
                default="queued",
                max_length=20,
                verbose_name="وضعیت",
            ),
        ),
        migrations.AddField(
            model_name="catalogsyncrun",
            name="cancelled_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="زمان توقف دستی"),
        ),
        migrations.AddField(
            model_name="catalogsyncrun",
            name="deadline_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="مهلت پایان"),
        ),
        migrations.AddField(
            model_name="catalogsyncrun",
            name="heartbeat_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="آخرین فعالیت"),
        ),
        migrations.AlterField(
            model_name="externalsourcefetchlog",
            name="status",
            field=models.CharField(
                choices=[
                    ("queued", "در صف"),
                    ("running", "در حال اجرا"),
                    ("success", "موفق"),
                    ("partial", "نسبی"),
                    ("failed", "ناموفق"),
                    ("cancelled", "متوقف‌شده"),
                ],
                db_index=True,
                default="queued",
                max_length=20,
                verbose_name="وضعیت",
            ),
        ),
        migrations.AddField(
            model_name="externalsourcefetchlog",
            name="cancelled_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="زمان توقف دستی"),
        ),
        migrations.AddField(
            model_name="externalsourcefetchlog",
            name="deadline_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="مهلت پایان"),
        ),
        migrations.AddField(
            model_name="externalsourcefetchlog",
            name="heartbeat_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="آخرین فعالیت"),
        ),
    ]
