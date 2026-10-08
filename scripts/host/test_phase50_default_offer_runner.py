"""Offline regression for guarded 3DPrintHub Google default-offer deploy runner.

Never invokes uapi, SSH, Git fetch, backups or Production; mocks quota source.
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path
import re
from types import SimpleNamespace
from unittest.mock import patch
import sys

RUNNER = Path(__file__).with_name("phase50_default_offer_deploy.sh")
SOURCE = RUNNER.read_text(encoding="utf-8")
BLOCKS = re.findall(r"<<'PY'\n(.*?)\nPY", SOURCE, re.S)
assert len(BLOCKS) == 3, "Expected quota + DB + live smoke Python heredocs"
for index, block in enumerate(BLOCKS):
    compile(block, f"{RUNNER.name}:block-{index}", "exec")

quota = BLOCKS[0]
sample = """---
result:
  data:
    -
      _count: '1977'
      _max: '2000'
      percent: 99
      units: MB
"""

def quota_check(minimum, stats=sample):
    capture = io.StringIO()
    with patch("subprocess.run", return_value=SimpleNamespace(stdout=stats)), \
         patch.object(sys, "argv", ["preflight", str(minimum)]), \
         contextlib.redirect_stdout(capture):
        exec(compile(quota, "cPanel quota script", "exec"), {"__name__": "__main__"})
    return capture.getvalue()

assert "CPANEL_QUOTA_FREE_MB=23 REQUIRED_MB=22" in quota_check(22)
try:
    quota_check(24)
except SystemExit as error:
    assert str(error) == "CPANEL_QUOTA_INSUFFICIENT_FOR_PROTECTED_ROLLBACK"
else:
    raise AssertionError("Quota below reserve must fail closed")

try:
    quota_check(22, "malformed-statistics")
except SystemExit as error:
    assert str(error) == "CPANEL_QUOTA_UNVERIFIED"
else:
    raise AssertionError("Unknown cPanel quota must fail closed")

smoke = BLOCKS[-1]
assert 'data-default-variant-id="([0-9]+)"' in smoke
assert 'data-total="([0-9]+)"' in smoke
assert 'first_google_offer_differs_from_client_price' in smoke
print("DEFAULT_OFFER_RUNNER_PARSER_SELFTEST=PASS")
