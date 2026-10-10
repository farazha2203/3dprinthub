from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "host" / "phase50_a2v_isfahan_seo_deploy.sh"


class Phase50A2VDeployRunnerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = RUNNER.read_text(encoding="utf-8")

    def test_exact_host_and_target_lineage_are_pinned(self):
        self.assertIn('HOST_BRANCH="release/phase50-a2j-hero-20260915"', self.source)
        self.assertIn('TARGET_BRANCH="release/phase50-a2v-isfahan-seo-20261010"', self.source)
        self.assertIn('BASE="0277018726cf02e565ba83eb724cfbf8acc523fb"', self.source)

    def test_backup_and_real_quota_gates_precede_fast_forward(self):
        self.assertLess(self.source.index("reserve 48"), self.source.index("git fetch"))
        self.assertLess(self.source.index("PREDEPLOY_SOURCE_ENV_DATABASE_BACKUP=PASS"), self.source.index("git merge --ff-only"))
        self.assertIn("gzip -t", self.source)
        self.assertIn("sha256sum -c", self.source)

    def test_production_delta_rejects_migrations_and_unknown_files(self):
        self.assertIn("unexpected_release_file", self.source)
        self.assertIn("migration_dependency_settings_or_env_delta", self.source)
        self.assertIn("MIGRATION_PLAN_NOT_EMPTY", self.source)

    def test_rollout_finishes_with_exact_sha_and_public_smoke(self):
        self.assertIn('test "$(git rev-parse HEAD)" = "$TARGET"', self.source)
        self.assertIn("phase50_a2v_public_smoke.py", self.source)
        self.assertIn("PHASE50_A2V_DEPLOY=PASS", self.source)

    def test_guarded_rollback_is_written_and_verified_before_fast_forward(self):
        self.assertIn('cat > "$BACKUP/rollback-source.sh"', self.source)
        self.assertIn('git reset --hard "$BASE"', self.source)
        self.assertIn('sha256sum -c "$BACKUP/rollback-source.sha256"', self.source)
        self.assertLess(self.source.index('echo "SOURCE_ROLLBACK_SCRIPT='), self.source.index('git merge --ff-only'))


if __name__ == "__main__":
    unittest.main()
