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
        from .epic49_runtime_contract import install as install_epic49_runtime_contract
        install_epic49_runtime_contract()
        from . import signals  # noqa: F401
        from . import epic49_publish_signals  # noqa: F401
        from . import checks  # noqa: F401
