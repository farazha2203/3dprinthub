from __future__ import annotations


def install() -> None:
    """Ensure cached variant prices use the newly-synced Phase49.3F strategy.

    The existing import pipeline creates/updates variants before the catalog
    profile is fully synchronized. A variant recalc performed too early can
    therefore still see the legacy strategy. This wrapper runs only after the
    profile save and recalculates active variants against the final strategy.
    """
    from . import epic49_catalog_profile

    if getattr(epic49_catalog_profile, "_phase49_3f_pricing_finalize_installed", False):
        return

    original = epic49_catalog_profile.sync_catalog_profile

    def sync_catalog_profile(product, asset, data: dict, **kwargs):
        profile = original(product, asset, data, **kwargs)
        strategy = str(getattr(profile, "pricing_strategy", "legacy") or "legacy").strip().lower()
        if strategy in {"fixed", "dynamic"}:
            for variant in product.variants.filter(is_active=True).select_related("material", "quality", "color"):
                variant.recalculate_price(save=True)
        return profile

    epic49_catalog_profile.sync_catalog_profile = sync_catalog_profile
    epic49_catalog_profile._phase49_3f_pricing_finalize_installed = True
