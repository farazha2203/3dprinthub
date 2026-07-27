from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0002_store_commerce"),
    ]

    operations = [
        migrations.AddField(model_name="storeaddress", name="district", field=models.CharField(blank=True, max_length=120, verbose_name="منطقه / محله")),
        migrations.AddField(model_name="storeaddress", name="plaque", field=models.CharField(blank=True, max_length=20, verbose_name="پلاک")),
        migrations.AddField(model_name="storeaddress", name="unit", field=models.CharField(blank=True, max_length=20, verbose_name="واحد")),
        migrations.AddField(model_name="storeaddress", name="recipient_national_code", field=models.CharField(blank=True, max_length=10, verbose_name="کد ملی تحویل‌گیرنده")),
        migrations.AddField(model_name="storeaddress", name="delivery_notes", field=models.CharField(blank=True, max_length=300, verbose_name="توضیحات تحویل")),
    ]
