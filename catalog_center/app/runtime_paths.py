from __future__ import annotations

import os
import sys
from pathlib import Path


APP_DATA_DIRNAME = "3DPrintHub-CatalogCenter-Data"


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
    return Path.home() / APP_DATA_DIRNAME


def data_root() -> Path:
    """Writable application data root.

    Precedence:
    1. CATALOG_DATA_ROOT environment override.
    2. Portable EXE sibling data directory.
    3. Existing canonical development data directory.
    """
    override = str(os.getenv("CATALOG_DATA_ROOT") or "").strip()
    if override:
        return Path(os.path.expandvars(os.path.expanduser(override))).resolve()
    if is_frozen():
        return (executable_root() / APP_DATA_DIRNAME).resolve()
    return _legacy_development_data_root().resolve()


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
        "env_file": str(env_file()),
    }
