from django.db import migrations, models


SLIDER_EFFECT_CHOICES = [
    ("cinematic_fade", "Cinematic Fade"),
    ("wedding_dissolve", "Wedding Dissolve"),
    ("cinematic_zoom", "Cinematic Zoom"),
    ("ken_burns", "Ken Burns Fade"),
    ("soft_blur", "Soft Blur Dissolve"),
    ("cinematic_reveal", "Cinematic Reveal"),
]


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("store", "0029_epic49_catalog_product_backfill"),
    ]

    operations = [
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_title_fa",
            field=models.CharField(blank=True, max_length=220, verbose_name="عنوان اختصاصی اسلایدر"),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_description_fa",
            field=models.TextField(blank=True, verbose_name="توضیح اختصاصی اسلایدر"),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_alt_text",
            field=models.CharField(blank=True, max_length=240, verbose_name="Alt اختصاصی تصویر اسلایدر"),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_button_text",
            field=models.CharField(blank=True, default="مشاهده محصول", max_length=80, verbose_name="متن دکمه اسلایدر"),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_focus_keyword",
            field=models.CharField(blank=True, max_length=180, verbose_name="عبارت کلیدی اسلایدر"),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_transition_effect",
            field=models.CharField(choices=SLIDER_EFFECT_CHOICES, default="cinematic_fade", max_length=32, verbose_name="افکت اسلایدر"),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_transition_duration_ms",
            field=models.PositiveIntegerField(default=1400, verbose_name="مدت Transition اسلایدر"),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="homepage_slider_display_duration_ms",
            field=models.PositiveIntegerField(default=7000, verbose_name="مدت نمایش اسلایدر"),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="sync_revision",
            field=models.PositiveBigIntegerField(db_index=True, default=1, verbose_name="نسخه همگام‌سازی"),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="last_modified_source",
            field=models.CharField(db_index=True, default="desktop", max_length=20, verbose_name="منبع آخرین تغییر"),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="last_modified_by",
            field=models.CharField(blank=True, max_length=120, verbose_name="عامل آخرین تغییر"),
        ),
    ]
