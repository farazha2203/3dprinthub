from __future__ import annotations

import unittest
from types import SimpleNamespace

from app import phase49_3i27_category_provider_bridge as phase


class Phase493I27CategoryProviderBridgeTests(unittest.TestCase):
    def test_workspace_categories_uses_app_provider_not_database(self):
        workspace = SimpleNamespace(
            app=SimpleNamespace(
                get_all_categories=lambda: [
                    {"slug": "decor", "name": "دکور و لوازم خانه"},
                    {"slug": "cake-stand", "name": "استند کیک"},
                ]
            ),
            db=SimpleNamespace(),
            product_id=10,
        )
        rows = phase.workspace_categories(workspace)
        self.assertEqual([row["slug"] for row in rows], ["decor", "cake-stand"])
        self.assertFalse(hasattr(workspace.db, "categories"))

    def test_install_bridges_missing_database_categories_before_exact_link_action(self):
        calls = []

        class Workspace:
            def _phase49_3i21_link_refresh(self):
                calls.extend(self.db.categories())
                return "ok"

        phase.install_workspace(Workspace)
        instance = Workspace()
        instance.db = SimpleNamespace()
        instance.app = SimpleNamespace(
            get_all_categories=lambda: [{"slug": "decor", "name": "دکور"}]
        )
        instance.product_id = 11

        self.assertEqual(instance._phase49_3i21_link_refresh(), "ok")
        self.assertEqual(calls, [{"slug": "decor", "name": "دکور"}])
        self.assertTrue(callable(instance.db.categories))

    def test_invalid_category_rows_are_ignored(self):
        workspace = SimpleNamespace(
            app=SimpleNamespace(
                get_all_categories=lambda: [
                    {"slug": "", "name": "بدون اسلاگ"},
                    {"slug": "valid", "name": "معتبر"},
                    object(),
                ]
            ),
            product_id=12,
        )
        self.assertEqual(
            phase.workspace_categories(workspace),
            [{"slug": "valid", "name": "معتبر"}],
        )


if __name__ == "__main__":
    unittest.main()
