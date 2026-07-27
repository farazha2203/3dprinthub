from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


def seed_phase29(apps, schema_editor):
    CatalogSourcePolicy = apps.get_model("store", "CatalogSourcePolicy")
    CatalogPricingReview = apps.get_model("store", "CatalogPricingReview")
    ImportedPrintAsset = apps.get_model("store", "ImportedPrintAsset")
    CustomerLinkAnalysis = apps.get_model("store", "CustomerLinkAnalysis")
    LinkAnalysisManualReview = apps.get_model("store", "LinkAnalysisManualReview")
    Order = apps.get_model("website", "Order")
    Quote = apps.get_model("website", "Quote")
    Payment = apps.get_model("website", "Payment")
    priorities = {"makerworld": 10, "printables": 30, "thingiverse": 40, "grabcad": 80, "custom": 100}
    default_limits = {"makerworld": 500, "printables": 250, "thingiverse": 180, "grabcad": 80, "custom": 100}
    for policy in CatalogSourcePolicy.objects.all():
        policy.source_priority = priorities.get(policy.source_kind, 100)
        policy.default_limit = max(int(policy.default_limit or 0), default_limits.get(policy.source_kind, 100))
        if policy.source_kind == "makerworld":
            policy.maximum_limit = max(int(policy.maximum_limit or 0), 3000)
        policy.save(update_fields=["source_priority", "default_limit", "maximum_limit"])
        try:
            schedule = policy.schedule
        except Exception:
            schedule = None
        if schedule:
            schedule.requested_limit = policy.default_limit
            schedule.save(update_fields=["requested_limit", "updated_at"])
    for asset in ImportedPrintAsset.objects.all().iterator():
        CatalogPricingReview.objects.get_or_create(asset_id=asset.pk)

    # Remove legacy prices that were produced without an explicit/profile/operator
    # source for both weight and time. These rows must return to operator inquiry.
    allowed = {"source_explicit", "source_profile", "operator_verified"}
    for analysis in CustomerLinkAnalysis.objects.filter(estimated_price__gt=0).iterator():
        specs = analysis.technical_specs or {}
        weight_source = str(specs.get("weight_source_kind") or "unknown")
        time_source = str(specs.get("print_time_source_kind") or "unknown")
        if weight_source in allowed and time_source in allowed:
            continue
        analysis.estimated_weight_grams = None
        analysis.estimated_print_minutes = None
        analysis.estimated_price = 0
        analysis.estimated_price_min = 0
        analysis.estimated_price_max = 0
        analysis.estimate_confidence = 0
        analysis.estimate_breakdown = {}
        analysis.status = "needs_input" if analysis.title else "partial"
        analysis.save(update_fields=[
            "estimated_weight_grams", "estimated_print_minutes", "estimated_price",
            "estimated_price_min", "estimated_price_max", "estimate_confidence",
            "estimate_breakdown", "status", "updated_at",
        ])
        if analysis.order_id:
            Order.objects.filter(pk=analysis.order_id).update(status="reviewing")
            quote = Quote.objects.filter(order_id=analysis.order_id).first()
            if quote:
                has_payment = Payment.objects.filter(
                    quote_id=quote.pk, status__in=["paid", "pending", "awaiting_review"]
                ).exists()
                note = (quote.admin_note or "") + "\n[Phase29] قیمت قبلی منبع معتبر وزن/زمان نداشت و نیازمند بررسی اپراتور است."
                if has_payment:
                    quote.status = "draft"
                    quote.admin_note = note + " پرداخت مرتبط وجود دارد؛ مغایرت مالی باید دستی بررسی شود."
                    quote.save(update_fields=["status", "admin_note", "updated_at"])
                else:
                    quote.weight_grams = 0
                    quote.print_time_minutes = 0
                    quote.labor_fee = 0
                    quote.post_processing_fee = 0
                    quote.status = "draft"
                    quote.admin_note = note
                    quote.customer_note = "قیمت قبلی حذف شد؛ اپراتور وزن، زمان و مبلغ جدید را اعلام می‌کند."
                    quote.save(update_fields=[
                        "weight_grams", "print_time_minutes", "labor_fee", "post_processing_fee",
                        "status", "admin_note", "customer_note", "updated_at",
                    ])
        if not LinkAnalysisManualReview.objects.filter(
            analysis_id=analysis.pk, status__in=["pending", "in_progress"]
        ).exists():
            LinkAnalysisManualReview.objects.create(
                analysis_id=analysis.pk,
                requested_by_id=analysis.user_id,
                reason="incomplete_data",
                priority=180,
                customer_note="قیمت قدیمی به دلیل نداشتن منبع معتبر وزن/زمان حذف شد و نیازمند بررسی اپراتور است.",
                source_snapshot={
                    "source_url": analysis.normalized_url or analysis.source_url,
                    "source_domain": analysis.source_domain,
                    "source_name": analysis.source_name,
                    "title": analysis.title,
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0015_phase28_quote_deposit_payment"),
        ("store", "0019_phase26_realtime_manual_review"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="pricingsetting",
            name="minimum_billable_minutes",
            field=models.PositiveIntegerField(default=60, help_text="برای قطعات زیر یک ساعت مقدار ۶۰ قرار دهید تا حداقل یک ساعت محاسبه شود.", validators=[django.core.validators.MinValueValidator(1)], verbose_name="حداقل زمان قابل محاسبه به دقیقه"),
        ),
        migrations.AddField(
            model_name="pricingsetting",
            name="billing_increment_minutes",
            field=models.PositiveIntegerField(default=60, help_text="با مقدار ۶۰، زمان ۶۱ تا ۱۲۰ دقیقه دو ساعت محاسبه می‌شود.", validators=[django.core.validators.MinValueValidator(1)], verbose_name="پله گردکردن زمان چاپ به دقیقه"),
        ),
        migrations.AddField(
            model_name="importedprintasset",
            name="archive_status",
            field=models.CharField(choices=[("none", "فایل محلی نداریم"), ("downloaded", "فایل دانلود شده"), ("archived", "فایل بایگانی و قابل استفاده"), ("ordered", "فایل برای سفارش مشتری نگهداری می‌شود")], db_index=True, default="none", max_length=20, verbose_name="وضعیت فایل محلی"),
        ),
        migrations.AddField(
            model_name="importedprintasset",
            name="archived_model_file",
            field=models.FileField(blank=True, help_text="فایل خصوصی است و فقط مدیریت به آن دسترسی دارد.", null=True, upload_to="store/private-imported-models/", verbose_name="فایل سه‌بعدی آرشیوی"),
        ),
        migrations.AddField(
            model_name="importedprintasset",
            name="keep_public_when_source_disabled",
            field=models.BooleanField(default=False, help_text="برای مدل‌هایی که فایل آن‌ها موجود یا قبلاً سفارش گرفته شده فعال می‌شود.", verbose_name="حفظ نمایش در صورت قطع منبع"),
        ),
        migrations.AddField(
            model_name="catalogsourcepolicy",
            name="source_priority",
            field=models.PositiveSmallIntegerField(db_index=True, default=100, help_text="عدد کمتر یعنی دریافت و نمایش زودتر؛ برای MakerWorld مقدار ۱۰ پیشنهاد می‌شود.", verbose_name="اولویت منبع"),
        ),
        migrations.AddField(
            model_name="linkanalysismanualreview",
            name="operator_notification_sent_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="زمان اعلان به اپراتور"),
        ),
        migrations.AddField(
            model_name="linkanalysismanualreview",
            name="operator_notification_error",
            field=models.TextField(blank=True, verbose_name="خطای اعلان اپراتور"),
        ),
        migrations.AddField(
            model_name="linkanalysismanualreview",
            name="operator_material",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="manual_link_pricing_reviews", to="website.material", verbose_name="متریال تأییدشده اپراتور"),
        ),
        migrations.AddField(
            model_name="linkanalysismanualreview",
            name="operator_weight_grams",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="وزن قطعی اپراتور به گرم"),
        ),
        migrations.AddField(
            model_name="linkanalysismanualreview",
            name="operator_print_minutes",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="زمان واقعی چاپ به دقیقه"),
        ),
        migrations.AddField(
            model_name="linkanalysismanualreview",
            name="operator_price_override",
            field=models.PositiveBigIntegerField(default=0, help_text="اگر صفر باشد، قیمت از وزن، زمان، نرخ روز متریال و تنظیمات ساعتی محاسبه می‌شود.", verbose_name="قیمت قطعی دستی (اختیاری)"),
        ),
        migrations.AddField(
            model_name="linkanalysismanualreview",
            name="operator_specs",
            field=models.JSONField(blank=True, default=dict, help_text="ابعاد، نازل، ساپورت، پرشدگی، تعداد قطعات و هر نکته لازم برای چاپ.", verbose_name="مشخصات تکمیلی اپراتور"),
        ),
        migrations.CreateModel(
            name="CatalogPricingReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("pending", "در انتظار تکمیل اپراتور"), ("verified", "وزن و زمان تأیید شده"), ("rejected", "غیرقابل قیمت‌گذاری")], db_index=True, default="pending", max_length=20, verbose_name="وضعیت")),
                ("weight_grams", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="وزن تأییدشده گرم")),
                ("print_minutes", models.PositiveIntegerField(blank=True, null=True, verbose_name="زمان واقعی چاپ دقیقه")),
                ("price_override", models.PositiveBigIntegerField(default=0, verbose_name="قیمت قطعی دستی (اختیاری)")),
                ("operator_note", models.TextField(blank=True, verbose_name="یادداشت اپراتور")),
                ("verified_at", models.DateTimeField(blank=True, null=True, verbose_name="زمان تأیید")),
                ("notification_sent_at", models.DateTimeField(blank=True, null=True, verbose_name="زمان اعلان به اپراتور")),
                ("notification_error", models.TextField(blank=True, verbose_name="خطای اعلان")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("asset", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="pricing_review", to="store.importedprintasset", verbose_name="مدل کاتالوگ")),
                ("material", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="catalog_pricing_reviews", to="website.material", verbose_name="متریال تأییدشده")),
                ("verified_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="verified_catalog_prices", to=settings.AUTH_USER_MODEL, verbose_name="اپراتور تأییدکننده")),
            ],
            options={"verbose_name": "قیمت‌گذاری اپراتوری مدل", "verbose_name_plural": "صف قیمت‌گذاری اپراتوری مدل‌ها", "ordering": ["status", "-updated_at"]},
        ),
        migrations.RunPython(seed_phase29, migrations.RunPython.noop),
    ]
