from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from store.phase49_catalog_visibility import (
    evaluate_catalog_product_visibility,
    publish_catalog_product_to_store,
)


class _Variants:
    def __init__(self, active=True, priced=True):
        self.active = active
        self.priced = priced
        self._price_filter = False

    def filter(self, **kwargs):
        clone = _Variants(self.active, self.priced)
        clone._price_filter = "cached_unit_price__gt" in kwargs
        return clone

    def exists(self):
        return self.priced if self._price_filter else self.active


class _Category:
    is_active = True


class _Asset:
    commercial_license_status = "allowed"


class _Product:
    category_id = 1
    category = _Category()
    main_image = "store/products/example.jpg"
    fixed_price = 500000
    variants = _Variants()
    is_active = False
    robots_index = False
    robots_follow = False
    published_at = object()

    def __init__(self):
        self.saved_fields = []

    def save(self, update_fields=None):
        self.saved_fields = list(update_fields or [])

    def get_absolute_url(self):
        return "/store/product/example/"


class Phase49VisibilityTests(SimpleTestCase):
    def test_approved_catalog_product_becomes_store_visible(self):
        product = _Product()
        data = {"publish_as_product": 1, "approved_for_sale": 1}
        decision = publish_catalog_product_to_store(product, _Asset(), data)
        self.assertTrue(decision.visible)
        self.assertTrue(product.is_active)
        self.assertTrue(product.robots_index)
        self.assertTrue(product.robots_follow)
        self.assertIn("is_active", product.saved_fields)

    def test_missing_main_image_fails_closed(self):
        product = _Product()
        product.main_image = ""
        with self.assertRaises(ValidationError):
            publish_catalog_product_to_store(
                product, _Asset(), {"publish_as_product": 1, "approved_for_sale": 1}
            )
        self.assertFalse(product.is_active)

    def test_not_approved_does_not_auto_activate(self):
        product = _Product()
        decision = evaluate_catalog_product_visibility(
            product, _Asset(), {"publish_as_product": 1, "approved_for_sale": 0}
        )
        self.assertFalse(decision.requested)
        self.assertFalse(decision.visible)

    def test_importer_emits_visibility_contract(self):
        importer = (
            Path(__file__).resolve().parent
            / "management"
            / "commands"
            / "phase37_import_catalog_center.py"
        ).read_text(encoding="utf-8")
        self.assertIn("publish_catalog_product_to_store", importer)
        self.assertIn('"visible_on_store"', importer)
        self.assertIn('"product_url"', importer)
        self.assertIn('"visibility_checks"', importer)
