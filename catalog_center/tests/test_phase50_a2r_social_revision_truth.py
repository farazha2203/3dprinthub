"""A2R Feed receipt checks with modern manual Story resend kept separately."""
import json
import unittest

from app.buffer_publish import _receipt_for_revision, _already_sent
from app.instagram_publish import same_public_revision_already_published
from app.social_revision_identity import same_site_revision


def ack(revision, *, extra=None, product=48):
    return json.dumps({
        "product_id": product, "product_revision": revision,
        "product_url": "/store/product/little-ballerina/",
        "public_http_ok": True,
        **(extra or {}),
    }, ensure_ascii=False)


class ReceiptDB:
    def __init__(self, receipt_ack):
        self.rows = [
            {"status": "instagram_published", "payload_json": json.dumps({
                "site_ack_fingerprint": receipt_ack, "provider_post_id": "previous-feed",
            })},
            {"status": "instagram_story_published", "payload_json": json.dumps({
                "site_ack_fingerprint": receipt_ack, "provider_post_id": "previous-story",
            })},
        ]

    def sync_receipts(self, product_id, limit=160):
        return self.rows[:limit]


class RevisionIdentityTests(unittest.TestCase):
    def test_diagnostic_ack_reordering_not_new_revision(self):
        old = ack(2, extra={"diagnostic_id": "first"})
        new = ack(2, extra={"diagnostic_id": "new", "server_ack_time": "later"})
        self.assertTrue(same_site_revision(old, new))
        db = ReceiptDB(old)
        self.assertIsNotNone(_receipt_for_revision(db, 536, new, {"instagram_published"}))
        self.assertTrue(_already_sent(db, 536, new))
        self.assertTrue(same_public_revision_already_published(db, 536, new))

    def test_real_new_revision_is_eligible_not_marked_duplicate(self):
        db = ReceiptDB(ack(1))
        new = ack(2)
        self.assertFalse(same_site_revision(ack(1), new))
        self.assertIsNone(_receipt_for_revision(db, 536, new, {"instagram_published"}))
        self.assertFalse(_already_sent(db, 536, new))
        self.assertFalse(same_public_revision_already_published(db, 536, new))

    def test_cross_product_must_not_match(self):
        self.assertFalse(same_site_revision(ack(2, product=47), ack(2, product=48)))

    def test_missing_or_invalid_revision_is_not_proof(self):
        self.assertFalse(same_site_revision("{}", '{"product_id":48,"product_revision":2}'))
        self.assertFalse(same_site_revision("not json", ack(2)))
        self.assertFalse(same_site_revision("", ack(2)))

    def test_identical_legacy_ack_preserves_compatibility(self):
        self.assertTrue(same_site_revision('{"legacy":"v1"}', '{"legacy":"v1"}'))


if __name__ == "__main__":
    unittest.main()
