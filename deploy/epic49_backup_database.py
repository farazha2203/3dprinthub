from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    db = settings.DATABASES["default"]
    engine = str(db.get("ENGINE") or "")
    if "mysql" not in engine.lower():
        raise RuntimeError(f"Epic49 production backup expects MySQL, got {engine!r}")

    executable = shutil.which("mysqldump")
    if not executable:
        raise RuntimeError("mysqldump was not found on PATH; migration is blocked until a database backup is available.")

    default_backup_root = Path.home() / "backups" / "3dprinthub"
    backup_root = Path(os.environ.get("EPIC49_BACKUP_ROOT") or default_backup_root).expanduser().resolve()
    backup_root.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    database = str(db.get("NAME") or "").strip()
    target = backup_root / f"epic49-before-0028-{database}-{stamp}.sql"

    host = str(db.get("HOST") or "localhost")
    port = str(db.get("PORT") or "3306")
    user = str(db.get("USER") or "")
    password = str(db.get("PASSWORD") or "")
    if not database or not user:
        raise RuntimeError("Database NAME/USER are incomplete; refusing to run backup.")

    command = [
        executable,
        "--single-transaction",
        "--quick",
        "--skip-lock-tables",
        "--default-character-set=utf8mb4",
        "--host", host,
        "--port", port,
        "--user", user,
        database,
    ]
    env = os.environ.copy()
    if password:
        env["MYSQL_PWD"] = password

    try:
        with target.open("wb") as output:
            result = subprocess.run(
                command,
                cwd=ROOT,
                env=env,
                stdout=output,
                stderr=subprocess.PIPE,
                timeout=900,
                check=False,
            )
    finally:
        env.pop("MYSQL_PWD", None)

    if result.returncode != 0:
        target.unlink(missing_ok=True)
        error = result.stderr.decode("utf-8", errors="replace")[-2000:]
        raise RuntimeError(f"mysqldump failed with code {result.returncode}: {error}")
    if not target.is_file() or target.stat().st_size < 1024:
        target.unlink(missing_ok=True)
        raise RuntimeError("Database backup file is missing or unexpectedly small.")

    digest = sha256(target)
    checksum = target.with_suffix(target.suffix + ".sha256")
    checksum.write_text(f"{digest}  {target.name}\n", encoding="ascii")
    print(f"EPIC49_DB_BACKUP={target}")
    print(f"EPIC49_DB_BACKUP_BYTES={target.stat().st_size}")
    print(f"EPIC49_DB_BACKUP_SHA256={digest}")
    print("EPIC49_DB_BACKUP=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
