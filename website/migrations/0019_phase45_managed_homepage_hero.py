from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0027_phase39_variant_color_fk"),
        ("website", "0018_phase38_operator_notifications"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomepageHeroSlide",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image_url", models.URLField(blank=True, help_text="اگر خالی باشد، تصویر اصلی همان محصول استفاده می‌شود. بعد از انتخاب محصول و ذخیره، تصاویر پیشنهادی پایین فرم نمایش داده می‌شوند.", max_length=2000, verbose_name="عکس انتخابی اسلایدر")),
                ("image_alt_text", models.CharField(blank=True, help_text="اگر خالی باشد از عنوان اسلاید و محصول ساخته می‌شود.", max_length=240, verbose_name="Alt تصویر برای SEO")),
                ("title_override", models.CharField(blank=True, help_text="اگر خالی باشد عنوان اصلی محصول نمایش داده می‌شود.", max_length=220, verbose_name="عنوان نمایشی")),
                ("group_title", models.CharField(blank=True, help_text="مثلاً قطعات خودرو، ابزار کارگاهی یا دکوراسیون. اگر خالی باشد دسته یا منبع محصول استفاده می‌شود.", max_length=160, verbose_name="عنوان گروه / دسته")),
                ("description", models.CharField(blank=True, help_text="حداکثر یک یا دو جمله کوتاه؛ برای خوانایی موبایل متن طولانی ننویسید.", max_length=480, verbose_name="توضیح کوتاه روی اسلاید")),
                ("button_text", models.CharField(default="مشاهده محصول", max_length=80, verbose_name="متن دکمه")),
                ("object_fit", models.CharField(choices=[("cover", "پر کردن تمام صفحه (Cover)"), ("contain", "نمایش کامل تصویر (Contain)")], default="cover", max_length=12, verbose_name="نحوه نمایش عکس")),
                ("focal_position", models.CharField(choices=[("center", "وسط"), ("top", "بالا"), ("bottom", "پایین"), ("left", "چپ"), ("right", "راست")], default="center", max_length=12, verbose_name="نقطه تمرکز عکس")),
                ("sort_order", models.PositiveIntegerField(db_index=True, default=100, verbose_name="ترتیب نمایش")),
                ("is_active", models.BooleanField(db_index=True, default=False, help_text="فقط اسلایدهای فعال در سایت عمومی نمایش داده می‌شوند.", verbose_name="تأیید و نمایش در اسلایدر")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")),
                ("asset", models.ForeignKey(help_text="فقط محصولی را انتخاب کنید که خودتان برای نمایش در اسلایدر صفحه اصلی تأیید کرده‌اید.", on_delete=django.db.models.deletion.CASCADE, related_name="homepage_hero_slides", to="store.importedprintasset", verbose_name="محصول / مدل کاتالوگ")),
            ],
            options={
                "verbose_name": "اسلاید صفحه اصلی",
                "verbose_name_plural": "اسلایدهای صفحه اصلی",
                "ordering": ["sort_order", "id"],
            },
        ),
    ]
