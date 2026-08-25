from __future__ import annotations

import json
import re
from typing import Any

from django import template

register = template.Library()

_PLACEHOLDERS = {"", "-", "—", "none", "null", "unknown", "نامشخص"}
_HEADER_PATTERNS = {
    "source_name": re.compile(r"^\s*منبع\s*:\s*(.+?)\s*$", re.M),
    "source_url": re.compile(r"^\s*صفحه اصلی\s*:\s*(https?://\S+)\s*$", re.M),
    "designer": re.compile(r"^\s*طراح\s*:\s*(.+?)\s*$", re.M),
    "license_name": re.compile(r"^\s*مجوز\s*:\s*(.+?)\s*$", re.M),
    "commercial_license_source": re.compile(r"^\s*مدرک مجوز تجاری\s*:\s*(.+?)\s*$", re.M),
}


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _meaningful(value: Any) -> bool:
    text = _clean(value)
    return bool(text) and text.casefold() not in _PLACEHOLDERS


def _json_blocks(text: str) -> list[dict[str, Any]]:
    """Read embedded legacy Catalog JSON without ever exposing it to templates."""
    value = str(text or "")
    decoder = json.JSONDecoder()
    blocks: list[dict[str, Any]] = []
    index = 0
    while True:
        start = value.find("{", index)
        if start < 0:
            break
        try:
            parsed, length = decoder.raw_decode(value[start:])
        except (TypeError, ValueError, json.JSONDecodeError):
            index = start + 1
            continue
        if isinstance(parsed, dict):
            blocks.append(parsed)
        index = start + max(1, length)
    return blocks


def _header_value(text: str, key: str) -> str:
    match = _HEADER_PATTERNS[key].search(str(text or ""))
    if not match:
        return ""
    value = _clean(match.group(1))
    return value if _meaningful(value) else ""


def _dedupe(values) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        text = _clean(value)
        if not _meaningful(text):
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        output.append(text)
    return output


def _first(*values):
    for value in values:
        if _meaningful(value):
            return _clean(value)
    return ""


def _number(value):
    try:
        number = float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _format_weight(value) -> str:
    number = _number(value)
    if number is None:
        return ""
    if float(number).is_integer():
        return f"{int(number):,} گرم"
    return f"{number:,.1f} گرم"


def _format_minutes(value) -> str:
    number = _number(value)
    if number is None:
        return ""
    minutes = max(1, int(round(number)))
    hours, rest = divmod(minutes, 60)
    if hours and rest:
        return f"{hours} ساعت و {rest} دقیقه"
    if hours:
        return f"{hours} ساعت"
    return f"{rest} دقیقه"


def _profile(product):
    try:
        return product.catalog_profile
    except Exception:
        return None


def _variant_values(product) -> tuple[list[str], list[str], Any, Any]:
    materials: list[str] = []
    colors: list[str] = []
    weight = None
    minutes = None
    try:
        variants = product.variants.filter(is_active=True).select_related("material", "color").order_by("id")
    except Exception:
        variants = []
    for variant in variants:
        material = getattr(getattr(variant, "material", None), "name", "")
        color = getattr(getattr(variant, "color", None), "name", "")
        if material:
            materials.append(material)
        if color:
            colors.append(color)
        if weight is None:
            weight = getattr(variant, "final_weight_grams", None) or getattr(variant, "material_weight_grams", None)
        if minutes is None:
            minutes = getattr(variant, "print_time_minutes", None)
    return _dedupe(materials), _dedupe(colors), weight, minutes


def _payload_from_product(product) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for block in _json_blocks(getattr(product, "technical_notes", "")):
        merged.update(block)
    return merged


def _technical_features(profile, payload: dict[str, Any]) -> list[dict[str, str]]:
    candidates = {}
    if profile is not None:
        value = getattr(profile, "technical_features", None)
        if isinstance(value, dict):
            candidates.update(value)
    for key in ("technical_features", "source_specs_fa"):
        value = payload.get(key)
        if isinstance(value, dict):
            candidates.update(value)
    result: list[dict[str, str]] = []
    for key, value in candidates.items():
        label = _clean(key)
        display = _clean(value)
        if label and _meaningful(display):
            result.append({"label": label, "value": display})
    return result[:12]


@register.simple_tag
def product_public_facts(product) -> dict[str, Any]:
    """Return customer-facing structured facts from canonical + legacy catalog data.

    Internal audit/AI fields (provider/model/fingerprint/hash/batch/workflow payloads)
    are intentionally never returned.
    """
    notes = str(getattr(product, "technical_notes", "") or "")
    payload = _payload_from_product(product)
    profile = _profile(product)
    variant_materials, variant_colors, variant_weight, variant_minutes = _variant_values(product)

    source_name = _first(
        getattr(product, "source_name", ""),
        payload.get("source_name"),
        _header_value(notes, "source_name"),
    )
    source_url = _first(
        getattr(product, "source_url", ""),
        _header_value(notes, "source_url"),
    )
    designer = _first(
        getattr(product, "source_attribution", ""),
        payload.get("author_name"),
        _header_value(notes, "designer"),
    )
    license_name = _first(
        getattr(profile, "license_name", "") if profile is not None else "",
        payload.get("license_name"),
        _header_value(notes, "license_name"),
    )
    commercial_license_source = _header_value(notes, "commercial_license_source")

    weight = _format_weight(payload.get("estimated_weight_grams") or variant_weight)
    print_time = _format_minutes(payload.get("estimated_print_minutes") or variant_minutes)
    dimensions = _first(getattr(product, "dimensions", ""), payload.get("dimensions"))
    use_case = _first(payload.get("use_case_class"))

    materials = _dedupe(payload.get("materials") or variant_materials)
    if not materials:
        recs = payload.get("material_recommendations")
        if isinstance(recs, list):
            materials = _dedupe(item.get("material") for item in recs if isinstance(item, dict) and item.get("recommended"))
    colors = _dedupe(payload.get("colors") or variant_colors)
    categories = _dedupe(payload.get("desktop_catalog_categories_fa") or [])
    tags = _dedupe(payload.get("desktop_catalog_tags_fa") or [])
    sales_bullets = _dedupe(payload.get("sales_bullets") or [])[:8]

    specs: list[dict[str, str]] = []
    for label, value in (
        ("وزن تقریبی", weight),
        ("زمان تقریبی چاپ", print_time),
        ("ابعاد", dimensions),
        ("کاربری", use_case),
    ):
        if _meaningful(value):
            specs.append({"label": label, "value": value})

    if profile is not None:
        lead_min = getattr(profile, "lead_time_min_days", None)
        lead_max = getattr(profile, "lead_time_max_days", None)
        if lead_min or lead_max:
            if lead_min and lead_max and int(lead_max) != int(lead_min):
                lead = f"{int(lead_min)} تا {int(lead_max)} روز"
            else:
                lead = f"{int(lead_max or lead_min)} روز"
            specs.append({"label": "زمان آماده‌سازی", "value": lead})

    return {
        "source": {
            "name": source_name,
            "url": source_url,
            "designer": designer,
            "license_name": license_name,
            "commercial_license_source": commercial_license_source,
        },
        "specs": specs,
        "materials": materials,
        "colors": colors,
        "categories": categories,
        "tags": tags,
        "sales_bullets": sales_bullets,
        "technical_features": _technical_features(profile, payload),
    }
