from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from store.models import CatalogAssetMetrics


BACKUP_VERSION = "43.1.0"


def _positive_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        number = int(float(value))
    except (TypeError, ValueError, OverflowError):
        return None
    return number if number > 0 else None


def seconds_to_minutes(value: Any) -> int | None:
    seconds = _positive_int(value)
    if seconds is None:
        return None
    return max(1, math.ceil(seconds / 60))


def extract_raw_print_seconds(payload: Any) -> set[int]:
    """Extract MakerWorld fields known to represent raw print seconds."""
    found: set[int] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                normalized = str(key).replace("_", "").lower()
                if normalized in {
                    "printtime",
                    "printtimeseconds",
                    "prediction",
                    "predictionseconds",
                }:
                    parsed = _positive_int(nested)
                    if parsed is not None:
                        found.add(parsed)
                elif isinstance(nested, (dict, list, tuple)):
                    walk(nested)
        elif isinstance(value, (list, tuple)):
            for item in value:
                walk(item)

    walk(payload)
    return found


def build_repair_candidate(metric: CatalogAssetMetrics) -> dict[str, Any] | None:
    asset = metric.asset
    if asset is None:
        return None

    source = getattr(asset, "source", None)
    source_code = str(getattr(source, "code", "") or "").strip().lower()
    source_kind = str(getattr(metric, "source_kind", "") or "").strip().lower()
    if source_code != "makerworld" and source_kind != "makerworld":
        return None

    current = _positive_int(metric.estimated_print_minutes)
    if current is None:
        return None

    raw_seconds = extract_raw_print_seconds(getattr(asset, "source_payload", None) or {})
    if current not in raw_seconds:
        return None

    corrected = seconds_to_minutes(current)
    if corrected is None or corrected == current:
        return None

    specs = dict(getattr(asset, "technical_specs", None) or {})
    spec_current = _positive_int(specs.get("estimated_print_minutes"))

    return {
        "metric_id": metric.pk,
        "asset_id": asset.pk,
        "title": str(getattr(asset, "title", "") or ""),
        "before_minutes": current,
        "after_minutes": corrected,
        "raw_seconds": sorted(raw_seconds),
        "update_asset_specs": spec_current == current,
        "spec_before": specs.get("estimated_print_minutes"),
    }


def backup_root() -> Path:
    root = Path(settings.BASE_DIR) / ".phase-backups" / "phase43-catalog-metrics"
    root.mkdir(parents=True, exist_ok=True)
    return root


class Command(BaseCommand):
    help = (
        "Repair MakerWorld print times stored as seconds in minute fields. "
        "Default mode is read-only dry-run."
    )

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--rollback", type=str)
        parser.add_argument("--limit", type=int, default=0)

    def handle(self, *args, **options):
        rollback_path = options.get("rollback")
        if rollback_path:
            self._rollback(Path(rollback_path))
            return

        apply_changes = bool(options.get("apply"))
        limit = max(0, int(options.get("limit") or 0))

        queryset = (
            CatalogAssetMetrics.objects
            .select_related("asset", "asset__source")
            .order_by("pk")
        )

        candidates: list[dict[str, Any]] = []
        for metric in queryset.iterator(chunk_size=250):
            candidate = build_repair_candidate(metric)
            if candidate:
                candidates.append(candidate)
                if limit and len(candidates) >= limit:
                    break

        self.stdout.write(f"PHASE43_DATAFIX_VERSION={BACKUP_VERSION}")
        self.stdout.write(f"MODE={'APPLY' if apply_changes else 'DRY_RUN'}")
        self.stdout.write(f"CANDIDATE_COUNT={len(candidates)}")

        for row in candidates[:50]:
            self.stdout.write(
                "CANDIDATE "
                f"metric={row['metric_id']} "
                f"asset={row['asset_id']} "
                f"before={row['before_minutes']} "
                f"after={row['after_minutes']} "
                f"title={row['title'][:80]}"
            )

        if len(candidates) > 50:
            self.stdout.write(f"CANDIDATE_OUTPUT_TRUNCATED={len(candidates) - 50}")

        if not apply_changes:
            self.stdout.write("DATABASE_WRITE=NO")
            self.stdout.write("NEXT=Run again with --apply only after reviewing this output.")
            self.stdout.write("PHASE43_CATALOG_METRICS_DATAFIX=DRY_RUN_OK")
            return

        if not candidates:
            self.stdout.write("DATABASE_WRITE=NO_CHANGES_NEEDED")
            self.stdout.write("PHASE43_CATALOG_METRICS_DATAFIX=APPLY_OK")
            return

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = backup_root() / f"phase43_catalog_metrics_{stamp}.json"
        backup_path.write_text(
            json.dumps(
                {
                    "version": BACKUP_VERSION,
                    "created_at_utc": datetime.now(timezone.utc).isoformat(),
                    "rows": candidates,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        changed_metrics = 0
        changed_assets = 0
        with transaction.atomic():
            for row in candidates:
                metric = (
                    CatalogAssetMetrics.objects
                    .select_for_update()
                    .select_related("asset", "asset__source")
                    .get(pk=row["metric_id"])
                )
                asset = metric.asset
                refreshed = build_repair_candidate(metric)
                if not refreshed:
                    continue
                if (
                    refreshed["before_minutes"] != row["before_minutes"]
                    or refreshed["after_minutes"] != row["after_minutes"]
                ):
                    continue

                metric.estimated_print_minutes = row["after_minutes"]
                metric.save(update_fields=["estimated_print_minutes"])
                changed_metrics += 1

                if row["update_asset_specs"] and asset is not None:
                    specs = dict(asset.technical_specs or {})
                    current_spec = _positive_int(specs.get("estimated_print_minutes"))
                    if current_spec == row["before_minutes"]:
                        specs["estimated_print_minutes"] = row["after_minutes"]
                        asset.technical_specs = specs
                        asset.save(update_fields=["technical_specs"])
                        changed_assets += 1

        self.stdout.write(f"BACKUP_FILE={backup_path}")
        self.stdout.write(f"METRICS_CHANGED={changed_metrics}")
        self.stdout.write(f"ASSET_SPECS_CHANGED={changed_assets}")
        self.stdout.write("DATABASE_WRITE=COMMITTED")
        self.stdout.write("PHASE43_CATALOG_METRICS_DATAFIX=APPLY_OK")

    def _rollback(self, backup_path: Path) -> None:
        backup_path = backup_path.expanduser().resolve()
        allowed = backup_root().resolve()
        try:
            backup_path.relative_to(allowed)
        except ValueError as exc:
            raise CommandError(f"Rollback file must be under {allowed}") from exc

        if not backup_path.is_file():
            raise CommandError(f"Backup file not found: {backup_path}")

        document = json.loads(backup_path.read_text(encoding="utf-8"))
        if document.get("version") != BACKUP_VERSION:
            raise CommandError("Unsupported backup version.")
        rows = document.get("rows")
        if not isinstance(rows, list):
            raise CommandError("Invalid backup rows.")

        restored_metrics = 0
        restored_assets = 0
        with transaction.atomic():
            for row in rows:
                metric = (
                    CatalogAssetMetrics.objects
                    .select_for_update()
                    .select_related("asset")
                    .get(pk=int(row["metric_id"]))
                )
                asset = metric.asset
                metric.estimated_print_minutes = int(row["before_minutes"])
                metric.save(update_fields=["estimated_print_minutes"])
                restored_metrics += 1

                if bool(row.get("update_asset_specs")) and asset is not None:
                    specs = dict(asset.technical_specs or {})
                    specs["estimated_print_minutes"] = row.get("spec_before")
                    asset.technical_specs = specs
                    asset.save(update_fields=["technical_specs"])
                    restored_assets += 1

        self.stdout.write(f"RESTORED_BACKUP={backup_path}")
        self.stdout.write(f"METRICS_RESTORED={restored_metrics}")
        self.stdout.write(f"ASSET_SPECS_RESTORED={restored_assets}")
        self.stdout.write("PHASE43_CATALOG_METRICS_ROLLBACK=OK")
