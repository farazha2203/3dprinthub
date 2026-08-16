from __future__ import annotations

import argparse
import ast
import json
import shutil
import sqlite3
import time
from pathlib import Path

try:
    # Normal package import (tests / module use).
    from .version import APP_VERSION as VERSION
except ImportError:  # pragma: no cover - exercised by the absolute script launcher on Windows.
    # INSTALL_OR_UPGRADE.ps1 executes this file directly, so the app directory is
    # sys.path[0] and the sibling version module is importable without a package.
    from version import APP_VERSION as VERSION


def _version_tag(version: str) -> str:
    parts = [part for part in str(version).split(".") if part.isdigit()]
    return "v" + "".join(parts[:2] or ["0"])


VERSION_TAG = _version_tag(VERSION)
VERSION_MARKER = str(VERSION).replace(".", "_")
DEFAULT_TARGET = Path(r"D:\projects\3dprinthub_catalog_center")
DEFAULT_DATA = Path(r"D:\projects\3dprinthub-catalog-manager")
DEFAULT_BACKUP_ROOT = Path(r"D:\projects\3dprinthub-backups")
IGNORED_NAMES = {"__pycache__", ".git", ".pytest_cache", "build", "dist", ".env", ".env.local", "release"}


def _timestamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S", time.localtime())


def _literal_assignment(path: Path, name: str) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                return node.value.value
    raise RuntimeError(f"Missing literal {name} in {path}")


def _validate_source(source: Path) -> dict:
    manifest_path = source / "PACKAGE_MANIFEST.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Package manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if str(manifest.get("version") or "") != VERSION:
        raise RuntimeError(f"Expected package version {VERSION}")
    required = [
        "app/main.py", "app/site_connection.py", "app/version.py", "launch.py",
        "RUN.ps1", "assets/brand_icon.png", "assets/brand_logo_horizontal.png",
    ]
    missing = [name for name in required if not (source / name).is_file()]
    if missing:
        raise RuntimeError(f"Package is incomplete: {', '.join(missing)}")
    app_version = _literal_assignment(source / "app" / "version.py", "APP_VERSION")
    launcher_version = _literal_assignment(source / "launch.py", "EXPECTED_VERSION")
    if app_version != VERSION or launcher_version != VERSION:
        raise RuntimeError(
            f"Version mismatch: manifest={VERSION}, app={app_version}, launcher={launcher_version}"
        )
    run_text = (source / "RUN.ps1").read_text(encoding="utf-8")
    if '"$Root\\launch.py"' not in run_text or "-m app.main" in run_text:
        raise RuntimeError("RUN.ps1 does not use the absolute launcher")
    main_text = (source / "app" / "main.py").read_text(encoding="utf-8")
    paste_contract = [
        "self.bridge_token_entry", "paste_bridge_token", "<Control-v>",
        "<Shift-Insert>", "open_bridge_token_menu", "toggle_bridge_token_visibility",
        "normalize_bridge_token_input",
    ]
    missing_paste_contract = [marker for marker in paste_contract if marker not in main_text]
    if missing_paste_contract:
        raise RuntimeError("Bridge Token paste contract is incomplete: " + ", ".join(missing_paste_contract))
    return manifest


def _ignore(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORED_NAMES or name.endswith(".pyc")}


def _sqlite_backup(source: Path, destination: Path) -> bool:
    if not source.is_file():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    source_connection = sqlite3.connect(f"file:{source.as_posix()}?mode=ro", uri=True)
    destination_connection = sqlite3.connect(destination)
    try:
        source_connection.backup(destination_connection)
    finally:
        destination_connection.close()
        source_connection.close()
    return True


def install(source: Path, target: Path = DEFAULT_TARGET, data_root: Path = DEFAULT_DATA, backup_root: Path = DEFAULT_BACKUP_ROOT, stamp: str | None = None) -> dict:
    source = source.resolve(); target = target.resolve(); data_root = data_root.resolve(); backup_root = backup_root.resolve()
    _validate_source(source)
    if target != source and target.is_relative_to(source):
        raise RuntimeError("The package source cannot contain the installation target")
    stamp = stamp or _timestamp()
    release_backup = backup_root / f"{VERSION_TAG}-{stamp}"
    if release_backup.exists():
        raise FileExistsError(f"Backup already exists: {release_backup}")
    release_backup.mkdir(parents=True)
    stage = target.parent / f".{target.name}.{VERSION_TAG}-stage-{stamp}"
    if stage.exists():
        raise FileExistsError(f"Install stage already exists: {stage}")
    db_path = data_root / "catalog.sqlite3"
    db_backup = release_backup / "data" / "catalog.sqlite3"
    db_saved = _sqlite_backup(db_path, db_backup)
    shutil.copytree(source, stage, ignore=_ignore)
    for persistent_name in (".env", ".env.local"):
        current_file = target / persistent_name
        staged_file = stage / persistent_name
        if current_file.is_file():
            shutil.copy2(current_file, staged_file)
    _validate_source(stage)
    app_backup = release_backup / "app_previous"
    old_app_saved = False; switched = False
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.rename(app_backup); old_app_saved = True
        stage.rename(target); switched = True
    except Exception:
        if old_app_saved and not target.exists() and app_backup.exists():
            app_backup.rename(target)
        raise
    finally:
        if not switched and stage.exists():
            shutil.rmtree(stage)
    record = {
        "version": VERSION, "created_at": stamp, "source": str(source), "target": str(target),
        "data_root": str(data_root), "app_backup": str(app_backup) if old_app_saved else "",
        "db_path": str(db_path), "db_backup": str(db_backup) if db_saved else "", "status": "installed",
    }
    (release_backup / "rollback-manifest.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"backup_root": release_backup, "db_saved": db_saved, "old_app_saved": old_app_saved}


def _latest_record(backup_root: Path) -> tuple[Path, dict]:
    candidates = sorted(path for path in backup_root.glob(f"{VERSION_TAG}-*/rollback-manifest.json") if path.is_file())
    if not candidates:
        raise FileNotFoundError(f"No {VERSION} rollback manifest found under {backup_root}")
    manifest_path = candidates[-1]
    return manifest_path, json.loads(manifest_path.read_text(encoding="utf-8"))


def rollback(backup_root: Path = DEFAULT_BACKUP_ROOT) -> dict:
    backup_root = backup_root.resolve()
    manifest_path, record = _latest_record(backup_root)
    if record.get("status") != "installed":
        raise RuntimeError("The latest backup is not in an installed state")
    target = Path(record["target"])
    app_backup = Path(record["app_backup"]) if record.get("app_backup") else None
    db_path = Path(record["db_path"])
    db_backup = Path(record["db_backup"]) if record.get("db_backup") else None
    release_backup = manifest_path.parent
    displaced = release_backup / f"app_{VERSION_TAG}_before_rollback_{_timestamp()}"
    if target.exists():
        target.rename(displaced)
    try:
        if app_backup and app_backup.exists():
            app_backup.rename(target)
        if db_backup and db_backup.is_file():
            current_copy = release_backup / "data" / f"catalog_before_rollback_{_timestamp()}.sqlite3"
            _sqlite_backup(db_path, current_copy)
            _sqlite_backup(db_backup, db_path)
    except Exception:
        if not target.exists() and displaced.exists():
            displaced.rename(target)
        raise
    record["status"] = "rolled_back"; record["rolled_back_at"] = _timestamp(); record["displaced_release"] = str(displaced)
    manifest_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"manifest": manifest_path, "target_restored": bool(app_backup), "db_restored": bool(db_backup)}


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Install or roll back 3DPrintHub Catalog Center v{VERSION}")
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--backup-root", type=Path, default=DEFAULT_BACKUP_ROOT)
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()
    if args.rollback:
        result = rollback(args.backup_root)
        print(f"ROLLBACK_MANIFEST={result['manifest']}")
        print(f"CATALOG_CENTER_V{VERSION_MARKER}_ROLLBACK=OK")
        return 0
    result = install(args.source, args.target, args.data_root, args.backup_root)
    print(f"BACKUP_ROOT={result['backup_root']}")
    print(f"DATABASE_BACKUP={'OK' if result['db_saved'] else 'NOT_PRESENT'}")
    print(f"PREVIOUS_APP_BACKUP={'OK' if result['old_app_saved'] else 'FRESH_INSTALL'}")
    print(f"CATALOG_CENTER_V{VERSION_MARKER}_INSTALL=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
