from __future__ import annotations


def install() -> None:
    """Finalize Phase49.3F prices only after the catalog profile strategy is saved.

    The mature import path creates/updates variants before the final profile sync.
    Recalculate after that sync, then derive the public min/max range from the same
    cached prices used by Cart/Checkout. No legacy product is changed.
    """
    from . import epic49_catalog_profile

    if getattr(epic49_catalog_profile, "_phase49_3f_pricing_finalize_installed", False):
        return

    original = epic49_catalog_profile.sync_catalog_profile

    def sync_catalog_profile(product, asset, data: dict, **kwargs):
        profile = original(product, asset, data, **kwargs)
        strategy = str(getattr(profile, "pricing_strategy", "legacy") or "legacy").strip().lower()
        if strategy not in {"fixed", "dynamic"}:
            return profile

        active = list(
            product.variants.filter(is_active=True)
            .select_related("material", "quality", "color")
            .order_by("id")
        )
        prices: list[int] = []
        for variant in active:
            prices.append(int(variant.recalculate_price(save=True) or 0))
        prices = [value for value in prices if value > 0]
        if not prices:
            return profile

        minimum = min(prices)
        maximum = max(prices)
        changed: list[str] = []
        if profile.price_min != minimum:
            profile.price_min = minimum
            changed.append("price_min")
        if profile.price_max != maximum:
            profile.price_max = maximum
            changed.append("price_max")
        wanted_mode = "fixed" if strategy == "fixed" else "variant"
        if profile.price_mode != wanted_mode:
            profile.price_mode = wanted_mode
            changed.append("price_mode")
        if changed:
            profile.save(update_fields=[*changed, "updated_at"])
        return profile

    epic49_catalog_profile.sync_catalog_profile = sync_catalog_profile
    epic49_catalog_profile._phase49_3f_pricing_finalize_installed = True
