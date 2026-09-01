from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from website.models import Material

from .models import Category, PrintQuality, Product, ProductVariant, StoreOrderItem
from .phase50_profile_matrix import PROFILE_SELECTION_CHOICES, sync_desktop_profile_matrix


class Phase50ProfileMatrixTests(TestCase):
    def setUp(self):
        self.material = Material.objects.create(
            name="PLA PROFILE MATRIX",
            price_per_kg=1_000_000,
            strength=3,
            heat_resistance=2,
            flexibility=1,
            chemical_resistance=2,
            printability=5,
            main_usage="test",
            sample_parts="test",
        )
        self.quality = PrintQuality.objects.create(
            code="profile-matrix-quality",
            name="کیفیت پروفایل",
        )
        self.category = Category.objects.create(
            name="پروفایل ماتریسی",
            slug="profile-matrix",
            section="creative",
        )
        self.product = Product.objects.create(
            category=self.category,
            title="پایه کیک پروفایلی",
            slug="cake-stand-profile-matrix",
            sku="PROFILE-MATRIX-001",
            short_description="پایه کیک با چند سایز و وزن",
            description="محصول تست پروفایل",
            main_image="store/products/profile-matrix.webp",
            is_active=True,
        )
        self.manual_variant = ProductVariant.objects.create(
            product=self.product,
            material=self.material,
            quality=self.quality,
            code="MANUAL-PRESERVE",
            material_weight_grams=Decimal("90"),
            final_weight_grams=Decimal("100"),
            shipping_weight_grams=Decimal("0"),
            print_time_minutes=60,
            size_label="دستی",
            sales_profile_key="manual-profile",
            sales_profile_name="پروفایل دستی",
            is_active=True,
        )

    def _asset(self, profiles, mode="size_weight"):
        return SimpleNamespace(
            source_payload={
                "desktop_catalog_v85": {
                    "sales_profile_selection_mode": mode,
                    "sales_profile_selector_label": "ابتدا سایز، سپس وزن را انتخاب کنید",
                    "sales_profiles_json": json.dumps(profiles, ensure_ascii=False),
                }
            }
        )

    def _profiles(self):
        return [
            {
                "key": "20-100",
                "name": "۲۰ سانتی - ۱۰۰ گرم",
                "description": "اقتصادی و سبک",
                "size_label": "20 سانتی‌متر",
                "weight_grams": 100,
                "material_weight_grams": 100,
                "print_time_minutes": 90,
                "fixed_price": 350000,
                "part_length_cm": 20,
                "part_width_cm": 20,
                "part_height_cm": 8,
                "build_profile": "hollow",
                "is_default": True,
                "sort_order": 10,
            },
            {
                "key": "20-150",
                "name": "۲۰ سانتی - ۱۵۰ گرم",
                "description": "تعادل وزن و استحکام",
                "size_label": "20 سانتی‌متر",
                "weight_grams": 150,
                "material_weight_grams": 150,
                "print_time_minutes": 120,
                "fixed_price": 450000,
                "part_length_cm": 20,
                "part_width_cm": 20,
                "part_height_cm": 8,
                "build_profile": "standard",
                "sort_order": 20,
            },
            {
                "key": "30-200",
                "name": "۳۰ سانتی - ۲۰۰ گرم",
                "description": "سایز بزرگ و سبک",
                "size_label": "30 سانتی‌متر",
                "weight_grams": 200,
                "material_weight_grams": 200,
                "print_time_minutes": 150,
                "fixed_price": 650000,
                "part_length_cm": 30,
                "part_width_cm": 30,
                "part_height_cm": 10,
                "build_profile": "standard",
                "sort_order": 30,
            },
            {
                "key": "30-300",
                "name": "۳۰ سانتی - ۳۰۰ گرم",
                "description": "نسخه سنگین‌تر",
                "size_label": "30 سانتی‌متر",
                "weight_grams": 300,
                "material_weight_grams": 300,
                "print_time_minutes": 210,
                "fixed_price": 850000,
                "part_length_cm": 30,
                "part_width_cm": 30,
                "part_height_cm": 10,
                "build_profile": "reinforced",
                "sort_order": 40,
            },
        ]

    def test_runtime_fields_and_new_selection_modes_exist(self):
        choice_codes = {code for code, _label in PROFILE_SELECTION_CHOICES}
        for mode in ("size_weight", "weight_size", "size_weight_build", "size_build_weight"):
            self.assertIn(mode, choice_codes)
        for model, fields in (
            (
                ProductVariant,
                (
                    "sales_profile_description",
                    "part_length_cm",
                    "part_width_cm",
                    "part_height_cm",
                ),
            ),
            (
                StoreOrderItem,
                ("part_length_cm", "part_width_cm", "part_height_cm"),
            ),
        ):
            for field in fields:
                self.assertIsNotNone(model._meta.get_field(field))

    def test_desktop_matrix_becomes_real_orderable_variants(self):
        count = sync_desktop_profile_matrix(self.product, self._asset(self._profiles()))
        self.assertEqual(count, 4)

        self.product.refresh_from_db()
        self.assertEqual(self.product.order_mode, "variant")
        self.assertEqual(self.product.sales_profile_selection_mode, "size_weight")
        self.assertEqual(self.product.pricing_policy, "profile_fixed")
        self.assertEqual(self.product.fixed_price, 0)
        self.assertTrue(self.product.price_is_final)

        profiles = list(
            self.product.variants.filter(code__startswith=f"CC-P{self.product.pk}-")
            .order_by("sales_profile_sort_order")
        )
        self.assertEqual(len(profiles), 4)
        self.assertEqual(
            [(item.size_label, item.final_weight_grams, item.fixed_price_override) for item in profiles],
            [
                ("20 سانتی‌متر", Decimal("100.00"), 350000),
                ("20 سانتی‌متر", Decimal("150.00"), 450000),
                ("30 سانتی‌متر", Decimal("200.00"), 650000),
                ("30 سانتی‌متر", Decimal("300.00"), 850000),
            ],
        )
        self.assertEqual(sum(1 for item in profiles if item.sales_profile_is_default), 1)
        self.assertEqual(profiles[0].part_dimensions_label, "20 × 20 × 8 سانتی‌متر")

        self.manual_variant.refresh_from_db()
        self.assertTrue(self.manual_variant.is_active)

    def test_republish_updates_existing_profiles_and_deactivates_only_removed_desktop_rows(self):
        sync_desktop_profile_matrix(self.product, self._asset(self._profiles()))
        original = self.product.variants.get(sales_profile_key="20-150")
        original_pk = original.pk

        reduced = self._profiles()[:2]
        reduced[1]["fixed_price"] = 475000
        reduced[1]["weight_grams"] = 155
        sync_desktop_profile_matrix(self.product, self._asset(reduced))

        updated = self.product.variants.get(sales_profile_key="20-150")
        self.assertEqual(updated.pk, original_pk)
        self.assertEqual(updated.fixed_price_override, 475000)
        self.assertEqual(updated.final_weight_grams, Decimal("155.00"))
        self.assertFalse(self.product.variants.get(sales_profile_key="30-200").is_active)
        self.assertFalse(self.product.variants.get(sales_profile_key="30-300").is_active)
        self.manual_variant.refresh_from_db()
        self.assertTrue(self.manual_variant.is_active)

    def test_invalid_stock_status_is_rejected_without_silent_mapping(self):
        rows = self._profiles()[:1]
        rows[0]["stock_status"] = "invented-state"
        with self.assertRaises(ValidationError):
            sync_desktop_profile_matrix(self.product, self._asset(rows))

    def test_variant_api_returns_profile_price_weight_description_and_part_dimensions(self):
        sync_desktop_profile_matrix(self.product, self._asset(self._profiles()))
        variant = self.product.variants.get(sales_profile_key="30-300")
        response = self.client.get(
            reverse("store:variant_commerce_options"),
            {"ids": str(variant.pk)},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        product_meta = payload["products"][str(self.product.pk)]
        meta = payload["variants"][str(variant.pk)]
        self.assertEqual(product_meta["selection_mode"], "size_weight")
        self.assertEqual(meta["profile_description"], "نسخه سنگین‌تر")
        self.assertEqual(meta["final_weight_grams"], "300.00")
        self.assertEqual(meta["unit_price"], 850000)
        self.assertEqual(meta["part_dimensions_label"], "30 × 30 × 10 سانتی‌متر")

    def test_brand_aware_filament_offer_sync_support_weight_and_api(self):
        rows = self._profiles()[:1]
        rows[0].update({
            "fixed_price": 0,
            "material": self.material.name,
            "brand": "Bambu Lab",
            "manufacturer": "Bambu Lab",
            "color": "سفید مات",
            "support_weight_grams": 20,
            "roll_weight_grams": 1000,
            "stock_roll_count": 1,
            "purchase_price_per_roll": 2_500_000,
            "sale_price_per_roll": 3_600_000,
            "usd_price_per_roll": 30,
            "usd_fx_rate_toman": 130_000,
        })
        sync_desktop_profile_matrix(self.product, self._asset(rows))
        variant = self.product.variants.get(sales_profile_key="20-100")
        self.assertEqual(variant.support_weight_grams, Decimal("20.00"))
        self.assertIsNotNone(variant.color)
        self.assertEqual(variant.color.brand_name, "Bambu Lab")
        self.assertEqual(variant.color.manufacturer_name, "Bambu Lab")
        self.assertEqual(variant.color.sale_price_per_roll, 3_600_000)
        self.assertEqual(variant.color.effective_sale_price_per_gram, Decimal("3600"))

        response = self.client.get(
            reverse("store:variant_commerce_options"),
            {"ids": str(variant.pk)},
        )
        self.assertEqual(response.status_code, 200)
        meta = response.json()["variants"][str(variant.pk)]
        self.assertEqual(meta["filament_brand_name"], "Bambu Lab")
        self.assertEqual(meta["filament_manufacturer_name"], "Bambu Lab")
        self.assertEqual(meta["support_weight_grams"], "20.00")

    def test_storefront_marks_profile_as_single_price_authority(self):
        root = Path(__file__).resolve().parents[1]
        template = (root / "templates" / "store" / "product_detail.html").read_text(encoding="utf-8")
        js = (root / "static" / "store" / "js" / "phase50-profile-selector.js").read_text(encoding="utf-8")
        css = (root / "static" / "store" / "css" / "phase50-profile-selector.css").read_text(encoding="utf-8")

        self.assertIn("{% if not variants %}", template)
        self.assertIn("قیمت و مشخصات بر اساس پروفایل انتخابی", template)
        self.assertIn("انتخاب پروفایل و مشخصات سفارش", template)
        for marker in (
            'size_weight: ["size", "weight"]',
            "profileDescription",
            "partDimensionsLabel",
            "filamentBrand",
            "supportWeight",
            "store-profile-option__price",
            "escapeHtml",
        ):
            self.assertIn(marker, js)
        self.assertIn(".store-profile-price-authority", css)
        self.assertIn("background: #0b2238", css)
        self.assertIn("#c99a2e", css)
