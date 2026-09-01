from django.contrib import admin
from django.test import SimpleTestCase

from store.models import PricingSetting, Product, ProductImage, ProductVariant
from store.phase39_models import MaterialColorOption
from website.models import Quote, SiteSetting
from store.phase50_product_admin_workspace import SECTION_TITLES


class Phase50ProductAdminWorkspaceTests(SimpleTestCase):
    def setUp(self):
        self.product_admin = admin.site._registry[Product]

    def test_product_admin_uses_requested_business_section_order(self):
        titles = tuple(title for title, _options in self.product_admin.fieldsets)
        self.assertEqual(titles, SECTION_TITLES)

    def test_core_product_and_seo_fields_remain_editable(self):
        fields = []
        for _title, options in self.product_admin.fieldsets:
            fields.extend(options.get("fields", ()))

        for name in (
            "category",
            "title",
            "main_image",
            "order_mode",
            "fixed_price",
            "sales_profile_selection_mode",
            "seo_focus_keyword",
            "meta_title",
            "meta_description",
            "canonical_url",
            "robots_index",
            "robots_follow",
            "schema_enabled",
            "og_title",
            "og_description",
            "og_image",
            "source_url",
            "source_name",
            "source_external_id",
        ):
            self.assertIn(name, fields)

    def test_operator_control_readonly_blocks_are_exposed(self):
        readonly = set(self.product_admin.readonly_fields)
        for name in (
            "phase50_gallery_admin",
            "phase50_sales_profiles_admin",
            "phase50_pricing_admin",
            "phase50_shipping_admin",
            "phase50_slider_admin",
            "phase50_license_admin",
            "phase50_windows_sync_admin",
            "seo_preview",
        ):
            self.assertIn(name, readonly)
            self.assertTrue(hasattr(self.product_admin, name))

    def test_mature_product_inlines_are_preserved_and_relabeled(self):
        by_model = {inline.model: inline for inline in self.product_admin.inlines}
        self.assertIn(ProductImage, by_model)
        self.assertIn(ProductVariant, by_model)

        image_inline = by_model[ProductImage]
        variant_inline = by_model[ProductVariant]

        self.assertEqual(image_inline.verbose_name_plural, "تصاویر و گالری محصول")
        self.assertEqual(variant_inline.verbose_name_plural, "پروفایل‌ها، سایز، وزن، قیمت و موجودی")

        for field in (
            "sales_profile_name",
            "sales_profile_key",
            "sales_profile_is_default",
            "sales_profile_sort_order",
            "size_label",
            "build_profile",
            "material",
            "quality",
            "color",
            "material_weight_grams",
            "final_weight_grams",
            "packaging_weight_grams",
            "shipping_weight_grams",
            "package_length_cm",
            "package_width_cm",
            "package_height_cm",
            "print_time_minutes",
            "cached_unit_price",
            "stock_status",
            "stock_quantity",
            "is_active",
        ):
            self.assertIn(field, variant_inline.fields)

    def test_existing_product_admin_operational_contracts_survive(self):
        self.assertIn("is_featured", self.product_admin.list_editable)
        self.assertIn("is_active", self.product_admin.list_editable)
        self.assertIn("sales_profile_selection_mode", self.product_admin.list_filter)
        self.assertIn("minimum_price", self.product_admin.list_display)
        self.assertIn("price_is_final", self.product_admin.list_display)
        self.assertIn("seo_preview", self.product_admin.readonly_fields)

    def test_tabbed_change_form_media_is_shared_across_business_admins(self):
        for model in (
            Product,
            PricingSetting,
            MaterialColorOption,
            SiteSetting,
            Quote,
        ):
            with self.subTest(model=model.__name__):
                registered = admin.site._registry[model]
                media = registered.media
                css = {
                    value
                    for values in media._css.values()
                    for value in values
                }
                js = set(media._js)
                self.assertIn("admin/phase49-admin-tabs.css", css)
                self.assertIn("admin/phase49-admin-tabs.js", js)

    def test_pricing_and_color_admins_use_task_focused_fieldsets(self):
        pricing = admin.site._registry[PricingSetting]
        self.assertEqual(
            tuple(title for title, _options in pricing.fieldsets),
            (
                "زمان و نرخ تولید",
                "دستمزد و حاشیه سود",
                "حداقل سفارش و بسته‌بندی",
                "مالیات",
                "وضعیت",
            ),
        )
        pricing_fields = {
            field
            for _title, options in pricing.fieldsets
            for field in options.get("fields", ())
        }
        self.assertTrue(
            {
                "default_hourly_rate",
                "assembly_hourly_rate",
                "default_labor_percent",
                "default_margin_percent",
                "minimum_order_amount",
                "packaging_fee",
                "vat_enabled",
                "tax_percent",
            }.issubset(pricing_fields)
        )

        colors = admin.site._registry[MaterialColorOption]
        self.assertEqual(
            tuple(title for title, _options in colors.fieldsets),
            (
                "هویت Filament",
                "رنگ، Finish و تصویر",
                "موجودی و قیمت رول",
                "هزینه‌های تولید و پیش‌گرم",
            ),
        )
        color_fields = {
            field
            for _title, options in colors.fieldsets
            for field in options.get("fields", ())
        }
        for name in (
            "brand_name",
            "color_type",
            "color_finish",
            "palette_hexes",
            "filament_image",
            "roll_weight_grams",
            "stock_roll_count_snapshot",
            "purchase_price_per_roll",
            "sale_price_per_roll",
            "low_stock_threshold_grams",
            "print_hourly_rate",
            "supervision_hourly_rate",
            "preheat_hours",
        ):
            self.assertIn(name, color_fields)
        self.assertNotIn("manufacturer_name", color_fields)
        self.assertNotIn("sale_price_per_gram_override", color_fields)
        self.assertIn("effective_price", colors.readonly_fields)
        self.assertIn("filament_preview", colors.readonly_fields)
