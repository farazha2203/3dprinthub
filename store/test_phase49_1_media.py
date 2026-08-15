from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import MagicMock

from django.http import Http404
from django.test import RequestFactory, SimpleTestCase, override_settings

from store.phase49_catalog_visibility import evaluate_catalog_product_visibility
from store.public_media import _safe_public_store_path, serve_public_store_media


class Phase491PublicMediaTests(SimpleTestCase):
    def test_public_store_image_is_served_from_media_root(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "store" / "products" / "demo.webp"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"RIFFdemoWEBP")
            with override_settings(MEDIA_ROOT=root):
                response = serve_public_store_media(
                    RequestFactory().get("/media/store/products/demo.webp"),
                    "store/products/demo.webp",
                )
            self.assertEqual(response.status_code, 200)
            self.assertIn("max-age=86400", response["Cache-Control"])

    def test_private_and_traversal_paths_are_rejected(self):
        for path in ("store/private-models/secret.stl", "../.env", "website/orders/a.jpg"):
            with self.subTest(path=path):
                with self.assertRaises(Http404):
                    _safe_public_store_path(path)


class Phase491VisibilityStorageTests(SimpleTestCase):
    def test_missing_physical_main_image_fails_visibility(self):
        storage = MagicMock()
        storage.exists.return_value = False
        main_image = SimpleNamespace(name="store/products/missing.webp", storage=storage)
        variants = MagicMock()
        variants.filter.return_value = variants
        variants.exists.return_value = True
        product = SimpleNamespace(
            category_id=1,
            category=SimpleNamespace(is_active=True),
            main_image=main_image,
            fixed_price=500000,
            variants=variants,
            get_absolute_url=lambda: "/store/product/test/",
        )
        asset = SimpleNamespace(commercial_license_status="allowed")
        decision = evaluate_catalog_product_visibility(
            product,
            asset,
            {"publish_as_product": 1, "approved_for_sale": 1},
        )
        self.assertFalse(decision.visible)
        self.assertFalse(decision.checks["main_image_storage"])
        self.assertIn("main_image_storage", decision.reasons)
