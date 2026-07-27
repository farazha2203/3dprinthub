from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "store/migrations/0020_phase29_verified_pricing_source_lifecycle.py",
    "store/migrations/0022_phase29_source_kind_state_sync.py",
    "website/migrations/0016_phase29_billable_time_rounding.py",
    "store/pricing_authority.py",
    "store/manual_pricing.py",
    "store/operator_notifications.py",
    "store/source_lifecycle.py",
    "store/management/commands/phase29_pricing_seo_audit.py",
    "store/management/commands/phase29_test_operator_alert.py",
    "store/test_phase13.py",
    "store/test_phase14.py",
    "store/test_phase29.py",
    "templates/store/external_catalog_detail.html",
    "templates/store/external_link_analysis.html",
]

for relative in REQUIRED:
    path = ROOT / relative
    if not path.is_file():
        raise SystemExit(f"Missing Phase 29 file: {relative}")

for path in list((ROOT / "store").rglob("*.py")) + list((ROOT / "website").rglob("*.py")) + list((ROOT / "config").rglob("*.py")):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

link_code = (ROOT / "store/link_intelligence.py").read_text(encoding="utf-8")
required_fragments = [
    '"weight_source_kind"',
    '"print_time_source_kind"',
    'source_explicit',
    'operator_verified',
    'billable_print_minutes',
    'normalize_public_url',
]
for fragment in required_fragments:
    if fragment not in link_code:
        raise SystemExit(f"Missing verified-pricing fragment: {fragment}")
for forbidden in ['["duration", "estimatedTime", "materialUsage", "filamentUsage"]']:
    if forbidden in link_code:
        raise SystemExit(f"Unsafe generic pricing extraction remains: {forbidden}")

catalog_template = (ROOT / "templates/store/external_catalog_detail.html").read_text(encoding="utf-8")
analysis_template = (ROOT / "templates/store/external_link_analysis.html").read_text(encoding="utf-8")
for phrase in ["قیمت حدسی نمایش داده نمی‌شود", "زمان قابل محاسبه", "استعلام"]:
    if phrase not in catalog_template + analysis_template:
        raise SystemExit(f"Missing customer safety phrase: {phrase}")

for secret_name in ["TELEGRAM_OPERATOR_BOT_TOKEN", "WHATSAPP_CLOUD_TOKEN"]:
    value = ""
    env_path = ROOT / ".env.production.example"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith(secret_name + "="):
            value = line.split("=", 1)[1].strip()
    if value:
        raise SystemExit(f"Example environment contains a real-looking secret: {secret_name}")


legacy_cta_expected = "ورود برای استعلام و سفارش"
legacy_cta_deprecated = "ورود و سفارش چاپ این مدل"
for relative in ["store/test_phase13.py", "store/test_phase14.py"]:
    test_text = (ROOT / relative).read_text(encoding="utf-8")
    if legacy_cta_expected not in test_text:
        raise SystemExit(f"Updated catalog CTA expectation missing: {relative}")
    if legacy_cta_deprecated in test_text:
        raise SystemExit(f"Deprecated catalog CTA expectation remains: {relative}")

print(f"PHASE29_VERIFY=OK required_files={len(REQUIRED)}")
