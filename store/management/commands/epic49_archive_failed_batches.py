from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


BATCH_NAME = re.compile(r"^desktop_catalog_v85_[0-9]{8}_[0-9]{6}$")
FAILED_STATUSES = {
    "bridge_exception",
    "import_failed",
    "completed_with_errors",
}


def _pending_root() -> Path:
    configured = getattr(settings, "CATALOG_BRIDGE_PENDING_ROOT", None)
    return Path(configured or (Path(settings.BASE_DIR) / "imports" / "desktop_catalog" / "pending")).resolve()


def _diagnostic(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _is_failed_diagnostic(payload: dict) -> bool:
    status = str(payload.get("status") or "").strip()
    if status in FAILED_STATUSES:
        return True
    ack = payload.get("ack") if isinstance(payload.get("ack"), dict) else {}
    return int(ack.get("failed_count") or 0) > 0


class Command(BaseCommand):
    help = "Safely archive failed Epic49 desktop catalog batches; never deletes batch data."

    def add_arguments(self, parser):
        parser.add_argument("--batch", action="append", default=[])
        parser.add_argument("--all-failed", action="store_true")
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        pending = _pending_root()
        diagnostics = pending.parent / "diagnostics"
        archive = pending.parent / "archive" / "failed"
        requested = [str(x or "").strip() for x in options["batch"] if str(x or "").strip()]

        for name in requested:
            if not BATCH_NAME.fullmatch(name):
                raise CommandError(f"Invalid batch name: {name}")
        if not requested and not options["all_failed"]:
            raise CommandError("Specify --batch NAME or --all-failed.")

        if requested:
            candidates = [pending / name for name in requested]
        else:
            candidates = sorted(path for path in pending.glob("desktop_catalog_v85_*") if path.is_dir())

        checked = eligible = archived = skipped = 0
        for batch in candidates:
            checked += 1
            name = batch.name
            if not batch.is_dir():
                self.stdout.write(f"SKIP_MISSING BATCH={name}")
                skipped += 1
                continue
            diag_path = diagnostics / f"{name}.json"
            if not diag_path.is_file():
                self.stdout.write(f"SKIP_NO_DIAGNOSTIC BATCH={name}")
                skipped += 1
                continue
            payload = _diagnostic(diag_path)
            if not payload:
                self.stdout.write(f"SKIP_INVALID_DIAGNOSTIC BATCH={name}")
                skipped += 1
                continue
            if not _is_failed_diagnostic(payload):
                self.stdout.write(f"SKIP_NOT_FAILED BATCH={name} STATUS={payload.get('status') or '-'}")
                skipped += 1
                continue

            eligible += 1
            destination = archive / name
            self.stdout.write(
                f"ARCHIVE_CANDIDATE BATCH={name} STATUS={payload.get('status') or '-'} "
                f"SOURCE={batch} DEST={destination}"
            )
            if not options["apply"]:
                continue
            if destination.exists():
                raise CommandError(f"Archive destination already exists: {destination}")
            archive.mkdir(parents=True, exist_ok=True)
            shutil.move(str(batch), str(destination))
            if not destination.is_dir() or batch.exists():
                raise CommandError(f"Archive move verification failed for {name}")
            archived += 1
            self.stdout.write(f"ARCHIVED BATCH={name}")

        self.stdout.write(f"CHECKED={checked}")
        self.stdout.write(f"ELIGIBLE={eligible}")
        self.stdout.write(f"ARCHIVED={archived}")
        self.stdout.write(f"SKIPPED={skipped}")
        self.stdout.write(f"MODE={'APPLY' if options['apply'] else 'DRY_RUN'}")
        self.stdout.write("EPIC49_FAILED_BATCH_ARCHIVE=OK")
