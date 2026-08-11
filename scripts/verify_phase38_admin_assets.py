from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
required = [
    root / "static/velzon_master/css/bootstrap-rtl.min.css",
    root / "static/velzon_master/css/app-rtl.min.css",
    root / "static/velzon_master/js/layout.js",
    root / "static/velzon_master/libs/bootstrap/dist/js/bootstrap.bundle.min.js",
    root / "static/fonts/iransans/IRANSansWeb_FaNum.woff",
    root / "static/fonts/iransans/IRANSansWeb_FaNum_Bold.woff",
]
missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
if missing:
    print("PHASE38_ADMIN_ASSETS_MISSING")
    for item in missing:
        print(item)
    raise SystemExit(1)
print("PHASE38_ADMIN_ASSETS=OK")
