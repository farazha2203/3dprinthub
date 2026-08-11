from decimal import Decimal

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


def ensure_mysql_innodb_session(apps, schema_editor):
    """Force new Phase39 tables to use InnoDB on hosts whose server default is MyISAM."""
    if schema_editor.connection.vendor != "mysql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SET SESSION default_storage_engine=InnoDB")


def set_default_vat(apps, schema_editor):
    PricingSetting = apps.get_model("store", "PricingSetting")
    PricingSetting.objects.filter(tax_percent=0).update(tax_percent=Decimal("10.00"), vat_enabled=True)


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0018_phase38_operator_notifications"),
        ("store", "0025_phase35_catalog_editor"),
    ]

    operations = [
        migrations.RunPython(ensure_mysql_innodb_session, migrations.RunPython.noop),
        migrations.AddField(
            model_name="pricingsetting", name="vat_enabled",
            field=models.BooleanField(default=True, verbose_name="اعمال مالیات ارزش افزوده"),
        ),
        migrations.AddField(
            model_name="pricingsetting", name="assembly_hourly_rate",
            field=models.PositiveIntegerField(default=100000, verbose_name="نرخ ساعتی مونتاژ"),
        ),
        migrations.AddField(
            model_name="pricingsetting", name="default_margin_percent",
            field=models.DecimalField(decimal_places=2, default=Decimal("30.00"), max_digits=6, verbose_name="حاشیه سود هدف درصدی"),
        ),
        migrations.AlterField(
            model_name="pricingsetting", name="tax_percent",
            field=models.DecimalField(decimal_places=2, default=Decimal("10.00"), max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name="درصد مالیات"),
        ),
        migrations.AddField(model_name="product", name="editorial_source_url", field=models.URLField(blank=True, verbose_name="لینک منبع محتوا")),
        migrations.AddField(model_name="product", name="source_attribution", field=models.CharField(blank=True, max_length=220, verbose_name="اعتبار/منبع")),
        migrations.AddField(model_name="product", name="hashtags", field=models.TextField(blank=True, verbose_name="هشتگ‌ها")),
        migrations.AddField(model_name="product", name="material_selection_intro", field=models.TextField(blank=True, verbose_name="راهنمای انتخاب متریال")),
        migrations.AddField(model_name="product", name="show_public_order_count", field=models.BooleanField(default=False, verbose_name="نمایش تعداد سفارش به مشتری")),
        migrations.AddField(model_name="product", name="customer_gallery_enabled", field=models.BooleanField(default=True, verbose_name="نمایش تصاویر مشتریان")),
        migrations.CreateModel(
            name="MaterialColorOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="نام رنگ")),
                ("code", models.SlugField(max_length=120, verbose_name="کد رنگ")),
                ("hex_code", models.CharField(blank=True, max_length=20, verbose_name="کد HEX")),
                ("sale_price_per_gram_override", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="قیمت فروش اختصاصی هر گرم")),
                ("low_stock_threshold_grams", models.DecimalField(decimal_places=2, default=100, max_digits=12, verbose_name="هشدار موجودی رنگ به گرم")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                ("material", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="store_color_options", to="website.material", verbose_name="متریال")),
            ],
            options={"verbose_name": "رنگ قابل فروش متریال", "verbose_name_plural": "رنگ‌های قابل فروش متریال", "ordering": ["material", "sort_order", "name"]},
        ),
        migrations.AddConstraint(model_name="materialcoloroption", constraint=models.UniqueConstraint(fields=("material", "code"), name="uniq_material_color_code")),
        migrations.AddField(model_name="productvariant", name="material_price_per_gram_override", field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="قیمت اختصاصی هر گرم")),
        migrations.AddField(model_name="productvariant", name="color_price_adjustment", field=models.BigIntegerField(default=0, verbose_name="تعدیل قیمت رنگ")),
        migrations.AddField(model_name="productvariant", name="assembly_fee_override", field=models.PositiveBigIntegerField(blank=True, null=True, verbose_name="هزینه مونتاژ اختصاصی")),
        migrations.AddField(model_name="productvariant", name="cached_cost_price", field=models.PositiveBigIntegerField(default=0, editable=False, verbose_name="بهای تمام‌شده تخمینی")),
        migrations.CreateModel(
            name="ProductMaterialRecommendation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("recommendation", models.CharField(choices=[("best", "پیشنهاد اصلی"), ("recommended", "پیشنهادی"), ("allowed", "قابل استفاده"), ("not_recommended", "توصیه نمی‌شود")], db_index=True, default="recommended", max_length=30, verbose_name="سطح پیشنهاد")),
                ("suitability_score", models.PositiveSmallIntegerField(default=70, verbose_name="امتیاز تناسب از ۱۰۰")),
                ("reason", models.TextField(blank=True, verbose_name="دلیل و تفاوت متریال")),
                ("customer_note", models.TextField(blank=True, verbose_name="توضیح برای مشتری")),
                ("is_customer_selectable", models.BooleanField(db_index=True, default=True, verbose_name="قابل انتخاب توسط مشتری")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                ("material", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="recommended_products", to="website.material", verbose_name="متریال")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="material_options", to="store.product", verbose_name="محصول")),
            ],
            options={"verbose_name": "پیشنهاد متریال محصول", "verbose_name_plural": "پیشنهادهای متریال محصول", "ordering": ["sort_order", "-suitability_score", "material__sort_order"]},
        ),
        migrations.AddConstraint(model_name="productmaterialrecommendation", constraint=models.UniqueConstraint(fields=("product", "material"), name="uniq_product_material_recommendation")),
        migrations.CreateModel(
            name="AccessoryComponent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160, verbose_name="نام قطعه جانبی")),
                ("sku", models.CharField(max_length=80, unique=True, verbose_name="کد داخلی")),
                ("unit_cost", models.PositiveBigIntegerField(default=0, verbose_name="قیمت خرید واحد")),
                ("default_sale_price", models.PositiveBigIntegerField(default=0, verbose_name="قیمت فروش واحد")),
                ("weight_grams", models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="وزن واحد")),
                ("stock_quantity", models.PositiveIntegerField(default=0, verbose_name="موجودی")),
                ("low_stock_threshold", models.PositiveIntegerField(default=2, verbose_name="هشدار موجودی")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
            ],
            options={"verbose_name": "قطعه جانبی / BOM", "verbose_name_plural": "قطعات جانبی / BOM", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="ProductBOMItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.DecimalField(decimal_places=2, default=1, max_digits=10, verbose_name="تعداد")),
                ("sale_price_override", models.PositiveBigIntegerField(blank=True, null=True, verbose_name="قیمت فروش اختصاصی")),
                ("assembly_minutes", models.PositiveIntegerField(default=0, verbose_name="زمان مونتاژ به دقیقه")),
                ("is_required", models.BooleanField(default=True, verbose_name="اجباری")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                ("component", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="product_usages", to="store.accessorycomponent", verbose_name="قطعه جانبی")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bom_items", to="store.product", verbose_name="محصول")),
            ],
            options={"verbose_name": "ردیف BOM محصول", "verbose_name_plural": "BOM و لوازم جانبی محصولات", "ordering": ["sort_order", "id"]},
        ),
        migrations.AddConstraint(model_name="productbomitem", constraint=models.UniqueConstraint(fields=("product", "component"), name="uniq_product_bom_component")),
        migrations.CreateModel(
            name="ProductPromotion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("featured", "محصول ویژه"), ("sale", "فروش ویژه"), ("limited", "تعداد محدود"), ("new", "محصول جدید"), ("bestseller", "پرفروش")], db_index=True, max_length=30, verbose_name="نوع")),
                ("title", models.CharField(blank=True, max_length=120, verbose_name="عنوان نمایشی")),
                ("discount_percent", models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name="درصد تخفیف")),
                ("discount_amount", models.PositiveBigIntegerField(default=0, verbose_name="تخفیف ثابت تومان")),
                ("stock_limit", models.PositiveIntegerField(default=0, verbose_name="تعداد محدود / صفر یعنی نامحدود")),
                ("starts_at", models.DateTimeField(blank=True, null=True, verbose_name="شروع")),
                ("ends_at", models.DateTimeField(blank=True, null=True, verbose_name="پایان")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="promotions", to="store.product", verbose_name="محصول")),
            ],
            options={"verbose_name": "کمپین محصول", "verbose_name_plural": "فروش ویژه و کمپین محصولات", "ordering": ["-is_active", "-created_at"]},
        ),
        migrations.CreateModel(
            name="ProductReviewImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="store/reviews/%Y/%m/", verbose_name="تصویر مشتری")),
                ("alt_text", models.CharField(blank=True, max_length=220, verbose_name="Alt تصویر")),
                ("is_approved", models.BooleanField(db_index=True, default=False, verbose_name="تأیید شده")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("review", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="store.productreview", verbose_name="نظر")),
            ],
            options={"verbose_name": "تصویر نظر مشتری", "verbose_name_plural": "تصاویر نظرات مشتریان", "ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="ShippingRateRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120, verbose_name="عنوان قانون")),
                ("min_weight_grams", models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name="حداقل وزن")),
                ("max_weight_grams", models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name="حداکثر وزن / صفر یعنی نامحدود")),
                ("base_fee", models.PositiveBigIntegerField(default=0, verbose_name="هزینه پایه")),
                ("per_kg_fee", models.PositiveBigIntegerField(default=0, verbose_name="هزینه هر کیلو")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                ("shipping_method", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rate_rules", to="store.shippingmethod", verbose_name="روش ارسال")),
            ],
            options={"verbose_name": "قانون وزنی ارسال", "verbose_name_plural": "قوانین وزنی ارسال", "ordering": ["sort_order", "min_weight_grams"]},
        ),
        migrations.AddField(model_name="storeorderitem", name="color_name", field=models.CharField(blank=True, max_length=100, verbose_name="رنگ هنگام سفارش")),
        migrations.AddField(model_name="storeorderitem", name="unit_cost_snapshot", field=models.PositiveBigIntegerField(default=0, verbose_name="بهای تمام‌شده واحد")),
        migrations.AddField(model_name="storeorderitem", name="gross_profit", field=models.BigIntegerField(default=0, verbose_name="سود ناخالص ردیف")),
        migrations.AddField(model_name="storeorderitem", name="material_charge_snapshot", field=models.PositiveBigIntegerField(default=0, verbose_name="هزینه فروش متریال")),
        migrations.AddField(model_name="storeorderitem", name="machine_charge_snapshot", field=models.PositiveBigIntegerField(default=0, verbose_name="هزینه زمان دستگاه")),
        migrations.AddField(model_name="storeorderitem", name="labor_charge_snapshot", field=models.PositiveBigIntegerField(default=0, verbose_name="دستمزد ساخت")),
        migrations.AddField(model_name="storeorderitem", name="accessory_charge_snapshot", field=models.PositiveBigIntegerField(default=0, verbose_name="لوازم جانبی")),
        migrations.AddField(model_name="storeorderitem", name="assembly_charge_snapshot", field=models.PositiveBigIntegerField(default=0, verbose_name="مونتاژ")),
        migrations.AddField(model_name="storeorderitem", name="color_adjustment_snapshot", field=models.BigIntegerField(default=0, verbose_name="تعدیل قیمت رنگ")),
        migrations.RunPython(set_default_vat, migrations.RunPython.noop),
    ]
