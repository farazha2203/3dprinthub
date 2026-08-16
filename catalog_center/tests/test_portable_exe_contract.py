from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import runtime_paths


ROOT = Path(__file__).resolve().parents[1]


class PortableRuntimePathTests(unittest.TestCase):
    def test_data_root_can_be_explicitly_overridden(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(
            os.environ, {"CATALOG_DATA_ROOT": temporary}, clear=False
        ):
            self.assertEqual(runtime_paths.data_root(), Path(temporary).resolve())

    def test_frozen_data_root_is_stable_across_release_folders(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(
            os.environ,
            {"LOCALAPPDATA": temporary, "CATALOG_DATA_ROOT": ""},
            clear=False,
        ), patch.object(runtime_paths, "is_frozen", return_value=True):
            expected = Path(temporary) / "3DPrintHub" / "CatalogCenter"
            self.assertEqual(runtime_paths.data_root(), expected.resolve())

    def test_old_release_data_is_migrated_non_destructively(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            exe_root = root / "release" / "8.5.4"
            legacy = exe_root / runtime_paths.LEGACY_PORTABLE_DATA_DIRNAME
            stable = root / "stable"
            legacy.mkdir(parents=True)
            (legacy / "catalog.sqlite3").write_bytes(b"db")
            (legacy / "config.json").write_text('{"site":"old"}', encoding="utf-8")
            (legacy / "logs").mkdir()
            (legacy / "logs" / "old.log").write_text("ok", encoding="utf-8")

            with patch.object(runtime_paths, "is_frozen", return_value=True), patch.object(
                runtime_paths, "executable_root", return_value=exe_root
            ), patch.object(runtime_paths, "persistent_data_root", return_value=stable), patch.dict(
                os.environ, {"CATALOG_DATA_ROOT": ""}, clear=False
            ):
                first = runtime_paths.migrate_legacy_portable_data()
                second = runtime_paths.migrate_legacy_portable_data()

            self.assertTrue(first["migrated"])
            self.assertGreaterEqual(first["copied"], 3)
            self.assertEqual((stable / "catalog.sqlite3").read_bytes(), b"db")
            self.assertTrue((stable / "logs" / "old.log").is_file())
            self.assertTrue((legacy / "catalog.sqlite3").is_file())
            self.assertEqual(second["reason"], "already_migrated")

    def test_portable_entry_keeps_writable_data_outside_bundle(self):
        source = (ROOT / "portable_entry.py").read_text(encoding="utf-8")
        self.assertIn("data_root()", source)
        self.assertIn("migrate_legacy_portable_data()", source)
        self.assertIn("persistent_data_root()", source)
        self.assertIn('app_main.DB_FILE = data / "catalog.sqlite3"', source)
        self.assertIn('app_main.CONFIG_FILE = data / "config.json"', source)
        self.assertIn('app_main.PROFILE_ROOT = data / "browser_profiles"', source)
        self.assertIn("--portable-verify", source)
        self.assertNotIn(r"D:\projects", source)


class PortableBuildContractTests(unittest.TestCase):
    def test_build_is_single_file_without_installer(self):
        wrapper = (ROOT / "BUILD_EXE.ps1").read_text(encoding="utf-8")
        builder = (ROOT / "build_portable_exe.py").read_text(encoding="utf-8")
        self.assertIn("PORTABLE_MODE=SINGLE_FILE", wrapper)
        self.assertIn("INSTALLER_REQUIRED=NO", wrapper)
        self.assertIn('"--onefile"', builder)
        self.assertIn('"--windowed"', builder)
        self.assertIn("portable_entry.py", builder)
        self.assertIn("config.example.json", builder)
        self.assertIn("release-manifest.json", builder)
        self.assertIn("PORTABLE_EXE_SHA256", builder)
        self.assertIn("--portable-verify", builder)
        self.assertNotIn("Inno Setup", builder)
        self.assertNotIn("NSIS", builder)

    def test_build_does_not_embed_runtime_database_or_secrets(self):
        builder = (ROOT / "build_portable_exe.py").read_text(encoding="utf-8")
        forbidden = ["catalog.sqlite3", "APIKEY.txt", "APIKEY-AVAL.txt", "ftp_password", "bridge_token"]
        for value in forbidden:
            self.assertNotIn(value, builder)


if __name__ == "__main__":
    unittest.main()
