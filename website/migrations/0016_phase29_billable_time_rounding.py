from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("website", "0015_phase28_quote_deposit_payment")]
    operations = [
        migrations.AddField(
            model_name="quote",
            name="minimum_billable_minutes",
            field=models.PositiveIntegerField(default=60, verbose_name="حداقل زمان قابل محاسبه به دقیقه"),
        ),
        migrations.AddField(
            model_name="quote",
            name="billing_increment_minutes",
            field=models.PositiveIntegerField(default=60, verbose_name="پله گردکردن زمان چاپ به دقیقه"),
        ),
    ]
