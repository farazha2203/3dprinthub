from __future__ import annotations

import unittest

from app import phase49_3i26_operator_completion as phase26
from app import phase49_3i27_category_provider_bridge as phase28


class _App:
    def get_all_categories(self):
        return [
            {"slug": "decor", "name": "دکور"},
            {"slug": "cake-stand", "name": "استند کیک"},
        ]


class _Workspace:
    app = _App()
    product_id = 1


class Phase493I28ExactLinkContractTests(unittest.TestCase):
    def test_category_provider_uses_app_boundary(self):
        rows = phase28.workspace_categories(_Workspace())
        self.assertEqual([row["slug"] for row in rows], ["decor", "cake-stand"])

    def test_canonical_title_compat_matches_v19_signature(self):
        original = phase26.canonical_source_title
        try:
            class DummyWorkspace:
                _phase49_3i21_link_refresh = staticmethod(lambda self: None)

            phase28.install_workspace(DummyWorkspace)
            title = phase26.canonical_source_title(
                "https://makerworld.com/en/models/2650242-cake-stand",
                "2650242",
                candidates=["Cake Stand"],
                current_title="MakerWorld model 2650242",
            )
            self.assertEqual(title, "Cake Stand")
        finally:
            phase26.canonical_source_title = original


if __name__ == "__main__":
    unittest.main()
