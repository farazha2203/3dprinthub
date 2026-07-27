from decimal import Decimal, ROUND_HALF_UP

from django.db import migrations, models


def seed_material_pricing(apps, schema_editor):
    Material = apps.get_model("website", "Material")
    for material in Material.objects.all().iterator():
        legacy_kg = int(material.price_per_kg or 0)
        sale_per_gram = 0
        if legacy_kg:
            sale_per_gram = int((Decimal(legacy_kg) / Decimal("1000")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        Material.objects.filter(pk=material.pk).update(
            default_roll_weight_grams=Decimal("1000"),
            default_purchase_price_per_roll=legacy_kg,
            sale_price_per_gram=sale_per_gram,
        )


class Migration(migrations.Migration):
    dependencies = [("website", "0009_iran_locations_and_merchant_seo")]

    operations = [
        migrations.AddField(
            model_name="material",
            name="default_purchase_price_per_roll",
            field=models.PositiveBigIntegerField(default=0, verbose_name="قیمت خرید پیش‌فرض هر رول"),
        ),
        migrations.AddField(
            model_name="material",
            name="default_roll_weight_grams",
            field=models.DecimalField(decimal_places=2, default=1000, max_digits=10, verbose_name="وزن پیش‌فرض هر رول به گرم"),
        ),
        migrations.AddField(
            model_name="material",
            name="reorder_threshold_grams",
            field=models.DecimalField(decimal_places=2, default=250, max_digits=12, verbose_name="حد هشدار سفارش مجدد به گرم"),
        ),
        migrations.AddField(
            model_name="material",
            name="sale_price_per_gram",
            field=models.PositiveIntegerField(default=0, verbose_name="قیمت فروش هر گرم"),
        ),
        migrations.AddField(
            model_name="material",
            name="track_filament_inventory",
            field=models.BooleanField(default=False, verbose_name="کنترل موجودی وزنی فیلامنت"),
        ),
        migrations.RunPython(seed_material_pricing, migrations.RunPython.noop),
    ]
