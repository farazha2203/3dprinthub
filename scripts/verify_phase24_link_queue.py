from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "store/link_analysis_queue.py",
    "store/migrations/0017_phase24_async_link_analysis_queue.py",
    "store/management/commands/process_link_analysis_queue.py",
    "store/management/commands/phase24_link_queue_audit.py",
    "store/test_phase24.py",
    "static/css/phase24-link-queue.css",
    "static/js/phase24-link-queue.js",
    "templates/store/external_link_analysis.html",
]
PYTHON_FILES = [
    "store/models.py",
    "store/link_intelligence.py",
    "store/link_analysis_queue.py",
    "store/views.py",
    "store/urls.py",
    "store/admin.py",
    "store/test_phase23.py",
    "store/test_phase24.py",
    "store/management/commands/process_link_analysis_queue.py",
    "store/management/commands/phase24_link_queue_audit.py",
    "store/management/commands/run_phase10_automation.py",
    "store/migrations/0017_phase24_async_link_analysis_queue.py",
]
TEMPLATES = [
    "templates/store/base.html",
    "templates/store/external_link_analysis.html",
    "templates/store/customer_link_analyses.html",
]

errors: list[str] = []
for relative in REQUIRED:
    if not (ROOT / relative).is_file():
        errors.append(f"missing:{relative}")

for relative in PYTHON_FILES:
    path = ROOT / relative
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except Exception as exc:
        errors.append(f"python:{relative}:{exc}")

for relative in TEMPLATES:
    text = (ROOT / relative).read_text(encoding="utf-8")
    for opening, closing in (("{%", "%}"), ("{{", "}}"), ("{#", "#}")):
        if text.count(opening) != text.count(closing):
            errors.append(f"template:{relative}:{opening}")

checks = {
    "CustomerLinkAnalysisJob": "store/models.py",
    "CustomerLinkAnalysisAttempt": "store/models.py",
    "enqueue_link_analysis": "store/link_analysis_queue.py",
    "process_link_analysis_queue": "store/link_analysis_queue.py",
    "release_stale_link_analysis_jobs": "store/link_analysis_queue.py",
    "external_link_analysis_status": "store/urls.py",
    "data-link-job": "templates/store/external_link_analysis.html",
    "_assert_public_host": "store/test_phase23.py",
}
for token, relative in checks.items():
    if token not in (ROOT / relative).read_text(encoding="utf-8"):
        errors.append(f"token:{token}:{relative}")

queue_source = (ROOT / "store/link_analysis_queue.py").read_text(encoding="utf-8")
if "DEFAULT_RETRY_DELAYS" not in queue_source or "next_run_at" not in queue_source:
    errors.append("queue:retry/backoff missing")

public_template = (ROOT / "templates/store/external_link_analysis.html").read_text(encoding="utf-8")
if "analysis.file_links|join" in public_template or "private_download_url" in public_template:
    errors.append("privacy:private file links exposed")

for ps1 in ("APPLY_PHASE24.ps1", "PUBLISH_PHASE24_GITHUB.ps1", "RUN_PHASE24_WORKER.ps1"):
    path = ROOT / ps1
    if path.exists():
        try:
            path.read_text(encoding="ascii")
        except UnicodeDecodeError:
            errors.append(f"powershell:{ps1}:not-ascii")

if errors:
    print("PHASE24_VERIFY=FAILED")
    for error in errors:
        print(error)
    sys.exit(1)
print("PHASE24_VERIFY=OK")
print(f"required_files={len(REQUIRED)} python_files={len(PYTHON_FILES)} templates={len(TEMPLATES)}")
