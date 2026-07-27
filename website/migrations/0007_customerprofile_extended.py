from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0006_remove_materialpartguide_alternative_materials_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerprofile",
            name="avatar",
            field=models.ImageField(blank=True, null=True, upload_to="customers/avatars/", verbose_name="تصویر پروفایل"),
        ),
        migrations.AddField(
            model_name="customerprofile",
            name="father_name",
            field=models.CharField(blank=True, max_length=100, verbose_name="نام پدر"),
        ),
        migrations.AddField(
            model_name="customerprofile",
            name="birth_date",
            field=models.DateField(blank=True, null=True, verbose_name="تاریخ تولد"),
        ),
        migrations.AddField(
            model_name="customerprofile",
            name="gender",
            field=models.CharField(blank=True, choices=[("male", "مرد"), ("female", "زن"), ("other", "سایر")], max_length=20, verbose_name="جنسیت"),
        ),
        migrations.AddField(
            model_name="customerprofile",
            name="landline",
            field=models.CharField(blank=True, max_length=20, verbose_name="تلفن ثابت"),
        ),
        migrations.AddField(
            model_name="customerprofile",
            name="occupation",
            field=models.CharField(blank=True, max_length=120, verbose_name="شغل / سمت"),
        ),
    ]
