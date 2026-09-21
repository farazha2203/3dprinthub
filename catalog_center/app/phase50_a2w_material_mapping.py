from __future__ import annotations

import json
import re
from typing import Any

from .epic49_desktop_schema import (
    effective_filament_offer_price_per_gram,
    normalize_material_color_options,
    normalize_palette_hexes,
)
from .phase49_3i39_professional_commerce import formula_price_breakdown

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _strict_hex(value: Any) -> str:
    text = str(value or "").strip().upper()
    return text if _HEX_RE.fullmatch(text) else ""


def _rgb(value: str) -> tuple[int, int, int] | None:
    text = _strict_hex(value)
    if not text:
        return None
    return (
        int(text[1:3], 16),
        int(text[3:5], 16),
        int(text[5:7], 16),
    )


def _distance_sq(left: str, right: str) -> int | None:
    a = _rgb(left)
    b = _rgb(right)
    if a is None or b is None:
        return None
    return sum((a[index] - b[index]) ** 2 for index in range(3))


def _offer_palette(raw: dict[str, Any]) -> list[str]:
    """Only explicit persisted HEX/palette evidence; never infer from color names."""
    return normalize_palette_hexes(
        raw.get("palette_hexes") or raw.get("palette_hex_json") or [],
        raw.get("hex") or raw.get("hex_code") or "",
        raw.get("secondary_hex") or "",
        raw.get("tertiary_hex") or "",
    )


def _normalize_offer(raw: dict[str, Any]) -> dict[str, Any] | None:
    normalized = normalize_material_color_options([raw])
    if not normalized:
        return None
    item = dict(normalized[0])
    item["local_offer_id"] = int(raw.get("id") or raw.get("_row_id") or 0)
    item["explicit_palette_hexes"] = _offer_palette(raw)
    return item


def _source_key(source_profile: dict[str, Any]) -> str:
    instance_id = int(float(source_profile.get("instance_id") or 0))
    return f"source-mw-{instance_id}" if instance_id > 0 else ""


def _ledger_by_key(ledger_profiles: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("key") or ""): dict(item)
        for item in (ledger_profiles or [])
        if isinstance(item, dict) and str(item.get("key") or "")
    }


def _candidate_sort_key(item: dict[str, Any]) -> tuple:
    rank = {"exact_hex": 0, "distance_only": 1, "no_local_hex": 2}.get(
        str(item.get("color_match") or ""),
        9,
    )
    distance = item.get("color_distance_sq")
    distance_value = int(distance) if distance is not None else 10**9
    offer = dict(item.get("offer") or {})
    return (
        rank,
        distance_value,
        str(offer.get("brand") or "").casefold(),
        str(offer.get("color") or "").casefold(),
        int(offer.get("local_offer_id") or 0),
    )


def build_source_filament_mapping_preview(
    source_profiles: list[dict[str, Any]],
    ledger_profiles: list[dict[str, Any]],
    filament_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a read-only W4 mapping preview.

    Material-family matching is exact/case-insensitive. Color confidence uses
    only explicit Local HEX/palette facts. Localized color names are never
    interpreted as HEX or used as an auto-match signal.
    """
    real_offers: list[dict[str, Any]] = []
    for raw in filament_rows or []:
        if not isinstance(raw, dict):
            continue
        normalized = _normalize_offer(raw)
        if normalized is not None:
            real_offers.append(normalized)

    ledger = _ledger_by_key(ledger_profiles)
    profiles_out: list[dict[str, Any]] = []
    total_slots = 0
    total_candidates = 0
    exact_count = 0
    distance_count = 0
    unknown_count = 0

    for source in source_profiles or []:
        if not isinstance(source, dict):
            continue
        key = _source_key(source)
        if not key:
            continue
        ledger_profile = dict(ledger.get(key) or {})
        production_rows = [
            dict(item)
            for item in (ledger_profile.get("production_rows") or [])
            if isinstance(item, dict)
        ]
        production = production_rows[0] if production_rows else {
            "weight_grams": float(source.get("weight_grams") or 0),
            "support_weight_grams": 0,
            "print_time_minutes": max(
                1,
                int(round(float(source.get("print_seconds") or 0) / 60.0)),
            ),
        }
        source_filaments = [
            dict(item)
            for item in (source.get("filaments") or [])
            if isinstance(item, dict)
        ]
        single_slot = len(source_filaments) == 1
        slots: list[dict[str, Any]] = []

        for slot_index, slot in enumerate(source_filaments, 1):
            material = str(slot.get("material") or "").strip()
            source_hex = _strict_hex(slot.get("color_hex"))
            used_grams = max(0.0, float(slot.get("used_grams") or 0))
            candidates: list[dict[str, Any]] = []

            for offer in real_offers:
                if str(offer.get("material") or "").strip().casefold() != material.casefold():
                    continue
                palette = [
                    _strict_hex(value)
                    for value in (offer.get("explicit_palette_hexes") or [])
                    if _strict_hex(value)
                ]
                if source_hex and source_hex in palette:
                    match = "exact_hex"
                    distance = 0
                elif source_hex and palette:
                    distances = [
                        value
                        for value in (_distance_sq(source_hex, color) for color in palette)
                        if value is not None
                    ]
                    match = "distance_only"
                    distance = min(distances) if distances else None
                else:
                    match = "no_local_hex"
                    distance = None

                rate_per_gram = float(effective_filament_offer_price_per_gram(offer))
                slot_material_cost = int(round(rate_per_gram * used_grams))
                full_profile_total = None
                if single_slot:
                    full_profile_total = int(
                        formula_price_breakdown(
                            offer,
                            production,
                            support_multiplier=ledger_profile.get(
                                "support_cost_multiplier", 1
                            ),
                            assembly_fee=ledger_profile.get("assembly_fee", 0),
                        ).get("total")
                        or 0
                    )

                row = {
                    "offer": dict(offer),
                    "source_material": material,
                    "source_hex": source_hex,
                    "used_grams": used_grams,
                    "color_match": match,
                    "color_distance_sq": distance,
                    "rate_per_gram": rate_per_gram,
                    "slot_material_cost": slot_material_cost,
                    "single_slot_profile_total": full_profile_total,
                }
                candidates.append(row)
                if match == "exact_hex":
                    exact_count += 1
                elif match == "distance_only":
                    distance_count += 1
                else:
                    unknown_count += 1

            candidates.sort(key=_candidate_sort_key)
            total_slots += 1
            total_candidates += len(candidates)
            slots.append({
                "slot_index": slot_index,
                "source_material": material,
                "source_hex": source_hex,
                "used_grams": used_grams,
                "used_meters": max(0.0, float(slot.get("used_meters") or 0)),
                "candidate_count": len(candidates),
                "exact_match_count": sum(
                    1 for item in candidates
                    if item.get("color_match") == "exact_hex"
                ),
                "candidates": candidates,
            })

        profiles_out.append({
            "profile_key": key,
            "profile_name": str(source.get("name") or key),
            "instance_id": int(float(source.get("instance_id") or 0)),
            "profile_id": int(float(source.get("profile_id") or 0)),
            "print_seconds": int(float(source.get("print_seconds") or 0)),
            "print_minutes": float(source.get("print_minutes") or 0),
            "weight_grams": float(source.get("weight_grams") or 0),
            "slot_count": len(slots),
            "single_slot": bool(single_slot),
            "slots": slots,
        })

    return {
        "schema": "phase50-a2w-w4-material-mapping-preview-v1",
        "profile_count": len(profiles_out),
        "slot_count": total_slots,
        "candidate_count": total_candidates,
        "exact_hex_candidate_count": exact_count,
        "distance_only_candidate_count": distance_count,
        "no_local_hex_candidate_count": unknown_count,
        "profiles": profiles_out,
        "mutates_ledger": False,
        "requires_operator_review": True,
    }


def preview_summary(preview: dict[str, Any]) -> str:
    return (
        f"{int(preview.get('profile_count') or 0)} Profile / "
        f"{int(preview.get('slot_count') or 0)} source slot / "
        f"{int(preview.get('candidate_count') or 0)} Local candidate / "
        f"exact HEX={int(preview.get('exact_hex_candidate_count') or 0)}"
    )
