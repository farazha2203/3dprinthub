$ErrorActionPreference = "Stop"

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

@'
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import traceback

PROJECT_ROOT = Path(r"D:\projects\3DPrintHub")
TRANSFER_DIR = PROJECT_ROOT / "transfer"
FIXTURE_JSON = TRANSFER_DIR / "3dprinthub_data.json"
FIXTURE_GZ = TRANSFER_DIR / "3dprinthub_data.json.gz"
MEDIA_ARCHIVE = TRANSFER_DIR / "media.tar.gz"
PRIVATE_MEDIA_ARCHIVE = TRANSFER_DIR / "private_media.tar.gz"
MANIFEST_PATH = TRANSFER_DIR / "transfer_manifest.json"
DUMPDATA_LOG = TRANSFER_DIR / "dumpdata_stderr.log"
OVERLONG_REPORT = TRANSFER_DIR / "overlong_values.json"

EXCLUDED_MODELS = {
    "contenttypes.contenttype",
    "auth.permission",
    "admin.logentry",
    "sessions.session",
}

REQUIRED_BUSINESS_MODELS = {
    "website.sitesetting",
    "website.material",
    "website.industryrecommendation",
    "website.partrecommendation",
}

MYSQL_LENGTH_LIMITS = {
    ("store.catalogseedurl", "url"): 700,
    ("store.importedprintasset", "source_url"): 700,
}

KNOWN_OUTPUTS = (
    FIXTURE_JSON,
    FIXTURE_GZ,
    MEDIA_ARCHIVE,
    PRIVATE_MEDIA_ARCHIVE,
    MANIFEST_PATH,
    DUMPDATA_LOG,
    OVERLONG_REPORT,
)


def fail(message: str, code: int = 1) -> None:
    print(f"\nSTOP: {message}", file=sys.stderr)
    raise SystemExit(code)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def directory_stats(path: Path) -> dict[str, int]:
    if not path.exists():
        return {"file_count": 0, "size_bytes": 0}

    files = [item for item in path.rglob("*") if item.is_file()]
    return {
        "file_count": len(files),
        "size_bytes": sum(item.stat().st_size for item in files),
    }


def create_tar(source_dir: Path, archive_path: Path) -> dict[str, int]:
    source_dir.mkdir(parents=True, exist_ok=True)
    stats = directory_stats(source_dir)

    with tarfile.open(archive_path, "w:gz", compresslevel=9) as archive:
        archive.add(source_dir, arcname=source_dir.name)

    return stats


try:
    print("== 3DPrintHub transfer builder v3 ==")

    if not PROJECT_ROOT.is_dir():
        fail(f"Project directory not found: {PROJECT_ROOT}")

    manage_py = PROJECT_ROOT / "manage.py"
    settings_py = PROJECT_ROOT / "config" / "settings.py"
    sqlite_path = PROJECT_ROOT / "db.sqlite3"

    for required in (manage_py, settings_py, sqlite_path):
        if not required.is_file():
            fail(f"Required project file not found: {required}")

    TRANSFER_DIR.mkdir(parents=True, exist_ok=True)

    for path in KNOWN_OUTPUTS:
        path.unlink(missing_ok=True)

    os.chdir(PROJECT_ROOT)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"

    import django

    django.setup()

    from django.apps import apps
    from django.db import connection

    print("LOCAL_DATABASE_VENDOR:", connection.vendor)
    print("LOCAL_DATABASE_NAME:", connection.settings_dict["NAME"])
    print("SQLITE_FILE_SIZE:", sqlite_path.stat().st_size)

    if connection.vendor != "sqlite":
        fail(
            "The local project is not using SQLite. "
            "Do not export until DB_NAME is absent from the local .env."
        )

    configured_db = Path(str(connection.settings_dict["NAME"])).resolve()
    if configured_db != sqlite_path.resolve():
        fail(
            "Django is connected to a different SQLite file: "
            f"{configured_db}"
        )

    print("\n== Reading actual database inventory ==")

    database_counts: dict[str, int] = {}
    count_errors: dict[str, str] = {}

    for model in apps.get_models():
        label = model._meta.label_lower

        try:
            database_counts[label] = model._base_manager.using("default").count()
        except Exception as exc:
            count_errors[label] = f"{type(exc).__name__}: {exc}"

    business_counts = {
        label: count
        for label, count in database_counts.items()
        if label.startswith(("website.", "store."))
    }

    nonzero_business = {
        label: count
        for label, count in business_counts.items()
        if count
    }

    for label, count in sorted(nonzero_business.items()):
        print(f"{label}: {count}")

    total_business_objects = sum(business_counts.values())
    print("TOTAL_DATABASE_BUSINESS_OBJECTS:", total_business_objects)

    if total_business_objects == 0:
        fail("The SQLite database has no website/store business data.")

    print("\n== Required content models ==")

    required_status = {}

    for label in sorted(REQUIRED_BUSINESS_MODELS):
        count = database_counts.get(label)
        required_status[label] = count
        print(f"{label}: {count}")

    missing_required = [
        label
        for label, count in required_status.items()
        if count is None or count == 0
    ]

    if missing_required:
        print(
            "WARNING: These expected content models are empty or unavailable:",
            ", ".join(missing_required),
        )

    # Close the inspection connection before starting a separate Django process.
    connection.close()

    print("\n== Exporting all database data in forced UTF-8 ==")

    command = [
        sys.executable,
        "-X",
        "utf8",
        str(manage_py),
        "dumpdata",
        "--database",
        "default",
        "--all",
        "--format",
        "json",
        "--natural-foreign",
        "--natural-primary",
        "--exclude",
        "contenttypes",
        "--exclude",
        "auth.permission",
        "--exclude",
        "admin.logentry",
        "--exclude",
        "sessions",
        "--indent",
        "2",
        "--verbosity",
        "0",
    ]

    child_env = os.environ.copy()
    child_env["PYTHONUTF8"] = "1"
    child_env["PYTHONIOENCODING"] = "utf-8"

    with FIXTURE_JSON.open("wb") as stdout_handle, DUMPDATA_LOG.open(
        "wb"
    ) as stderr_handle:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=child_env,
            stdout=stdout_handle,
            stderr=stderr_handle,
            check=False,
        )

    if result.returncode != 0:
        error_text = DUMPDATA_LOG.read_text(
            encoding="utf-8",
            errors="replace",
        )
        print(error_text)
        fail(f"dumpdata failed with exit code {result.returncode}")

    if not FIXTURE_JSON.is_file() or FIXTURE_JSON.stat().st_size == 0:
        fail("dumpdata produced an empty file.")

    try:
        with FIXTURE_JSON.open("r", encoding="utf-8") as handle:
            fixture = json.load(handle)
    except Exception as exc:
        fail(f"Generated fixture is not valid UTF-8 JSON: {exc}")

    if not isinstance(fixture, list):
        fail("Fixture root is not a JSON list.")

    fixture_counts = Counter(
        item.get("model", "")
        for item in fixture
        if isinstance(item, dict)
    )

    fixture_business_counts = {
        label: count
        for label, count in fixture_counts.items()
        if label.startswith(("website.", "store."))
    }

    fixture_business_total = sum(fixture_business_counts.values())

    print("FIXTURE_OBJECTS:", len(fixture))
    print("FIXTURE_BUSINESS_OBJECTS:", fixture_business_total)

    if fixture_business_total == 0:
        fail("Fixture contains no website/store business data.")

    print("\n== Comparing SQLite counts with fixture counts ==")

    mismatches = []

    for label, database_count in sorted(database_counts.items()):
        if label in EXCLUDED_MODELS:
            continue

        fixture_count = fixture_counts.get(label, 0)

        if fixture_count != database_count:
            mismatches.append(
                {
                    "model": label,
                    "database": database_count,
                    "fixture": fixture_count,
                }
            )
            print(
                f"MISMATCH {label}: "
                f"database={database_count}, fixture={fixture_count}"
            )

    print("EXPORT_COUNT_MISMATCHES:", len(mismatches))

    if mismatches:
        fail(
            "Fixture counts do not match the SQLite database. "
            "The export was not packaged."
        )

    print("\n== Checking values against the MySQL-compatible schema ==")

    overlong = []

    for item in fixture:
        if not isinstance(item, dict):
            continue

        model_label = item.get("model", "")
        fields = item.get("fields") or {}

        for (target_model, field_name), limit in MYSQL_LENGTH_LIMITS.items():
            if model_label != target_model:
                continue

            value = fields.get(field_name) or ""

            if len(value) > limit:
                overlong.append(
                    {
                        "model": model_label,
                        "pk": item.get("pk"),
                        "field": field_name,
                        "length": len(value),
                        "limit": limit,
                        "value": value,
                    }
                )

    if overlong:
        OVERLONG_REPORT.write_text(
            json.dumps(overlong, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        fail(
            f"{len(overlong)} value(s) exceed the host field limits. "
            f"See: {OVERLONG_REPORT}"
        )

    print("MYSQL_LENGTH_CHECK=OK")

    print("\n== Compressing fixture ==")

    with FIXTURE_JSON.open("rb") as source, gzip.open(
        FIXTURE_GZ,
        "wb",
        compresslevel=9,
    ) as destination:
        shutil.copyfileobj(source, destination)

    # Keep only the compressed fixture to reduce transfer size.
    FIXTURE_JSON.unlink()

    print("\n== Packaging media ==")

    media_stats = create_tar(PROJECT_ROOT / "media", MEDIA_ARCHIVE)
    private_media_stats = create_tar(
        PROJECT_ROOT / "private_media",
        PRIVATE_MEDIA_ARCHIVE,
    )

    package_files = (
        FIXTURE_GZ,
        MEDIA_ARCHIVE,
        PRIVATE_MEDIA_ARCHIVE,
    )

    files_manifest = {}

    for path in package_files:
        files_manifest[path.name] = {
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        }

    files_manifest[MEDIA_ARCHIVE.name].update(media_stats)
    files_manifest[PRIVATE_MEDIA_ARCHIVE.name].update(private_media_stats)

    manifest = {
        "format_version": 3,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "database": {
            "vendor": "sqlite",
            "path": str(sqlite_path),
            "size_bytes": sqlite_path.stat().st_size,
        },
        "excluded_models": sorted(EXCLUDED_MODELS),
        "database_model_counts": dict(sorted(database_counts.items())),
        "fixture_model_counts": dict(sorted(fixture_counts.items())),
        "fixture_objects": len(fixture),
        "business_objects": fixture_business_total,
        "required_content_models": required_status,
        "count_errors": count_errors,
        "files": files_manifest,
    }

    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n== Transfer package ready ==")
    print("TRANSFER_PACKAGE_READY=OK")
    print("TRANSFER_DIRECTORY:", TRANSFER_DIR)
    print("DATABASE_OBJECTS:", sum(database_counts.values()))
    print("BUSINESS_OBJECTS:", fixture_business_total)

    for path in (*package_files, MANIFEST_PATH):
        print(f"{path.name}: {path.stat().st_size} bytes")

    print("\nUpload exactly these four files to:")
    print("/home/sfkilvrs/3dprinthub/transfer/")
    print()
    print(FIXTURE_GZ)
    print(MEDIA_ARCHIVE)
    print(PRIVATE_MEDIA_ARCHIVE)
    print(MANIFEST_PATH)

except SystemExit:
    raise
except Exception:
    traceback.print_exc()
    raise SystemExit(99)
'@ | python -

if ($LASTEXITCODE -ne 0) {
    throw "3DPrintHub transfer package creation failed."
}
