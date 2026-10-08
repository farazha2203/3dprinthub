"""Offline bounded regression for the Phase50.A2U Host deploy safety gates."""
import contextlib
import io
from pathlib import Path
import re
import sys
from types import SimpleNamespace
from unittest.mock import patch

script = Path(__file__).with_name("phase50_a2u_seo_category_deploy.sh").read_text(encoding="utf-8")
blocks = re.findall(r"<<'PY'\n(.*?)\nPY", script, re.S)
assert len(blocks) == 2, "Only quota-readback and MySQL preflight embedded Python expected"
for i, block in enumerate(blocks):
    compile(block, f"embedded-a2u-{i}", "exec")
quota = blocks[0]
fake = """---
result:
  data:
    -
      _count: '1996'
      _max: '2000'
      percent: 100
"""
with patch("subprocess.run", return_value=SimpleNamespace(stdout=fake)), \
     contextlib.redirect_stdout(io.StringIO()) as output:
    exec(compile(quota, "readback", "exec"), {"__name__": "__main__"})
assert "CPANEL_REPORTED_MB=1996/2000" in output.getvalue()
for bad in ("garbled", fake.replace("2000", "3000")):
    with patch("subprocess.run", return_value=SimpleNamespace(stdout=bad)), \
         contextlib.redirect_stdout(io.StringIO()):
        try:
            exec(compile(quota, "readback", "exec"), {"__name__": "__main__"})
        except AssertionError:
            pass
        else:
            raise AssertionError("Quota identity must fail closed on unknown cap")

for token in (
    "test -z \"$(git status --porcelain --untracked-files=all)\"",
    'git merge --ff-only "$FETCHED"',
    'git merge-base --is-ancestor "$BASE" "$FETCHED"',
    'git diff --name-only "$BASE" "$FETCHED"',
    'reserve 48', 'reserve 32',
    'conv=fsync', 'trap ', 'FRESH_SCOPED_SOURCE_ENV_FULL_MYSQL_ROLLBACK=PASS',
    'gzip -t "$BACKUP/database-before-3i53.sql.gz"',
    'sha256sum -c source.sha256 database.sha256',
    'templates/store/product_list.html',
    'MYSQL_IDENTITY_EMPTY_MIGRATION_PLAN=PASS',
    'PHASE50_A2U_DEPLOY_CODE=PASS',
):
    assert token in script, f"Missing deployment contract: {token}"
assert script.index('echo "FRESH_SCOPED_SOURCE_ENV_FULL_MYSQL_ROLLBACK=PASS"') < \
       script.index('git merge --ff-only "$FETCHED"')
assert "rm -rf" not in script and "migrate --noinput" not in script
print("PHASE50_A2U_GUARDED_RUNNER_SELFTEST=PASS")
