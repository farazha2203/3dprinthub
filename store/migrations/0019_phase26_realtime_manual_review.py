from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0018_phase25_worker_operations"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LinkAnalysisManualReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("pending", "در انتظار بررسی"), ("in_progress", "در حال بررسی"), ("resolved", "حل‌شده"), ("rejected", "ردشده"), ("cancelled", "لغوشده")], db_index=True, default="pending", max_length=20, verbose_name="وضعیت")),
                ("reason", models.CharField(choices=[("auto_failed", "شکست تحلیل خودکار"), ("customer_request", "درخواست مشتری"), ("admin_escalation", "ارجاع مدیریت"), ("adapter_blocked", "محدودیت منبع"), ("incomplete_data", "اطلاعات ناقص")], db_index=True, default="customer_request", max_length=30, verbose_name="دلیل")),
                ("priority", models.SmallIntegerField(db_index=True, default=100, verbose_name="اولویت")),
                ("customer_note", models.TextField(blank=True, verbose_name="توضیح مشتری")),
                ("reviewer_note", models.TextField(blank=True, verbose_name="یادداشت کارشناس")),
                ("resolution_action", models.CharField(blank=True, choices=[("", "بدون اقدام نهایی"), ("retry", "تحلیل مجدد"), ("data_completed", "تکمیل دستی اطلاعات"), ("customer_contacted", "ارتباط با مشتری"), ("rejected", "غیرقابل پردازش"), ("no_action", "بدون اقدام")], max_length=30, verbose_name="اقدام نهایی")),
                ("error_snapshot", models.TextField(blank=True, verbose_name="خطای زمان ارجاع")),
                ("source_snapshot", models.JSONField(blank=True, default=dict, verbose_name="خلاصه منبع")),
                ("requested_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="زمان درخواست")),
                ("started_at", models.DateTimeField(blank=True, null=True, verbose_name="شروع بررسی")),
                ("resolved_at", models.DateTimeField(blank=True, null=True, verbose_name="پایان بررسی")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("analysis", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="manual_reviews", to="store.customerlinkanalysis", verbose_name="تحلیل لینک")),
                ("job", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="manual_reviews", to="store.customerlinkanalysisjob", verbose_name="Job مرتبط")),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_link_manual_reviews", to=settings.AUTH_USER_MODEL, verbose_name="کارشناس مسئول")),
                ("requested_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="requested_link_manual_reviews", to=settings.AUTH_USER_MODEL, verbose_name="درخواست‌کننده")),
            ],
            options={
                "verbose_name": "بررسی دستی تحلیل لینک",
                "verbose_name_plural": "صف بررسی دستی تحلیل لینک‌ها",
                "ordering": ["-priority", "requested_at", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="linkanalysismanualreview",
            index=models.Index(fields=["status", "-priority", "requested_at"], name="store_link_review_queue_idx"),
        ),
        migrations.AddIndex(
            model_name="linkanalysismanualreview",
            index=models.Index(fields=["analysis", "status"], name="store_link_review_analysis_idx"),
        ),
    ]
