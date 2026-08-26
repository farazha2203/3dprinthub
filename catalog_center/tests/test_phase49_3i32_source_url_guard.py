from __future__ import annotations

import json
import sqlite3
import unittest

from app.phase49_3i32_source_url_guard import (
    install_workspace,
    recover_source_url_from_history,
    resolve_source_url_for_save,
)


class _Var:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class _DB:
    def __init__(self, source_url):
        self.row = {
            "id": 7,
            "source_code": "makerworld",
            "external_id": "3176140",
            "source_url": source_url,
            "normalized_url": source_url,
            "fingerprint": "before",
        }

    def product(self, _product_id):
        return dict(self.row)

    def update_product(self, _product_id, values):
        self.row.update(values)


class _Workspace:
    def __init__(self, existing, primary="", secondary=""):
        self.product_id = 7
        self.db = _DB(existing)
        self.row = self.db.product(7)
        self.source_url = _Var(primary)
        self.spec_source_url = _Var(secondary)

    def save(self, silent=False):
        # Emulate the mature ProductStudio boundary which historically treated
        # two blank mirrored controls as authority and could erase source_url.
        chosen = self.source_url.get().strip() or self.spec_source_url.get().strip()
        self.db.update_product(7, {"source_url": chosen, "normalized_url": chosen})
        self.row = self.db.product(7)
        return True


class _HistoryDB:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            "CREATE TABLE product_history(id INTEGER PRIMARY KEY, product_id INTEGER, before_json TEXT, after_json TEXT)"
        )
        self.conn.execute(
            "CREATE TABLE discovered_urls(id INTEGER PRIMARY KEY, source_code TEXT, external_id TEXT, url TEXT)"
        )
        self.conn.commit()


class Phase49I32SourceUrlGuardTests(unittest.TestCase):
    def test_resolver_preserves_existing_when_both_controls_are_blank(self):
        existing = "https://makerworld.com/en/models/3176140-product-name"
        self.assertEqual(resolve_source_url_for_save(existing, "", ""), existing)

    def test_resolver_accepts_explicit_primary_edit(self):
        existing = "https://example.com/old"
        new = "https://example.com/new"
        self.assertEqual(resolve_source_url_for_save(existing, new, existing), new)

    def test_resolver_accepts_explicit_secondary_edit_when_primary_is_unchanged(self):
        existing = "https://example.com/old"
        new = "https://example.com/new"
        self.assertEqual(resolve_source_url_for_save(existing, existing, new), new)

    def test_resolver_does_not_invent_url_for_never_linked_product(self):
        self.assertEqual(resolve_source_url_for_save("", "", ""), "")

    def test_recovery_uses_exact_pre_delete_url_from_product_history(self):
        db = _HistoryDB()
        expected = "https://makerworld.com/en/models/3176140-product-name?from=search#profileId-3591648"
        db.conn.execute(
            "INSERT INTO product_history(id, product_id, before_json, after_json) VALUES(1, 7, ?, ?)",
            (json.dumps({"source_url": expected}), json.dumps({"source_url": ""})),
        )
        db.conn.commit()
        recovered = recover_source_url_from_history(
            db,
            7,
            {"source_code": "makerworld", "external_id": "3176140", "source_url": ""},
        )
        self.assertEqual(recovered, expected)

    def test_recovery_falls_back_to_exact_discovered_identity_without_network(self):
        db = _HistoryDB()
        expected = "https://makerworld.com/en/models/3176140-product-name"
        db.conn.execute(
            "INSERT INTO discovered_urls(id, source_code, external_id, url) VALUES(1, 'makerworld', '3176140', ?)",
            (expected,),
        )
        db.conn.commit()
        recovered = recover_source_url_from_history(
            db,
            7,
            {"source_code": "makerworld", "external_id": "3176140", "source_url": ""},
        )
        self.assertEqual(recovered, expected)

    def test_final_workspace_save_guard_prevents_accidental_link_deletion(self):
        existing = "https://makerworld.com/en/models/3176140-product-name?from=search#profileId-3591648"
        Guarded = type("GuardedWorkspace", (_Workspace,), {})
        install_workspace(Guarded)
        workspace = Guarded(existing, "", "")

        self.assertTrue(workspace.save(silent=True))
        self.assertEqual(workspace.db.row["source_url"], existing)
        self.assertEqual(workspace.source_url.get(), existing)
        self.assertEqual(workspace.spec_source_url.get(), existing)
        self.assertTrue(workspace.db.row["normalized_url"])

    def test_final_workspace_save_guard_preserves_intentional_link_change(self):
        existing = "https://example.com/old"
        new = "https://example.com/new"
        Guarded = type("EditedWorkspace", (_Workspace,), {})
        install_workspace(Guarded)
        workspace = Guarded(existing, existing, new)

        self.assertTrue(workspace.save())
        self.assertEqual(workspace.db.row["source_url"], new)
        self.assertEqual(workspace.source_url.get(), new)
        self.assertEqual(workspace.spec_source_url.get(), new)


if __name__ == "__main__":
    unittest.main()
