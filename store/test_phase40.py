from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class Phase40ConnectionSettingsTests(SimpleTestCase):
    def test_mysql_connections_force_innodb_and_strict_mode(self):
        database = settings.DATABASES["default"]
        if database.get("ENGINE") != "django.db.backends.mysql":
            self.skipTest("MySQL is not configured in this environment.")
        options = database.get("OPTIONS", {})
        self.assertEqual(options.get("charset"), "utf8mb4")
        init_command = options.get("init_command", "")
        self.assertIn("default_storage_engine='InnoDB'", init_command)
        self.assertIn("STRICT_TRANS_TABLES", init_command)


class Phase40ImporterContractTests(SimpleTestCase):
    def test_importer_has_current_v85_safety_contract(self):
        path = Path(__file__).resolve().parent / "management" / "commands" / "phase37_import_catalog_center.py"
        text = path.read_text(encoding="utf-8")
        for marker in (
            "CATALOG_ACK_JSON=",
            "CATALOG_INTELLIGENCE_V8_5_IMPORT=OK",
            "Unsupported batch schema; expected 8.5",
            "Editorial path escapes the batch root",
            "local_image_files_json",
            "publish_incomplete",
        ):
            self.assertIn(marker, text)
