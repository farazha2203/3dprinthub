from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import epic49_local_publish as local_publish


ROOT = Path(__file__).resolve().parents[1]


class Epic49LocalPublishTests(unittest.TestCase):
    def test_local_preflight_accepts_only_expected_sqlite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "manage.py").write_text("# test\n", encoding="utf-8")
            db = (root / "db.sqlite3").resolve()
            stdout = f"EPIC49_LOCAL_DB_VENDOR=sqlite\nEPIC49_LOCAL_DB_NAME={db}\n"
            completed = subprocess.CompletedProcess(["python"], 0, stdout=stdout, stderr="")
            with patch.object(local_publish, "running_as_portable", return_value=False), patch.object(
                local_publish, "_run", return_value=completed
            ) as runner:
                result = local_publish.local_django_preflight(
                    repo_root=root,
                    python_executable="python-test",
                )
            self.assertEqual(result["database_vendor"], "sqlite")
            self.assertEqual(result["database_name"], db)
            command = runner.call_args.args[0]
            self.assertIn("manage.py", " ".join(command))
            self.assertIn("shell", command)

    def test_local_preflight_blocks_mysql_even_if_manage_py_exists(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "manage.py").write_text("# test\n", encoding="utf-8")
            completed = subprocess.CompletedProcess(
                ["python"],
                0,
                stdout="EPIC49_LOCAL_DB_VENDOR=mysql\nEPIC49_LOCAL_DB_NAME=production_db\n",
                stderr="",
            )
            with patch.object(local_publish, "running_as_portable", return_value=False), patch.object(
                local_publish, "_run", return_value=completed
            ):
                with self.assertRaisesRegex(RuntimeError, "SQLite نیست"):
                    local_publish.local_django_preflight(repo_root=root, python_executable="python-test")

    def test_local_preflight_blocks_unexpected_sqlite_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "manage.py").write_text("# test\n", encoding="utf-8")
            other_db = (root / "other.sqlite3").resolve()
            completed = subprocess.CompletedProcess(
                ["python"],
                0,
                stdout=f"EPIC49_LOCAL_DB_VENDOR=sqlite\nEPIC49_LOCAL_DB_NAME={other_db}\n",
                stderr="",
            )
            with patch.object(local_publish, "running_as_portable", return_value=False), patch.object(
                local_publish, "_run", return_value=completed
            ):
                with self.assertRaisesRegex(RuntimeError, "مورد انتظار یکی نیست"):
                    local_publish.local_django_preflight(repo_root=root, python_executable="python-test")

    def test_local_preflight_blocks_portable_runtime(self):
        with patch.object(local_publish, "running_as_portable", return_value=True):
            with self.assertRaisesRegex(RuntimeError, "Portable"):
                local_publish.local_django_preflight(repo_root=Path.cwd(), python_executable="python-test")

    def test_local_import_uses_official_v85_management_command_and_ack(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            (root / "manage.py").write_text("# test\n", encoding="utf-8")
            db = (root / "db.sqlite3").resolve()
            batch = Path(temp) / "desktop_catalog_v85_20260818_182300"
            batch.mkdir()
            (batch / "batch_manifest.json").write_text(
                json.dumps({"schema_version": "8.5", "batch_uuid": "u", "models": []}),
                encoding="utf-8",
            )
            preflight = subprocess.CompletedProcess(
                ["python"], 0,
                stdout=f"EPIC49_LOCAL_DB_VENDOR=sqlite\nEPIC49_LOCAL_DB_NAME={db}\n",
                stderr="",
            )
            ack = {
                "schema_version": "8.5",
                "batch_uuid": "u",
                "imported_count": 1,
                "failed_count": 0,
                "items": [{"desktop_product_id": 7, "status": "created", "server_id": 1, "product_id": 2}],
            }
            imported = subprocess.CompletedProcess(
                ["python"], 0,
                stdout="CATALOG_ACK_JSON=" + json.dumps(ack, ensure_ascii=False) + "\nIMPORTED_COUNT=1\n",
                stderr="",
            )
            with patch.object(local_publish, "running_as_portable", return_value=False), patch.object(
                local_publish, "_run", side_effect=[preflight, imported]
            ) as runner:
                result = local_publish.import_batch_to_local_django(
                    batch,
                    repo_root=root,
                    python_executable="python-test",
                )
            self.assertEqual(result["ack"]["failed_count"], 0)
            import_command = runner.call_args_list[1].args[0]
            self.assertIn("phase37_import_catalog_center", import_command)
            self.assertIn("--continue-on-error", import_command)
            self.assertNotIn("ftp", " ".join(import_command).lower())


class Epic49DualPublishContractTests(unittest.TestCase):
    def test_workspace_exposes_two_explicit_publish_targets(self):
        source = (ROOT / "app" / "phase49_dual_publish_desktop.py").read_text(encoding="utf-8")
        for marker in [
            "🧪 انتشار آزمایشی روی کامپیوتر",
            "🌐 انتشار واقعی روی سایت اصلی",
            "def publish_to_local_computer",
            "def publish_to_production_site",
            "build_batch(product_ids=[self.product_id], quiet=True)",
            "self.app.publish_product_now(self.product_id, parent=self)",
            "انتشار روی سایت اصلی — مرحله ۱ از ۲",
            "تأیید نهایی انتشار Production",
            "desktop_local_imported",
        ]:
            self.assertIn(marker, source)

    def test_local_module_has_no_ftp_or_bridge_publish_dependency(self):
        source = (ROOT / "app" / "epic49_local_publish.py").read_text(encoding="utf-8")
        self.assertIn("phase37_import_catalog_center", source)
        self.assertIn("EPIC49_LOCAL_DB_VENDOR", source)
        self.assertIn("expected_local_db", source)
        self.assertNotIn("upload_batch", source)
        self.assertNotIn("import_batch(settings", source)
        self.assertNotIn("connect_ftp", source)

    def test_launcher_installs_and_reports_dual_publish_contract(self):
        source = (ROOT / "launch.py").read_text(encoding="utf-8")
        self.assertIn("install_dual_publish_workspace(ProductWorkspace)", source)
        self.assertIn("EPIC49_DUAL_PUBLISH_TARGETS=ENABLED", source)
        self.assertIn("EPIC49_LOCAL_PUBLISH_SQLITE_GUARD=ENABLED", source)


if __name__ == "__main__":
    unittest.main()
