from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def seed_adapter_policies(apps, schema_editor):
    Policy = apps.get_model("store", "LinkAnalysisAdapterPolicy")
    defaults = [
        ("makerworld", "MakerWorld", ["makerworld.com"], 4, 25),
        ("printables", "Printables", ["printables.com"], 4, 25),
        ("thingiverse", "Thingiverse", ["thingiverse.com"], 4, 25),
        ("grabcad", "GrabCAD", ["grabcad.com"], 3, 25),
        ("direct_file", "لینک مستقیم فایل", [], 2, 15),
        ("generic", "تحلیل عمومی وب", [], 4, 20),
    ]
    for key, name, domains, attempts, timeout in defaults:
        Policy.objects.get_or_create(
            adapter_key=key,
            defaults={
                "display_name": name,
                "domain_patterns": domains,
                "max_attempts": attempts,
                "request_timeout_seconds": timeout,
                "retry_delays_seconds": [30, 120, 600, 1800],
            },
        )

    Control = apps.get_model("store", "LinkAnalysisQueueControl")
    Control.objects.get_or_create(singleton_key=1)

    Job = apps.get_model("store", "CustomerLinkAnalysisJob")
    for job in Job.objects.select_related("analysis").iterator(chunk_size=500):
        domain = (job.analysis.source_domain or "").lower()
        url = (job.analysis.normalized_url or job.analysis.source_url or "").lower()
        key = "generic"
        if any(url.split("?", 1)[0].endswith(ext) for ext in (".stl", ".3mf", ".step", ".stp", ".obj", ".iges", ".igs")):
            key = "direct_file"
        elif "makerworld.com" in domain:
            key = "makerworld"
        elif "printables.com" in domain:
            key = "printables"
        elif "thingiverse.com" in domain:
            key = "thingiverse"
        elif "grabcad.com" in domain:
            key = "grabcad"
        Job.objects.filter(pk=job.pk).update(adapter_key=key)


def reverse_seed(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("store", "0017_phase24_async_link_analysis_queue"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerlinkanalysisjob",
            name="adapter_key",
            field=models.CharField(db_index=True, default="generic", max_length=40, verbose_name="Adapter تحلیل"),
        ),
        migrations.AddField(
            model_name="customerlinkanalysisjob",
            name="failure_notified_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="اعلان شکست ارسال شد"),
        ),
        migrations.AddField(
            model_name="customerlinkanalysisjob",
            name="success_notified_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="اعلان موفقیت ارسال شد"),
        ),
        migrations.CreateModel(
            name="LinkAnalysisQueueControl",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("singleton_key", models.PositiveSmallIntegerField(default=1, editable=False, unique=True)),
                ("is_paused", models.BooleanField(db_index=True, default=False, verbose_name="توقف سراسری صف")),
                ("pause_reason", models.CharField(blank=True, max_length=300, verbose_name="دلیل توقف")),
                ("heartbeat_timeout_seconds", models.PositiveIntegerField(default=90, verbose_name="مهلت سلامت Worker ثانیه")),
                ("stale_lock_minutes", models.PositiveSmallIntegerField(default=15, verbose_name="مهلت آزادسازی قفل دقیقه")),
                ("default_batch_size", models.PositiveSmallIntegerField(default=3, verbose_name="تعداد Job در هر چرخه")),
                ("default_sleep_seconds", models.PositiveSmallIntegerField(default=3, verbose_name="فاصله چرخه Worker ثانیه")),
                ("notify_customer_on_success", models.BooleanField(default=True, verbose_name="اعلان موفقیت به مشتری")),
                ("notify_customer_on_failure", models.BooleanField(default=True, verbose_name="اعلان خطای نهایی به مشتری")),
                ("email_customer_on_success", models.BooleanField(default=False, verbose_name="ایمیل موفقیت به مشتری")),
                ("email_customer_on_failure", models.BooleanField(default=False, verbose_name="ایمیل خطای نهایی به مشتری")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_link_queue_controls", to=settings.AUTH_USER_MODEL, verbose_name="آخرین ویرایش‌کننده")),
            ],
            options={
                "verbose_name": "تنظیمات صف تحلیل لینک",
                "verbose_name_plural": "تنظیمات صف تحلیل لینک",
            },
        ),
        migrations.CreateModel(
            name="LinkAnalysisAdapterPolicy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("adapter_key", models.CharField(choices=[("makerworld", "MakerWorld"), ("printables", "Printables"), ("thingiverse", "Thingiverse"), ("grabcad", "GrabCAD"), ("direct_file", "لینک مستقیم فایل"), ("generic", "تحلیل عمومی وب")], db_index=True, max_length=40, unique=True, verbose_name="Adapter")),
                ("display_name", models.CharField(blank=True, max_length=120, verbose_name="نام نمایشی")),
                ("domain_patterns", models.JSONField(blank=True, default=list, verbose_name="دامنه‌های منطبق")),
                ("is_enabled", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
                ("paused_until", models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="توقف تا")),
                ("priority_override", models.SmallIntegerField(blank=True, null=True, verbose_name="اولویت جایگزین")),
                ("max_attempts", models.PositiveSmallIntegerField(default=4, verbose_name="حداکثر تلاش")),
                ("retry_delays_seconds", models.JSONField(blank=True, default=list, verbose_name="فواصل Retry ثانیه")),
                ("request_timeout_seconds", models.PositiveSmallIntegerField(default=20, verbose_name="مهلت دریافت صفحه ثانیه")),
                ("cache_remote_images", models.BooleanField(default=True, verbose_name="ذخیره تصویر منبع")),
                ("notify_on_success", models.BooleanField(default=True, verbose_name="اعلان موفقیت")),
                ("notify_on_failure", models.BooleanField(default=True, verbose_name="اعلان شکست")),
                ("success_count", models.PositiveBigIntegerField(default=0, verbose_name="تعداد موفق")),
                ("failure_count", models.PositiveBigIntegerField(default=0, verbose_name="تعداد ناموفق")),
                ("consecutive_failure_count", models.PositiveIntegerField(default=0, verbose_name="خطاهای پیاپی")),
                ("last_success_at", models.DateTimeField(blank=True, null=True, verbose_name="آخرین موفقیت")),
                ("last_failure_at", models.DateTimeField(blank=True, null=True, verbose_name="آخرین شکست")),
                ("last_error", models.TextField(blank=True, verbose_name="آخرین خطا")),
                ("notes", models.TextField(blank=True, verbose_name="یادداشت اجرایی")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "سیاست Adapter تحلیل لینک",
                "verbose_name_plural": "سیاست‌های Adapter تحلیل لینک",
                "ordering": ["adapter_key"],
            },
        ),
        migrations.CreateModel(
            name="LinkAnalysisWorkerHeartbeat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("worker_id", models.CharField(db_index=True, max_length=180, unique=True, verbose_name="شناسه Worker")),
                ("hostname", models.CharField(blank=True, max_length=180, verbose_name="نام میزبان")),
                ("process_id", models.PositiveIntegerField(default=0, verbose_name="PID")),
                ("status", models.CharField(choices=[("starting", "در حال شروع"), ("idle", "آماده"), ("running", "در حال پردازش"), ("stopping", "در حال توقف"), ("stopped", "متوقف"), ("error", "خطا")], db_index=True, default="starting", max_length=20, verbose_name="وضعیت")),
                ("started_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="زمان شروع")),
                ("last_seen_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="آخرین Heartbeat")),
                ("stopped_at", models.DateTimeField(blank=True, null=True, verbose_name="زمان توقف")),
                ("loop_count", models.PositiveBigIntegerField(default=0, verbose_name="تعداد چرخه")),
                ("processed_count", models.PositiveBigIntegerField(default=0, verbose_name="کل پردازش")),
                ("succeeded_count", models.PositiveBigIntegerField(default=0, verbose_name="موفق")),
                ("failed_count", models.PositiveBigIntegerField(default=0, verbose_name="ناموفق")),
                ("last_error", models.TextField(blank=True, verbose_name="آخرین خطا")),
                ("worker_version", models.CharField(default="phase25", max_length=40, verbose_name="نسخه Worker")),
                ("metadata", models.JSONField(blank=True, default=dict, verbose_name="اطلاعات اجرا")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("current_job", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="worker_heartbeats", to="store.customerlinkanalysisjob", verbose_name="Job فعلی")),
            ],
            options={
                "verbose_name": "Heartbeat Worker تحلیل لینک",
                "verbose_name_plural": "Heartbeatهای Worker تحلیل لینک",
                "ordering": ["-last_seen_at", "worker_id"],
            },
        ),
        migrations.AddIndex(
            model_name="linkanalysisworkerheartbeat",
            index=models.Index(fields=["status", "-last_seen_at"], name="store_link_worker_health_idx"),
        ),
        migrations.CreateModel(
            name="LinkAnalysisOperationsDashboard",
            fields=[],
            options={
                "verbose_name": "داشبورد عملیات تحلیل لینک",
                "verbose_name_plural": "داشبورد عملیات تحلیل لینک",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("store.customerlinkanalysisjob",),
        ),
        migrations.RunPython(seed_adapter_policies, reverse_seed),
    ]
