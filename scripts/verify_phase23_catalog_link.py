from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "store/link_intelligence.py",
    "store/migrations/0016_phase23_catalog_link_intelligence.py",
    "store/management/commands/process_catalog_refresh_requests.py",
    "store/management/commands/phase23_catalog_link_audit.py",
    "templates/store/external_catalog.html",
    "templates/store/external_catalog_detail.html",
    "templates/store/external_link_analyzer.html",
    "templates/store/external_link_analysis.html",
    "templates/store/customer_link_analyses.html",
    "static/css/phase23-catalog-link.css",
]
PYTHON_FILES = [
    "store/models.py",
    "store/catalog_sync.py",
    "store/catalog_automation.py",
    "store/presentation.py",
    "store/link_intelligence.py",
    "store/forms.py",
    "store/views.py",
    "store/urls.py",
    "store/admin.py",
    "store/sitemaps.py",
    "website/models.py",
    "store/test_phase23.py",
    "store/migrations/0016_phase23_catalog_link_intelligence.py",
]
TEMPLATES = [
    "templates/store/external_catalog.html",
    "templates/store/external_catalog_detail.html",
    "templates/store/external_link_analyzer.html",
    "templates/store/external_link_analysis.html",
    "templates/store/customer_link_analyses.html",
    "templates/website/customer/account_base.html",
    "templates/website/partials/hero.html",
    "templates/website/partials/external-models-home.html",
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

public_templates = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in TEMPLATES)
if "private_download_url" in public_templates:
    errors.append("privacy:private_download_url exposed in a public template")
if "analysis.file_links|join" in public_templates:
    errors.append("privacy:file link values exposed in analysis template")

checks = {
    "public_reference_enabled": "store/models.py",
    "CatalogRefreshRequest": "store/models.py",
    "CustomerLinkAnalysis": "store/models.py",
    "external_link_analyzer": "store/urls.py",
    "customer_link_analyses": "store/urls.py",
    "normalize_public_url": "store/link_intelligence.py",
    "minimum_order_adjustment": "store/link_intelligence.py",
}
for token, relative in checks.items():
    if token not in (ROOT / relative).read_text(encoding="utf-8"):
        errors.append(f"token:{token}:{relative}")

if errors:
    print("PHASE23_VERIFY=FAILED")
    for error in errors:
        print(error)
    sys.exit(1)
print("PHASE23_VERIFY=OK")
print(f"required_files={len(REQUIRED)} python_files={len(PYTHON_FILES)} templates={len(TEMPLATES)}")
