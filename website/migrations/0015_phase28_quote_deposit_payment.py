import uuid
import website.private_storage
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("website", "0014_support_chat_google_profile_and_order_attachments")]

    operations = [
        migrations.AddField(
            model_name="sitesetting",
            name="payment_card_number",
            field=models.CharField(blank=True, max_length=32, verbose_name="شماره کارت دریافت وجه"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="payment_card_holder",
            field=models.CharField(blank=True, max_length=150, verbose_name="نام صاحب کارت"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="default_deposit_percent",
            field=models.PositiveSmallIntegerField(default=30, verbose_name="درصد پیش‌فرض بیعانه"),
        ),
        migrations.AddField(
            model_name="quote",
            name="deposit_percent",
            field=models.DecimalField(decimal_places=2, default=30, max_digits=5, verbose_name="درصد بیعانه"),
        ),
        migrations.AddField(
            model_name="payment",
            name="payment_kind",
            field=models.CharField(choices=[("deposit", "بیعانه"), ("full", "پرداخت کامل"), ("balance", "تسویه مانده")], default="deposit", max_length=20, verbose_name="نوع پرداخت"),
        ),
        migrations.AddField(
            model_name="payment",
            name="idempotency_key",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name="payment",
            name="note",
            field=models.TextField(blank=True, verbose_name="توضیحات پرداخت"),
        ),
        migrations.AlterField(
            model_name="payment",
            name="status",
            field=models.CharField(choices=[("pending", "در انتظار پرداخت"), ("awaiting_review", "در انتظار بررسی رسید"), ("paid", "پرداخت موفق"), ("failed", "پرداخت ناموفق"), ("cancelled", "لغو شده")], default="pending", max_length=20, verbose_name="وضعیت پرداخت"),
        ),
        migrations.AlterField(
            model_name="payment",
            name="receipt_image",
            field=models.ImageField(blank=True, null=True, storage=website.private_storage.PrivateModelStorage(), upload_to="payments/receipts/", verbose_name="تصویر رسید پرداخت دستی"),
        ),
    ]
