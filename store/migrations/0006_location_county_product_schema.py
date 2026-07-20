from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[("store","0005_storeorder_postal_required")]
    operations=[
        migrations.AddField(model_name="storeaddress",name="county",field=models.CharField(blank=True,max_length=120,verbose_name="شهرستان")),
        migrations.AddField(model_name="product",name="brand_name",field=models.CharField(default="3DprintHub",max_length=120,verbose_name="برند محصول")),
        migrations.AddField(model_name="product",name="mpn",field=models.CharField(blank=True,max_length=100,verbose_name="کد MPN")),
        migrations.AddField(model_name="product",name="gtin",field=models.CharField(blank=True,max_length=14,verbose_name="GTIN / بارکد")),
        migrations.AddField(model_name="product",name="schema_enabled",field=models.BooleanField(default=True,verbose_name="ساخت اسکیما محصول")),
    ]
