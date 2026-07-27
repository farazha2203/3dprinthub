from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def seed_sources_and_rules(apps, schema_editor):
    Category = apps.get_model("store", "Category")
    PrintCatalogSource = apps.get_model("store", "PrintCatalogSource")
    CatalogSourcePolicy = apps.get_model("store", "CatalogSourcePolicy")
    CatalogCategoryRule = apps.get_model("store", "CatalogCategoryRule")

    categories = {}
    specs = [
        ("external-industrial", "فایل‌های صنعتی و مهندسی", "industrial", "industrial"),
        ("external-functional", "ابزار و قطعات کاربردی", "industrial", "functional"),
        ("external-decorative", "دکور و محصولات تزئینی", "creative", "decorative"),
        ("external-toys", "اسباب‌بازی و سرگرمی", "creative", "toy"),
        ("external-cosplay", "کازپلی و ماکت", "creative", "cosplay"),
        ("external-education", "آموزشی و دانشگاهی", "academic", "education"),
        ("external-automotive", "خودرو و موتورسیکلت", "automotive", "automotive"),
        ("external-other", "سایر مدل‌های آماده", "general", "other"),
    ]
    for slug, name, section, segment in specs:
        category, _ = Category.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "section": section, "description": "مدل‌های خارجی بررسی‌شده و آماده سفارش چاپ", "is_active": True},
        )
        categories[segment] = category

    source_specs = [
        {
            "code": "makerworld", "name": "MakerWorld", "base_url": "https://makerworld.com/en",
            "domains": "makerworld.com,makerworld.bblmw.com", "kind": "makerworld", "mode": "public_html",
            "public": "licensed_only", "template": "https://makerworld.com/en/models/search?keyword=&sortBy={sort}&page={page}",
            "terms": "https://makerworld.com/en/terms", "delay": 1500,
            "note": "مجوز استاندارد MakerWorld برای فروش چاپ فیزیکی کافی نیست؛ فقط مجوز تجاری صریح قابل تأیید است.",
        },
        {
            "code": "printables", "name": "Printables", "base_url": "https://www.printables.com/",
            "domains": "printables.com,media.printables.com", "kind": "printables", "mode": "public_html",
            "public": "licensed_only", "template": "https://www.printables.com/model?ordering={sort}&page={page}",
            "terms": "https://www.printables.com/terms-of-use", "delay": 1400,
            "note": "مجوز هر مدل جداگانه بررسی می‌شود؛ مجوزهای NC یا مبهم منتشر نمی‌شوند.",
        },
        {
            "code": "thingiverse", "name": "Thingiverse", "base_url": "https://www.thingiverse.com/",
            "domains": "thingiverse.com,api.thingiverse.com", "kind": "thingiverse", "mode": "official_api",
            "public": "licensed_only", "template": "", "terms": "https://www.thingiverse.com/legal/api-terms-of-use",
            "delay": 1200, "api": "https://api.thingiverse.com", "token": "THINGIVERSE_ACCESS_TOKEN",
            "note": "فقط API رسمی؛ scraping غیرفعال است و انتساب منبع الزامی است.",
        },
        {
            "code": "grabcad", "name": "GrabCAD Library", "base_url": "https://grabcad.com/library",
            "domains": "grabcad.com", "kind": "grabcad", "mode": "admin_reference",
            "public": "admin_only", "template": "https://grabcad.com/library?page={page}",
            "terms": "https://grabcad.com/terms", "delay": 2000,
            "note": "فقط مرجع داخلی مدیریت؛ انتشار عمومی، ذخیره لینک دانلود و فروش خودکار غیرفعال است.",
        },
    ]
    for item in source_specs:
        source, _ = PrintCatalogSource.objects.get_or_create(
            code=item["code"],
            defaults={
                "name": item["name"], "base_url": item["base_url"], "allowed_domains": item["domains"],
                "adapter_key": "custom", "default_category": categories["other"], "request_headers": {},
                "request_timeout_seconds": 25, "respect_robots_txt": True, "download_preview_images": False,
                "store_private_download_url": item["kind"] != "grabcad", "license_note": item["note"], "is_active": True,
            },
        )
        CatalogSourcePolicy.objects.update_or_create(
            source=source,
            defaults={
                "source_kind": item["kind"], "discovery_mode": item["mode"], "public_display_policy": item["public"],
                "discovery_url_template": item["template"], "api_base_url": item.get("api", ""),
                "api_token_env": item.get("token", ""), "default_limit": 200, "maximum_limit": 2000,
                "page_size": 24, "request_delay_ms": item["delay"], "max_pages": 100,
                "cache_images_after_approval": True, "store_download_links": item["kind"] != "grabcad",
                "auto_create_draft_products": False, "terms_url": item["terms"], "requires_attribution": True,
                "policy_note": item["note"], "is_active": True,
            },
        )

    keywords = {
        "industrial": "gear,bearing,pulley,mechanical,engineering,jig,fixture,robot,cnc,چرخ دنده,صنعتی,مهندسی",
        "functional": "bracket,mount,holder,adapter,replacement,tool,enclosure,clip,repair,براکت,نگهدارنده,ابزار,تعمیر",
        "decorative": "decor,vase,sculpture,statue,figurine,ornament,lamp,planter,دکور,گلدان,مجسمه,فیگور",
        "toy": "toy,game,puzzle,fidget,miniature,dice,اسباب بازی,بازی,پازل",
        "cosplay": "cosplay,helmet,mask,costume,prop,armor,sword,کازپلی,ماسک,زره,شمشیر",
        "education": "education,school,science,math,physics,biology,anatomy,university,آموزشی,دانشگاهی,فیزیک,ریاضی",
        "automotive": "automotive,car,vehicle,motorcycle,engine,dashboard,خودرو,ماشین,موتورسیکلت,داشبورد",
        "other": "",
    }
    for priority, segment in enumerate(["automotive", "industrial", "functional", "decorative", "toy", "cosplay", "education", "other"], 10):
        CatalogCategoryRule.objects.get_or_create(
            segment=segment,
            source_kind="",
            target_category=categories[segment],
            defaults={"title_keywords": keywords[segment], "priority": priority * 10, "is_active": True},
        )


def reverse_seed(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("store", "0009_inventory_finance_catalog"),
    ]

    operations = [
        migrations.CreateModel(
            name="CatalogSourcePolicy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_kind", models.CharField(choices=[("makerworld", "MakerWorld"), ("printables", "Printables"), ("thingiverse", "Thingiverse"), ("grabcad", "GrabCAD"), ("custom", "سفارشی")], db_index=True, max_length=30, verbose_name="نوع منبع")),
                ("discovery_mode", models.CharField(choices=[("public_html", "HTML عمومی"), ("official_api", "API رسمی"), ("admin_reference", "فقط مرجع مدیریتی")], default="public_html", max_length=30, verbose_name="روش دریافت")),
                ("public_display_policy", models.CharField(choices=[("admin_only", "فقط ادمین"), ("licensed_only", "فقط با مجوز تجاری معتبر"), ("source_link_only", "نمایش عمومی فقط با لینک منبع")], default="licensed_only", max_length=30, verbose_name="سیاست نمایش عمومی")),
                ("discovery_url_template", models.CharField(blank=True, help_text="می‌تواند شامل {page}، {sort} و {limit} باشد.", max_length=600, verbose_name="قالب آدرس لیست")),
                ("api_base_url", models.URLField(blank=True, verbose_name="آدرس پایه API")),
                ("api_token_env", models.CharField(blank=True, max_length=100, verbose_name="نام متغیر محیطی توکن")),
                ("default_limit", models.PositiveIntegerField(default=200, verbose_name="تعداد پیش‌فرض دریافت")),
                ("maximum_limit", models.PositiveIntegerField(default=2000, verbose_name="حداکثر تعداد در هر اجرا")),
                ("page_size", models.PositiveIntegerField(default=24, verbose_name="تعداد در هر صفحه")),
                ("request_delay_ms", models.PositiveIntegerField(default=1200, verbose_name="فاصله درخواست‌ها میلی‌ثانیه")),
                ("max_pages", models.PositiveIntegerField(default=100, verbose_name="حداکثر صفحه")),
                ("cache_images_after_approval", models.BooleanField(default=True, verbose_name="ذخیره محلی تصویر پس از تأیید")),
                ("store_download_links", models.BooleanField(default=True, verbose_name="ذخیره لینک فایل فقط برای ادمین")),
                ("auto_create_draft_products", models.BooleanField(default=False, verbose_name="ساخت خودکار محصول غیرفعال پس از تأیید")),
                ("terms_url", models.URLField(blank=True, verbose_name="لینک قوانین منبع")),
                ("requires_attribution", models.BooleanField(default=True, verbose_name="الزام ذکر منبع")),
                ("policy_note", models.TextField(blank=True, verbose_name="یادداشت حقوقی و اجرایی")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
                ("last_synced_at", models.DateTimeField(blank=True, null=True, verbose_name="آخرین همگام‌سازی")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("source", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="sync_policy", to="store.printcatalogsource", verbose_name="منبع")),
            ],
            options={"verbose_name": "سیاست دریافت کاتالوگ", "verbose_name_plural": "سیاست‌های دریافت کاتالوگ"},
        ),
        migrations.CreateModel(
            name="CatalogSyncRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_mode", models.CharField(choices=[("downloads", "بیشترین دانلود"), ("likes", "بیشترین لایک"), ("views", "بیشترین بازدید"), ("trending", "ترند"), ("newest", "جدیدترین")], default="downloads", max_length=20, verbose_name="مرتب‌سازی")),
                ("requested_limit", models.PositiveIntegerField(default=200, verbose_name="تعداد درخواستی")),
                ("status", models.CharField(choices=[("queued", "در صف"), ("running", "در حال اجرا"), ("completed", "تکمیل‌شده"), ("partial", "نیمه‌کامل"), ("failed", "ناموفق")], db_index=True, default="queued", max_length=20, verbose_name="وضعیت")),
                ("discovered_count", models.PositiveIntegerField(default=0, verbose_name="کشف‌شده")),
                ("imported_count", models.PositiveIntegerField(default=0, verbose_name="ثبت یا به‌روزرسانی")),
                ("skipped_count", models.PositiveIntegerField(default=0, verbose_name="ردشده")),
                ("failed_count", models.PositiveIntegerField(default=0, verbose_name="خطا")),
                ("current_page", models.PositiveIntegerField(default=0, verbose_name="صفحه فعلی")),
                ("cursor", models.CharField(blank=True, max_length=500, verbose_name="نشانگر ادامه")),
                ("log", models.TextField(blank=True, verbose_name="گزارش")),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("requested_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="catalog_sync_runs", to=settings.AUTH_USER_MODEL, verbose_name="اجراکننده")),
                ("source", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sync_runs", to="store.printcatalogsource", verbose_name="منبع")),
            ],
            options={"verbose_name": "اجرای دریافت کاتالوگ", "verbose_name_plural": "اجراهای دریافت کاتالوگ", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="CatalogCategoryRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_kind", models.CharField(blank=True, choices=[("", "همه منابع"), ("makerworld", "MakerWorld"), ("printables", "Printables"), ("thingiverse", "Thingiverse"), ("grabcad", "GrabCAD"), ("custom", "سفارشی")], max_length=30, verbose_name="منبع")),
                ("title_keywords", models.TextField(blank=True, help_text="با ویرگول جدا کنید.", verbose_name="کلیدواژه‌های عنوان/برچسب")),
                ("source_category_keywords", models.TextField(blank=True, verbose_name="کلیدواژه دسته منبع")),
                ("segment", models.CharField(choices=[("industrial", "صنعتی و مهندسی"), ("functional", "کاربردی و ابزار"), ("decorative", "تزئینی و دکور"), ("toy", "اسباب‌بازی و سرگرمی"), ("cosplay", "کازپلی و ماکت"), ("education", "آموزشی و دانشگاهی"), ("automotive", "خودرو و موتورسیکلت"), ("other", "سایر")], max_length=30, verbose_name="گروه خودکار")),
                ("priority", models.PositiveIntegerField(db_index=True, default=100, verbose_name="اولویت")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
                ("target_category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="catalog_rules", to="store.category", verbose_name="دسته مقصد")),
            ],
            options={"verbose_name": "قانون دسته‌بندی خودکار", "verbose_name_plural": "قوانین دسته‌بندی خودکار", "ordering": ["priority", "id"]},
        ),
        migrations.CreateModel(
            name="CatalogAssetMetrics",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_kind", models.CharField(db_index=True, max_length=30, verbose_name="منبع")),
                ("source_category", models.CharField(blank=True, max_length=250, verbose_name="دسته منبع")),
                ("segment", models.CharField(choices=[("industrial", "صنعتی و مهندسی"), ("functional", "کاربردی و ابزار"), ("decorative", "تزئینی و دکور"), ("toy", "اسباب‌بازی و سرگرمی"), ("cosplay", "کازپلی و ماکت"), ("education", "آموزشی و دانشگاهی"), ("automotive", "خودرو و موتورسیکلت"), ("other", "سایر")], db_index=True, default="other", max_length=30, verbose_name="گروه خودکار")),
                ("popularity_rank", models.PositiveIntegerField(default=0, verbose_name="رتبه محبوبیت")),
                ("views_count", models.PositiveBigIntegerField(db_index=True, default=0, verbose_name="بازدید")),
                ("likes_count", models.PositiveBigIntegerField(db_index=True, default=0, verbose_name="لایک")),
                ("downloads_count", models.PositiveBigIntegerField(db_index=True, default=0, verbose_name="دانلود")),
                ("makes_count", models.PositiveBigIntegerField(default=0, verbose_name="تعداد ساخت")),
                ("comments_count", models.PositiveBigIntegerField(default=0, verbose_name="نظر")),
                ("rating", models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name="امتیاز")),
                ("estimated_weight_grams", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="وزن تخمینی گرم")),
                ("estimated_print_minutes", models.PositiveIntegerField(blank=True, null=True, verbose_name="زمان تخمینی چاپ دقیقه")),
                ("estimate_source", models.CharField(blank=True, max_length=100, verbose_name="منبع برآورد وزن/زمان")),
                ("file_formats", models.JSONField(blank=True, default=list, verbose_name="فرمت فایل‌ها")),
                ("file_links", models.JSONField(blank=True, default=list, verbose_name="لینک فایل‌ها فقط برای ادمین")),
                ("image_urls", models.JSONField(blank=True, default=list, verbose_name="آدرس تصاویر منبع")),
                ("creator_url", models.URLField(blank=True, verbose_name="صفحه سازنده")),
                ("license_code", models.CharField(blank=True, max_length=120, verbose_name="کد مجوز")),
                ("commercial_use_allowed", models.BooleanField(blank=True, db_index=True, null=True, verbose_name="اجازه فروش چاپ فیزیکی")),
                ("license_review_status", models.CharField(choices=[("unknown", "نامشخص"), ("allowed", "مجاز برای فروش چاپ"), ("blocked", "غیرمجاز برای فروش چاپ"), ("manual", "نیازمند بررسی دستی")], db_index=True, default="unknown", max_length=20, verbose_name="بررسی مجوز")),
                ("public_approved", models.BooleanField(db_index=True, default=False, verbose_name="تأیید نمایش عمومی")),
                ("blocked_reason", models.TextField(blank=True, verbose_name="علت مسدودی")),
                ("attribution_text", models.CharField(blank=True, max_length=500, verbose_name="متن انتساب")),
                ("raw_metrics", models.JSONField(blank=True, default=dict, verbose_name="داده خام شاخص‌ها")),
                ("last_synced_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("asset", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="metrics", to="store.importedprintasset", verbose_name="فایل واردشده")),
                ("target_category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="external_catalog_assets", to="store.category", verbose_name="دسته مقصد")),
            ],
            options={"verbose_name": "آمار و مجوز فایل خارجی", "verbose_name_plural": "آمار و مجوز فایل‌های خارجی", "ordering": ["-downloads_count", "-likes_count", "-views_count", "id"]},
        ),
        migrations.AddIndex(model_name="catalogassetmetrics", index=models.Index(fields=["source_kind", "public_approved"], name="store_cat_src_pub_idx")),
        migrations.AddIndex(model_name="catalogassetmetrics", index=models.Index(fields=["segment", "public_approved"], name="store_cat_seg_pub_idx")),
        migrations.CreateModel(
            name="CatalogSyncDashboard",
            fields=[],
            options={"verbose_name": "داشبورد کاتالوگ خارجی", "verbose_name_plural": "داشبورد کاتالوگ خارجی", "proxy": True, "indexes": [], "constraints": []},
            bases=("store.catalogsyncrun",),
        ),
        migrations.RunPython(seed_sources_and_rules, reverse_seed),
    ]
