from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[("website","0008_customerprofile_theme_seosettings")]
    operations=[
        migrations.CreateModel(name="IranProvince",fields=[("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),("name",models.CharField(db_index=True,max_length=100,unique=True,verbose_name="استان")),("code",models.CharField(blank=True,db_index=True,max_length=20,verbose_name="کد استان")),("is_active",models.BooleanField(db_index=True,default=True,verbose_name="فعال")),("sort_order",models.PositiveSmallIntegerField(default=0,verbose_name="ترتیب"))],options={"verbose_name":"استان ایران","verbose_name_plural":"استان‌های ایران","ordering":["sort_order","name"]}),
        migrations.CreateModel(name="IranCounty",fields=[("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),("name",models.CharField(db_index=True,max_length=120,verbose_name="شهرستان")),("code",models.CharField(blank=True,db_index=True,max_length=30,verbose_name="کد شهرستان")),("is_active",models.BooleanField(db_index=True,default=True,verbose_name="فعال")),("province",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="counties",to="website.iranprovince",verbose_name="استان"))],options={"verbose_name":"شهرستان ایران","verbose_name_plural":"شهرستان‌های ایران","ordering":["province__sort_order","name"]}),
        migrations.CreateModel(name="IranCity",fields=[("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),("name",models.CharField(db_index=True,max_length=120,verbose_name="شهر")),("district_name",models.CharField(blank=True,max_length=120,verbose_name="بخش")),("division_code",models.CharField(blank=True,db_index=True,max_length=30,verbose_name="کد تقسیمات کشوری")),("source_id",models.CharField(blank=True,db_index=True,max_length=100,verbose_name="شناسه منبع")),("is_active",models.BooleanField(db_index=True,default=True,verbose_name="فعال")),("county",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="cities",to="website.irancounty",verbose_name="شهرستان")),("province",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="cities",to="website.iranprovince",verbose_name="استان"))],options={"verbose_name":"شهر ایران","verbose_name_plural":"شهرهای ایران","ordering":["province__sort_order","county__name","name"]}),
        migrations.AddConstraint(model_name="irancounty",constraint=models.UniqueConstraint(fields=("province","name"),name="unique_iran_county_per_province")),
        migrations.AddConstraint(model_name="irancity",constraint=models.UniqueConstraint(fields=("province","county","name"),name="unique_iran_city_per_county")),
        migrations.AddField(model_name="seosettings",name="organization_phone",field=models.CharField(blank=True,max_length=30,verbose_name="تلفن سازمان")),
        migrations.AddField(model_name="seosettings",name="organization_email",field=models.EmailField(blank=True,max_length=254,verbose_name="ایمیل سازمان")),
        migrations.AddField(model_name="seosettings",name="street_address",field=models.CharField(blank=True,max_length=255,verbose_name="نشانی سازمان")),
        migrations.AddField(model_name="seosettings",name="address_locality",field=models.CharField(blank=True,max_length=100,verbose_name="شهر سازمان")),
        migrations.AddField(model_name="seosettings",name="address_region",field=models.CharField(blank=True,max_length=100,verbose_name="استان سازمان")),
        migrations.AddField(model_name="seosettings",name="organization_postal_code",field=models.CharField(blank=True,max_length=20,verbose_name="کد پستی سازمان")),
        migrations.AddField(model_name="seosettings",name="country_code",field=models.CharField(default="IR",max_length=2,verbose_name="کد کشور")),
        migrations.AddField(model_name="seosettings",name="same_as",field=models.TextField(blank=True,help_text="هر لینک در یک خط",verbose_name="شبکه‌های اجتماعی")),
        migrations.AddField(model_name="seosettings",name="merchant_return_days",field=models.PositiveSmallIntegerField(default=7,verbose_name="مهلت بازگشت کالا (روز)")),
        migrations.AddField(model_name="seosettings",name="shipping_rate",field=models.PositiveIntegerField(default=0,verbose_name="هزینه پایه ارسال در اسکیما (تومان)")),
        migrations.AddField(model_name="seosettings",name="handling_min_days",field=models.PositiveSmallIntegerField(default=1,verbose_name="حداقل زمان آماده‌سازی")),
        migrations.AddField(model_name="seosettings",name="handling_max_days",field=models.PositiveSmallIntegerField(default=3,verbose_name="حداکثر زمان آماده‌سازی")),
        migrations.AddField(model_name="seosettings",name="transit_min_days",field=models.PositiveSmallIntegerField(default=1,verbose_name="حداقل زمان حمل")),
        migrations.AddField(model_name="seosettings",name="transit_max_days",field=models.PositiveSmallIntegerField(default=7,verbose_name="حداکثر زمان حمل")),
    ]
