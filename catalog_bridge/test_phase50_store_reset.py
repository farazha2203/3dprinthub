from __future__ import annotations

import gzip
import hashlib
import json
import os
import tempfile
from pathlib import Path

from django.test import TestCase, override_settings

from store.models import Category, ImportedPrintAsset, PrintCatalogSource, Product, ProductImage
from website.models import HomepageHeroSlide


TOKEN = "phase50-store-reset-token-12345678901234567890"
HEADERS = {"HTTP_AUTHORIZATION": f"Bearer {TOKEN}"}
CONFIRMATION = "RESET_IMPORTED_STORE_PRODUCTS"


@override_settings(CATALOG_BRIDGE_TOKEN=TOKEN)
class Phase50StoreResetTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.media_root = self.root / "media"
        self.backup_base = self.root / "backups"
        self.media_root.mkdir(parents=True)
        self.backup_base.mkdir(parents=True)
        self.settings_ctx = self.settings(
            MEDIA_ROOT=str(self.media_root),
            PHASE50_STORE_RESET_BACKUP_ROOT=str(self.backup_base),
        )
        self.settings_ctx.enable()

    def tearDown(self):
        self.settings_ctx.disable()
        self.temp.cleanup()

    def _catalog_product(self):
        category = Category.objects.create(name="Reset Category", slug="reset-category")
        product = Product.objects.create(
            category=category,
            title="Reset Product",
            slug="reset-product",
            sku="RESET-001",
            short_description="Reset product short description",
            description="Reset product description",
            main_image="store/products/reset-main.webp",
            is_active=True,
        )
        source = PrintCatalogSource.objects.create(
            name="Reset Source",
            code="reset-source",
            base_url="https://example.com/",
        )
        asset = ImportedPrintAsset.objects.create(
            source=source,
            source_url="https://example.com/reset-product",
            external_id="RESET-EXT-1",
            title="Reset source asset",
            product=product,
        )
        gallery = ProductImage.objects.create(
            product=product,
            image="store/products/gallery/reset-gallery.webp",
            alt_text="Reset gallery",
        )
        slide = HomepageHeroSlide.objects.create(
            asset=asset,
            title_override="Reset Hero",
            is_active=True,
        )
        return product, asset, gallery, slide

    def _write_media(self, name: str, payload: bytes) -> dict:
        live = self.media_root / name
        live.parent.mkdir(parents=True, exist_ok=True)
        live.write_bytes(payload)
        return {
            "name": name,
            "exists": True,
            "size": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }

    def _backup(self, product, asset, slide, media_rows):
        root = self.backup_base / "20260914-170000-store-product-reset"
        root.mkdir()
        dump = root / "database-before-3i53.sql.gz"
        with gzip.open(dump, "wb", compresslevel=1) as handle:
            handle.write(b"-- MySQL dump 10.13 test fixture\n")
            handle.write(os.urandom(16384))
        for item in media_rows:
            live = self.media_root / item["name"]
            backup = root / "media" / item["name"]
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(live.read_bytes())
        manifest = {
            "products": [{"id": product.pk}],
            "variants": 0,
            "images": 1,
            "orders": 0,
            "order_items": 0,
            "inventory_movements": 0,
            "linked_assets": [{"id": asset.pk, "product_id": product.pk}],
            "hero_slides": [{"id": slide.pk, "asset_id": asset.pk}],
            "media": media_rows,
        }
        (root / "store-reset-manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        return root

    def _payload(self, backup_root, **overrides):
        payload = {
            "confirmation": CONFIRMATION,
            "backup_root": str(backup_root),
            "expected_products": 1,
            "expected_variants": 0,
            "expected_images": 1,
            "expected_hero_slides": 1,
            "preserve_source_assets": True,
            "preserve_master_data": True,
            "preserve_portfolio": True,
        }
        payload.update(overrides)
        return payload

    def test_reset_requires_auth_and_explicit_confirmation(self):
        response = self.client.post(
            "/api/catalog-bridge/v1/store-reset/",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        response = self.client.post(
            "/api/catalog-bridge/v1/store-reset/",
            data=json.dumps({"confirmation": "wrong"}),
            content_type="application/json",
            **HEADERS,
        )
        self.assertEqual(response.status_code, 400)

    def test_preflight_reports_exact_preservation_contract(self):
        product, _asset, _gallery, slide = self._catalog_product()
        response = self.client.get(
            "/api/catalog-bridge/v1/store-reset/",
            **HEADERS,
        )
        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["eligible"])
        self.assertEqual(payload["counts"]["products"], 1)
        self.assertEqual(payload["counts"]["hero_slides"], 1)
        self.assertTrue(payload["preserves"]["hero_slides"])
        self.assertTrue(payload["preserves"]["orders_and_snapshots"])
        self.assertEqual(slide.asset.product_id, product.pk)

    def test_reset_refuses_manual_unlinked_product(self):
        category = Category.objects.create(name="Manual", slug="manual")
        Product.objects.create(
            category=category,
            title="Manual Product",
            slug="manual-product",
            sku="MANUAL-1",
            short_description="Manual",
            description="Manual",
            main_image="store/products/manual.webp",
        )
        response = self.client.post(
            "/api/catalog-bridge/v1/store-reset/",
            data=json.dumps({
                "confirmation": CONFIRMATION,
                "expected_products": 1,
                "expected_variants": 0,
                "expected_images": 0,
                "expected_hero_slides": 0,
                "preserve_source_assets": True,
                "preserve_master_data": True,
                "preserve_portfolio": True,
            }),
            content_type="application/json",
            **HEADERS,
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("imported Catalog Products", response.json()["detail"])
        self.assertEqual(Product.objects.count(), 1)

    def test_verified_reset_clears_products_and_preserves_source_asset_and_hero(self):
        product, asset, _gallery, slide = self._catalog_product()
        media = [
            self._write_media("store/products/reset-main.webp", b"main-image-bytes" * 100),
            self._write_media("store/products/gallery/reset-gallery.webp", b"gallery-image-bytes" * 100),
        ]
        backup_root = self._backup(product, asset, slide, media)
        response = self.client.post(
            "/api/catalog-bridge/v1/store-reset/",
            data=json.dumps(self._payload(backup_root)),
            content_type="application/json",
            **HEADERS,
        )
        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["after"]["products"], 0)
        self.assertEqual(payload["after"]["images"], 0)
        self.assertEqual(payload["after"]["hero_slides"], 1)
        self.assertEqual(payload["after"]["linked_assets"], 0)
        self.assertEqual(payload["hero_slides_preserved"], [slide.pk])
        self.assertEqual(payload["deleted_media_count"], 2)
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductImage.objects.count(), 0)
        self.assertEqual(HomepageHeroSlide.objects.count(), 1)
        asset.refresh_from_db()
        slide.refresh_from_db()
        self.assertIsNone(asset.product_id)
        self.assertEqual(slide.asset_id, asset.pk)
        for item in media:
            self.assertFalse((self.media_root / item["name"]).exists())
            self.assertTrue((backup_root / "media" / item["name"]).exists())
