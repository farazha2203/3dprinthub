from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
required = [
    root / "store/migrations/0025_phase35_catalog_editor.py",
    root / "store/phase35_catalog_editor.py",
    root / "store/phase34b_publishing.py",
    root / "website/migrations/0017_phase30_online_payment_gateway.py",
    root / "static/admin/phase35-admin.css",
    root / "templates/admin/base.html",
]
missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
if missing:
    print("PHASE38_HOST_BASELINE_MISSING")
    for item in missing:
        print(item)
    raise SystemExit(1)

store_admin = (root / "store/admin.py").read_text(encoding="utf-8")
checks = {
    "phase35 thumbnail": '"preview_thumbnail"' in store_admin,
    "phase35 source link": 'source_title_admin' in store_admin,
    "phase35 price final": '"price_is_final"' in store_admin,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    print("PHASE38_HOST_BASELINE_CONTRACT_FAILED")
    for name in failed:
        print(name)
    raise SystemExit(1)
print("PHASE38_HOST_BASELINE=OK")
