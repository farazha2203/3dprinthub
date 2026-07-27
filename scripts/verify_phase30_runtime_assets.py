from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "static/velzon_master/js/layout.js",
    "static/velzon_master/css/bootstrap-rtl.min.css",
    "static/velzon_master/css/icons-rtl.min.css",
    "static/velzon_master/css/app-rtl.min.css",
    "static/velzon_master/css/custom-rtl.min.css",
    "static/velzon_master/libs/bootstrap/dist/js/bootstrap.bundle.min.js",
    "static/velzon_master/libs/simplebar/dist/simplebar.min.js",
    "static/velzon_master/libs/node-waves/dist/waves.min.js",
    "static/velzon_master/libs/feather-icons/dist/feather.min.js",
    "static/velzon_master/js/pages/plugins/lord-icon-2.1.0.js",
    "static/velzon_master/libs/choices.js/public/assets/styles/choices.min.css",
    "static/velzon_master/libs/choices.js/public/assets/scripts/choices.min.js",
    "static/velzon_master/libs/flatpickr/dist/flatpickr.min.css",
    "static/velzon_master/libs/flatpickr/dist/flatpickr.min.js",
    "static/velzon_master/libs/flatpickr/dist/l10n/fa.js",
    "static/velzon_master/images/sidebar/img-1.jpg",
    "static/velzon_master/images/sidebar/img-2.jpg",
    "static/velzon_master/images/sidebar/img-3.jpg",
    "static/velzon_master/images/sidebar/img-4.jpg",
)

missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
print(f"required_runtime_assets: {len(REQUIRED)}")
print(f"missing_runtime_assets: {len(missing)}")
for path in missing:
    print(f"MISSING: {path}")
if missing:
    print("PHASE30_RUNTIME_ASSETS=FAILED")
    raise SystemExit(1)
print("PHASE30_RUNTIME_ASSETS=OK")
