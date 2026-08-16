from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app import secure_secrets
from app.persistent_connection_profile import persist_connection_profile


class _Value:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value


class _DB:
    def __init__(self):
        self.values = {}

    def set_setting(self, key, value):
        self.values[key] = value


class PersistentConnectionProfileTests(unittest.TestCase):
    def test_validated_profile_persists_nonsecrets_and_keyring_secrets(self):
        app = SimpleNamespace(
            db=_DB(),
            ftp_password=_Value("ftp-secret"),
            _entered_bridge_token=lambda: "bridge-secret",
            _refresh_connection_secret_source=lambda: None,
        )
        cfg = SimpleNamespace(
            ftp_host="ftp.3dprinthub.ir",
            ftp_port=21,
            ftp_user="user",
            remote_root="/3dprinthub",
            site_url="https://3dprinthub.ir",
        )
        with patch("app.persistent_connection_profile.set_secret") as set_secret:
            persist_connection_profile(app, cfg)

        self.assertEqual(app.db.values["site_url"], "https://3dprinthub.ir")
        self.assertEqual(app.db.values["ftp_host"], "ftp.3dprinthub.ir")
        self.assertNotIn("ftp_password", app.db.values)
        self.assertNotIn("bridge_token", app.db.values)
        set_secret.assert_any_call("ftp_password", "ftp-secret")
        set_secret.assert_any_call("bridge_token", "bridge-secret")

    def test_env_connection_secrets_move_to_keyring_and_are_scrubbed(self):
        class FakeKeyring:
            def __init__(self):
                self.values = {}

            def set_password(self, service, username, password):
                self.values[(service, username)] = password

        fake = FakeKeyring()
        with tempfile.TemporaryDirectory() as temporary:
            env_file = Path(temporary) / ".env"
            env_file.write_text(
                "CATALOG_SITE_URL=https://3dprinthub.ir\n"
                "FTP_PASSWORD=ftp-secret\n"
                "CATALOG_BRIDGE_TOKEN='bridge-secret'\n",
                encoding="utf-8",
            )
            with patch("app.secure_secrets._keyring", return_value=fake):
                migrated = secure_secrets.migrate_connection_env_to_keyring(env_file)

            text = env_file.read_text(encoding="utf-8")
            self.assertEqual(migrated, ["bridge_token", "ftp_password"])
            self.assertNotIn("ftp-secret", text)
            self.assertNotIn("bridge-secret", text)
            self.assertIn("CATALOG_SITE_URL=https://3dprinthub.ir", text)
            self.assertEqual(
                fake.values[(secure_secrets.SERVICE_NAME, "FTP_PASSWORD")],
                "ftp-secret",
            )
            self.assertEqual(
                fake.values[(secure_secrets.SERVICE_NAME, "CATALOG_BRIDGE_TOKEN")],
                "bridge-secret",
            )


if __name__ == "__main__":
    unittest.main()
