#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))

for relative, expected in manifest["files"].items():
    path = root / relative
    if not path.is_file():
        raise SystemExit(f"MISSING: {relative}")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"HASH_MISMATCH: {relative}")

compile((root / "server" / "phase43_catalog_metrics_datafix.py").read_text(encoding="utf-8"),
        "phase43_catalog_metrics_datafix.py", "exec")
print("PACKAGE_VERSION=" + manifest["version"])
print("PACKAGE_VERIFY=OK")
