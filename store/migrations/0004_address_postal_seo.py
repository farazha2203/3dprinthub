from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[("store","0003_storeaddress_details")]
    operations=[
        migrations.AlterField(model_name="storeaddress",name="postal_code",field=models.CharField(max_length=20,verbose_name="کد پستی")),
        migrations.AddField(model_name="category",name="seo_focus_keyword",field=models.CharField(blank=True,max_length=180,verbose_name="عبارت کلیدی اصلی")),
        migrations.AddField(model_name="category",name="canonical_url",field=models.URLField(blank=True,verbose_name="Canonical اختصاصی")),
        migrations.AddField(model_name="category",name="robots_index",field=models.BooleanField(db_index=True,default=True,verbose_name="اجازه ایندکس")),
        migrations.AddField(model_name="category",name="robots_follow",field=models.BooleanField(default=True,verbose_name="اجازه دنبال‌کردن لینک‌ها")),
        migrations.AddField(model_name="category",name="og_title",field=models.CharField(blank=True,max_length=180,verbose_name="عنوان Open Graph")),
        migrations.AddField(model_name="category",name="og_description",field=models.CharField(blank=True,max_length=320,verbose_name="توضیح Open Graph")),
        migrations.AddField(model_name="category",name="og_image",field=models.ImageField(blank=True,null=True,upload_to="store/seo/",verbose_name="تصویر Open Graph")),
        migrations.AddField(model_name="product",name="seo_focus_keyword",field=models.CharField(blank=True,max_length=180,verbose_name="عبارت کلیدی اصلی")),
        migrations.AddField(model_name="product",name="canonical_url",field=models.URLField(blank=True,verbose_name="Canonical اختصاصی")),
        migrations.AddField(model_name="product",name="robots_index",field=models.BooleanField(db_index=True,default=True,verbose_name="اجازه ایندکس")),
        migrations.AddField(model_name="product",name="robots_follow",field=models.BooleanField(default=True,verbose_name="اجازه دنبال‌کردن لینک‌ها")),
        migrations.AddField(model_name="product",name="og_title",field=models.CharField(blank=True,max_length=180,verbose_name="عنوان Open Graph")),
        migrations.AddField(model_name="product",name="og_description",field=models.CharField(blank=True,max_length=320,verbose_name="توضیح Open Graph")),
        migrations.AddField(model_name="product",name="og_image",field=models.ImageField(blank=True,null=True,upload_to="store/seo/",verbose_name="تصویر Open Graph")),
        migrations.AddField(model_name="servicepage",name="seo_focus_keyword",field=models.CharField(blank=True,max_length=180,verbose_name="عبارت کلیدی اصلی")),
        migrations.AddField(model_name="servicepage",name="canonical_url",field=models.URLField(blank=True,verbose_name="Canonical اختصاصی")),
        migrations.AddField(model_name="servicepage",name="robots_index",field=models.BooleanField(db_index=True,default=True,verbose_name="اجازه ایندکس")),
        migrations.AddField(model_name="servicepage",name="robots_follow",field=models.BooleanField(default=True,verbose_name="اجازه دنبال‌کردن لینک‌ها")),
        migrations.AddField(model_name="servicepage",name="og_title",field=models.CharField(blank=True,max_length=180,verbose_name="عنوان Open Graph")),
        migrations.AddField(model_name="servicepage",name="og_description",field=models.CharField(blank=True,max_length=320,verbose_name="توضیح Open Graph")),
        migrations.AddField(model_name="servicepage",name="og_image",field=models.ImageField(blank=True,null=True,upload_to="store/seo/",verbose_name="تصویر Open Graph")),
    ]
