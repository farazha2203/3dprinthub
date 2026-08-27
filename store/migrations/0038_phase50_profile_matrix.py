from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0037_phase50_professional_commerce_policy"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="sales_profile_selection_mode",
            field=models.CharField(
                choices=[
                    ("list", "فهرست کامل پروفایل‌ها"),
                    ("size", "انتخاب بر اساس سایز"),
                    ("weight", "انتخاب بر اساس وزن"),
                    ("build", "انتخاب بر اساس مدل ساخت"),
                    ("size_build", "سایز ← مدل ساخت"),
                    ("build_size", "مدل ساخت ← سایز"),
                    ("size_weight", "سایز ← وزن"),
                    ("weight_size", "وزن ← سایز"),
                    ("size_weight_build", "سایز ← وزن ← مدل ساخت"),
                    ("size_build_weight", "سایز ← مدل ساخت ← وزن"),
                ],
                db_index=True,
                default="size_build",
                help_text="تعیین می‌کند مشتری پروفایل‌های این محصول را بر اساس سایز، وزن، مدل ساخت یا ترکیب آن‌ها انتخاب کند.",
                max_length=24,
                verbose_name="روش انتخاب پروفایل فروش",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="sales_profile_description",
            field=models.CharField(
                blank=True,
                default="",
                help_text="مثال: سبک‌تر و اقتصادی، یا سنگین‌تر و مقاوم‌تر.",
                max_length=300,
                verbose_name="توضیح کوتاه پروفایل",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="part_length_cm",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                verbose_name="طول خود قطعه به سانتی‌متر",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="part_width_cm",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                verbose_name="عرض خود قطعه به سانتی‌متر",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="part_height_cm",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                verbose_name="ارتفاع خود قطعه به سانتی‌متر",
            ),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="part_length_cm",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                verbose_name="طول قطعه هنگام سفارش",
            ),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="part_width_cm",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                verbose_name="عرض قطعه هنگام سفارش",
            ),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="part_height_cm",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                verbose_name="ارتفاع قطعه هنگام سفارش",
            ),
        ),
    ]
