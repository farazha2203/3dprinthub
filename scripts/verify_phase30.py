from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "website/payment_gateways/base.py",
    "website/payment_gateways/zarinpal.py",
    "website/payment_gateways/registry.py",
    "website/payment_services.py",
    "website/migrations/0017_phase30_online_payment_gateway.py",
    "website/test_phase30_online_payment.py",
    "website/test_phase30_zarinpal_provider.py",
    "website/management/commands/phase30_payment_audit.py",
    "docs/PHASE30_ONLINE_PAYMENT_GATEWAY_FA.md",
]
MARKERS = {
    "website/models.py": ["class PaymentLedgerEntry", "callback_token", "gateway_amount", "online_payment_enabled"],
    "website/views.py": ["quote_gateway_start_view", "quote_gateway_callback_view"],
    "website/urls.py": ["quote_gateway_start", "quote_gateway_callback"],
    "templates/website/quote_detail.html": ["ادامه و ورود به درگاه پرداخت", "ادامه پرداخت قبلی"],
    "config/settings.py": ["PAYMENT_GATEWAY_ENABLED", "ZARINPAL_MERCHANT_ID", "ZARINPAL_CURRENCY"],
}

errors = []
for rel in REQUIRED:
    if not (ROOT / rel).is_file():
        errors.append(f"missing:{rel}")
for rel, needles in MARKERS.items():
    path = ROOT / rel
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    for needle in needles:
        if needle not in text:
            errors.append(f"marker:{rel}:{needle}")
for path in [
    ROOT / "website/models.py",
    ROOT / "website/views.py",
    ROOT / "website/forms.py",
    ROOT / "website/payment_services.py",
    ROOT / "website/payment_gateways/base.py",
    ROOT / "website/payment_gateways/zarinpal.py",
    ROOT / "website/payment_gateways/registry.py",
    ROOT / "website/migrations/0017_phase30_online_payment_gateway.py",
]:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except Exception as exc:
        errors.append(f"syntax:{path.relative_to(ROOT)}:{exc}")

migration_text = (ROOT / "website/migrations/0017_phase30_online_payment_gateway.py").read_text(encoding="utf-8")
for dangerous in ["RunPython", "DeleteModel", "RemoveField"]:
    if dangerous in migration_text:
        errors.append(f"dangerous_migration_operation:{dangerous}")

result = {"phase": "30", "required_files": len(REQUIRED), "errors": errors}
print(json.dumps(result, ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)
print(f"PHASE30_VERIFY=OK required_files={len(REQUIRED)}")
