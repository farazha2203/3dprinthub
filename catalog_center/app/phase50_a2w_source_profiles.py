from __future__ import annotations

import asyncio
import json
import re
from copy import deepcopy
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .epic49_desktop_schema import normalize_material_color_options


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


_DIM_LABEL = (
    r"(?:small|medium|large|extra\s+large|mini|standard)\s+"
    r"(?:version|size)|(?:size|version)\s*#?\s*\d+"
)
_DIM_AXIS_RE = re.compile(
    rf"(?i)(?P<label>{_DIM_LABEL})\s*[:\-–—]?\s*"
    r"(?P<axis>height|width|length|depth)\s*[:=]\s*"
    r"(?P<value>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>mm|cm|m|inches?|inch|in)"
    r"(?=$|[\s•·;,:!?<]|\d+[.)])"
)
_DIM_LABELED_FULL_RE = re.compile(
    rf"(?i)(?P<label>{_DIM_LABEL})\s*[:\-–—]?\s*"
    r"(?:dimensions?|size)?\s*[:=]?\s*"
    r"(?P<a>\d+(?:\.\d+)?)\s*[x×*]\s*"
    r"(?P<b>\d+(?:\.\d+)?)\s*[x×*]\s*"
    r"(?P<c>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>mm|cm|m|inches?|inch|in)"
    r"(?=$|[\s•·;,:!?<]|\d+[.)])"
)
_DIM_GENERIC_FULL_RE = re.compile(
    r"(?i)(?:dimensions?|model\s+size|object\s+size|part\s+size)\s*[:=\-]?\s*"
    r"(?P<a>\d+(?:\.\d+)?)\s*[x×*]\s*"
    r"(?P<b>\d+(?:\.\d+)?)\s*[x×*]\s*"
    r"(?P<c>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>mm|cm|m|inches?|inch|in)"
    r"(?=$|[\s•·;,:!?<]|\d+[.)])"
)


def _to_cm(value: Any, unit: str) -> float:
    number = max(0.0, _float(value, 0))
    token = str(unit or "cm").strip().casefold()
    factor = {
        "mm": 0.1,
        "cm": 1.0,
        "m": 100.0,
        "in": 2.54,
        "inch": 2.54,
        "inches": 2.54,
    }.get(token, 1.0)
    return round(number * factor, 3)


def _plain_dimension_text(value: Any) -> str:
    text = unescape(str(value or ""))
    text = re.sub(
        r"(?i)<br\s*/?>|</p\s*>|</li\s*>|</h[1-6]\s*>",
        "\n",
        text,
    )
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\x07", "\n")
    text = re.sub(r"[\t\r\f\v ]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


def _description_from_html(html_text: str) -> str:
    for tag in re.findall(r"<meta\b[^>]*>", str(html_text or ""), re.I | re.S):
        if not re.search(
            r"(?i)(?:name|property)\s*=\s*[\"'](?:description|og:description)[\"']",
            tag,
        ):
            continue
        match = re.search(
            r"(?i)content\s*=\s*([\"'])(.*?)\1",
            tag,
            re.S,
        )
        if match:
            return unescape(match.group(2)).strip()
    return ""


def extract_ordered_dimension_evidence(value: Any) -> list[dict[str, Any]]:
    text = _plain_dimension_text(value)
    events: list[tuple[int, str, dict[str, float], str]] = []
    for match in _DIM_LABELED_FULL_RE.finditer(text):
        events.append((
            match.start(),
            match.group("label"),
            {
                "length": _to_cm(match.group("a"), match.group("unit")),
                "width": _to_cm(match.group("b"), match.group("unit")),
                "height": _to_cm(match.group("c"), match.group("unit")),
            },
            match.group(0).strip(),
        ))
    for match in _DIM_AXIS_RE.finditer(text):
        axis = match.group("axis").casefold()
        if axis == "depth":
            axis = "width"
        events.append((
            match.start(),
            match.group("label"),
            {axis: _to_cm(match.group("value"), match.group("unit"))},
            match.group(0).strip(),
        ))
    for match in _DIM_GENERIC_FULL_RE.finditer(text):
        events.append((
            match.start(),
            "Dimensions",
            {
                "length": _to_cm(match.group("a"), match.group("unit")),
                "width": _to_cm(match.group("b"), match.group("unit")),
                "height": _to_cm(match.group("c"), match.group("unit")),
            },
            match.group(0).strip(),
        ))

    ordered: list[dict[str, Any]] = []
    by_label: dict[str, dict[str, Any]] = {}
    for position, label, dims, evidence in sorted(events, key=lambda item: item[0]):
        key = re.sub(r"\s+", " ", str(label or "")).strip().casefold()
        current = by_label.get(key)
        if current is None:
            current = {
                "label": re.sub(r"\s+", " ", str(label or "")).strip(),
                "dimensions_cm": {},
                "evidence": [],
                "_position": position,
            }
            by_label[key] = current
            ordered.append(current)
        current["dimensions_cm"].update(
            {axis: value for axis, value in dims.items() if value > 0}
        )
        if evidence and evidence not in current["evidence"]:
            current["evidence"].append(evidence)

    result: list[dict[str, Any]] = []
    for item in ordered:
        dims = dict(item.get("dimensions_cm") or {})
        if not dims:
            continue
        result.append({
            "label": str(item.get("label") or ""),
            "dimensions_cm": dims,
            "known_axes": [
                axis for axis in ("length", "width", "height")
                if _float(dims.get(axis), 0) > 0
            ],
            "evidence": " | ".join(item.get("evidence") or []),
            "source": "source_description",
            "is_estimated": False,
        })
    return result


def enrich_source_profiles_with_description_dimensions(
    profiles: list[dict[str, Any]],
    description: Any,
) -> list[dict[str, Any]]:
    output = [deepcopy(item) for item in (profiles or []) if isinstance(item, dict)]
    evidence = extract_ordered_dimension_evidence(description)
    if not output or not evidence:
        return output
    if len(output) != len(evidence):
        return output
    for profile, fact in zip(output, evidence):
        dims = dict(fact.get("dimensions_cm") or {})
        profile["dimensions_cm"] = dims
        profile["dimension_source"] = "source_description"
        profile["dimension_is_estimated"] = False
        profile["dimension_label"] = str(fact.get("label") or "")
        profile["dimension_evidence"] = str(fact.get("evidence") or "")
        profile["dimension_known_axes"] = list(fact.get("known_axes") or [])
        profile["dimension_binding"] = "ordered_description_to_profile"
    return output


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
    html_text = capture.read_text(encoding="utf-8", errors="ignore")
    profiles = extract_makerworld_print_profiles_from_html(
        html_text,
        source_url=str(row.get("source_url") or ""),
    )
    description = (
        _description_from_html(html_text)
        or str(row.get("source_description") or "")
        or str(row.get("source_short_description") or "")
    )
    profiles = enrich_source_profiles_with_description_dimensions(
        profiles,
        description,
    )
    return profiles, capture


def _profile_dimension_payload(source: dict[str, Any]) -> dict[str, Any]:
    """Build operational Profile dimensions while preserving factual provenance.

    Owner rule: when Source provides exactly one dimensional axis for a Size,
    use that numeric value for all three Profile axes. The supplied axis remains
    factual; the other two axes are explicitly marked as owner-rule estimates.
    """
    raw_dims = {
        axis: max(0.0, _float((source.get("dimensions_cm") or {}).get(axis), 0))
        for axis in ("length", "width", "height")
    }
    factual_axes = [
        axis
        for axis in (source.get("dimension_known_axes") or [])
        if axis in {"length", "width", "height"} and raw_dims.get(axis, 0) > 0
    ]
    if not factual_axes:
        factual_axes = [
            axis for axis in ("length", "width", "height")
            if raw_dims.get(axis, 0) > 0
        ]

    dims = dict(raw_dims)
    axis_sources = {
        axis: "source_description"
        for axis in factual_axes
    }
    owner_equal_fill = False
    if len(factual_axes) == 1:
        scalar = raw_dims[factual_axes[0]]
        if scalar > 0:
            for axis in ("length", "width", "height"):
                if dims.get(axis, 0) <= 0:
                    dims[axis] = scalar
                    axis_sources[axis] = "owner_equal_dimension_rule"
                    owner_equal_fill = True

    known_axes = [
        axis for axis in ("length", "width", "height")
        if dims.get(axis, 0) > 0
    ]
    if not known_axes:
        return {
            "dimensions_cm": {},
            "dimension_axis_sources": {},
            "dimension_known_axes": [],
            "dimension_factual_axes": [],
            "dimension_source": "",
            "dimension_is_estimated": False,
        }

    if owner_equal_fill:
        dimension_source = "mixed"
    else:
        dimension_source = str(
            source.get("dimension_source") or "source_description"
        )
    return {
        "dimensions_cm": {
            axis: dims[axis]
            for axis in ("length", "width", "height")
            if dims.get(axis, 0) > 0
        },
        "dimension_axis_sources": axis_sources,
        "dimension_known_axes": known_axes,
        "dimension_factual_axes": factual_axes,
        "dimension_source": dimension_source,
        "dimension_is_estimated": bool(
            owner_equal_fill or source.get("dimension_is_estimated", False)
        ),
    }


def _source_dimension_size_label(
    source: dict[str, Any],
    instance_id: int,
) -> str:
    payload = _profile_dimension_payload(source)
    dims = dict(payload.get("dimensions_cm") or {})
    label = re.sub(
        r"(?i)\s+(?:version|size)\b",
        "",
        str(source.get("dimension_label") or ""),
    ).strip()
    if all(_float(dims.get(axis), 0) > 0 for axis in ("length", "width", "height")):
        prefix = f"{label} " if label else ""
        return (
            f"{prefix}{_float(dims['length']):g} x "
            f"{_float(dims['width']):g} x "
            f"{_float(dims['height']):g} cm"
        )[:80]
    tokens = []
    for axis, short in (("length", "L"), ("width", "W"), ("height", "H")):
        value = _float(dims.get(axis), 0)
        if value > 0:
            tokens.append(f"{short}={value:g}")
    if tokens:
        prefix = f"{label} " if label else ""
        return f"{prefix}{' '.join(tokens)} cm"[:80]
    return f"Source {instance_id}"


def _source_dimension_fields(source: dict[str, Any]) -> dict[str, Any]:
    payload = _profile_dimension_payload(source)
    dims = dict(payload.get("dimensions_cm") or {})
    output: dict[str, Any] = {}
    for axis, field in (
        ("length", "part_length_cm"),
        ("width", "part_width_cm"),
        ("height", "part_height_cm"),
    ):
        value = _float(dims.get(axis), 0)
        if value > 0:
            output[field] = value
    if output:
        output.update({
            "dimension_source": str(payload.get("dimension_source") or ""),
            "dimension_is_estimated": bool(
                payload.get("dimension_is_estimated", False)
            ),
            "dimension_label": str(source.get("dimension_label") or ""),
            "dimension_evidence": str(source.get("dimension_evidence") or ""),
            "dimension_known_axes": list(
                payload.get("dimension_known_axes") or []
            ),
            "dimension_factual_axes": list(
                payload.get("dimension_factual_axes") or []
            ),
            "dimension_binding": str(
                source.get("dimension_binding")
                or "ordered_description_to_profile"
            ),
            "dimension_axis_sources": dict(
                payload.get("dimension_axis_sources") or {}
            ),
        })
    return output


def _fallback_dimensions(value: Any) -> dict[str, float]:
    if isinstance(value, dict):
        return {
            axis: max(0.0, _float(value.get(axis), 0))
            for axis in ("length", "width", "height")
        }
    if isinstance(value, (list, tuple)) and len(value) >= 3:
        return {
            axis: max(0.0, _float(raw, 0))
            for axis, raw in zip(("length", "width", "height"), value[:3])
        }
    scalar = max(0.0, _float(value, 0))
    return {axis: scalar for axis in ("length", "width", "height")}


def patch_source_ledger_dimensions(
    current_profiles: list[dict[str, Any]],
    source_profiles: list[dict[str, Any]],
    *,
    owner_fallback_by_key: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_by_key = {
        f"source-mw-{_int(source.get('instance_id'), 0)}": dict(source)
        for source in (source_profiles or [])
        if isinstance(source, dict) and _int(source.get("instance_id"), 0) > 0
    }
    fallbacks = dict(owner_fallback_by_key or {})
    output: list[dict[str, Any]] = []
    changed_keys: list[str] = []
    exact_keys: list[str] = []
    estimated_keys: list[str] = []

    for raw in current_profiles or []:
        if not isinstance(raw, dict):
            continue
        item = deepcopy(raw)
        key = str(item.get("key") or "")
        source = source_by_key.get(key)
        if source is None:
            output.append(item)
            continue

        before = deepcopy(item)
        exact_fields = _source_dimension_fields(source)
        source_axis_sources = dict(
            exact_fields.get("dimension_axis_sources") or {}
        )
        axis_sources = dict(item.get("dimension_axis_sources") or {})
        for axis, field in (
            ("length", "part_length_cm"),
            ("width", "part_width_cm"),
            ("height", "part_height_cm"),
        ):
            value = _float(exact_fields.get(field), 0)
            if value <= 0:
                continue
            authority = str(source_axis_sources.get(axis) or "")
            if authority == "source_description":
                item[field] = value
                axis_sources[axis] = authority
            elif (
                authority == "owner_equal_dimension_rule"
                and _float(item.get(field), 0) <= 0
            ):
                item[field] = value
                axis_sources[axis] = authority

        fallback = _fallback_dimensions(fallbacks.get(key))
        used_fallback = False
        if any(value > 0 for value in fallback.values()):
            for axis, field in (
                ("length", "part_length_cm"),
                ("width", "part_width_cm"),
                ("height", "part_height_cm"),
            ):
                if _float(item.get(field), 0) <= 0 and fallback[axis] > 0:
                    item[field] = fallback[axis]
                    axis_sources[axis] = "owner_estimated"
                    used_fallback = True

        exact_used = any(
            value == "source_description" for value in axis_sources.values()
        )
        estimated_used = any(
            value in {"owner_estimated", "owner_equal_dimension_rule"}
            for value in axis_sources.values()
        )
        if exact_used or estimated_used:
            item["dimension_axis_sources"] = axis_sources
            if exact_used and estimated_used:
                item["dimension_source"] = "mixed"
            elif exact_used:
                item["dimension_source"] = "source_description"
            else:
                item["dimension_source"] = "owner_estimated"
            item["dimension_is_estimated"] = estimated_used
            item["dimension_known_axes"] = [
                axis for axis in ("length", "width", "height")
                if axis in axis_sources
            ]
            item["dimension_factual_axes"] = [
                axis
                for axis in (exact_fields.get("dimension_factual_axes") or [])
                if axis in {"length", "width", "height"}
            ]
            if exact_used:
                item["dimension_label"] = str(
                    source.get("dimension_label") or item.get("dimension_label") or ""
                )
                item["dimension_evidence"] = str(
                    source.get("dimension_evidence")
                    or item.get("dimension_evidence")
                    or ""
                )
                item["dimension_binding"] = str(
                    source.get("dimension_binding")
                    or "ordered_description_to_profile"
                )
                if (
                    not str(item.get("size_label") or "").strip()
                    or str(item.get("size_label") or "").startswith("Source ")
                ):
                    item["size_label"] = _source_dimension_size_label(
                        source,
                        _int(source.get("instance_id"), 0),
                    )
            elif estimated_used:
                item["dimension_label"] = str(
                    item.get("dimension_label") or "Owner fallback"
                )
                item["dimension_evidence"] = str(
                    item.get("dimension_evidence")
                    or "Owner-approved estimated fallback"
                )
                item["dimension_binding"] = str(
                    item.get("dimension_binding") or "owner_estimated_fallback"
                )

        if item != before:
            changed_keys.append(key)
        if exact_used:
            exact_keys.append(key)
        if used_fallback:
            estimated_keys.append(key)
        output.append(item)

    return output, {
        "changed_keys": changed_keys,
        "exact_keys": exact_keys,
        "estimated_keys": estimated_keys,
        "changed_count": len(changed_keys),
    }


def _source_material_families(source: dict[str, Any]) -> set[str]:
    families = {
        str(value or "").strip().casefold()
        for value in (source.get("material_families") or [])
        if str(value or "").strip()
    }
    for filament in source.get("filaments") or []:
        if not isinstance(filament, dict):
            continue
        material = str(filament.get("material") or "").strip()
        if material:
            families.add(material.casefold())
    return families


def _source_placeholder_options(source: dict[str, Any]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for filament in source.get("filaments") or []:
        if not isinstance(filament, dict):
            continue
        material = str(filament.get("material") or "").strip()
        color_hex = str(filament.get("color_hex") or "").strip().upper()
        if not material:
            continue
        key = (material.casefold(), color_hex.casefold())
        if key in seen:
            continue
        seen.add(key)
        output.append({
            "material": material,
            "brand": "",
            "manufacturer": "",
            "color": color_hex or "Source color",
            "hex": color_hex,
            "description": (
                "Source-declared material/color; local Filament mapping pending."
            ),
        })
    return output


def local_filament_options_for_source(
    source: dict[str, Any],
    filament_rows: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    families = _source_material_families(source)
    if not families or not filament_rows:
        return []
    output: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str, str]] = set()
    for raw in filament_rows:
        if not isinstance(raw, dict):
            continue
        material = str(
            raw.get("material")
            or raw.get("material_name")
            or ""
        ).strip()
        if material.casefold() not in families:
            continue
        normalized = normalize_material_color_options([raw])
        if not normalized:
            continue
        item = dict(normalized[0])
        item["local_offer_id"] = _int(
            raw.get("id") or raw.get("_row_id"),
            0,
        )
        key = (
            str(item.get("material") or "").strip().casefold(),
            str(item.get("brand") or "").strip().casefold(),
            str(item.get("color") or "").strip().casefold(),
            str(item.get("color_type") or "").strip().casefold(),
            str(item.get("color_finish") or "").strip().casefold(),
        )
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def _material_option_key(item: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        str(item.get("material") or item.get("material_name") or "")
        .strip().casefold(),
        str(item.get("brand") or item.get("brand_name") or "")
        .strip().casefold(),
        str(item.get("color") or item.get("color_name") or "")
        .strip().casefold(),
        str(item.get("color_type") or item.get("type") or "solid")
        .strip().casefold(),
        str(item.get("color_finish") or item.get("finish") or "matte")
        .strip().casefold(),
    )


def _merge_local_filament_options(
    existing: list[dict[str, Any]],
    local_options: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    normalized_existing = normalize_material_color_options(existing or [])
    output: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str, str]] = set()

    for item in normalized_existing:
        description = str(item.get("description") or "")
        is_source_placeholder = (
            not str(item.get("brand") or "").strip()
            and "local Filament mapping pending" in description
        )
        if is_source_placeholder:
            continue
        key = _material_option_key(item)
        if key in seen:
            continue
        seen.add(key)
        output.append(dict(item))

    for item in local_options:
        key = _material_option_key(item)
        if key in seen:
            continue
        seen.add(key)
        output.append(dict(item))
    return output


def ledger_candidates(
    source_profiles: list[dict[str, Any]],
    *,
    filament_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for index, source in enumerate(source_profiles, 1):
        if not isinstance(source, dict):
            continue
        instance_id = _int(source.get("instance_id"), 0)
        if instance_id <= 0:
            continue
        options = local_filament_options_for_source(
            source,
            filament_rows,
        )
        if not options:
            options = _source_placeholder_options(source)
        candidate = {
            "key": f"source-mw-{instance_id}",
            "name": str(source.get("name") or f"Source Profile {index}")[:120],
            "size_label": _source_dimension_size_label(source, instance_id),
            "production_rows": [{
                "weight_grams": max(0.0, _float(source.get("weight_grams"), 0)),
                "print_time_minutes": max(
                    1,
                    int(round(_float(source.get("print_seconds"), 0) / 60.0)),
                ),
                "support_weight_grams": 0,
            }],
            "material_options": options,
            "pricing_strategy": "dynamic",
            "price_min": 0,
            "price_max": 0,
            "is_default": False,
            "is_active": True,
            "sort_order": 800 + index,
        }
        candidate.update(_source_dimension_fields(source))
        output.append(candidate)
    return output


def merge_source_ledger_profiles(
    current_profiles: list[dict[str, Any]],
    source_profiles: list[dict[str, Any]],
    *,
    filament_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    candidates = ledger_candidates(
        source_profiles,
        filament_rows=filament_rows,
    )
    candidate_map = {
        str(item.get("key") or ""): deepcopy(item)
        for item in candidates
        if str(item.get("key") or "")
    }
    source_map = {
        f"source-mw-{_int(item.get('instance_id'), 0)}": dict(item)
        for item in (source_profiles or [])
        if isinstance(item, dict) and _int(item.get("instance_id"), 0) > 0
    }
    current = [
        deepcopy(item)
        for item in (current_profiles or [])
        if isinstance(item, dict)
    ]
    existing_keys = {str(item.get("key") or "") for item in current}

    for item in current:
        key = str(item.get("key") or "")
        source = source_map.get(key)
        if source is None:
            continue
        local_options = local_filament_options_for_source(
            source,
            filament_rows,
        )
        if local_options:
            item["material_options"] = _merge_local_filament_options(
                [
                    dict(option)
                    for option in (item.get("material_options") or [])
                    if isinstance(option, dict)
                ],
                local_options,
            )

    for key, candidate in candidate_map.items():
        if key not in existing_keys:
            current.append(candidate)
    patched, _ = patch_source_ledger_dimensions(
        current,
        source_profiles,
    )
    return patched


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
            html_text = capture_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
            cached_profiles = extract_makerworld_print_profiles_from_html(
                html_text,
                source_url=source_url,
            )
            description = (
                _description_from_html(html_text)
                or str(row.get("source_description") or "")
                or str(row.get("source_short_description") or "")
            )
            cached_profiles = enrich_source_profiles_with_description_dimensions(
                cached_profiles,
                description,
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
