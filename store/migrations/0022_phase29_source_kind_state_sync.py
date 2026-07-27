from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0021_merge_phase27_2_phase29"),
    ]

    operations = [
        migrations.AlterField(
            model_name="catalogcategoryrule",
            name="source_kind",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "همه منابع"),
                    ("makerworld", "MakerWorld / Bambu Lab"),
                    ("printables", "Printables"),
                    ("thingiverse", "Thingiverse"),
                    ("grabcad", "GrabCAD"),
                    ("custom", "سفارشی"),
                ],
                max_length=30,
                verbose_name="منبع",
            ),
        ),
        migrations.AlterField(
            model_name="catalogsourcepolicy",
            name="source_kind",
            field=models.CharField(
                choices=[
                    ("makerworld", "MakerWorld / Bambu Lab"),
                    ("printables", "Printables"),
                    ("thingiverse", "Thingiverse"),
                    ("grabcad", "GrabCAD"),
                    ("custom", "سفارشی"),
                ],
                db_index=True,
                max_length=30,
                verbose_name="نوع منبع",
            ),
        ),
    ]
