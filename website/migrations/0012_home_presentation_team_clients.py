from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0011_order_intake_private_models_market_pricing"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomePresentationSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("hero_slider_count", models.PositiveSmallIntegerField(default=6, help_text="برای حفظ سرعت صفحه اول، مقدار ۴ تا ۶ پیشنهاد می‌شود.", verbose_name="تعداد تصاویر اسلایدر Hero")),
                ("catalog_preview_count", models.PositiveSmallIntegerField(default=8, help_text="مدل‌ها از بین موارد دارای مجوز، تصویر محلی و لینک فایل انتخاب می‌شوند.", verbose_name="تعداد مدل در بخش معرفی")),
                ("randomize_hero", models.BooleanField(default=True, verbose_name="نمایش رندوم مدل‌های Hero")),
                ("show_team_section", models.BooleanField(default=True, verbose_name="نمایش بخش متخصصان")),
                ("show_clients_section", models.BooleanField(default=True, verbose_name="نمایش بخش مشتریان")),
                ("hero_badge", models.CharField(default="مرکز تخصصی طراحی، مهندسی معکوس و چاپ سه‌بعدی", max_length=180, verbose_name="نشان بالای Hero")),
                ("catalog_heading", models.CharField(default="مدل‌های آماده برای چاپ", max_length=180, verbose_name="عنوان بخش معرفی مدل‌ها")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "تنظیمات پرزنت صفحه اول", "verbose_name_plural": "تنظیمات پرزنت صفحه اول"},
        ),
        migrations.CreateModel(
            name="TeamMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160, verbose_name="نام و نام خانوادگی")),
                ("role", models.CharField(max_length=180, verbose_name="سمت یا تخصص اصلی")),
                ("photo", models.ImageField(blank=True, help_text="تصویر عمودی یا مربعی با کیفیت مناسب و حجم بهینه بارگذاری شود.", null=True, upload_to="website/team/", verbose_name="تصویر متخصص")),
                ("years_experience", models.PositiveSmallIntegerField(default=0, verbose_name="سال سابقه")),
                ("short_bio", models.TextField(blank=True, help_text="در ۲ تا ۴ جمله، تجربه مرتبط با طراحی، چاپ، مهندسی معکوس یا کنترل کیفیت نوشته شود.", verbose_name="معرفی کوتاه")),
                ("expertise", models.TextField(blank=True, help_text="هر توانمندی را در یک خط بنویسید؛ مانند طراحی CAD، مهندسی معکوس، انتخاب متریال.", verbose_name="توانمندی‌ها")),
                ("certifications", models.CharField(blank=True, max_length=300, verbose_name="گواهی‌ها و دوره‌ها")),
                ("linkedin_url", models.URLField(blank=True, verbose_name="لینک حرفه‌ای")),
                ("sort_order", models.PositiveIntegerField(db_index=True, default=100, verbose_name="ترتیب نمایش")),
                ("is_featured", models.BooleanField(db_index=True, default=True, verbose_name="نمایش در صفحه اول")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "متخصص مجموعه", "verbose_name_plural": "متخصصان مجموعه", "ordering": ["sort_order", "id"]},
        ),
        migrations.CreateModel(
            name="ClientReference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180, verbose_name="نام مشتری یا مجموعه")),
                ("logo", models.ImageField(blank=True, help_text="لوگوی دارای مجوز نمایش، ترجیحاً PNG یا WebP با پس‌زمینه شفاف.", null=True, upload_to="website/clients/", verbose_name="لوگو")),
                ("industry", models.CharField(blank=True, max_length=160, verbose_name="حوزه فعالیت")),
                ("project_summary", models.CharField(blank=True, help_text="بدون افشای اطلاعات محرمانه، نوع خدمت یا نتیجه همکاری را کوتاه بنویسید.", max_length=360, verbose_name="خلاصه همکاری")),
                ("website_url", models.URLField(blank=True, verbose_name="وب‌سایت مشتری")),
                ("display_permission_confirmed", models.BooleanField(db_index=True, default=False, help_text="بدون تأیید این گزینه، مشتری در سایت عمومی نمایش داده نمی‌شود.", verbose_name="مجوز نمایش نام و لوگو تأیید شده")),
                ("sort_order", models.PositiveIntegerField(db_index=True, default=100, verbose_name="ترتیب نمایش")),
                ("is_featured", models.BooleanField(db_index=True, default=True, verbose_name="نمایش در صفحه اول")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "مشتری مجموعه", "verbose_name_plural": "مشتریان مجموعه", "ordering": ["sort_order", "id"]},
        ),
    ]
