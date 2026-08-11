$ErrorActionPreference = "Stop"

$ProjectRoot = "D:\projects\3DPrintHub"
Set-Location $ProjectRoot

if (-not (Test-Path ".\manage.py")) {
    throw "manage.py was not found in $ProjectRoot"
}

Write-Host "== Checking local database =="

@'
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.db import connection

print("LOCAL_DATABASE_VENDOR:", connection.vendor)
print("LOCAL_DATABASE_NAME:", connection.settings_dict["NAME"])

if connection.vendor != "sqlite":
    print("STOP: The local project is not using SQLite.")
    sys.exit(2)

print("LOCAL_SQLITE_CHECK=OK")
'@ | python -

if ($LASTEXITCODE -ne 0) {
    throw "Local database check failed."
}

$TransferDir = Join-Path $ProjectRoot "transfer"
New-Item -ItemType Directory -Path $TransferDir -Force | Out-Null

$KnownOutputs = @(
    "3dprinthub_data.json",
    "3dprinthub_data.json.gz",
    "media.tar.gz",
    "private_media.tar.gz",
    "transfer_manifest.json",
    "overlong_urls.json"
)

foreach ($Name in $KnownOutputs) {
    $Path = Join-Path $TransferDir $Name
    Remove-Item $Path -Force -ErrorAction SilentlyContinue
}

Write-Host "== Exporting SQLite data =="

python manage.py dumpdata `
    --all `
    --format json `
    --natural-foreign `
    --natural-primary `
    --exclude contenttypes `
    --exclude auth.permission `
    --exclude admin.logentry `
    --exclude sessions `
    --exclude sites.site `
    --indent 2 `
    --output ".\transfer\3dprinthub_data.json"

if ($LASTEXITCODE -ne 0) {
    throw "Django dumpdata failed."
}

Write-Host "== Validating and packaging transfer files =="

@'
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import gzip
import hashlib
import json
import shutil
import sys
import tarfile

root = Path.cwd()
transfer = root / "transfer"
raw_fixture = transfer / "3dprinthub_data.json"
fixture_gz = transfer / "3dprinthub_data.json.gz"
manifest_path = transfer / "transfer_manifest.json"
overlong_report = transfer / "overlong_urls.json"

if not raw_fixture.is_file():
    raise SystemExit(f"Fixture was not created: {raw_fixture}")

try:
    with raw_fixture.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
except Exception as exc:
    raise SystemExit(f"Invalid fixture JSON: {exc}") from exc

if not isinstance(data, list):
    raise SystemExit("Fixture root must be a JSON list.")

model_counts = Counter(
    item.get("model", "")
    for item in data
    if isinstance(item, dict)
)

business_objects = sum(
    count
    for model, count in model_counts.items()
    if model.startswith(("website.", "store."))
)

if business_objects == 0:
    raise SystemExit(
        "No website/store business data was found in the SQLite fixture."
    )

length_checks = {
    ("store.catalogseedurl", "url"): 700,
    ("store.importedprintasset", "source_url"): 700,
}

overlong = []

for item in data:
    if not isinstance(item, dict):
        continue

    model = item.get("model", "")
    fields = item.get("fields") or {}

    for (target_model, field_name), limit in length_checks.items():
        if model != target_model:
            continue

        value = fields.get(field_name) or ""

        if len(value) > limit:
            overlong.append(
                {
                    "model": model,
                    "pk": item.get("pk"),
                    "field": field_name,
                    "length": len(value),
                    "limit": limit,
                    "value": value,
                }
            )

if overlong:
    overlong_report.write_text(
        json.dumps(overlong, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    raise SystemExit(
        f"{len(overlong)} overlong URL value(s) found. "
        f"See {overlong_report}"
    )

with raw_fixture.open("rb") as src, gzip.open(
    fixture_gz,
    "wb",
    compresslevel=9,
) as dst:
    shutil.copyfileobj(src, dst)

raw_fixture.unlink()

archive_info = {}

for folder_name in ("media", "private_media"):
    folder = root / folder_name
    folder.mkdir(parents=True, exist_ok=True)

    archive = transfer / f"{folder_name}.tar.gz"

    with tarfile.open(archive, "w:gz") as tar:
        tar.add(folder, arcname=folder_name)

    file_count = sum(1 for path in folder.rglob("*") if path.is_file())

    archive_info[archive.name] = {
        "file_count": file_count,
    }

def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()

package_files = [
    fixture_gz,
    transfer / "media.tar.gz",
    transfer / "private_media.tar.gz",
]

for path in package_files:
    archive_info.setdefault(path.name, {})
    archive_info[path.name].update(
        {
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
    )

manifest = {
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "project_root": str(root),
    "fixture_objects": len(data),
    "business_objects": business_objects,
    "model_counts": dict(sorted(model_counts.items())),
    "files": archive_info,
}

manifest_path.write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print("TRANSFER_PACKAGE_READY=OK")
print("TRANSFER_DIRECTORY:", transfer)
print("FIXTURE_OBJECTS:", len(data))
print("BUSINESS_OBJECTS:", business_objects)

for path in package_files + [manifest_path]:
    print(
        f"{path.name}: "
        f"{path.stat().st_size} bytes"
        + (
            f" sha256={sha256(path)}"
            if path != manifest_path
            else ""
        )
    )
'@ | python -

if ($LASTEXITCODE -ne 0) {
    throw "Transfer package creation failed."
}

Write-Host ""
Write-Host "== Files ready for upload =="

Get-ChildItem `
    ".\transfer\3dprinthub_data.json.gz",
    ".\transfer\media.tar.gz",
    ".\transfer\private_media.tar.gz",
    ".\transfer\transfer_manifest.json" |
    Select-Object Name, Length, FullName

Write-Host ""
Write-Host "Upload the four files above to:"
Write-Host "/home/sfkilvrs/3dprinthub/transfer/"
