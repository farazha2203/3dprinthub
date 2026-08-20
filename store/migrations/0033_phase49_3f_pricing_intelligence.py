from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0032_phase49_slider_media_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="productcatalogprofile",
            name="pricing_strategy",
            field=models.CharField(
                choices=[
                    ("legacy", "رفتار قبلی"),
                    ("fixed", "قیمت قطعی"),
                    ("dynamic", "قیمت محاسباتی"),
                ],
                db_index=True,
                default="legacy",
                max_length=20,
                verbose_name="روش قیمت‌گذاری Catalog Center",
            ),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="pricing_inputs",
            field=models.JSONField(
                blank=True,
                default=dict,
                verbose_name="ورودی‌های محاسبه قیمت Catalog Center",
            ),
        ),
        migrations.AddField(
            model_name="productcatalogprofile",
            name="technical_summary_fa",
            field=models.TextField(
                blank=True,
                verbose_name="خلاصه فنی فارسی قابل فهم برای مشتری",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="part_weight_grams",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name="وزن خود قطعه (گرم)",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="support_weight_grams",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name="وزن ساپورت (گرم)",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="support_cost_multiplier",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("1.00"),
                max_digits=6,
                verbose_name="ضریب هزینه ساپورت",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="supervision_hourly_rate_override",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name="نرخ ساعتی نظارت اختصاصی",
            ),
        ),
    ]
