import uuid

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [("website", "0016_phase29_billable_time_rounding")]

    operations = [
        migrations.AddField(
            model_name="sitesetting",
            name="online_payment_enabled",
            field=models.BooleanField(default=False, verbose_name="درگاه پرداخت آنلاین فعال باشد؟"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="online_payment_provider",
            field=models.CharField(choices=[("zarinpal", "زرین‌پال")], default="zarinpal", max_length=30, verbose_name="درگاه پرداخت آنلاین"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="online_payment_title",
            field=models.CharField(default="پرداخت امن آنلاین", max_length=120, verbose_name="عنوان نمایش درگاه"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="online_payment_minimum_toman",
            field=models.PositiveIntegerField(default=1000, verbose_name="حداقل مبلغ پرداخت آنلاین به تومان"),
        ),
        migrations.AlterField(
            model_name="payment",
            name="status",
            field=models.CharField(choices=[("pending", "در انتظار پرداخت"), ("verifying", "در حال تأیید درگاه"), ("awaiting_review", "در انتظار بررسی رسید"), ("paid", "پرداخت موفق"), ("failed", "پرداخت ناموفق"), ("cancelled", "لغو شده")], default="pending", max_length=20, verbose_name="وضعیت پرداخت"),
        ),
        migrations.AddField(model_name="payment", name="callback_token", field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
        migrations.AddField(model_name="payment", name="provider", field=models.CharField(blank=True, db_index=True, default="", max_length=30, verbose_name="ارائه‌دهنده درگاه")),
        migrations.AddField(model_name="payment", name="gateway_amount", field=models.PositiveBigIntegerField(default=0, verbose_name="مبلغ ارسال‌شده به درگاه")),
        migrations.AddField(model_name="payment", name="gateway_currency", field=models.CharField(default="IRT", max_length=8, verbose_name="واحد مبلغ درگاه")),
        migrations.AddField(model_name="payment", name="checkout_url", field=models.URLField(blank=True, max_length=800, verbose_name="لینک پرداخت درگاه")),
        migrations.AddField(model_name="payment", name="provider_status_code", field=models.IntegerField(blank=True, null=True, verbose_name="کد وضعیت درگاه")),
        migrations.AddField(model_name="payment", name="provider_message", field=models.CharField(blank=True, max_length=500, verbose_name="پیام درگاه")),
        migrations.AddField(model_name="payment", name="request_payload", field=models.JSONField(blank=True, default=dict, verbose_name="درخواست ارسال‌شده به درگاه")),
        migrations.AddField(model_name="payment", name="raw_response", field=models.JSONField(blank=True, default=dict, verbose_name="پاسخ خام درگاه")),
        migrations.AddField(model_name="payment", name="callback_payload", field=models.JSONField(blank=True, default=dict, verbose_name="پارامترهای بازگشت درگاه")),
        migrations.AddField(model_name="payment", name="client_ip", field=models.GenericIPAddressField(blank=True, null=True, verbose_name="IP شروع‌کننده پرداخت")),
        migrations.AddField(model_name="payment", name="user_agent", field=models.CharField(blank=True, max_length=500, verbose_name="مرورگر شروع‌کننده")),
        migrations.AddField(model_name="payment", name="initiated_at", field=models.DateTimeField(blank=True, null=True, verbose_name="زمان ایجاد Authority")),
        migrations.AddField(model_name="payment", name="callback_received_at", field=models.DateTimeField(blank=True, null=True, verbose_name="زمان دریافت Callback")),
        migrations.AddField(model_name="payment", name="verified_at", field=models.DateTimeField(blank=True, null=True, verbose_name="زمان تأیید سمت سرور")),
        migrations.AddField(model_name="payment", name="failed_at", field=models.DateTimeField(blank=True, null=True, verbose_name="زمان شکست")),
        migrations.AddField(model_name="payment", name="retry_count", field=models.PositiveSmallIntegerField(default=0, verbose_name="تعداد تلاش تأیید")),
        migrations.AddField(model_name="payment", name="updated_at", field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now, verbose_name="آخرین بروزرسانی"), preserve_default=False),
        migrations.CreateModel(
            name="PaymentLedgerEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("entry_type", models.CharField(choices=[("payment", "دریافت وجه"), ("refund", "استرداد وجه"), ("adjustment", "اصلاح مالی")], db_index=True, default="payment", max_length=20, verbose_name="نوع ثبت")),
                ("direction", models.CharField(choices=[("credit", "بستانکار"), ("debit", "بدهکار")], default="credit", max_length=10, verbose_name="جهت")),
                ("amount", models.PositiveBigIntegerField(verbose_name="مبلغ به تومان")),
                ("currency", models.CharField(default="IRT", max_length=8, verbose_name="واحد")),
                ("event_key", models.CharField(db_index=True, max_length=180, unique=True, verbose_name="کلید یکتای رویداد")),
                ("provider_ref", models.CharField(blank=True, db_index=True, max_length=255, verbose_name="شناسه مرجع درگاه")),
                ("description", models.CharField(blank=True, max_length=500, verbose_name="شرح")),
                ("metadata", models.JSONField(blank=True, default=dict, verbose_name="اطلاعات تکمیلی")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="زمان ثبت")),
                ("payment", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ledger_entries", to="website.payment", verbose_name="پرداخت")),
                ("quote", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ledger_entries", to="website.quote", verbose_name="پیش‌فاکتور")),
            ],
            options={"verbose_name": "ثبت دفتر مالی پرداخت", "verbose_name_plural": "دفتر مالی پرداخت‌ها", "ordering": ["-created_at", "-id"]},
        ),
        migrations.AddIndex(model_name="payment", index=models.Index(fields=["provider", "authority"], name="webpay_provider_auth_idx")),
        migrations.AddIndex(model_name="payment", index=models.Index(fields=["status", "created_at"], name="webpay_status_created_idx")),
        migrations.AddIndex(model_name="paymentledgerentry", index=models.Index(fields=["quote", "created_at"], name="webpay_ledger_quote_idx")),
    ]
