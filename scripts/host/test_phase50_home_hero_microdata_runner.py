"""Offline, no Host calls: verify embedded deploy Python and quota gates."""
import contextlib
import io
from pathlib import Path
import re
import sys
from types import SimpleNamespace
from unittest.mock import patch

script = Path(__file__).with_name("phase50_home_hero_microdata_deploy.sh").read_text(encoding="utf-8")
blocks = re.findall(r"<<'PY'\n(.*?)\nPY", script, re.S)
assert len(blocks) == 3, "quota, database, public HTML Python heredocs expected"
for i, block in enumerate(blocks):
    compile(block, f"runner:embedded:{i}", "exec")

fixture = """---
result:
  data:
    -
      _count: '1994'
      _max: '2000'
      units: MB
"""

def exercise_quota(text, needed):
    with patch("subprocess.run", return_value=SimpleNamespace(stdout=text)), \
         patch.object(sys, "argv", ["quota", str(needed)]), \
         contextlib.redirect_stdout(io.StringIO()):
        exec(compile(blocks[0], "quota", "exec"), {"__name__": "__main__"})

exercise_quota(fixture, 6)
try:
    exercise_quota(fixture, 7)
except SystemExit as e:
    assert str(e) == "HOST_QUOTA_BELOW_SCOPED_BACKUP_RESERVE"
else:
    raise AssertionError("must reject low quota")

try:
    exercise_quota("bad quota", 6)
except SystemExit as e:
    assert str(e) == "HOST_ACCOUNT_QUOTA_UNVERIFIED"
else:
    raise AssertionError("must reject unknown quota")

assert "HOMEPAGE_6_INVALID_PRODUCTS_REMOVED=PASS" in blocks[-1]
assert 'itemtype="https://schema.org/Product"' in blocks[-1]
assert "SIX_STORE_PRODUCT_OFFERS_PRESERVED=PASS" in blocks[-1]
assert "FRESH_SCOPED_SOURCE_ENV_FULL_DB_ROLLBACK=PASS" in script
print("HERO_MICRODATA_RUNNER_SELFTEST=PASS")
