from django.db import migrations, models
from django.db.models.deletion import CASCADE


class Migration(migrations.Migration):
    # MySQL cannot reliably roll DDL back. Keep 0028 strictly schema-only so a
    # data issue can never leave an unrecorded half-created table migration.
    atomic = False

    dependencies = [
        ("store", "0027_phase39_variant_color_fk"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductCatalogProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_slug", models.SlugField(max_length=220, unique=True, verbose_name="اسلاگ عمومی امن")),
                ("legacy_slug", models.CharField(blank=True, db_index=True, max_length=240, verbose_name="اسلاگ قبلی برای Redirect")),
                ("desktop_product_id", models.PositiveBigIntegerField(blank=True, db_index=True, null=True, verbose_name="شناسه محصول دسکتاپ")),
                ("batch_uuid", models.CharField(blank=True, db_index=True, max_length=80, verbose_name="شناسه Batch")),
                ("source_hash", models.CharField(blank=True, db_index=True, max_length=64, verbose_name="هش منبع")),
                ("product_type", models.CharField(db_index=True, default="ready_product", max_length=40, verbose_name="نوع محصول")),
                ("use_description", models.TextField(blank=True, verbose_name="شرح کاربرد")),
                ("availability_status", models.CharField(db_index=True, default="made_to_order", max_length=40, verbose_name="وضعیت عرضه")),
                ("stock_quantity", models.PositiveIntegerField(default=0, verbose_name="موجودی")),
                ("lead_time_min_days", models.PositiveIntegerField(default=1, verbose_name="حداقل زمان آماده‌سازی")),
                ("lead_time_max_days", models.PositiveIntegerField(default=1, verbose_name="حداکثر زمان آماده‌سازی")),
                ("has_3d_file", models.BooleanField(default=False, verbose_name="فایل سه‌بعدی موجود است")),
                ("commercial_license_status", models.CharField(db_index=True, default="unknown", max_length=30, verbose_name="وضعیت مجوز تجاری")),
                ("license_name", models.CharField(blank=True, max_length=200, verbose_name="نام مجوز")),
                ("license_url", models.URLField(blank=True, max_length=1000, verbose_name="لینک مجوز")),
                ("technical_features", models.JSONField(blank=True, default=dict, verbose_name="ویژگی‌های فنی")),
                ("keywords", models.JSONField(blank=True, default=list, verbose_name="کلیدواژه‌ها")),
                ("price_min", models.PositiveBigIntegerField(db_index=True, default=0, verbose_name="حداقل قیمت")),
                ("price_max", models.PositiveBigIntegerField(db_index=True, default=0, verbose_name="حداکثر قیمت")),
                ("price_mode", models.CharField(choices=[("fixed", "قیمت ثابت"), ("range", "بازه قیمت"), ("variant", "بر اساس متریال/رنگ"), ("quote", "نیازمند استعلام")], db_index=True, default="fixed", max_length=20, verbose_name="مدل قیمت")),
                ("download_image_limit", models.PositiveSmallIntegerField(default=10, verbose_name="سقف دریافت تصویر")),
                ("homepage_slider_enabled", models.BooleanField(db_index=True, default=False, verbose_name="نمایش در اسلایدر")),
                ("homepage_slider_image_url", models.CharField(blank=True, max_length=2000, verbose_name="تصویر انتخابی اسلایدر")),
                ("homepage_slider_sort_order", models.PositiveIntegerField(db_index=True, default=100, verbose_name="ترتیب اسلایدر")),
                ("last_synced_at", models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="آخرین همگام‌سازی")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("product", models.OneToOneField(on_delete=CASCADE, related_name="catalog_profile", to="store.product", verbose_name="محصول فروشگاه")),
            ],
            options={
                "verbose_name": "پروفایل کاتالوگ محصول",
                "verbose_name_plural": "پروفایل‌های کاتالوگ محصولات",
                "ordering": ["-updated_at", "-id"],
            },
        ),
    ]
