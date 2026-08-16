from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


APP_VENDOR_DIRNAME = "3DPrintHub"
APP_DATA_DIRNAME = "CatalogCenter"
LEGACY_PORTABLE_DATA_DIRNAME = "3DPrintHub-CatalogCenter-Data"
MIGRATION_MARKER = ".portable-profile-v2-migrated"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"))


def resource_root() -> Path:
    """Root containing bundled read-only application resources."""
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS")).resolve()
    return Path(__file__).resolve().parents[1]


def executable_root() -> Path:
    """Directory containing the portable EXE, or source root in development."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def _legacy_development_data_root() -> Path:
    if os.name == "nt":
        return Path(r"D:\projects\3dprinthub-catalog-manager")
    return Path.home() / ".local" / "share" / "3dprinthub" / "catalog-center"


def persistent_data_root() -> Path:
    """Stable writable profile shared by all portable EXE releases on one PC."""
    override = str(os.getenv("CATALOG_DATA_ROOT") or "").strip()
    if override:
        return Path(os.path.expandvars(os.path.expanduser(override))).resolve()
    if os.name == "nt":
        local_appdata = str(os.getenv("LOCALAPPDATA") or "").strip()
        base = Path(local_appdata) if local_appdata else (Path.home() / "AppData" / "Local")
        return (base / APP_VENDOR_DIRNAME / APP_DATA_DIRNAME).resolve()
    return (Path.home() / ".local" / "share" / "3dprinthub" / "catalog-center").resolve()


def data_root() -> Path:
    """Writable application data root.

    Precedence:
    1. CATALOG_DATA_ROOT environment override.
    2. Stable per-user profile for frozen/portable EXE releases.
    3. Existing canonical development data directory for source runs.
    """
    override = str(os.getenv("CATALOG_DATA_ROOT") or "").strip()
    if override:
        return Path(os.path.expandvars(os.path.expanduser(override))).resolve()
    if is_frozen():
        return persistent_data_root()
    return _legacy_development_data_root().resolve()


def legacy_portable_data_candidates() -> list[Path]:
    """Return old per-release data folders that can be migrated safely."""
    if not is_frozen():
        return []
    root = executable_root()
    candidates: list[Path] = [root / LEGACY_PORTABLE_DATA_DIRNAME]

    # Typical layout: ...\release\8.5.4\EXE. Search sibling release versions too.
    release_root = root.parent
    try:
        siblings = sorted(
            [item for item in release_root.iterdir() if item.is_dir()],
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        candidates.extend(item / LEGACY_PORTABLE_DATA_DIRNAME for item in siblings)
    except Exception:
        pass

    # Development/runtime location used by older source builds on the main workstation.
    if os.name == "nt":
        candidates.append(Path(r"D:\projects\3dprinthub-catalog-manager"))

    unique: list[Path] = []
    seen: set[str] = set()
    target = data_root().resolve()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except Exception:
            continue
        key = str(resolved).lower()
        if resolved == target or key in seen:
            continue
        seen.add(key)
        if candidate.is_dir() and any((candidate / name).exists() for name in ("catalog.sqlite3", "config.json", ".env")):
            unique.append(candidate)
    return unique


def _copy_missing_tree(source: Path, target: Path) -> int:
    copied = 0
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        destination = target / relative
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        copied += 1
    return copied


def migrate_legacy_portable_data() -> dict[str, str | int | bool]:
    """One-time, non-destructive migration from old release-local data folders.

    Existing files in the stable profile always win; no source file is deleted.
    """
    target = data_root()
    target.mkdir(parents=True, exist_ok=True)
    marker = target / MIGRATION_MARKER
    if marker.is_file():
        return {"migrated": False, "reason": "already_migrated", "target": str(target), "copied": 0}

    source = next(iter(legacy_portable_data_candidates()), None)
    copied = 0
    if source is not None:
        copied = _copy_missing_tree(source, target)

    marker.write_text(
        "source=" + (str(source) if source is not None else "none") + "\n" + f"copied={copied}\n",
        encoding="utf-8",
    )
    return {
        "migrated": source is not None,
        "source": str(source) if source is not None else "",
        "target": str(target),
        "copied": copied,
    }


def env_file() -> Path:
    override = str(os.getenv("CATALOG_ENV_FILE") or "").strip()
    if override:
        return Path(os.path.expandvars(os.path.expanduser(override))).resolve()
    if is_frozen():
        return data_root() / ".env"
    return resource_root() / ".env"


def config_template() -> Path:
    return resource_root() / "config.example.json"


def asset_root() -> Path:
    return resource_root() / "assets"


def default_host_mirror() -> Path:
    if is_frozen():
        return data_root() / "host_mirror"
    if os.name == "nt":
        return Path(r"D:\projects\3dprinthub-houst")
    return data_root() / "host_mirror"


def runtime_summary() -> dict[str, str | bool]:
    return {
        "frozen": is_frozen(),
        "resource_root": str(resource_root()),
        "executable_root": str(executable_root()),
        "data_root": str(data_root()),
        "persistent_data_root": str(persistent_data_root()),
        "env_file": str(env_file()),
    }
