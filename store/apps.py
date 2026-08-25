from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "store"
    verbose_name = "فروشگاه و بانک قطعات"

    def ready(self):
        # ProductCatalogProfile intentionally lives in its own module so the
        # mature store/models.py remains stable. Importing it here registers
        # the model under the `store` app before commands/views use it.
        from . import epic49_catalog_profile  # noqa: F401

        # Phase49.3B: migration 0032 owns these columns. Importing the module now
        # contributes the runtime fields before Admin registration; the publish
        # wrapper itself is installed later, after Unified Sync rebinds services.
        from . import phase49_3b_profile_media

        # Phase49.3F keeps the mature store/models.py stable too. The additive
        # migrations own the DB columns; this module contributes their runtime
        # model fields before Admin/runtime contracts are registered.
        from . import phase49_3f_pricing
        from . import phase49_3f_pricing_finalize

        # Phase50 Variant 2.0 follows the same additive pattern: migration 0034
        # owns the DB columns while this module contributes the runtime fields to
        # the mature ProductVariant / StoreOrderItem classes.
        from .phase50_variant2 import install as install_phase50_variant2
        install_phase50_variant2()

        from .epic49_runtime_contract import install as install_epic49_runtime_contract
        install_epic49_runtime_contract()
        from . import epic49_catalog_admin  # noqa: F401
        from . import signals  # noqa: F401
        from . import epic49_publish_signals  # noqa: F401

        # Epic49 unified must load after the publish signal so both the direct
        # service call and the signal-held callable are rebound to one revision-
        # protected Desktop <-> Server contract.
        from .phase49_unified_sync import install as install_phase49_unified_sync
        install_phase49_unified_sync()

        # Install profile persistence after Unified Sync so its apply_homepage_slider
        # wrapper cannot be overwritten by the revision-aware rebind above.
        phase49_3b_profile_media.install()

        # Phase49.3F is installed after Unified Sync/Profile Media so the explicit
        # fixed/dynamic pricing strategy becomes the final pricing contract used
        # by Catalog import, ProductVariant, Cart and Checkout.
        phase49_3f_pricing.install()
        phase49_3f_pricing_finalize.install()

        # Phase49.3I extends the mature pricing contract with an explicit range
        # strategy. It is semantic/runtime-only: the existing CharField/price_min/
        # price_max columns already support it, so no new migration is required.
        from .phase49_3i_pricing_modes import install as install_phase49_3i_pricing_modes
        install_phase49_3i_pricing_modes()

        # Phase49.3I.9 maps the desktop AI/SEO/source attribution payload onto the
        # real Product fields consumed by <title>, meta description, OG and Store
        # product pages. It wraps the mature converter; no second importer exists.
        from .phase49_3i9_seo_sync import install as install_phase49_3i9_seo_sync
        install_phase49_3i9_seo_sync()

        # Extend the already-registered mature Django Admin instead of replacing
        # website/store admin implementations.
        from .phase49_3f_admin import install as install_phase49_3f_admin
        install_phase49_3f_admin()

        # Phase50 exposes size/build/packaging fields through the mature Admin
        # registration and order snapshots without replacing the existing Admin.
        from .phase50_variant_admin import install as install_phase50_variant_admin
        install_phase50_variant_admin()

        # Phase50.A.1C: ImportedPrintAsset working-media stays private on
        # Production. Admin previews resolve Product-owned public media first and
        # expose translation/price/license completeness without raw JSON hunting.
        from .phase50_admin_media_integrity import install as install_phase50_admin_media_integrity
        install_phase50_admin_media_integrity()

        # Epic49 Persian Sales Hero: dedicated Windows Persian Slider SEO is the
        # public source of truth. Imported English/raw source boilerplate is not
        # allowed to become Store metadata or homepage Hero copy.
        from .phase49_persian_sales_runtime import install as install_phase49_persian_sales_runtime
        install_phase49_persian_sales_runtime()

        # Phase49.3B: after the mature publish path creates/updates the slide,
        # persist product-friendly fit/scale/position/background settings coming
        # from Windows Catalog Center into the same HomepageHeroSlide record.
        from .phase49_3b_hero_media_sync import install as install_phase49_3b_hero_media_sync
        install_phase49_3b_hero_media_sync()

        from . import checks  # noqa: F401
