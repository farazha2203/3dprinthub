from django.contrib import admin
from django.test import SimpleTestCase

from store.models import Product, ProductImage, ProductVariant
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
        self.assertIn("seo_status", self.product_admin.list_display)
