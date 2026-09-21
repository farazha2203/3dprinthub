from __future__ import annotations

import asyncio
import json
import re
from copy import deepcopy
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


def _walk(node: Any):
    yield node
    if isinstance(node, dict):
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return int(default)
def _next_data(html_text: str) -> dict[str, Any]:
    match = re.search(
        r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        str(html_text or ""),
        re.I | re.S,
    )
    if not match:
        return {}
    try:
        data = json.loads(unescape(match.group(1)).strip())
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _profile_instances(next_data: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[list] = []
    for node in _walk(next_data):
        if not isinstance(node, dict):
            continue
        instances = node.get("instances")
        if not isinstance(instances, list):
            continue
        usable = [
            item for item in instances
            if isinstance(item, dict)
            and int(item.get("id") or 0) > 0
            and str(item.get("title") or "").strip()
        ]
        if usable:
            candidates.append(usable)
    if not candidates:
        return []
    return max(candidates, key=len)
def _compatibility(model_info: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    raw = [model_info.get("compatibility"), *(model_info.get("otherCompatibility") or [])]
    seen = set()
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = str(item.get("devProductName") or "").strip()
        nozzle = _float(item.get("nozzleDiameter"), 0)
        key = (name.casefold(), nozzle)
        if not name or key in seen:
            continue
        seen.add(key)
        rows.append({
            "printer": name,
            "model_code": str(item.get("devModelName") or "").strip(),
            "nozzle_diameter_mm": nozzle or None,
        })
    return rows


def _filaments(plates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for plate in plates:
        for item in plate.get("filaments") or []:
            if not isinstance(item, dict):
                continue
            material = str(item.get("type") or "").strip()
            color = str(item.get("color") or "").strip().upper()
            if not material:
                continue
            key = (material.casefold(), color.casefold())
            row = merged.setdefault(key, {
                "material": material,
                "color_hex": color,
                "used_grams": 0.0,
                "used_meters": 0.0,
            })
            row["used_grams"] += _float(item.get("usedG"), 0)
            row["used_meters"] += _float(item.get("usedM"), 0)
    return list(merged.values())
def extract_makerworld_print_profiles(
    next_data: dict[str, Any],
    *,
    source_url: str = "",
) -> list[dict[str, Any]]:
    if "makerworld.com" not in urlsplit(str(source_url or "")).netloc.casefold():
        return []
    output: list[dict[str, Any]] = []
    for instance in _profile_instances(next_data):
        if int(instance.get("status") or 1) <= 0:
            continue
        extension = instance.get("extention") if isinstance(instance.get("extention"), dict) else {}
        model_info = extension.get("modelInfo") if isinstance(extension.get("modelInfo"), dict) else {}
        plates = [dict(item) for item in (model_info.get("plates") or []) if isinstance(item, dict)]
        seconds = sum(max(0, _int(item.get("prediction"), 0)) for item in plates)
        weight = sum(max(0.0, _float(item.get("weight"), 0)) for item in plates)
        filament_rows = _filaments(plates)
        settings = model_info.get("projectSettings") if isinstance(model_info.get("projectSettings"), dict) else {}
        instance_id = int(instance.get("id") or 0)
        profile_id = int(instance.get("profileId") or 0)
        output.append({
            "schema": "phase50-a2w-source-profile-v1",
            "source": "makerworld",
            "instance_id": instance_id,
            "profile_id": profile_id,
            "name": str(instance.get("title") or f"Source Profile {instance_id}").strip(),
            "source_profile_url": re.sub(r"#.*$", "", str(source_url or "")) + f"#profileId-{instance_id}",
            "plate_count": len(plates),
            "print_seconds": seconds,
            "print_minutes": round(seconds / 60.0, 3) if seconds else 0,
            "weight_grams": round(weight, 3),
            "material_families": list(dict.fromkeys(row["material"] for row in filament_rows)),
            "filaments": filament_rows,
            "compatibility": _compatibility(model_info),
            "nozzle_diameter_mm": _float((model_info.get("compatibility") or {}).get("nozzleDiameter"), 0) or None,
            "layer_height_mm": _float(settings.get("layerHeight"), 0) or None,
            "wall_loops": _int(settings.get("wallLoops"), 0) or None,
            "sparse_infill_density": str(settings.get("sparseInfillDensity") or "").strip(),
            "has_filament_mixed": bool(model_info.get("hasFilamentMixed")),
            "plates": [
                {
                    "index": _int(item.get("index"), index),
                    "prediction_seconds": max(0, _int(item.get("prediction"), 0)),
                    "weight_grams": max(0.0, _float(item.get("weight"), 0)),
                }
                for index, item in enumerate(plates, 1)
            ],
        })
    return output


def extract_makerworld_print_profiles_from_html(
    html_text: str,
    *,
    source_url: str,
) -> list[dict[str, Any]]:
    return extract_makerworld_print_profiles(_next_data(html_text), source_url=source_url)
def latest_product_html(local_dir: Path) -> Path | None:
    root = Path(local_dir)
    if not root.is_dir():
        return None
    candidates = [
        path for path in root.rglob("model_*.html")
        if path.is_file()
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, str(path)))


def profiles_from_latest_capture(row: dict[str, Any]) -> tuple[list[dict[str, Any]], Path | None]:
    raw_dir = str(row.get("local_dir") or "").strip()
    if not raw_dir:
        return [], None
    capture = latest_product_html(Path(raw_dir))
    if capture is None:
        return [], None
    profiles = extract_makerworld_print_profiles_from_html(
        capture.read_text(encoding="utf-8", errors="ignore"),
        source_url=str(row.get("source_url") or ""),
    )
    return profiles, capture


def ledger_candidates(source_profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for index, source in enumerate(source_profiles, 1):
        if not isinstance(source, dict):
            continue
        instance_id = _int(source.get("instance_id"), 0)
        if instance_id <= 0:
            continue
        options = []
        for filament in source.get("filaments") or []:
            if not isinstance(filament, dict):
                continue
            material = str(filament.get("material") or "").strip()
            color_hex = str(filament.get("color_hex") or "").strip().upper()
            if not material:
                continue
            options.append({
                "material": material,
                "brand": "",
                "manufacturer": "",
                "color": color_hex or "Source color",
                "hex": color_hex,
                "description": "Source-declared material/color; local Filament mapping pending.",
            })
        output.append({
            "key": f"source-mw-{instance_id}",
            "name": str(source.get("name") or f"Source Profile {index}")[:120],
            "size_label": f"Source {instance_id}",
            "production_rows": [{
                "weight_grams": max(0.0, _float(source.get("weight_grams"), 0)),
                "print_time_minutes": max(1, int(round(_float(source.get("print_seconds"), 0) / 60.0))),
                "support_weight_grams": 0,
            }],
            "material_options": options,
            "pricing_strategy": "dynamic",
            "price_min": 0,
            "price_max": 0,
            "is_default": False,
            "is_active": True,
            "sort_order": 800 + index,
        })
    return output
def merge_source_ledger_profiles(
    current_profiles: list[dict[str, Any]],
    source_profiles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates = ledger_candidates(source_profiles)
    keys = {str(item.get("key") or "") for item in candidates}
    preserved = [
        deepcopy(item)
        for item in (current_profiles or [])
        if isinstance(item, dict) and str(item.get("key") or "") not in keys
    ]
    return [*preserved, *candidates]


def persist_source_profiles(
    db,
    product_id: int,
    profiles: list[dict[str, Any]],
    *,
    evidence_path: Path | None = None,
) -> dict[str, Any]:
    row = db.product(int(product_id))
    if row is None:
        raise RuntimeError("محصول پیدا نشد.")
    before = dict(row)
    payload = json.dumps(list(profiles or []), ensure_ascii=False)
    db.update_product(int(product_id), {"source_print_profiles_json": payload})
    after = dict(db.product(int(product_id)))
    try:
        db.save_history(
            int(product_id),
            "a2w_source_profiles_refreshed",
            before,
            after,
            f"Source profiles={len(profiles or [])}; evidence={evidence_path or '-'}",
        )
    except Exception:
        pass
    return {
        "product_id": int(product_id),
        "profiles": list(profiles or []),
        "profile_count": len(profiles or []),
        "evidence_path": str(evidence_path or ""),
    }


def refresh_product_source_profiles(
    db,
    product_id: int,
    *,
    fresh_capture: bool = True,
    progress=None,
) -> dict[str, Any]:
    row_obj = db.product(int(product_id))
    if row_obj is None:
        raise RuntimeError("محصول پیدا نشد.")
    row = dict(row_obj)
    source_url = str(row.get("source_url") or "").strip()
    if "makerworld.com" not in urlsplit(source_url).netloc.casefold():
        raise RuntimeError("W3 factual Profile import فعلاً فقط برای MakerWorld فعال است.")
    raw_dir = str(row.get("local_dir") or "").strip()
    if not raw_dir:
        raise RuntimeError("پوشه محلی محصول مشخص نیست.")
    local_dir = Path(raw_dir).resolve()
    cached_profiles, cached_path = profiles_from_latest_capture(row)
    capture_path = cached_path
    capture_error = ""

    if fresh_capture:
        try:
            if callable(progress):
                progress(10, "دریافت تازه صفحه محصول برای Print Profile")
            from .classic_methods import collect_classic_exact
            capture_root = local_dir / "source_profile_capture"
            result = asyncio.run(
                collect_classic_exact(
                    source_url,
                    capture_root,
                    headed=False,
                    capture_network=False,
                    download_images=False,
                )
            )
            capture_path = Path(str(result.get("html_path") or ""))
            if not capture_path.is_file():
                raise RuntimeError("Fresh source capture did not produce HTML.")
            cached_profiles = extract_makerworld_print_profiles_from_html(
                capture_path.read_text(encoding="utf-8", errors="ignore"),
                source_url=source_url,
            )
        except Exception as exc:
            capture_error = f"{type(exc).__name__}: {exc}"
            if not cached_profiles:
                raise RuntimeError(
                    "دریافت تازه Profile ناموفق بود و capture معتبر قبلی هم وجود ندارد: "
                    + capture_error
                ) from exc

    if not cached_profiles:
        raise RuntimeError("هیچ Print Profile factual در __NEXT_DATA__ محصول پیدا نشد.")
    if callable(progress):
        progress(85, f"{len(cached_profiles)} Source Profile factual پیدا شد")
    result = persist_source_profiles(
        db,
        int(product_id),
        cached_profiles,
        evidence_path=capture_path,
    )
    result["fresh_capture"] = bool(fresh_capture and not capture_error)
    result["capture_error"] = capture_error
    result["used_cached_capture"] = bool(capture_error)
    if callable(progress):
        progress(100, "Source Print Profileها ذخیره شدند")
    return result
