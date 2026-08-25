from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0034_phase50_variant2_commerce"),
    ]

    operations = [
        migrations.AddField(
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
                ],
                db_index=True,
                default="size_build",
                help_text="تعیین می‌کند مشتری پروفایل‌های این محصول را بر اساس سایز، وزن، مدل ساخت یا ترکیب آن‌ها انتخاب کند.",
                max_length=24,
                verbose_name="روش انتخاب پروفایل فروش",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="sales_profile_selector_label",
            field=models.CharField(
                blank=True,
                default="",
                help_text="مثال: سایز و مدل ساخت را انتخاب کنید. اگر خالی باشد عنوان مناسب خودکار نمایش داده می‌شود.",
                max_length=120,
                verbose_name="عنوان انتخاب پروفایل",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="sales_profile_name",
            field=models.CharField(
                blank=True,
                default="",
                help_text="مثال: 24 سانتی‌متر سبک یا 300 گرم توپر.",
                max_length=120,
                verbose_name="نام پروفایل فروش",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="sales_profile_key",
            field=models.CharField(
                blank=True,
                db_index=True,
                default="",
                help_text="شناسه داخلی برای اجازه داشتن چند پروفایل با متریال/رنگ/سایز مشابه اما وزن، زمان چاپ یا قیمت متفاوت.",
                max_length=80,
                verbose_name="کلید پروفایل",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="sales_profile_sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش پروفایل"),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="sales_profile_is_default",
            field=models.BooleanField(db_index=True, default=False, verbose_name="پروفایل پیش‌فرض"),
        ),
        migrations.RemoveConstraint(
            model_name="productvariant",
            name="uniq_product_material_quality_color_size_build",
        ),
        migrations.AddConstraint(
            model_name="productvariant",
            constraint=models.UniqueConstraint(
                fields=(
                    "product",
                    "material",
                    "quality",
                    "color",
                    "size_label",
                    "build_profile",
                    "sales_profile_key",
                ),
                name="uniq_product_material_quality_color_size_build_profile",
            ),
        ),
    ]
