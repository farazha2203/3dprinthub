from __future__ import annotations

import argparse
from pathlib import Path

STATE_SYNC = "0020_phase27_2_state_sync"
PHASE29 = "0020_phase29_verified_pricing_source_lifecycle"
MERGE = "0021_merge_phase27_2_phase29"


def _merge_content() -> str:
    return f'''from django.db import migrations\n\n\nclass Migration(migrations.Migration):\n    dependencies = [\n        ("store", "{STATE_SYNC}"),\n        ("store", "{PHASE29}"),\n    ]\n\n    operations = []\n'''


def ensure_merge(project_root: Path) -> int:
    migrations_dir = project_root / "store" / "migrations"
    state_sync_path = migrations_dir / f"{STATE_SYNC}.py"
    phase29_path = migrations_dir / f"{PHASE29}.py"
    merge_path = migrations_dir / f"{MERGE}.py"

    if not migrations_dir.is_dir():
        raise SystemExit(f"Store migrations directory not found: {migrations_dir}")
    if not phase29_path.is_file():
        raise SystemExit(f"Phase 29 migration not found: {phase29_path}")

    if not state_sync_path.is_file():
        if merge_path.exists():
            merge_path.unlink()
            print(f"Removed stale merge migration: {merge_path.name}")
        print("Phase 27.2 state-sync migration is absent; no merge migration is needed.")
        return 0

    expected = _merge_content()
    if merge_path.exists() and merge_path.read_text(encoding="utf-8") == expected:
        print(f"Migration merge already valid: {merge_path.name}")
        return 0

    merge_path.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Created migration merge: {merge_path.name}")
    print(f"Merged leaves: {STATE_SYNC}, {PHASE29}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create the Phase 29 merge migration only when the Phase 27.2 generated state-sync branch exists."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root containing manage.py and store/migrations.",
    )
    args = parser.parse_args()
    return ensure_merge(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
