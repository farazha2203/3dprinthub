from django.db import migrations, models


def seed_brands(apps, schema_editor):
    Option = apps.get_model("store", "MaterialColorOption")
    Brand = apps.get_model("store", "FilamentBrand")
    seen = set()
    for value in Option.objects.exclude(brand_name="").values_list("brand_name", flat=True).iterator():
        name = str(value or "").strip()
        key = name.casefold()
        if not name or key in seen:
            continue
        seen.add(key)
        Brand.objects.get_or_create(name=name, defaults={"is_active": True})


def reverse_seed(apps, schema_editor):
    return None


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0024_phase49_3i51_material_catalog_description"),
        ("store", "0041_phase50_filament_visual_identity"),
    ]

    operations = [
        migrations.CreateModel(
            name="FilamentBrand",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_index=True, max_length=120, unique=True, verbose_name="نام برند")),
                ("description", models.TextField(blank=True, default="", verbose_name="توضیح برند / SEO")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
                ("sort_order", models.PositiveIntegerField(default=100, verbose_name="ترتیب")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "برند فیلامنت",
                "verbose_name_plural": "برندهای فیلامنت",
                "ordering": ["sort_order", "name", "id"],
            },
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="description",
            field=models.TextField(blank=True, default="", verbose_name="توضیح Filament / SEO"),
        ),
        migrations.RunPython(seed_brands, reverse_seed),
    ]
