"""Regression of revision-safe receipt matching on the actual v8.9.11 runtime."""
import json
import unittest
from unittest.mock import patch

from app.buffer_publish import (
    BufferConfig, _receipt_for_revision, _already_sent,
    reconcile_product_receipts,
)
from app.instagram_publish import same_public_revision_already_published
from app.social_revision_identity import same_site_revision


def ack(rev, *, product=48, diagnostic="old"):
    return json.dumps({"product_id": product, "product_revision": rev,
                       "public_http_ok": True, "diagnostic_id": diagnostic})


class FakeDB:
    def __init__(self, old, new):
        self.ack = new
        self.rows = [{
            "id": 3, "status": "instagram_submitted", "server_id": "demo-post",
            "payload_json": json.dumps({"site_ack_fingerprint": old,
                                        "provider_post_id": "demo-post"}),
        }]
        self.written = []

    def sync_receipts(self, product_id, limit=160):
        return self.rows[:limit]

    def product(self, product_id):
        return {"id": product_id, "server_ack_json": self.ack}

    def record_sync_receipt(self, *args, **kwargs):
        self.written.append((args, kwargs))


class ActualRuntimeRevisionSafety(unittest.TestCase):
    def test_same_server_revision_with_changed_ack_diagnostics(self):
        previous, current = ack(2), ack(2, diagnostic="new")
        self.assertTrue(same_site_revision(previous, current))
        db = FakeDB(previous, current)
        db.rows[0]["status"] = "instagram_published"
        self.assertIsNotNone(_receipt_for_revision(db, 536, current, {"instagram_published"}))
        self.assertTrue(_already_sent(db, 536, current))
        self.assertTrue(same_public_revision_already_published(db, 536, current))

    def test_new_revision_remains_eligible(self):
        old, new = ack(1), ack(2)
        self.assertFalse(same_site_revision(old, new))
        db = FakeDB(old, new)
        db.rows[0]["status"] = "instagram_published"
        self.assertIsNone(_receipt_for_revision(db, 536, new, {"instagram_published"}))
        self.assertFalse(_already_sent(db, 536, new))

    def test_cross_product_never_matches(self):
        self.assertFalse(same_site_revision(ack(2, product=47), ack(2, product=48)))

    def test_missing_revision_fails_closed(self):
        self.assertFalse(same_site_revision('{"product_id":48}', ack(2)))
        self.assertFalse(same_site_revision("bad json", ack(2)))

    def test_provider_reconciliation_tolerates_cosmetic_ack_change(self):
        db = FakeDB(ack(2), ack(2, diagnostic="after-qt"))
        with patch("app.buffer_publish.get_secret", return_value="test-only"), patch(
            "app.buffer_publish._read_post_state",
            return_value={"id": "demo-post", "status": "sent", "externalLink": "https://example.invalid/demo"},
        ):
            result = reconcile_product_receipts(db, 536, BufferConfig(channel_id="dry-run"))
        self.assertEqual(result["stale_skipped"], 0)
        self.assertEqual(len(result["reconciled"]), 1)
        self.assertEqual(len(db.written), 1)
        self.assertTrue(db.written[0][1]["payload"]["reconciled_without_repost"])


if __name__ == "__main__":
    unittest.main()
