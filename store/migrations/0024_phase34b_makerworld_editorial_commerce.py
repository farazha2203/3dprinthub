from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0017_phase30_online_payment_gateway"),
        ("store", "0023_phase33_automation_deadlines"),
    ]

    operations = [
        migrations.AddField(model_name="product", name="consultation_required", field=models.BooleanField(default=True, verbose_name="نیازمند مشاوره")),
        migrations.AddField(model_name="product", name="fixed_delivery_days", field=models.PositiveIntegerField(default=3, verbose_name="زمان آماده‌سازی به روز")),
        migrations.AddField(model_name="product", name="fixed_price", field=models.PositiveBigIntegerField(default=0, verbose_name="قیمت ثابت به تومان")),
        migrations.AddField(model_name="product", name="order_mode", field=models.CharField(choices=[("variant", "قیمت‌گذاری بر اساس تنوع"), ("fixed", "قیمت ثابت و سفارش مستقیم")], db_index=True, default="variant", max_length=20, verbose_name="روش سفارش")),
        migrations.AddField(model_name="importedprintasset", name="commercial_license_evidence", field=models.FileField(blank=True, null=True, upload_to="store/private-license-evidence/", verbose_name="مدرک مجوز تجاری")),
        migrations.AddField(model_name="importedprintasset", name="commercial_license_note", field=models.TextField(blank=True, verbose_name="یادداشت مجوز تجاری")),
        migrations.AddField(model_name="importedprintasset", name="commercial_license_source", field=models.CharField(blank=True, max_length=300, verbose_name="منبع تأیید مجوز")),
        migrations.AddField(model_name="importedprintasset", name="commercial_license_status", field=models.CharField(choices=[("unknown", "نامشخص"), ("blocked", "غیرمجاز"), ("review", "نیازمند بررسی"), ("allowed", "مجاز برای فروش چاپ"), ("owned", "طراحی متعلق به مجموعه"), ("public_domain", "مالکیت عمومی")], db_index=True, default="unknown", max_length=20, verbose_name="وضعیت مجوز تجاری")),
        migrations.AddField(model_name="importedprintasset", name="editorial_status", field=models.CharField(choices=[("imported", "واردشده"), ("review", "در انتظار بررسی"), ("license_review", "نیازمند بررسی مجوز"), ("reference", "مرجع قابل نمایش"), ("printable", "مجاز برای فروش چاپ"), ("product", "تبدیل‌شده به محصول"), ("portfolio", "تبدیل‌شده به نمونه‌کار"), ("rejected", "ردشده"), ("archived", "بایگانی‌شده")], db_index=True, default="imported", max_length=24, verbose_name="وضعیت تحریریه")),
        migrations.AddField(model_name="importedprintasset", name="fixed_print_price", field=models.PositiveBigIntegerField(default=0, verbose_name="قیمت ثابت چاپ به تومان")),
        migrations.AddField(model_name="importedprintasset", name="persian_description", field=models.TextField(blank=True, verbose_name="توضیحات فارسی")),
        migrations.AddField(model_name="importedprintasset", name="persian_short_description", field=models.CharField(blank=True, max_length=500, verbose_name="توضیح کوتاه فارسی")),
        migrations.AddField(model_name="importedprintasset", name="persian_title", field=models.CharField(blank=True, max_length=260, verbose_name="عنوان فارسی پیشنهادی")),
        migrations.AddField(model_name="importedprintasset", name="portfolio_item", field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="imported_source_asset", to="website.portfolioitem", verbose_name="نمونه‌کار ساخته‌شده")),
        migrations.AddField(model_name="importedprintasset", name="source_description", field=models.TextField(blank=True, verbose_name="توضیحات اصلی منبع")),
        migrations.AddField(model_name="importedprintasset", name="source_title", field=models.CharField(blank=True, max_length=260, verbose_name="عنوان اصلی منبع")),
        migrations.AddField(model_name="importedprintassetimage", name="is_primary", field=models.BooleanField(db_index=True, default=False, verbose_name="تصویر اصلی")),
        migrations.AddField(model_name="importedprintassetimage", name="is_selected", field=models.BooleanField(db_index=True, default=True, verbose_name="انتخاب برای انتشار")),
        migrations.AddField(model_name="importedprintassetimage", name="source_content_type", field=models.CharField(blank=True, max_length=80, verbose_name="نوع محتوای تصویر")),
        migrations.AddField(model_name="importedprintassetimage", name="source_height", field=models.PositiveIntegerField(default=0, verbose_name="ارتفاع تصویر منبع")),
        migrations.AddField(model_name="importedprintassetimage", name="source_name", field=models.CharField(blank=True, max_length=120, verbose_name="نام منبع تصویر")),
        migrations.AddField(model_name="importedprintassetimage", name="source_page_url", field=models.URLField(blank=True, max_length=1000, verbose_name="صفحه منبع تصویر")),
        migrations.AddField(model_name="importedprintassetimage", name="source_width", field=models.PositiveIntegerField(default=0, verbose_name="عرض تصویر منبع")),
    ]
