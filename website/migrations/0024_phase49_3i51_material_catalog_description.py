from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0023_phase49_3f_material_runtime_rates"),
    ]

    operations = [
        migrations.AddField(
            model_name="material",
            name="catalog_description",
            field=models.TextField(
                blank=True,
                default="",
                verbose_name="توضیح متریال / SEO",
            ),
        ),
    ]
