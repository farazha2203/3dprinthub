from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("website", "0017_phase30_online_payment_gateway")]

    operations = [
        migrations.AddField(
            model_name="sitesetting",
            name="contact_eyebrow",
            field=models.CharField(default="تماس با ما", max_length=120, verbose_name="برچسب بخش تماس"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="contact_title",
            field=models.CharField(default="آماده بررسی پروژه شما هستیم", max_length=255, verbose_name="عنوان بخش تماس"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="contact_description",
            field=models.TextField(default="برای طراحی، ساخت، چاپ سه‌بعدی صنعتی و مهندسی معکوس قطعات با ما در ارتباط باشید.", verbose_name="توضیح بخش تماس"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="contact_location_title",
            field=models.CharField(default="محل فعالیت 3DprintHub.ir", max_length=180, verbose_name="عنوان محل فعالیت"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="telegram_operator_enabled",
            field=models.BooleanField(default=False, verbose_name="اعلان تلگرام برای اپراتور فعال باشد؟"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="telegram_operator_bot_token",
            field=models.CharField(blank=True, help_text="توکن BotFather؛ فقط مدیر ارشد باید به این مقدار دسترسی داشته باشد.", max_length=255, verbose_name="توکن ربات تلگرام اپراتور"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="telegram_operator_chat_id",
            field=models.CharField(blank=True, max_length=120, verbose_name="Chat ID تلگرام اپراتور"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="operator_alert_emails",
            field=models.TextField(blank=True, help_text="چند ایمیل را با ویرگول جدا کنید.", verbose_name="ایمیل‌های اعلان اپراتور"),
        ),
    ]
