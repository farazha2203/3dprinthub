from django.db import migrations, models
from django.utils import timezone


def seed_phase35_defaults(apps, schema_editor):
    Asset = apps.get_model("store", "ImportedPrintAsset")
    Product = apps.get_model("store", "Product")
    Asset.objects.filter(fixed_print_price=0).update(
        fixed_print_price=500_000,
        price_status="estimated",
        price_is_final=False,
        pricing_note="قیمت علی‌الحساب است و پس از بررسی اپراتور قطعی می‌شود.",
    )
    Asset.objects.exclude(persian_title="").filter(translation_status="missing").update(
        translation_status="draft"
    )
    Product.objects.filter(fixed_price__gt=0).update(
        price_note="قیمت علی‌الحساب است و پس از بررسی اپراتور قطعی می‌شود."
    )


class Migration(migrations.Migration):
    dependencies = [("store", "0024_phase34b_makerworld_editorial_commerce")]
    operations = [
        migrations.AddField(model_name="importedprintasset", name="translation_status", field=models.CharField(choices=[("missing","ترجمه نشده"),("draft","پیش‌نویس خودکار"),("translated","ترجمه ماشینی"),("reviewed","ترجمه بازبینی‌شده")], db_index=True, default="missing", max_length=20, verbose_name="وضعیت ترجمه")),
        migrations.AddField(model_name="importedprintasset", name="translation_provider", field=models.CharField(blank=True, max_length=40, verbose_name="موتور ترجمه")),
        migrations.AddField(model_name="importedprintasset", name="translated_at", field=models.DateTimeField(blank=True, null=True, verbose_name="زمان ترجمه")),
        migrations.AddField(model_name="importedprintasset", name="price_status", field=models.CharField(choices=[("unset","قیمت‌گذاری نشده"),("estimated","علی‌الحساب"),("final","قطعی")], db_index=True, default="unset", max_length=20, verbose_name="وضعیت قیمت")),
        migrations.AddField(model_name="importedprintasset", name="price_is_final", field=models.BooleanField(db_index=True, default=False, verbose_name="قیمت قطعی است")),
        migrations.AddField(model_name="importedprintasset", name="pricing_note", field=models.CharField(blank=True, default="قیمت علی‌الحساب است و پس از بررسی اپراتور قطعی می‌شود.", max_length=300, verbose_name="یادداشت قیمت")),
        migrations.AddField(model_name="importedprintasset", name="estimated_material_cost", field=models.PositiveBigIntegerField(default=0, verbose_name="برآورد هزینه متریال به تومان")),
        migrations.AddField(model_name="product", name="title_en", field=models.CharField(blank=True, max_length=220, verbose_name="عنوان انگلیسی")),
        migrations.AddField(model_name="product", name="short_description_en", field=models.CharField(blank=True, max_length=500, verbose_name="توضیح کوتاه انگلیسی")),
        migrations.AddField(model_name="product", name="description_en", field=models.TextField(blank=True, verbose_name="توضیحات انگلیسی")),
        migrations.AddField(model_name="product", name="source_url", field=models.URLField(blank=True, max_length=1000, verbose_name="لینک مرجع اصلی")),
        migrations.AddField(model_name="product", name="source_name", field=models.CharField(blank=True, max_length=120, verbose_name="نام منبع")),
        migrations.AddField(model_name="product", name="source_external_id", field=models.CharField(blank=True, db_index=True, max_length=160, verbose_name="شناسه منبع")),
        migrations.AddField(model_name="product", name="price_is_final", field=models.BooleanField(db_index=True, default=False, verbose_name="قیمت قطعی است")),
        migrations.AddField(model_name="product", name="price_note", field=models.CharField(blank=True, default="قیمت علی‌الحساب است و پس از بررسی اپراتور قطعی می‌شود.", max_length=300, verbose_name="یادداشت قیمت")),
        migrations.RunPython(seed_phase35_defaults, migrations.RunPython.noop),
    ]
