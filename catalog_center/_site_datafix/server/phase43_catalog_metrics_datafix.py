#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "43.1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    return str(value)


def ensure_json(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text:
            try:
                return json.loads(text)
            except Exception:
                return {}
    return {}


def walk_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_dicts(child)


def to_positive_number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or number <= 0:
        return None
    return number


def extract_makerworld_instances(*payloads: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple] = set()

    for payload in payloads:
        payload = ensure_json(payload)
        for node in walk_dicts(payload):
            # MakerWorld structured payload uses a list named "instances".
            instances = node.get("instances")
            if not isinstance(instances, list):
                continue
            for item in instances:
                if not isinstance(item, dict):
                    continue
                seconds = to_positive_number(item.get("print_time"))
                if seconds is None:
                    continue
                weight = to_positive_number(item.get("weight"))
                row = {
                    "id": item.get("id"),
                    "profile_id": item.get("profile_id"),
                    "title": str(item.get("title") or ""),
                    "print_time_seconds": int(round(seconds)),
                    "weight_grams": weight,
                }
                key = (
                    row["id"],
                    row["profile_id"],
                    row["print_time_seconds"],
                    row["weight_grams"],
                )
                if key not in seen:
                    seen.add(key)
                    rows.append(row)
    return rows


def is_makerworld_asset(asset: Any, metrics: Any | None) -> bool:
    url = str(getattr(asset, "source_url", "") or "").lower()
    if "makerworld." in url:
        return True

    if metrics is not None:
        source_kind = str(getattr(metrics, "source_kind", "") or "").lower()
        if source_kind == "makerworld":
            return True

    source = getattr(asset, "source", None)
    if source is not None:
        for name in ("kind", "slug", "name", "source_kind"):
            value = str(getattr(source, name, "") or "").lower()
            if "makerworld" in value:
                return True
    return False


def int_value(value: Any) -> int | None:
    number = to_positive_number(value)
    return int(round(number)) if number is not None else None


def select_evidence(
    technical_specs: dict[str, Any],
    metrics: Any | None,
    instances: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not instances:
        return None

    tech_current = int_value(technical_specs.get("estimated_print_minutes"))
    metric_current = int_value(
        getattr(metrics, "estimated_print_minutes", None)
        if metrics is not None else None
    )

    # The safe repair condition is exact evidence:
    # a field named "estimated_print_minutes" contains the exact raw MakerWorld
    # "print_time" seconds value. This avoids guessing or changing already-correct data.
    current_values = {value for value in (tech_current, metric_current) if value}
    if not current_values:
        return None

    exact = [
        row for row in instances
        if row["print_time_seconds"] in current_values
    ]
    if not exact:
        return None

    distinct_seconds = {row["print_time_seconds"] for row in exact}
    if len(distinct_seconds) != 1:
        return None

    seconds = next(iter(distinct_seconds))
    corrected_minutes = max(1, math.ceil(seconds / 60))

    # If the "corrected" number would be identical there is nothing to do.
    if corrected_minutes == seconds:
        return None

    matching = [row for row in exact if row["print_time_seconds"] == seconds]
    weights = {
        round(float(row["weight_grams"]), 3)
        for row in matching
        if row.get("weight_grams") is not None
    }
    unambiguous_weight = next(iter(weights)) if len(weights) == 1 else None

    return {
        "raw_seconds": seconds,
        "corrected_minutes": corrected_minutes,
        "technical_specs_current": tech_current,
        "metrics_current": metric_current,
        "weight_grams": unambiguous_weight,
        "matching_instances": matching,
    }


def bootstrap(project_root: Path):
    project_root = project_root.resolve()
    if not (project_root / "manage.py").is_file():
        raise SystemExit(f"STOP: manage.py not found: {project_root}")
    if not (project_root / "store" / "models.py").is_file():
        raise SystemExit(f"STOP: store/models.py not found: {project_root}")

    sys.path.insert(0, str(project_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    import django
    django.setup()

    from django.apps import apps
    from django.db import transaction

    try:
        Asset = apps.get_model("store", "ImportedPrintAsset")
        Metrics = apps.get_model("store", "CatalogAssetMetrics")
    except LookupError as exc:
        raise SystemExit(f"STOP: Required production models are missing: {exc}")

    return Asset, Metrics, transaction


def scan(Asset, Metrics) -> tuple[list[dict[str, Any]], dict[str, int]]:
    changes: list[dict[str, Any]] = []
    stats = {
        "assets_total": 0,
        "makerworld_assets": 0,
        "with_instances": 0,
        "repair_candidates": 0,
    }

    queryset = Asset._base_manager.all().order_by("pk")
    for asset in queryset.iterator(chunk_size=200):
        stats["assets_total"] += 1
        metrics = Metrics._base_manager.filter(asset_id=asset.pk).first()

        if not is_makerworld_asset(asset, metrics):
            continue
        stats["makerworld_assets"] += 1

        technical_specs = ensure_json(getattr(asset, "technical_specs", {}))
        source_payload = ensure_json(getattr(asset, "source_payload", {}))
        raw_metrics = ensure_json(
            getattr(metrics, "raw_metrics", {}) if metrics is not None else {}
        )

        instances = extract_makerworld_instances(
            source_payload,
            technical_specs,
            raw_metrics,
        )
        if not instances:
            continue
        stats["with_instances"] += 1

        evidence = select_evidence(technical_specs, metrics, instances)
        if evidence is None:
            continue

        stats["repair_candidates"] += 1
        changes.append(
            {
                "asset_id": asset.pk,
                "source_url": str(getattr(asset, "source_url", "") or ""),
                "title": str(getattr(asset, "title", "") or ""),
                "metrics_id": getattr(metrics, "pk", None),
                "evidence": json_safe(evidence),
            }
        )

    return changes, stats


def backup_rows(project_root: Path, Asset, Metrics, candidates: list[dict[str, Any]]) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    root = project_root / ".phase-backups" / f"phase43-datafix-{stamp}"
    root.mkdir(parents=True, exist_ok=False)
    output = root / "catalog_metrics_before.json"

    rows = []
    for candidate in candidates:
        asset = Asset._base_manager.get(pk=candidate["asset_id"])
        metrics = (
            Metrics._base_manager.filter(pk=candidate["metrics_id"]).first()
            if candidate.get("metrics_id") else None
        )
        rows.append(
            {
                "asset_id": asset.pk,
                "technical_specs": json_safe(getattr(asset, "technical_specs", {})),
                "metrics": None if metrics is None else {
                    "id": metrics.pk,
                    "estimated_print_minutes": json_safe(
                        getattr(metrics, "estimated_print_minutes", None)
                    ),
                    "estimated_weight_grams": json_safe(
                        getattr(metrics, "estimated_weight_grams", None)
                    ),
                },
            }
        )

    payload = {
        "phase": 43,
        "version": VERSION,
        "created_at": utc_now(),
        "rows": rows,
    }
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output


def apply_changes(project_root: Path, Asset, Metrics, transaction, candidates: list[dict[str, Any]]):
    backup = backup_rows(project_root, Asset, Metrics, candidates)
    changed_assets = 0
    changed_metrics = 0
    weight_backfills = 0

    with transaction.atomic():
        for candidate in candidates:
            asset = Asset._base_manager.select_for_update().get(
                pk=candidate["asset_id"]
            )
            metrics = (
                Metrics._base_manager.select_for_update()
                .filter(asset_id=asset.pk)
                .first()
            )

            technical_specs = ensure_json(getattr(asset, "technical_specs", {}))
            source_payload = ensure_json(getattr(asset, "source_payload", {}))
            raw_metrics = ensure_json(
                getattr(metrics, "raw_metrics", {}) if metrics is not None else {}
            )
            instances = extract_makerworld_instances(
                source_payload, technical_specs, raw_metrics
            )
            evidence = select_evidence(technical_specs, metrics, instances)
            if evidence is None:
                continue

            seconds = evidence["raw_seconds"]
            minutes = evidence["corrected_minutes"]
            weight = evidence["weight_grams"]

            asset_fields = []
            current_tech = int_value(technical_specs.get("estimated_print_minutes"))
            if current_tech == seconds:
                technical_specs = dict(technical_specs)
                technical_specs["estimated_print_minutes"] = minutes

                if (
                    weight is not None
                    and to_positive_number(
                        technical_specs.get("estimated_weight_grams")
                    ) is None
                ):
                    technical_specs["estimated_weight_grams"] = weight
                    weight_backfills += 1

                asset.technical_specs = technical_specs
                asset_fields.append("technical_specs")

            if asset_fields:
                asset.save(update_fields=asset_fields)
                changed_assets += 1

            if metrics is not None:
                metric_fields = []
                current_metric = int_value(
                    getattr(metrics, "estimated_print_minutes", None)
                )
                if current_metric == seconds:
                    metrics.estimated_print_minutes = minutes
                    metric_fields.append("estimated_print_minutes")

                if (
                    weight is not None
                    and to_positive_number(
                        getattr(metrics, "estimated_weight_grams", None)
                    ) is None
                ):
                    metrics.estimated_weight_grams = weight
                    metric_fields.append("estimated_weight_grams")
                    weight_backfills += 1

                if metric_fields:
                    metrics.save(update_fields=sorted(set(metric_fields)))
                    changed_metrics += 1

    return {
        "backup": str(backup),
        "changed_assets": changed_assets,
        "changed_metrics": changed_metrics,
        "weight_backfills": weight_backfills,
    }


def rollback(Asset, Metrics, transaction, backup_path: Path) -> dict[str, int]:
    payload = json.loads(backup_path.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise SystemExit("STOP: Invalid rollback backup.")

    assets = 0
    metrics_count = 0
    with transaction.atomic():
        for row in rows:
            asset = Asset._base_manager.select_for_update().get(pk=row["asset_id"])
            asset.technical_specs = row.get("technical_specs") or {}
            asset.save(update_fields=["technical_specs"])
            assets += 1

            metric_row = row.get("metrics")
            if metric_row and metric_row.get("id"):
                metrics = Metrics._base_manager.select_for_update().get(
                    pk=metric_row["id"]
                )
                metrics.estimated_print_minutes = metric_row.get(
                    "estimated_print_minutes"
                )
                metrics.estimated_weight_grams = metric_row.get(
                    "estimated_weight_grams"
                )
                metrics.save(
                    update_fields=[
                        "estimated_print_minutes",
                        "estimated_weight_grams",
                    ]
                )
                metrics_count += 1

    return {"restored_assets": assets, "restored_metrics": metrics_count}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="3DPrintHub Phase43.1 safe MakerWorld catalog metrics data repair"
    )
    parser.add_argument(
        "--project-root",
        default="/home/sfkilvrs/3dprinthub",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply only unambiguous repairs. Default is dry-run.",
    )
    parser.add_argument(
        "--rollback",
        type=Path,
        help="Restore a catalog_metrics_before.json backup.",
    )
    parser.add_argument(
        "--json-report",
        type=Path,
        help="Optional output report path.",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    Asset, Metrics, transaction = bootstrap(project_root)

    if args.rollback:
        result = rollback(Asset, Metrics, transaction, args.rollback.resolve())
        print(json.dumps({"mode": "rollback", **result}, ensure_ascii=False))
        print("PHASE43_DATAFIX_ROLLBACK=OK")
        return 0

    candidates, stats = scan(Asset, Metrics)
    result: dict[str, Any] = {
        "phase": 43,
        "version": VERSION,
        "mode": "apply" if args.apply else "dry-run",
        "created_at": utc_now(),
        "stats": stats,
        "candidates": candidates,
    }

    if args.apply and candidates:
        result["apply"] = apply_changes(
            project_root, Asset, Metrics, transaction, candidates
        )
        remaining, verify_stats = scan(Asset, Metrics)
        result["verification"] = {
            "remaining_candidates": len(remaining),
            "stats": verify_stats,
        }
        if remaining:
            raise SystemExit(
                "STOP: Verification still found repair candidates. "
                "Database transaction completed, but inspect the report before continuing."
            )
    elif args.apply:
        result["apply"] = {
            "backup": None,
            "changed_assets": 0,
            "changed_metrics": 0,
            "weight_backfills": 0,
        }

    report_path = args.json_report
    if report_path is None:
        report_dir = project_root / "phase43_reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_path = report_dir / f"catalog_metrics_datafix_{stamp}.json"

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"PHASE43_DATAFIX_MODE={result['mode']}")
    for key, value in stats.items():
        print(f"{key.upper()}={value}")
    print(f"REPORT={report_path}")
    if args.apply:
        print("DATABASE_MIGRATION=NOT_RUN")
        print("PHASE43_DATAFIX_APPLY=OK")
    else:
        print("DATABASE_MUTATION=NOT_EXECUTED")
        print("PHASE43_DATAFIX_DRY_RUN=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
