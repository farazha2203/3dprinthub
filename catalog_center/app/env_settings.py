from __future__ import annotations

import json
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
_VALID_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_loaded_from_file: set[str] = set()


def _decode_value(raw: str) -> str:
    value = (raw or "").strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            decoded = json.loads(value)
            return str(decoded)
        except Exception:
            return value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1]
    return value


def parse_env_file(path: Path = ENV_FILE) -> dict[str, str]:
    path = Path(path)
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not _VALID_KEY.fullmatch(key):
            continue
        values[key] = _decode_value(raw_value)
    return values


def load_project_env(path: Path = ENV_FILE, *, override: bool = False) -> dict[str, str]:
    values = parse_env_file(path)
    for key, value in values.items():
        if override or key not in os.environ:
            os.environ[key] = value
            _loaded_from_file.add(key)
    return values


def env_value(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def env_int(name: str, default: int) -> int:
    raw = env_value(name, str(default)).strip()
    try:
        return int(raw)
    except (TypeError, ValueError):
        return int(default)


def env_source(name: str) -> str:
    if name in _loaded_from_file:
        return f".env ({ENV_FILE})"
    if os.getenv(name):
        return "Windows/process environment"
    return "not set"


load_project_env()
