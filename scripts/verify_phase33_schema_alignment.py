#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


EXPECTED = {
    ("ImportedPrintAsset", "source_url"): {
        "call": "URLField",
        "max_length": 1000,
    },
    ("CatalogSeedURL", "url"): {
        "call": "URLField",
        "max_length": 1200,
    },
    ("CustomerLinkAnalysis", "normalized_url"): {
        "call": "URLField",
        "max_length": 2000,
        "db_index": True,
    },
}


def call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def literal_keyword(call: ast.Call, name: str):
    for keyword in call.keywords:
        if keyword.arg == name:
            return ast.literal_eval(keyword.value)
    return None


def find_field(tree: ast.Module, class_name: str, field_name: str) -> ast.Call:
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for statement in node.body:
            if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
                continue
            target = statement.targets[0]
            if isinstance(target, ast.Name) and target.id == field_name:
                if not isinstance(statement.value, ast.Call):
                    raise RuntimeError(
                        f"{class_name}.{field_name} is not a field call"
                    )
                return statement.value
        raise RuntimeError(f"Field not found: {class_name}.{field_name}")
    raise RuntimeError(f"Class not found: {class_name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", required=True)
    args = parser.parse_args()

    path = Path(args.models).expanduser().resolve()
    if not path.is_file():
        print(f"STOP: models file not found: {path}", file=sys.stderr)
        return 20

    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))

    for (class_name, field_name), expected in EXPECTED.items():
        call = find_field(tree, class_name, field_name)
        actual_call = call_name(call.func)
        if actual_call != expected["call"]:
            print(
                f"STOP: {class_name}.{field_name} uses {actual_call}, "
                f"expected {expected['call']}",
                file=sys.stderr,
            )
            return 21

        actual_max_length = literal_keyword(call, "max_length")
        if actual_max_length != expected["max_length"]:
            print(
                f"STOP: {class_name}.{field_name} max_length="
                f"{actual_max_length}, expected {expected['max_length']}",
                file=sys.stderr,
            )
            return 22

        if "db_index" in expected:
            actual_db_index = literal_keyword(call, "db_index")
            if actual_db_index is not expected["db_index"]:
                print(
                    f"STOP: {class_name}.{field_name} db_index="
                    f"{actual_db_index}, expected {expected['db_index']}",
                    file=sys.stderr,
                )
                return 23

        print(
            f"SCHEMA_FIELD_OK class={class_name} field={field_name} "
            f"max_length={expected['max_length']}"
        )

    print("PHASE33_SCHEMA_ALIGNMENT=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
