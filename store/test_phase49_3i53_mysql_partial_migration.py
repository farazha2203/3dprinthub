from __future__ import annotations

import importlib
import unittest

from django.db import migrations


class Phase493I53MySQLMigration0039ContractTests(unittest.TestCase):
    def test_0039_uses_idempotent_adds_and_alters_existing_variant_support(self):
        module = importlib.import_module(
            "store.migrations.0039_phase50_filament_offer_pricing"
        )

        self.assertTrue(
            issubclass(module.AddFieldIfMissing, migrations.AddField)
        )

        operations = module.Migration.operations

        variant_support = [
            operation
            for operation in operations
            if getattr(operation, "model_name", "") == "productvariant"
            and getattr(operation, "name", "") == "support_weight_grams"
        ]
        self.assertEqual(len(variant_support), 1)
        self.assertIsInstance(variant_support[0], migrations.AlterField)
        self.assertNotIsInstance(
            variant_support[0],
            module.AddFieldIfMissing,
        )

        expected_idempotent_adds = {
            ("materialcoloroption", "brand_name"),
            ("materialcoloroption", "manufacturer_name"),
            ("materialcoloroption", "roll_weight_grams"),
            ("materialcoloroption", "stock_roll_count_snapshot"),
            ("materialcoloroption", "purchase_price_per_roll"),
            ("materialcoloroption", "sale_price_per_roll"),
            ("materialcoloroption", "usd_price_per_roll"),
            ("materialcoloroption", "usd_fx_rate_toman"),
            ("storeorderitem", "support_weight_grams"),
            ("storeorderitem", "filament_brand_name"),
            ("storeorderitem", "filament_manufacturer_name"),
        }
        actual_idempotent_adds = {
            (operation.model_name, operation.name)
            for operation in operations
            if isinstance(operation, module.AddFieldIfMissing)
        }
        self.assertEqual(actual_idempotent_adds, expected_idempotent_adds)


if __name__ == "__main__":
    unittest.main()
