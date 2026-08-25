from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0033_phase49_3f_pricing_intelligence"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="productvariant",
            name="uniq_product_material_quality_color",
        ),
        migrations.AddField(
            model_name="productvariant",
            name="size_label",
            field=models.CharField(blank=True, default="", help_text="مثال: 20 سانتی‌متر، 24 سانتی‌متر یا Large.", max_length=80, verbose_name="سایز / ابعاد فروش"),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="build_profile",
            field=models.CharField(choices=[("standard", "استاندارد"), ("hollow", "توخالی / سبک"), ("reinforced", "تقویت‌شده"), ("solid", "توپر / سنگین"), ("custom", "سفارشی")], db_index=True, default="standard", max_length=20, verbose_name="مدل ساخت / میزان پُری"),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="packaging_weight_grams",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name="وزن بسته‌بندی به گرم"),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="package_length_cm",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name="طول بسته به سانتی‌متر"),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="package_width_cm",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name="عرض بسته به سانتی‌متر"),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="package_height_cm",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name="ارتفاع بسته به سانتی‌متر"),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="size_label",
            field=models.CharField(blank=True, default="", max_length=80, verbose_name="سایز هنگام سفارش"),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="build_profile",
            field=models.CharField(blank=True, default="standard", max_length=20, verbose_name="مدل ساخت هنگام سفارش"),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="packaging_weight_grams",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="وزن بسته‌بندی هنگام سفارش"),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="package_length_cm",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name="طول بسته هنگام سفارش"),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="package_width_cm",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name="عرض بسته هنگام سفارش"),
        ),
        migrations.AddField(
            model_name="storeorderitem",
            name="package_height_cm",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name="ارتفاع بسته هنگام سفارش"),
        ),
        migrations.AddConstraint(
            model_name="productvariant",
            constraint=models.UniqueConstraint(
                fields=("product", "material", "quality", "color", "size_label", "build_profile"),
                name="uniq_product_material_quality_color_size_build",
            ),
        ),
    ]
