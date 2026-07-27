from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def backfill_pending_jobs(apps, schema_editor):
    Analysis = apps.get_model("store", "CustomerLinkAnalysis")
    Job = apps.get_model("store", "CustomerLinkAnalysisJob")
    now = django.utils.timezone.now()
    for analysis in Analysis.objects.filter(status__in=["pending", "processing"]).iterator(chunk_size=500):
        Analysis.objects.filter(pk=analysis.pk).update(status="pending")
        Job.objects.get_or_create(
            analysis_id=analysis.pk,
            defaults={
                "status": "queued",
                "priority": 100,
                "max_attempts": 4,
                "next_run_at": now,
                "progress_stage": "queued",
                "progress_message": "در انتظار پردازش پس از ارتقا",
            },
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0016_phase23_catalog_link_intelligence"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomerLinkAnalysisJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("queued", "در صف"), ("running", "در حال پردازش"), ("retry", "در انتظار تلاش مجدد"), ("completed", "تکمیل‌شده"), ("failed", "ناموفق"), ("cancelled", "لغوشده")], db_index=True, default="queued", max_length=20, verbose_name="وضعیت صف")),
                ("priority", models.SmallIntegerField(db_index=True, default=100, verbose_name="اولویت")),
                ("attempt_count", models.PositiveSmallIntegerField(default=0, verbose_name="تعداد تلاش")),
                ("max_attempts", models.PositiveSmallIntegerField(default=4, verbose_name="حداکثر تلاش")),
                ("next_run_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="زمان اجرای بعدی")),
                ("locked_at", models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="زمان قفل")),
                ("worker_id", models.CharField(blank=True, max_length=180, verbose_name="شناسه Worker")),
                ("progress_percent", models.PositiveSmallIntegerField(default=0, verbose_name="درصد پیشرفت")),
                ("progress_stage", models.CharField(blank=True, max_length=80, verbose_name="مرحله فعلی")),
                ("progress_message", models.CharField(blank=True, max_length=300, verbose_name="پیام پیشرفت")),
                ("last_error_type", models.CharField(blank=True, max_length=160, verbose_name="نوع آخرین خطا")),
                ("last_error", models.TextField(blank=True, verbose_name="آخرین خطا")),
                ("last_started_at", models.DateTimeField(blank=True, null=True, verbose_name="شروع آخرین تلاش")),
                ("completed_at", models.DateTimeField(blank=True, null=True, verbose_name="زمان تکمیل")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("analysis", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="job", to="store.customerlinkanalysis", verbose_name="تحلیل لینک")),
            ],
            options={
                "verbose_name": "صف تحلیل لینک مشتری",
                "verbose_name_plural": "صف تحلیل لینک‌های مشتریان",
                "ordering": ["-priority", "next_run_at", "id"],
            },
        ),
        migrations.CreateModel(
            name="CustomerLinkAnalysisAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attempt_number", models.PositiveSmallIntegerField(verbose_name="شماره تلاش")),
                ("status", models.CharField(choices=[("running", "در حال اجرا"), ("success", "موفق"), ("transient_failure", "خطای موقت"), ("permanent_failure", "خطای قطعی")], db_index=True, default="running", max_length=24)),
                ("stage", models.CharField(blank=True, max_length=80, verbose_name="آخرین مرحله")),
                ("error_type", models.CharField(blank=True, max_length=160, verbose_name="نوع خطا")),
                ("error_message", models.TextField(blank=True, verbose_name="متن خطا")),
                ("started_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("duration_ms", models.PositiveBigIntegerField(default=0, verbose_name="مدت اجرا میلی‌ثانیه")),
                ("worker_id", models.CharField(blank=True, max_length=180, verbose_name="شناسه Worker")),
                ("job", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attempts", to="store.customerlinkanalysisjob", verbose_name="Job تحلیل")),
            ],
            options={
                "verbose_name": "تلاش تحلیل لینک",
                "verbose_name_plural": "تلاش‌های تحلیل لینک",
                "ordering": ["-started_at", "-id"],
            },
        ),
        migrations.AddIndex(
            model_name="customerlinkanalysisjob",
            index=models.Index(fields=["status", "next_run_at", "-priority"], name="store_link_job_queue_idx"),
        ),
        migrations.AddIndex(
            model_name="customerlinkanalysisjob",
            index=models.Index(fields=["status", "locked_at"], name="store_link_job_lock_idx"),
        ),
        migrations.AddIndex(
            model_name="customerlinkanalysisattempt",
            index=models.Index(fields=["job", "-started_at"], name="store_link_attempt_job_idx"),
        ),
        migrations.AddIndex(
            model_name="customerlinkanalysisattempt",
            index=models.Index(fields=["status", "-started_at"], name="store_link_attempt_status_idx"),
        ),
        migrations.AddConstraint(
            model_name="customerlinkanalysisattempt",
            constraint=models.UniqueConstraint(fields=("job", "attempt_number"), name="store_link_attempt_unique"),
        ),
        migrations.RunPython(backfill_pending_jobs, noop_reverse),
    ]
