from pathlib import Path
import unittest


class ServerContractTests(unittest.TestCase):
    def test_importer_emits_v84_ack_and_legacy_marker(self):
        path=Path(__file__).resolve().parents[1]/"server"/"store"/"management"/"commands"/"phase37_import_catalog_center.py"
        text=path.read_text(encoding="utf-8")
        self.assertIn("CATALOG_ACK_JSON=",text)
        self.assertIn("Unsupported batch schema; expected 8.5",text)
        self.assertIn("CATALOG_INTELLIGENCE_V8_5_IMPORT=OK",text)
        self.assertIn('"schema_version": "8.3"',text)
        self.assertIn("CATALOG_INTELLIGENCE_V8_3_IMPORT=OK",text)
        self.assertIn("CATALOG_INTELLIGENCE_V8_5_IMPORT=OK",text)
        self.assertIn("desktop_product_id",text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
