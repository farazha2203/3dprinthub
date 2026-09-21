from __future__ import annotations

import base64
import json
import tempfile
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from django.test import RequestFactory, TestCase, override_settings
from PIL import Image

from catalog_bridge.unified_views import filament_sync_view
from django.urls import reverse

from website.models import Material

from .epic49_catalog_profile import ProductCatalogProfile
from .models import Category, PrintQuality, Product, ProductVariant
from .phase39_models import MaterialColorOption
from .phase50_profile_matrix import sync_desktop_profile_matrix


class Phase50FilamentOfferOperationsTests(TestCase):
    def setUp(self):
        self.bridge_token = "phase50-filament-visual-test-token-1234567890"
        self._media = tempfile.TemporaryDirectory()
        self._override = override_settings(
            MEDIA_ROOT=self._media.name,
            CATALOG_BRIDGE_TOKEN=self.bridge_token,
        )
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(self._media.cleanup)
        self.factory = RequestFactory()

        self.material = Material.objects.create(
            name="PLA OFFER OPS",
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
            code="offer-ops-quality",
            name="کیفیت Offer",
        )
        self.category = Category.objects.create(
            name="Offer Operations",
            slug="offer-operations",
            section="creative",
        )
        self.product = Product.objects.create(
            category=self.category,
            title="محصول Offer",
            slug="filament-offer-ops",
            sku="OFFER-OPS-001",
            short_description="تست Offer",
            description="تست",
            main_image="store/products/offer-ops.webp",
            is_active=True,
        )

    def _asset(self, rows):
        return SimpleNamespace(
            source_payload={
                "desktop_catalog_v85": {
                    "sales_profile_selection_mode": "size_weight",
                    "sales_profile_selector_label": "سایز، سپس سازنده/فیلامنت/رنگ",
                    "sales_profiles_json": json.dumps(rows, ensure_ascii=False),
                }
            }
        )

    def test_runtime_0041_filament_visual_fields_exist(self):
        for name in (
            "print_hourly_rate",
            "supervision_hourly_rate",
            "preheat_hours",
            "preheat_temperature_c",
            "preheat_hourly_rate",
            "filament_image_url",
            "color_finish",
            "palette_hexes",
            "filament_image",
        ):
            self.assertIsNotNone(MaterialColorOption._meta.get_field(name))

    def _webp_base64(self) -> str:
        buffer = BytesIO()
        Image.new("RGB", (40, 40), (241, 93, 156)).save(buffer, "WEBP")
        return base64.b64encode(buffer.getvalue()).decode("ascii")

    def test_bridge_sync_persists_brand_palette_finish_and_server_image(self):
        request = self.factory.post(
            "/api/catalog-bridge/v1/filaments/sync/",
            data=json.dumps(
                {
                    "operator": "desktop-test",
                    "filament": {
                        "material": self.material.name,
                        "brand": "Bambu Lab",
                        "manufacturer": "Ignored Old Company",
                        "color": "Pink Dual",
                        "color_type": "dual",
                        "color_finish": "glossy",
                        "palette_hexes": ["#F15D9C", "#7C3AED"],
                        "roll_weight_grams": 750,
                        "stock_roll_count": 2.5,
                        "purchase_price_per_roll": 2_100_000,
                        "sale_price_per_roll": 3_000_000,
                        "filament_image_base64": self._webp_base64(),
                    },
                },
                ensure_ascii=False,
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.bridge_token}",
        )
        response = filament_sync_view(request)
        self.assertEqual(response.status_code, 200, response.content)
        payload = json.loads(response.content.decode("utf-8"))
        self.assertEqual(payload["contract"], "phase49-filament-library-v3")

        color = MaterialColorOption.objects.get(
            material=self.material,
            name="Pink Dual",
            brand_name="Bambu Lab",
        )
        self.assertEqual(color.manufacturer_name, "Bambu Lab")
        self.assertEqual(color.color_type, "dual")
        self.assertEqual(color.color_finish, "glossy")
        self.assertEqual(color.palette_hexes, ["#F15D9C", "#7C3AED"])
        self.assertEqual(color.hex_code, "#F15D9C")
        self.assertEqual(color.secondary_hex, "#7C3AED")
        self.assertTrue(color.filament_image.name)
        self.assertTrue(Path(color.filament_image.path).is_file())
        self.assertEqual(color.effective_sale_price_per_gram, Decimal("4000"))

        serialized = payload["filament"]
        self.assertEqual(serialized["brand"], "Bambu Lab")
        self.assertEqual(serialized["manufacturer"], "Bambu Lab")
        self.assertEqual(serialized["color_finish"], "glossy")
        self.assertEqual(serialized["palette_hexes"], ["#F15D9C", "#7C3AED"])
        self.assertEqual(Decimal(serialized["effective_sale_price_per_gram"]), Decimal("4000"))
        self.assertTrue(serialized["filament_image_server_url"])

    def test_bridge_rejects_invalid_filament_image_payload(self):
        request = self.factory.post(
            "/api/catalog-bridge/v1/filaments/sync/",
            data=json.dumps(
                {
                    "filament": {
                        "material": self.material.name,
                        "brand": "Bambu Lab",
                        "color": "Broken",
                        "filament_image_base64": "not-valid-base64!!!",
                    }
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.bridge_token}",
        )
        response = filament_sync_view(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn("filament_image_base64", response.content.decode("utf-8"))

    def test_sale_price_per_gram_uses_only_roll_sale_divided_by_roll_weight(self):
        color = MaterialColorOption.objects.create(
            material=self.material,
            name="قیمت مرجع",
            code="owner-roll-price",
            brand_name="Owner Brand",
            manufacturer_name="Old Manufacturer",
            roll_weight_grams=Decimal("750"),
            sale_price_per_roll=3_000_000,
            usd_price_per_roll=Decimal("999"),
            usd_fx_rate_toman=Decimal("999999"),
            sale_price_per_gram_override=Decimal("999999"),
        )
        self.assertEqual(
            color.effective_sale_price_per_gram,
            Decimal("4000"),
        )

    def test_formula_uses_exact_color_offer_hourly_supervision_preheat_and_purchase_rate(self):
        color = MaterialColorOption.objects.create(
            material=self.material,
            name="سفید",
            code="white-bambu",
            hex_code="#F5F5F5",
            brand_name="Bambu Lab",
            manufacturer_name="Bambu Lab",
            roll_weight_grams=Decimal("1000"),
            stock_roll_count_snapshot=Decimal("3"),
            purchase_price_per_roll=2_500_000,
            sale_price_per_roll=3_600_000,
            print_hourly_rate=150_000,
            supervision_hourly_rate=50_000,
            preheat_hours=Decimal("24"),
            preheat_temperature_c=Decimal("70"),
            preheat_hourly_rate=30_000,
            filament_image_url="https://example.com/bambu-white.webp",
        )
        variant = ProductVariant.objects.create(
            product=self.product,
            material=self.material,
            quality=self.quality,
            color=color,
            code="OFFER-OPS-FORMULA",
            material_weight_grams=Decimal("100"),
            final_weight_grams=Decimal("100"),
            print_time_minutes=60,
            is_active=True,
        )
        breakdown = variant.price_breakdown()
        self.assertEqual(breakdown["material_cost"], 360000)
        self.assertEqual(breakdown["machine_cost"], 150000)
        self.assertEqual(breakdown["supervision_cost"], 50000)
        self.assertEqual(breakdown["preheat_cost"], 720000)
        self.assertEqual(breakdown["hourly_rate"], 150000)
        self.assertEqual(Decimal(breakdown["preheat_hours"]), Decimal("24"))
        self.assertEqual(Decimal(breakdown["preheat_temperature_c"]), Decimal("70"))
        self.assertGreaterEqual(breakdown["estimated_cost"], 1_170_000)
        self.assertEqual(color.current_stock_grams, Decimal("3000"))
        self.assertTrue(variant.color_stock_sufficient)

    def test_desktop_dynamic_profile_matches_catalog_formula_including_preheat(self):
        profile = ProductCatalogProfile.objects.create(
            product=self.product,
            public_slug="filament-offer-ops",
            pricing_strategy="dynamic",
            price_mode="variant",
            # Reproduce the real #625 failure boundary: the persisted Profile
            # still carried the pre-repair 0/70k service-rate range.
            price_min=705_000,
            price_max=825_000,
        )
        rows = [{
            "key": "spino-60-pla-white",
            "name": "60g PLA White",
            "size_label": "60g",
            "weight_grams": 60,
            "material_weight_grams": 110,
            "support_weight_grams": 50,
            "support_cost_multiplier": 1,
            "print_time_minutes": 180,
            "assembly_fee": 0,
            "part_length_cm": 10,
            "part_width_cm": 10,
            "part_height_cm": 10,
            "material": self.material.name,
            "brand": "eSUN",
            "manufacturer": "eSUN",
            "color": "سفید",
            "roll_weight_grams": 1000,
            "stock_roll_count": 1,
            "purchase_price_per_roll": 3_500_000,
            "sale_price_per_roll": 4_500_000,
            "print_hourly_rate": 150_000,
            "supervision_hourly_rate": 50_000,
            "preheat_hours": 4,
            "preheat_temperature_c": 55,
            "preheat_hourly_rate": 30_000,
            "fixed_price": 0,
            "is_default": True,
            "is_active": True,
        }, {
            "key": "spino-60-pla-bambu",
            "name": "60g PLA Bambu",
            "size_label": "60g",
            "weight_grams": 60,
            "material_weight_grams": 110,
            "support_weight_grams": 50,
            "support_cost_multiplier": 1,
            "print_time_minutes": 180,
            "assembly_fee": 0,
            "part_length_cm": 10,
            "part_width_cm": 10,
            "part_height_cm": 10,
            "material": self.material.name,
            "brand": "Bambu Lab",
            "manufacturer": "Bambu Lab",
            "color": "صورتی پاستیلی",
            "roll_weight_grams": 1000,
            "stock_roll_count": 1,
            "purchase_price_per_roll": 3_500_000,
            "sale_price_per_roll": 4_500_000,
            "print_hourly_rate": 150_000,
            "supervision_hourly_rate": 50_000,
            "preheat_hours": 0,
            "preheat_temperature_c": 0,
            "preheat_hourly_rate": 0,
            "fixed_price": 0,
            "is_active": True,
        }]
        sync_desktop_profile_matrix(self.product, self._asset(rows))
        variant = self.product.variants.get(sales_profile_key="spino-60-pla-white")
        self.assertEqual(variant.part_weight_grams, Decimal("60.00"))
        self.assertEqual(variant.support_weight_grams, Decimal("50.00"))
        self.assertEqual(variant.support_cost_multiplier, Decimal("1.00"))
        self.assertEqual(variant.hourly_rate_override, 150_000)
        self.assertEqual(variant.supervision_hourly_rate_override, 50_000)
        result = variant.price_breakdown()
        self.assertEqual(result["pricing_authority"], "desktop_sales_profile_formula_v1")
        self.assertEqual(result["material_cost"], 495_000)
        self.assertEqual(result["machine_cost"], 450_000)
        self.assertEqual(result["supervision_cost"], 150_000)
        self.assertEqual(result["preheat_cost"], 120_000)
        self.assertEqual(result["unit_price"], 1_215_000)
        self.assertEqual(Decimal(result["actual_material_grams"]), Decimal("110"))
        self.assertEqual(Decimal(result["chargeable_material_grams"]), Decimal("110"))
        self.assertEqual(result["billable_print_minutes"], 180)

        # Matrix sync itself is the final mutable-Variant boundary. It must
        # immediately replace the stale persisted Profile range using the fresh
        # Desktop-managed rate facts, before parity verification can run.
        profile.refresh_from_db()
        self.assertEqual(profile.price_min, 1_095_000)
        self.assertEqual(profile.price_max, 1_215_000)

        # Historical/manual variants are retained but may not contaminate the
        # public Catalog range once Desktop-managed CC-P variants exist.
        ProductVariant.objects.create(
            product=self.product,
            material=self.material,
            quality=self.quality,
            code="MANUAL-LOW-PRICE",
            material_weight_grams=Decimal("1"),
            final_weight_grams=Decimal("1"),
            print_time_minutes=1,
            is_active=True,
        )
        from . import epic49_catalog_profile
        asset = SimpleNamespace(
            commercial_license_status="allowed",
            license_name="Commercial",
            license_url="https://example.com/license",
        )
        synced = epic49_catalog_profile.sync_catalog_profile(
            self.product,
            asset,
            {
                "desktop_product_id": 625,
                "pricing_strategy": "dynamic",
                "availability_status": "made_to_order",
                "material_color_options_json": json.dumps([{"material": self.material.name}]),
            },
            price_min=1,
            price_max=2,
            bump_revision=False,
        )
        synced.refresh_from_db()
        self.assertEqual(synced.price_min, 1_095_000)
        self.assertEqual(synced.price_max, 1_215_000)

    def test_desktop_two_brands_same_material_color_create_distinct_fixed_variants(self):
        base = {
            "name": "پایه کیک 20",
            "description": "",
            "size_label": "20",
            "weight_grams": 300,
            "material_weight_grams": 320,
            "support_weight_grams": 20,
            "print_time_minutes": 200,
            "part_length_cm": 20,
            "part_width_cm": 20,
            "part_height_cm": 13,
            "material": self.material.name,
            "color": "سفید",
            "stock_roll_count": 3,
            "roll_weight_grams": 1000,
            "print_hourly_rate": 150000,
            "is_active": True,
        }
        rows = [
            {
                **base,
                "key": "cake20--r1-m1",
                "brand": "Bambu Lab",
                "manufacturer": "Bambu Lab",
                "fixed_price": 900000,
                "sale_price_per_roll": 3_600_000,
                "sort_order": 10,
                "is_default": True,
            },
            {
                **base,
                "key": "cake20--r1-m2",
                "brand": "eSUN",
                "manufacturer": "eSUN",
                "fixed_price": 1_050_000,
                "sale_price_per_roll": 4_000_000,
                "sort_order": 20,
            },
        ]
        count = sync_desktop_profile_matrix(self.product, self._asset(rows))
        self.assertEqual(count, 2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.pricing_policy, "profile_material_color_fixed")
        variants = list(
            self.product.variants.filter(code__startswith=f"CC-P{self.product.pk}-")
            .select_related("color")
            .order_by("fixed_price_override")
        )
        self.assertEqual(len(variants), 2)
        self.assertEqual(
            [(v.color.brand_name, v.fixed_price_override) for v in variants],
            [("Bambu Lab", 900000), ("eSUN", 1050000)],
        )
        self.assertEqual({v.part_dimensions_label for v in variants}, {"20 × 20 × 13 سانتی‌متر"})

    def test_variant_api_exposes_manufacturer_swatch_image_stock_preheat_and_orderable(self):
        color = MaterialColorOption.objects.create(
            material=self.material,
            name="صورتی",
            code="pink-esun",
            hex_code="#FF66AA",
            brand_name="eSUN",
            manufacturer_name="eSUN",
            roll_weight_grams=Decimal("1000"),
            stock_roll_count_snapshot=Decimal("3"),
            sale_price_per_roll=4_000_000,
            print_hourly_rate=160_000,
            supervision_hourly_rate=40_000,
            preheat_hours=Decimal("2"),
            preheat_temperature_c=Decimal("65"),
            preheat_hourly_rate=25_000,
            filament_image_url="https://example.com/esun-pink.webp",
            color_finish="glossy",
            palette_hexes=["#FF66AA", "#FFFFFF"],
        )
        variant = ProductVariant.objects.create(
            product=self.product,
            material=self.material,
            quality=self.quality,
            color=color,
            code="OFFER-OPS-API",
            material_weight_grams=Decimal("200"),
            final_weight_grams=Decimal("200"),
            print_time_minutes=90,
            is_active=True,
        )
        response = self.client.get(
            reverse("store:variant_commerce_options"),
            {"ids": str(variant.pk)},
        )
        self.assertEqual(response.status_code, 200)
        meta = response.json()["variants"][str(variant.pk)]
        self.assertEqual(meta["filament_manufacturer_name"], "eSUN")
        self.assertEqual(meta["filament_brand_name"], "eSUN")
        self.assertEqual(meta["color_name"], "صورتی")
        self.assertEqual(meta["material_id"], self.material.pk)
        self.assertEqual(meta["quality_id"], self.quality.pk)
        self.assertEqual(meta["quality"], str(self.quality))
        self.assertEqual(meta["unit_price"], variant.price_breakdown()["unit_price"])
        self.assertEqual(meta["stock_status"], variant.stock_status)
        self.assertEqual(meta["color_hex"], "#FF66AA")
        self.assertEqual(meta["color_finish"], "glossy")
        self.assertEqual(meta["color_palette_hexes"], ["#FF66AA", "#FFFFFF"])
        self.assertEqual(meta["filament_sale_price_per_roll"], 4_000_000)
        self.assertEqual(Decimal(meta["filament_sale_price_per_gram"]), Decimal("4000"))
        self.assertEqual(meta["filament_image_url"], "https://example.com/esun-pink.webp")
        self.assertEqual(Decimal(meta["current_stock_grams"]), Decimal("3000"))
        self.assertTrue(meta["color_stock_sufficient"])
        self.assertTrue(meta["orderable"])
        self.assertEqual(meta["offer_print_hourly_rate"], 160000)
        self.assertEqual(Decimal(meta["preheat_hours"]), Decimal("2"))

    def test_storefront_selector_is_color_first_with_palette_and_finish_visuals(self):
        root = Path(__file__).resolve().parents[1]
        js = (root / "static" / "store" / "js" / "phase50-profile-selector.js").read_text(encoding="utf-8")
        css = (root / "static" / "store" / "css" / "phase50-profile-selector.css").read_text(encoding="utf-8")
        template = (root / "templates" / "store" / "product_detail.html").read_text(encoding="utf-8")
        self.assertIn('GUIDED_DIMENSIONS = ["size", "color", "material", "quality"]', js)
        self.assertIn('brand: "برند فیلامنت"', js)
        self.assertNotIn('manufacturer: "سازنده / برند فیلامنت"', js)
        self.assertIn("colorPalette", js)
        self.assertIn("colorFinishLabel", js)
        self.assertIn("filamentSalePricePerGram", js)
        self.assertIn("linear-gradient(135deg", js)
        self.assertIn("button.disabled", js)
        self.assertIn("resolveGuidedVariant", js)
        self.assertIn(".store-profile-color-swatch", css)
        self.assertIn(".store-profile-color-image", css)
        self.assertNotIn("filament_visual_options", template)
        self.assertNotIn("قیمت خودکار هر گرم", template)
