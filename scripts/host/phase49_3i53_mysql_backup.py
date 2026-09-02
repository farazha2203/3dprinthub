#!/usr/bin/env python3
from __future__ import annotations

import gzip
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Mapping, Sequence


def stream_command_to_gzip(
    command: Sequence[str],
    *,
    env: Mapping[str, str],
    outfile: Path,
    stderr_path: Path,
) -> tuple[int, bytes]:
    outfile = Path(outfile)
    stderr_path = Path(stderr_path)
    outfile.parent.mkdir(parents=True, exist_ok=True)

    try:
        with stderr_path.open("wb") as stderr_handle:
            with subprocess.Popen(
                list(command),
                stdout=subprocess.PIPE,
                stderr=stderr_handle,
                env=dict(env),
            ) as proc:
                if proc.stdout is None:
                    raise RuntimeError("subprocess stdout pipe is unavailable")
                with gzip.open(outfile, "wb", compresslevel=6) as target:
                    shutil.copyfileobj(proc.stdout, target, length=1024 * 1024)
                proc.stdout.close()
                returncode = proc.wait()

        stderr = stderr_path.read_bytes() if stderr_path.exists() else b""
        return returncode, stderr
    except Exception:
        try:
            outfile.unlink()
        except FileNotFoundError:
            pass
        raise
    finally:
        try:
            stderr_path.unlink()
        except FileNotFoundError:
            pass


def verify_gzip_mysql_dump(outfile: Path) -> int:
    outfile = Path(outfile)
    if not outfile.is_file():
        raise RuntimeError("database backup file is missing")

    size = outfile.stat().st_size
    if size < 1024:
        raise RuntimeError("database backup is unexpectedly small")

    with outfile.open("rb") as raw:
        magic = raw.read(2)
    if magic != b"\x1f\x8b":
        raise RuntimeError("database backup does not have gzip magic")

    with gzip.open(outfile, "rb") as source:
        prefix = source.read(4096)

    if b"MySQL dump" not in prefix and b"MariaDB dump" not in prefix:
        raise RuntimeError("database backup payload does not look like mysqldump output")

    return size


def run_production_backup(expected_db: str) -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    import django

    django.setup()

    from django.db import connection

    cfg = connection.settings_dict
    if connection.vendor != "mysql":
        raise SystemExit("DEPLOY_FAIL=backup_database_vendor_not_mysql")
    if str(cfg.get("NAME") or "") != expected_db:
        raise SystemExit("DEPLOY_FAIL=backup_database_name_mismatch")

    binary = shutil.which("mysqldump")
    if not binary:
        raise SystemExit("DEPLOY_FAIL=mysqldump_missing")

    root = Path(os.environ["PHASE49_BACKUP_ROOT"])
    outfile = root / "database-before-3i53.sql.gz"
    stderr_path = root / ".mysqldump.stderr"

    command = [
        binary,
        "--single-transaction",
        "--quick",
        "--routines",
        "--triggers",
        "--no-tablespaces",
        "--default-character-set=utf8mb4",
        "-h",
        str(cfg.get("HOST") or "localhost"),
        "-P",
        str(cfg.get("PORT") or "3306"),
        "-u",
        str(cfg.get("USER") or ""),
        str(cfg.get("NAME") or ""),
    ]

    child_env = os.environ.copy()
    child_env["MYSQL_PWD"] = str(cfg.get("PASSWORD") or "")

    returncode, stderr = stream_command_to_gzip(
        command,
        env=child_env,
        outfile=outfile,
        stderr_path=stderr_path,
    )

    if returncode:
        try:
            outfile.unlink()
        except FileNotFoundError:
            pass
        raise SystemExit(
            "DEPLOY_FAIL=mysqldump_failed:"
            + stderr.decode("utf-8", errors="replace")[-1200:]
        )

    try:
        size = verify_gzip_mysql_dump(outfile)
    except Exception as exc:
        try:
            outfile.unlink()
        except FileNotFoundError:
            pass
        raise SystemExit(f"DEPLOY_FAIL=database_backup_invalid:{type(exc).__name__}:{exc}")

    print("DATABASE_BACKUP=" + str(outfile))
    print("DATABASE_BACKUP_SIZE=" + str(size))
    print("DATABASE_BACKUP_GZIP=VALID")


def self_test() -> None:
    payload = (
        b"-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)\n"
        + b"CREATE TABLE demo(id bigint);\n"
        + (b"INSERT INTO demo VALUES (1);\n" * 80000)
    )

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        outfile = root / "fixture.sql.gz"
        stderr_path = root / "fixture.stderr"
        command = [
            sys.executable,
            "-c",
            "import sys; sys.stdout.buffer.write(" + repr(payload) + ")",
        ]

        returncode, stderr = stream_command_to_gzip(
            command,
            env=os.environ.copy(),
            outfile=outfile,
            stderr_path=stderr_path,
        )
        if returncode != 0 or stderr:
            raise SystemExit("MYSQL_BACKUP_SELF_TEST=FAIL:child_process")

        verify_gzip_mysql_dump(outfile)
        with gzip.open(outfile, "rb") as source:
            restored = source.read()
        if restored != payload:
            raise SystemExit("MYSQL_BACKUP_SELF_TEST=FAIL:roundtrip")

    print("MYSQL_BACKUP_SELF_TEST=PASS")


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        return 0

    if len(sys.argv) != 2:
        print(
            "usage: phase49_3i53_mysql_backup.py <expected_database>",
            file=sys.stderr,
        )
        return 2

    run_production_backup(sys.argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
