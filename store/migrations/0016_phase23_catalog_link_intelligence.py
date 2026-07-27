import uuid
from urllib.parse import unquote, urlparse

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_reference_titles(apps, schema_editor):
    ImportedPrintAsset = apps.get_model("store", "ImportedPrintAsset")
    queryset = ImportedPrintAsset.objects.filter(title="").select_related("source")
    for asset in queryset.iterator(chunk_size=500):
        path_name = unquote(urlparse(asset.source_url or "").path.rstrip("/").rsplit("/", 1)[-1])
        path_name = path_name.replace("-", " ").replace("_", " ").replace(":", " ").strip()
        source_name = getattr(asset.source, "name", "") or "منبع خارجی"
        title = path_name or (asset.external_id or "").strip() or f"مدل از {source_name}"
        ImportedPrintAsset.objects.filter(pk=asset.pk).update(title=title[:260])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("website", "0014_support_chat_google_profile_and_order_attachments"),
        ("store", "0015_phase17_catalog_preview_profiles"),
    ]

    operations = [
        migrations.AddField(
            model_name="catalogsourcepolicy",
            name="public_reference_enabled",
            field=models.BooleanField(
                db_index=True,
                default=True,
                help_text="نام، تصویر، مشخصات و لینک صفحه منبع را حتی بدون فایل مستقیم به‌صورت مرجع نمایش می‌دهد؛ لینک فایل خصوصی عمومی نمی‌شود.",
                verbose_name="نمایش مرجع عمومی",
            ),
        ),
        migrations.RunPython(backfill_reference_titles, noop_reverse),
        migrations.CreateModel(
            name="CatalogRefreshRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(blank=True, db_index=True, max_length=80, verbose_name="شناسه نشست")),
                ("status", models.CharField(choices=[("pending", "در انتظار بررسی"), ("running", "در حال بروزرسانی"), ("completed", "بروزرسانی شد"), ("failed", "ناموفق")], db_index=True, default="pending", max_length=20, verbose_name="وضعیت")),
                ("customer_note", models.CharField(blank=True, max_length=500, verbose_name="توضیح مشتری")),
                ("result_summary", models.TextField(blank=True, verbose_name="نتیجه بروزرسانی")),
                ("requested_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="زمان درخواست")),
                ("processed_at", models.DateTimeField(blank=True, null=True, verbose_name="زمان پردازش")),
                ("asset", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="refresh_requests", to="store.importedprintasset", verbose_name="مدل خارجی")),
                ("requested_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="catalog_refresh_requests", to=settings.AUTH_USER_MODEL, verbose_name="درخواست‌کننده")),
            ],
            options={
                "verbose_name": "درخواست بروزرسانی مدل خارجی",
                "verbose_name_plural": "درخواست‌های بروزرسانی مدل‌های خارجی",
                "ordering": ["-requested_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="CustomerLinkAnalysis",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_token", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, verbose_name="شناسه عمومی")),
                ("session_key", models.CharField(blank=True, db_index=True, max_length=80, verbose_name="شناسه نشست")),
                ("source_url", models.URLField(max_length=2000, verbose_name="لینک ارسالی مشتری")),
                ("normalized_url", models.URLField(db_index=True, max_length=2000, verbose_name="لینک نرمال‌شده")),
                ("source_domain", models.CharField(db_index=True, max_length=255, verbose_name="دامنه منبع")),
                ("source_name", models.CharField(blank=True, max_length=255, verbose_name="نام سایت منبع")),
                ("status", models.CharField(choices=[("pending", "در انتظار تحلیل"), ("processing", "در حال تحلیل"), ("ready", "آماده برآورد"), ("needs_input", "نیازمند اطلاعات تکمیلی"), ("partial", "اطلاعات ناقص دریافت شد"), ("failed", "تحلیل ناموفق"), ("converted", "تبدیل‌شده به سفارش")], db_index=True, default="pending", max_length=20, verbose_name="وضعیت")),
                ("title", models.CharField(blank=True, max_length=300, verbose_name="نام محصول یا فایل")),
                ("short_description", models.CharField(blank=True, max_length=700, verbose_name="توضیح کوتاه")),
                ("description", models.TextField(blank=True, verbose_name="توضیحات استخراج‌شده")),
                ("author_name", models.CharField(blank=True, max_length=220, verbose_name="طراح یا فروشنده")),
                ("image_url", models.URLField(blank=True, max_length=2000, verbose_name="تصویر اصلی منبع")),
                ("cached_image", models.ImageField(blank=True, null=True, upload_to="store/link-analysis/previews/", verbose_name="تصویر ذخیره‌شده")),
                ("image_urls", models.JSONField(blank=True, default=list, verbose_name="تصاویر استخراج‌شده")),
                ("tags", models.JSONField(blank=True, default=list, verbose_name="برچسب‌ها")),
                ("technical_specs", models.JSONField(blank=True, default=dict, verbose_name="مشخصات فنی")),
                ("file_formats", models.JSONField(blank=True, default=list, verbose_name="فرمت‌های شناسایی‌شده")),
                ("file_links", models.JSONField(blank=True, default=list, verbose_name="لینک فایل‌ها فقط برای ادمین")),
                ("source_payload", models.JSONField(blank=True, default=dict, verbose_name="داده خام امن‌شده")),
                ("detected_material_name", models.CharField(blank=True, max_length=120, verbose_name="متریال تشخیص‌داده‌شده")),
                ("estimated_weight_grams", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="وزن تخمینی گرم")),
                ("estimated_print_minutes", models.PositiveIntegerField(blank=True, null=True, verbose_name="زمان تخمینی چاپ دقیقه")),
                ("quantity", models.PositiveIntegerField(default=1, verbose_name="تعداد")),
                ("estimate_confidence", models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name="اعتماد برآورد درصد")),
                ("estimated_price", models.PositiveBigIntegerField(default=0, verbose_name="قیمت میانی تخمینی تومان")),
                ("estimated_price_min", models.PositiveBigIntegerField(default=0, verbose_name="حداقل قیمت تخمینی تومان")),
                ("estimated_price_max", models.PositiveBigIntegerField(default=0, verbose_name="حداکثر قیمت تخمینی تومان")),
                ("estimate_breakdown", models.JSONField(blank=True, default=dict, verbose_name="جزئیات برآورد")),
                ("analysis_warnings", models.JSONField(blank=True, default=list, verbose_name="هشدارهای تحلیل")),
                ("error_message", models.TextField(blank=True, verbose_name="خطای تحلیل")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("analyzed_at", models.DateTimeField(blank=True, null=True, verbose_name="زمان تحلیل")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("material", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="link_analyses", to="website.material", verbose_name="متریال برآورد")),
                ("order", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="source_link_analysis", to="website.order", verbose_name="سفارش ساخته‌شده")),
                ("related_asset", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="customer_link_analyses", to="store.importedprintasset", verbose_name="مدل خارجی مرتبط")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="external_link_analyses", to=settings.AUTH_USER_MODEL, verbose_name="مشتری")),
            ],
            options={
                "verbose_name": "تحلیل لینک محصول مشتری",
                "verbose_name_plural": "تحلیل لینک‌های محصولات مشتریان",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.AddIndex(
            model_name="catalogrefreshrequest",
            index=models.Index(fields=["status", "requested_at"], name="store_cat_refresh_q_idx"),
        ),
        migrations.AddIndex(
            model_name="customerlinkanalysis",
            index=models.Index(fields=["status", "-created_at"], name="store_link_status_idx"),
        ),
        migrations.AddIndex(
            model_name="customerlinkanalysis",
            index=models.Index(fields=["source_domain", "-created_at"], name="store_link_domain_idx"),
        ),
    ]
