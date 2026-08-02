#!/usr/bin/env python3
from __future__ import annotations

import ast
import sys
from pathlib import Path

TARGETS = {
    "refresh_variant_prices_for_material",
    "refresh_all_variant_prices",
    "assign_affiliate_partner_to_order",
    "reverse_affiliate_on_refund",
    "phase8_custom_order_production_job",
    "phase29_sync_verified_catalog_pricing",
    "phase29_ensure_catalog_pricing_queue",
    "phase29_enforce_source_state",
    "phase29_enforce_policy_state",
}


def is_raw_guard(node: ast.If) -> bool:
    test = node.test
    if not isinstance(test, ast.Call):
        return False
    if not isinstance(test.func, ast.Attribute):
        return False
    if test.func.attr != "get":
        return False
    if not isinstance(test.func.value, ast.Name) or test.func.value.id != "kwargs":
        return False
    if not test.args:
        return False
    arg = test.args[0]
    return isinstance(arg, ast.Constant) and arg.value == "raw"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "store" / "signals.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    failures = []
    for name in sorted(TARGETS):
        function = functions.get(name)
        if function is None:
            failures.append(f"missing_function={name}")
            continue
        if not any(isinstance(node, ast.If) and is_raw_guard(node) for node in function.body[:3]):
            failures.append(f"missing_raw_guard={name}")
    if failures:
        for item in failures:
            print(item)
        print("PHASE32_SIGNAL_GUARD_VERIFY=FAILED")
        return 1
    print(f"SIGNAL_GUARD_FUNCTION_COUNT={len(TARGETS)}")
    print("PHASE32_SIGNAL_GUARD_VERIFY=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
