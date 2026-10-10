"""Offline safety-contract checks for the A2W Home Hero text hotfix."""

from pathlib import Path
import unittest


RUNNER = Path(__file__).with_name("phase50_a2w_home_hero_comment_hotfix_deploy.sh")


class A2WHomeHeroCommentDeployTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = RUNNER.read_text(encoding="utf-8")

    def test_pins_current_live_host_and_approved_release(self):
        self.assertIn('BASE="5a1a6ea08abf6400661fbeb80dec03446500e158"', self.source)
        self.assertIn('HOST_BRANCH="release/phase50-a2j-hero-20260915"', self.source)
        self.assertIn('RELEASE_BRANCH="release/phase50-a2w-service-seo-20261010"', self.source)
        self.assertIn('git ls-remote origin "refs/heads/$RELEASE_BRANCH"', self.source)
        self.assertIn('git merge --ff-only "$FETCHED"', self.source)

    def test_allows_only_home_hero_template_test_and_phase_closure(self):
        allowlist = self.source.split('case "$changed" in', 1)[1].split('esac', 1)[0]
        self.assertIn("templates/website/partials/hero.html", allowlist)
        self.assertIn("website/test_phase50_a2k_tympanus_slicebox.py", allowlist)
        self.assertIn("scripts/host/phase50_a2w_home_hero_comment_hotfix_deploy.sh", allowlist)
        self.assertIn("docs/PATHS.md", allowlist)
        self.assertIn("docs/phases/PHASE50_A2V_ISFAHAN_SEO_RELEASE.md", allowlist)
        self.assertIn('*) fail "unexpected_release_file:$changed" ;;', allowlist)
        self.assertIn("migration_dependency_settings_or_env_delta", self.source)

    def test_integrity_checked_full_rollback_precedes_merge(self):
        backup = self.source.index("PREDEPLOY_SOURCE_ENV_DATABASE_BACKUP=PASS")
        promotion = self.source.index('git merge --ff-only "$FETCHED"')
        self.assertLess(backup, promotion)
        self.assertIn('gzip -t "$BACKUP/database-before-3i53.sql.gz"', self.source)
        self.assertIn('sha256sum -c "$BACKUP/rollback-source.sha256"', self.source)
        self.assertIn("reserve 48", self.source)
        self.assertIn("reserve 32", self.source)

    def test_public_smoke_rejects_comment_and_preserves_slide_image_parity(self):
        self.assertIn("HOME_HERO_COMMENT_STILL_VISIBLE", self.source)
        self.assertIn("len(slides) != len(images)", self.source)
        self.assertIn("PUBLIC_HOME_HERO_SMOKE=PASS", self.source)


if __name__ == "__main__":
    unittest.main()
