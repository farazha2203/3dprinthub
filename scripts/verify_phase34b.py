#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
from pathlib import Path

REQUIRED = [
    "store/makerworld_next_data.py",
    "store/phase34b_translation.py",
    "store/phase34b_publishing.py",
    "store/test_phase34b.py",
    "store/migrations/0024_phase34b_makerworld_editorial_commerce.py",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    for rel in REQUIRED:
        path = root / rel
        if not path.is_file():
            raise SystemExit(f"STOP: missing file: {rel}")
        if path.suffix == ".py":
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    models = (root / "store/models.py").read_text(encoding="utf-8")
    for marker in [
        "commercial_license_status",
        "fixed_print_price",
        "persian_title",
        "portfolio_item",
        "order_mode",
        "consultation_required",
    ]:
        if marker not in models:
            raise SystemExit(f"STOP: model marker missing: {marker}")
    print("PHASE34B_FILES=OK")
    print("PHASE34B_MODEL_MARKERS=OK")
    print("PHASE34B_VERIFY=OK")


if __name__ == "__main__":
    main()
