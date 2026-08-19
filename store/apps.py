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
