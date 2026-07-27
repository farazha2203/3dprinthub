from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0014_phase16_bambu_price_history"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImportedPrintAssetPrintProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_key", models.CharField(blank=True, max_length=160, verbose_name="شناسه پروفایل منبع")),
                ("profile_name", models.CharField(default="پروفایل چاپ", max_length=220, verbose_name="نام پروفایل")),
                ("weight_grams", models.DecimalField(blank=True, db_index=True, decimal_places=2, max_digits=12, null=True, verbose_name="وزن چاپ (گرم)")),
                ("print_minutes", models.PositiveIntegerField(blank=True, null=True, verbose_name="زمان چاپ (دقیقه)")),
                ("material", models.CharField(blank=True, max_length=120, verbose_name="متریال پیشنهادی")),
                ("nozzle_mm", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="نازل (میلی‌متر)")),
                ("layer_height_mm", models.DecimalField(blank=True, decimal_places=3, max_digits=5, null=True, verbose_name="ارتفاع لایه")),
                ("infill_percent", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="درصد پرشدگی")),
                ("source_payload", models.JSONField(blank=True, default=dict, verbose_name="داده خام پروفایل")),
                ("is_manual", models.BooleanField(db_index=True, default=False, verbose_name="ثبت دستی")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("asset", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="print_profiles", to="store.importedprintasset", verbose_name="مدل دریافت‌شده")),
            ],
            options={
                "verbose_name": "وزن و پروفایل چاپ",
                "verbose_name_plural": "وزن‌ها و پروفایل‌های چاپ مدل‌ها",
                "ordering": ["weight_grams", "profile_name", "id"],
            },
        ),
        migrations.AddConstraint(
            model_name="importedprintassetprintprofile",
            constraint=models.UniqueConstraint(
                condition=~models.Q(("source_key", "")),
                fields=("asset", "source_key"),
                name="store_asset_profile_source_key_uniq",
            ),
        ),
    ]
