#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/phase48_backups/$STAMP"

cd "$PROJECT"

echo "=== PHASE48 PRODUCTION DEPLOY ==="
echo "PROJECT=$PROJECT"
echo "GIT_HEAD=$(git rev-parse HEAD)"
echo "GIT_BRANCH=$(git branch --show-current)"
echo "BACKUP_ROOT=$BACKUP_ROOT"

mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"

if [[ -f ".env" ]]; then
  cp -p ".env" "$BACKUP_ROOT/.env"
  chmod 600 "$BACKUP_ROOT/.env"
fi

if [[ -d "imports/desktop_catalog/pending" ]]; then
  tar -czf "$BACKUP_ROOT/pending-before-deploy.tgz" \
    imports/desktop_catalog/pending
fi

echo
echo "=== TRACKED SOURCE CHECK ==="
git diff --exit-code
git diff --cached --exit-code

echo
echo "=== DJANGO PRECHECK ==="
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

echo
echo "=== DATABASE BACKUP ==="
PHASE48_BACKUP_ROOT="$BACKUP_ROOT" "$PY" - <<'PY'
import gzip
import os
import shutil
import subprocess
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection

cfg = connection.settings_dict
if connection.vendor != "mysql":
    raise SystemExit(f"Refusing production backup: expected mysql, got {connection.vendor}")

binary = shutil.which("mysqldump")
if not binary:
    raise SystemExit("mysqldump was not found; deployment stopped before migrations.")

name = str(cfg.get("NAME") or "")
user = str(cfg.get("USER") or "")
password = str(cfg.get("PASSWORD") or "")
host = str(cfg.get("HOST") or "localhost")
port = str(cfg.get("PORT") or "3306")

backup_root = Path(os.environ["PHASE48_BACKUP_ROOT"])
outfile = backup_root / "database-before-phase48.sql.gz"

cmd = [
    binary,
    "--single-transaction",
    "--quick",
    "--routines",
    "--triggers",
    "--default-character-set=utf8mb4",
    "-h", host,
    "-P", port,
    "-u", user,
    name,
]
env = os.environ.copy()
env["MYSQL_PWD"] = password

with gzip.open(outfile, "wb", compresslevel=6) as target:
    proc = subprocess.run(
        cmd,
        stdout=target,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
if proc.returncode:
    try:
        outfile.unlink()
    except FileNotFoundError:
        pass
    raise SystemExit(
        "mysqldump failed: "
        + proc.stderr.decode("utf-8", errors="replace")[-3000:]
    )

print(f"DATABASE_BACKUP={outfile}")
print(f"DATABASE_BACKUP_SIZE={outfile.stat().st_size}")
PY

echo
echo "=== MIGRATION PLAN ==="
"$PY" manage.py migrate --plan

echo
echo "=== MIGRATE ==="
"$PY" manage.py migrate --noinput

echo
echo "=== COLLECTSTATIC ==="
"$PY" manage.py collectstatic --noinput

echo
echo "=== PASSENGER RESTART ==="
mkdir -p tmp
touch tmp/restart.txt
sleep 3

echo
echo "=== RUNTIME VERIFY ==="
"$PY" deploy/phase48_verify_runtime.py

echo
echo "PHASE48_PRODUCTION_DEPLOY=OK"
echo "BACKUP_ROOT=$BACKUP_ROOT"
