from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[("store","0004_address_postal_seo")]
    operations=[
        migrations.AlterField(model_name="storeorder",name="postal_code",field=models.CharField(max_length=20,verbose_name="کد پستی")),
    ]
