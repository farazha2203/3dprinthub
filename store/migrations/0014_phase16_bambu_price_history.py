from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def seed_existing_prices(apps, schema_editor):
    Item = apps.get_model("store", "BambuFilamentCatalogItem")
    History = apps.get_model("store", "BambuFilamentPriceHistory")
    now = django.utils.timezone.now()
    rows = []
    for item in Item.objects.all().iterator():
        rows.append(
            History(
                item_id=item.pk,
                observed_at=getattr(item, "last_seen_at", None) or now,
                min_price_usd=item.min_price_usd,
                max_price_usd=item.max_price_usd,
                conservative_price_usd=item.conservative_price_usd,
                previous_conservative_price_usd=None,
                delta_usd=Decimal("0"),
                delta_percent=Decimal("0"),
                available=item.available,
                changed=False,
                source_mode="phase16_baseline",
                variants=item.variants or [],
            )
        )
    if rows:
        History.objects.bulk_create(rows, batch_size=500)


def remove_seeded_baselines(apps, schema_editor):
    History = apps.get_model("store", "BambuFilamentPriceHistory")
    History.objects.filter(source_mode="phase16_baseline").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0013_phase12_resilient_sources"),
    ]

    operations = [
        migrations.CreateModel(
            name="BambuFilamentPriceHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("observed_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="زمان مشاهده")),
                ("min_price_usd", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="کمترین قیمت جدید")),
                ("max_price_usd", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="بیشترین قیمت جدید")),
                ("conservative_price_usd", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="قیمت جدید")),
                ("previous_conservative_price_usd", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="قیمت قبلی")),
                ("delta_usd", models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name="تغییر دلاری")),
                ("delta_percent", models.DecimalField(decimal_places=4, default=0, max_digits=12, verbose_name="درصد تغییر")),
                ("available", models.BooleanField(db_index=True, default=True, verbose_name="موجود")),
                ("changed", models.BooleanField(db_index=True, default=False, verbose_name="قیمت تغییر کرده")),
                ("source_mode", models.CharField(blank=True, max_length=80, verbose_name="روش دریافت")),
                ("variants", models.JSONField(blank=True, default=list, verbose_name="تنوع‌ها و قیمت‌ها")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("item", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="price_history", to="store.bambufilamentcatalogitem", verbose_name="محصول Bambu")),
            ],
            options={
                "verbose_name": "تاریخچه قیمت Bambu",
                "verbose_name_plural": "تاریخچه قیمت‌های Bambu Lab",
                "ordering": ["-observed_at", "-id"],
            },
        ),
        migrations.AddIndex(
            model_name="bambufilamentpricehistory",
            index=models.Index(fields=["item", "-observed_at"], name="store_bambu_hist_item_idx"),
        ),
        migrations.AddIndex(
            model_name="bambufilamentpricehistory",
            index=models.Index(fields=["changed", "-observed_at"], name="store_bambu_hist_chg_idx"),
        ),
        migrations.RunPython(seed_existing_prices, remove_seeded_baselines),
    ]
