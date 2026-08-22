from __future__ import annotations

import unittest

from app import phase49_3i_discovery_review as discovery_review
from app.phase49_3i_preview_recovery import (
    PREVIEW_CARD_EVAL_JS,
    discover_preview_candidates_safe,
    install,
)


class Phase493IPreviewRecoveryTests(unittest.TestCase):
    def test_javascript_keeps_backslash_n_instead_of_literal_newline_inside_quote(self):
        self.assertIn("+ '\\n' +", PREVIEW_CARD_EVAL_JS)
        self.assertNotIn("+ '\n' +", PREVIEW_CARD_EVAL_JS)
        self.assertIn("els => els.map", PREVIEW_CARD_EVAL_JS)
        self.assertIn("a[href]", 'a[href]')

    def test_install_replaces_only_preview_candidate_boundary(self):
        original = discovery_review.discover_preview_candidates
        old_marker = getattr(discovery_review, "_phase49_3i_preview_recovery_installed", False)
        try:
            discovery_review._phase49_3i_preview_recovery_installed = False
            install()
            self.assertIs(
                discovery_review.discover_preview_candidates,
                discover_preview_candidates_safe,
            )
        finally:
            discovery_review.discover_preview_candidates = original
            discovery_review._phase49_3i_preview_recovery_installed = old_marker

    def test_hotfix_does_not_call_full_product_fetch(self):
        from pathlib import Path

        source = (
            Path(__file__).resolve().parents[1]
            / "app"
            / "phase49_3i_preview_recovery.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("collect_classic_exact(", source)
        self.assertNotIn("extract_direct_link(", source)
        self.assertNotIn("download_public_file(", source)
        self.assertIn("candidates_from_dom_rows", source)


if __name__ == "__main__":
    unittest.main()
