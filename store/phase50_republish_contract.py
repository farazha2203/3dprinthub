from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path

from .phase50_public_media_name import canonical_server_media_filename


def _json_list(value) -> list:
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return parsed if isinstance(parsed, list) else []


def _int(value, default=0) -> int:
    try:
        return int(float(str(value if value not in (None, "") else default).replace(",", "")))
    except Exception:
        return int(default)


def _decimal(value, default=0) -> Decimal:
    try:
        return Decimal(str(value if value not in (None, "") else default))
    except Exception:
        return Decimal(str(default))


def _text(value) -> str:
    return str(value or "").strip()


def _basename(field_file) -> str:
    return Path(str(getattr(field_file, "name", "") or "").replace("\\", "/")).name


def _field_sha256(field_file) -> str:
    name = str(getattr(field_file, "name", "") or "").strip()
    storage = getattr(field_file, "storage", None)
    if not name or storage is None:
        return ""
    digest = hashlib.sha256()
    try:
        with storage.open(name, "rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except Exception:
        return ""
    return digest.hexdigest()


def _expected_media(data: dict) -> list[dict]:
    selected = _json_list(data.get("selected_images_json") or data.get("images_json"))
    local_names = _json_list(data.get("local_image_files_json"))
    metadata = _json_list(data.get("image_metadata_json"))
    alt_texts = _json_list(data.get("image_alt_texts_json"))
    output = []
    for index in range(len(selected)):
        meta = metadata[index] if index < len(metadata) and isinstance(metadata[index], dict) else {}
        raw_filename = (
            _text(meta.get("seo_filename"))
            or (Path(_text(local_names[index])).name if index < len(local_names) else "")
        )
        filename = canonical_server_media_filename(data, index, raw_filename)
        output.append({
            "filename": filename,
            "sha256": _text(meta.get("final_sha256")).lower(),
            "alt": _text(alt_texts[index] if index < len(alt_texts) else meta.get("alt_text")),
        })
    return output


def _expected_profiles(data: dict) -> list[dict]:
    output = []
    for item in _json_list(data.get("sales_profiles_json")):
        if not isinstance(item, dict) or not bool(item.get("is_active", True)):
            continue
        output.append(item)
    return output


def _append(mismatches: list[str], key: str, expected, actual) -> None:
    if expected != actual:
        mismatches.append(f"{key}: expected={expected!r} actual={actual!r}")


def _append_material(mismatches: list[str], key: str, expected, actual) -> None:
    """Compare material identity the same way Store sync resolves it.

    Material rows are resolved case-insensitively (for example pla and PLA
    refer to the same Material). Republish parity must not roll back solely
    because the persisted canonical Material.name uses different case.
    """
    expected_text = _text(expected)
    actual_text = _text(actual)
    if expected_text.casefold() != actual_text.casefold():
        mismatches.append(f"{key}: expected={expected!r} actual={actual!r}")


def verify_product_republish_contract(product, asset, data: dict) -> dict:
    """Verify the imported Store Product mirrors the current Desktop batch.

    This is intentionally fail-closed for fields that the Desktop batch owns.
    Server-computed dynamic prices are not compared to stale Desktop display
    snapshots; instead their pricing inputs and the authoritative price range
    are verified.
    """

    mismatches: list[str] = []

    expected_title = _text(data.get("title_fa"))[:220]
    if expected_title:
        _append(mismatches, "product.title", expected_title, _text(product.title))

    expected_meta_title = _text(data.get("seo_title_fa"))[:180]
    if expected_meta_title:
        _append(mismatches, "product.meta_title", expected_meta_title, _text(product.meta_title))

    expected_meta_description = _text(data.get("seo_description_fa")).replace("\n", " ")[:320]
    if expected_meta_description:
        _append(
            mismatches,
            "product.meta_description",
            expected_meta_description,
            _text(product.meta_description).replace("\n", " "),
        )

    profile = getattr(product, "catalog_profile", None)
    desktop_id = _int(data.get("desktop_product_id"), 0)
    if desktop_id:
        _append(
            mismatches,
            "profile.desktop_product_id",
            desktop_id,
            _int(getattr(profile, "desktop_product_id", 0), 0),
        )

    expected_profiles = _expected_profiles(data)
    expected_min = _int(data.get("price_min"), 0)
    expected_max = _int(data.get("price_max"), expected_min)
    if expected_min:
        _append(mismatches, "profile.price_min", expected_min, _int(getattr(profile, "price_min", 0), 0))
        # Profile-driven products intentionally keep Product.fixed_price at 0:
        # each active Variant/Profile is the price authority. Requiring the
        # public range minimum in Product.fixed_price creates a false parity
        # failure after sync_desktop_profile_matrix correctly clears it.
        _append(
            mismatches,
            "product.fixed_price",
            0 if expected_profiles else expected_min,
            _int(getattr(product, "fixed_price", 0), 0),
        )
    if expected_max:
        _append(mismatches, "profile.price_max", expected_max, _int(getattr(profile, "price_max", 0), 0))

    expected_media = _expected_media(data)
    gallery = list(product.images.all().order_by("sort_order", "id"))
    if expected_media:
        _append(mismatches, "media.gallery_count", len(expected_media), len(gallery))
        first = expected_media[0]
        if first["filename"]:
            _append(mismatches, "media.main_filename", first["filename"], _basename(product.main_image))
        if first["sha256"]:
            _append(mismatches, "media.main_sha256", first["sha256"], _field_sha256(product.main_image))
        for index, expected in enumerate(expected_media):
            if index >= len(gallery):
                break
            row = gallery[index]
            if expected["filename"]:
                _append(mismatches, f"media.gallery[{index}].filename", expected["filename"], _basename(row.image))
            if expected["sha256"]:
                _append(mismatches, f"media.gallery[{index}].sha256", expected["sha256"], _field_sha256(row.image))
            if expected["alt"]:
                _append(mismatches, f"media.gallery[{index}].alt", expected["alt"], _text(row.alt_text))
    prefix = f"CC-P{product.pk}-"
    actual_profiles = list(
        product.variants.filter(code__startswith=prefix, is_active=True)
        .select_related("material", "color", "quality")
        .order_by("sales_profile_sort_order", "pk")
    )
    active_total = product.variants.filter(is_active=True).count()
    if expected_profiles:
        _append(mismatches, "variants.active_count", len(expected_profiles), len(actual_profiles))
        _append(mismatches, "variants.total_active_count", len(expected_profiles), active_total)
        actual_by_key = {
            _text(getattr(row, "sales_profile_key", "")): row
            for row in actual_profiles
        }
        expected_keys = {_text(item.get("key") or item.get("profile_key")) for item in expected_profiles}
        actual_keys = set(actual_by_key)
        _append(mismatches, "variants.keys", sorted(expected_keys), sorted(actual_keys))

        for item in expected_profiles:
            key = _text(item.get("key") or item.get("profile_key"))
            row = actual_by_key.get(key)
            if row is None:
                continue
            color = getattr(row, "color", None)
            material = getattr(row, "material", None)

            scalar_checks = {
                "size_label": (_text(item.get("size_label")), _text(getattr(row, "size_label", ""))),
                "material": (_text(item.get("material")), _text(getattr(material, "name", ""))),
                "color": (_text(item.get("color")), _text(getattr(color, "name", ""))),
                "brand": (_text(item.get("brand") or item.get("brand_name")), _text(getattr(color, "brand_name", ""))),
                "manufacturer": (
                    _text(item.get("manufacturer") or item.get("manufacturer_name") or item.get("brand") or item.get("brand_name")),
                    _text(getattr(color, "manufacturer_name", "")),
                ),
                "stock_status": (_text(item.get("stock_status") or "made_to_order"), _text(getattr(row, "stock_status", ""))),
            }
            for field, (expected, actual) in scalar_checks.items():
                if not expected:
                    continue
                mismatch_key = f"variant[{key}].{field}"
                if field == "material":
                    _append_material(mismatches, mismatch_key, expected, actual)
                else:
                    _append(mismatches, mismatch_key, expected, actual)

            numeric_checks = {
                "final_weight_grams": (
                    _decimal(item.get("weight_grams", item.get("final_weight_grams", 0))),
                    _decimal(getattr(row, "final_weight_grams", 0)),
                ),
                "material_weight_grams": (
                    _decimal(item.get("material_weight_grams", item.get("weight_grams", 0))),
                    _decimal(getattr(row, "material_weight_grams", 0)),
                ),
                "support_weight_grams": (
                    _decimal(item.get("support_weight_grams", 0)),
                    _decimal(getattr(row, "support_weight_grams", 0)),
                ),
                "print_time_minutes": (
                    _decimal(max(1, _int(item.get("print_time_minutes"), 60))),
                    _decimal(getattr(row, "print_time_minutes", 0)),
                ),
                "part_length_cm": (_decimal(item.get("part_length_cm", 0)), _decimal(getattr(row, "part_length_cm", 0))),
                "part_width_cm": (_decimal(item.get("part_width_cm", 0)), _decimal(getattr(row, "part_width_cm", 0))),
                "part_height_cm": (_decimal(item.get("part_height_cm", 0)), _decimal(getattr(row, "part_height_cm", 0))),
                "fixed_price_override": (
                    _decimal(item.get("fixed_price", 0)),
                    _decimal(getattr(row, "fixed_price_override", 0)),
                ),
            }
            for field, (expected, actual) in numeric_checks.items():
                _append(mismatches, f"variant[{key}].{field}", expected, actual)

            if color is not None:
                color_checks = {
                    "roll_weight_grams": (item.get("roll_weight_grams", 1000), getattr(color, "roll_weight_grams", 0)),
                    "stock_roll_count": (item.get("stock_roll_count", 0), getattr(color, "stock_roll_count_snapshot", 0)),
                    "purchase_price_per_roll": (item.get("purchase_price_per_roll", 0), getattr(color, "purchase_price_per_roll", 0)),
                    "sale_price_per_roll": (item.get("sale_price_per_roll", 0), getattr(color, "sale_price_per_roll", 0)),
                    "print_hourly_rate": (item.get("print_hourly_rate", 0), getattr(color, "print_hourly_rate", 0)),
                    "supervision_hourly_rate": (item.get("supervision_hourly_rate", 0), getattr(color, "supervision_hourly_rate", 0)),
                    "preheat_hours": (item.get("preheat_hours", 0), getattr(color, "preheat_hours", 0)),
                    "preheat_temperature_c": (item.get("preheat_temperature_c", 0), getattr(color, "preheat_temperature_c", 0)),
                    "preheat_hourly_rate": (item.get("preheat_hourly_rate", 0), getattr(color, "preheat_hourly_rate", 0)),
                }
                for field, (expected, actual) in color_checks.items():
                    _append(
                        mismatches,
                        f"variant[{key}].filament.{field}",
                        _decimal(expected),
                        _decimal(actual),
                    )

    return {
        "ok": not mismatches,
        "mismatches": mismatches,
        "media_count": len(expected_media),
        "profile_count": len(expected_profiles),
        "desktop_product_id": desktop_id,
    }
