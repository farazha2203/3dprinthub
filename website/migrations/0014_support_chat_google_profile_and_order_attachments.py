import uuid
import django.db.models.deletion
import website.private_storage
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0013_phase18_catalog_display_defaults"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="customerprofile",
            name="phone",
            field=models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name="شماره تماس"),
        ),
        migrations.CreateModel(
            name="OrderAttachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("file", models.FileField(storage=website.private_storage.PrivateModelStorage(), upload_to="order-attachments/%Y/%m/", verbose_name="فایل خصوصی")),
                ("original_name", models.CharField(max_length=255, verbose_name="نام اصلی فایل")),
                ("content_type", models.CharField(blank=True, max_length=120, verbose_name="نوع فایل")),
                ("size_bytes", models.PositiveBigIntegerField(default=0, verbose_name="حجم فایل")),
                ("note", models.CharField(blank=True, max_length=300, verbose_name="توضیح")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="زمان ارسال")),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attachments", to="website.order", verbose_name="سفارش")),
            ],
            options={"verbose_name": "مدرک یا فایل سفارش", "verbose_name_plural": "مدارک و فایل‌های سفارش", "ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="SupportConversation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("subject", models.CharField(default="گفت‌وگو با پشتیبانی", max_length=220, verbose_name="موضوع")),
                ("status", models.CharField(choices=[("open", "باز"), ("waiting_customer", "منتظر پاسخ مشتری"), ("waiting_staff", "منتظر پاسخ پشتیبانی"), ("closed", "بسته شده")], db_index=True, default="open", max_length=30, verbose_name="وضعیت")),
                ("last_message_at", models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="آخرین پیام")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="بروزرسانی")),
                ("assigned_to", models.ForeignKey(blank=True, limit_choices_to={"is_staff": True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_support_conversations", to=settings.AUTH_USER_MODEL, verbose_name="کارشناس پاسخ‌گو")),
                ("customer", models.ForeignKey(limit_choices_to={"is_staff": False}, on_delete=django.db.models.deletion.CASCADE, related_name="support_conversations", to=settings.AUTH_USER_MODEL, verbose_name="مشتری")),
                ("order", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="support_conversations", to="website.order", verbose_name="سفارش مرتبط")),
            ],
            options={"verbose_name": "گفت‌وگوی پشتیبانی", "verbose_name_plural": "گفت‌وگوهای پشتیبانی", "ordering": ["-last_message_at", "-updated_at"]},
        ),
        migrations.CreateModel(
            name="SupportMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("body", models.TextField(blank=True, verbose_name="متن پیام")),
                ("attachment", models.FileField(blank=True, null=True, storage=website.private_storage.PrivateModelStorage(), upload_to="support-chat/%Y/%m/", verbose_name="پیوست خصوصی")),
                ("attachment_name", models.CharField(blank=True, max_length=255, verbose_name="نام پیوست")),
                ("attachment_content_type", models.CharField(blank=True, max_length=120, verbose_name="نوع پیوست")),
                ("attachment_size", models.PositiveBigIntegerField(default=0, verbose_name="حجم پیوست")),
                ("read_by_customer_at", models.DateTimeField(blank=True, null=True, verbose_name="خوانده‌شده توسط مشتری")),
                ("read_by_staff_at", models.DateTimeField(blank=True, null=True, verbose_name="خوانده‌شده توسط پشتیبانی")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="زمان ارسال")),
                ("conversation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="website.supportconversation", verbose_name="گفت‌وگو")),
                ("sender", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="support_messages", to=settings.AUTH_USER_MODEL, verbose_name="فرستنده")),
            ],
            options={"verbose_name": "پیام پشتیبانی", "verbose_name_plural": "پیام‌های پشتیبانی", "ordering": ["created_at", "id"]},
        ),
    ]
