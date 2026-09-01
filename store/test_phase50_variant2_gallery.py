from decimal import Decimal
from pathlib import Path

from django.contrib import admin
from django.test import SimpleTestCase
from django.urls import resolve, reverse

from .models import ProductVariant, StoreOrderItem
from .phase50_variant_views import variant_commerce_options_view


class Phase50Variant2GalleryContractTests(SimpleTestCase):
    def test_variant2_fields_and_constraint_are_in_runtime_state(self):
        for name in (
            "size_label",
            "build_profile",
            "packaging_weight_grams",
            "package_length_cm",
            "package_width_cm",
            "package_height_cm",
        ):
            self.assertIsNotNone(ProductVariant._meta.get_field(name))

        for name in (
            "size_label",
            "build_profile",
            "packaging_weight_grams",
            "package_length_cm",
            "package_width_cm",
            "package_height_cm",
        ):
            self.assertIsNotNone(StoreOrderItem._meta.get_field(name))

        names = {constraint.name for constraint in ProductVariant._meta.constraints}
        self.assertIn("uniq_product_material_quality_color_size_build_profile", names)
        self.assertNotIn("uniq_product_material_quality_color", names)

    def test_effective_shipping_weight_includes_packaging_without_manual_override(self):
        variant = ProductVariant(
            material_weight_grams=Decimal("120"),
            final_weight_grams=Decimal("125"),
            shipping_weight_grams=Decimal("0"),
            packaging_weight_grams=Decimal("35"),
        )
        self.assertEqual(variant.effective_shipping_weight_grams, Decimal("160"))
        variant.shipping_weight_grams = Decimal("210")
        self.assertEqual(variant.effective_shipping_weight_grams, Decimal("210"))

    def test_variant_metadata_endpoint_is_stable_and_public(self):
        path = reverse("store:variant_commerce_options")
        self.assertEqual(path, "/store/api/variant-commerce-options/")
        self.assertIs(resolve(path).func, variant_commerce_options_view)

    def test_admin_exposes_variant_commerce_fields(self):
        variant_admin = admin.site._registry.get(ProductVariant)
        self.assertIsNotNone(variant_admin)
        self.assertIn("size_label", variant_admin.list_display)
        self.assertIn("build_profile", variant_admin.list_display)
        self.assertIn("packaging_weight_grams", variant_admin.list_display)

    def test_gallery_assets_require_contain_fit_lightbox_and_thumbnail_swap(self):
        root = Path(__file__).resolve().parents[1]
        js = (root / "static" / "store" / "js" / "store.js").read_text(encoding="utf-8")
        css = (root / "static" / "store" / "css" / "store.css").read_text(encoding="utf-8")
        self.assertIn("installProductGallery", js)
        self.assertIn("store-lightbox", js)
        self.assertIn("store-gallery-thumb-active", js)
        self.assertIn("/store/api/variant-commerce-options/", js)
        self.assertIn("object-fit:contain!important", css)

    def test_storefront_profile_selector_uses_existing_variant_contract(self):
        root = Path(__file__).resolve().parents[1]
        selector_js = (root / "static" / "store" / "js" / "phase50-profile-selector.js").read_text(encoding="utf-8")
        selector_css = (root / "static" / "store" / "css" / "phase50-profile-selector.css").read_text(encoding="utf-8")
        base = (root / "templates" / "store" / "base.html").read_text(encoding="utf-8")

        for marker in (
            "MODE_DIMENSIONS",
            "installSelector",
            "store-profile-option",
            "/store/api/variant-commerce-options/",
            'select.dispatchEvent(new Event("change"',
        ):
            self.assertIn(marker, selector_js)

        for marker in (
            "store-profile-selector",
            "store-profile-summary__price",
            "store-profile-native-fallback",
        ):
            self.assertIn(marker, selector_css)

        self.assertIn("store/css/phase50-profile-selector.css", base)
        self.assertIn("store/js/phase50-profile-selector.js", base)

    def test_product_detail_progressively_enhances_information_tabs_without_replacing_seo(self):
        root = Path(__file__).resolve().parents[1]
        template = (
            root / "templates" / "store" / "product_detail.html"
        ).read_text(encoding="utf-8")
        css = (
            root / "static" / "store" / "css" / "phase49-product-info-tabs.css"
        ).read_text(encoding="utf-8")
        js = (
            root / "static" / "store" / "js" / "phase49-product-info-tabs.js"
        ).read_text(encoding="utf-8")

        for marker in (
            "data-product-info-tabs",
            'data-product-info-tab="overview"',
            'data-product-info-tab="faq"',
            'data-product-info-tab="reviews"',
            'data-product-info-panel="overview"',
            'data-product-info-panel="faq"',
            'data-product-info-panel="reviews"',
            "store/css/phase49-product-info-tabs.css",
            "store/js/phase49-product-info-tabs.js",
            "product_schema_json",
            "product_faq_schema_json",
            "{% block canonical %}",
            "{% block robots %}",
        ):
            self.assertIn(marker, template)

        for marker in (
            ".phase49-product-info__tabs",
            ".phase49-product-info__tab[aria-selected",
            ".phase49-product-info.is-enhanced",
            "prefers-reduced-motion",
        ):
            self.assertIn(marker, css)

        for marker in (
            "initProductInfoTabs",
            'root.classList.add("is-enhanced")',
            "aria-selected",
            "ArrowLeft",
            "ArrowRight",
            "history.replaceState",
        ):
            self.assertIn(marker, js)
