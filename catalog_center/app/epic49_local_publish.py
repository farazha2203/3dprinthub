from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from .v8_features import parse_ack_lines


LOCAL_SITE_URL = "http://127.0.0.1:8000"


def running_as_portable() -> bool:
    return bool(getattr(sys, "frozen", False))


def default_repo_root() -> Path:
    configured = str(os.getenv("CATALOG_LOCAL_DJANGO_ROOT") or "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    # catalog_center/app/epic49_local_publish.py -> repository root
    return Path(__file__).resolve().parents[2]


def expected_local_db(repo_root: Path | None = None) -> Path:
    root = Path(repo_root or default_repo_root()).resolve()
    configured = str(os.getenv("CATALOG_LOCAL_DJANGO_DB") or "").strip()
    return Path(configured).expanduser().resolve() if configured else (root / "db.sqlite3").resolve()


def _run(command: list[str], *, cwd: Path, timeout: int = 180) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def _marker(stdout: str, name: str) -> str:
    prefix = name + "="
    for line in (stdout or "").splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""


def local_django_preflight(
    *,
    repo_root: Path | None = None,
    python_executable: str | None = None,
) -> dict:
    """Prove that the Local button targets the workstation SQLite database.

    This is deliberately strict. The Local button must never be able to inherit
    a production MySQL DATABASE_URL from the current Windows environment.
    Portable/employee EXE builds are not developer runtimes and are blocked.
    """
    if running_as_portable():
        raise RuntimeError(
            "LOCAL PUBLISH BLOCKED: انتشار آزمایشی روی کامپیوتر فقط در نسخه Source/Developer فعال است. "
            "نسخه Portable کارمندان فقط مجاز به استفاده از دکمه انتشار سایت اصلی است."
        )

    root = Path(repo_root or default_repo_root()).resolve()
    manage_py = root / "manage.py"
    if not manage_py.is_file():
        raise RuntimeError(f"manage.py برای تست لوکال پیدا نشد: {manage_py}")

    python_bin = str(python_executable or sys.executable)
    probe = (
        "from django.db import connection; "
        "connection.ensure_connection(); "
        "print('EPIC49_LOCAL_DB_VENDOR=' + str(connection.vendor)); "
        "print('EPIC49_LOCAL_DB_NAME=' + str(connection.settings_dict.get('NAME') or ''))"
    )
    result = _run([python_bin, str(manage_py), "shell", "-c", probe], cwd=root, timeout=90)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()[-3000:]
        raise RuntimeError(f"بررسی دیتابیس Local ناموفق بود:\n{detail}")

    vendor = _marker(result.stdout, "EPIC49_LOCAL_DB_VENDOR").lower()
    raw_name = _marker(result.stdout, "EPIC49_LOCAL_DB_NAME")
    if vendor != "sqlite":
        raise RuntimeError(
            "LOCAL PUBLISH BLOCKED: دیتابیس مقصد SQLite نیست. "
            f"vendor={vendor or 'unknown'} name={raw_name or '-'}"
        )
    if not raw_name:
        raise RuntimeError("LOCAL PUBLISH BLOCKED: نام فایل SQLite از Django دریافت نشد.")

    actual_db = Path(raw_name).expanduser().resolve()
    expected_db = expected_local_db(root)
    if actual_db != expected_db:
        raise RuntimeError(
            "LOCAL PUBLISH BLOCKED: دیتابیس Django با دیتابیس Local مورد انتظار یکی نیست.\n"
            f"Actual: {actual_db}\nExpected: {expected_db}"
        )
    return {
        "repo_root": root,
        "manage_py": manage_py,
        "database_vendor": vendor,
        "database_name": actual_db,
        "site_url": str(os.getenv("CATALOG_LOCAL_SITE_URL") or LOCAL_SITE_URL).rstrip("/"),
    }


def import_batch_to_local_django(
    batch: Path,
    *,
    repo_root: Path | None = None,
    python_executable: str | None = None,
) -> dict:
    """Import one standard v8.5 desktop batch directly into local Django.

    No FTP, Bridge HTTP request, production credentials, or production ACK fields
    are used by this function.
    """
    batch = Path(batch).resolve()
    manifest = batch / "batch_manifest.json"
    if not manifest.is_file():
        raise RuntimeError(f"Batch manifest پیدا نشد: {manifest}")

    preflight = local_django_preflight(repo_root=repo_root, python_executable=python_executable)
    root = Path(preflight["repo_root"])
    python_bin = str(python_executable or sys.executable)
    result = _run(
        [
            python_bin,
            str(preflight["manage_py"]),
            "phase37_import_catalog_center",
            str(batch),
            "--continue-on-error",
        ],
        cwd=root,
        timeout=300,
    )
    ack = parse_ack_lines(result.stdout)
    if ack is None:
        detail = "\n".join(
            part for part in [(result.stdout or "")[-2500:], (result.stderr or "")[-2500:]] if part
        )
        raise RuntimeError(f"Importer لوکال ACK معتبر برنگرداند.\n{detail}")
    if result.returncode != 0 or int(ack.get("failed_count") or 0) > 0:
        detail = (result.stderr or result.stdout or "").strip()[-3000:]
        raise RuntimeError(
            "Import لوکال با خطا پایان یافت.\n"
            f"failed_count={ack.get('failed_count')} returncode={result.returncode}\n{detail}"
        )
    return {
        "ack": ack,
        "preflight": preflight,
        "stdout_tail": (result.stdout or "")[-4000:],
        "stderr_tail": (result.stderr or "")[-2000:],
    }
