from __future__ import annotations

import os
from pathlib import Path

SERVICE_NAME = "3DPrintHub Catalog Intelligence"
USERS = {
    "openai": "OPENAI_API_KEY",
    "avalai": "AVALAI_API_KEY",
}

CONNECTION_USERS = {
    "ftp_password": "FTP_PASSWORD",
    "bridge_token": "CATALOG_BRIDGE_TOKEN",
}

LEGACY_FILES = {
    "openai": ["APIKEY.txt"],
    "avalai": ["APIKEY-AVAL.txt", "APIKEY_AVAL.txt"],
}


def _keyring():
    try:
        import keyring
        return keyring
    except Exception:
        return None


def get_secret(name: str) -> str:
    """Read a connection secret without touching SQLite or log files."""
    env_name = CONNECTION_USERS.get(name, name.upper())
    env = (os.getenv(env_name) or "").strip()
    if env:
        return env
    kr = _keyring()
    if not kr:
        return ""
    try:
        return (kr.get_password(SERVICE_NAME, env_name) or "").strip()
    except Exception:
        return ""


def set_secret(name: str, value: str) -> None:
    env_name = CONNECTION_USERS.get(name, name.upper())
    value = (value or "").strip()
    if not value:
        raise ValueError("Secret is empty")
    kr = _keyring()
    if not kr:
        raise RuntimeError("Windows Credential Store backend is unavailable.")
    kr.set_password(SERVICE_NAME, env_name, value)


def delete_secret(name: str) -> None:
    env_name = CONNECTION_USERS.get(name, name.upper())
    kr = _keyring()
    if not kr:
        return
    try:
        kr.delete_password(SERVICE_NAME, env_name)
    except Exception:
        pass


def secret_source(name: str) -> str:
    env_name = CONNECTION_USERS.get(name, name.upper())
    if (os.getenv(env_name) or "").strip():
        return env_name
    kr = _keyring()
    if kr:
        try:
            if (kr.get_password(SERVICE_NAME, env_name) or "").strip():
                return "Windows Credential Store"
        except Exception:
            pass
    return "Not configured"


def migrate_connection_env_to_keyring(env_path: str | Path) -> list[str]:
    """Move FTP/Bridge secrets from a portable .env into Windows Credential Store.

    The source file is scrubbed only after every discovered secret is saved successfully.
    No secret value is returned or logged.
    """
    path = Path(env_path)
    if not path.is_file():
        return []

    original_lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    reverse = {env_name: name for name, env_name in CONNECTION_USERS.items()}
    discovered: dict[str, str] = {}
    secret_line_indexes: set[int] = set()

    for index, raw_line in enumerate(original_lines):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if key not in reverse:
            continue
        value = raw_value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1].strip()
        if value:
            discovered[reverse[key]] = value
            secret_line_indexes.add(index)

    if not discovered:
        return []

    kr = _keyring()
    if not kr:
        raise RuntimeError("Windows Credential Store backend is unavailable; portable secrets were not migrated.")

    for secret_name, value in discovered.items():
        env_name = CONNECTION_USERS[secret_name]
        kr.set_password(SERVICE_NAME, env_name, value)

    cleaned = [line for index, line in enumerate(original_lines) if index not in secret_line_indexes]
    cleaned.append("# Connection secrets migrated to Windows Credential Store.")
    path.write_text("\n".join(cleaned).rstrip() + "\n", encoding="utf-8")
    return sorted(discovered)


def _project_root(project_root: str | Path | None = None) -> Path:
    if project_root:
        return Path(project_root)
    env = (os.getenv("THREEDPRINTHUB_PROJECT_ROOT") or "").strip()
    if env:
        return Path(env)
    return Path(r"D:\projects\3DPrintHub")


def _read_legacy_file(provider: str, project_root: str | Path | None = None) -> str:
    root = _project_root(project_root)
    for name in LEGACY_FILES.get(provider, []):
        path = root / name
        try:
            if path.is_file():
                value = path.read_text(encoding="utf-8-sig")
                for raw_line in value.splitlines():
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line and line.split("=", 1)[0].strip().upper().endswith("API_KEY"):
                        line = line.split("=", 1)[1].strip()
                    line = line.strip().strip('"').strip("'")
                    if line:
                        return line
        except Exception:
            continue
    return ""


def get_provider_key(provider: str, project_root: str | Path | None = None) -> str:
    provider = (provider or "openai").lower().strip()
    env_name = USERS.get(provider, "OPENAI_API_KEY")
    env = (os.getenv(env_name) or "").strip()
    if env:
        return env
    kr = _keyring()
    if kr:
        try:
            value = (kr.get_password(SERVICE_NAME, env_name) or "").strip()
            if value:
                return value
        except Exception:
            pass
    return _read_legacy_file(provider, project_root)


def set_provider_key(provider: str, value: str) -> None:
    provider = (provider or "openai").lower().strip()
    env_name = USERS.get(provider, "OPENAI_API_KEY")
    value = (value or "").strip()
    if not value:
        raise ValueError("API key is empty")
    kr = _keyring()
    if not kr:
        raise RuntimeError("Windows Credential Store backend is unavailable. Use an environment variable instead.")
    kr.set_password(SERVICE_NAME, env_name, value)


def delete_provider_key(provider: str) -> None:
    provider = (provider or "openai").lower().strip()
    env_name = USERS.get(provider, "OPENAI_API_KEY")
    kr = _keyring()
    if not kr:
        return
    try:
        kr.delete_password(SERVICE_NAME, env_name)
    except Exception:
        pass


def provider_key_source(provider: str, project_root: str | Path | None = None) -> str:
    provider = (provider or "openai").lower().strip()
    env_name = USERS.get(provider, "OPENAI_API_KEY")
    if (os.getenv(env_name) or "").strip():
        return env_name
    kr = _keyring()
    if kr:
        try:
            if (kr.get_password(SERVICE_NAME, env_name) or "").strip():
                return "Windows Credential Store"
        except Exception:
            pass
    root = _project_root(project_root)
    for name in LEGACY_FILES.get(provider, []):
        try:
            if (root / name).is_file() and (root / name).read_text(encoding="utf-8-sig").strip():
                return str(root / name)
        except Exception:
            continue
    return "Not configured"


def migrate_legacy_key_to_keyring(provider: str, project_root: str | Path | None = None) -> bool:
    value = _read_legacy_file(provider, project_root)
    if not value:
        return False
    set_provider_key(provider, value)
    return True

# Backward-compatible helpers used by v8.3 code.
def get_openai_key() -> str:
    return get_provider_key("openai")

def set_openai_key(value: str) -> None:
    set_provider_key("openai", value)

def delete_openai_key() -> None:
    delete_provider_key("openai")

def key_source() -> str:
    return provider_key_source("openai")
