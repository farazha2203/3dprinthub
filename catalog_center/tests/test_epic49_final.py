from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from app.site_connection import SiteConnection, _augment_ack_with_public_verification
from app.v8_features import ack_item_confirms_publish


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def _repo_server_file(relative: str) -> Path | None:
    """Return a Django-server file only when tests run inside the full repo.

    The canonical Windows Catalog Center is intentionally standalone and does
    not contain the Django project. Server contract tests are enforced in the
    Git checkout and skipped (not failed) in the portable Windows copy.
    """
    candidate = REPO / Path(relative)
    return candidate if candidate.is_file() else None


class Epic49StrictAckTests(unittest.TestCase):
    def setUp(self):
        self.row = {"publish_as_product": 1, "publish_as_portfolio": 0}
        self.base = {
            "status": "updated",
            "server_id": "119",
            "product_id": 3,
            "visible_on_store": True,
        }

    def test_public_http_failure_blocks_final_publish(self):
        self.assertFalse(
            ack_item_confirms_publish(
                {**self.base, "public_http_ok": False},
                self.row,
                require_store_visibility=True,
            )
        )

    def test_public_http_success_allows_final_publish(self):
        self.assertTrue(
            ack_item_confirms_publish(
                {**self.base, "public_http_ok": True},
                self.row,
                require_store_visibility=True,
            )
        )

    def test_legacy_phase49_ack_stays_compatible(self):
        self.assertTrue(
            ack_item_confirms_publish(
                dict(self.base),
                self.row,
                require_store_visibility=True,
            )
        )


class Epic49PublicVerificationTests(unittest.TestCase):
    def _cfg(self):
        return SiteConnection(
            ftp_host="ftp.example.test",
            ftp_port=21,
            ftp_user="user",
            ftp_password="secret",
            remote_root="/home/example/app",
            site_url="https://3dprinthub.ir",
            bridge_token="x" * 32,
        )

    @patch("app.site_connection.verify_publish_item")
    def test_visible_ack_is_augmented_with_public_http_success(self, verify):
        verify.return_value = {
            "ok": True,
            "product": {"http_status": 200, "url": "https://3dprinthub.ir/store/product/test/"},
            "images": [{"http_status": 200, "url": "https://3dprinthub.ir/media/store/products/test.webp", "ok": True}],
            "main_image_url": "https://3dprinthub.ir/media/store/products/test.webp",
            "error": "",
        }
        ack = {
            "items": [{
                "desktop_product_id": 7,
                "status": "updated",
                "server_id": 119,
                "product_id": 3,
                "visible_on_store": True,
                "product_url": "/store/product/test/",
            }]
        }
        result = _augment_ack_with_public_verification(self._cfg(), ack)
        item = result["items"][0]
        self.assertTrue(item["public_http_ok"])
        self.assertEqual(item["public_product_http_status"], 200)
        self.assertEqual(item["public_main_image_http_status"], 200)
        self.assertTrue(item["public_main_image_url"].endswith("test.webp"))

    @patch("app.site_connection.verify_publish_item")
    def test_public_failure_is_written_into_ack_error(self, verify):
        verify.return_value = {
            "ok": False,
            "product": {"http_status": 200},
            "images": [{"http_status": 404, "url": "https://3dprinthub.ir/media/store/products/missing.webp", "ok": False}],
            "main_image_url": "",
            "error": "PRODUCT_MEDIA_HTTP_FAILED",
        }
        ack = {
            "items": [{
                "status": "updated",
                "server_id": 119,
                "product_id": 3,
                "visible_on_store": True,
                "product_url": "/store/product/test/",
            }]
        }
        item = _augment_ack_with_public_verification(self._cfg(), ack)["items"][0]
        self.assertFalse(item["public_http_ok"])
        self.assertIn("PRODUCT_MEDIA_HTTP_FAILED", item["error"])


class Epic49ServerSyncContractTests(unittest.TestCase):
    def _require_server_file(self, relative: str) -> Path:
        path = _repo_server_file(relative)
        if path is None:
            self.skipTest("Standalone Catalog Center: Django server source is intentionally not packaged")
        return path

    def test_existing_product_is_resynced_instead_of_early_return(self):
        source = self._require_server_file("store/phase34b_publishing.py").read_text(encoding="utf-8")
        self.assertNotIn("if asset.product_id:\n        return asset.product", source)
        self.assertIn("_sync_product_fields(product, asset)", source)
        self.assertIn("_selected_asset_images(asset)", source)
        self.assertIn("product.images.all().delete()", source)

    def test_failed_batch_archive_is_non_destructive(self):
        source = self._require_server_file(
            "store/management/commands/epic49_archive_failed_batches.py"
        ).read_text(encoding="utf-8")
        self.assertIn("shutil.move", source)
        self.assertNotIn("shutil.rmtree", source)
        self.assertNotIn("unlink(", source)
        self.assertIn("SKIP_NO_DIAGNOSTIC", source)
        self.assertIn("SKIP_NOT_FAILED", source)


if __name__ == "__main__":
    unittest.main()
