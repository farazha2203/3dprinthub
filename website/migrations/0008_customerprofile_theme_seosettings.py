from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[("website","0007_customerprofile_extended")]
    operations=[
        migrations.AddField(model_name="customerprofile",name="theme_preference",field=models.CharField(choices=[("original","رنگ‌بندی اصلی"),("brand-gold","طلایی و سرمه‌ای"),("hybrid","ترکیبی")],default="original",max_length=20,verbose_name="رنگ‌بندی انتخابی")),
        migrations.AddField(model_name="customerprofile",name="theme_prompt_seen",field=models.BooleanField(default=False,verbose_name="انتخاب رنگ نمایش داده شده")),
        migrations.CreateModel(name="SEOSettings",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("site_name",models.CharField(default="3DprintHub.ir",max_length=120,verbose_name="نام سایت")),
            ("site_url",models.URLField(default="https://3dprinthub.ir",verbose_name="آدرس اصلی سایت")),
            ("default_meta_title",models.CharField(default="3DprintHub.ir | طراحی و چاپ سه‌بعدی",max_length=180,verbose_name="عنوان پیش‌فرض سئو")),
            ("default_meta_description",models.CharField(default="طراحی، چاپ سه‌بعدی، مهندسی معکوس و ساخت قطعات صنعتی و سفارشی.",max_length=320,verbose_name="توضیح پیش‌فرض سئو")),
            ("default_og_image",models.ImageField(blank=True,null=True,upload_to="seo/",verbose_name="تصویر پیش‌فرض اشتراک‌گذاری")),
            ("organization_name",models.CharField(default="3DprintHub",max_length=180,verbose_name="نام سازمان در اسکیما")),
            ("organization_logo",models.ImageField(blank=True,null=True,upload_to="seo/",verbose_name="لوگوی سازمان در اسکیما")),
            ("google_site_verification",models.CharField(blank=True,max_length=255,verbose_name="کد تأیید Google Search Console")),
            ("bing_site_verification",models.CharField(blank=True,max_length=255,verbose_name="کد تأیید Bing Webmaster")),
            ("allow_search_indexing",models.BooleanField(default=True,verbose_name="اجازه ایندکس سایت")),
            ("twitter_card",models.CharField(choices=[("summary","Summary"),("summary_large_image","Summary Large Image")],default="summary_large_image",max_length=30,verbose_name="نوع Twitter Card")),
            ("robots_extra",models.TextField(blank=True,verbose_name="دستورات اضافه robots.txt")),
            ("updated_at",models.DateTimeField(auto_now=True)),
        ],options={"verbose_name":"تنظیمات سئو سایت","verbose_name_plural":"تنظیمات سئو سایت"}),
    ]
