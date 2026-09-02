from django.db import migrations, models


class AddFieldIfMissing(migrations.AddField):
    """Add a field unless a previous non-transactional DDL attempt already did."""

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        to_model = to_state.apps.get_model(app_label, self.model_name)
        field = to_model._meta.get_field(self.name)
        table = to_model._meta.db_table

        with schema_editor.connection.cursor() as cursor:
            table_names = set(schema_editor.connection.introspection.table_names(cursor))
            if table in table_names:
                description = schema_editor.connection.introspection.get_table_description(
                    cursor,
                    table,
                )
                columns = {str(column.name) for column in description}
                if str(field.column) in columns:
                    return

        return super().database_forwards(
            app_label,
            schema_editor,
            from_state,
            to_state,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0038_phase50_profile_matrix"),
    ]

    operations = [
        AddFieldIfMissing(
            model_name="materialcoloroption",
            name="brand_name",
            field=models.CharField(
                blank=True,
                default="",
                max_length=120,
                verbose_name="برند فیلامنت",
            ),
        ),
        AddFieldIfMissing(
            model_name="materialcoloroption",
            name="manufacturer_name",
            field=models.CharField(
                blank=True,
                default="",
                max_length=160,
                verbose_name="کارخانه / سازنده فیلامنت",
            ),
        ),
        AddFieldIfMissing(
            model_name="materialcoloroption",
            name="roll_weight_grams",
            field=models.DecimalField(
                decimal_places=2,
                default=1000,
                max_digits=10,
                verbose_name="وزن هر رول به گرم",
            ),
        ),
        AddFieldIfMissing(
            model_name="materialcoloroption",
            name="stock_roll_count_snapshot",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name="اسنپ‌شات تعداد رول موجود",
            ),
        ),
        AddFieldIfMissing(
            model_name="materialcoloroption",
            name="purchase_price_per_roll",
            field=models.PositiveBigIntegerField(
                default=0,
                verbose_name="قیمت خرید هر رول",
            ),
        ),
        AddFieldIfMissing(
            model_name="materialcoloroption",
            name="sale_price_per_roll",
            field=models.PositiveBigIntegerField(
                default=0,
                verbose_name="قیمت فروش هر رول",
            ),
        ),
        AddFieldIfMissing(
            model_name="materialcoloroption",
            name="usd_price_per_roll",
            field=models.DecimalField(
                decimal_places=4,
                default=0,
                max_digits=14,
                verbose_name="قیمت دلاری هر رول",
            ),
        ),
        AddFieldIfMissing(
            model_name="materialcoloroption",
            name="usd_fx_rate_toman",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=14,
                verbose_name="نرخ دلار ثبت‌شده برای این رول",
            ),
        ),
        # ProductVariant.support_weight_grams already exists in migration 0033.
        # 0039 only aligns its state metadata with the current runtime contract.
        migrations.AlterField(
            model_name="productvariant",
            name="support_weight_grams",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name="وزن ساپورت مصرفی",
            ),
        ),
        AddFieldIfMissing(
            model_name="storeorderitem",
            name="support_weight_grams",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name="وزن ساپورت هنگام سفارش",
            ),
        ),
        AddFieldIfMissing(
            model_name="storeorderitem",
            name="filament_brand_name",
            field=models.CharField(
                blank=True,
                default="",
                max_length=120,
                verbose_name="برند فیلامنت هنگام سفارش",
            ),
        ),
        AddFieldIfMissing(
            model_name="storeorderitem",
            name="filament_manufacturer_name",
            field=models.CharField(
                blank=True,
                default="",
                max_length=160,
                verbose_name="سازنده فیلامنت هنگام سفارش",
            ),
        ),
    ]
