#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-sync", required=True)
    parser.add_argument("--tests", required=True)
    args = parser.parse_args()

    sync_path = Path(args.catalog_sync).resolve()
    tests_path = Path(args.tests).resolve()
    sync_text = sync_path.read_text(encoding="utf-8-sig")
    tests_text = tests_path.read_text(encoding="utf-8-sig")

    ast.parse(sync_text, filename=str(sync_path))
    ast.parse(tests_text, filename=str(tests_path))

    forbidden = 'run.refresh_from_db(fields=["status", "cancelled_at"])'
    if forbidden in sync_text:
        print("STOP: status-overwriting refresh_from_db is still present.", file=sys.stderr)
        return 20

    required = [
        "persisted_state = CatalogSyncRun.objects.filter(pk=run.pk).values(",
        'persisted_state["status"] == "cancelled"',
        "test_partial_sync_status_is_not_overwritten_by_persisted_running_state",
    ]
    combined = sync_text + "\n" + tests_text
    for pattern in required:
        if pattern not in combined:
            print(f"STOP: required regression pattern missing: {pattern}", file=sys.stderr)
            return 21

    print("PHASE33_SYNC_FINALIZATION_REGRESSION=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
