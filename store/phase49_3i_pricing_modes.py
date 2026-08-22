from __future__ import annotations


RANGE_CODE = "range"
RANGE_LABEL = "بازه قیمت"


def _money(value, default=0) -> int:
    try:
        return max(0, int(float(str(value if value not in (None, "") else default).replace(",", "").strip() or 0)))
    except Exception:
        return max(0, int(default or 0))


def _range_values(data: dict, kwargs: dict, product) -> tuple[int, int]:
    minimum = _money(kwargs.get("price_min") or data.get("price_min"), getattr(product, "fixed_price", 0))
    maximum = _money(kwargs.get("price_max") or data.get("price_max"), minimum)
    if minimum and maximum and maximum < minimum:
        minimum, maximum = maximum, minimum
    return minimum, maximum


def install() -> None:
    from . import epic49_catalog_profile

    if getattr(epic49_catalog_profile, "_phase49_3i_pricing_modes_installed", False):
        return

    # IMPORTANT: do not mutate ProductCatalogProfile.pricing_strategy.choices here.
    # The migration-owned field already has enough max_length to persist `range`,
    # and changing choices at runtime makes `makemigrations --check` generate a
    # metadata-only AlterField migration. Phase49.3I intentionally remains
    # schema-free. Windows is the operator UI that exposes the three business
    # modes; server import stores the semantic `range` value directly.
    original_sync = epic49_catalog_profile.sync_catalog_profile

    def sync_catalog_profile(product, asset, data: dict, **kwargs):
        profile = original_sync(product, asset, data, **kwargs)
        raw_strategy = str(data.get("pricing_strategy") or "").strip().lower()
        if raw_strategy != RANGE_CODE:
            return profile
        minimum, maximum = _range_values(data, kwargs, product)
        changed = []
        for key, value in {
            "pricing_strategy": RANGE_CODE,
            "price_mode": "range",
            "price_min": minimum,
            "price_max": maximum,
        }.items():
            if getattr(profile, key, None) != value:
                setattr(profile, key, value)
                changed.append(key)
        if changed:
            profile.save(update_fields=[*changed, "updated_at"])
        return profile

    epic49_catalog_profile.sync_catalog_profile = sync_catalog_profile
    epic49_catalog_profile._phase49_3i_pricing_modes_installed = True
