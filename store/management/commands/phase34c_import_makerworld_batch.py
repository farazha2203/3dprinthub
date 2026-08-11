from __future__ import annotations

import json
import time
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from store.management.commands.phase34c_import_makerworld_export import (
    import_manifest,
)


class Command(BaseCommand):
    help = "Import one auto-discovered MakerWorld batch."

    def add_arguments(self, parser):
        parser.add_argument("batch_path")
        parser.add_argument(
            "--dry-run",
            action="store_true",
        )
        parser.add_argument(
            "--continue-on-error",
            action="store_true",
        )

    def handle(self, *args, **options):
        batch_path = Path(
            options["batch_path"]
        ).resolve()
        batch_manifest_path = (
            batch_path / "batch_manifest.json"
        )

        if not batch_manifest_path.is_file():
            raise CommandError(
                f"Batch manifest was not found: "
                f"{batch_manifest_path}"
            )

        batch = json.loads(
            batch_manifest_path.read_text(encoding="utf-8")
        )
        rows = list(batch.get("models") or [])

        imported = 0
        failed = 0
        skipped = 0
        results: list[dict] = []

        for row in rows:
            if row.get("status") != "collected":
                skipped += 1
                continue

            relative_manifest = str(row.get("manifest") or "")
            manifest_path = batch_path / Path(relative_manifest)

            if options["dry_run"]:
                if not manifest_path.is_file():
                    failed += 1
                    results.append(
                        {
                            "model_id": row.get("model_id"),
                            "status": "failed",
                            "error": "manifest missing",
                        }
                    )
                else:
                    results.append(
                        {
                            "model_id": row.get("model_id"),
                            "status": "dry_run_ok",
                        }
                    )
                continue

            try:
                with transaction.atomic():
                    asset = import_manifest(manifest_path)

                imported += 1
                results.append(
                    {
                        "model_id": row.get("model_id"),
                        "status": "imported",
                        "asset_id": asset.pk,
                        "title": asset.title,
                        "image_count": asset.images.count(),
                    }
                )
            except Exception as error:
                failed += 1
                results.append(
                    {
                        "model_id": row.get("model_id"),
                        "status": "failed",
                        "error": (
                            f"{type(error).__name__}: {error}"
                        ),
                    }
                )
                if not options["continue_on_error"]:
                    break

        report = {
            "batch_name": batch.get("batch_name"),
            "processed_at": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ",
                time.gmtime(),
            ),
            "imported_count": imported,
            "failed_count": failed,
            "skipped_count": skipped,
            "dry_run": bool(options["dry_run"]),
            "results": results,
        }

        report_path = batch_path / "server_import_report.json"
        report_path.write_text(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        self.stdout.write(f"IMPORTED_COUNT={imported}")
        self.stdout.write(f"FAILED_COUNT={failed}")
        self.stdout.write(f"SKIPPED_COUNT={skipped}")
        self.stdout.write(f"REPORT={report_path}")

        if failed:
            raise CommandError(
                f"Batch import has {failed} failure(s)."
            )

        self.stdout.write(
            "PHASE34C_AUTO_BATCH_IMPORT=OK"
        )
