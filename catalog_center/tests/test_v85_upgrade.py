import hashlib
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest import mock

from app.site_connection import SiteConnection, upload_batch
from app.upgrade import install, rollback


VERSION = "8.6.0"


def write_minimal_package(source: Path) -> None:
    (source / "app").mkdir(parents=True)
    (source / "assets").mkdir()
    (source / "PACKAGE_MANIFEST.json").write_text(json.dumps({"version": VERSION}), encoding="utf-8")
    (source / "app" / "site_connection.py").write_text("# new\n", encoding="utf-8")
    (source / "app" / "version.py").write_text(f'APP_VERSION = "{VERSION}"\n', encoding="utf-8")
    (source / "launch.py").write_text(f'EXPECTED_VERSION = "{VERSION}"\n', encoding="utf-8")
    (source / "RUN.ps1").write_text('& $Python "$Root\\launch.py"\n', encoding="utf-8")
    (source / "app" / "main.py").write_text(
        "\n".join([
            "self.bridge_token_entry", "paste_bridge_token", "<Control-v>", "<Shift-Insert>",
            "open_bridge_token_menu", "toggle_bridge_token_visibility", "normalize_bridge_token_input",
        ]), encoding="utf-8"
    )
    (source / "assets" / "brand_icon.png").write_bytes(b"png")
    (source / "assets" / "brand_logo_horizontal.png").write_bytes(b"png")


class V85UpgradeTests(unittest.TestCase):
    def test_powershell_installer_invokes_upgrade_by_absolute_script_path(self):
        root = Path(__file__).resolve().parents[1]
        installer = (root / "INSTALL_OR_UPGRADE.ps1").read_text(encoding="utf-8")
        self.assertIn('Join-Path $PackageRoot "app\\upgrade.py"', installer)
        self.assertIn("& $Python $UpgradeScript --source $PackageRoot", installer)
        self.assertNotIn("-m app.upgrade", installer)
        self.assertIn("ACTIVE_VERSION=$ExpectedVersion", installer)
        self.assertIn("Push-Location $NeutralLocation", installer)

    def test_install_preserves_data_and_rollback_restores_previous_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source = root / "package"; target = root / "installed"; data = root / "data"; backups = root / "backups"
            write_minimal_package(source)
            target.mkdir(); (target / "old.txt").write_text("old", encoding="utf-8")
            data.mkdir(); db_path = data / "catalog.sqlite3"
            with closing(sqlite3.connect(db_path)) as connection:
                connection.execute("CREATE TABLE sample(value TEXT)"); connection.execute("INSERT INTO sample VALUES ('before')"); connection.commit()
            result = install(source, target, data, backups, stamp="20260816-180000")
            self.assertTrue((target / "app" / "main.py").is_file())
            with closing(sqlite3.connect(db_path)) as connection:
                self.assertEqual(connection.execute("SELECT value FROM sample").fetchone()[0], "before")
            with closing(sqlite3.connect(db_path)) as connection:
                connection.execute("UPDATE sample SET value='after'"); connection.commit()
            rolled_back = rollback(backups)
            self.assertTrue(rolled_back["target_restored"])
            self.assertEqual((target / "old.txt").read_text(encoding="utf-8"), "old")
            with closing(sqlite3.connect(db_path)) as connection:
                self.assertEqual(connection.execute("SELECT value FROM sample").fetchone()[0], "before")
            self.assertTrue((result["backup_root"] / "rollback-manifest.json").is_file())

    def test_install_works_when_extracted_package_is_nested_inside_old_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); target = root / "installed"; source = target / "3DPrintHub_Catalog_Intelligence_v8.6.0"
            write_minimal_package(source); (target / "old-root.txt").write_text("old", encoding="utf-8")
            result = install(source, target, root / "data", root / "backups", stamp="20260816-181000")
            self.assertEqual((target / "app" / "version.py").read_text(encoding="utf-8"), f'APP_VERSION = "{VERSION}"\n')
            self.assertFalse((target / "old-root.txt").exists())
            self.assertTrue((result["backup_root"] / "app_previous" / "old-root.txt").is_file())

    def test_install_can_verify_and_stage_an_already_extracted_target_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); target = root / "installed"; write_minimal_package(target)
            result = install(target, target, root / "data", root / "backups", stamp="20260816-182000")
            self.assertTrue((target / "launch.py").is_file())
            self.assertTrue((result["backup_root"] / "app_previous" / "launch.py").is_file())

    def test_invalid_batch_is_rejected_before_network_connection(self):
        with tempfile.TemporaryDirectory() as temporary:
            batch = Path(temporary) / "bad-name"; batch.mkdir()
            (batch / "batch_manifest.json").write_text(json.dumps({"schema_version": "8.5", "batch_name": "bad-name", "batch_uuid": "uuid"}), encoding="utf-8")
            settings = SiteConnection("ftp.example.com", 21, "user", "secret", "/3dprinthub", "https://example.com", "token")
            with mock.patch("app.site_connection.connect_ftp") as connection:
                with self.assertRaises(ValueError): upload_batch(settings, batch)
                connection.assert_not_called()

    def test_brand_assets_are_packaged(self):
        root = Path(__file__).resolve().parents[1]
        icon = root / "assets" / "brand_icon.png"; logo = root / "assets" / "brand_logo_horizontal.png"
        self.assertTrue(icon.is_file()); self.assertTrue(logo.is_file())
        self.assertEqual(hashlib.sha256(icon.read_bytes()).hexdigest(), "f3ff35ae0e78161d0930d82dfd15f5a9c573a99e1e6a2b2e9030275749998c86")
        self.assertEqual(hashlib.sha256(logo.read_bytes()).hexdigest(), "3b53b171f05e329f284835489d3a4729dec7bab4e7de568e23b4b3dcaeec9971")
        wrapper = (root / "BUILD_EXE.ps1").read_text(encoding="utf-8"); builder = (root / "build_portable_exe.py").read_text(encoding="utf-8")
        self.assertIn("build_portable_exe.py", wrapper); self.assertIn("--add-data", builder); self.assertIn("brand_icon.png", builder)
        self.assertIn("config.example.json", builder); self.assertIn("portable_entry.py", builder); self.assertIn("--onefile", builder)
        self.assertIn("staging_dir", builder); self.assertIn("stable_exe_updated", builder)


if __name__ == "__main__":
    unittest.main()
