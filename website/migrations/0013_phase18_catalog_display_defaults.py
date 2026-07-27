from django.db import migrations, models


def set_default_grid_to_nine(apps, schema_editor):
    Setting = apps.get_model("website", "HomePresentationSetting")
    Setting.objects.filter(catalog_preview_count=8).update(catalog_preview_count=9)


def restore_previous_grid_default(apps, schema_editor):
    Setting = apps.get_model("website", "HomePresentationSetting")
    Setting.objects.filter(catalog_preview_count=9).update(catalog_preview_count=8)


class Migration(migrations.Migration):
    dependencies = [("website", "0012_home_presentation_team_clients")]
    operations = [
        migrations.AlterField(
            model_name="homepresentationsetting",
            name="catalog_preview_count",
            field=models.PositiveSmallIntegerField(
                default=9,
                help_text="مدل‌ها در شبکه سه‌ستونه نمایش داده می‌شوند؛ مقدار پیشنهادی ۹ است.",
                verbose_name="تعداد مدل در بخش معرفی",
            ),
        ),
        migrations.RunPython(set_default_grid_to_nine, restore_previous_grid_default),
    ]
