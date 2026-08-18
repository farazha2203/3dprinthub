from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0019_phase45_managed_homepage_hero"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepageheroslide",
            name="selected_asset_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="store.importedprintassetimage",
                verbose_name="تصویر انتخاب‌شده از آلبوم محصول",
                help_text="در Hero Studio با کلیک روی تصویر ذخیره می‌شود و از URL موقت مستقل است.",
            ),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="transition_effect",
            field=models.CharField(
                choices=[
                    ("cinematic_fade", "Cinematic Fade — محوشدن سینمایی"),
                    ("wedding_dissolve", "Wedding Dissolve — دیزالو نرم"),
                    ("cinematic_zoom", "Cinematic Zoom — زوم سینمایی"),
                    ("ken_burns", "Ken Burns Fade — پن و زوم آرام"),
                    ("soft_blur", "Soft Blur Dissolve — محوشدن با بلور"),
                    ("cinematic_reveal", "Cinematic Reveal — آشکارسازی سینمایی"),
                ],
                default="cinematic_fade",
                max_length=32,
                verbose_name="افکت تعویض اسلاید",
            ),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="transition_duration_ms",
            field=models.PositiveIntegerField(
                default=1400,
                validators=[MinValueValidator(300), MaxValueValidator(4000)],
                verbose_name="مدت افکت (میلی‌ثانیه)",
                help_text="بین 300 تا 4000 میلی‌ثانیه.",
            ),
        ),
        migrations.AddField(
            model_name="homepageheroslide",
            name="display_duration_ms",
            field=models.PositiveIntegerField(
                default=7000,
                validators=[MinValueValidator(2000), MaxValueValidator(30000)],
                verbose_name="مدت نمایش اسلاید (میلی‌ثانیه)",
                help_text="بین 2000 تا 30000 میلی‌ثانیه.",
            ),
        ),
    ]
