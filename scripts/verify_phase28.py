from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "store/test_phase28.py",
    "store/test_phase24.py",
    "website/test_phase28_payment.py",
    "website/migrations/0015_phase28_quote_deposit_payment.py",
    "store/management/commands/phase28_conversion_audit.py",
    "website/management/commands/test_smtp_delivery.py",
    "store/templatetags/store_consultation.py",
    "templates/store/external_link_analysis.html",
    "templates/website/quote_detail.html",
    "APPLY_PHASE28.ps1",
    "docs/PHASE28_AUTH_CONVERSION_SERVER_DEPLOYMENT_FA.md",
]

for relative in REQUIRED:
    path = ROOT / relative
    if not path.exists():
        raise SystemExit(f"Missing required Phase 28 file: {relative}")

for path in [
    ROOT / "store/views.py",
    ROOT / "store/link_intelligence.py",
    ROOT / "store/realtime.py",
    ROOT / "website/views.py",
    ROOT / "website/models.py",
    ROOT / "config/settings.py",
]:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


phase24_tests = (ROOT / "store/test_phase24.py").read_text(encoding="utf-8")
for marker in [
    "test_anonymous_submit_redirects_to_login_without_creating_analysis",
    "test_authenticated_submit_queues_without_running_remote_fetch_in_request",
    "self.client.force_login(self.user)",
]:
    if marker not in phase24_tests:
        raise SystemExit(f"Phase 24 submission regression test is stale: {marker}")

store_views = (ROOT / "store/views.py").read_text(encoding="utf-8")
if "@login_required\ndef external_link_analyzer" not in store_views:
    raise SystemExit("Link analyzer is not protected by login_required.")
for marker in ["action == \"manual_quote\"", "create_manual_quote_request_from_analysis"]:
    if marker not in store_views:
        raise SystemExit(f"Missing manual quote flow marker: {marker}")

settings_text = (ROOT / "config/settings.py").read_text(encoding="utf-8")
for marker in ["REALTIME_REDIS_AUTO_FALLBACK", "REALTIME_ALLOW_POLLING_ONLY", "REALTIME_BACKEND_MODE"]:
    if marker not in settings_text:
        raise SystemExit(f"Missing realtime fallback marker: {marker}")

for relative in [
    "templates/store/external_catalog.html",
    "templates/store/external_catalog_detail.html",
    "templates/store/external_link_analysis.html",
    "templates/store/product_list.html",
    "templates/store/product_detail.html",
    "templates/website/partials/hero.html",
]:
    text = (ROOT / relative).read_text(encoding="utf-8")
    if "consultation_links" not in text:
        raise SystemExit(f"Consultation links missing from {relative}")

analysis_template = (ROOT / "templates/store/external_link_analysis.html").read_text(encoding="utf-8")
if "analysis.file_links|length" not in analysis_template:
    raise SystemExit("Private link references must only be displayed as a count.")
import re
if re.search(r"{%\s*for\s+\w+\s+in\s+analysis\.file_links", analysis_template):
    raise SystemExit("Private file links appear to be iterated in the customer template.")

print("Phase 28 structural verification passed.")
