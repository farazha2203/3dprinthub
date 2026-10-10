"""Offline contract checks for the fail-closed A2W Host runner."""

from pathlib import Path
import re
import unittest


RUNNER = Path(__file__).with_name("phase50_a2w_service_seo_deploy.sh")


class A2WDeployRunnerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = RUNNER.read_text(encoding="utf-8")

    def test_exact_host_baseline_and_release_branch_are_pinned(self):
        self.assertIn('INITIAL_BASE="06f37f75cf01c1de3ddfeb06aafe97536f69d5b8"', self.source)
        self.assertIn('BASE="${2:-$INITIAL_BASE}"', self.source)
        self.assertIn('[[ "$BASE" =~ ^[0-9a-f]{40}$ ]] || fail expected_base_sha_invalid', self.source)
        self.assertIn('RELEASE_BRANCH="release/phase50-a2w-service-seo-20261010"', self.source)
        self.assertIn('git ls-remote origin "refs/heads/$RELEASE_BRANCH"', self.source)
        self.assertIn('git merge --ff-only "$FETCHED"', self.source)

    def test_strict_allowlist_and_required_runtime_surfaces(self):
        paths = re.findall(r"\|?(store/[A-Za-z0-9_./-]+|templates/[A-Za-z0-9_./-]+|scripts/[A-Za-z0-9_./-]+|docs/[A-Za-z0-9_./-]+)\|?", self.source)
        self.assertIn("store/phase50_service_seo.py", paths)
        self.assertIn("templates/store/service_landing.html", paths)
        self.assertIn("scripts/seo/phase50_a2w_service_seo_smoke.py", paths)
        self.assertIn("scripts/host/test_phase50_a2w_deploy_runner.py", paths)
        self.assertIn("docs/phases/PHASE50_A2X_STUDIO_PROP_DISCOVERY.md", paths)
        self.assertIn("docs/phases/PHASE50_A2Y_SERVICE_VERTICAL_LANDINGS.md", paths)
        required = re.search(r"for required in (.+?); do", self.source).group(1).split()
        self.assertNotIn("store/templatetags/store_seo.py", required)

    def test_successor_runner_requires_only_its_smoke_and_guard_files(self):
        self.assertIn('REQUIRED_DELTA=(scripts/host/phase50_a2w_service_seo_deploy.sh scripts/host/test_phase50_a2w_deploy_runner.py scripts/seo/phase50_a2w_service_seo_smoke.py docs/phases/PHASE50_A2Y_SERVICE_VERTICAL_LANDINGS.md)', self.source)

    def test_public_smoke_covers_all_eight_service_routes_and_exact_rare_part_titles(self):
        smoke = (RUNNER.parent.parent / "seo" / "phase50_a2w_service_seo_smoke.py").read_text(encoding="utf-8")
        self.assertIn('"/store/services/rare-car-part-reconstruction/": ("قطعه", "خودرو")', smoke)
        self.assertIn('"/store/services/rare-motorcycle-part-reconstruction/": ("قطعه", "موتورسیکلت")', smoke)
        self.assertEqual(smoke.count('"/store/services/'), 8)
        self.assertIn('*) fail "unexpected_release_file:$changed" ;;', self.source)

    def test_forbids_migration_dependency_settings_and_secret_deltas(self):
        self.assertIn("migration_dependency_settings_or_env_delta", self.source)
        self.assertIn("migration_plan", self.source)
        self.assertNotIn('manage.py migrate ', self.source)
        self.assertIn("collectstatic --noinput", self.source)

    def test_full_database_env_and_source_rollback_are_required_before_merge(self):
        backup = self.source.index("PREDEPLOY_SOURCE_ENV_DATABASE_BACKUP=PASS")
        promotion = self.source.index('git merge --ff-only "$FETCHED"')
        self.assertLess(backup, promotion)
        self.assertIn("gzip -t", self.source)
        self.assertIn('sha256sum -c "$BACKUP/rollback-source.sha256"', self.source)
        self.assertIn('reserve 48', self.source)
        self.assertIn('reserve 32', self.source)


if __name__ == "__main__":
    unittest.main()
